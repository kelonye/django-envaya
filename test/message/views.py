from envaya.views import receive

@receive
def receive1(req):
    req.queue({
        'message': 'message1'
    })

@receive
def receive2(req):
    req.queue({
        'to': '254700111444',
        'message': 'message2'
    })
