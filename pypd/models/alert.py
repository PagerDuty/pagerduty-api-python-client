# Copyright (c) PagerDuty.
# See LICENSE for details.
try:
    import ujson as json
except ImportError:
    import json

from .entity import Entity
from ..errors import InvalidArguments


class Alert(Entity):
    def resolve(self, from_email=None):
        """Resolve an alert using a valid email address."""
        if from_email is None:
            raise InvalidArguments(from_email)

        parent_incident_id = self['incident']['id']
        endpoint = 'incidents/{0}/alerts/{1}'.format(parent_incident_id, self['id'])

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

    def associate(self, new_parent_incident=None, from_email=None,):
        """Associate an alert with an incident using a valid email address."""
        if from_email is None:
            raise InvalidArguments(from_email)

        if new_parent_incident is None:
            raise InvalidArguments(new_parent_incident)

        parent_incident_id = self['incident']['id']
        endpoint = 'incidents/{0}/alerts/{1}'.format(parent_incident_id, self['id'])

        new_parent_incident_id = new_parent_incident['id'] if isinstance(new_parent_incident, Entity) else new_parent_incident

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
