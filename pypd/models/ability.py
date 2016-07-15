"""
PagerDuty abilities are strings that represent an account ability.

However, abilities don't *really* follow the style of other endpoints so
instead of making a typical endpoint, we'll just expose methods. That can be
called.
"""
# Copyright (c) PagerDuty.
# See LICENSE for details.
from ..mixins import ClientMixin


def abilities(api_key=None, add_headers=None):
    """Fetch a list of permission-like strings for this account."""
    client = ClientMixin(api_key=api_key)
    result = client.request('GET', endpoint='abilities',
                            add_headers=add_headers,)
    return result['abilities']


def can(ability, add_headers=None):
    """Test whether an ability is allowed."""
    client = ClientMixin(api_key=None)
    try:
        client.request('GET', endpoint='abilities/%s' % ability,
                       add_headers=add_headers)
        return True
    except Exception:
        pass
    return False
