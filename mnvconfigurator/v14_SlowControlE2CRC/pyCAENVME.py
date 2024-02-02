#!/usr/bin/python

"""
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2009/12/09 16:32:05 $"
"""

from ctypes import *
vme = windll.CAENVMElib

from random import *

class CAENVMETypes():
    cvErrorsDict = {
        0:'cvSuccess',
        -1:'cvBusError',
        -2:'cvComError',
        -3:'cvGenericError',
        -4:'cvInvalidParam'}
    class CVErrors():
        cvSuccess = 0
        cvBusError = -1
        cvComError = -2
        cvGenericError = -3
        cvInvalidParam = -4
    class CVBoardTypes():
        cvV1718 = 0
        cvV2718 = 1
        cvA2818 = 2
        cvA2719 = 3
    class CVAddressModifier():
        cvA24_U_MBLT = 56
        cvA24_U_DATA = 57
        cvA24_U_PGM = 58
        cvA24_U_BLT = 59
        cvA24_S_MBLT = 60
        cvA24_S_DATA = 61
        cvA24_S_PGM = 62
        cvA24_S_BLT = 63
    class CVDataWidth():
        cvD8 = 1
        cvD16 = 2
        cvD32 = 4
        cvD64 = 8
        cvD16_swapped = 18
        cvD32_swapped = 20
        cvD64_swapped = 24

class Controller(CAENVMETypes):
    def __init__(self):
        self.boardType = 0
        self.boardNum = 0
        self.linkNum = 0
        self.handle = -1
        self.addressModifier = CAENVMETypes.CVAddressModifier.cvA24_U_DATA
        self.dataWidth = CAENVMETypes.CVDataWidth.cvD16

    def Init(self, boardType, linkNum, boardNum):
        h = c_long(-1)
        cvRetError = vme.CAENVME_Init(c_int(boardType), c_short(linkNum), \
            c_short(boardNum), byref(h))        
        if cvRetError==CAENVMETypes.CVErrors.cvSuccess:
            self.handle = h.value
        return(CAENVMETypes.cvErrorsDict[cvRetError])

    def SWRelease(self):
        sw = c_char_p('')    
        cvRetError = vme.CAENVME_SWRelease(sw)
        if cvRetError==CAENVMETypes.CVErrors.cvSuccess:
            return(sw.value)
        else:
            return(CAENVMETypes.cvErrorsDict[cvRetError])

    def BoardFWRelease(self):
        fw = c_char_p('') 
        cvRetError = vme.CAENVME_BoardFWRelease(c_long(self.handle), fw)
        if cvRetError==CAENVMETypes.CVErrors.cvSuccess:
            return(fw.value)
        else:
            return(CAENVMETypes.cvErrorsDict[cvRetError])

    def End(self):
        cvRetError = vme.CAENVME_End(c_long(self.handle))
        if cvRetError==CAENVMETypes.CVErrors.cvSuccess:
            self.handle = -1
        return(CAENVMETypes.cvErrorsDict[cvRetError])

    def ReadCycle(self, addr, data):        
        d = c_void_p(data)
        cvRetError = vme.CAENVME_ReadCycle(c_long(self.handle), c_ulong(addr), byref(d), \
            c_int(self.addressModifier), c_int(self.dataWidth))
        if cvRetError==CAENVMETypes.CVErrors.cvSuccess:
            return(d.value)
        else:
            return(CAENVMETypes.cvErrorsDict[cvRetError])

    def WriteCycle(self, addr, data):
        d = c_void_p(data)
        cvRetError = vme.CAENVME_WriteCycle(c_long(self.handle), c_ulong(addr), byref(d), \
            c_int(self.addressModifier), c_int(self.dataWidth))
        return(CAENVMETypes.cvErrorsDict[cvRetError])
        

if __name__ == '__main__':
    try:
        ctrl = Controller()
        print('CAENVME Library v.' + ctrl.SWRelease())
        
        print('Controller initialized = ' + (ctrl.Init(CAENVMETypes.CVBoardTypes.cvV2718, 0, 0)))
        print('Controller handle = ' + str(ctrl.handle))
        print('V2718 board firmware = ' + str(ctrl.BoardFWRelease()))
        addr = 0x40F000; data = randint(0, 0x1FFFF)
        print('WriteCycle: ' + ctrl.WriteCycle(addr, data))
        print('WriteCycle: address = ' + hex(addr) + ', Wdata = ' + str(data))
        addr = 0x40F000; data = 0x0
        print('ReadCycle : address = ' + hex(addr) + ', Rdata = ' + str(ctrl.ReadCycle(addr, data)))

        #print('Controller end = ' + str(ctrl.End()))
        #print('Controller handle = ' + str(ctrl.handle))

    except:
        import sys
        print "Unexpected error:", sys.exc_info()[0]

        
    
    
                                  
def CAEN_SystemReset():
    handle = c_long(0); print('handle='+str(handle));print(handle.value)
    cvRetError = vme.CAENVME_SystemReset(handle)
    if cvRetError==0:
        return cvRetError
    else:
        return('CVErrorCodes = ' + cvRetError)
    


