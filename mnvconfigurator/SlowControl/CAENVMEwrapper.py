#!/usr/bin/python

from ctypes import *
##vme = windll.CAENVMElib
cdll.LoadLibrary("/usr/lib/libCAENVME.so")
vme = CDLL("/usr/lib/libCAENVME.so")

#cdll.LoadLibrary("/work/software/mnvsingle/mnvdaq/lib/libhardware.so")
#hardware = CDLL("/work/software/mnvsingle/mnvdaq/lib/libhardware.so")

from random import *

class CAENVMETypes():
    '''Cristian's wraper for CAEN VME Types'''
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

class CAENErr(Exception):
    def __init__(self, cvNumber):
        self.value = CAENVMETypes.cvErrorsDict[cvNumber]
    def __str__(self):
        return repr(self.value)
    
class Controller(CAENVMETypes):
    '''Cristian's wraper for CAEN VME V2718 functions'''
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
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        self.handle = h.value

    def SWRelease(self):
        sw = c_char_p('')    
        cvRetError = vme.CAENVME_SWRelease(sw)
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        return(sw.value)

    def BoardFWRelease(self):
        fw = c_char_p('') 
        cvRetError = vme.CAENVME_BoardFWRelease(c_long(self.handle), fw)
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        return(fw.value)

    def End(self):
        cvRetError = vme.CAENVME_End(c_long(self.handle))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        self.handle = -1

    def SystemReset(self):
        cvRetError = vme.CAENVME_SystemReset(c_long(self.handle))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)

    def ReadCycle(self, addr):        
        data = c_void_p(-1)
        cvRetError = vme.CAENVME_ReadCycle(c_long(self.handle), c_ulong(addr), \
            byref(data), c_int(self.addressModifier), c_int(self.dataWidth))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        if (self.dataWidth==CAENVMETypes.CVDataWidth.cvD16) | \
           (self.dataWidth==CAENVMETypes.CVDataWidth.cvD16_swapped):
            return(data.value & 0xFFFF)
        if (self.dataWidth==CAENVMETypes.CVDataWidth.cvD32) | \
           (self.dataWidth==CAENVMETypes.CVDataWidth.cvD32_swapped):
            return(data.value)
        if (self.dataWidth==CAENVMETypes.CVDataWidth.cvD8):
            return(data.value & 0xFF)

    def WriteCycle(self, addr, data):
        d = c_void_p(data)
        cvRetError = vme.CAENVME_WriteCycle(c_long(self.handle), c_ulong(addr), \
            byref(d), c_int(self.addressModifier), c_int(self.dataWidth))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)



