
import ujson as json
from itertools import ifilter

from pypd.mixins import ClientMixin


class Entity(ClientMixin):
    id = None
    _data = None
    parse = None
    endpoint = None
    # flag so subsequent 'save' operations fail, and require a 'clone'
    _is_deleted = False
    EXCLUDE_FILTERS = ('name',)
    STR_OUTPUT_FIELDS = ('id',)
    TRANSLATE_QUERY_PARAM = None

    @staticmethod
    def sanitize_ep(endpoint, plural=False):
        if plural:
            if endpoint.endswith('y'):
                endpoint = endpoint[:-1] + 'ies'
            elif not endpoint.endswith('s'):
                endpoint += 's'
        else:
            if endpoint.endswith('ies'):
                endpoint = endpoint[:-3] + 'y'
            elif endpoint.endswith('s'):
                endpoint = endpoint[:-1]

        return endpoint

    def __init__(self, api_key=None, _data=None):
        if _data is not None:
            self._set(_data)
        ClientMixin.__init__(self, api_key)

    @classmethod
    def fetch(cls, id, api_key=None, **kwargs):
        inst = cls(api_key=api_key)
        parse_key = cls.sanitize_ep(cls.endpoint)
        endpoint = '/'.join((cls.endpoint, id))
        data = cls._parse(inst.request('GET',
                                       endpoint=endpoint,
                                       query_params=kwargs),
                          key=parse_key)
        inst._set(data)
        return inst

    @classmethod
    def _find_exclude_filter(cls, exclude, item):
        if exclude is None:
            return True

        bools = []
        for ef in cls.EXCLUDE_FILTERS:
            if callable(ef):
                bools.append(ef(item))
            else:
                bools.append(item.get(ef) not in exclude)

        return all(bools)

    @classmethod
    def find(cls, api_key=None, **kwargs):
        inst = cls(api_key=api_key)
        parse_key = cls.sanitize_ep(cls.endpoint, plural=True)
        exclude = kwargs.pop('exclude', None)
        query = kwargs.pop('query', None)

        if isinstance(exclude, basestring):
            exclude = [exclude, ]

        if cls.TRANSLATE_QUERY_PARAM:
            params = {}
            for param in cls.TRANSLATE_QUERY_PARAM:
                params[param] = kwargs.pop(param, None)

            if query is None:
                iparams = ifilter(None, params.values())
                try:
                    query = iparams.next()
                except StopIteration:
                    pass
            if query is not None:
                kwargs['query'] = query

        data = cls._parse(inst.request('GET',
                                       endpoint=cls.endpoint,
                                       query_params=kwargs),
                          key=parse_key)
        collection = [cls(api_key=api_key, _data=d) for d in data
                      if cls._find_exclude_filter(exclude, d)]
        return collection

    @classmethod
    def find_one(cls, *args, **kwargs):
        iterable = iter(cls.find(*args, **kwargs))
        return iterable.next()

    @classmethod
    def create(cls, data=None, api_key=None, add_headers=None, **kwargs):
        inst = cls(api_key=api_key)
        entity_endpoint = cls.sanitize_ep(cls.endpoint)
        body = {}
        body[entity_endpoint] = data
        inst._set(cls._parse(inst.request('POST', 
                                          endpoint=cls.endpoint,
                                          data=body,
                                          query_params=kwargs,
                                          add_headers=add_headers,
                                          ),
                             key=entity_endpoint))
        return inst

    @classmethod
    def delete(cls, id, api_key=None, **kwargs):
        inst = cls(api_key=api_key)
        endpoint = '/'.join((cls.endpoint, id))
        inst.request('DELETE', endpoint=endpoint, query_params=kwargs)
        inst._is_deleted = True
        return True

    @classmethod
    def _parse(cls, data, key=None):
        parse = cls.parse if cls.parse is not None else cls.endpoint

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
        if self._data is None:
            return None
        return self._data['id']

    @property
    def json(self):
        return self._data

    def remove(self):
        return self.__class__.delete(self.id)

    def __getitem__(self, attr):
        try:
            return self._data[attr]
        except:
            raise AttributeError("'%s' has no attribute '%s'" %
                                 (type(self), attr,))

    def __json__(self):
        return json.dumps(self._data)

    def __str__(self):
        id_ = hex(id(self))
        clsname = self.__class__.__name__

        info = {}

        for field in self.__class__.STR_OUTPUT_FIELDS:
            try:
                info[field] = self[field]
            except:
                pass

        if not info.get('id'):
            return '<%s uninitialized at %s>' % (clsname, id_,)

        output = '<%s ' % clsname
        for k, v in info.items():
            output += '%s=%s ' % (k, v)
        output += 'at %s>' % id_
        return output

    def __repr__(self):
        return self.__str__()
