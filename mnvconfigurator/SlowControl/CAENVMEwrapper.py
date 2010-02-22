#!/usr/bin/python

from ctypes import *
#vme = windll.CAENVMElib
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



    def ReadCycleMBLT(self, addr, size):
        print 'inside ReadCycleMBLT'
        cubyte=c_ubyte(0)
        pcubyte=pointer(cubyte)
        data = c_char_p('')

        count = c_int(0)
        cvRetError = vme.CAENVME_MBLTReadCycle(c_long(self.handle), c_ulong(addr), \
            pcubyte, c_int(size), c_int(self.addressModifier), byref(count))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)

        print count, count.value
        print pcubyte
        print pcubyte.contents
        for i in range(size):
            print i, pcubyte[i], hex(pcubyte[i])
            
    def ReadCycleBLT(self, addr, size):
        print 'inside ReadCycleBLT'
        cubyte=c_ubyte(0)
        #cubyte=create_string_buffer(size)
        pcubyte=pointer(cubyte)
        data = c_char_p('')
        #print data, repr(data.value)

        count = c_int(0)
        cvRetError = vme.CAENVME_BLTReadCycle(c_long(self.handle), c_ulong(addr), \
            pcubyte, c_int(size), c_int(self.addressModifier), c_int(self.dataWidth), byref(count))
        if cvRetError!=CAENVMETypes.CVErrors.cvSuccess:
            raise CAENErr(cvRetError)
        
        #print data, repr(data.value)
        print count, count.value

        print pcubyte, pcubyte.contents
        #print sizeof(pcubyte.contents), repr( (pcubyte.contents).raw  )        
        for i in range(2*size):
            print i, pcubyte[i], hex(pcubyte[i])

        #buffer_size = size * sizeof(c_char)
        #data_buffer = create_string_buffer(buffer_size) 
        #memmove(data_buffer, pcubyte, buffer_size)
        #print data_buffer, data_buffer.value

  
if __name__ == '__main__':
    try:
        ctrl = Controller()
        print 'CAENVME Library v.%s'%ctrl.SWRelease()
        ctrl.Init(CAENVMETypes.CVBoardTypes.cvV2718, 0, 0)
        print 'Controller initialized:'
        print '\thandle = %s'%ctrl.handle
        print '\tCAENVME software = %s'%ctrl.SWRelease()
        #print '\tV2718   firmware = %s'%ctrl.BoardFWRelease()
        addr=0x068000; size=8
        ctrl.ReadCycleMBLT(addr, size)
        #ctrl.ReadCycleBLT(addr+2, size)
        
        #addr = 0x06F000; data = randint(0, 0x1FFFF)
        #print('WriteCycle: ' + ctrl.WriteCycle(addr, data))
        #print('WriteCycle: address = ' + hex(addr) + ', Wdata = ' + str(data))
        #addr = 0x40F000; data = 0x0
        #print('ReadCycle : address = ' + hex(addr) + ', Rdata = ' + str(ctrl.ReadCycle(addr, data)))

        #print('Controller end = ' + str(ctrl.End()))
        #print('Controller handle = ' + str(ctrl.handle))

    except:
        import sys
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]       


