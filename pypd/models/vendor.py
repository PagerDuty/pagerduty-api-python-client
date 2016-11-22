
# Copyright (c) PagerDuty.
# See LICENSE for details.
from .entity import Entity
from ..errors import InvalidEndpointOperation, InvalidEndpoint


class Vendor(Entity):
    """PagerDuty vedor entity."""

    ALLOWED_VENDOR_TYPES = [
        # 'vendor',
        'vendor_reference',
    ]

    @classmethod
    def validate(cls, vendor_info):
        """Validate `vendor_info` to be valid vendor data."""
        assert isinstance(vendor_info, dict)
        assert (vendor_info['type'] in cls.ALLOWED_VENDOR_TYPES)

    @classmethod
    def delete(cls, *args, **kwargs):
        """Disable this endpoint, not valid v2."""
        raise InvalidEndpoint('Not a valid location on this endpoint')

    def remove(self, *args, **kwargs):
        """Disable this operation, not valid on this endpoint."""
        raise InvalidEndpointOperation(
            'Not a valid operation on this endpoint.'
        )

    @classmethod
    def create(cls, data=None, *args, **kwargs):
        """Validate and then create a Vendor entity."""
        cls.validate(data)
        # otherwise endpoint should contain the service path too
        getattr(Entity, 'create').im_func(cls, data=data, *args, **kwargs)
