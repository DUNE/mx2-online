"""
   Tools.py:
   Contains some GUI tools used by the run control.
   Extracted here to prevent clutter in the main file.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Mar. 2010
                    
   Address all complaints to the management.
"""

import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from wx.lib.mixins.listctrl import ListRowHighlighter


#########################################################
#   AutoSizingListCtrl
#########################################################
class AutoSizingListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin, ListRowHighlighter):
	def __init__(self, parent, id=-1, style=wx.LC_REPORT):
		wx.ListCtrl.__init__(self, parent, id, style=style)
		ListCtrlAutoWidthMixin.__init__(self)
		ListRowHighlighter.__init__(self)
		

