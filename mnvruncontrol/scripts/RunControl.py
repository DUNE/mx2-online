
import wx
import sys
import wx.richtext as rt
from commands import *
from subprocess import *

class MyFrame(wx.Frame):
    """
    This is MyFrame.  It just shows a few controls on a wxPanel,
    and has a simple menu.
    """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
                          pos=(0, 0), size=(600, 600))

        # Create the menubar
        menuBar = wx.MenuBar()

        # and a menu 
        menu = wx.Menu()

        # add an item to the menu, using \tKeyName automatically
        # creates an accelerator, the third param is some help text
        # that will show up in the statusbar
        menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit this simple sample")

        # bind the menu event to an event handler
        self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)

        # and put the menu on the menubar
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)

        self.CreateStatusBar()
        

        # Now create the Panel to put the other controls on.
        panel = wx.Panel(self)

        l1 = wx.StaticText(panel, -1, "Run")
        t1 = wx.TextCtrl(panel, -1, "1337", size=(125, -1))
	self.t1 = t1

        l2 = wx.StaticText(panel, -1, "Subrun")
        t2 = wx.TextCtrl(panel, -1, "391", size=(125, -1))
	self.t2 = t2

        l3 = wx.StaticText(panel, -1, "Gates")
        t3 = wx.TextCtrl(panel, -1, "10", size=(125, -1))
	self.t3 = t3

        l4 = wx.StaticText(panel, -1, "Run Mode")
        t4 = wx.TextCtrl(panel, -1, "0", size=(125, -1))
	self.t4 = t4

        l5 = wx.StaticText(panel, -1, "FEBs")
        t5 = wx.TextCtrl(panel, -1, "4", size=(125, -1))
	self.t5 = t5

        b = wx.Button(panel, -1, "Start DAQ Singleton")
        self.Bind(wx.EVT_BUTTON, self.StartDaqSingleton, b)

        space = 6
        #bsizer = wx.BoxSizer(wx.VERTICAL)
        #bsizer.Add(b, 0, wx.GROW|wx.ALL, space)
        #bsizer.Add(b2, 0, wx.GROW|wx.ALL, space)
        #bsizer.Add(b3, 0, wx.GROW|wx.ALL, space)

        sizer = wx.FlexGridSizer(cols=2, hgap=space, vgap=space)
        sizer.AddMany([ l1, t1,
                        l2, t2,
                        l3, t3,
                        l4, t4,
                        l5, t5,  
			b, (0,0)
                        ])
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(sizer, 0, wx.ALL, 25)
        panel.SetSizer(border)
        panel.SetAutoLayout(True)


    def OnTimeToClose(self, evt):
        self.Close()

    def StartDaqSingleton(self, evt):
	self.run     = self.t1.GetValue()
        self.subrun  = self.t2.GetValue()
	self.gates   = self.t3.GetValue()
	self.runMode = self.t4.GetValue()
        self.febs    = self.t5.GetValue()

	#get_date = 'date -u +%y%m%d%k%M'
	#date = getoutput(get_date)
        date = getoutput('date -u +%y%m%d%k%M')
	
	self.ETNAME = 'MN_%08d_%04d_numib_v04_%s' % (int(self.run),int(self.subrun),date)
	print self.ETNAME

	self.StartETSys()	
	self.StartETMon()
	self.StartEBSvc()

    def StartETSys(self):
	
        self.etSysFrame = wx.Frame(self, -1, 'ET System', pos=(600, 0), size=(400, 300))
        self.etSysFrame.rtc = rt.RichTextCtrl(self.etSysFrame, style=wx.VSCROLL|wx.NO_BORDER);
        self.etSysFrame.Show(True)

	EVENT_SIZE=2048 
	FRAMES=8
	EVENTS=int(self.gates)*FRAMES*int(self.febs)

	#self.et_sys = Popen(['$ET_HOME/Linux-x86_64-64/bin/et_start','-v','-f','test','-n',str(EVENTS),'-s',str(EVENT_SIZE)], stdout=PIPE)
	self.et_sys = Popen(['$ET_HOME/Linux-x86_64-64/bin/et_start','-v','-f',str(self.ETNAME),'-n',str(EVENTS),'-s',str(EVENT_SIZE)], stdout=PIPE)
	#self.et_sys = Popen(['$ET_HOME/Linux-x86_64-64/bin/et_start','-v -f ./'+self.ETNAME+' -n '+str(EVENTS)+' -s '+str(EVENT_SIZE)], stdout=PIPE)
	#self.et_sys = Popen(['./start_et_system',str(self.ETNAME),str(self.febs),str(self.gates)], stdout=PIPE)
	self.etSysFrame.rtc.WriteText(self.et_sys.communicate()[0])

    def StartETMon(self):

        self.etMonFrame = wx.Frame(self, -1, 'ET Monitor', pos=(600, 400), size=(400, 300))
        self.etMonFrame.rtc = rt.RichTextCtrl(self.etMonFrame, style=wx.VSCROLL|wx.NO_BORDER);
        self.etMonFrame.Show(True)

        self.et_mon = Popen(['$ET_HOME/Linux-x86_64-64/bin/et_monitor','-f',str(self.ETNAME)], stdout=PIPE)
        self.etMonFrame.rtc.WriteText(self.et_mon.communicate()[0])

    def StartEBSvc(self):

        self.ebSvcFrame = wx.Frame(self, -1, 'EB Service', pos=(1050, 0), size=(400, 800))
	self.ebSvcFrame.rtc = rt.RichTextCtrl(self.ebSvcFrame, style=wx.VSCROLL|wx.NO_BORDER);
        self.ebSvcFrame.Show()

        self.eb_svc = Popen(['nice','${DAQROOT}/bin/event_builder',str(self.ETNAME)], stdout=PIPE)
        self.ebSvcFrame.rtc.WriteText(self.eb_svc.communicate()[0])

	
class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "Run Control")
        self.SetTopWindow(frame)

        frame.Show(True)
        return True
        
app = MyApp(redirect=True)
app.MainLoop()

