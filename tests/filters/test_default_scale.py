from unittest import TestCase
import mock

from marathon.models.app import MarathonApp
from hollowman.filters.default_scale import DefaultScaleRequestFilter
from tests import RequestStub
from os import getcwd
from json import loads


class DefaultScaleRequestFilterTest(TestCase):

    def setUp(self):
        self.filter = DefaultScaleRequestFilter()
        self.marathon_client_patch = mock.patch('hollowman.filters.default_scale.MarathonClient')

        self.marathon_client_mock = self.marathon_client_patch.start()
        full_app_data = loads(open('json/single_full_app.json').read())
        self.marathon_client_mock.return_value.get_app.return_value = MarathonApp(**full_app_data)

    def tearDown(self):
        self.marathon_client_patch.stop()

    def test_suspend_a_running_app(self):
        _data = {
            "instances": 0
        }
        request = RequestStub(
            data=_data,
            method='POST',
            path='/v2/apps//foo'
        )

        result_request = self.filter.run(request)

        self.assertTrue('labels' in result_request.get_json())
        self.assertEqual(2, result_request.get_json()['labels']['hollowman.default_scale'])


    def test_suspend_a_running_app_with_labels(self):
        _data = {
            "instances": 0,
            "labels": {
                "owner": "zeus"
            }
        }
        request = RequestStub(
            data=_data,
            method='POST',
            path='/v2/apps//foo'
        )

        result_request = self.filter.run(request)

        self.assertTrue('labels' in result_request.get_json())
        self.assertEqual(2, result_request.get_json()['labels']['hollowman.default_scale'])
        self.assertEqual("zeus", result_request.get_json()['labels']['owner'])

    def test_suspend_and_already_suspended_app(self):
        """
        In this case we must not override the value o labels.hollowman.default_scale.
        """
        _data = {
            "instances": 0
        }
        request = RequestStub(
            data=_data,
            method='POST',
            path='/v2/apps//foo'
        )

        with mock.patch('hollowman.filters.default_scale.MarathonClient') as marathon_client:
            marathon_client.return_value.get_app.return_value.instances = 0
            result_request = self.filter.run(request)

            self.assertFalse('labels' in result_request.get_json())

    def test_create_label_on_app_without_labels(self):
        _data = {
            "instances": 0
        }
        request = RequestStub(
            data=_data,
            method='POST',
            path='/v2/apps//foo'
        )

        result_request = self.filter.run(request)

        self.assertTrue('labels' in result_request.get_json())
        self.assertEqual(2, result_request.get_json()['labels']['hollowman.default_scale'])

    def test_get_current_scale(self):
        current_scale = self.filter.get_current_scale('/foo')
        self.assertEqual(current_scale, 2)

    def test_get_app_id(self):
        self.assertEqual('/foo', self.filter.get_app_id('/v2/apps//foo'))
        self.assertEqual('/foo/taz/bar', self.filter.get_app_id('/v2/apps//foo/taz/bar'))