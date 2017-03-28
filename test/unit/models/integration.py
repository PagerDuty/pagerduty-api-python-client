# Copyright (c) PagerDuty.
# See LICENSE for details.
import json
import unittest
import os.path

import requests_mock

from pypd import Integration, Service
from pypd.errors import (InvalidEndpointOperation, InvalidEndpoint,
                         InvalidArguments)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i: i + n]


class IntegrationTestCase(unittest.TestCase):

    def setUp(self):
        self.base_url = 'https://api.pagerduty.com'
        self.api_key = 'FAUX_API_KEY'
        self.limit = 25
        base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data')
        path = os.path.join(base_path, 'sample_services.json')
        with open(path) as f:
            self.service_data = json.load(f)

        path = os.path.join(base_path, 'sample_integrations.json')
        with open(path) as f:
            self.integration_data = json.load(f)

        # use a particular service because of not wanting to enumerate multiple
        # integration endpoints in json
        self.service_id = 'P91VIE2'
        self.service = list(filter(
            lambda s: s['id'] == self.service_id,
            self.service_data,
        ))[0]

        self.service_data = {
            'service': self.service,
        }

        self.integration = list(filter(
            lambda i: i['service']['id'] == self.service_id,
            self.integration_data,
        ))[0]

        self.integration_id = self.integration['id']

    @requests_mock.Mocker()
    def test_fetch_all_from_service(self, m):
        # setup mocked request uris
        service_url = '{0}/services/{1}'.format(
            self.base_url,
            self.service_id,
        )

        for integration in self.integration_data:
            integration_url = '{0}/integrations/{1}'.format(
                service_url,
                integration['id']
            )

            m.register_uri(
                'GET',
                integration_url,
                json={'integration': integration},
                complete_qs=False
            )

        m.register_uri(
            'GET',
            service_url,
            json=self.service_data,
            complete_qs=False
        )

        service = Service.fetch(self.service_id, api_key=self.api_key)
        integrations = service.integrations()
        integration_ids = [i.id for i in integrations]
        service_data_integration_ids = [
            i['id'] for i in service['integrations']
        ]

        for integration_id in integration_ids:
            self.assertIn(integration_id, service_data_integration_ids)

        for integration in integrations:
            self.assertEqual(integration['service']['id'], self.service_id)

    @requests_mock.Mocker()
    def test_fetch_one_from_service(self, m):
        # setup mocked request uris
        integration_id = 'P1ONR10'
        service_url = '{0}/services/{1}'.format(
            self.base_url,
            self.service_id,
        )

        integration_data = self.integration_data[0]

        integration_url = '{0}/integrations/{1}'.format(
            service_url,
            integration_data['id']
        )

        m.register_uri(
            'GET',
            integration_url,
            json={'integration': integration_data},
            complete_qs=False
        )

        m.register_uri(
            'GET',
            service_url,
            json=self.service_data,
            complete_qs=False
        )

        service = Service.fetch(self.service_id, api_key=self.api_key)
        integration = service.get_integration(integration_id)
        self.assertEqual(integration['service']['id'], service.id)
        self.assertEqual(
            integration['type'],
            'event_transformer_api_inbound_integration_reference'
        )
        Integration.validate(integration._data)
        self.assertDictEqual(integration._data, integration_data)

    @requests_mock.Mocker()
    def test_fetch_with_service_id(self, m):
        # setup mocked request uris
        integration_id = 'P1ONR10'
        integration_data = self.integration_data[0]

        service_url = '{0}/services/{1}'.format(
            self.base_url,
            self.service_id,
        )

        integration_url = '{0}/integrations/{1}'.format(
            service_url,
            integration_data['id']
        )

        m.register_uri(
            'GET',
            integration_url,
            json={'integration': integration_data},
            complete_qs=False
        )

        service_id = integration_data['service']['id']
        integration = Integration.fetch(integration_id, service=service_id)
        self.assertDictEqual(integration._data, integration_data)

    @requests_mock.Mocker()
    def test_fetch_with_service(self, m):
        # setup mocked request uris
        integration_id = 'P1ONR10'
        service_url = '{0}/services/{1}'.format(
            self.base_url,
            self.service_id,
        )

        integration_data = self.integration_data[0]

        integration_url = '{0}/integrations/{1}'.format(
            service_url,
            integration_data['id']
        )

        m.register_uri(
            'GET',
            integration_url,
            json={'integration': integration_data},
            complete_qs=False
        )

        m.register_uri(
            'GET',
            service_url,
            json=self.service_data,
            complete_qs=False
        )

        service = Service.fetch(self.service_id, api_key=self.api_key)
        integration = Integration.fetch(integration_id, service=service)
        self.assertDictEqual(integration._data, integration_data)

    @requests_mock.Mocker()
    def test_delete_and_remove(self, m):
        integration_id = 'P1ONR10'
        service_url = '{0}/services/{1}'.format(
            self.base_url,
            self.service_id,
        )
        integration_data = self.integration_data[0]

        integration_url = '{0}/integrations/{1}'.format(
            service_url,
            integration_data['id']
        )

        m.register_uri(
            'GET',
            integration_url,
            json={'integration': integration_data},
            complete_qs=False
        )

        integration = Integration.fetch(integration_id,
                                        service=self.service_id)

        with self.assertRaises(InvalidEndpoint):
            Integration.delete(integration_id)

        with self.assertRaises(InvalidEndpointOperation):
            integration.remove()

    @requests_mock.Mocker()
    def test_validate_valid(self, m):
        integration_data = self.integration_data[0]
        Integration.validate(integration_data)

        for allowed_type in Integration.ALLOWED_INTEGRATION_TYPES:
            data = integration_data.copy()
            data['type'] = allowed_type
            Integration.validate(data)

    @requests_mock.Mocker()
    def test_validate_invalid(self, m):
        integration_data = self.integration_data[0].copy()
        integration_data['type'] = 'invalidtype'

        with self.assertRaises(AssertionError):
            Integration.validate(integration_data)

        with self.assertRaises(AssertionError):
            Integration.validate(None)

    @requests_mock.Mocker()
    def test_create_invalid(self, m):
        integration_data = self.integration_data[0]

        service_url = '{0}/services/{1}'.format(
            self.base_url,
            self.service_id,
        )

        integration_url = '{0}/integrations/{1}'.format(
            service_url,
            integration_data['id']
        )

        m.register_uri(
            'POST',
            integration_url,
            json={'integration': integration_data},
            complete_qs=False
        )

        with self.assertRaises(InvalidArguments):
            Integration.create(service=None, data=integration_data)

    @requests_mock.Mocker()
    def test_create_valid(self, m):
        integration_data = self.integration_data[0].copy()
        integration_data.pop('created_at', None)
        integration_data.pop('id', None)

        service_url = '{0}/services/{1}'.format(
            self.base_url,
            self.service_id,
        )
        create_url = '{0}/integrations'.format(service_url)

        m.register_uri(
            'POST',
            create_url,
            json={'integration': integration_data},
            complete_qs=False
        )

        Integration.create(service=self.service_id, data=integration_data)


if __name__ == "__main__":
    unittest.main()
