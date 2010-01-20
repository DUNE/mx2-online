
import wx
import sys
from commands import *

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
	run     = self.t1.GetValue()
        subrun  = self.t2.GetValue()
        runMode = self.t3.GetValue()
        gates   = self.t4.GetValue()
        febs    = self.t5.GetValue()

	#get_date = 'date -u +%y%m%d%k%M'
	#date = getoutput(get_date)
        date = getoutput('date -u +%y%m%d%k%M')
	
	ETNAME = 'MN_%08d_%04d_numib_v04_%s' % (int(run),int(subrun),date)
	#print ETNAME

	self.etSysFrame = wx.Frame(self, -1, 'ET System', pos=(600, 0), size=(400, 300))
	self.etSysFrame.Show(True)	

        self.etMonFrame = wx.Frame(self, -1, 'ET Monitor', pos=(600, 400), size=(400, 300))
        self.etMonFrame.Show(True) 

        self.ebSvcFrame = wx.Frame(self, -1, 'EB Service', pos=(1050, 0), size=(400, 800))
        self.ebSvcFrame.Show()

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "Run Control")
        self.SetTopWindow(frame)

        frame.Show(True)
        return True
        
app = MyApp(redirect=True)
app.MainLoop()

