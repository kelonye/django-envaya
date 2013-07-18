import envaya

@envaya.receive
def receive1(req):
    req.queue({
        'message': 'message1'
    })

@envaya.receive
def receive2(req):
    req.queue({
        'to': '254700111000',
        'message': 'message2'
    })
