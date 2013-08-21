from lib.views import receive


@receive('254700111000', 't')
def receive_incoming(req):
    req.envaya.queue({
        'message': 'outgoing1'
    })
    req.envaya.queue({
        'to': '254700111444',
        'message': 'outgoing2'
    })


@receive('254700111000', 't')
def receive_outgoing(req):
    pass


@receive('254700111000', 't')
def receive_send_status(req):
    pass
