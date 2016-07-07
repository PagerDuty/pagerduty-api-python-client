# Copyright (c) PagerDuty.
# See LICENSE for details.
import logging

import simplejson as json

from pypd.models.entity import Entity
from pypd.models.log_entry import LogEntry


class Incident(Entity):
    endpoint = 'incidents'
    logEntryFactory = LogEntry

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

    @property
    def log_entries(self, time_zone='UTC', is_overview=False, 
                    include=None, fetch_all=True):
        endpoint = '/'.join((self.endpoint, self.id, 'log_entries'))

        query_params = {
            'time_zone': time_zone,
            'is_overview': json.dumps(is_overview),
        }

        if include:
            query_params['include'] = include

        result = self.logEntryFactory.find(
            endpoint=endpoint,
            api_key=self.api_key,
            fetch_all=fetch_all,
            **query_params
        )

        return result
