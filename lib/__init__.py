#!/usr/bin/env python
import sys
import sha
import json
import hashlib
import logging
from django.http import HttpResponse
from django.utils import simplejson as json
from django.views.decorators.csrf import csrf_exempt
from models import InboxMessage, OutboxMessage, ACTIONS
from django.utils.decorators import decorator_from_middleware as use


logger = logging.getLogger('envaya')


class Envaya(list):

    def __init__(self, req):
        super(Envaya, self).__init__()
        self.req = req
        if self.req.POST['action'] == ACTIONS[1]: #incoming
            self.save_incoming_message()
        elif self.req.POST['action'] == ACTIONS[2]: #outgoing
            self.queue_unsent_messages()
        elif self.req.POST['action'] == ACTIONS[3]: #send_status
            self.mark_send_status()

    def save_incoming_message(self):
        InboxMessage.objects.create(
            frm=self.req.POST['from'],
            message=self.req.POST['message']
        )

    def queue_unsent_messages(self):
        unsent_messages = OutboxMessage.objects.filter(
            send_status='queued'
        )
        for msg in unsent_messages:
            msg = msg.toDICT
            msg['event'] = 'send'
            self.append(msg)

    def mark_send_status(self):
        pk = self.req.POST['id']
        msg = OutboxMessage.objects.get(pk=pk)
        msg.send_status = self.req.POST['status']
        msg.send_error = self.req.POST['error']
        msg.save()

    def queue(self, message):
        frm = self.req.POST['phone_number']
        if self.req.POST['action'] == ACTIONS[1]:
            frm = self.req.POST['from']
        message.setdefault('event', 'send')
        message.setdefault('to', frm)
        outbox_message = OutboxMessage.objects.create(
            to=message['to'],
            message=message['message']
        )
        message['id'] = outbox_message.pk
        self.append(message)

    def send(self):
        if len(self) != 0:
            logger.info('SENDING')
        res = {}
        for message in self:
            logger.info(message)
            event = message['event']
            res.setdefault(event, [])
            del message['event']
            res[event].append(message)
        events = [{'event': k, 'messages': v} for k, v in res.iteritems()]
        content = {
            'events': events
        }
        json_content = json.dumps(content)
        return HttpResponse(
            json_content, content_type='application/json'
        )


def validate(req, attr):
    if req.POST.get(attr, None) == None:
        e = 'invalid request ' + attr
        raise Exception(e)


# middlewares


def set_auth_params(phone_number, password):

    def wrapper(view):
        def func(req):
            req.auth_params = {
                'phone_number': phone_number,
                'password': password
            }
            return view(req)
        func.func_name = view.func_name
        return func
    return wrapper


class ValidateReq(object):
    
    def process_request(self, req):

        if req.method != 'POST':
            return HttpResponse(status=405)

        for attr in [
            'phone_number',
            'action'
        ]:
            try:
                validate(req, attr)
            except Exception, e:
                return HttpResponse(e, status=400)

        if req.POST['action'] not in ACTIONS.values():
            e = 'invalid request action'

            return HttpResponse(e, status=400)
        if req.auth_params['phone_number'] != req.POST['phone_number']:
            e = 'request is from a forbiddened number'
            return HttpResponse(e, status=403)


class AuthReq(object):

    def process_request(self, req):

        if len(sys.argv) > 1 and sys.argv[1] == 'test':
            return

        def ksort(d):
            return [k for k in sorted(d.keys())]

        data = req.POST.copy()
        data_string = req.build_absolute_uri(req.get_full_path())
        for k in ksort(data):
            v = data[k]
            data_string += ',%s=%s' % (k, v)
        data_string += ',' + req.auth_params['password']

        sig = req.META['HTTP_X_REQUEST_SIGNATURE']
        generated_sig = sha.new(data_string).digest().encode('base64')

        if sig.strip() != generated_sig.strip():
            e = 'wrong phone/password combination'
            return HttpResponse(e, status=403)


class HandleTestReq(object):

    def process_request(self, req):
        if req.POST['action'] == 'test':
            e = 'OK'
            return HttpResponse(e)


class ValidateIncomingReq(object):

    def process_request(self, req):
        if req.POST['action'] == ACTIONS[1]:
            for attr in [
                'from',
                'message_type',
                'message',
                'timestamp'
            ]:  
                try:
                    validate(req, attr)
                except Exception, e:
                    return HttpResponse(e, status=400)


class ValidateOutgoingReq(object):

    def process_request(self, req):
        if req.POST['action'] == ACTIONS[2]:
            pass


class ValidateSendStatusReq(object):

    def process_request(self, req):
        if req.POST['action'] == ACTIONS[3]:
            for attr in [
                'id',
                'status',
                'error'
            ]:
                try:
                    validate(req, attr)
                except Exception, e:
                    return HttpResponse(e, status=400)


class Log(object):

    def process_request(self, req):
        logger.info('RECEIVING')
        for k, v in req.POST.iteritems():
            logger.info('%s: %s' % (k, v))


def receive(phone_number, password):

    def wrapper(view):
        @csrf_exempt
        @set_auth_params(phone_number, password)
        @use(ValidateReq)
        @use(AuthReq)
        @use(HandleTestReq)
        @use(ValidateIncomingReq)
        @use(ValidateOutgoingReq)
        @use(ValidateSendStatusReq)
        @use(Log)
        def func(req):
            envaya = Envaya(req)
            req.envaya = envaya
            view(req)
            return envaya.send()
        func.func_name = view.func_name
        return func
    return wrapper
