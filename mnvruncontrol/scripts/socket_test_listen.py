# you want to use this such that it is executed
# after which you're dropped into the interactive shell:
# python -i socket_test.py

import random

from mnvruncontrol.backend.PostOffice import Routing, Envelope

import logging
PO_logger = logging.getLogger("PostOffice")
PO_logger.setLevel(logging.DEBUG)
PO_logger.addHandler(logging.StreamHandler())

def handler(msg):
	print msg

tm = Routing.MessageTerminus()
sub = Envelope.Subscription(action=Envelope.Subscription.DELIVER, delivery_address=tm)
tm.AddHandler(sub, handler)

n_attempts = 0
while n_attempts < 10:
	port_num = random.randrange(30000,50000)
	po = Routing.PostOffice(use_logging=True, listen_port=port_num)
	#po.listen_port = port_num
	try:
		po.AddSubscription(sub)
		po.Startup()
	except Exception as e:
		print e
		n_attempts += 1
		continue
	
	print "Listening on port", port_num
	break
