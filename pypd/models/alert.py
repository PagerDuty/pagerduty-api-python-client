# Copyright (c) PagerDuty.
# See LICENSE for details.
try:
    import ujson as json
except ImportError:
    import json

from .entity import Entity


class Alert(Entity):
    def resolve(self, incident=None, from_email=None):
        """Resolve an alert using a valid email address."""
        if from_email is None:
            raise Exception('%s.resolve requires \'from_email\' argument.')

        if incident is None and endpoint is None:
            raise InvalidArguments(incident, endpoint)

        iid = incident['id'] if isinstance(incident, Entity) else incident
        endpoint = 'incidents/{0}/alerts/{1}'.format(iid, self['id'])

        add_headers = {'from': from_email, }
        data = {
            'alert': {
                'id': iid,
                'type': 'alert',
                'status': 'resolved',
            }
        }

        result = self.request('PUT',
                              endpoint=endpoint,
                              add_headers=add_headers,
                              data=data,)
        return result

    def associate(self, incident=None, new_parent=None, from_email=None,):
        """Associate an alert with an incident using a valid email address."""
        if from_email is None:
            raise Exception('%s.associate requires \'from_email\' argument.')

        if new_parent is None:
            raise Exception('%s.associate requires \'new_parent\' argument.')

        iid = incident['id'] if isinstance(incident, Entity) else incident
        endpoint = 'incidents/{0}/alerts/{1}'.format(iid, self['id'])

        new_parent_id = new_parent['id'] if isinstance(new_parent, Entity) else new_parent

        add_headers = {'from': from_email, }
        data = {
            'alert': {
                'id': iid,
                'type': 'alert',
                'incident': {
                    'type': 'incident',
                    'id': new_parent_id,
                }
            }
        }

        print data

        result = self.request('PUT',
                              endpoint=endpoint,
                              add_headers=add_headers,
                              data=data,)
        return result

    def update(self, *args, **kwargs):
        """Update an alert."""
        raise NotImplemented
