#ifndef FPGAFrame_h
#define FPGAFrame_h

#include "FrameTypes.h"
#include "LVDSFrame.h"

/*! \class FPGAFrame
 *
 * \brief The class which holds all of the information associated with an FPGAFrame.
 *
 */

class FPGAFrame : public LVDSFrame {
	private:

		unsigned int Timer, TestPulseCount, GateTimeStamp;
		unsigned short GateStart, GateLength, InjectDACValue, HVTarget, 
			HVActual, DCM2PhaseTotal, HVPeriodAuto, HVPeriodManual, Temperature,
			DiscrimEnableMask[4]; // One element each for trips 0-3
		unsigned char TripPowerOff[1], InjectCount[6][1], InjectEnable[6][1], 
			InjectRange[1], InjectPhase[1], InjectDACMode[1], InjectDACDone[1], 
			InjectDACStart[1], HVEnabled[1], HVControl[1], HVManual[1], 
			statusTXSyncLock[1], statusRXLock[1], PhaseStart[1], PhaseIncrement[1], 
			statusSCMDUnknown[1], statusFCMDUnknown[1],PhaseCount[1], 
			DCM1Lock[1], DCM2Lock[1], DCM1NoClock[1], DCM2NoClock[1], DCM2PhaseDone[1], 
			TestPulse2Bit[1], FirmwareVersion[1], boardID[1],
			HVNumAve[1], HVPulseWidth[1], TripXThresh[1], TripXCompEnc[1],
			ExtTriggerFound[1], ExtTriggerRearm[1], AfterPulseExtendedWidth[1],
			PreviewEnable[1], firmwareVersion[1];

	public:
		FPGAFrame( FrameTypes::febAddresses theAddress ); 
		~FPGAFrame(){};


		void SetFPGAFrameDefaultValues();
		void ShowValues();
		void MakeMessage(); 
		void MakeShortMessage();
		void DecodeRegisterValues();
    unsigned int GetOutgoingMessageLength();

		unsigned char inline  GetFirmwareVersion() const { 
      return FirmwareVersion[0]; 
    };
		unsigned int inline   GetTimer() const {
      return Timer; 
    };
		unsigned short inline GetGateStart() const {
      return GateStart; 
    };
		unsigned short inline GetGateLength() const {
      return GateLength; 
    };
    unsigned char inline  GetBoardID() const {
      return boardID[0]; 
    };
		unsigned char inline  GetTripPowerOff() const {
      return TripPowerOff[0]; 
    };
		unsigned char inline  GetInjCount0() const {
      return InjectCount[0][0]; 
    };
		unsigned char inline  GetInjCount1() const {
      return InjectCount[1][0]; 
    };
		unsigned char inline  GetInjCount2() const {
      return InjectCount[2][0]; 
    };
		unsigned char inline  GetInjCount3() const {
      return InjectCount[3][0]; 
    };
		unsigned char inline  GetInjCount4() const {
      return InjectCount[4][0]; 
    };
		unsigned char inline  GetInjCount5() const {
      return InjectCount[5][0]; 
    };
		unsigned char inline  GetInjEnable0() const {
      return InjectEnable[0][0]; 
    };
		unsigned char inline  GetInjEnable1() const {
      return InjectEnable[1][0]; 
    };
		unsigned char inline  GetInjEnable2() const {
      return InjectEnable[2][0]; 
    };
		unsigned char inline  GetInjEnable3() const {
      return InjectEnable[3][0]; 
    };
		unsigned char inline  GetInjEnable4() const {
      return InjectEnable[4][0]; 
    };
		unsigned char inline  GetInjEnable5() const {
      return InjectEnable[5][0]; 
    };
		unsigned char inline  GetInjectRange() const {
      return InjectRange[0]; 
    };
		unsigned char inline  GetInjectPhase() const {
      return InjectPhase[0]; 
    };
		unsigned short inline GetInjDACValue() const {
      return InjectDACValue; 
    };
		unsigned char inline  GetInjDACMode() const {
      return InjectDACMode[0]; 
    };
		unsigned char inline  GetInjDACStart() const {
      return InjectDACStart[0]; 
    };
		unsigned char inline  GetInjDACDone() const {
      return InjectDACDone[0]; 
    };
		unsigned char inline  GetHVEnabled() const {
      return HVEnabled[0]; 
    };
		unsigned short inline GetHVTarget() const {
      return HVTarget; 
    };
		unsigned short inline GetHVActual() const {
      return HVActual; 
    };
		unsigned char inline  GetHVControl() const {
      return HVControl[0]; 
    };
		unsigned char inline  GetHVManual() const {
      return HVManual[0]; 
    };
		unsigned char inline  GetStatusRXLock() const {
      return statusRXLock[0]; 
    };
		unsigned char inline  GetStatusTXSyncLock() const {
      return statusTXSyncLock[0]; 
    };
		unsigned char inline  GetPhaseStart() const {
      return PhaseStart[0]; 
    };
		unsigned char inline  GetPhaseInc() const {
      return PhaseIncrement[0]; 
    };
		unsigned char inline  GetPhaseCount() const {
      return PhaseCount[0]; 
    };
		unsigned char inline  GetStatusSCMDUnknown() const {
      return statusSCMDUnknown[0]; 
    };
		unsigned char inline  GetStatusFCMDUnknown() const {
      return statusFCMDUnknown[0]; 
    };
		unsigned char inline  GetDCM1Lock() const {
      return DCM1Lock[0]; 
    };
		unsigned char inline  GetDCM2Lock() const {
      return DCM2Lock[0]; 
    };
		unsigned char inline  GetDCM1NoClock() const {
      return DCM1NoClock[0]; 
    };
		unsigned char inline  GetDCM2NoClock() const {
      return DCM2NoClock[0]; 
    };
		unsigned char inline  GetDCM2PhaseDone() const {
      return DCM2PhaseDone[0]; 
    };
		unsigned short inline GetDCM2PhaseTotal() const {
      return DCM2PhaseTotal; 
    };
		unsigned char inline  GetTP2Bit() const {
      return TestPulse2Bit[0]; 
    };
		unsigned int inline   GetTPCount() const {
      return TestPulseCount; 
    };
		unsigned char inline  GetHVNumAvg() const {
      return HVNumAve[0]; 
    };
		unsigned short inline GetHVPeriodManual() const {
      return HVPeriodManual; 
    };
		unsigned short inline GetHVPeriodAuto() const {
      return HVPeriodAuto; 
    };
		unsigned char inline  GetHVPulseWidth() const {
      return HVPulseWidth[0]; 
    };
		unsigned short inline GetTemperature() const {
      return Temperature; 
    };
		unsigned char inline  GetTripXThresh() const {
      return TripXThresh[0]; 
    };
		unsigned char inline  GetTripXCompEnc() const {
      return TripXCompEnc[0]; 
    };
		unsigned char inline  GetExtTriggerFound() const {
      return ExtTriggerFound[0]; 
    };
		unsigned char inline  GetExtTriggerRearm() const {
      return ExtTriggerRearm[0]; 
    };
		unsigned short inline GetDiscEnMask0() const {
      return DiscrimEnableMask[0]; 
    };
		unsigned short inline GetDiscEnMask1() const {
      return DiscrimEnableMask[1]; 
    };
		unsigned short inline GetDiscEnMask2() const {
      return DiscrimEnableMask[2]; 
    };
		unsigned short inline GetDiscEnMask3() const {
      return DiscrimEnableMask[3]; 
    };
		unsigned int inline   GetGateTimeStamp() const {
      return GateTimeStamp; 
    };
		unsigned char inline  GetAfterPulseExtendedWidth() const {
      return AfterPulseExtendedWidth[0]; 
    };
		unsigned char inline  GetPreviewEnable() const {
      return PreviewEnable[0]; 
    };

