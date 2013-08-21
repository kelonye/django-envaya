import unittest
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from lib.models import InboxMessage, OutboxMessage


class RequestTestCase(TestCase):

    uri = reverse('receive')

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

    uri = reverse('receive')

    def setUp(self):
        data = {
              'phone_number': '254700111000'
            , 'action': 'test'
        }
        client = Client()
        res = client.post(uri, data)
        self.assertEqual(res.status_code, 200)


class IncomingRequestTestCase(TestCase):

    uri = reverse('receive')

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
        #
        # assert req was logged
        assert InboxMessage.objects.all().count() == 1
        msg = InboxMessage.objects.get()
        assert msg.action == 'incoming'
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

    uri = reverse('receive')

    def setUp(self):
        self.client = Client()
        def POST(uri, data):
            data.setdefault('phone_number', '254700111000')
            data.setdefault('action', 'outgoing')
            return self.client.post(uri, data)
        self.client.POST = POST

    def test_response(self):
        send_status = InboxMessage.objects.create(
            dump=''
        )
        OutboxMessage.objects.create(
              to='254700111888'
            , message='outgoing'
            , send_status=send_status
        )
        OutboxMessage.objects.create(
              to='254700111999'
            , message='outgoing'
        )
        data = {
        }
        res = self.client.POST(self.uri, data)
        self.assertEqual(res.status_code, 200)
        #
        # assert req was logged
        send_status.delete()
        assert InboxMessage.objects.all().count() == 1
        msg = InboxMessage.objects.get()
        assert msg.action == 'outgoing'
        #
        # res data
        data = json.loads(res.content)
        # assert message is queued
        assert data['events']
        event = data['events'][0]
        assert event['event'] == 'send'
        # assert queued up only 1 unsent msg
        assert len(event['messages']) == 1
        msg = event['messages'][0]
        assert msg['to'] == '254700111999'
        assert msg['message'] == 'outgoing'


class SendstatusRequestTestCase(TestCase):

    uri = reverse('receive')

    def setUp(self):
        self.client = Client()
        def POST(uri, data):
            data.setdefault('phone_number', '254700111000')
            data.setdefault('action', 'send_status')
            return self.client.post(uri, data)
        self.client.POST = POST

    def test_should_have_required_props(self):
        data = {
        }
        res = self.client.POST(self.uri, data)
        self.assertEqual(res.status_code, 400)

    def test_response(self):
        outboxmsg = OutboxMessage.objects.create(
              to='254700111999'
            , message='outgoing'
        )
        data = {
              'id': str(outboxmsg.pk)
            , 'status': 'failed'
            , 'error': 'invalid receipient phone number'
        }
        res = self.client.POST(self.uri, data)
        self.assertEqual(res.status_code, 200)
        #
        # assert req was logged
        assert InboxMessage.objects.all().count() == 1
        msg = InboxMessage.objects.get()
        assert msg.action == 'send_status'
        #
        outboxmsg = OutboxMessage.objects.get(pk=outboxmsg.pk)
        assert outboxmsg.send_status == msg
