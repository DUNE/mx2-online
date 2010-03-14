import wx
import wx.lib.newevent

ConfigUpdatedEvent,      EVT_CONFIGUPDATED         = wx.lib.newevent.NewEvent()

DAQQuitEvent,            EVT_DAQQUIT               = wx.lib.newevent.NewEvent()

ErrorMsgEvent,           EVT_ERRORMSG              = wx.lib.newevent.NewEvent()

NewDataEvent,            EVT_NEWDATA               = wx.lib.newevent.NewEvent()

ReadyForNextSubrunEvent, EVT_READY_FOR_NEXT_SUBRUN = wx.lib.newevent.NewEvent()

StopRunningEvent,        EVT_STOP_RUNNING          = wx.lib.newevent.NewEvent()

SubrunOverEvent,         EVT_SUBRUN_OVER           = wx.lib.newevent.NewEvent()

ThreadReadyEvent,        EVT_THREAD_READY          = wx.lib.newevent.NewEvent()

UpdateNodeEvent,         EVT_UPDATE_NODE           = wx.lib.newevent.NewEvent()

UpdateProgressEvent,     EVT_UPDATE_PROGRESS       = wx.lib.newevent.NewEvent()

UpdateSeriesEvent,       EVT_UPDATE_SERIES         = wx.lib.newevent.NewEvent()

UpdateWindowCountEvent,  EVT_UPDATE_WINDOW_COUNT   = wx.lib.newevent.NewEvent()
