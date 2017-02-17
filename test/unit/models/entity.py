# Copyright (c) PagerDuty.
# See LICENSE for details.
import unittest
try:
    from urllib import urlencode
except:
    from urllib.parse import urlencode

import requests_mock

from pypd.models.entity import Entity


class EntityTestCase(unittest.TestCase):

    def setUp(self):
        self.base_url = 'https://api.pagerduty.com'
        self.endpoint = 'entities'
        self.url = '%s/%s' % (self.base_url, self.endpoint)
        self.api_key = 'FAUX_API_KEY'
        self.limit = 1
        self.total = None
        self.responses_data = [
            {
                'limit': self.limit,
                'offset': 0,
                'total': self.total,
                'more': True,
                'entities': [
                    {
                        'id': 'id1234',
                        'name': 'Entity 1'
                    }
                ]
            },
            {
                'limit': self.limit,
                'offset': 1,
                'total': self.total,
                'more': False,
                'entities': [
                    {
                        'id': 'id5678',
                        'name': 'Entity 2',
                    }
                ]
            }
        ]

        class TestEntity(Entity):
            endpoint = self.endpoint

        self.cls = TestEntity

    def test_sanitize_endpoint(self):
        class PluralEndpoint(Entity):
            endpoint = 'plurals'

        class PluralEndsInYEndpoint(Entity):
            endpoint = 'pluraly'

        class PluralEndsNotWithSEndpoint(Entity):
            endpoint = 'plural'

        class SingularEndpoint(Entity):
            endpoint = 'singular'

        class SingularEndpointEndsWithIes(Entity):
            endpoint = 'singularies'

        class SingularEndpointEndswithS(Entity):
            endpoint = 'singulars'

        plural_cases = [
            (PluralEndpoint, 'plurals'),
            (PluralEndsInYEndpoint, 'pluralies'),
            (PluralEndsNotWithSEndpoint, 'plurals'),
        ]

        singular_cases = [
            (SingularEndpoint, 'singular'),
            (SingularEndpointEndsWithIes, 'singulary'),
            (SingularEndpointEndswithS, 'singular'),
        ]

        for cls, expected_result in plural_cases:
            self.assertEqual(
                cls.sanitize_ep(cls.endpoint, plural=True),
                expected_result
            )

        for cls, expected_result in singular_cases:
            self.assertEqual(
                cls.sanitize_ep(cls.endpoint),
                expected_result
            )

    @requests_mock.Mocker()
    def test_fetch_page(self, m):
        method = 'GET'
        limit = 25
        offset = 0
        more = False
        total = None

        # define endpoint entity data
        entities_data = {
            'limit': limit,
            'offset': offset,
            'total': total,
            'more': more,
            'entities': [
                {
                    'id': 'id1234'
                }
            ]
        }

        # register request mock url with resultant data
        m.register_uri(method, self.url, json=entities_data)
        entities, response = self.cls._fetch_page(
            api_key=self.api_key,
        )

        self.assertTrue(isinstance(entities[0], self.cls))
        self.assertEqual(len(entities), len(entities_data['entities']))
        self.assertEqual(response['total'], None)
        self.assertEqual(response['more'], False)
        self.assertEqual(response['limit'], limit)
        self.assertEqual(response['offset'], offset)

    @requests_mock.Mocker()
    def test_fetch_all(self, m):
        # setup mocked request uris
        for data in self.responses_data:
            query = {
                'limit': data['limit'],
                'offset': data['offset'],
            }
            url = self.url + '?%s' % urlencode(query)
            m.register_uri('GET', url, json=data, complete_qs=True)

        # fetch all entities from endpoint
        entities = self.cls._fetch_all(
            api_key=self.api_key,
            limit=self.limit,
        )

        # ensure result is all instances of self.cls and that data on the
        # instances is correct
        for n, entity in enumerate(entities):
            self.assertTrue(isinstance(entity, self.cls))
            self.assertEqual(
                entity['id'],
                self.responses_data[n]['entities'][0]['id']
            )

        # ensure that the result is actually all of the results
        self.assertEqual(
            len(entities),
            len(self.responses_data[0]['entities']) +
            len(self.responses_data[1]['entities'])
        )

    @requests_mock.Mocker()
    def test_find(self, m):
        # setup mocked request uris
        for data in self.responses_data:
            query = {
                'limit': data['limit'],
                'offset': data['offset'],
            }
            url = self.url + '?%s' % urlencode(query)
            m.register_uri('GET', url, json=data, complete_qs=True)

        # try excluding by id
        class ExcludeById(Entity):
            endpoint = 'entities'
            EXCLUDE_FILTERS = ('id',)

        entities = ExcludeById.find(
            api_key=self.api_key,
            limit=self.limit,
            exclude=('id1234',),
        )

        # expect that only 1 (of 2) entities will show up
        self.assertEqual(len(entities), 1)
        # ensure that the 1 result is not the excluded one
        self.assertNotEqual(entities[0]['id'], 'id1234')

        # try excluding by just name
        class ExcludeByName(Entity):
            endpoint = 'entities'

        entities = ExcludeByName.find(
            api_key=self.api_key,
            limit=self.limit,
            exclude=('Entity 2',),
        )

        # expect that only 1 (of 2) entities will show up
        self.assertEqual(len(entities), 1)
        # ensure that the 1 result is not the excluded one
        self.assertNotEqual(entities[0]['name'], 'Entity 2')

        # try exlcuding by id, but only with only 'name' exclude filter
        entities = ExcludeByName.find(
            api_key=self.api_key,
            limit=self.limit,
            exclude=('id1234',),
        )

        # expect that only 1 (of 2) entities will show up
        self.assertEqual(len(entities), 2)

        # try excluding by custom function
        class ExcludeByCallable(Entity):
            endpoint = 'entities'
            EXCLUDE_FILTERS = [
                lambda cls, item, ev: item.get('name').count(ev),
            ]

        entities = ExcludeByCallable.find(
            api_key=self.api_key,
            limit=self.limit,
            exclude=('Entity 1',),
        )

        # expect that only 1 (of 2) entities will show up
        self.assertEqual(len(entities), 1)
        # expect that the excluded one is correctly Entity 1
        self.assertNotEqual(entities[0]['name'], 'Entity 1')

    def test_translate_query_params_with_name(self):
        class TranslateNameQueryParam(Entity):
            TRANSLATE_QUERY_PARAM = ('name',)

        kwargs = {
            'name': 'PagerDuty',
        }

        # ensure fallback query works using TRANSLATE_QUERY_PARAM
        qp = TranslateNameQueryParam.translate_query_params(**kwargs)
        self.assertEqual(qp['query'], kwargs['name'])
        self.assertNotIn('name', qp)


    def test_translate_query_params_with_name_and_query(self):
        class TranslateNameQueryParam(Entity):
            TRANSLATE_QUERY_PARAM = ('name',)

        kwargs = {
            'name': 'PagerDuty',
            'query': 'PlopperDuty',
        }

        qp = TranslateNameQueryParam.translate_query_params(**kwargs)
        self.assertEqual(qp['query'], kwargs['query'])
        self.assertNotIn('name', qp)


    def test_translate_query_params_with_name_and_query_no_translation(self):
        class TranslateNameQueryParam(Entity):
            TRANSLATE_QUERY_PARAM = None

        kwargs = {
            'name': 'PagerDuty',
            'query': 'PlopperDuty',
        }

        qp = TranslateNameQueryParam.translate_query_params(**kwargs)
        self.assertEqual(qp['query'], kwargs['query'])
        self.assertEqual(qp['name'], kwargs['name'])

    @requests_mock.Mocker()
    def test_parse(self, m):
        # setup mocked request uris
        for data in self.responses_data:
            query = {
                'limit': 1,
                'offset': data['offset'],
            }
            url = self.url + '?%s' % urlencode(query)
            m.register_uri('GET', url, json=data, complete_qs=True)

        # define a class to test parsing using parse as a string
        class TestParseString(Entity):
            endpoint = 'entities'
            parse = 'entities'

        # fetch the entities
        entities = TestParseString.find(api_key=self.api_key, maximum=1,)
        # ensure that there is only 1 result (maximum)
        self.assertEqual(len(entities), 1)

        # for each entity ensure instance of TestParseString, and data is valid
        for n, entity in enumerate(entities):
            self.assertEqual(
                entities[n]['id'],
                self.responses_data[n]['entities'][0]['id']
            )
            self.assertTrue(isinstance(entities[n], TestParseString))

        # class to test parse implemented as a classmethod
        class TestParseFunction(Entity):
            endpoint = 'entities'

            @classmethod
            def parse(cls, data):
                return data['entities']

        # fetch entities
        entities = TestParseFunction.find(api_key=self.api_key, limit=1,
                                          maximum=1)
        # ensure only one was returned
        self.assertEqual(len(entities), 1)

        # for each entity ensure instance of TestParseFunction and that
        # returned data is valid
        for n, entity in enumerate(entities):
            self.assertEqual(
                entities[n]['id'],
                self.responses_data[n]['entities'][0]['id']
            )
            self.assertTrue(isinstance(entities[n], TestParseFunction))


if __name__ == '__main__':
    unittest.main()
