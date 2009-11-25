#ifndef feb_h
#define feb_h

/* system headers go here */

/* CAEN VME headers go here */

/* custom headers go here */
#include "trips.h"
#include "FrameTypes.h"
#include "Frames.h"
#include "adctdc.h"

/*********************************************************************************
 * Class for creating Front-End Board (FEB) objects for use with the 
 * MINERvA data acquisition system and associated software projects.
 *
 * Elaine Schulte, Rutgers University
 * April 22, 2009
 *
 **********************************************************************************/

/*! \class feb
 *
 * \brief The class which holds all of the information associated with an FEB 
 *
 * This class holds all of the informatio about an FEB including the TRiP-T 
 * initialization.
 *
 */

class feb : public Frames {
  private:
    febAddresses boardNumber; /*!< the FEB board number (1-15) */
    unsigned char firmwareVersion[1]; /*!< the firmware version on this board */
    int maxHits; /*!< the maximum number of hits a discriminator can take */
    bool initialized;  /*!< a flag for the initialization state of this FEB */
    trips *tripChips[6]; /*!< the trip objects for this FEB */
    adc *adcHits[6]; //we can have as many as 6 hits (for now) /*!< The ADC objects for this FEB */
    disc *hits_n_timing; //timing & number of hits /*!< The discriminator for this FEB */

    unsigned char *buffer; /*!< a buffer for FEB data */
    const int NRegisters; /*!< the number of registers this FEB's firmware has */

    /*! here are some variables for the data about the feb */
    unsigned int Timer, TestPulseCount, GateTimeStamp;
    unsigned short GateStart, GateLength, InjectDACValue, HVTarget, 
      HVActual, DCM2PhaseTotal, HVPeriodAuto, HVPeriodManual, Temperature,
      DiscrimEnableMask[4]; // One element each for trips 0-3
    unsigned char TripPowerOff[1], InjectCount[6][1], InjectEnable[6][1], 
      InjectRange[1], InjectPhase[1], InjectDACMode[1], InjectDACDone[1], 
      InjectDACStart[1], HVEnabled[1], HVControl[1], HVManual[1], 
      VXOOff[1], VXOMuxXilinx[1], PhaseStart[1], PhaseIncrement[1], 
      PhaseSpare[1], PhaseCount[1], DCM1Lock[1], DCM2Lock[1], 
      DCM1NoClock[1], DCM2NoClock[1], DCM2PhaseDone[1], 
      TestPulse2Bit[1], FirmwareVersion[1], boardID[1],
      HVNumAve[1], HVPulseWidth[1], CosmicTrig[1], TripXCompEnc[1],
      ExtTriggerFound[1], ExtTriggerRearm[1];

  public:
     feb(int, bool, febAddresses, int reg, std::ofstream &log_file);
    /*! The constructor */
    //feb(int, bool, febAddresses, int reg); // allocate new space for trips, adc's, discriminators
    /*! The destructor */
    ~feb() {
       for (int i=0;i<6;i++) delete tripChips[i]; 
       for (int i=0;i<6;i++) delete adcHits[i];
       delete hits_n_timing;
    };    
		// Must clean up FEB outoingMessage arrays manually on a use-by-use basis!
		// We do not kill them in the destructor!


    /*! Get functions */
    febAddresses inline GetBoardNumber() {return boardNumber;};
    int inline GetFWB() {return (int)FirmwareVersion[0];};
    int inline GetFirmwareVersion() {return (int)FirmwareVersion[0];};
    int inline GetMaxHits() {return maxHits;};
    bool inline GetInit() {return initialized;};
    inline unsigned char *GetBuffer() {return buffer;};
    
    inline trips *GetTrip(int i) {return tripChips[i];};
    inline adc *GetADC(int i) {return adcHits[i];};
    inline adc **GetADC() {return adcHits;};
    inline disc *GetDisc() {return hits_n_timing;};

    /*! Set functions */
    void inline SetMaxHits(int a) {maxHits=a;};
    void inline SetInitialized(bool a) {initialized=a;};
    void SetFEBDefaultValues();
    void ShowValues();
    void MakeMessage();
    void DecodeRegisterValues(int);

