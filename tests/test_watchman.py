import mock
import unittest

from flask import Flask
from flask.ext.testing import TestCase
from flask_watchman import Watchman


class TestWatchman(TestCase):
    """
    Test flask apps that are using class based views
    """
    def create_app(self):
        app = Flask(__name__, static_folder=None)

        Watchman(app)

        app.config.setdefault('APP_LOGGING', 'MY LOGGING')

        return app

    def test_watchman_routes_exists(self):
        """
        Test that the routes added exist
        """

        r = self.client.options('/version')
        self.assertStatus(r, 200)

        r = self.client.options('/environment')
        self.assertStatus(r, 200)

    @mock.patch('flask_watchman.subprocess')
    def test_version_route_works(self, mocked_subprocess):
        """
        Tests that the version route works
        """
        process = mock.Mock()
        process.communicate.side_effect = [
            ['latest-release', 'error'],
            ['latest-commit', 'error']
        ]
        mocked_subprocess.Popen.return_value = process

        r = self.client.get('/version')
        self.assertStatus(r, 200)

        self.assertTrue(mocked_subprocess.Popen.called)

        self.assertEqual(
            r.json['commit'],
            'latest-commit'
        )

        self.assertEqual(
            r.json['release'],
            'latest-release'
        )

    @mock.patch('flask_watchman.os.environ')
    def test_environment_route_works(self, mocked_environ):
        """
        Tests that the environment route works
        """
        mocked_environ.keys.return_value = ['OS_SHELL']
        mocked_environ.get.return_value = '/bin/favourite-shell'

        r = self.client.get('/environment')
        self.assertStatus(r, 200)

        self.assertEqual(
            r.json['os']['OS_SHELL'],
            '/bin/favourite-shell'
        )

        self.assertEqual(
            r.json['app']['APP_LOGGING'],
            'MY LOGGING'
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
