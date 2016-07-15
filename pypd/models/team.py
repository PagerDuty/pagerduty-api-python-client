# Copyright (c) PagerDuty.
# See LICENSE for details.
from .entity import Entity
from .user import User


class Team(Entity):
    """PagerDuty team entity."""
    STR_OUTPUT_FIELDS = ('id', 'name',)

    def add_user(self, user):
        if isinstance(user, User):
            user = user.id

        if not isinstance(user, basestring):
            raise Exception('Invalid user ID provided!')

        endpoint = '/'.join((self.endpoint, self.id, 'users', user))
        result = self.request('PUT', endpoint=endpoint)
        return result

    def update(self, *args, **kwargs):
        """Update this team."""
        raise NotImplemented