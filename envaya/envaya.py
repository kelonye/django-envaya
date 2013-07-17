#!/usr/bin/env python
import json
import logging

from django.http import HttpResponse
from django.utils import simplejson as json
from django.views.decorators.csrf import csrf_exempt


logger = logging.getLogger('envaya')


class Envaya(object):

    def __init__(self, req):
        self.req = req
        self.phone = req.POST['phone_number']

    def send(self, messages, event='send'):
        logger.info('SENDING')
        def build_messages():
            for message in messages:
                if isinstance(message, str):
                    to = self.phone
                    message = {
                        'to': to,
                        'message': message
                    }
                logger.info('%s : %s' % (
                      message['to']
                    , message['message']
                ))
                yield message

        content = {
            'events': [{
               'event': event,
               'messages': [m for m in build_messages()]
            }]
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
        req.envaya = Envaya(req)
        return view(req)
    return wrapper
