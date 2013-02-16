#ifndef FEB_h
#define FEB_h

#include "trips.h"
#include "FrameTypes.h"
#include "Frames.h"
#include "adctdc.h"

/*********************************************************************************
* Class for creating Front-End Board (FEB) objects for use with the 
* MINERvA data acquisition system and associated software projects.
*
* Elaine Schulte, Rutgers University
* Gabriel Perdue, The University of Rochester
*
**********************************************************************************/

/*! \class FEB
 *
 * \brief The class which holds all of the information associated with an FEB 
 *
 * This class holds all of the informatio about an FEB including the TRiP-T 
 * initialization.
 *
 */

class FEB : public Frames {
	private:
		febAddresses boardNumber;         /*!< the FEB board number (1-15) */
		unsigned char firmwareVersion[1]; /*!< the firmware version on this board */
		int TrueIncomingMessageLength;    /*!< true FEB incoming message length */
		trips *tripChips[6];              /*!< the trip objects for this FEB */
		adc *adcHits[8];                  /*!< The ADC objects for this FEB; We can have as many as 8 hits. */
		disc *hits_n_timing;              /*!< The discriminator for this FEB */

		unsigned char *buffer; 
		int NRegisters; 

		/*! here are some variables for the data about the FEB */
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
			PreviewEnable[1];

	public:
		FEB( febAddresses theAddress ); 
		~FEB() {
			for (int i=0;i<6;i++) delete tripChips[i]; 
			for (unsigned int i=0;i<ADCFramesMaxNumber;i++) delete adcHits[i]; 
			delete hits_n_timing;
		};    
		// Must clean up FEB outoingMessage arrays manually on a use-by-use basis!
		// We do not kill them in the destructor!


		/*! Get functions */
		febAddresses inline GetBoardNumber() {return boardNumber;};
		int inline GetFirmwareVersion() {return (int)FirmwareVersion[0];};
		int inline GetMaxHits() {return ADCFramesMaxNumber;};
		inline unsigned char *GetBuffer() {return buffer;};

		inline trips *GetTrip(int i) {return tripChips[i];};
		inline adc *GetADC(int i) {return adcHits[i];};
		inline adc **GetADC() {return adcHits;};
		inline disc *GetDisc() {return hits_n_timing;};

		/*! Set functions */
		void SetFEBDefaultValues();
		void ShowValues();
		void MakeMessage();
		void MakeShortMessage();
		int DecodeRegisterValues(int);
		int inline GetExpectedIncomingMessageLength() {return TrueIncomingMessageLength;};

