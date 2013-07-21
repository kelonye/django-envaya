import unittest
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from models import InboxMessage, OutboxMessage


class RequestTestCase(TestCase):

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
        self.assertEqual(res.content, 'invalid request phone_number\n')

    def test_req_must_have_action_property(self):
        uri = reverse('receive1')
        data = {
            'phone_number': '254700111000'
        }
        res = self.client.post(uri, data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.content, 'invalid request action\n')


class IncomingRequestTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        def POST(uri, data):
            data.setdefault('phone_number', '254700111000')
            data.setdefault('action', 'incoming')
            return self.client.post(uri, data)
        self.client.POST = POST

    def test_response_format(self):
        uri = reverse('receive1')
        data = {
        }
        res = self.client.POST(uri, data)
        self.assertEqual(res.status_code, 400)

        data = {
              'from': '254700111999'
            , 'message_type': ''
            , 'message': ''
            , 'timestamp': ''
        }
        res = self.client.POST(uri, data)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        assert data['events']
        assert data['events'][0]['event'] == 'send'
        assert data['events'][0]['messages']
        msg = data['events'][0]['messages'][0]
        assert msg['to'] == '254700111999'
        assert msg['message'] == 'message1'

        uri = reverse('receive2')
        data = {
              'from': '254700111999'
            , 'message_type': ''
            , 'message': ''
            , 'timestamp': ''
        }
        res = self.client.POST(uri, data)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        assert data['events']
        assert data['events'][0]['event'] == 'send'
        assert data['events'][0]['messages']
        msg = data['events'][0]['messages'][0]
        assert msg['to'] == '254700111444'
        assert msg['message'] == 'message2'
