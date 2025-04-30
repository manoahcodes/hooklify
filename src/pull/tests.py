from django.conf import settings
from django.test import TestCase

class NeonDBTestCase(TestCase):
    def test_db_url(self):
        self.assertTrue(
            hasattr(settings, 'DATABASE_URL'),
            msg="DATABASE_URL is not defined in Django settings."
        )
        self.assertIn("neon.tech", settings.DATABASE_URL)

