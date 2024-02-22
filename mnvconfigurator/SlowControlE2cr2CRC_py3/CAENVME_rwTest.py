#!/usr/bin/python

from ctypes import *
vme = windll.CAENVMElib

from random import *
from .CAENVMEwrapper import *


if __name__ == '__main__':
    try:
        ctrl = Controller()
        print(('CAENVME Library v.' + ctrl.SWRelease()))
        
        print(('Controller initialized = ' + (ctrl.Init(CAENVMETypes.CVBoardTypes.cvV2718, 0, 0))))
        print(('Controller handle = ' + str(ctrl.handle)))
        print(('V2718 board firmware = ' + str(ctrl.BoardFWRelease())))
        addr = 0x40F000; data = randint(0, 0x1FFFF)
        print(('WriteCycle: ' + ctrl.WriteCycle(addr, data)))
        print(('WriteCycle: address = ' + hex(addr) + ', Wdata = ' + str(data)))
        addr = 0x40F000; data = 0x0
        print(('ReadCycle : address = ' + hex(addr) + ', Rdata = ' + str(ctrl.ReadCycle(addr, data))))

        #print('Controller end = ' + str(ctrl.End()))
        #print('Controller handle = ' + str(ctrl.handle))

    except:
        import sys
        print("Unexpected error:", sys.exc_info()[0], sys.exc_info()[1])

        
    
    
                                  

    


