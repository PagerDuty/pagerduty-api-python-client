# Copyright (c) PagerDuty.
# See LICENSE for details.
import logging

from pypd.models.entity import Entity
from pypd.models.service import Service


class EscalationPolicy(Entity):
    STR_OUTPUT_FIELDS = ('id', 'name',)
    TRANSLATE_QUERY_PARAM = ('name',)

    @property
    def services(self):
        ids = [ref['id'] for ref in self['services']]
        return map(Service.fetch, ids)
