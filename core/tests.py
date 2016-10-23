from django.core.urlresolvers import reverse
from django.test import TestCase


class TestFrontView(TestCase):
    def test_renders(self):
        response = self.client.get(reverse('core:front'))
        self.assertEqual(response.status_code, 200)


class TestFlatpageListView(TestCase):
    def test_renders(self):
        response = self.client.get(reverse('core:flatpage_list'))
        self.assertEqual(response.status_code, 200)
