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

  req.queue({
      'event': 'cancel'
    , 'message': 'hello'
  })

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
