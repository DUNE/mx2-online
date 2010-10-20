"""
  Events.py:
  Event objects used internally by the run control.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Apr. 2010
                    
   Address all complaints to the management.
"""

import wx
import wx.lib.newevent

AlertEvent,              EVT_ALERT                 = wx.lib.newevent.NewEvent()

NotifyEvent,             EVT_NOTIFY                = wx.lib.newevent.NewEvent()

CommStatusEvent,         EVT_COMM_STATUS           = wx.lib.newevent.NewEvent()

ConfigUpdatedEvent,      EVT_CONFIG_UPDATED        = wx.lib.newevent.NewEvent()

ControlStatusEvent,      EVT_CONTROL_STATUS        = wx.lib.newevent.NewEvent()

DAQQuitEvent,            EVT_DAQ_QUIT              = wx.lib.newevent.NewEvent()

EndSubrunEvent,          EVT_END_SUBRUN            = wx.lib.newevent.NewEvent()

ErrorMsgEvent,           EVT_ERRORMSG              = wx.lib.newevent.NewEvent()

PMTVoltageUpdateEvent,   EVT_PMT_VOLTAGE_UPDATE    = wx.lib.newevent.NewEvent()

NewDataEvent,            EVT_NEWDATA               = wx.lib.newevent.NewEvent()

ReadyForNextSubrunEvent, EVT_READY_FOR_NEXT_SUBRUN = wx.lib.newevent.NewEvent()

StartRunningEvent,       EVT_START_RUNNING         = wx.lib.newevent.NewEvent()

StatusUpdateEvent,       EVT_STATUS_UPDATE         = wx.lib.newevent.NewEvent()

StopRunningEvent,        EVT_STOP_RUNNING          = wx.lib.newevent.NewEvent()

SubrunOverEvent,         EVT_SUBRUN_OVER           = wx.lib.newevent.NewEvent()

SubrunStartingEvent,     EVT_SUBRUN_STARTING       = wx.lib.newevent.NewEvent()

UpdateNodeEvent,         EVT_UPDATE_NODE           = wx.lib.newevent.NewEvent()

UpdateProgressEvent,     EVT_UPDATE_PROGRESS       = wx.lib.newevent.NewEvent()

UpdateSeriesEvent,       EVT_UPDATE_SERIES         = wx.lib.newevent.NewEvent()

UpdateWindowCountEvent,  EVT_UPDATE_WINDOW_COUNT   = wx.lib.newevent.NewEvent()

WaitForCleanupEvent,     EVT_WAIT_FOR_CLEANUP      = wx.lib.newevent.NewEvent()
