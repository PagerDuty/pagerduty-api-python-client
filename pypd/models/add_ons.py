# Copyright (c) PagerDuty.
# See LICENSE for details.
from .entity import Entity


class AddOn(Entity):
    """PagerDuty add-on entity."""

    endpoint = 'addons'

    @classmethod
    def install(cls, type_, name, src, *args, **kwargs):
        """Install an add-on to this account."""
        data = kwargs.pop('data', None)
        if data is None:
            data = {
                'addon': {
                    'type': type_,
                    'name': name,
                    'src': src,
                }
            }
        cls.create(data=data, *args, **kwargs)

    def update(self, *args, **kwargs):
        """Update this add-on."""
        raise NotImplemented
