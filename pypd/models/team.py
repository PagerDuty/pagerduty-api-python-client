
from pypd.models.entity import Entity
from pypd.models.user import User


class Team(Entity):
    endpoint = 'teams'
    STR_OUTPUT_FIELDS = ('id', 'name',)

    def add_user(self, user):
        if isinstance(user, User):
            user = user.id

        if not isinstance(user, basestring):
            raise Exception('Invalid user ID provided!')

        endpoint = '/'.join((self.endpoint, self.id, 'users', user))
        result = self.request('PUT', endpoint=endpoint)
        return result