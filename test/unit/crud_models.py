import os
import os.path
import unittest
import ujson as json

import requests_mock
from mock import Mock

from pypd.mixins import ClientMixin
from pypd.errors import (BadRequest, UnknownError, InvalidResponse,
                         InvalidHeaders)


# ignore methods that aren't tests
requests_mock.Mocker.TEST_PREFIX = 'test_'


@requests_mock.Mocker()
class ClientMixinTestCase(unittest.TestCase):

    def setUp(self):
        self.base_url = 'https://api.pagerduty.com'
        self.endpoint = '/mock'

        class Requester(ClientMixin):
            endpoint = self.endpoint

        self.requester = Requester(base_url=self.base_url)

    def test_request_2xx(self, m):
        url = self.base_url
        m.register_uri('GET', url, json={'status': 'OK'})

    def test_request_4xx(self, m):
        url = self.base_url
        method = 'GET'
        m.register_uri(method, url, status_code=401)
        self.requester.request(method, )
        with self.assertRaises(BadRequest) as ctx:
            self.assertEqual(ctx.exception.code, 401)

    def test_request_404(self, m):
        pass

    def test_request_5xx(self, m):
        pass

    def test_request_invalid_json(self, m):
        pass

    def test_valid_headers(self, m):
        pass

    def test_invalid_headers(self, m):
        pass


# class EntitityTestCase(unittest.TestCase):
#     def setUp(self):
#         self.path = path = os.path.join(
#             os.path.dirname(__file__),
#             'sample_escalation_policies.json'
#         )

#         with open(path, 'r+b') as f:
#             self.json_string = f.read()
#             self.decoded = json.loads(self.json_string)

#     @requests_mock.Mocker()
#     def test_find_success(self):
#         import pypd
#         cls = pypd.EscalationPolicy
#         policies = cls.find()
#         json_policies = map(lambda p: p.json(), policies)
#         self.assertEqual(json_policies, self.decoded['escalation_policies'])

#     def test_fetch_success(self):
#         import pypd
#         policy_dict = self.decoded['escalation_policies'][0]
#         body = json.dumps({'escalation_policy': policy_dict})
#         cls = pypd.EscalationPolicy
#         policy = cls.fetch(policy_dict['id'])
#         self.assertEqual(policy.json(), policy_dict)

#     def test_fetch_fail_403(self):
#         import pypd
#         from pypd.errors import BadRequest
#         cls = pypd.EscalationPolicy
#         body = {'error': {'code': 2001, 'message': 'xxxx', 'errors': []}}
#         with self.assertRaises(BadRequest) as ctx:
#             cls.fetch('notgoingtobefound')
#             self.assertEqual(ctx.exception.code, 2001)

#     def test_fetch_fail_404(self):
#         import pypd
#         from requests.exceptions import HTTPError

#         cls = pypd.EscalationPolicy
#         cls._do_request = self.make_do_request('', 404)
#         with self.assertRaises(HTTPError) as ctx:
#             cls.fetch('notgoingtobefound')
#             self.assertEqual(ctx.exception.code, 404)

#     def test_delete(self):
#         pass

#     def test_update(self):
#         pass


if __name__ == '__main__':
    unittest.main()
