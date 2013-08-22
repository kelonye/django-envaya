#!/usr/bin/env python
import pytz
from datetime import datetime
from django.db import models
from django.dispatch import receiver
from django.utils import simplejson as json
from django.db.models.signals import post_save, pre_save


ACTIONS = {
    1 : 'incoming',
    2: 'outgoing',
    3: 'send_status',
    4: 'device_status',
    5: 'amqp_started',
    6: 'forward_sent',
    7: 'test'
}


def datetime_now_tz():
    return datetime.utcnow().replace(tzinfo=pytz.utc)


class InboxMessage(models.Model):
    date_received = models.DateTimeField(
        default=datetime_now_tz
    )
    frm = models.CharField(
        max_length=20
    )
    message = models.TextField(
    )
    def __unicode__(self):
        return '%s: %s' % (
            self.date_received, self.action
        )


class OutboxMessage(models.Model):
    CHOICES = [
        (x, x) for x in ['queued', 'failed', 'cancelled', 'sent']
    ]
    date_sent = models.DateTimeField(
        default=datetime_now_tz
    )
    to = models.CharField(
        max_length=20
    )
    message = models.TextField(
    )
    send_status = models.CharField(
        max_length=10,
        default='queued',
        choices=CHOICES
    )
    send_error = models.TextField(
    )

    def __unicode__(self):
        return '%s: %s' % (
            self.date_sent, self.to
        )

    @property
    def toDICT(self):
        return {
            'id': self.pk,
            'to': self.to,
            'message': self.message
        }