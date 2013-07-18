#!/usr/bin/env python
import json
import logging

from django.http import HttpResponse
from django.utils import simplejson as json
from django.views.decorators.csrf import csrf_exempt


logger = logging.getLogger('envaya')


class Envaya(list):

    def __init__(self, req):
        super(Envaya, self).__init__()
        self.req = req
        self.phone_number = req.POST['phone_number']

    def queue(self, message):
        message.setdefault('event', 'send')
        message.setdefault('to', self.phone_number)
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


def validate_req(view):
    def wrapper(req):
        if req.method != 'POST':
            return HttpResponse(status=405)
        if not req.POST.get('phone_number', None):
            e = 'invalid request phone_number'
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
    @log
    def wrapper(req):
        envaya = Envaya(req)
        req.queue = envaya.queue
        view(req)
        return envaya.send()
    return wrapper
