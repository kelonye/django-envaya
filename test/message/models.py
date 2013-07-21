from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from envaya.models import InboxMessage, OutboxMessage

@receiver(post_save, sender=InboxMessage)
def on_saved_inbox_message(sender, instance, created, **kwargs):
  print instance.action

@receiver(post_save, sender=OutboxMessage)
def on_saved_outbox_message(sender, instance, created, **kwargs):
  if not created:
    print instance.send_status.status
    print instance.send_status.error
