Install
---

    $ pip install envaya

Use
---

```python

# settings.py

INSTALLED_APPS = (
  'messages',
  'envaya',
)

# message/models.py

from envaya.models import InboxMessage, OutboxMessage

@receiver(post_save, sender=InboxMessage)
def on_saved_inbox_message(sender, instance, created, **kwargs):
  print instance.action

@receiver(post_save, sender=OutboxMessage)
def on_saved_outbox_message(sender, instance, created, **kwargs):
  if not created:
    print instance.send_status.status
    print instance.send_status.error

# message/views.py

import envaya

@envaya.receive
def receive(req):

  print req.POST

  # send a message to `to`
  req.queue({
      'event': 'send'
    , 'to': '254700111000'
    , 'message': 'hello'
  })


# message/admin.py


# message/urls.py

urlpatterns = patterns('message.views',
    url(r'^receive/$', 'receive', name='receive'),
)

```

Test
---

    $ make deps test

License
---

MIT
