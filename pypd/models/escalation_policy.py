# Copyright (c) PagerDuty.
# See LICENSE for details.
from .entity import Entity
from .service import Service


class EscalationPolicy(Entity):
    """PagerDuty escalation policy entity."""

    STR_OUTPUT_FIELDS = ('id', 'name',)
    TRANSLATE_QUERY_PARAM = ('name',)

    def services(self):
        """Fetch all instances of services for this EP."""
        ids = [ref['id'] for ref in self['services']]
        return [Service.fetch(id) for id in ids]

    def update(self, *args, **kwargs):
        """Update this escalation policy."""
        raise NotImplemented