		void inline SetTimer(unsigned int a) {
      Timer=a;
    };
		void inline SetGateStart(unsigned short a) {
      GateStart=a;
    };
		void inline SetGateLength(unsigned short a) {
      GateLength=a;
    };
		void inline SetInjectDACValue(unsigned short a) {
      InjectDACValue=a;
    };
		void inline SetHVTarget(unsigned short a) {
      HVTarget=a;
    };
		void inline SetHVPeriodManual(unsigned short a) {
      HVPeriodManual=a;
    };
		void inline SetTripPowerOff(unsigned char *a) {
      TripPowerOff[0]=a[0];
    };
		void inline SetInjectCount(unsigned char *a, int i) {
      InjectCount[i][0]=a[0];
    };
		void inline SetInjectEnable(unsigned char *a, int i) {
      InjectEnable[i][0]=a[0];
    };
		void inline SetInjectRange(unsigned char *a) {
      InjectRange[0]=a[0];
    };
		void inline SetInjectPhase(unsigned char *a) {
      InjectPhase[0]=a[0];
    };
		void inline SetInjectDACMode(unsigned char *a) {
      InjectDACMode[0]=a[0];
    };
		void inline SetInjectDACStart(unsigned char *a) {
      InjectDACStart[0]=a[0];
    };
		void inline SetHVEnabled(unsigned char *a) {
      HVEnabled[0]=a[0];
    };
		void inline SetHVManual(unsigned char *a) {
      HVManual[0]=a[0];
    };
		void inline SetPhaseStart(unsigned char *a) {
      PhaseStart[0]=a[0];
    };
		void inline SetPhaseIncrement(unsigned char *a) {
      PhaseIncrement[0]=a[0];
    };
		void inline SetPhaseCount(unsigned char *a) {
      PhaseCount[0]=a[0];
    };
		void inline SetHVNumAve(unsigned char *a) {
      HVNumAve[0]=a[0];
    };
		void inline SetHVPulseWidth(unsigned char *a) {
      HVPulseWidth[0]=a[0];
    };
		void inline SetTripXThresh(unsigned char *a) {
      TripXThresh[0]=a[0];
    };
		void inline SetExtTriggerRearm(unsigned char *a) {
      ExtTriggerRearm[0]=a[0];
    };
		void inline SetDiscrimEnableMask(unsigned short a, int i) {
      DiscrimEnableMask[i]=a;
    };
		void inline SetAfterPulseExtendedWidth(unsigned char *a) {
      AfterPulseExtendedWidth[0]=a[0];
    };
		void inline SetPreviewEnable(unsigned char *a) { 
      PreviewEnable[0]=a[0];
    };
};

#endif
