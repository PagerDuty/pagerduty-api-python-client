import os
import os.path
import unittest
import ujson as json

from mock import Mock


class ApiCallTestCase(unittest.TestCase):
    def setUp(self):
        from requests.models import Response

        self.path = path = os.path.join(
            os.path.dirname(__file__),
            'sample_escalation_policies.json'
        )

        with open(path, 'r+b') as f:
            self.json_string = f.read()
            self.decoded = json.loads(self.json_string)

        def make_do_request(body, code=200):
            def do_request(self_, requests_method, *args, **kwargs):
                import requests
                response = requests.Response()
                setattr(response, '_content', body)
                setattr(response, 'status_code', code)
                response.url = 'mock://pagerduty.com'
                return response
            return do_request

        self.make_do_request = make_do_request
        self.response_cls = Response

    def test_find_success(self):
        import pypd
        cls = pypd.EscalationPolicy
        cls._do_request = self.make_do_request(self.json_string)
        policies = cls.find()
        json_policies = map(lambda p: p.json(), policies)
        self.assertEqual(json_policies, self.decoded['escalation_policies'])

    def test_fetch_success(self):
        import pypd
        policy_dict = self.decoded['escalation_policies'][0]
        body = json.dumps({'escalation_policy': policy_dict})
        cls = pypd.EscalationPolicy
        cls._do_request = self.make_do_request(body)
        policy = cls.fetch(policy_dict['id'])
        self.assertEqual(policy.json(), policy_dict)

    def test_fetch_fail_403(self):
        import pypd
        from pypd.errors import BadRequest
        cls = pypd.EscalationPolicy
        body = {'error': {'code': 2001, 'message': 'xxxx', 'errors': []}}
        cls._do_request = self.make_do_request(json.dumps(body), 403)
        with self.assertRaises(BadRequest) as ctx:
            cls.fetch('notgoingtobefound')
        self.assertEqual(ctx.exception.code, 2001)

    def test_fetch_fail_404(self):
        import pypd
        from requests.exceptions import HTTPError

        cls = pypd.EscalationPolicy
        cls._do_request = self.make_do_request('', 404)
        with self.assertRaises(HTTPError) as ctx:
            cls.fetch('notgoingtobefound')

    def test_delete(self):
        pass

    def test_update(self):
        pass


if __name__ == '__main__':
    unittest.main()
