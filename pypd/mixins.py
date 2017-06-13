"""Helpful mixins for PagerDuty entity classes."""
import datetime
import logging
try:
    import ujson as json
except ImportError:
    import json
from numbers import Number
import sys

import requests

from .log import log
from .errors import (BadRequest, UnknownError, InvalidResponse, InvalidHeaders)


CONTENT_TYPE = 'application/vnd.pagerduty+json;version=2'
AUTH_TEMPLATE = 'Token token={0}'
BASIC_AUTH_TEMPLATE = 'Basic {0}'


if sys.version_info[0] < 3:
    stringtype = basestring
else:
    stringtype = str


class ClientMixin(object):
    api_key = None
    base_url = None

    def __init__(self, api_key=None, base_url=None):
        # if no api key is provided try to get one from the packages api_key
        if api_key:
            self.api_key = api_key

        if self.api_key is None:
            from pypd import api_key
            self.api_key = api_key

        if base_url:
            self.base_url = base_url

        if self.base_url is None:
            from pypd import base_url
            self.base_url = base_url

    def _handle_response(self, response):
        if response.status_code == 404:
            response.raise_for_status()
        elif response.status_code // 100 == 4:
            raise BadRequest(response.status_code, response.text)
        elif response.status_code // 100 != 2:
            raise UnknownError(response.status_code, response.text)

        if not response.text:
            return None

        try:
            response = json.loads(response.text)
        except:
            raise InvalidResponse(response.text)

        return response

    def _do_request(self, method, *args, **kwargs):
        """
        Modularized because API was broken.

        Need to be able to inject Mocked response objects here.
        """
        log('Doing HTTP [{3}] request: {0} - headers: {1} - payload: {2}'.format(
            args[0], kwargs.get('headers'), kwargs.get('data'), method,),
            level=logging.DEBUG,)
        requests_method = getattr(requests, method)
        return self._handle_response(requests_method(*args, **kwargs))

    def request(self, method='GET', endpoint='', query_params=None,
                data=None, add_headers=None, headers=None,):
        auth = 'Token token={0}'.format(self.api_key)
        if query_params is None:
            query_params = {}

        if headers is None:
            headers = {
                'Accept': CONTENT_TYPE,
                'Authorization': auth,
                'Content-Type': 'application/json',
            }
        elif not isinstance(headers, dict):
            raise InvalidHeaders(headers)

        if add_headers is not None:
            headers.update(**add_headers)

        for k, v in query_params.copy().items():
            if isinstance(v, stringtype):
                continue
            elif isinstance(v, Number):
                continue
            elif isinstance(v, datetime.datetime):
                query_params[k] = v.isoformat()
            elif isinstance(v, ClientMixin):
                query_params[k] = v['id']
            try:
                iter(v)
            except:
                continue
            key = '%s[]' % k
            query_params.pop(k)
            values = [v_['id'] if isinstance(v_, ClientMixin) else v_
                      for v_ in v]
            query_params[key] = values

        kwargs = {
            'headers': headers,
            'params': query_params,
        }

        if data is not None:
            kwargs['data'] = json.dumps(data)

        return self._do_request(
            method.lower(),
            '/'.join((self.base_url, endpoint)),
            **kwargs
        )
