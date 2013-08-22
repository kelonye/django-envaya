import unittest
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from lib.models import InboxMessage, OutboxMessage


class TestCase(TestCase):

    uri = reverse('receive')

class RequestTestCase(TestCase):

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
            , 'password': 't'
            , 'action': 'incoming'
        }
        res = self.client.post(self.uri, data)
        self.assertEqual(res.status_code, 403)


class TestRequestTestCase(TestCase):

    def test_must_return_ok(self):
        data = {
              'phone_number': '254700111000'
            , 'action': 'test'
        }
        client = Client()
        res = client.post(self.uri, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content, 'OK')


class IncomingRequestTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        def POST(uri, data):
            data.setdefault('phone_number', '254700111000')
            data.setdefault('action', 'incoming')
            return self.client.post(uri, data)
        self.POST = POST

    def test_should_have_required_props(self):
        data = {
        }
        res = self.POST(self.uri, data)
        self.assertEqual(res.status_code, 400)

    def test_response(self):
        data = {
              'from': '254700111999'
            , 'message_type': ''
            , 'message': 'hello'
            , 'timestamp': ''
        }
        res = self.POST(self.uri, data)
        self.assertEqual(res.status_code, 200)
        #
        # assert req was logged
        assert InboxMessage.objects.all().count() == 1
        msg = InboxMessage.objects.get()
        assert msg.message == 'hello'
        assert msg.frm == '254700111999'
        #
        # res data
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


class OutgoingRequestTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        def POST(uri, data):
            data.setdefault('phone_number', '254700111000')
            data.setdefault('action', 'outgoing')
            return self.client.post(uri, data)
        self.POST = POST

    def test_response(self):
        OutboxMessage.objects.create(
              to='254700111222'
            , message='outgoing'
            , send_status='queued'
        )
        OutboxMessage.objects.create(
              to='254700111333'
            , message='outgoing'
            , send_status='failed'
        )
        OutboxMessage.objects.create(
              to='254700111444'
            , message='outgoing'
            , send_status='cancelled'
        )
        OutboxMessage.objects.create(
              to='254700111555'
            , message='outgoing'
            , send_status='sent'
        )
        data = {
        }
        res = self.POST(self.uri, data)
        self.assertEqual(res.status_code, 200)
        # res data
        data = json.loads(res.content)
        # assert message is queued
        assert data['events']
        event = data['events'][0]
        assert event['event'] == 'send'
        # assert queued up only 1 unsent msg
        assert len(event['messages']) == 1
        msg = event['messages'][0]
        assert msg['to'] == '254700111222'
        assert msg['message'] == 'outgoing'


class SendstatusRequestTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        def POST(uri, data):
            data.setdefault('phone_number', '254700111000')
            data.setdefault('action', 'send_status')
            return self.client.post(uri, data)
        self.POST = POST

    def test_should_have_required_props(self):
        data = {
        }
        res = self.POST(self.uri, data)
        self.assertEqual(res.status_code, 400)

    def test_response(self):
        outbox_message = OutboxMessage.objects.create(
              to='254700111999'
            , message='outgoing'
        )
        data = {
              'id': str(outbox_message.pk)
            , 'status': 'failed'
            , 'error': 'invalid receipient phone number'
        }
        res = self.POST(self.uri, data)
        self.assertEqual(res.status_code, 200)
        #
        outbox_message = OutboxMessage.objects.get(pk=outbox_message.pk)
        assert outbox_message.send_status == 'failed'
        assert outbox_message.send_error == 'invalid receipient phone number'
