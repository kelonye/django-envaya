from envaya.views import receive

@receive('254700111000')
def receive_incoming(req):
    req.queue({
        'message': 'outgoing1'
    })
    req.queue({
        'to': '254700111444',
        'message': 'outgoing2'
    })


@receive('254700111000')
def receive_outgoing(req):
    pass


@receive('254700111000')
def receive_send_status(req):
    pass