# Copyright (c) PagerDuty.
# See LICENSE for details.
import ujson as json


class Error(Exception):
    pass


class InvalidHeaders(Error):
    def __init__(self, headers):
        self.headers = headers
        self.message = "Request received an invalid headers object, %r".format(
            headers,
        )


class BadRequest(Error):
    def __init__(self, code=400, message='', *args, **kwargs):
        self.code = code
        self.message = message
        self.errors = []

        Error.__init__(self, *args, **kwargs)

        try:
            obj = json.loads(message)['error']
            self.code = obj.get('code', code)
            self.message = obj.get('message', message)
            self.errors = obj.get('errors', [])
        except:
            pass

    def __str__(self):
        error = '{0} ({1}): {2}'.format(self.__class__.__name__, self.code,
                                        self.message)
        if self.errors:
            addon = self.errors[0] if len(self.errors) == 1 else self.errors
            error = '{0} - {1}'.format(error, addon)

        return error


class UnknownError(Error):
    def __init__(self, code, url, message=''):
        self.code = code
        self.url = url
        self.message = message

    def __str__(self):
        return '{0} ({1}): {2}'.format(self.__class__.__name__, self.code,
                                       self.message)


class InvalidResponse(Error):
    """A server response was pure nonsense."""

    def __init__(self, data):
        self.data = data

    def __str__(self):
        return 'InvalidResponse: {0}'.format(self.data)


class InvalidArguments(Exception):
    """A function was passed invalid arguments."""


class InvalidEndpoint(Exception):
    """An endpoint was accessed that is not a valid API endpoint."""


class InvalidEndpointOperation(Exception):
    """An invalid operation on this endpoint was accessed."""
