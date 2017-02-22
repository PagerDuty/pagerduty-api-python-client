# Copyright (c) PagerDuty.
# See LICENSE for details.
import re
import json
import unittest
import os.path
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
from operator import itemgetter

import requests_mock

from pypd import EscalationPolicy


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i: i + n]


class EntityTestCase(unittest.TestCase):

    def setUp(self):
        self.base_url = 'https://api.pagerduty.com'
        self.endpoint = 'escalation_policies'
        self.url = '%s/%s' % (self.base_url, self.endpoint,)
        self.api_key = 'FAUX_API_KEY'
        self.limit = 25

        base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data')

        path = os.path.join(base_path, 'sample_escalation_policies.json')
        with open(path) as f:
            self.data = json.load(f)
            self.query_datas = [
                {
                    'limit': self.limit,
                    'offset': n * self.limit,
                    'escalation_policies': chunk,
                }
                for n, chunk in enumerate(chunks(self.data, self.limit))
            ]

        path = os.path.join(base_path, 'sample_services.json')
        with open(path) as f:
            self.service_data = json.load(f)

    @requests_mock.Mocker()
    def test_output_fields(self, m):
        # setup mocked request uris
        query = {
            'limit': self.query_datas[0]['limit'],
            'offset': self.query_datas[0]['offset'],
        }
        url = self.url + '?%s' % urlencode(query)
        m.register_uri('GET', url, json=self.query_datas[0], complete_qs=True)

        eps = EscalationPolicy.find(api_key=self.api_key, fetch_all=True)
        # ensure all the instances are there, as usual
        self.assertEqual(len(eps), len(self.query_datas[0][self.endpoint]))

        for ep in eps:
            # ensure that there is a name field shown for stringified version
            for field in EscalationPolicy.STR_OUTPUT_FIELDS:
                matches = re.findall(r'%s=\"(.+?)\"' % field, str(ep))
                self.assertEqual(matches[0], ep[field])

            matches = re.findall(r'id=\"(.+?)\"', str(ep))
            self.assertEqual(matches[0], ep['id'])

    @requests_mock.Mocker()
    def test_translate_query_params(self, m):
        name = 'Alexis demo EP'
        query = {
            'query': name,
            'limit': self.query_datas[0]['limit'],
            'offset': self.query_datas[0]['offset'],
        }
        url = self.url + '?%s' % urlencode(query)

        # filter the dataset to only include eps with "Alexis" in it
        filtered = list(filter(
            lambda d: d['name'].count('Alexis'),
            self.query_datas[0]['escalation_policies']
        ))
        data = self.query_datas[0].copy()
        data['escalation_policies'] = filtered
        m.register_uri('GET', url, json=data, complete_qs=True)

        # query for the eps
        eps = EscalationPolicy.find(api_key=self.api_key, name=name,)
        self.assertEqual(len(eps), 1)

    @requests_mock.Mocker()
    def test_services(self, m):
        query = {
            'limit': 1,
            'offset': self.query_datas[0]['offset'],
        }
        url = self.url + '?%s' % urlencode(query)
        m.register_uri('GET', url, json=self.query_datas[0], complete_qs=True)

        # get one ep
        ep = EscalationPolicy.find_one(api_key=self.api_key)
        # intersect the escalation policy service data with the service data
        # found in sample_services.json
        service_ids = set(service['id'] for service in self.service_data)
        ep_service_ids = set(service['id'] for service in ep['services'])
        intersect = service_ids.intersection(ep_service_ids)

        # setup fetch url requests with requests_mock using actual data from
        # sample_services.json
        for o in ep['services']:
            url = self.base_url + '/services/' + o['id']
            data = next(iter(filter(
                lambda s: s['id'] in intersect,
                self.service_data
            )))
            data = {'service': data, }
            m.register_uri('GET', url, json=data, complete_qs=True)

        services = ep.services()
        # ensure the number of services were fetched properly
        self.assertEqual(len(services), len(ep['services']))
        # ensure all the proper services are there (by id)
        diff = set(service['id'] for service in services)\
            .difference(set(ep_service_ids))
        self.assertEqual(len(diff), 0)


if __name__ == "__main__":
    unittest.main()
