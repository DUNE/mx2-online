#########################################################
#   ConfigUpdatedEvent
#########################################################

EVT_CONFIGUPDATED_ID = wx.NewId()
class ConfigUpdatedEvent(wx.CommandEvent):
	""" An event informing the main window that the configuration database has been updated. """
	def __init__(self):
		wx.CommandEvent.__init__(self)
		self.SetEventType(EVT_CONFIGUPDATED_ID)

#########################################################
#   ErrorMsgEvent
#########################################################

EVT_ERRORMSG_ID = wx.NewId()
class ErrorMsgEvent(wx.CommandEvent):
	""" An event requesting an error message from the main window. """
	def __init__(self):
		wx.CommandEvent.__init__(self)
		self.SetEventType(EVT_ERRORMSG_ID)

#########################################################
#   NewDataEvent
#########################################################

EVT_NEWDATA_ID = wx.NewId()
class NewDataEvent(wx.PyEvent):
	""" An event to carry data between the threaded processes and the windows built to display their output. """
	def __init__(self, data):
		wx.PyEvent.__init__(self)
		self.data = data	
		self.SetEventType(EVT_NEWDATA_ID)
		
#########################################################
#   UpdateEvent
#########################################################

EVT_UPDATE_ID = wx.NewId()
class UpdateEvent(wx.PyEvent):
	""" An event that notifies the data acquisition handler that things are still running. """
	def __init__(self):
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_UPDATE_ID)

#########################################################
#   UpdateProgressEvent
#########################################################

#EVT_UPDATEPROGRESS_ID = wx.NewId()
#class UpdateProgressEvent(wx.NotifyEvent):
	#""" An event informing the main window what progress has been made in the run. """
	#def __init__(self, text=None, progress=(0,0)):
		#wx.NotifyEvent.__init__(self)
		#self.text = text
		#self.progress = progress
		#self.SetEventType(EVT_UPDATEPROGRESS_ID)

UpdateProgressEvent, EVT_UPDATEPROGRESS_ID = wx.lib.newevent.NewEvent()

#########################################################
#   ThreadReadyEvent
#########################################################

EVT_THREAD_READY_ID = wx.NewId()
class ThreadReadyEvent(wx.CommandEvent):
	""" An event that informs the next process that it's done """
	def __init__(self):
		wx.CommandEvent.__init__(self)
		self.SetEventType(EVT_THREAD_READY_ID)

#########################################################
#   DAQQuitEvent
#########################################################

EVT_DAQQUIT_ID = wx.NewId()
class DAQQuitEvent(wx.CommandEvent):
	""" An event informing the main window that one of the
	    essential DAQ processes has quit, and that data
	    acquisition should thus be stopped. """
	def __init__(self, processname=None):
		wx.CommandEvent.__init__(self)
		self.processname = processname		# if the DAQ quit for some reason other than normal exit, this is the process that died first
		self.SetEventType(EVT_DAQQUIT_ID)


#########################################################
#   ReadyForNextSubrunEvent
#########################################################

EVT_READY_FOR_NEXT_SUBRUN_ID = wx.NewId()
class ReadyForNextSubrunEvent(wx.CommandEvent):
	""" An event used internally to indicate that the manager is ready to start the next subrun. """
	def __init__(self):
		wx.CommandEvent.__init__(self)
		self.SetEventType(EVT_READY_FOR_NEXT_SUBRUN_ID)


