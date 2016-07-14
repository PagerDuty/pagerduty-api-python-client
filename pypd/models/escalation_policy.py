# Copyright (c) PagerDuty.
# See LICENSE for details.
from pypd.models.entity import Entity
from pypd.models.service import Service


class EscalationPolicy(Entity):
    """PagerDuty escalation policy entity."""
    STR_OUTPUT_FIELDS = ('id', 'name',)
    TRANSLATE_QUERY_PARAM = ('name',)

    def services(self):
        """Fetch all instances of services for this EP."""
        ids = [ref['id'] for ref in self['services']]
        return map(Service.fetch, ids)
