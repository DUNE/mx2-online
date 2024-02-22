import SC_MainApp as SC

class TestClass():
    def Setup(self):
        print('Setup - Begin')

        #first get a controller
        theController=SC.CAENVMEwrapper.Controller()
        theController.Init(SC.CAENVMEwrapper.CAENVMETypes.CVBoardTypes.cvV2718, 0, 0) 
        print('handle=%s, SWrelease=%s, FWRelease=%s'% \
            (theController.handle, theController.SWRelease(), theController.BoardFWRelease()))

        #and hardcode some CROCs...
        addrListCROCs=[1,6]
        vmeCROCs=[] 
        for addr in addrListCROCs:
            vmeCROCs.append(SC.CROC(theController, addr<<16))
        print([c.Description() for c in vmeCROCs])

        #then take each CROC CH and find the FEBs attached
        for theCROC in vmeCROCs:
            for theCROCChannel in theCROC.Channels():
                SC.FindFEBs(theCROCChannel)
                print('Found FEBs at %s %s %s'%(theCROC.Description(),theCROCChannel.Description(),theCROCChannel.FEBs))

        #and hardcode some devices you need..
        theCROC=vmeCROCs[0]                     #; print theCROC.Description()
        theCROCChannel=theCROC.Channels()[0]    #; print theCROCChannel.Description()
        theFEB=SC.FEB(theCROCChannel.FEBs[0])   #; print theFEB.FPGADescription(theCROCChannel, theCROC)
                                                #print theFEB.FPGARead(theCROCChannel)
                                                #print '\n'.join(theFEB.GetAllHVActual(vmeCROCs))
        print('Setup - End')
        return theFEB, theCROCChannel, vmeCROCs

    #define the method for timing performance
    def TestFPGARead(self, theFEB, theCROCChannel):
        theFEB.FPGARead(theCROCChannel)
    def TestGetAllHVActual(self, theFEB, vmeCROCs):
        theFEB.GetAllHVActual(vmeCROCs)
    def TestTRIPRead(self, theFEB, theCROCChannel):
        theFEB.TRIPRead(theCROCChannel)

if __name__=='__main__':
    import timeit

    #get necessary objects...
    tc=TestClass()
    theFEB, theCROCChannel, vmeCROCs=tc.Setup()

    #run one time desired code, just because...
    tc.TestFPGARead(theFEB, theCROCChannel)
    tc.TestGetAllHVActual(theFEB, vmeCROCs)
    tc.TestTRIPRead(theFEB, theCROCChannel)

    #use timeit module...
    myStatement='tc.TestFPGARead(theFEB, theCROCChannel)'         
    nTimes=3
    nCalls=1000
    print('Runing timeit.Timer(%s)... \n%s times, %s calls each'%(myStatement,nTimes,nCalls))
    t=timeit.Timer(myStatement, 'from __main__ import tc, theFEB, theCROCChannel, vmeCROCs')

    results=t.repeat(nTimes, nCalls)
    print('Results=%s'%results)
    print('Execution time < %s seconds'%min(results))
    


