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
  messages = [
      'received' # send back to source
    , {'to': '254700111000', 'message':'heya'}
  ]
  return envaya.send(messages)
```

Test
---

    $ make

License
---

MIT