    /*! Get functions for FPGA read */
    unsigned int inline GetTimer() {return Timer;};
    unsigned short inline GetGateStart() {return GateStart;};
    unsigned short inline GetGateLength() {return GateLength;};
    unsigned char inline GetTripPowerOff() {return TripPowerOff[0];};
    unsigned char inline GetInjCount0() {return InjectCount[0][0];};
    unsigned char inline GetInjCount1() {return InjectCount[1][0];};
    unsigned char inline GetInjCount2() {return InjectCount[2][0];};
    unsigned char inline GetInjCount3() {return InjectCount[3][0];};
    unsigned char inline GetInjCount4() {return InjectCount[4][0];};
    unsigned char inline GetInjCount5() {return InjectCount[5][0];};
    unsigned char inline GetInjEnable0() {return InjectEnable[0][0];};
    unsigned char inline GetInjEnable1() {return InjectEnable[1][0];};
    unsigned char inline GetInjEnable2() {return InjectEnable[2][0];};
    unsigned char inline GetInjEnable3() {return InjectEnable[3][0];};
    unsigned char inline GetInjEnable4() {return InjectEnable[4][0];};
    unsigned char inline GetInjEnable5() {return InjectEnable[5][0];};
    unsigned char inline GetInjectRange() {return InjectRange[0];};
    unsigned char inline GetInjectPhase() {return InjectPhase[0];};
    unsigned short inline GetInjDACValue() {return InjectDACValue;};
    unsigned char inline GetInjDACMode() {return InjectDACMode[0];};
    unsigned char inline GetInjDACStart() {return InjectDACStart[0];};
    unsigned char inline GetInjDACDone() {return InjectDACDone[0];};
    unsigned char inline GetHVEnabled() {return HVEnabled[0];};
    unsigned short inline GetHVTarget() {return HVTarget;};
    unsigned short inline GetHVActual() {return HVActual;};
    unsigned char inline GetHVControl() {return HVControl[0];};
    unsigned char inline GetHVManual() {return HVManual[0];};
    unsigned char inline GetVXOXilinx() {return VXOMuxXilinx[0];};
    unsigned char inline GetPhaseStart() {return PhaseStart[0];};
    unsigned char inline GetPhaseInc() {return PhaseIncrement[0];};
    unsigned char inline GetPhaseSpare() {return PhaseSpare[0];};
    unsigned char inline GetPhaseCount() {return PhaseCount[0];};
    unsigned char inline GetDCM1Lock() {return DCM1Lock[0];};
    unsigned char inline GetDCM2Lock() {return DCM2Lock[0];};
    unsigned char inline GetDCM1NoClock() {return DCM1NoClock[0];};
    unsigned char inline GetDCM2NoClock() {return DCM2NoClock[0];};
    unsigned char inline GetDCM2PhaseDone() {return DCM2PhaseDone[0];};
    unsigned short inline GetDCM2PhaseTotal() {return DCM2PhaseTotal;};
    unsigned char inline GetTP2Bit() {return TestPulse2Bit[0];};
    unsigned int inline GetTPCount() {return TestPulseCount;};
    unsigned char inline GetVersion() {return FirmwareVersion[0];};
    unsigned char inline GetHVNumAvg() {return HVNumAve[0];};
    unsigned short inline GetHVPeriodManual() {return HVPeriodManual;};
    unsigned short inline GetHVPeriodAuto() {return HVPeriodAuto;};
    unsigned char inline GetHVPulseWidth() {return HVPulseWidth[0];};
    unsigned short inline GetTemperature() {return Temperature;};
    unsigned char inline GetTripXCompEnc() {return TripXCompEnc[0];};
    unsigned char inline GetExtTriggerFound() {return ExtTriggerFound[0];};
    unsigned char inline GetExtTriggerRearm() {return ExtTriggerRearm[0];};
    unsigned short inline GetDiscEnMask0() {return DiscrimEnableMask[0];};
    unsigned short inline GetDiscEnMask1() {return DiscrimEnableMask[1];};
    unsigned short inline GetDiscEnMask2() {return DiscrimEnableMask[2];};
    unsigned short inline GetDiscEnMask3() {return DiscrimEnableMask[3];};
    unsigned int inline GetGateTimeStamp() {return GateTimeStamp;};
    /*! set functions for FEB setable values */
    void inline SetTimer(unsigned int a) {Timer=a;};
    void inline SetTestPulseCount(unsigned int a) {TestPulseCount=a;};
	void inline SetGateTimeStamp(unsigned int a) {GateTimeStamp=a;};
    void inline SetGateStart(unsigned short a) {GateStart=a;};
    void inline SetGateLength(unsigned short a) {GateLength=a;};
    void inline SetInjectDACValue(unsigned short a) {InjectDACValue=a;};
    void inline SetHVTarget(unsigned short a) {HVTarget=a;};
    void inline SetHVActual(unsigned short a) {HVActual=a;};
    void inline SetDCM2PhaseTotal(unsigned short a) {DCM2PhaseTotal=a;};
    void inline SetHVPeriodAuto(unsigned short a) {HVPeriodAuto=a;};
    void inline SetHVPeriodManual(unsigned short a) {HVPeriodManual=a;};
    void inline SetTemperature(unsigned short a) {Temperature=a;};
    void inline SetTripPowerOff(unsigned char *a) {TripPowerOff[0]=a[0];};
	void SetTripPowerOff(char *a);
    void inline SetInjectCount(unsigned char *a, int i) {InjectCount[i][0]=a[0];};
	void SetInjectCount(char *a, int i);
    void inline SetInjectEnable(unsigned char *a, int i) {InjectEnable[i][0]=a[0];};
	void SetInjectEnable(char *a, int i);
    void inline SetInjectRange(unsigned char *a) {InjectRange[0]=a[0];};
	void SetInjectRange(char *a);
    void inline SetInjectPhase(unsigned char *a) {InjectPhase[0]=a[0];};
    void SetInjectPhase(char *a);
	void inline SetInjectDACMode(unsigned char *a) {InjectDACMode[0]=a[0];};
    void SetInjectDACMode(char *a);
    void inline SetInjectDACDone(unsigned char *a) {InjectDACDone[0]=a[0];};
    void SetInjectDACDone(char *a);
    void inline SetInjectDACStart(unsigned char *a) {InjectDACStart[0]=a[0];};
    void SetInjectDACStart(char *a);
    void inline SetHVEnabled(unsigned char *a) {HVEnabled[0]=a[0];};
    void SetHVEnabled(char *a);
    void inline SetHVControl(unsigned char *a) {HVControl[0]=a[0];};
    void SetHVControl(char *a);
    void inline SetHVManual(unsigned char *a) {HVManual[0]=a[0];};
    void SetHVManual(char *a);
    void inline SetVXOOff(unsigned char *a) {VXOOff[0]=a[0];};
    void SetVXOOff(char *a);
    void inline SetVXOMuxXilinx(unsigned char *a) {VXOMuxXilinx[0]=a[0];};
    void SetVXOMuxXilinx(char *a);
    void inline SetPhaseStart(unsigned char *a) {PhaseStart[0]=a[0];};
    void SetPhaseStart(char *a);
    void inline SetPhaseIncrement(unsigned char *a) {PhaseIncrement[0]=a[0];};
    void SetPhaseIncrement(char *a);
    void inline SetPhaseSpare(unsigned char *a) {PhaseSpare[0]=a[0];};
    void SetPhaseSpare(char *a);
    void inline SetPhaseCount(unsigned char *a) {PhaseCount[0]=a[0];};
    void SetPhaseCount(char *a);
    void inline SetDCM1Lock(unsigned char *a) {DCM1Lock[0]=a[0];};
    void SetDCM1Lock(char *a);
    void inline SetDCM2Lock(unsigned char *a) {DCM2Lock[0]=a[0];};
    void SetDCM2Lock(char *a);
    void inline SetDCM1NoClock(unsigned char *a) {DCM1NoClock[0]=a[0];};
    void SetDCM1NoClock(char *a);
    void inline SetDCM2NoClock(unsigned char *a) {DCM2NoClock[0]=a[0];};
    void SetDCM2NoClock(char *a);
    void inline SetDCM2PhaseDone(unsigned char *a) {DCM2PhaseDone[0]=a[0];};
    void SetDCM2PhaseDone(char *a);
    void inline SetTestPulse2Bit(unsigned char *a) {TestPulse2Bit[0]=a[0];};
    void SetTestPulse2Bit(char *a);
    void inline SetBoardID(unsigned char *a) {boardID[0]=a[0];};
    void SetBoardID(char *a);
    void inline SetFirmwareVersion(unsigned char *a) {FirmwareVersion[0]=a[0];};
    void SetFirmwareVersion(char *a);
    void inline SetHVNumAve(unsigned char *a) {HVNumAve[0]=a[0];};
    void SetHVNumAve(char *a);
    void inline SetHVPulseWidth(unsigned char *a) {HVPulseWidth[0]=a[0];};
    void SetHVPulseWidth(char *a);
    void inline SetCosmicTrig(unsigned char *a) {CosmicTrig[0]=a[0];};
    void SetCosmicTrig(char *a);
    void inline SetTripXCompEnc(unsigned char *a) {TripXCompEnc[0]=a[0];};
    void SetTripXCompEnc(char *a);
    void inline SetExtTriggerFound(unsigned char *a) {ExtTriggerFound[0]=a[0];};
    void SetExtTriggerFound(char *a);
    void inline SetExtTriggerRearm(unsigned char *a) {ExtTriggerRearm[0]=a[0];};
    void SetExtTriggerRearm(char *a);
    void inline SetDiscrimEnableMask(unsigned short a, int i) {DiscrimEnableMask[i]=a;};
};

#endif
