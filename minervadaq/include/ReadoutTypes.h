#ifndef ReadoutTypes_h
#define ReadoutTypes_h
/*! \file ReadoutTypes.h
*/

//! RunningMode defines the subrun type. It is not equivalent to trigger type.
/*!
  The RunningMode defines the sort of data being collected during a run and is not synonymous with 
  trigger type.  For example, the MixedBeamLightInjection RunningMode will alternate between beam 
  gates and LI gates.  The RunningMode defines the CRIM timing mode and sets the behavior of the LI 
  box and governs the switch between trigger types.  These are equivalent to OperatingMode in the 
  old Windows DAQ system.  This value is not stored in the data stream but *is* stored in the 
  SAM metadata.
  */
namespace Modes {
  typedef enum RunningModes {
    OneShot                 = 0, /*!< "OneShot" - Internal CRIM Timing, No Frequency. */
    NuMIBeam                = 1, /*!< "MTM" - MTM CRIM Timing, (No Frequency). */
    Cosmics                 = 2, /*!< "Cosmic" - Intneral CRIM Timing, w/ Frequency Set! */
    PureLightInjection      = 3, /*!< MTM CRIM Timing, (No Frequency), software gates, LI Box alive */
    MixedBeamPedestal       = 4, /*!< MTM CRIM Timing, (No Frequency), MTM && software gates */
    MixedBeamLightInjection = 5, /*!< MTM CRIM Timing, (No Frequency), MTM && software gates, LI Box alive */
    MTBFBeamMuon            = 6, /*!< MTBF=="Cosmic" - Intneral CRIM Timing, w/ Frequency Set! */
    MTBFBeamOnly            = 7  /*!< MTBF=="Cosmic" - Intneral CRIM Timing, w/ Frequency Set! */
  };
}

//! The TriggerType defines whether we issue a software gate or accept a passive signal.
/*! 
  The TriggerType dictates whether or not the DAQ issues a software gate command to the CRIM and 
  additionally is written into the DAQ Header to identify the data type for the GATE.  The value 
  assignments here must match those defined in the DAQHeader class in the MINERvA Software framework.
  */
namespace Triggers {
  typedef enum TriggerType {
    UnknownTrigger  = 0x0000,
    Pedestal        = 0x0001,
    LightInjection  = 0x0002,
    ChargeInjection = 0x0004,
    Cosmic          = 0x0008,
    NuMI            = 0x0010,
    MTBFMuon        = 0x0020,
    MTBFBeam        = 0x0040,
    MonteCarlo      = 0x0080,  /*!< Obviously, the DAQ should not write this type, ever! */
    DataMCOverlay   = 0x0081   /*!< Obviously, the DAQ should not write this type, ever! */
  };
}

//! Encode the location and physical hardware used to collect data.
namespace Detectors {
  typedef enum DetectorTypes {
    UnknownDetector        = 0x00,
    PMTTestStand           = 0x01,
    TrackingPrototype      = 0x02,
    TestBeam               = 0x04,
    FrozenDetector         = 0x08,
    UpstreamDetector       = 0x10,
    FullMinerva            = 0x20,
    DTReserved7            = 0x40,
    DTReserved8            = 0x80
  };
}

#endif
