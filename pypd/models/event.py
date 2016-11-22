# Copyright (c) PagerDuty.
# See LICENSE for details.
"""
Entity module provides a base class Entity for defining a PagerDuty entity.

Entities should be used as the base for all things that ought to be queryable
via PagerDuty v2 API.
"""

from .entity import Entity


class Event(Entity):
    base_url = 'https://events.pagerduty.com/generic/2010-04-15/'\
               'create_event.json'
    EVENT_TYPES = ('trigger', 'acknowledge', 'resolve',)

    @classmethod
    def validate(cls, event_info):
        """Validate that provided event information is valid."""
        assert 'service_key' in event_info
        assert isinstance(event_info['service_key'], basestring)
        assert 'event_type' in event_info
        assert event_info['event_type'] in cls.EVENT_TYPES
        if event_info['event_type'] != cls.EVENT_TYPES[0]:
            assert 'incident_key' in event_info
            assert isinstance(event_info['incident_key'], basestring)
        else:
            assert 'description' in event_info

        if 'details' in event_info:
            assert isinstance(event_info['details'], dict)

        if 'contexts' in event_info:
            assert isinstance(event_info['contexts'], (list, tuple,))

    @classmethod
    def create(cls, data=None, api_key=None, endpoint=None, add_headers=None,
               **kwargs):
        """Create an event on your PagerDuty account."""
        cls.validate(data)
        inst = cls(api_key=api_key)
        endpoint = ''
        return inst.request('POST',
                            endpoint=endpoint,
                            data=data,
                            query_params=kwargs,
                            add_headers=add_headers,
                            )
