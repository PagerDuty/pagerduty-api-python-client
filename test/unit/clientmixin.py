# Copyright (c) PagerDuty.
# See LICENSE for details.
import unittest

import requests_mock
from requests import HTTPError

from pypd.mixins import ClientMixin
from pypd.errors import (BadRequest, UnknownError, InvalidResponse,
                         InvalidHeaders)


# ignore methods that aren't tests
requests_mock.Mocker.TEST_PREFIX = 'test_'


@requests_mock.Mocker()
class ClientMixinTestCase(unittest.TestCase):

    def setUp(self):
        self.base_url = 'https://api.pagerduty.com'
        self.endpoint = 'mock'
        self.url = '%s/%s' % (self.base_url, self.endpoint,)

        class Requester(ClientMixin):
            endpoint = self.endpoint

        self.requester = Requester(base_url=self.base_url)

    def test_request_2xx(self, m):
        method = 'GET'
        body = {'status': 'OK'}
        m.register_uri(method, self.url, json=body)
        result = self.requester.request(method, self.endpoint)
        self.assertEqual(body, result)

    def test_request_4xx(self, m):
        method = 'GET'
        m.register_uri(method, self.url, status_code=401)
        self.assertRaises(
            BadRequest,
            self.requester.request, method, self.endpoint)

    def test_request_404(self, m):
        method = 'GET'
        m.register_uri(method, self.url, status_code=404)

        self.assertRaises(
            HTTPError,
            self.requester.request, method, self.endpoint
        )

    def test_request_5xx(self, m):
        method = 'GET'
        m.register_uri(method, self.url, status_code=500)

        self.assertRaises(
            UnknownError,
            self.requester.request, method, self.endpoint
        )

    def test_request_invalid_json(self, m):
        method = 'GET'
        m.register_uri(method, self.url, text='{"1"}')

        self.assertRaises(
            InvalidResponse,
            self.requester.request, method, self.endpoint
        )

    def test_valid_headers(self, m):
        method = 'GET'
        m.register_uri(method, self.url)
        self.requester.request(method, self.endpoint)

    def test_invalid_headers(self, m):
        method = 'GET'
        m.register_uri(method, self.url)

        self.assertRaises(
            InvalidHeaders,
            self.requester.request, method, self.endpoint,
            headers=''
        )

    def test_statuses_array(self, m):
        method = 'GET'
        body = {'status': 'OK'}
        url = '%s?statuses[]=triggered&statuses[]=acknowledged' % self.url
        m.register_uri(method, url, json=body)
        result = self.requester.request(method, self.endpoint,
                                        query_params={'statuses': ['triggered',
                                                                   'acknowledged']})
        self.assertEqual(body, result)

if __name__ == '__main__':
    unittest.main()
