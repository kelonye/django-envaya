Install
---

    $ pip install envaya

Use
---

```python

from envaya.views import receive

# receive msgs from a phone running envaya
@receive('254700111000')
def handle(req):

  print req.POST

  # send a message to `to`
  req.queue({
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
