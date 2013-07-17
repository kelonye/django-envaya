import unittest
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from models import User
from envaya import json

FIXTURES = (
    'users'
)

class EnvayaT(TestCase):

    fixtures = FIXTURES

    def setUp(self):
        self.client = Client()

    def test_cannot_get(self):
        uri = reverse('receive1')
        res = self.client.get(uri)
        self.assertEqual(res.status_code, 405)

    def test_req_must_have_phone_number(self):
        uri = reverse('receive1')
        data = {
        }
        res = self.client.post(uri, data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.content, 'invalid request phone_number')

    def test_response_format(self):
        uri = reverse('receive1')
        data = {
            'phone_number': '254700111000'
        }
        res = self.client.post(uri, data)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        assert data['events']
        assert data['events'][0]['event'] == 'send'
        assert data['events'][0]['messages']

    def test_send_to_phone_number(self):
        uri = reverse('receive1')
        data = {
            'phone_number': '254700111000'
        }
        res = self.client.post(uri, data)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'message1')

    def test_send_back_to_sender(self):

        uri = reverse('receive2')
        data = {
            'phone_number': '254700111000'
        }
        res = self.client.post(uri, data)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'message2')
