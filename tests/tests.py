import unittest
import os
import json
from   app import create_app, db, models

localhost = '/'


class SchoolMeTestCase(unittest.TestCase):
    def setUp(self):
        self.app         = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()


class MainTests(SchoolMeTestCase):
    def test_map_200(self):
        """Does the main page return status 200"""
        res = self.client.get(localhost)
        self.assertTrue(res.status_code == 200)


class APITests(SchoolMeTestCase):
    pass
