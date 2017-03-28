# Copyright (c) PagerDuty.
# See LICENSE for details.
from .entity import Entity


class User(Entity):
    """PagerDuty user entity."""
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

        return getattr(Entity, 'create').__func__(
            cls,
            data=data,
            api_key=api_key,
            add_headers=add_headers
        )

    def contact_methods(self, **kwargs):
        """Get all contact methods for this user."""
        endpoint = '{0}/{1}/contact_methods'.format(
            self.endpoint,
            self['id'],
        )
        result = self.request('GET', endpoint=endpoint, query_params=kwargs)
        return result['contact_methods']

    def create_contact_method(self, data, **kwargs):
        """Create a contact method for this user."""
        data = {'contact_method': data, }
        endpoint = '{0}/{1}/contact_methods'.format(
            self.endpoint,
            self['id'],
        )
        result = self.request('POST', endpoint=endpoint, data=data,
                              query_params=kwargs)
        self._data['contact_methods'].append(result['contact_method'])
        return result

    def delete_contact_method(self, id, **kwargs):
        """Delete a contact method for this user."""
        endpoint = '{0}/{1}/contact_methods/{2}'.format(
            self.endpoint,
            self['id'],
            id,
        )
        return self.request('DELETE', endpoint=endpoint, query_params=kwargs)

    def get_contact_method(self, id, **kwargs):
        """Get a contact method for this user."""
        endpoint = '{0}/{1}/contact_methods/{2}'.format(
            self.endpoint,
            self['id'],
            id,
        )
        result = self.request('GET', endpoint=endpoint, query_params=kwargs)
        return result['contact_method']

    def notification_rules(self, **kwargs):
        """Get all notification rules for this user."""
        endpoint = '{0}/{1}/notification_rules'.format(
            self.endpoint,
            self['id'],
        )
        result = self.request('GET', endpoint=endpoint, query_params=kwargs)
        return result['notification_rules']

    def get_notification_rule(self, id, **kwargs):
        """Get a notification rule for this user."""
        endpoint = '{0}/{1}/notification_rules/{2}'.format(
            self.endpoint,
            self['id'],
            id,
        )
        result = self.request('GET', endpoint=endpoint, query_params=kwargs)
        return result['notification_rule']

    def create_notification_rule(self, data, **kwargs):
        """Create a notification rule for this user."""
        data = {'notification_rule': data, }
        endpoint = '{0}/{1}/notification_rules'.format(
            self.endpoint,
            self['id'],
        )
        result = self.request('POST', endpoint=endpoint, data=data,
                              query_params=kwargs)
        self._data['notification_rules'].append(result['notification_rule'])
        return result

    def delete_notification_rule(self, id, **kwargs):
        """Get a notification rule for this user."""
        endpoint = '{0}/{1}/notification_rules/{2}'.format(
            self.endpoint,
            self['id'],
            id,
        )
        return self.request('DELETE', endpoint=endpoint, query_params=kwargs)

    def update_contact_method(self, *args, **kwargs):
        """Please implement me."""
        raise NotImplemented

    def update_notification_rule(self, *args, **kwargs):
        """Please implement me."""
        raise NotImplemented

    def update(self, *args, **kwargs):
        """Update this team."""
        raise NotImplemented
