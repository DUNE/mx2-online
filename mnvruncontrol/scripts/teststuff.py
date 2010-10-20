import os
import sys
import uuid
import pprint
from mnvruncontrol.configuration import Logging
from mnvruncontrol.configuration import MetaData
from mnvruncontrol.backend import PostOffice

PO = PostOffice.PostOffice(listen_port=3000, use_logging=True)

class FrontEnd(PostOffice.MessageTerminus):
	def __init__(self, obj_id=None):
		PostOffice.MessageTerminus.__init__(self, obj_id)
	
	def respond(self, message):
		if message.subject == "frontend_info" and message.info == "need_HV_confirmation":
			global PO
			PO.Send( message.ResponseMessage(subject="mgr_directive", directive="continue", client_id=self.id) )
		
		elif message.subject == "frontend_info" and message.info == "series_end":
			#PO.Send( PostOffice.Message(subject="lock_request", request="release", requester_id=self.id) )
			print "Series finished!"
			
	
		
frontend = FrontEnd(obj_id=uuid.UUID("00000000-0000-0000-0000-000000000000"))


subs = []
subs.append(PostOffice.Subscription(subject="control_request", action=PostOffice.Subscription.FORWARD, delivery_address=("localhost", 1090)))
subs.append(PostOffice.Subscription(subject="mgr_directive", action=PostOffice.Subscription.FORWARD, delivery_address=("localhost", 1090)))
subs.append( PostOffice.Subscription(subject="frontend_info", action=PostOffice.Subscription.DELIVER, delivery_address=frontend) )

for sub in subs:
	PO.AddSubscription(sub)
	
subs = [ PostOffice.Subscription(subject="frontend_info", action=PostOffice.Subscription.FORWARD, delivery_address=(None, 3000)) ]
PO.ForwardRequest( ("localhost", 1090), subs )
frontend.AddHandler(subs[0], frontend.respond)

msgs = PO.SendAndWaitForResponse( PostOffice.Message(subject="control_request", request="get", requester_id=frontend.id, requester_name="booyah", requester_location="nowhere"), timeout=5 )
print msgs


msgs = PO.SendAndWaitForResponse( PostOffice.Message(subject="mgr_directive", directive="status_report", client_id=frontend.id), timeout=5 )
print msgs

config = msgs[0].status["configuration"]
config.detector = MetaData.DetectorTypes.UNKNOWN
config.is_single_run = False
config.auto_start_series = False

msgs = PO.SendAndWaitForResponse( PostOffice.Message(subject="mgr_directive", directive="start", client_id=frontend.id, configuration=config), timeout=5 )
print msgs


print "press 'enter' to continue"
raw_input()
