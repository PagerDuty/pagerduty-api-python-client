
import logging

from pypd.models.entity import Entity


class Incident(Entity):
    endpoint = 'incidents'

    def resolve(self, from_email=None, resolution=None,):
        endpoint = '/'.join((self.endpoint, self.id,))

        if from_email is None:
            raise Exception('%s.resolve requires \'from_email\' argument.')

        add_headers = {'from': from_email, }
        data = {
            'incident': {
                'type': 'incident',
                'status': 'resolved',
            }
        }

        if resolution is not None:
            data['resolution'] = resolution

        result = self.request('PUT',
                              endpoint=endpoint,
                              add_headers=add_headers,
                              data=data,)
        return result
