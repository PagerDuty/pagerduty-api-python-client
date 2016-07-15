# Copyright (c) PagerDuty.
# See LICENSE for details.
from .entity import Entity
from ..errors import InvalidEndpointOperation, InvalidEndpoint


class OnCall(Entity):
    endpoint = 'oncalls'  # silly

    STR_OUTPUT_FIELDS = ('escalation_level', 'user.id')

    @classmethod
    def fetch(*args, **kwargs):
        """Disable this endpoint, not valid v2."""
        raise InvalidEndpoint('Not a valid location on this endpoint')

    def remove(self, *args, **kwargs):
        """Disable this operation, not valid on this endpoint."""
        raise InvalidEndpointOperation(
            'Not a valid operation on this endpoint.'
        )

    create = fetch
    delete = fetch
