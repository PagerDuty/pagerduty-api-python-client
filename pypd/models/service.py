# Copyright (c) PagerDuty.
# See LICENSE for details.
from .entity import Entity
from .integration import Integration
from .vendor import Vendor


class Service(Entity):
    """PagerDuty service entity."""

    STR_OUTPUT_FIELDS = ('id', 'name',)
    integrationFactory = Integration
    vendorFactory = Vendor

    ALLOWED_SERVICE_TYPES = [
        # 'service',
        'service_reference',
    ]

    @classmethod
    def validate(cls, service_info):
        """Validate `service_info` to be acceptable service data."""
        assert isinstance(service_info, dict)
        assert (service_info['type'] in cls.ALLOWED_SERVICE_TYPES)

    def create_integration(self, integration_info, **kwargs):
        """
        Create an integration for this incident.

        See: https://v2.developer.pagerduty.com/v2/page/api-reference#!/
              Services/post_services_id_integrations
        """
        service_info = integration_info.get('service')
        vendor_info = integration_info.get('vendor')

        if service_info is not None:
            self.__class__.validate(service_info)

        if vendor_info is not None:
            self.vendorFactory.validate(vendor_info)

        endpoint = '{0}/{1}/integrations'.format(
            self.endpoint,
            self['id'],
        )
        return self.integrationFactory.create(
            endpoint=endpoint,
            api_key=self.api_key,
            data=integration_info,
            query_params=kwargs
        )

    def integrations(self, **kwargs):
        """Retrieve all this services integrations."""
        ids = [ref['id'] for ref in self['integrations']]
        return [Integration.fetch(id, service=self, query_params=kwargs) for id in ids]

    def get_integration(self, id, **kwargs):
        """Retrieve a single integration by id."""
        return Integration.fetch(id, service=self, query_params=kwargs)

    def update_integration(self, *args, **kwargs):
        """Update this integration on this service."""
        raise NotImplemented

    # sugar-pills
    view_integration = get_integration
    add_integration = create_integration
