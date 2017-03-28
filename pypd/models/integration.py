# Copyright (c) PagerDuty.
# See LICENSE for details.
from .entity import Entity
from ..errors import (InvalidEndpointOperation, InvalidArguments,
                      InvalidEndpoint)


class Integration(Entity):
    """PagerDuty note entity."""

    ALLOWED_INTEGRATION_TYPES = [
        'aws_cloudwatch_inbound_integration',
        'aws_cloudwatch_inbound_integration_reference',
        'cloudkick_inbound_integration',
        'cloudkick_inbound_integration_reference',
        'event_transformer_api_inbound_integration',
        'event_transformer_api_inbound_integration_reference',
        'generic_email_inbound_integration',
        'generic_email_inbound_integration_reference',
        'generic_events_api_inbound_integration',
        'generic_events_api_inbound_integration_reference',
        'keynote_inbound_integration',
        'keynote_inbound_integration_reference',
        'nagios_inbound_integration',
        'nagios_inbound_integration_reference',
        'pingdom_inbound_integration',
        'pingdom_inbound_integration_reference',
        'sql_monitor_inbound_integration',
        'sql_monitor_inbound_integration_reference',
    ]

    @classmethod
    def validate(cls, integration_info):
        """Validate `integration_info` to be valid integration data."""
        assert isinstance(integration_info, dict)
        assert (integration_info['type'] in cls.ALLOWED_INTEGRATION_TYPES)

    @classmethod
    def fetch(cls, id, service=None, endpoint=None, *args, **kwargs):
        """Customize fetch because it lives on a special endpoint."""
        if service is None and endpoint is None:
            raise InvalidArguments(service, endpoint)

        if endpoint is None:
            sid = service['id'] if isinstance(service, Entity) else service
            endpoint = 'services/{0}/integrations'.format(sid)

        return getattr(Entity, 'fetch').__func__(cls, id, endpoint=endpoint,
                                                 *args, **kwargs)

    @classmethod
    def delete(*args, **kwargs):
        """Disable this endpoint, not valid v2."""
        raise InvalidEndpoint('Not a valid location on this endpoint')

    def remove(self, *args, **kwargs):
        """Disable this operation, not valid on this endpoint."""
        raise InvalidEndpointOperation(
            'Not a valid operation on this endpoint.'
        )

    @classmethod
    def create(cls, service=None, endpoint=None, data=None, *args, **kwargs):
        """
        Create an integration within the scope of an service.

        Make sure that they should reasonably be able to query with an
        service or endpoint that knows about an service.
        """
        cls.validate(data)

        if service is None and endpoint is None:
            raise InvalidArguments(service, endpoint)
        if endpoint is None:
            sid = service['id'] if isinstance(service, Entity) else service
            endpoint = 'services/{0}/integrations'.format(sid)

        # otherwise endpoint should contain the service path too
        getattr(Entity, 'create').__func__(cls, endpoint=endpoint, data=data,
                                          *args, **kwargs)
