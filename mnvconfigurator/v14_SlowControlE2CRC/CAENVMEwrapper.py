#!/usr/bin/python

from ctypes import *
###vme = windll.CAENVMElib
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
        -4:'cvInvalidParam',
        -5:'cvTimeoutError'}
    class CVErrors():
        cvSuccess  = 0
        cvBusError = -1
        cvComError = -2
        cvGenericError = -3
        cvInvalidParam = -4
        cvTimeoutError = -5
    class CVBoardTypes():
        cvV1718 = 0
        cvV2718 = 1
        cvA2818 = 2
        cvA2719 = 3
    cvAMDict = {'A24_U_DATA':0x39, 'A24_U_BLT':0x3B,
                'A32_U_DATA':0x09, 'A32_U_PGM':0x0A, 'A32_U_BLT':0x0B,
                'A32_S_DATA':0x0D, 'A32_S_PGM':0x0E, 'A32_S_BLT':0x0F,}
    class CVAddressModifier():
        cvA32_LCK    = 0x05 #5
        cvA32_U_MBLT = 0x08 #8
        cvA32_U_DATA = 0x09 #9  CROCE, used by SlowControl
        cvA32_U_PGM  = 0x0A #10 CROCE
        cvA32_U_BLT  = 0x0B #11 CROCE, used by SlowControl
        cvA32_S_MBLT = 0x0C #12
        cvA32_S_DATA = 0x0D #13 CROCE
        cvA32_S_PGM  = 0x0E #14 CROCE
        cvA32_S_BLT  = 0x0F #15 CROCE
        cvA16_U      = 0x29 #41
        cvA16_LCK    = 0x2C #44
        cvA16_S      = 0x2D #45
        cvCR_CSR     = 0x2F #47
        cvA24_LCK    = 0x32 #50
        cvA24_U_MBLT = 0x38 #56
        cvA24_U_DATA = 0x39 #57 CROC, used by SlowControl
        cvA24_U_PGM  = 0x3A #58
        cvA24_U_BLT  = 0x3B #59 CROC, used by SlowControl
        cvA24_S_MBLT = 0x3C #60
        cvA24_S_DATA = 0x3D #61
        cvA24_S_PGM  = 0x3E #62
        cvA24_S_BLT  = 0x3F #63
    cvDWDict = {'D16':0x02, 'D32':0x04, 'D16sw':0x12, 'D32sw':0x14}
    class CVDataWidth():
        cvD8  = 0x01         # 1
        cvD16 = 0x02         # 2 CROC and CROCE, used by SlowControl
        cvD32 = 0x04         # 4 CROCE, used by SlowControl
        cvD64 = 0x08         # 8
        cvD16_swapped = 0x12 #18
        cvD32_swapped = 0x14 #20
        cvD64_swapped = 0x18 #24
    cvTimeoutDict = {0:'50us', 1:'400us'}
    class CVVMETimeouts():
        cvTimeout50us   = 0  # Timeout is 50 microseconds
        cvTimeout400us  = 1  # Timeout is 400 microseconds

