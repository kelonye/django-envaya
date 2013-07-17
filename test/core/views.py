import envaya

@envaya.receive
def receive1(req):
    messages = [
        'message1'
    ]
    return req.envaya.send(messages)

@envaya.receive
def receive2(req):
    messages = [
        {'to': '254700111000', 'message':'message2'}
    ]
    return req.envaya.send(messages)
