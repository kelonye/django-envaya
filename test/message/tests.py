import unittest
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from models import InboxMessage, OutboxMessage


class RequestTestCase(TestCase):

    uri = reverse('receive_incoming')

    def setUp(self):
        self.client = Client()

    def test_must_be_a_post(self):
        res = self.client.get(self.uri)
        self.assertEqual(res.status_code, 405)

    def test_must_have_required_props(self):
        data = {
        }
        res = self.client.post(self.uri, data)
        self.assertEqual(res.status_code, 400)

    def test_must_be_from_the_specified_no(self):
        data = {
              'phone_number': '254700111001'
            , 'action': 'incoming'
        }
        res = self.client.post(self.uri, data)
        self.assertEqual(res.status_code, 403)


class IncomingRequestTestCase(TestCase):

    uri = reverse('receive_incoming')

    def setUp(self):
        self.client = Client()
        def POST(uri, data):
            data.setdefault('phone_number', '254700111000')
            data.setdefault('action', 'incoming')
            return self.client.post(uri, data)
        self.client.POST = POST

    def test_should_have_required_props(self):
        data = {
        }
        res = self.client.POST(self.uri, data)
        self.assertEqual(res.status_code, 400)

    def test_response(self):
        data = {
              'from': '254700111999'
            , 'message_type': ''
            , 'message': ''
            , 'timestamp': ''
        }
        res = self.client.POST(self.uri, data)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        # assert can send to sender
        assert data['events']
        event = data['events'][0]
        assert event['event'] == 'send'
        msg = event['messages'][0]
        assert msg['to'] == '254700111999'
        assert msg['message'] == 'outgoing1'
        # assert can send to other
        msg = event['messages'][1]
        assert msg['to'] == '254700111444'
        assert msg['message'] == 'outgoing2'

@unittest.skip('')
class OutgoingRequestTestCase(TestCase):

    uri = reverse('receive_outgoing')

    def setUp(self):
        self.client = Client()
        def POST(uri, data):
            data.setdefault('phone_number', '254700111000')
            data.setdefault('action', 'outgoing')
            return self.client.post(uri, data)
        self.client.POST = POST
        self.msg = OutboxMessage.objects.create(
              to='254700111999'
            , message='outgoing'
        )

    def test_response(self):
        data = {
        }
        res = self.client.POST(uri, data)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        # assert message is queued
        assert data['events']
        event = data['events'][0]
        assert event['event'] == 'send'
        assert len(event['messages']) == 1
        msg = event['messages'][0]
        assert msg['to'] == '254700111000'
        assert msg['message'] == 'outgoing'