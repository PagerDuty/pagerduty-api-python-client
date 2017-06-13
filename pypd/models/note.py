# Copyright (c) PagerDuty.
# See LICENSE for details.
from .entity import Entity
from ..errors import (InvalidEndpointOperation, InvalidEndpoint,
                      InvalidArguments)


class Note(Entity):
    """PagerDuty note entity."""

    @classmethod
    def fetch(*args, **kwargs):
        """Disable this endpoint, not valid v2."""
        raise InvalidEndpoint('Not a valid location on this endpoint')

    def remove(self, *args, **kwargs):
        """Disable this operation, not valid on this endpoint."""
        raise InvalidEndpointOperation(
            'Not a valid operation on this endpoint.'
        )

    delete = fetch

    @classmethod
    def create(cls, incident=None, endpoint=None, *args, **kwargs):
        """
        Create a note within the scope of an incident.

        Make sure that they should reasonably be able to query with an
        incident or endpoint that knows about an incident.
        """
        if incident is None and endpoint is None:
            raise InvalidArguments(incident, endpoint)
        if endpoint is None:
            iid = incident['id'] if isinstance(incident, Entity) else incident
            endpoint = 'incidents/{0}/notes'.format(iid)

        # otherwise endpoint should contain the incident path too
        return getattr(Entity, 'create').__func__(
            cls,
            endpoint=endpoint,
            *args,
            **kwargs
        )
