import unittest
import os
import json
from   app import create_app, models

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
        """Is the main page up, and returning 200"""
        res = self.client.get(localhost)
        self.assertTrue(res.status_code == 200)


class APITests(SchoolMeTestCase):
    def test_get_schools_200(self):
        """Does the school API return 200 and the correct result for Rooftop"""
        roof      = models.School.query.filter_by(cds_code=u'38684786089775').first()
        roof_dict = roof.as_dict(ensure_strings = True)
        res       = self.client.get(os.path.join(localhost, 'api', 'schools', '38684786089775'))
        data      = json.loads(res.data)
        self.assertTrue(res.status_code == 200 and data == roof_dict)

    def test_get_schools_404(self):
        """Does the school API return 404"""
        res = self.client.get(os.path.join(localhost, 'api' 'schools', '12345678'))
        self.assertTrue(res.status_code == 404)

    def test_get_districts_200(self):
        """Does the district API return 200 and the correct result for SFUSD"""
        sfusd      = models.District.query.filter_by(cds_code=u'38684780000000').first()
        sfusd_dict = sfusd.as_dict(ensure_strings = True)
        res        = self.client.get(os.path.join(localhost, 'api', 'districts', '38684780000000'))
        data       = json.loads(res.data)
        self.assertTrue(res.status_code == 200 and data == sfusd_dict)

    def test_get_districts_404(self):
        """Does the district API return 404"""
        res = self.client.get(os.path.join(localhost, 'api' 'districts', '12345678'))
        self.assertTrue(res.status_code == 404)
