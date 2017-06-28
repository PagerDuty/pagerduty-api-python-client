"""Helpful mixins for PagerDuty entity classes."""
import datetime
import logging
from numbers import Number

import requests
import six

from .log import log
from .errors import (BadRequest, UnknownError, InvalidResponse, InvalidHeaders)


CONTENT_TYPE = 'application/vnd.pagerduty+json;version=2'
AUTH_TEMPLATE = 'Token token={0}'
BASIC_AUTH_TEMPLATE = 'Basic {0}'


class ClientMixin(object):
    api_key = None
    base_url = None
    proxies = None

    def __init__(self, api_key=None, base_url=None, proxies=None):
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

        if not proxies:
            from pypd import proxies

        self.proxies = proxies

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
            response = response.json()
        except:
            raise InvalidResponse(response.text)

        return response

    def _do_request(self, method, *args, **kwargs):
        """
        Modularized because API was broken.

        Need to be able to inject Mocked response objects here.
        """
        log('Doing HTTP [{3}] request: {0} - headers: {1} - payload: {2}'.format(
            args[0], kwargs.get('headers'), kwargs.get('json'), method,),
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
            if isinstance(v, six.string_types):
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
            'proxies': self.proxies,
        }

        if data is not None:
            kwargs['json'] = data

        return self._do_request(
            method.lower(),
            '/'.join((self.base_url, endpoint)),
            **kwargs
        )
