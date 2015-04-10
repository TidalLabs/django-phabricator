from django.core.urlresolvers import reverse
from django.test import TestCase
from dj_phab.defaults import get_granularities

class TestContext(TestCase):
    urls = 'dj_phab.urls'

    def test_smoke(self):
        response = self.client.get(reverse('djp-smoke'))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('granularities', context)
        self.assertItemsEqual(context['granularities'], get_granularities())
