# Copyright (c) PagerDuty.
# See LICENSE for details.
import six

from .entity import Entity
from ..errors import InvalidArguments, MissingFromEmail


class Alert(Entity):
    @classmethod
    def fetch(cls, id, incident=None, endpoint=None, *args, **kwargs):
        """Customize fetch because this is a nested resource."""
        if incident is None and endpoint is None:
            raise InvalidArguments(incident, endpoint)

        if endpoint is None:
            iid = incident['id'] if isinstance(incident, Entity) else incident
            endpoint = 'incidents/{0}/alerts'.format(iid)

        return getattr(Entity, 'fetch').__func__(cls, id, endpoint=endpoint,
                                                 *args, **kwargs)

    def resolve(self, from_email):
        """Resolve an alert using a valid email address."""
        if from_email is None or not isinstance(from_email, six.string_types):
            raise MissingFromEmail(from_email)

        parent_incident_id = self['incident']['id']
        endpoint_format = 'incidents/{0}/alerts/{1}'
        endpoint = endpoint_format.format(parent_incident_id, self['id'])

        add_headers = {'from': from_email, }
        data = {
            'alert': {
                'id': self['id'],
                'type': 'alert',
                'status': 'resolved',
            }
        }

        result = self.request('PUT',
                              endpoint=endpoint,
                              add_headers=add_headers,
                              data=data,)
        return result

    def associate(self, from_email, new_parent_incident=None):
        """Associate an alert with an incident using a valid email address."""
        if from_email is None or not isinstance(from_email, six.string_types):
            raise MissingFromEmail(from_email)

        if new_parent_incident is None:
            raise InvalidArguments(new_parent_incident)

        parent_incident_id = self['incident']['id']
        endpoint_format = 'incidents/{0}/alerts/{1}'
        endpoint = endpoint_format.format(parent_incident_id, self['id'])

        if isinstance(new_parent_incident, Entity):
            new_parent_incident_id = new_parent_incident['id']
        else:
            new_parent_incident_id = new_parent_incident

        add_headers = {'from': from_email, }
        data = {
            'alert': {
                'id': self['id'],
                'type': 'alert',
                'incident': {
                    'type': 'incident',
                    'id': new_parent_incident_id,
                }
            }
        }

        result = self.request('PUT',
                              endpoint=endpoint,
                              add_headers=add_headers,
                              data=data,)
        return result

    def update(self, *args, **kwargs):
        """Update an alert."""
        raise NotImplemented
