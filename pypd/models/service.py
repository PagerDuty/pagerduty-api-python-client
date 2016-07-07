# Copyright (c) PagerDuty.
# See LICENSE for details.
from pypd.models.entity import Entity


class Service(Entity):
    endpoint = 'services'
    STR_OUTPUT_FIELDS = ('id', 'name',)

    def add_integration():
        pass
