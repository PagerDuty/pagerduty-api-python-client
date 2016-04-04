
from pypd.models.entity import Entity


class Service(Entity):
    endpoint = 'services'
    STR_OUTPUT_FIELDS = ('id', 'name',)
