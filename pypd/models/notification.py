# Copyright (c) PagerDuty.
# See LICENSE for details.
import datetime

from .entity import Entity
from ..errors import (InvalidArguments, InvalidEndpoint,
                      InvalidEndpointOperation)


class Notification(Entity):
    """A PagerDuty Notification entity."""

    @classmethod
    def find(cls, *args, **kwargs):
        """
        Find notifications.

        Optional kwargs are:
            since:
                datetime instance
            until:
                datetime instance

        If not specified, until will default to now(), and since will default
        to 30 days prior to until.

        As per PD spec, date range must not exceed 1 month.
        """
        seconds = 60 * 60 * 24 * 30  # seconds in 30 days
        until = kwargs.pop('until', None)
        since = kwargs.pop('since', None)

        if until is None:
            until = datetime.datetime.now()

        if since is None:
            since = until - datetime.timedelta(seconds=seconds)

        dt = until - since
        if dt > datetime.timedelta(seconds=seconds):
            raise InvalidArguments(until, since)

        kwargs['since'] = since.isoformat()
        kwargs['until'] = until.isoformat()

        return getattr(Entity, 'find').__func__(cls, *args, **kwargs)

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
