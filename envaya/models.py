#!/usr/bin/env python
import pytz
from django.db import models
from django.dispatch import receiver


def datetime_now_tz():
    return datetime.utcnow().replace(tzinfo=pytz.utc)


# model to represent:
#  - incoming messages
#  - outgoing messages status notifications
#  - change in device notifications
class InboxMessage(models.Model):

    ACTIONS = {
          'outgoing': 1
        , 'incoming': 2
        , 'send_status': 3
        , 'device_status': 4
        , 'amqp_started': 5
        , 'forward_sent': 6
    }
    date_received = models.DateTimeField(
        default=datetime_now_tz
    )
    dump = models.TextField(
    )

    @property
    def JSON(self):
        return json.loads(self.dump)

    def get(self, attr):
        return self.JSON.get(attr, '')

    @property
    def phone_number(self):
        return self.get('phone_number')

    @property
    def action(self):
        return self.get('action')

    # action=incoming properties
    @property
    def frm(self):
        return self.get('frm')

    @property
    def message_type(self):
        return self.get('message_type')

    @property
    def message(self):
        return self.get('message')

    @property
    def timestamp(self):
        return self.get('timestamp')

    @property
    def mms_parts(self):
        return self.get('mms_parts')

    # action=outgoing properties

    # action=send_status properties
    @property
    def outbox_message(self):
        pk = self.get('id')
        return OutboxMeesage.objects.get(
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
