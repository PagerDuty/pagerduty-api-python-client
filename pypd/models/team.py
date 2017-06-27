# Copyright (c) PagerDuty.
# See LICENSE for details.
import six

from .entity import Entity
from .user import User
from .escalation_policy import EscalationPolicy


class Team(Entity):
    """PagerDuty team entity."""

    STR_OUTPUT_FIELDS = ('id', 'name',)
    escalationPolicyFactory = EscalationPolicy

    def remove_escalation_policy(self, escalation_policy, **kwargs):
        """Remove an escalation policy from this team."""
        if isinstance(escalation_policy, Entity):
            escalation_policy = escalation_policy['id']

        assert isinstance(escalation_policy, six.string_types)

        endpoint = '{0}/{1}/escalation_policies/{2}'.format(
            self.endpoint,
            self['id'],
            escalation_policy,
        )

        return self.request('DELETE', endpoint=endpoint, query_params=kwargs)

    def add_escalation_policy(self, escalation_policy, **kwargs):
        """Add an escalation policy to this team."""
        if isinstance(escalation_policy, Entity):
            escalation_policy = escalation_policy['id']

        assert isinstance(escalation_policy, six.string_types)

        endpoint = '{0}/{1}/escalation_policies/{2}'.format(
            self.endpoint,
            self['id'],
            escalation_policy,
        )
        return self.request('PUT', endpoint=endpoint, query_params=kwargs)

    def remove_user(self, user, **kwargs):
        """Remove a user from this team."""
        if isinstance(user, Entity):
            user = user['id']

        assert isinstance(user, six.string_types)

        endpoint = '{0}/{1}/escalation_policies/{2}'.format(
            self.endpoint,
            self['id'],
            user,
        )
        return self.request('DELETE', endpoint=endpoint, query_params=kwargs)

    def add_user(self, user, **kwargs):
        """Add a user to this team."""
        if isinstance(user, User):
            user = user['id']

        assert isinstance(user, six.string_types)

        endpoint = '{0}/{1}/users/{2}'.format(
            self.endpoint,
            self['id'],
            user,
        )
        result = self.request('PUT', endpoint=endpoint, query_params=kwargs)
        return result

    def update(self, *args, **kwargs):
        """Update this team."""
        raise NotImplemented
