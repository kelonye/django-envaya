import lib


@lib.receive('254700111000', 't')
def receive(req):
    if req.POST['action'] == 'incoming':
        req.envaya.queue({
            'message': 'outgoing1'
        })
        req.envaya.queue({
            'to': '254700111444',
            'message': 'outgoing2'
        })
