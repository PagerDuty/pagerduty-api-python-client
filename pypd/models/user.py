# Copyright (c) PagerDuty.
# See LICENSE for details.
from .entity import Entity


class User(Entity):
    endpoint = 'users'
    STR_OUTPUT_FIELDS = ('id', 'email',)
    EXCLUDE_FILTERS = TRANSLATE_QUERY_PARAM = ('email', 'name',)

    @property
    def email(self):
        return self['email']

    @classmethod
    def create(cls, data=None, api_key=None, add_headers=None, from_email=None,
               **kwargs):
        if add_headers is None:
            add_headers = {}

        if from_email is None:
            raise Exception('%s.create requires from_email keyword argument'
                            % (cls,))
        if from_email is not None:
            add_headers['From'] = from_email

        return getattr(Entity, 'create').im_func(
            cls,
            data=data,
            api_key=api_key,
            add_headers=add_headers
        )

    def create_contact_method(self, data, **kwargs):
        data = {'contact_method': data, }
        endpoint = '/'.join((self.endpoint, self.id, 'contact_methods'))
        result = self.request('POST', endpoint=endpoint, data=data,
                              query_params=kwargs)
        self._data['contact_methods'].append(result['contact_method'])
        return result
