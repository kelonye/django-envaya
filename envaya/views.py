#!/usr/bin/env python
import json
import logging

from django.http import HttpResponse
from django.utils import simplejson as json
from django.views.decorators.csrf import csrf_exempt
from models import InboxMessage, OutboxMessage


logger = logging.getLogger('envaya')


class Envaya(list):

    def __init__(self, req):
        super(Envaya, self).__init__()
        self.req = req
        self.msg = InboxMessage.objects.create(
            dump=json.dumps(req.POST.dict())
        )

        if self.msg.action == self.msg.ACTIONS[1]: #incoming
            pass
        elif self.msg.action == self.msg.ACTIONS[2]: #outgoing
            self.queue_unsent_messages()
        elif self.msg.action == self.msg.ACTIONS[3]: #send_status
            self.mark_send_status()

    def queue_unsent_messages(self):
        unsent_messages = OutboxMessage.objects.filter(
            send_status=None
        )
        for msg in unsent_messages:
            req.queue(msg.toDICT)

    def mark_send_status(self):
        pass

    def queue(self, message):
        frm = self.msg.phone_number
        if self.msg.action == self.msg.ACTIONS[1]:
            frm = self.msg.frm
        message.setdefault('event', 'send')
        message.setdefault('to', frm)
        self.append(message)

    def send(self):
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
        e = 'invalid request ' + attr + '\n'
        raise Exception(e)


def validate_req(view):
    def wrapper(req):
        if req.method != 'POST':
            return HttpResponse(status=405)
        for attr in [
              'phone_number'
            , 'action'
        ]:
            try:
                validate(req, attr)
            except Exception, e:
                return HttpResponse(e, status=400)
        return view(req)
    return wrapper


def validate_incoming_req(view):
    def wrapper(req):
        if req.POST['action'] == InboxMessage.ACTIONS[1]:
            for attr in [
                  'from'
                , 'message_type'
                , 'message'
                , 'timestamp'
            ]:  
                try:
                    validate(req, attr)
                except Exception, e:
                    return HttpResponse(e, status=400)
        return view(req)
    return wrapper


def validate_outgoing_req(view):
    def wrapper(req):
        if req.POST['action'] == InboxMessage.ACTIONS[2]:
            pass
        return view(req)
    return wrapper


def validate_send_status_req(view):
    def wrapper(req):
        if req.POST['action'] == InboxMessage.ACTIONS[3]:
            for attr in [
                  'id'
                , 'status'
                , 'message'
                , 'error'
            ]:
                try:
                    validate(req, attr)
                except Exception, e:
                    return HttpResponse(e, status=400)
        return view(req)
    return wrapper


def log(view):
    def wrapper(req):
        logger.info('RECEIVING')
        for k, v in req.POST.iteritems():
            logger.info('%s: %s' % (k, v))
        return view(req)
    return wrapper


def receive(view):
    @csrf_exempt
    @validate_req
    @validate_incoming_req
    @validate_outgoing_req
    @validate_send_status_req
    @log
    def wrapper(req):
        envaya = Envaya(req)
        req.envaya = envaya
        req.queue = envaya.queue
        view(req)
        return envaya.send()
    return wrapper
