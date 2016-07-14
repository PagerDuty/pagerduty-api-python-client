# Copyright (c) PagerDuty.
# See LICENSE for details.
from pypd.models.entity import Entity


class MaintenanceWindow(Entity):
    endpoint = 'maintenance_windows'

    def update(self, *args, **kwargs):
        """Update a MaintenanceWindow."""
        raise NotImplemented
