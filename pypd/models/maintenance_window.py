# Copyright (c) PagerDuty.
# See LICENSE for details.
from .entity import Entity


class MaintenanceWindow(Entity):
    """PagerDuty maintenance window entity."""

    def update(self, *args, **kwargs):
        """Update a MaintenanceWindow."""
        raise NotImplemented
