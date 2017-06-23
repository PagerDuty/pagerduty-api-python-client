# Copyright (c) PagerDuty.
# See LICENSE for details.
import json
import unittest
import os.path

import requests_mock

from pypd import Incident, Alert


def get_object_by_id(data, search_id):
    return list(filter(lambda s: s['id'] == search_id, data))[0]


def get_data(data_type, mock_object):
    return {data_type: mock_object}


class AlertTestCase(unittest.TestCase):

    def setUp(self):
        self.base_url = 'https://api.pagerduty.com'
        self.api_key = 'FAUX_API_KEY'
        self.limit = 25
        base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data'
        )
        path = os.path.join(base_path, 'sample_incidents.json')
        with open(path) as f:
            self.incidents_data = json.load(f)

        path = os.path.join(base_path, 'sample_alerts.json')
        with open(path) as f:
            self.alerts_data = json.load(f)

        self.first_incident_id = 'INCIDENT1'
        self.first_incident = get_object_by_id(
            self.incidents_data,
            self.first_incident_id
        )
        self.first_incident_data = get_data('incident', self.first_incident)

        self.second_incident_id = 'INCIDENT2'
        self.second_incident = get_object_by_id(
            self.incidents_data,
            self.second_incident_id
        )
        self.second_incident_data = get_data('incident', self.second_incident)

        self.first_alert_id = 'ALERT1'
        self.first_alert = get_object_by_id(
            self.alerts_data,
            self.first_alert_id
        )
        self.first_alert_data = get_data('alert', self.first_alert)

        self.second_alert_id = 'ALERT2'
        self.second_alert = get_object_by_id(
            self.alerts_data, self.second_alert_id)
        self.second_alert_data = get_data('alert', self.second_alert)

    # test helpers
    def build_incident_url(self, incident_id):
        return '{0}/incidents/{1}'.format(
            self.base_url,
            incident_id,
        )

    def build_incident_alerts_url(self, incident_id):
        return '{0}/incidents/{1}/alerts'.format(
            self.base_url,
            incident_id,
        )

    def build_alert_url(self, incident_id, alert_id):
        return '{0}/incidents/{1}/alerts/{2}'.format(
            self.base_url,
            incident_id,
            alert_id,
        )

    def mock_request(self, m, method, url, payload):
        m.register_uri(
            method,
            url,
            json=payload,
            complete_qs=False
        )

    def mock_get_request(self, m, url, payload):
        self.mock_request(m, 'GET', url, payload)

    def mock_put_request(self, m, url, payload):
        self.mock_request(m, 'PUT', url, payload)

    @requests_mock.Mocker()
    def test_fetch_all_alerts_from_incident(self, m):
        incident_url = self.build_incident_url(self.first_incident_id)
        self.mock_get_request(m, incident_url, self.first_incident_data)

        alerts_url = self.build_incident_alerts_url(self.first_incident_id)
        self.mock_get_request(
            m,
            alerts_url,
            {'alerts': [self.first_alert, self.second_alert, ]}
        )

        incident = Incident.fetch(self.first_incident_id, api_key=self.api_key)
        alerts = incident.alerts()
        alert_ids = [i.id for i in alerts]

        for alert_id in [self.first_alert_id, self.second_alert_id]:
            self.assertIn(alert_id, alert_ids)

    @requests_mock.Mocker()
    def test_fetch_one_from_incident(self, m):
        incident_url = self.build_incident_url(self.first_incident_id)
        self.mock_get_request(m, incident_url, self.first_incident_data)

        incident_alerts_url = self.build_incident_alerts_url(
            self.first_incident_id
        )
        self.mock_get_request(
            m,
            incident_alerts_url,
            {'alerts': [self.first_alert, self.second_alert, ]}
        )

        alert_url = self.build_alert_url(
            self.first_incident_id,
            self.first_alert_id
        )
        self.mock_get_request(m, alert_url, self.first_alert_data)

        incident = Incident.fetch(self.first_incident_id, api_key=self.api_key)
        alerts = incident.alerts()
        alert = Alert.fetch(
            self.first_alert_id,
            incident,
            None,
            api_key=self.api_key
        )

        incident_alert_ids = [i.id for i in alerts]
        self.assertIn(alert.id, incident_alert_ids)

    @requests_mock.Mocker()
    def test_resolve(self, m):
        incident_url = self.build_incident_url(self.first_incident_id)
        self.mock_get_request(m, incident_url, self.first_incident_data)

        alert_url = self.build_alert_url(
            self.first_incident_id,
            self.first_alert_id
        )
        self.mock_get_request(m, alert_url, self.first_alert_data)
        self.mock_put_request(m, alert_url, self.first_alert_data)

        incident = Incident.fetch(self.first_incident_id, api_key=self.api_key)
        alert = Alert.fetch(
            self.first_alert_id,
            incident,
            None,
            api_key=self.api_key
        )
        alert.resolve('nizar@pagerduty.com')

        last_request_json = m.last_request.json()
        self.assertEqual('PUT', m.last_request.method)
        self.assertEqual(self.first_alert_id, last_request_json['alert']['id'])
        self.assertEqual('resolved', last_request_json['alert']['status'])

    @requests_mock.Mocker()
    def test_associate(self, m):
        incident_url = self.build_incident_url(self.first_incident_id)
        self.mock_get_request(m, incident_url, self.first_incident_data)

        second_incident_url = self.build_incident_url(self.second_incident_id)
        self.mock_get_request(
            m,
            second_incident_url,
            self.second_incident_data
        )

        alert_url = self.build_alert_url(
            self.first_incident_id,
            self.first_alert_id
        )
        self.mock_get_request(m, alert_url, self.first_alert_data)
        self.mock_put_request(m, alert_url, self.first_alert_data)

        incident = Incident.fetch(self.first_incident_id, api_key=self.api_key)
        new_incident = Incident.fetch(
            self.second_incident_id,
            api_key=self.api_key
        )
        alert = Alert.fetch(
            self.first_alert_id,
            incident,
            None,
            api_key=self.api_key
        )

        alert.associate('nizar@pagerduty.com', new_incident)

        last_request_json = m.last_request.json()
        self.assertEqual('PUT', m.last_request.method)
        self.assertEqual(self.first_alert_id, last_request_json['alert']['id'])
        self.assertEqual(
            self.second_incident_id,
            last_request_json['alert']['incident']['id']
        )

if __name__ == "__main__":
    unittest.main()
