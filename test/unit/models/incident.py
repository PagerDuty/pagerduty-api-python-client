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

from pypd import Incident
from pypd.errors import InvalidArguments, MissingFromEmail


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i: i + n]


class IncidentTestCase(unittest.TestCase):
    """Tests for Incident model specific cases."""

    def setUp(self):
        """Setup the test case."""
        self.base_url = 'https://api.pagerduty.com'
        self.endpoint = 'incidents'
        self.url = '{0}/{1}'.format(self.base_url, self.endpoint)
        self.api_key = 'FAUX_API_KEY'
        self.limit = 25

        self.base_path = base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data')

        path = os.path.join(base_path, 'sample_incidents.json')
        with open(path) as f:
            self.data = json.load(f)
            self.query_datas = [
                {
                    'limit': self.limit,
                    'offset': n * self.limit,
                    'incidents': chunk,
                }
                for n, chunk in enumerate(chunks(self.data, self.limit))
            ]

        path = os.path.join(base_path, 'sample_services.json')
        with open(path) as f:
            self.service_data = json.load(f)

    @requests_mock.Mocker()
    def test_resolve_invalid_from_email(self, m):
        """Coverage for using an invalid (cheaply validated) from email."""
        query = {
            'limit': 1,
            'offset': 0,
        }
        url = self.url + '?{}'.format(urlencode(query))
        m.register_uri('GET', url, json=self.query_datas[0], complete_qs=True)
        incident = Incident.find_one(api_key=self.api_key)
        resolution = 'Incident was resolved manually.'

        with self.assertRaises(MissingFromEmail):
            incident.resolve(None)
        with self.assertRaises(MissingFromEmail):
            incident.resolve(None, resolution=resolution)
        with self.assertRaises(MissingFromEmail):
            incident.resolve(1, resolution=resolution)
        with self.assertRaises(MissingFromEmail):
            incident.resolve(incident, resolution=resolution)

    @requests_mock.Mocker()
    def test_resolve_valid(self, m):
        """Coverage for using a valid (cheaply validated) email."""
        query = {
            'limit': 1,
            'offset': 0,
        }
        url = self.url + '?{}'.format(urlencode(query))
        m.register_uri('GET', url, json=self.query_datas[0], complete_qs=True)
        incident = Incident.find_one(api_key=self.api_key)
        path = os.path.join(
            self.base_path,
            'sample_incident_resolve_response.json'
        )
        with open(path) as f:
            resolve_response = json.load(f)
            resolution = resolve_response['incidents'][0]['resolve_reason']

        url = '{0}/{1}'.format(self.url, incident['id'])
        m.register_uri('PUT', url, json=resolve_response, complete_qs=True)
        response = incident.resolve('jdc@pagerduty.com', resolution=resolution)
        self.assertEqual(incident['id'], response['incidents'][0]['id'])

    @requests_mock.Mocker()
    def test_reassign_invalid_from_email(self, m):
        """Coverage for using an invalid (cheaply validated) from email."""
        query = {
            'limit': 1,
            'offset': 0,
        }
        url = self.url + '?{}'.format(urlencode(query))
        m.register_uri('GET', url, json=self.query_datas[0], complete_qs=True)
        incident = Incident.find_one(api_key=self.api_key)

        with self.assertRaises(MissingFromEmail):
            incident.reassign(None, ['foo'])
        with self.assertRaises(MissingFromEmail):
            incident.reassign(1, ['foo'])
        with self.assertRaises(MissingFromEmail):
            incident.reassign(incident, ['foo'])

    @requests_mock.Mocker()
    def test_reassign_invalid_user_id(self, m):
        """Coverage for using an invalid (cheaply validated) assignee."""
        query = {
            'limit': 1,
            'offset': 0,
        }
        url = self.url + '?{}'.format(urlencode(query))
        m.register_uri('GET', url, json=self.query_datas[0], complete_qs=True)
        incident = Incident.find_one(api_key=self.api_key)

        with self.assertRaises(InvalidArguments):
            incident.reassign('jdc@pagerduty.com', None)
        with self.assertRaises(InvalidArguments):
            incident.reassign('jdc@pagerduty.com', 1)
        with self.assertRaises(InvalidArguments):
            incident.reassign('jdc@pagerduty.com', 'foo')
        with self.assertRaises(InvalidArguments):
            incident.reassign('jdc@pagerduty.com', [None])
        with self.assertRaises(InvalidArguments):
            incident.reassign('jdc@pagerduty.com', [1])

    @requests_mock.Mocker()
    def test_snooze_invalid_from_email(self, m):
        """Coverage for invalid from email for snooze."""
        query = {
            'limit': 1,
            'offset': 0,
        }
        url = self.url + '?{}'.format(urlencode(query))
        m.register_uri('GET', url, json=self.query_datas[0], complete_qs=True)
        incident = Incident.find_one(api_key=self.api_key)
        duration = 3600

        with self.assertRaises(MissingFromEmail):
            incident.snooze(None, duration=duration)
        with self.assertRaises(MissingFromEmail):
            incident.snooze(1, duration=duration)
        with self.assertRaises(MissingFromEmail):
            incident.snooze(incident, duration=duration)

    @requests_mock.Mocker()
    def test_snooze_valid(self, m):
        """Coverage for valid snooze."""
        query = {
            'limit': 1,
            'offset': 0,
        }
        url = self.url + '?{}'.format(urlencode(query))
        m.register_uri('GET', url, json=self.query_datas[0], complete_qs=True)
        incident = Incident.find_one(api_key=self.api_key)
        path = os.path.join(
            self.base_path,
            'sample_incident_snooze_response.json'
        )
        duration = 3600
        with open(path) as f:
            snooze_response = json.load(f)

        url = '{0}/{1}/snooze'.format(self.url, incident['id'])
        m.register_uri('POST', url, json=snooze_response, complete_qs=True)
        snoozed_incident = incident.snooze(
            'jdc@pagerduty.com',
            duration=duration
        )
        self.assertEqual(incident['id'], snoozed_incident['id'])

    @requests_mock.Mocker()
    def test_note_invalid_from_email(self, m):
        """Coverage for invalid from email for notes."""
        query = {
            'limit': 1,
            'offset': 0,
        }
        url = self.url + '?{}'.format(urlencode(query))
        m.register_uri('GET', url, json=self.query_datas[0], complete_qs=True)
        incident = Incident.find_one(api_key=self.api_key)
        content = 'Some notes, derp.'

        with self.assertRaises(MissingFromEmail):
            incident.create_note(None, content=content)
        with self.assertRaises(MissingFromEmail):
            incident.create_note(1, content=content)
        with self.assertRaises(MissingFromEmail):
            incident.create_note(incident, content=content)

    @requests_mock.Mocker()
    def test_create_note_valid(self, m):
        """Coverage for valid snooze."""
        query = {
            'limit': 1,
            'offset': 0,
        }
        url = self.url + '?{}'.format(urlencode(query))
        m.register_uri('GET', url, json=self.query_datas[0], complete_qs=True)
        incident = Incident.find_one(api_key=self.api_key)
        path = os.path.join(
            self.base_path,
            'sample_incident_create_note_response.json'
        )
        with open(path) as f:
            create_response = json.load(f)
            content = create_response['note']['content']

        url = '{0}/{1}/notes'.format(self.url, incident['id'])
        m.register_uri('POST', url, json=create_response, complete_qs=True)
        note = incident.create_note(
            'jdc@pagerduty.com',
            content=content
        )
        self.assertNotEqual(incident['id'], note['id'])
        self.assertEqual(content, note['content'])