		/*! Get functions for FPGA read */
		const unsigned int inline   GetTimer() const             { return Timer; };
		const unsigned short inline GetGateStart() const         { return GateStart; };
		const unsigned short inline GetGateLength() const        { return GateLength; };
    const unsigned char inline  GetBoardID() const           { return boardID[0]; };
		const unsigned char inline  GetTripPowerOff() const      { return TripPowerOff[0]; };
		const unsigned char inline  GetInjCount0() const         { return InjectCount[0][0]; };
		const unsigned char inline  GetInjCount1() const         { return InjectCount[1][0]; };
		const unsigned char inline  GetInjCount2() const         { return InjectCount[2][0]; };
		const unsigned char inline  GetInjCount3() const         { return InjectCount[3][0]; };
		const unsigned char inline  GetInjCount4() const         { return InjectCount[4][0]; };
		const unsigned char inline  GetInjCount5() const         { return InjectCount[5][0]; };
		const unsigned char inline  GetInjEnable0() const        { return InjectEnable[0][0]; };
		const unsigned char inline  GetInjEnable1() const        { return InjectEnable[1][0]; };
		const unsigned char inline  GetInjEnable2() const        { return InjectEnable[2][0]; };
		const unsigned char inline  GetInjEnable3() const        { return InjectEnable[3][0]; };
		const unsigned char inline  GetInjEnable4() const        { return InjectEnable[4][0]; };
		const unsigned char inline  GetInjEnable5() const        { return InjectEnable[5][0]; };
		const unsigned char inline  GetInjectRange() const       { return InjectRange[0]; };
		const unsigned char inline  GetInjectPhase() const       { return InjectPhase[0]; };
		const unsigned short inline GetInjDACValue() const       { return InjectDACValue; };
		const unsigned char inline  GetInjDACMode() const        { return InjectDACMode[0]; };
		const unsigned char inline  GetInjDACStart() const       { return InjectDACStart[0]; };
		const unsigned char inline  GetInjDACDone() const        { return InjectDACDone[0]; };
		const unsigned char inline  GetHVEnabled() const         { return HVEnabled[0]; };
		const unsigned short inline GetHVTarget() const          { return HVTarget; };
		const unsigned short inline GetHVActual() const          { return HVActual; };
		const unsigned char inline  GetHVControl() const         { return HVControl[0]; };
		const unsigned char inline  GetHVManual() const          { return HVManual[0]; };
		const unsigned char inline  GetStatusRXLock() const      { return statusRXLock[0]; };
		const unsigned char inline  GetStatusTXSyncLock() const  { return statusTXSyncLock[0]; };
		const unsigned char inline  GetPhaseStart() const        { return PhaseStart[0]; };
		const unsigned char inline  GetPhaseInc() const          { return PhaseIncrement[0]; };
		const unsigned char inline  GetPhaseCount() const        { return PhaseCount[0]; };
		const unsigned char inline  GetStatusSCMDUnknown() const { return statusSCMDUnknown[0]; };
		const unsigned char inline  GetStatusFCMDUnknown() const { return statusFCMDUnknown[0]; };
		const unsigned char inline  GetDCM1Lock() const          { return DCM1Lock[0]; };
		const unsigned char inline  GetDCM2Lock() const          { return DCM2Lock[0]; };
		const unsigned char inline  GetDCM1NoClock() const       { return DCM1NoClock[0]; };
		const unsigned char inline  GetDCM2NoClock() const       { return DCM2NoClock[0]; };
		const unsigned char inline  GetDCM2PhaseDone() const     { return DCM2PhaseDone[0]; };
		const unsigned short inline GetDCM2PhaseTotal() const    { return DCM2PhaseTotal; };
		const unsigned char inline  GetTP2Bit() const            { return TestPulse2Bit[0]; };
		const unsigned int inline   GetTPCount() const           { return TestPulseCount; };
		const unsigned char inline  GetHVNumAvg() const          { return HVNumAve[0]; };
		const unsigned short inline GetHVPeriodManual() const    { return HVPeriodManual; };
		const unsigned short inline GetHVPeriodAuto() const      { return HVPeriodAuto; };
		const unsigned char inline  GetHVPulseWidth() const      { return HVPulseWidth[0]; };
		const unsigned short inline GetTemperature() const       { return Temperature; };
		const unsigned char inline  GetTripXThresh() const       { return TripXThresh[0]; };
		const unsigned char inline  GetTripXCompEnc() const      { return TripXCompEnc[0]; };
		const unsigned char inline  GetExtTriggerFound() const   { return ExtTriggerFound[0]; };
		const unsigned char inline  GetExtTriggerRearm() const   { return ExtTriggerRearm[0]; };
		const unsigned short inline GetDiscEnMask0() const       { return DiscrimEnableMask[0]; };
		const unsigned short inline GetDiscEnMask1() const       { return DiscrimEnableMask[1]; };
		const unsigned short inline GetDiscEnMask2() const       { return DiscrimEnableMask[2]; };
		const unsigned short inline GetDiscEnMask3() const       { return DiscrimEnableMask[3]; };
		const unsigned int inline   GetGateTimeStamp() const     { return GateTimeStamp; };
		// new v90 registers...
		const unsigned char inline  GetAfterPulseExtendedWidth() const { return AfterPulseExtendedWidth[0]; };
		const unsigned char inline  GetPreviewEnable() const           { return PreviewEnable[0]; };

		/*! set functions for FEB setable values */
		void inline SetTimer(unsigned int a) {Timer=a;};
		void inline SetGateStart(unsigned short a) {GateStart=a;};
		void inline SetGateLength(unsigned short a) {GateLength=a;};
		void inline SetInjectDACValue(unsigned short a) {InjectDACValue=a;};
		void inline SetHVTarget(unsigned short a) {HVTarget=a;};
		void inline SetHVPeriodManual(unsigned short a) {HVPeriodManual=a;};
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
		void inline SetInjectDACStart(unsigned char *a) {InjectDACStart[0]=a[0];};
		void SetInjectDACStart(char *a);
		void inline SetHVEnabled(unsigned char *a) {HVEnabled[0]=a[0];};
		void SetHVEnabled(char *a);
		void inline SetHVManual(unsigned char *a) {HVManual[0]=a[0];};
		void SetHVManual(char *a);
		void inline SetPhaseStart(unsigned char *a) {PhaseStart[0]=a[0];};
		void SetPhaseStart(char *a);
		void inline SetPhaseIncrement(unsigned char *a) {PhaseIncrement[0]=a[0];};
		void SetPhaseIncrement(char *a);
		void inline SetPhaseCount(unsigned char *a) {PhaseCount[0]=a[0];};
		void SetPhaseCount(char *a);
		void inline SetHVNumAve(unsigned char *a) {HVNumAve[0]=a[0];};
		void SetHVNumAve(char *a);
		void inline SetHVPulseWidth(unsigned char *a) {HVPulseWidth[0]=a[0];};
		void SetHVPulseWidth(char *a);
		void inline SetTripXThresh(unsigned char *a) {TripXThresh[0]=a[0];};
		void SetTripXThresh(char *a);
		void inline SetExtTriggerRearm(unsigned char *a) {ExtTriggerRearm[0]=a[0];};
		void SetExtTriggerRearm(char *a);
		void inline SetDiscrimEnableMask(unsigned short a, int i) {DiscrimEnableMask[i]=a;};
		// new v90 registers...
		void inline SetAfterPulseExtendedWidth(unsigned char *a) {AfterPulseExtendedWidth[0]=a[0];};
		void SetAfterPulseExtendedWidth(char *a);
		void inline SetPreviewEnable(unsigned char *a) {PreviewEnable[0]=a[0];};
		void SetPreviewEnable(char *a);
};

#endif