class CAENErr(Exception):
    def __init__(self, cvNumber=-3):
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
        self.addressModifier = CAENVMETypes.cvAMDict['A24_U_DATA'] #CAENVMETypes.CVAddressModifier.cvA24_U_DATA
        self.dataWidth = CAENVMETypes.cvDWDict['D16']              #CAENVMETypes.CVDataWidth.cvD16

    def Init(self, boardType, linkNum, boardNum):
        h = c_long(-1)
        cvRetError = vme.CAENVME_Init(c_int(boardType), c_short(linkNum), \
            c_short(boardNum), byref(h))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        self.boardType = boardType
        self.boardNum = boardNum
        self.linkNum = linkNum
        self.handle = h.value

    def SWRelease(self):
        sw = c_char_p(''.encode())  
        cvRetError = vme.CAENVME_SWRelease(sw)
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        return(sw.value.decode())

    def BoardFWRelease(self):
        fw = c_char_p(''.encode()) 
        cvRetError = vme.CAENVME_BoardFWRelease(c_long(self.handle), fw)
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        return(fw.value.decode())

    def End(self):
        cvRetError = vme.CAENVME_End(c_long(self.handle))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        self.handle = -1

    def SystemReset(self):
        cvRetError = vme.CAENVME_SystemReset(c_long(self.handle))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)

    def ReadCycle(self, addr, am='A24_U_DATA', dw='D16'):
        self.addressModifier = CAENVMETypes.cvAMDict[am]
        self.dataWidth       = CAENVMETypes.cvDWDict[dw]
        data = c_void_p(-1)
        cvRetError = vme.CAENVME_ReadCycle(c_long(self.handle), c_ulong(addr), \
            byref(data), c_int(self.addressModifier), c_int(self.dataWidth))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        if (self.dataWidth==CAENVMETypes.cvDWDict['D16'] or self.dataWidth==CAENVMETypes.cvDWDict['D16sw']):
            return(data.value & 0xFFFF)
        if (self.dataWidth==CAENVMETypes.cvDWDict['D32'] or self.dataWidth==CAENVMETypes.cvDWDict['D32sw']):
            return(data.value & 0xFFFFFFFF)
        raise CAENErr(CAENVMETypes.CVErrors.cvInvalidParam)

    def WriteCycle(self, addr, data, am='A24_U_DATA', dw='D16'):
        self.addressModifier = CAENVMETypes.cvAMDict[am]
        self.dataWidth       = CAENVMETypes.cvDWDict[dw]
        d = c_void_p(data)
        cvRetError = vme.CAENVME_WriteCycle(c_long(self.handle), c_ulong(addr), \
            byref(d), c_int(self.addressModifier), c_int(self.dataWidth))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)

    def GetFIFOMode(self):
        pMode = pointer(c_short(-1))
        cvRetError = vme.CAENVME_GetFIFOMode(c_long(self.handle), pMode)
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        return(pMode.contents.value)

    def SetFIFOMode(self, mode):
        cvRetError = vme.CAENVME_SetFIFOMode(c_long(self.handle), c_short(mode))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)  

    def ReadCycleBLT(self, addr, size, am='A24_U_BLT', dw='D32sw'):
        self.addressModifier = CAENVMETypes.cvAMDict[am]
        self.dataWidth       = CAENVMETypes.cvDWDict[dw]
        buffType = c_ubyte * size
        myBuff = buffType()      
        count = c_int(-1)
        cvRetError = vme.CAENVME_BLTReadCycle(
            c_long(self.handle), c_ulong(addr), byref(myBuff), c_int(size), \
            c_int(self.addressModifier), \
            c_int(self.dataWidth), \
            byref(count))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        return [myBuff[i] for i in range(count.value)]

##    def ReadCycleBLT(self, addr, size):
##        buffType = c_ubyte * size
##        myBuff = buffType()      
##        count = c_int(-1)
##        cvRetError = vme.CAENVME_BLTReadCycle(
##            c_long(self.handle), c_ulong(addr), byref(myBuff), c_int(size), \
##            c_int(CAENVMETypes.CVAddressModifier.cvA24_U_BLT), \
##            c_int(CAENVMETypes.CVDataWidth.cvD16_swapped), \
##            byref(count))
##        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
##            raise CAENErr(cvRetError)
##        return [myBuff[i] for i in range(count.value)]

    def GetTimeout(self):   #added 2014.10.11
        timeout = c_int(-1) 
        cvRetError = vme.CAENVME_GetTimeout(c_long(self.handle), byref(timeout))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        return(CAENVMETypes.cvTimeoutDict[timeout.value])

    def SetTimeout(self, timeouttype):   #added 2014.10.11
        if timeouttype in CAENVMETypes.cvTimeoutDict:
            timeout = c_int(timeouttype) 
            cvRetError = vme.CAENVME_SetTimeout(c_long(self.handle), timeout)
            if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
                raise CAENErr(cvRetError)
            return(CAENVMETypes.cvTimeoutDict[timeout.value])
        else:
            raise CAENErr(CAENVMETypes.CVErrors.cvInvalidParam)
