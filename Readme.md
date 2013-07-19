Install
---

    $ pip install envaya

Example
---

```python

import envaya

@envaya.receive
def receive(req):

  print req.POST

  # send a message back to source
  req.queue({
      'event': 'cancel'
    , 'message': 'hello'
  })

  # send a message to `to`
  req.queue({
      'event': 'send'
    , 'to': '254700111000'
    , 'message': 'hello'
  })


```

Test
---

    $ make deps test

License
---

MIT
