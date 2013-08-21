#!/usr/bin/env python
import pytz
from datetime import datetime
from django.db import models
from django.dispatch import receiver
from django.utils import simplejson as json
from django.db.models.signals import post_save, pre_save


def datetime_now_tz():
    return datetime.utcnow().replace(tzinfo=pytz.utc)


# model to represent:
#  - incoming messages
#  - outgoing messages status notifications
#  - change in device notifications
class InboxMessage(models.Model):

    ACTIONS = {
          1 : 'incoming'
        , 2: 'outgoing'
        , 3: 'send_status'
        , 4: 'device_status'
        , 5: 'amqp_started'
        , 6: 'forward_sent'
        , 7: 'test'
    }
    date_received = models.DateTimeField(
        default=datetime_now_tz
    )
    dump = models.TextField(
    )

    def __unicode__(self):
        return '%s: %s' % (
              self.date_received
            , self.action
        )

    @property
    def toJSON(self):
        return json.loads(self.dump)

    def get(self, attr):
        return self.toJSON.get(attr, '')

    @property
    def phone_number(self):
        return self.get('phone_number')

    @property
    def action(self):
        return self.get('action')

    # action=incoming properties
    @property
    def frm(self):
        return self.get('from')

    @property
    def message_type(self):
        return self.get('message_type')

    @property
    def message(self):
        return self.get('message')

    @property
    def timestamp(self):
        return self.get('timestamp')

    # action=outgoing properties

    # action=send_status properties
    @property
    def outbox_message(self):
        pk = self.get('id')
        return OutboxMessage.objects.get(
            pk=pk
        )

    @property
    def status(self):
        return self.get('status')

    @property
    def error(self):
        return self.get('error')

    # action=device_status properties

    # action=forward_sent properties

    # action=amqp_started properties


# model to represent a `send` event message
# we won't be saving cancel, cancel_all, log and settings events
# we also won't be prioritizing outgoing send events
class OutboxMessage(models.Model):
    date_sent = models.DateTimeField(
        default=datetime_now_tz
    )
    to = models.CharField(
        max_length=20
    )
    message = models.TextField(
    )
    # send status inbox message
    send_status = models.ForeignKey(
          InboxMessage
        , blank=True
        , null=True
    )

    def __unicode__(self):
        return '%s: %s' % (
              self.date_sent
            , self.to
        )

    @property
    def toDICT(self):
        return {
              'id': self.pk
            , 'to': self.to
            , 'message': self.message
        }
