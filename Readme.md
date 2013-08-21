Install
---

    $ pip install django_envaya

Use
---

```python

from django_envaya import receive

# receive msgs from a phone running envaya
@receive('254700111000', 'password')
def handle(req):

  print req.POST

  # send a message to `to`
  req.envaya.queue({
      'event': 'send'
    , 'to': '254700111000'
    , 'message': 'hello'
  })

```

Example
---
    
    $ make deps example

Admin password is `test`

Test
---

    $ make deps test

License
---

MIT
