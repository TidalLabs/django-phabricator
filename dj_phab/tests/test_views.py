from django.test import TestCase
from django.core.urlresolvers import reverse

class TestSmoke(TestCase):
    urls = 'dj_phab.urls'

    def test_smoke(self):
        response = self.client.get(reverse('smoke'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u"Hi Django-Phabricator!")
