# Copyright (c) PagerDuty.
# See LICENSE for details.
from .entity import Entity


class Schedule(Entity):
    """PagerDuty schedule entity."""

    def get_oncall(self, **kwargs):
        """Retrieve this schedule's "on call" users."""

        endpoint = '/'.join((self.endpoint, self.id, 'users'))

        return self.request('GET', endpoint=endpoint, query_params=kwargs)
