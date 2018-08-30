from django.test import TestCase, Client
from django.urls import reverse
from django.test.utils import setup_test_environment


class unauthorizedAccessTests(TestCase):
    def test_login(self):
        client = Client()
        print(reverse('classy:index'))
        response = client.get(reverse('classy:index'))
        self.assertEqual(response.status_code, 200)
