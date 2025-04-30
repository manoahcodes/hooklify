from django.conf import settings
from django.test import TestCase

class NeonDBTestCase(TestCase):
    def test_db_url(self):
        self.assertIn("postgres", settings.DATABASE_URL)

