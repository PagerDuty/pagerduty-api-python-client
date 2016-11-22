# Copyright (c) PagerDuty.
# See LICENSE for details.
"""
Entity module provides a base class Entity for defining a PagerDuty entity.

Entities should be used as the base for all things that ought to be queryable
via PagerDuty v2 API.
"""
import re
import ujson as json
from itertools import ifilter

from ..mixins import ClientMixin
from ..log import warn


class NotInitialized(Exception):
    """Raise when an entity is not initialized but accessed as if it were."""


class Entity(ClientMixin):
    """
    Base class for implementing a PagerDuty-something.

    Entities can access their underlying entity data by using dict-like
    accessor methods, ie. `get('property_name', default_value)` and using
    entity['property'] accessors.

    Entities inherit from a ClientMixin which handles doing HTTP requests. They
    also have some special properties to them:

    Entity classes have classmethods for which to initialize queries that ought
    to return a class instance, or a list of class instances they are:
        find:
            finds some instances of this entity, returns a list
        find_one:
            finds one instance of this entity, returns instance
        fetch:
            finds one instance of this entity, returns instance
        create:
            creates an instance of this entity (HTTP POST), returns instance
        delete:
            deletes an instance of this entity (HTTP DELETE), returns None

    Entities have instance methods that help interact with an entity on the api
    they are:
        remove:
            deletes this entity instance, returns None
        get:
            access any property on the entity, like dict-accessor get

    Entities have properties that are also interesting (accessed with dot
    notation):
        id:
            the entities ID value (str)
        json:
            the json representation of the entity (dict)
        _data:
            (do not use directly) contains raw entity data, accessible with
            `get(property, default_value)` OR with entity['property'] syntax

    Entity classes use few special class instances:
        TRANSLATE_QUERY_PARAM:
            A list of strings that ought to be translated to 'query' for the
            query string '?query=stuff', eg.

                TRANSLATE_QUERY_PARAM = ('name',)
                query_with_kwargs(name='joeblow')
                # output = 'uri?query=joeblow'
        MAX_LIMIT_VALUE:
            The normal maximum number of entities returned per page from the
            PagerDuty API
        EXCLUDE_FILTERS:
            A list of strings and methods that will be used to filter out
            entities with the matching criteria. Where strings will look
            to match the keyword argument `excludes='joeblow'` to a value found
            on a key matching any EXLCUDE_FILTERS value OR will apply a method
            with signatures `def exclude_method(cls, item, value)`. Eg.

            class CustomEntity(Entity):
                EXCLUDE_FILTERS = ['name', ...]

                # is the same as

                EXCLUDE_FILTERS =
                    [lambda cls, item, ev: item.get('name').count(ev), ...]
    """

    id = None
    _data = None
    parse = None
    endpoint = None
    # flag so subsequent 'save' operations fail, and require a 'clone'
    _is_deleted = False
    EXCLUDE_FILTERS = ('name',)  # exclude will filter on these properties
    STR_OUTPUT_FIELDS = ('id',)  # fields to output in __str__
    TRANSLATE_QUERY_PARAM = None  # translates uri?query=stuff
    MAX_LIMIT_VALUE = 100

    def __init__(self, api_key=None, _data=None):
        """Initialize Entity model."""
        if _data is not None:
            self._set(_data)

        # sanitize the endpoint name incase people make mistakes
        self.endpoint = self.__class__.get_endpoint()
        if self.endpoint.endswith('/'):
            warn('Endpoints should not end with a trailing slash, %s',
                 self.__class__)
            self.endpoint = self.endpoint[:-1]

        ClientMixin.__init__(self, api_key)

    @staticmethod
    def sanitize_ep(endpoint, plural=False):
        """
        Sanitize an endpoint to a singular or plural form.

        Used mostly for convenience in the `_parse` method to grab the raw
        data from queried datasets.

        XXX: this is el cheapo (no bastante bien)
        """
        # if we need a plural endpoint (acessing lists)
        if plural:
            if endpoint.endswith('y'):
                endpoint = endpoint[:-1] + 'ies'
            elif not endpoint.endswith('s'):
                endpoint += 's'
        else:
            # otherwise make sure it's singular form
            if endpoint.endswith('ies'):
                endpoint = endpoint[:-3] + 'y'
            elif endpoint.endswith('s'):
                endpoint = endpoint[:-1]

        return endpoint

    @classmethod
    def get_endpoint(cls):
        """
        Accessor method to enable omition of endpoint name.

        In general we want the class name to be translated to endpoint name,
        this way unless otherwise specified will translate class name to
        endpoint name.
        """
        if cls.endpoint is not None:
            return cls.endpoint
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return cls.sanitize_ep(
            re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower(),
            plural=True
        )

    @classmethod
    def _fetch_all(cls, api_key, endpoint=None, offset=0, limit=25, **kwargs):
        """
        Call `self._fetch_page` for as many pages as exist.

        TODO: should be extended to do async page fetches if API allows it via
        exposing total value.

        Returns a list of `cls` instances.
        """
        output = []
        qp = kwargs.copy()
        limit = max(1, min(100, limit))
        maximum = kwargs.get('maximum')
        qp['limit'] = min(limit, maximum) if maximum is not None else limit
        qp['offset'] = offset
        more, total = None, None

        while True:
            entities, options = cls._fetch_page(
                api_key=api_key, endpoint=endpoint, **qp
            )
            output += entities
            more = options.get('more')
            limit = options.get('limit')
            offset = options.get('offset')
            total = options.get('total')

            if more is None:
                if total is None or offset is None:
                    break
                more = (limit + offset) < total

            if not more or (maximum is not None and len(output) >= maximum):
                break

            qp['limit'] = limit
            qp['offset'] = offset + limit

        return output

    @classmethod
    def _fetch_page(cls, api_key, endpoint=None, page_index=0, offset=None,
                    limit=25, **kwargs):
        """
        Fetch a single page of `limit` number of results.

        Optionally provide `page_index` an integer (0-based) index for the
        page to return. Calculated based on `limit` and `offset`.

        Optionally provide `offset` which will override `page_index` if both
        are passed, will be used to calculate the integer offset of items.

        Optionally provide `limit` integer describing how many items pages
        ought to have.

        Returns a tuple containing a list of `cls` instances and response
        options.
        """
        # if offset is provided have it overwrite the page_index provided
        if offset is not None:
            page_index = int(offset / limit)

        # limit can be maximum MAX_LIMIT_VALUE for most PD queries
        limit = max(1, min(cls.MAX_LIMIT_VALUE, limit))

        # make an tmp instance to do query work
        inst = cls(api_key=api_key)

        kwargs['offset'] = int(page_index * limit)
        maximum = kwargs.pop('maximum', None)

        # if maximum is valid, make the limit <= maximum
        kwargs['limit'] = min(limit, maximum) if maximum is not None else limit
        ep = parse_key = cls.sanitize_ep(cls.get_endpoint(), plural=True)

        # if an override to the endpoint is provided use that instead
        # this is useful for nested value searches ie. for
        # `incident_log_entries` but instead of /log_entries querying with
        # context of /incident/INCIDENTID/log_entries.
        # XXX: could be cleaner
        if endpoint is not None:
            ep = endpoint

        response = inst.request('GET', endpoint=ep, query_params=kwargs)
        # XXX: this is a little gross right now. Seems like the best way
        # to do the parsing out of something and then return everything else
        datas = cls._parse(response, key=parse_key)
        response.pop(parse_key, None)
        entities = map(lambda d: cls(api_key=api_key, _data=d), datas)
        # return a tuple
        return entities, response

    @classmethod
    def fetch(cls, id, api_key=None, endpoint=None, add_headers=None,
              **kwargs):
        """
        Fetch a single entity from the API endpoint.

        Used when you know the exact ID that must be queried.
        """
        if endpoint is None:
            endpoint = cls.get_endpoint()

        inst = cls(api_key=api_key)
        parse_key = cls.sanitize_ep(endpoint)
        endpoint = '/'.join((endpoint, id))
        data = cls._parse(inst.request('GET',
                                       endpoint=endpoint,
                                       add_headers=add_headers,
                                       query_params=kwargs),
                          key=parse_key)
        inst._set(data)
        return inst

    # sugar-pills
    get = fetch

    @classmethod
    def _find_exclude_filter(cls, excludes, item):
        """
        For each item returned by a `find()` maybe filter it out.

        Called for each item returned to find a function or string to exclude
        `item` from a filtered list. This method should return truthy values
        where `True`-like values will allow `item` to be included into the
        set, and `False` values will not allow them into the set (filter
        predicate).

        This is a dynamic filtering method such that users of the library
        will be able to do something like:

        Class.find(exclude=('email@address.com', 1,))

        Where the coreesponding EXCLUDE_FILTERS = ('email', 'id',). Similar to
        matching any value on any indexed field, where EXCLUDE_FILTERS are the
        indexes.

        XXX: Even explaining this was difficult. Probably an easier more
        pragmatic way to do this.
        """
        # if exclude is left blank (not a list) then the predicate will just
        # be true
        if excludes is None:
            return False

        # oh my...
        def test_each_exclude(exclude_value):
            # excluded_value is one of excludes = (...,)
            def exclude_equals_value_test(exclude_filter):
                # exclude_filter is one of EXCLUDE_FILTERS = (...,)
                if callable(exclude_filter):
                    return exclude_filter(cls, item, exclude_value,)
                return item.get(exclude_filter) == exclude_value
            return any(map(exclude_equals_value_test, cls.EXCLUDE_FILTERS))
        return any(map(test_each_exclude, excludes))

    @classmethod
    def translate_query_params(cls, query=None, **kwargs):
        """
        Translate an arbirtary keyword argument to the expected query.

        In the v2 API, many endpoints expect a particular query argument to be
        in the form of `query=xxx` where `xxx` would be the name of perhaps
        the name, ID or otherwise. This function ought to take a more aptly
        named parameter specified in `TRANSLATE_QUERY_PARAM`, and substitute it
        into the `query` keyword argument. The purpose is so that some models
        (optionally) have nicer named keyword arguments than `query` for easier
        to read python.

        If a query argument is given then the output should be that value. If a
        substitute value is given as a keyword specified in
        `TRANSLATE_QUERY_PARAM`(and query is not) then the `query` argument
        will be that keyword argument.

        Eg. No query param

            query = None
            TRANSLATE_QUERY_PARAM = ('name',)
            kwargs = {'name': 'PagerDuty'}
            ...
            output = {'query': 'PagerDuty'}

        or, query param explicitly

            query = 'XXXXPlopperDuty'
            TRANSLATE_QUERY_PARAM = ('name',)
            kwargs = {'name': 'PagerDuty'}
            ...
            output = {'query': 'XXXXPlopperDuty'}

        XXX: Clean this up. It's *too* flexible.
        """
        values = []
        output = kwargs.copy()

        # remove any of the TRANSLATE_QUERY_PARAMs in output
        for param in cls.TRANSLATE_QUERY_PARAM:
            popped = output.pop(param, None)
            if popped is not None:
                values.append(popped)

        # if query is not provided, use the first parameter we removed from
        # the kwargs
        try:
            output['query'] = ifilter(None, values).next()
        except StopIteration:
            pass

        # if query is provided, just use it
        if query is not None:
            output['query'] = query

        return output

    @classmethod
    def find(cls, api_key=None, fetch_all=True, endpoint=None, maximum=None,
             **kwargs):
        """
        Find some entities from the API endpoint.

        If no api_key is provided, the global api key will be used.
        If fetch_all is True, page through all the data and find every record
        that exists.
        If add_headers is provided (as a dict) use it to add headers to the
        HTTP request, eg.

            {'host': 'some.hidden.host'}

        Capitalizing header keys does not matter.

        Remaining keyword arguments will be passed as `query_params` to the
        instant method `request` (ClientMixin).
        """
        exclude = kwargs.pop('exclude', None)
        query = kwargs.pop('query', None)

        # if exclude param was passed a a string, list-ify it
        if isinstance(exclude, basestring):
            exclude = [exclude, ]

        if cls.TRANSLATE_QUERY_PARAM:
            query_params = cls.translate_query_params(query, **kwargs)
        else:
            query_params = kwargs

        # unless otherwise specified use the class variable for the endpoint
        if endpoint is None:
            endpoint = cls.get_endpoint()

        if fetch_all:
            result = cls._fetch_all(api_key=api_key, endpoint=endpoint,
                                    maximum=maximum,
                                    **query_params)
        else:
            result = cls._fetch_page(api_key=api_key, endpoint=endpoint,
                                     maximum=maximum,
                                     **query_params)

        # for each result run it through an exlcusion filter
        collection = [r for r in result
                      if not cls._find_exclude_filter(exclude, r)]
        return collection

    @classmethod
    def find_one(cls, *args, **kwargs):
        """Like `find()` except ensure that only one result is returned."""
        # ensure that maximum is supplied so that a big query is not happening
        # behind the scenes
        if 'maximum' not in kwargs:
            kwargs['maximum'] = 1

        # call find and extract the first iterated value from the result
        iterable = iter(cls.find(*args, **kwargs))
        return iterable.next()

    @classmethod
    def create(cls, data=None, api_key=None, endpoint=None, add_headers=None,
               **kwargs):
        """
        Create an instance of the Entity model by calling to the API endpoint.

        This ensures that server knows about the creation before returning
        the class instance.

        NOTE: The server must return a response with the schema containing
        the entire entity value. A True or False response is no bueno.
        """
        inst = cls(api_key=api_key)
        entity_endpoint = cls.sanitize_ep(cls.get_endpoint())
        body = {}
        body[entity_endpoint] = data

        if endpoint is None:
            endpoint = cls.get_endpoint()

        inst._set(cls._parse(inst.request('POST',
                                          endpoint=endpoint,
                                          data=body,
                                          query_params=kwargs,
                                          add_headers=add_headers,
                                          ),
                             key=entity_endpoint))
        return inst

    # sugar-pills
    post = create

    @classmethod
    def delete(cls, id, api_key=None, **kwargs):
        """Delete an entity from the server by ID."""
        inst = cls(api_key=api_key)
        endpoint = '/'.join((cls.get_endpoint(), id))
        inst.request('DELETE', endpoint=endpoint, query_params=kwargs)
        inst._is_deleted = True
        return True

    @classmethod
    def put(cls, id, api_key=None, **kwargs):
        """Delete an entity from the server by ID."""
        inst = cls(api_key=api_key)
        endpoint = '/'.join((cls.get_endpoint(), id))
        return inst.request('PUT', endpoint=endpoint, query_params=kwargs)

    @classmethod
    def _parse(cls, data, key=None):
        """
        Parse a set of data to extract entity-only data.

        Use classmethod `parse` if available, otherwise use the `endpoint`
        class variable to extract data from a data blob.
        """
        parse = cls.parse if cls.parse is not None else cls.get_endpoint()

        if callable(parse):
            data = parse(data)
        elif isinstance(parse, str):
            data = data[key]
        else:
            raise Exception('"parse" should be a callable or string got, {0}'
                            .format(parse))
        return data

    def _set(self, data):
        self._data = data

    @property
    def id(self):
        """
        Return the entity's ID from `self._data`.

        If not initialized raise a `NotInitialized` exception.
        """
        if self._data is None:
            raise NotInitialized
        return self._data['id']

    @property
    def json(self):
        """
        Return a dict that can be serialized to a JSON-string.

        Does NOT return an encoded string.
        """
        return self._data

    def remove(self):
        """Delete this instance from server record."""
        return self.__class__.delete(self.id)

    def __getitem__(self, attr):
        """Attribute accessor method in dict-like fashion."""
        try:
            return self._data[attr]
        except:
            raise AttributeError("'%s' has no attribute '%s'" %
                                 (type(self), attr,))

    def get(self, attr, default=None):
        """Attribute accessor method in dict-like fashion."""
        try:
            return self[attr]
        except:
            return default

    def __json__(self):
        """Return a valid JSON string dump of the entity data."""
        return json.dumps(self._data)

    def __str__(self):
        """Return a more meaningful class string."""
        id_ = hex(id(self))
        clsname = self.__class__.__name__

        info = {}

        for field in self.__class__.STR_OUTPUT_FIELDS:
            depth = field.split('.')
            original_field = field
            try:
                value = self
                while depth:
                    field = depth.pop(0)
                    value = value[field]
            except:
                pass
            info[original_field] = value

        if not info.get('id') and 'id' in self.__class__.STR_OUTPUT_FIELDS:
            return '<%s uninitialized at %s>' % (clsname, id_,)

        output = '<%s ' % clsname
        for k, v in info.items():
            output += '%s="%s" ' % (k, v)
        output += 'at %s>' % id_
        return output

    def __repr__(self):
        """Return a more meaningful programmer representation string."""
        return self.__str__()
