# you want to use this such that it is executed
# after which you're dropped into the interactive shell:
# python -i socket_test.py
import logging
PO_logger = logging.getLogger("PostOffice")
PO_logger.setLevel(5)
PO_logger.addHandler(logging.StreamHandler())

from mnvruncontrol.backend.PostOffice import Routing, Envelope

po = Routing.PostOffice(use_logging=True, listen_port=55000)
po.Startup()

host = ""
port = 0
while True:
	h = raw_input("Hostname to send test message to (leave blank for default = '%s'): " % host)
	p = raw_input("Port to send test message to (leave blank for default = %s): " % port)
	
	host = h or host
	port = int(p) if p else port

	sub = Envelope.Subscription(action=Envelope.Subscription.FORWARD, delivery_address=(host, port))
	po.AddSubscription(sub)

	po.SendWithConfirmation( Envelope.Message(subject="test_msg") )
	
