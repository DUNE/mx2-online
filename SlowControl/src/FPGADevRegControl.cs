using System;
using System.Collections.Generic;
using System.Collections.Specialized;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Text;
using System.Windows.Forms;

namespace MinervaUserControls
{
    public partial class FPGADevRegControl : UserControl
    {
        private const int NLogicalRgisters = 60;

        private UInt32[] FPGALogicalReg = new UInt32[NLogicalRgisters];
        private bool isAdvancedGUI = false;

        #region Define Logical Registers
        public enum LogicalRegisters : byte
        {
            Timer = 0,              // 32 bits
            GateStart = 1,          // 16 bits
            GateLength = 2,         // 16 bits
            TripPowerOff = 3,       //  6 bits
            InjectCount0 = 4,       //  7 bits
            InjectCount1 = 5,       //  7 bits
            InjectCount2 = 6,       //  7 bits
            InjectCount3 = 7,       //  7 bits
            InjectCount4 = 8,       //  7 bits
            InjectCount5 = 9,       //  7 bits
            InjectEnable0 = 10,     //  1 bit
            InjectEnable1 = 11,     //  1 bit
            InjectEnable2 = 12,     //  1 bit
            InjectEnable3 = 13,     //  1 bit
            InjectEnable4 = 14,     //  1 bit
            InjectEnable5 = 15,     //  1 bit
            InjectRange = 16,       //  4 bits
            InjectPhase = 17,       //  4 bits
            InjectDACValue = 18,    // 12 bits
            InjectDACMode = 19,     //  2 bits
            InjectDACStart = 20,    //  1 bit
            InjectDACDone = 21,     //  1 bit, readonly
            HVEnabled = 22,         //  1 bit
            HVTarget = 23,          // 16 bits
            HVActual = 24,          // 16 bits, readonly
            HVControl = 25,         //  8 bits, readonly
            HVAutoManual = 26,      //  1 bit
            PhaseStart = 27,        //  1 bit
            PhaseIncrement = 28,    //  1 bit
            PhaseTicks = 29,        //  8 bits 
            DCM1Lock = 30,          //  1 bit, readonly
            DCM2Lock = 31,          //  1 bit, readonly
            DCM1NoClock = 32,       //  1 bit, readonly
            DCM2NoClock = 33,       //  1 bit, readonly
            DCM2PhaseDone = 34,     //  1 bit, readonly
            DCM2PhaseTotal = 35,    //  9 bits, readonly
            TestPulse2Bit = 36,     //  2 bits, readonly
            TestPulseCount = 37,    // 32 bits, readonly
            BoardID = 38,           //  4 bits
            FirmwareVersion = 39,   //  8 bits, readonly
            HVNumAvg = 40,          //  4 bits
            HVPeriodManual = 41,    // 16 bits
            HVPeriodAuto = 42,      // 16 bits, readonly
            HVPulseWidth = 43,      //  8 bits
            Temperature = 44,       // 16 bits, readonly
            TripXThreshold = 45,    //  8 bits
            TripXComparators = 46,  //  6 bits, readonly
            ExtTriggFound = 47,     //  1 bit, readonly ->  08.08.2008
            ExtTriggRearm = 48,     //  1 bit           ->  08.08.2008
            DiscrimEnableMaskTrip0 = 49,    // 16 bits  -> 10.30.2008
            DiscrimEnableMaskTrip1 = 50,    // 16 bits  -> 10.30.2008
            DiscrimEnableMaskTrip2 = 51,    // 16 bits  -> 10.30.2008
            DiscrimEnableMaskTrip3 = 52,    // 16 bits  -> 10.30.2008
            GateTimeStamp = 53,             // 32 bits, readonly  -> 12.22.2008
            StatusSCMDUnknown = 54,         // 1bit, readonly     -> 11.13.2009
            StatusFCMDUnknown = 55,         // 1bit, readonly     -> 11.13.2009
            StatusRXLock = 56,              // 1bit, readonly     -> 11.13.2009
            StatusTXSyncLock = 57           // 1bit, readonly     -> 11.13.2009
        }
        #endregion

        #region Define Default Logical Values
        private const UInt32 TimerDefaultValue = 12;
        private const UInt32 GateStartDefaultValue = 65488;
        private const UInt32 GateLengthDefaultValue = 1024;
        private const UInt32 TripPowerOffDefaultValue = 0x3F;
        private const UInt32 InjectCountDefaultValue = 0;
        private const UInt32 InjectEnableDefaultValue = 0;
        private const UInt32 InjectRangeDefaultValue = 0;
        private const UInt32 InjectPhaseDefaultValue = 1;   //valid inputs are 1,2,4,8
        private const UInt32 InjectDACValueDefaultValue = 0;
        private const UInt32 InjectDACModeDefaultValue = 0;
        private const UInt32 InjectDACDoneDefaultValue = 0;
        private const UInt32 InjectDACStartDefaultValue = 0;
        private const UInt32 HVEnabledDefaultValue = 0;
        private const UInt32 HVTargetDefaultValue = 32768;
        private const UInt32 HVActualDefaultValue = 0;
        private const UInt32 HVControlDefaultValue = 0;
        private const UInt32 HVManualDefaultValue = 0;
        private const UInt32 PhaseStartDefaultValue = 0;
        private const UInt32 PhaseIncrementDefaultValue = 0;
        private const UInt32 PhaseCountDefaultValue = 0;
        private const UInt32 DCM1LockDefaultValue = 0;
        private const UInt32 DCM2LockDefaultValue = 0;
        private const UInt32 DCM1NoClockDefaultValue = 0;
        private const UInt32 DCM2NoClockDefaultValue = 0;
        private const UInt32 DCM2PhaseDoneDefaultValue = 0;
        private const UInt32 DCM2PhaseTotalDefaultValue = 0;
        private const UInt32 TestPulse2BitDefaultValue = 0;
        private const UInt32 TestPulseCountDefaultValue = 0;
        private const UInt32 BoardIDDefaultValue = 0;
        private const UInt32 FirmwareVersionDefaultValue = 0;
        private const UInt32 HVNumAveDefaultValue = 0;
        private const UInt32 HVPeriodAutoDefaultValue = 0;
        private const UInt32 HVPeriodManualDefaultValue = 0;
        private const UInt32 HVPulseWidthDefaultValue = 0;
        private const UInt32 TemperatureDefaultValue = 0;
        private const UInt32 TripXThresholdDefaultValue = 0;
        private const UInt32 TripXComparatorsDefaultValue = 0;
        private const UInt32 ExtTriggFoundDefaultValue = 0; // 08.08.2008
        private const UInt32 ExtTriggRearmDefaultValue = 0; // 08.08.2008
        private const UInt32 DiscrimEnableMaskTrip0DefaultValue = 0xFFFF;   // 10.30.2008
        private const UInt32 DiscrimEnableMaskTrip1DefaultValue = 0xFFFF;   // 10.30.2008
        private const UInt32 DiscrimEnableMaskTrip2DefaultValue = 0xFFFF;   // 10.30.2008
        private const UInt32 DiscrimEnableMaskTrip3DefaultValue = 0xFFFF;   // 10.30.2008
        private const UInt32 GateTimeStampDefaultValue = 0;                 // 12.22.2008
        private const UInt32 StatusSCMDUnknownDefaultValue = 0;             // 11.13.2009
        private const UInt32 StatusFCMDUnknownDefaultValue = 0;             // 11.13.2009
        private const UInt32 StatusRXLockDefaultValue = 0;                  // 11.13.2009
        private const UInt32 StatusTXSyncLockDefaultValue = 0;              // 11.13.2009
        #endregion 
        
        #region Define Control-type members (TextBox, ComboBox and Label)
        private TextBox txt_LWRTimer = new TextBox(); private Label lbl_Timer = new Label();
        private TextBox txt_LWRGateStart = new TextBox(); private Label lbl_GateStart = new Label();
        private TextBox txt_LWRGateLength = new TextBox(); private Label lbl_GateLength = new Label();
        private TextBox txt_LWRTripXPowerDown = new TextBox(); private Label lbl_TripXPowerDown = new Label();
        private CheckBox chk_LWRTrip0InjectCntEnable = new CheckBox(); private Label lbl_Trip0InjectCnt = new Label();
        private TextBox txt_LWRTrip0InjectCnt = new TextBox();
        private CheckBox chk_LWRTrip1InjectCntEnable = new CheckBox(); private Label lbl_Trip1InjectCnt = new Label();
        private TextBox txt_LWRTrip1InjectCnt = new TextBox();
        private CheckBox chk_LWRTrip2InjectCntEnable = new CheckBox(); private Label lbl_Trip2InjectCnt = new Label();
        private TextBox txt_LWRTrip2InjectCnt = new TextBox();
        private CheckBox chk_LWRTrip3InjectCntEnable = new CheckBox(); private Label lbl_Trip3InjectCnt = new Label();
        private TextBox txt_LWRTrip3InjectCnt = new TextBox();
        private CheckBox chk_LWRTrip4InjectCntEnable = new CheckBox(); private Label lbl_Trip4InjectCnt = new Label();
        private TextBox txt_LWRTrip4InjectCnt = new TextBox();
        private CheckBox chk_LWRTrip5InjectCntEnable = new CheckBox(); private Label lbl_Trip5InjectCnt = new Label();
        private TextBox txt_LWRTrip5InjectCnt = new TextBox();
        private TextBox txt_LWRTripXInjectCntRange = new TextBox(); private Label lbl_TripXInjectCntRange = new Label();
        private ComboBox cmb_LWRTripXInjectCntPhase = new ComboBox(); private Label lbl_TripXInjectCntPhase = new Label();
        private TextBox txt_LWRTripXInjDACVal = new TextBox(); private Label lbl_TripXInjDACVal = new Label();
        private ComboBox cmb_LWRTripXInjDACMode = new ComboBox(); private Label lbl_TripXInjDACMode = new Label();
        private ComboBox cmb_LWRTripXInjDACStartClearn = new ComboBox(); private Label lbl_TripXInjDACStartClearn = new Label();
        private TextBox txt_LRTripXInjDACDone = new TextBox(); private Label lbl_TripXInjDACDone = new Label();
        private ComboBox cmb_LWRHVEnable = new ComboBox(); private Label lbl_HVEnable = new Label();
        private TextBox txt_LWRHVTarget = new TextBox(); private Label lbl_HVTarget = new Label();
        private TextBox txt_LRHVActual = new TextBox(); private Label lbl_HVActual = new Label();
        private TextBox txt_LRHVControl = new TextBox(); private Label lbl_HVControl = new Label();
        private ComboBox cmb_LWRHVAutoMan = new ComboBox(); private Label lbl_HVAutoMan = new Label();
        private ComboBox cmb_LWRPHShiftStartClearn = new ComboBox(); private Label lbl_PHShiftStartClearn = new Label();
        private ComboBox cmb_LWRPHShiftDecr0Incr1 = new ComboBox(); private Label lbl_PHShiftDecr0Incr1 = new Label();
        private TextBox txt_LWRPHShiftVal = new TextBox(); private Label lbl_PHShiftVal = new Label();
        private TextBox txt_LRDCM1Locked = new TextBox(); private Label lbl_DCM1Locked = new Label();
        private TextBox txt_LRDCM2Locked = new TextBox(); private Label lbl_DCM2Locked = new Label();
        private TextBox txt_LRDCM1NoClk = new TextBox(); private Label lbl_DCM1NoClk = new Label();
        private TextBox txt_LRDCM2NoClk = new TextBox(); private Label lbl_DCM2NoClk = new Label();
        private TextBox txt_LRDCM2PHShiftDone = new TextBox(); private Label lbl_DCM2PHShiftDone = new Label();
        private TextBox txt_LRDCM2TotalPhaseShift = new TextBox(); private Label lbl_DCM2TotalPhaseShift = new Label();
        private TextBox txt_LRTestPulseCounter2b = new TextBox(); private Label lbl_TestPulseCounter2b = new Label();
        private TextBox txt_LRTestPulseCounter = new TextBox(); private Label lbl_TestPulseCounter = new Label();
        private TextBox txt_LRMyBoardID = new TextBox(); private Label lbl_MyBoardID = new Label();
        private TextBox txt_LRVersion = new TextBox(); private Label lbl_Version = new Label();
        private TextBox txt_LWRHVNumAve = new TextBox(); private Label lbl_HVNumAve = new Label();
        private TextBox txt_LWRHVPeriodMan = new TextBox(); private Label lbl_HVPeriodMan = new Label();
        private TextBox txt_LRHVPeriodAuto = new TextBox(); private Label lbl_HVPeriodAuto = new Label();
        private TextBox txt_LWRHVPulseWidth = new TextBox(); private Label lbl_HVPulseWidth = new Label();
        private TextBox txt_LRTemperature = new TextBox(); private Label lbl_Temperature = new Label();
        private TextBox txt_LWRTripXThreshold = new TextBox(); private Label lbl_TripXThreshold = new Label();
        private TextBox txt_LRTripXComparators = new TextBox(); private Label lbl_TripXComparators = new Label();
        private TextBox txt_LRExtTriggFound = new TextBox(); private Label lbl_ExtTriggFound = new Label(); // 08.08.2008
        private TextBox txt_LWRExtTriggRearm = new TextBox(); private Label lbl_ExtTriggRearm = new Label(); // 08.08.2008
        private TextBox txt_LWRDiscrimEnableMaskTrip0 = new TextBox(); private Label lbl_DiscrimEnableMaskTrip0 = new Label(); // 10.30.2008
        private TextBox txt_LWRDiscrimEnableMaskTrip1 = new TextBox(); private Label lbl_DiscrimEnableMaskTrip1 = new Label(); // 10.30.2008
        private TextBox txt_LWRDiscrimEnableMaskTrip2 = new TextBox(); private Label lbl_DiscrimEnableMaskTrip2 = new Label(); // 10.30.2008
        private TextBox txt_LWRDiscrimEnableMaskTrip3 = new TextBox(); private Label lbl_DiscrimEnableMaskTrip3 = new Label(); // 10.30.2008
        private TextBox txt_LRGateTimeStamp = new TextBox(); private Label lbl_GateTimeStamp = new Label(); // 12.22.2008
        private TextBox txt_LRStatusSCMDUnknown = new TextBox(); private Label lbl_StatusSCMDUnknown = new Label();     // 11.13.2009
        private TextBox txt_LRStatusFCMDUnknown = new TextBox(); private Label lbl_StatusFCMDUnknown = new Label();     // 11.13.2009
        private TextBox txt_LRStatusRXLock = new TextBox(); private Label lbl_StatusRXLock = new Label();               // 11.13.2009
        private TextBox txt_LRStatusTXSyncLock = new TextBox(); private Label lbl_StatusTXSyncLock = new Label();       // 11.13.2009
        #endregion        
        
        public int NRegs
        {
            get { return NLogicalRgisters; }
        }
        public UInt32[] FPGARegValues
        {
            get 
            {
                UpdateFPGALogicalRegArray();
                return FPGALogicalReg; 
            }
            set 
            { 
                value.CopyTo(FPGALogicalReg, 0);
                UpdateFormControls();
            }
        }
        public UInt32 FPGAGetRegValue(UInt32 index)
        {
            UpdateFPGALogicalRegArray();
            return FPGALogicalReg[index];
        }
        public void FPGASetRegValue(UInt32 index, UInt32 value)
        {
            FPGALogicalReg[index] = value;
            UpdateFormControls();
        }

        public FPGADevRegControl()
        {
            InitializeComponent();
            myInitializeComponent();
            ShowAdvancedGUI(isAdvancedGUI);
            FPGALogicalReg[(int)LogicalRegisters.Timer] = TimerDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.GateStart] = GateStartDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.GateLength] = GateLengthDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.TripPowerOff] = TripPowerOffDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectCount0] = InjectCountDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectCount1] = InjectCountDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectCount2] = InjectCountDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectCount3] = InjectCountDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectCount4] = InjectCountDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectCount5] = InjectCountDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectEnable0] = InjectEnableDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectEnable1] = InjectEnableDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectEnable2] = InjectEnableDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectEnable3] = InjectEnableDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectEnable4] = InjectEnableDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectEnable5] = InjectEnableDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectRange] = InjectRangeDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectPhase] = InjectPhaseDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectDACValue] = InjectDACValueDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectDACMode] = InjectDACModeDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectDACStart] = InjectDACStartDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.InjectDACDone] = InjectDACDoneDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.HVEnabled] = HVEnabledDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.HVTarget] = HVTargetDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.HVActual] = HVActualDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.HVControl] = HVControlDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.HVAutoManual] = HVManualDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.PhaseStart] = PhaseStartDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.PhaseIncrement] = PhaseIncrementDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.PhaseTicks] = PhaseCountDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.DCM1Lock] = DCM1LockDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.DCM2Lock] = DCM2LockDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.DCM1NoClock] = DCM1NoClockDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.DCM2NoClock] = DCM2NoClockDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.DCM2PhaseDone] = DCM2PhaseDoneDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.DCM2PhaseTotal] = DCM2PhaseTotalDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.TestPulse2Bit] = TestPulse2BitDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.TestPulseCount] = TestPulseCountDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.BoardID] = BoardIDDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.FirmwareVersion] = FirmwareVersionDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.HVNumAvg] = HVNumAveDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.HVPeriodAuto] = HVPeriodAutoDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.HVPeriodManual] = HVPeriodManualDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.HVPulseWidth] = HVPulseWidthDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.Temperature] = TemperatureDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.TripXThreshold] = TripXThresholdDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.TripXComparators] = TripXComparatorsDefaultValue;
            FPGALogicalReg[(int)LogicalRegisters.ExtTriggFound] = ExtTriggFoundDefaultValue;    // 08.08.2008
            FPGALogicalReg[(int)LogicalRegisters.ExtTriggRearm] = ExtTriggRearmDefaultValue;    // 08.08.2008
            FPGALogicalReg[(int)LogicalRegisters.DiscrimEnableMaskTrip0] = DiscrimEnableMaskTrip0DefaultValue;  // 10.30.2008
            FPGALogicalReg[(int)LogicalRegisters.DiscrimEnableMaskTrip1] = DiscrimEnableMaskTrip1DefaultValue;  // 10.30.2008
            FPGALogicalReg[(int)LogicalRegisters.DiscrimEnableMaskTrip2] = DiscrimEnableMaskTrip2DefaultValue;  // 10.30.2008
            FPGALogicalReg[(int)LogicalRegisters.DiscrimEnableMaskTrip3] = DiscrimEnableMaskTrip3DefaultValue;  // 10.30.2008
            FPGALogicalReg[(int)LogicalRegisters.GateTimeStamp] = GateTimeStampDefaultValue;    // 12.22.2008
            FPGALogicalReg[(int)LogicalRegisters.StatusSCMDUnknown] = StatusSCMDUnknownDefaultValue;    // 11.13.2009
            FPGALogicalReg[(int)LogicalRegisters.StatusFCMDUnknown] = StatusFCMDUnknownDefaultValue;    // 11.13.2009
            FPGALogicalReg[(int)LogicalRegisters.StatusRXLock] = StatusRXLockDefaultValue;              // 11.13.2009
            FPGALogicalReg[(int)LogicalRegisters.StatusTXSyncLock] = StatusTXSyncLockDefaultValue;      // 11.13.2009
        }

        private void myInitializeComponent()
        {
            int Xwidth = 100;
            int Yheight = 15;

            //Create Register_Timer Controls
            lbl_Timer.Width = Xwidth;
            lbl_Timer.Height = Yheight;
            lbl_Timer.Text = "WR Timer";
            lbl_Timer.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_Timer.BackColor = Color.Coral;
            this.Controls.Add(lbl_Timer);
            txt_LWRTimer.Width = Xwidth;
            txt_LWRTimer.Height = Yheight;
            txt_LWRTimer.Enabled = true;
            txt_LWRTimer.BackColor = Color.White;
            txt_LWRTimer.Name = "Timer";
            txt_LWRTimer.Text = TimerDefaultValue.ToString();
            txt_LWRTimer.TabIndex = (int)LogicalRegisters.Timer;
            txt_LWRTimer.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRTimer);

            //Create Register_GateStart Controls
            lbl_GateStart.Width = Xwidth;
            lbl_GateStart.Height = Yheight;
            lbl_GateStart.Text = "WR Gate Start";
            lbl_GateStart.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_GateStart.BackColor = Color.Coral;
            this.Controls.Add(lbl_GateStart);
            txt_LWRGateStart.Width = Xwidth;
            txt_LWRGateStart.Height = Yheight;
            txt_LWRGateStart.Enabled = true;
            txt_LWRGateStart.BackColor = Color.White;
            txt_LWRGateStart.Name = "GateStart";
            txt_LWRGateStart.Text = GateStartDefaultValue.ToString();
            txt_LWRGateStart.TabIndex = (int)LogicalRegisters.GateStart;
            txt_LWRGateStart.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRGateStart);

            //Create Register_GateLength Controls
            lbl_GateLength.Width = Xwidth;
            lbl_GateLength.Height = Yheight;
            lbl_GateLength.Text = "WR Gate Length";
            lbl_GateLength.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_GateLength.BackColor = Color.Coral;
            this.Controls.Add(lbl_GateLength);
            txt_LWRGateLength.Width = Xwidth;
            txt_LWRGateLength.Height = Yheight;
            txt_LWRGateLength.Enabled = true;
            txt_LWRGateLength.BackColor = Color.White;
            txt_LWRGateLength.Name = "GateLength";
            txt_LWRGateLength.Text = GateLengthDefaultValue.ToString();
            txt_LWRGateLength.TabIndex = (int)LogicalRegisters.GateLength;
            txt_LWRGateLength.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRGateLength);

            //Create Register_TripXPowerDown Controls
            lbl_TripXPowerDown.Width = Xwidth;
            lbl_TripXPowerDown.Height = Yheight;
            lbl_TripXPowerDown.Text = "WR Trip PowOFF";
            lbl_TripXPowerDown.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_TripXPowerDown.BackColor = Color.Coral;
            this.Controls.Add(lbl_TripXPowerDown);
            txt_LWRTripXPowerDown.Width = Xwidth;
            txt_LWRTripXPowerDown.Height = Yheight;
            txt_LWRTripXPowerDown.Enabled = true;
            txt_LWRTripXPowerDown.BackColor = Color.White;
            txt_LWRTripXPowerDown.Name = "TripXPowerDown";
            txt_LWRTripXPowerDown.Text = TripPowerOffDefaultValue.ToString();
            txt_LWRTripXPowerDown.TabIndex = (int)LogicalRegisters.TripPowerOff;
            txt_LWRTripXPowerDown.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRTripXPowerDown);

            //Create Register_Trip0InjectCnt Controls
            lbl_Trip0InjectCnt.Width = Xwidth;
            lbl_Trip0InjectCnt.Height = Yheight;
            lbl_Trip0InjectCnt.Text = "WR Trip0 InjCnt+EN";
            lbl_Trip0InjectCnt.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_Trip0InjectCnt.BackColor = Color.Coral;
            this.Controls.Add(lbl_Trip0InjectCnt);
            txt_LWRTrip0InjectCnt.Width = Xwidth;
            txt_LWRTrip0InjectCnt.Height = Yheight;
            txt_LWRTrip0InjectCnt.Enabled = true;
            txt_LWRTrip0InjectCnt.BackColor = Color.White;
            txt_LWRTrip0InjectCnt.Name = "Trip0InjectCnt";
            txt_LWRTrip0InjectCnt.Text = InjectCountDefaultValue.ToString();
            txt_LWRTrip0InjectCnt.TabIndex = (int)LogicalRegisters.InjectCount0;
            txt_LWRTrip0InjectCnt.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRTrip0InjectCnt);
            //chk_LWRTrip0InjectCntEnable.Location = new Point(txt_LWRTrip0InjectCnt.Left + txt_LWRTrip0InjectCnt.Width + 5, txt_LWRTrip0InjectCnt.Top);
            chk_LWRTrip0InjectCntEnable.Width = Xwidth / 5;
            chk_LWRTrip0InjectCntEnable.Checked = Convert.ToBoolean(InjectEnableDefaultValue & 0x1);
            chk_LWRTrip0InjectCntEnable.Name = "Trip0InjectCntEnable";
            chk_LWRTrip0InjectCntEnable.TabIndex = (int)LogicalRegisters.InjectEnable0;
            chk_LWRTrip0InjectCntEnable.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(chk_LWRTrip0InjectCntEnable);

            //Create Register_Trip1InjectCnt Controls
            lbl_Trip1InjectCnt.Width = Xwidth;
            lbl_Trip1InjectCnt.Height = Yheight;
            lbl_Trip1InjectCnt.Text = "WR Trip1 InjCnt+EN";
            lbl_Trip1InjectCnt.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_Trip1InjectCnt.BackColor = Color.Coral;
            this.Controls.Add(lbl_Trip1InjectCnt);
            txt_LWRTrip1InjectCnt.Width = Xwidth;
            txt_LWRTrip1InjectCnt.Height = Yheight;
            txt_LWRTrip1InjectCnt.Enabled = true;
            txt_LWRTrip1InjectCnt.BackColor = Color.White;
            txt_LWRTrip1InjectCnt.Name = "Trip1InjectCnt";
            txt_LWRTrip1InjectCnt.Text = InjectCountDefaultValue.ToString();
            txt_LWRTrip1InjectCnt.TabIndex = (int)LogicalRegisters.InjectCount1;
            txt_LWRTrip1InjectCnt.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRTrip1InjectCnt);
            chk_LWRTrip1InjectCntEnable.Width = Xwidth / 5;
            chk_LWRTrip1InjectCntEnable.Checked = Convert.ToBoolean(InjectEnableDefaultValue & 0x2);
            chk_LWRTrip1InjectCntEnable.Name = "Trip1InjectCntEnable";
            chk_LWRTrip1InjectCntEnable.TabIndex = (int)LogicalRegisters.InjectEnable1;
            chk_LWRTrip1InjectCntEnable.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(chk_LWRTrip1InjectCntEnable);

            //Create Register_Trip2InjectCnt Controls
            lbl_Trip2InjectCnt.Width = Xwidth;
            lbl_Trip2InjectCnt.Height = Yheight;
            lbl_Trip2InjectCnt.Text = "WR Trip2 InjCnt+EN";
            lbl_Trip2InjectCnt.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_Trip2InjectCnt.BackColor = Color.Coral;
            this.Controls.Add(lbl_Trip2InjectCnt);
            txt_LWRTrip2InjectCnt.Width = Xwidth;
            txt_LWRTrip2InjectCnt.Height = Yheight;
            txt_LWRTrip2InjectCnt.Enabled = true;
            txt_LWRTrip2InjectCnt.BackColor = Color.White;
            txt_LWRTrip2InjectCnt.Name = "Trip2InjectCnt";
            txt_LWRTrip2InjectCnt.Text = InjectCountDefaultValue.ToString();
            txt_LWRTrip2InjectCnt.TabIndex = (int)LogicalRegisters.InjectCount2;
            txt_LWRTrip2InjectCnt.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRTrip2InjectCnt);
            chk_LWRTrip2InjectCntEnable.Width = Xwidth / 5;
            chk_LWRTrip2InjectCntEnable.Checked = Convert.ToBoolean(InjectEnableDefaultValue & 0x4);
            chk_LWRTrip2InjectCntEnable.Name = "Trip2InjectCntEnable";
            chk_LWRTrip2InjectCntEnable.TabIndex = (int)LogicalRegisters.InjectEnable2;
            chk_LWRTrip2InjectCntEnable.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(chk_LWRTrip2InjectCntEnable);

            //Create Register_Trip3InjectCnt Controls
            lbl_Trip3InjectCnt.Width = Xwidth;
            lbl_Trip3InjectCnt.Height = Yheight;
            lbl_Trip3InjectCnt.Text = "WR Trip3 InjCnt+EN";
            lbl_Trip3InjectCnt.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_Trip3InjectCnt.BackColor = Color.Coral;
            this.Controls.Add(lbl_Trip3InjectCnt);
            txt_LWRTrip3InjectCnt.Width = Xwidth;
            txt_LWRTrip3InjectCnt.Height = Yheight;
            txt_LWRTrip3InjectCnt.Enabled = true;
            txt_LWRTrip3InjectCnt.BackColor = Color.White;
            txt_LWRTrip3InjectCnt.Name = "Trip3InjectCnt";
            txt_LWRTrip3InjectCnt.Text = InjectCountDefaultValue.ToString();
            txt_LWRTrip3InjectCnt.TabIndex = (int)LogicalRegisters.InjectCount3;
            txt_LWRTrip3InjectCnt.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRTrip3InjectCnt);
            chk_LWRTrip3InjectCntEnable.Width = Xwidth / 5;
            chk_LWRTrip3InjectCntEnable.Checked = Convert.ToBoolean(InjectEnableDefaultValue & 0x8);
            chk_LWRTrip3InjectCntEnable.Name = "Trip3InjectCntEnable";
            chk_LWRTrip3InjectCntEnable.TabIndex = (int)LogicalRegisters.InjectEnable3;
            chk_LWRTrip3InjectCntEnable.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(chk_LWRTrip3InjectCntEnable);

            //Create Register_Trip4InjectCnt Controls
            lbl_Trip4InjectCnt.Width = Xwidth;
            lbl_Trip4InjectCnt.Height = Yheight;
            lbl_Trip4InjectCnt.Text = "WR Trip4 InjCnt+EN";
            lbl_Trip4InjectCnt.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_Trip4InjectCnt.BackColor = Color.Coral;
            this.Controls.Add(lbl_Trip4InjectCnt);
            txt_LWRTrip4InjectCnt.Width = Xwidth;
            txt_LWRTrip4InjectCnt.Height = Yheight;
            txt_LWRTrip4InjectCnt.Enabled = true;
            txt_LWRTrip4InjectCnt.BackColor = Color.White;
            txt_LWRTrip4InjectCnt.Name = "Trip4InjectCnt";
            txt_LWRTrip4InjectCnt.Text = InjectCountDefaultValue.ToString();
            txt_LWRTrip4InjectCnt.TabIndex = (int)LogicalRegisters.InjectCount4;
            txt_LWRTrip4InjectCnt.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRTrip4InjectCnt);
            chk_LWRTrip4InjectCntEnable.Width = Xwidth / 5;
            chk_LWRTrip4InjectCntEnable.Checked = Convert.ToBoolean(InjectEnableDefaultValue & 0x10);
            chk_LWRTrip4InjectCntEnable.Name = "Trip4InjectCntEnable";
            chk_LWRTrip4InjectCntEnable.TabIndex = (int)LogicalRegisters.InjectEnable4;
            chk_LWRTrip4InjectCntEnable.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(chk_LWRTrip4InjectCntEnable);

            //Create Register_Trip5InjectCnt Controls
            lbl_Trip5InjectCnt.Width = Xwidth;
            lbl_Trip5InjectCnt.Height = Yheight;
            lbl_Trip5InjectCnt.Text = "WR Trip5 InjCnt+EN";
            lbl_Trip5InjectCnt.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_Trip5InjectCnt.BackColor = Color.Coral;
            this.Controls.Add(lbl_Trip5InjectCnt);
            txt_LWRTrip5InjectCnt.Width = Xwidth;
            txt_LWRTrip5InjectCnt.Height = Yheight;
            txt_LWRTrip5InjectCnt.Enabled = true;
            txt_LWRTrip5InjectCnt.BackColor = Color.White;
            txt_LWRTrip5InjectCnt.Name = "Trip5InjectCnt";
            txt_LWRTrip5InjectCnt.Text = InjectCountDefaultValue.ToString();
            txt_LWRTrip5InjectCnt.TabIndex = (int)LogicalRegisters.InjectCount5;
            txt_LWRTrip5InjectCnt.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRTrip5InjectCnt);
            chk_LWRTrip5InjectCntEnable.Width = Xwidth / 5;
            chk_LWRTrip5InjectCntEnable.Checked = Convert.ToBoolean(InjectEnableDefaultValue & 0x20);
            chk_LWRTrip5InjectCntEnable.Name = "Trip5InjectCntEnable";
            chk_LWRTrip5InjectCntEnable.TabIndex = (int)LogicalRegisters.InjectEnable5;
            chk_LWRTrip5InjectCntEnable.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(chk_LWRTrip5InjectCntEnable);

            //Create Register_TripXInjectCntRange Controls
            lbl_TripXInjectCntRange.Width = Xwidth;
            lbl_TripXInjectCntRange.Height = Yheight;
            lbl_TripXInjectCntRange.Text = "WR TripX InjRange";
            lbl_TripXInjectCntRange.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_TripXInjectCntRange.BackColor = Color.Coral;
            this.Controls.Add(lbl_TripXInjectCntRange);
            txt_LWRTripXInjectCntRange.Width = Xwidth;
            txt_LWRTripXInjectCntRange.Height = Yheight;
            txt_LWRTripXInjectCntRange.Enabled = true;
            txt_LWRTripXInjectCntRange.BackColor = Color.White;
            txt_LWRTripXInjectCntRange.Name = "TripXInjectCntRange";
            txt_LWRTripXInjectCntRange.Text = InjectRangeDefaultValue.ToString();
            txt_LWRTripXInjectCntRange.TabIndex = (int)LogicalRegisters.InjectRange;
            txt_LWRTripXInjectCntRange.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRTripXInjectCntRange);

            //Create Register_TripXInjectCntPhase Controls
            lbl_TripXInjectCntPhase.Width = Xwidth;
            lbl_TripXInjectCntPhase.Height = Yheight;
            lbl_TripXInjectCntPhase.Text = "WR TripX InjPhase";
            lbl_TripXInjectCntPhase.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_TripXInjectCntPhase.BackColor = Color.Coral;
            this.Controls.Add(lbl_TripXInjectCntPhase);
            cmb_LWRTripXInjectCntPhase.Width = Xwidth;
            cmb_LWRTripXInjectCntPhase.Height = Yheight;
            cmb_LWRTripXInjectCntPhase.Items.Clear();
            cmb_LWRTripXInjectCntPhase.Items.Add("1 Sync CLK0");
            cmb_LWRTripXInjectCntPhase.Items.Add("2 Sync CLK90");
            cmb_LWRTripXInjectCntPhase.Items.Add("4 Sync CLK180");
            cmb_LWRTripXInjectCntPhase.Items.Add("8 Sync CLK270");
            cmb_LWRTripXInjectCntPhase.Items.Add("...Sync Error");
            cmb_LWRTripXInjectCntPhase.Name = "TripXInjectCntPhase";
            cmb_LWRTripXInjectCntPhase.SelectedIndex = 0;   //valid inputs are 1,2,4,8
            cmb_LWRTripXInjectCntPhase.TabIndex = (int)LogicalRegisters.InjectPhase;
            cmb_LWRTripXInjectCntPhase.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(cmb_LWRTripXInjectCntPhase);

            //Create Register_TripXInjDACVal Controls
            lbl_TripXInjDACVal.Width = Xwidth;
            lbl_TripXInjDACVal.Height = Yheight;
            lbl_TripXInjDACVal.Text = "WR InjDAC Value";
            lbl_TripXInjDACVal.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_TripXInjDACVal.BackColor = Color.Coral;
            this.Controls.Add(lbl_TripXInjDACVal);
            txt_LWRTripXInjDACVal.Width = Xwidth;
            txt_LWRTripXInjDACVal.Height = Yheight;
            txt_LWRTripXInjDACVal.Enabled = true;
            txt_LWRTripXInjDACVal.BackColor = Color.White;
            txt_LWRTripXInjDACVal.Name = "TripXInjDACVal";
            txt_LWRTripXInjDACVal.Text = InjectDACValueDefaultValue.ToString();
            txt_LWRTripXInjDACVal.TabIndex = (int)LogicalRegisters.InjectDACValue;
            txt_LWRTripXInjDACVal.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRTripXInjDACVal);

            //Create Register_TripXInjDACMode Controls
            lbl_TripXInjDACMode.Width = Xwidth;
            lbl_TripXInjDACMode.Height = Yheight;
            lbl_TripXInjDACMode.Text = "WR InjDAC Mode";
            lbl_TripXInjDACMode.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_TripXInjDACMode.BackColor = Color.Coral;
            this.Controls.Add(lbl_TripXInjDACMode);
            cmb_LWRTripXInjDACMode.Width = Xwidth;
            cmb_LWRTripXInjDACMode.Height = Yheight;
            cmb_LWRTripXInjDACMode.Items.Add("0 Normal");
            cmb_LWRTripXInjDACMode.Items.Add("1 PD 1K");
            cmb_LWRTripXInjDACMode.Items.Add("2 PD 100K");
            cmb_LWRTripXInjDACMode.Items.Add("3 PD Hi-Z");
            cmb_LWRTripXInjDACMode.Name = "TripXInjDACMode";
            cmb_LWRTripXInjDACMode.SelectedIndex = (int)InjectDACModeDefaultValue;
            cmb_LWRTripXInjDACMode.TabIndex = (int)LogicalRegisters.InjectDACMode;
            cmb_LWRTripXInjDACMode.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(cmb_LWRTripXInjDACMode);

            //Create Register_TripXInjDACStartClearn Controls
            lbl_TripXInjDACStartClearn.Width = Xwidth;
            lbl_TripXInjDACStartClearn.Height = Yheight;
            lbl_TripXInjDACStartClearn.Text = "WR InjDAC RS";
            lbl_TripXInjDACStartClearn.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_TripXInjDACStartClearn.BackColor = Color.Coral;
            this.Controls.Add(lbl_TripXInjDACStartClearn);
            cmb_LWRTripXInjDACStartClearn.Width = Xwidth;
            cmb_LWRTripXInjDACStartClearn.Height = Yheight;
            cmb_LWRTripXInjDACStartClearn.Items.Add("0 Reset");
            cmb_LWRTripXInjDACStartClearn.Items.Add("1 Start");
            cmb_LWRTripXInjDACStartClearn.Name = "TripXInjDACStartClearn";
            cmb_LWRTripXInjDACStartClearn.SelectedIndex = (int)InjectDACStartDefaultValue;
            cmb_LWRTripXInjDACStartClearn.TabIndex = (int)LogicalRegisters.InjectDACStart;
            cmb_LWRTripXInjDACStartClearn.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(cmb_LWRTripXInjDACStartClearn);

            //Create Register_TripXInjDACDone Controls
            lbl_TripXInjDACDone.Width = Xwidth;
            lbl_TripXInjDACDone.Height = Yheight;
            lbl_TripXInjDACDone.Text = "R  InjDAC Done";
            lbl_TripXInjDACDone.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_TripXInjDACDone.BackColor = Color.Coral;
            this.Controls.Add(lbl_TripXInjDACDone);
            txt_LRTripXInjDACDone.Width = Xwidth;
            txt_LRTripXInjDACDone.Height = Yheight;
            txt_LRTripXInjDACDone.Enabled = true;
            txt_LRTripXInjDACDone.BackColor = Color.White;
            txt_LRTripXInjDACDone.Name = "TripXInjDACDone";
            txt_LRTripXInjDACDone.Text = InjectDACDoneDefaultValue.ToString();
            txt_LRTripXInjDACDone.TabIndex = (int)LogicalRegisters.InjectDACDone;
            txt_LRTripXInjDACDone.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRTripXInjDACDone);

            //Create Register_HVAvgOn Controls
            lbl_HVEnable.Width = Xwidth;
            lbl_HVEnable.Height = Yheight;
            lbl_HVEnable.Text = "WR HV Enable";
            lbl_HVEnable.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_HVEnable.BackColor = Color.Coral;
            this.Controls.Add(lbl_HVEnable);
            cmb_LWRHVEnable.Width = Xwidth;
            cmb_LWRHVEnable.Height = Yheight;
            cmb_LWRHVEnable.Items.Add("0 HV Off");
            cmb_LWRHVEnable.Items.Add("1 HV On");
            cmb_LWRHVEnable.Name = "WR HV Enable";
            cmb_LWRHVEnable.SelectedIndex = (int)HVEnabledDefaultValue;
            cmb_LWRHVEnable.TabIndex = (int)LogicalRegisters.HVEnabled;
            cmb_LWRHVEnable.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(cmb_LWRHVEnable);

            //Create Register_HVWriteData Controls
            lbl_HVTarget.Width = Xwidth;
            lbl_HVTarget.Height = Yheight;
            lbl_HVTarget.Text = "WR HV Target";
            lbl_HVTarget.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_HVTarget.BackColor = Color.Coral;
            this.Controls.Add(lbl_HVTarget);
            txt_LWRHVTarget.Width = Xwidth;
            txt_LWRHVTarget.Height = Yheight;
            txt_LWRHVTarget.Enabled = true;
            txt_LWRHVTarget.BackColor = Color.White;
            txt_LWRHVTarget.Name = "HVTarget";
            txt_LWRHVTarget.Text = HVTargetDefaultValue.ToString();
            txt_LWRHVTarget.TabIndex = (int)LogicalRegisters.HVTarget;
            txt_LWRHVTarget.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRHVTarget);

            //Create Register_HVReadData Controls
            lbl_HVActual.Width = Xwidth;
            lbl_HVActual.Height = Yheight;
            lbl_HVActual.Text = "R  HV Actual";
            lbl_HVActual.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_HVActual.BackColor = Color.Coral;
            this.Controls.Add(lbl_HVActual);
            txt_LRHVActual.Width = Xwidth;
            txt_LRHVActual.Height = Yheight;
            txt_LRHVActual.Enabled = true;
            txt_LRHVActual.BackColor = Color.White;
            txt_LRHVActual.Name = "HVActual";
            txt_LRHVActual.Text = HVActualDefaultValue.ToString();
            txt_LRHVActual.TabIndex = (int)LogicalRegisters.HVActual;
            txt_LRHVActual.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRHVActual);

            //Create Register_HVReadDummy Controls
            lbl_HVControl.Width = Xwidth;
            lbl_HVControl.Height = Yheight;
            lbl_HVControl.Text = "R  HV Control";
            lbl_HVControl.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_HVControl.BackColor = Color.Coral;
            this.Controls.Add(lbl_HVControl);
            txt_LRHVControl.Width = Xwidth;
            txt_LRHVControl.Height = Yheight;
            txt_LRHVControl.Enabled = true;
            txt_LRHVControl.BackColor = Color.White;
            txt_LRHVControl.Name = "HVControl";
            txt_LRHVControl.Text = HVControlDefaultValue.ToString();
            txt_LRHVControl.TabIndex = (int)LogicalRegisters.HVControl;
            txt_LRHVControl.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRHVControl);

            //Create Register_HVLoopOff Controls
            lbl_HVAutoMan.Width = Xwidth;
            lbl_HVAutoMan.Height = Yheight;
            lbl_HVAutoMan.Text = "WR HV Auto/Man";
            lbl_HVAutoMan.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_HVAutoMan.BackColor = Color.Coral;
            this.Controls.Add(lbl_HVAutoMan);
            cmb_LWRHVAutoMan.Width = Xwidth;
            cmb_LWRHVAutoMan.Height = Yheight;
            cmb_LWRHVAutoMan.Items.Add("0 Auto");
            cmb_LWRHVAutoMan.Items.Add("1 Manual");
            cmb_LWRHVAutoMan.Name = "HVAuto0Manual1";
            cmb_LWRHVAutoMan.SelectedIndex = (int)HVManualDefaultValue;
            cmb_LWRHVAutoMan.TabIndex = (int)LogicalRegisters.HVAutoManual;
            cmb_LWRHVAutoMan.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(cmb_LWRHVAutoMan);

            //Create Register_PHShifStartClearn Controls
            lbl_PHShiftStartClearn.Width = Xwidth;
            lbl_PHShiftStartClearn.Height = Yheight;
            lbl_PHShiftStartClearn.Text = "WR PHASE RS";
            lbl_PHShiftStartClearn.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_PHShiftStartClearn.BackColor = Color.Coral;
            this.Controls.Add(lbl_PHShiftStartClearn);
            cmb_LWRPHShiftStartClearn.Width = Xwidth;
            cmb_LWRPHShiftStartClearn.Height = Yheight;
            cmb_LWRPHShiftStartClearn.Items.Add("0 Reset");
            cmb_LWRPHShiftStartClearn.Items.Add("1 Start");
            cmb_LWRPHShiftStartClearn.Name = "PHShiftStartClearn";
            cmb_LWRPHShiftStartClearn.SelectedIndex = (int)PhaseStartDefaultValue;
            cmb_LWRPHShiftStartClearn.TabIndex = (int)LogicalRegisters.PhaseStart;
            cmb_LWRPHShiftStartClearn.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(cmb_LWRPHShiftStartClearn);

            //Create Register_PHShiftDecr0Incr1 Controls
            lbl_PHShiftDecr0Incr1.Width = Xwidth;
            lbl_PHShiftDecr0Incr1.Height = Yheight;
            lbl_PHShiftDecr0Incr1.Text = "WR PHASE +/-";
            lbl_PHShiftDecr0Incr1.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_PHShiftDecr0Incr1.BackColor = Color.Coral;
            this.Controls.Add(lbl_PHShiftDecr0Incr1);
            cmb_LWRPHShiftDecr0Incr1.Width = Xwidth;
            cmb_LWRPHShiftDecr0Incr1.Height = Yheight;
            cmb_LWRPHShiftDecr0Incr1.Items.Add("0 Decrement");
            cmb_LWRPHShiftDecr0Incr1.Items.Add("1 Increment");
            cmb_LWRPHShiftDecr0Incr1.Name = "PHShiftDecr0Incr1";
            cmb_LWRPHShiftDecr0Incr1.SelectedIndex = (int)PhaseIncrementDefaultValue;
            cmb_LWRPHShiftDecr0Incr1.TabIndex = (int)LogicalRegisters.PhaseIncrement;
            cmb_LWRPHShiftDecr0Incr1.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(cmb_LWRPHShiftDecr0Incr1);

            //Create Register_PHShiftVal Controls
            lbl_PHShiftVal.Width = Xwidth;
            lbl_PHShiftVal.Height = Yheight;
            lbl_PHShiftVal.Text = "WR PHASE Ticks";
            lbl_PHShiftVal.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_PHShiftVal.BackColor = Color.Coral;
            this.Controls.Add(lbl_PHShiftVal);
            txt_LWRPHShiftVal.Width = Xwidth;
            txt_LWRPHShiftVal.Height = Yheight;
            txt_LWRPHShiftVal.Enabled = true;
            txt_LWRPHShiftVal.BackColor = Color.White;
            txt_LWRPHShiftVal.Name = "PHShiftVal";
            txt_LWRPHShiftVal.Text = PhaseCountDefaultValue.ToString();
            txt_LWRPHShiftVal.TabIndex = (int)LogicalRegisters.PhaseTicks;
            txt_LWRPHShiftVal.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRPHShiftVal);

            //Create Register_DCM1Locked Controls
            lbl_DCM1Locked.Width = Xwidth;
            lbl_DCM1Locked.Height = Yheight;
            lbl_DCM1Locked.Text = "R  DCM1 LOCK";
            lbl_DCM1Locked.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_DCM1Locked.BackColor = Color.Coral;
            this.Controls.Add(lbl_DCM1Locked);
            txt_LRDCM1Locked.Width = Xwidth;
            txt_LRDCM1Locked.Height = Yheight;
            txt_LRDCM1Locked.Enabled = true;
            txt_LRDCM1Locked.BackColor = Color.White;
            txt_LRDCM1Locked.Name = "DCM1Locked";
            txt_LRDCM1Locked.Text = DCM1LockDefaultValue.ToString();
            txt_LRDCM1Locked.TabIndex = (int)LogicalRegisters.DCM1Lock;
            txt_LRDCM1Locked.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRDCM1Locked);

            //Create Register_DCM2Locked Controls
            lbl_DCM2Locked.Width = Xwidth;
            lbl_DCM2Locked.Height = Yheight;
            lbl_DCM2Locked.Text = "R  DCM2 LOCK";
            lbl_DCM2Locked.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_DCM2Locked.BackColor = Color.Coral;
            this.Controls.Add(lbl_DCM2Locked);
            txt_LRDCM2Locked.Width = Xwidth;
            txt_LRDCM2Locked.Height = Yheight;
            txt_LRDCM2Locked.Enabled = true;
            txt_LRDCM2Locked.BackColor = Color.White;
            txt_LRDCM2Locked.Name = "DCM2Locked";
            txt_LRDCM2Locked.Text = DCM2LockDefaultValue.ToString();
            txt_LRDCM2Locked.TabIndex = (int)LogicalRegisters.DCM2Lock;
            txt_LRDCM2Locked.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRDCM2Locked);

            //Create Register_DCM1NoClk Controls
            lbl_DCM1NoClk.Width = Xwidth;
            lbl_DCM1NoClk.Height = Yheight;
            lbl_DCM1NoClk.Text = "R  DCM1 NoCLK";
            lbl_DCM1NoClk.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_DCM1NoClk.BackColor = Color.Coral;
            this.Controls.Add(lbl_DCM1NoClk);
            txt_LRDCM1NoClk.Width = Xwidth;
            txt_LRDCM1NoClk.Height = Yheight;
            txt_LRDCM1NoClk.Enabled = true;
            txt_LRDCM1NoClk.BackColor = Color.White;
            txt_LRDCM1NoClk.Name = "DCM1NoClk";
            txt_LRDCM1NoClk.Text = DCM1NoClockDefaultValue.ToString();
            txt_LRDCM1NoClk.TabIndex = (int)LogicalRegisters.DCM1NoClock;
            txt_LRDCM1NoClk.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRDCM1NoClk);

            //Create Register_DCM2NoClk Controls
            lbl_DCM2NoClk.Width = Xwidth;
            lbl_DCM2NoClk.Height = Yheight;
            lbl_DCM2NoClk.Text = "R  DCM2 NoCLK";
            lbl_DCM2NoClk.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_DCM2NoClk.BackColor = Color.Coral;
            this.Controls.Add(lbl_DCM2NoClk);
            txt_LRDCM2NoClk.Width = Xwidth;
            txt_LRDCM2NoClk.Height = Yheight;
            txt_LRDCM2NoClk.Enabled = true;
            txt_LRDCM2NoClk.BackColor = Color.White;
            txt_LRDCM2NoClk.Name = "DCM2NoClk";
            txt_LRDCM2NoClk.Text = DCM2NoClockDefaultValue.ToString();
            txt_LRDCM2NoClk.TabIndex = (int)LogicalRegisters.DCM2NoClock;
            txt_LRDCM2NoClk.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRDCM2NoClk);

            //Create Register_DCM2PHShiftDone Controls
            lbl_DCM2PHShiftDone.Width = Xwidth;
            lbl_DCM2PHShiftDone.Height = Yheight;
            lbl_DCM2PHShiftDone.Text = "R  DCM2 PHDone";
            lbl_DCM2PHShiftDone.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_DCM2PHShiftDone.BackColor = Color.Coral;
            this.Controls.Add(lbl_DCM2PHShiftDone);
            txt_LRDCM2PHShiftDone.Width = Xwidth;
            txt_LRDCM2PHShiftDone.Height = Yheight;
            txt_LRDCM2PHShiftDone.Enabled = true;
            txt_LRDCM2PHShiftDone.BackColor = Color.White;
            txt_LRDCM2PHShiftDone.Name = "DCM2PHShiftDone";
            txt_LRDCM2PHShiftDone.Text = DCM2PhaseDoneDefaultValue.ToString();
            txt_LRDCM2PHShiftDone.TabIndex = (int)LogicalRegisters.DCM2PhaseDone;
            txt_LRDCM2PHShiftDone.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRDCM2PHShiftDone);

            //Create Register_DCM2TotalPhaseShift Controls
            lbl_DCM2TotalPhaseShift.Width = Xwidth;
            lbl_DCM2TotalPhaseShift.Height = Yheight;
            lbl_DCM2TotalPhaseShift.Text = "R  DCM2 PHTotal";
            lbl_DCM2TotalPhaseShift.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_DCM2TotalPhaseShift.BackColor = Color.Coral;
            this.Controls.Add(lbl_DCM2TotalPhaseShift);
            txt_LRDCM2TotalPhaseShift.Width = Xwidth;
            txt_LRDCM2TotalPhaseShift.Height = Yheight;
            txt_LRDCM2TotalPhaseShift.Enabled = true;
            txt_LRDCM2TotalPhaseShift.BackColor = Color.White;
            txt_LRDCM2TotalPhaseShift.Name = "DCM2TotalPhaseShift";
            txt_LRDCM2TotalPhaseShift.Text = DCM2PhaseTotalDefaultValue.ToString();
            txt_LRDCM2TotalPhaseShift.TabIndex = (int)LogicalRegisters.DCM2PhaseTotal;
            txt_LRDCM2TotalPhaseShift.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRDCM2TotalPhaseShift);

            //Create Register_TestPulseCounter2b Controls
            lbl_TestPulseCounter2b.Width = Xwidth;
            lbl_TestPulseCounter2b.Height = Yheight;
            lbl_TestPulseCounter2b.Text = "R  TP Count2b";
            lbl_TestPulseCounter2b.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_TestPulseCounter2b.BackColor = Color.Coral;
            this.Controls.Add(lbl_TestPulseCounter2b);
            txt_LRTestPulseCounter2b.Width = Xwidth;
            txt_LRTestPulseCounter2b.Height = Yheight;
            txt_LRTestPulseCounter2b.Enabled = true;
            txt_LRTestPulseCounter2b.BackColor = Color.White;
            txt_LRTestPulseCounter2b.Name = "TestPulseCounter2b";
            txt_LRTestPulseCounter2b.Text = TestPulse2BitDefaultValue.ToString();
            txt_LRTestPulseCounter2b.TabIndex = (int)LogicalRegisters.TestPulse2Bit;
            txt_LRTestPulseCounter2b.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRTestPulseCounter2b);

            //Create Register_TestPulseCounter Controls
            lbl_TestPulseCounter.Width = Xwidth;
            lbl_TestPulseCounter.Height = Yheight;
            lbl_TestPulseCounter.Text = "R  TP Count";
            lbl_TestPulseCounter.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_TestPulseCounter.BackColor = Color.Coral;
            this.Controls.Add(lbl_TestPulseCounter);
            txt_LRTestPulseCounter.Width = Xwidth;
            txt_LRTestPulseCounter.Height = Yheight;
            txt_LRTestPulseCounter.Enabled = true;
            txt_LRTestPulseCounter.BackColor = Color.White;
            txt_LRTestPulseCounter.Name = "TestPulseCounter";
            txt_LRTestPulseCounter.Text = TestPulseCountDefaultValue.ToString();
            txt_LRTestPulseCounter.TabIndex = (int)LogicalRegisters.TestPulseCount;
            txt_LRTestPulseCounter.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRTestPulseCounter);

            //Create Register_MyBoardID Controls
            lbl_MyBoardID.Width = Xwidth;
            lbl_MyBoardID.Height = Yheight;
            lbl_MyBoardID.Text = "R MyBoardID";
            lbl_MyBoardID.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_MyBoardID.BackColor = Color.Coral;
            this.Controls.Add(lbl_MyBoardID);
            txt_LRMyBoardID.Width = Xwidth;
            txt_LRMyBoardID.Height = Yheight;
            txt_LRMyBoardID.Enabled = true;
            txt_LRMyBoardID.BackColor = Color.White;
            txt_LRMyBoardID.Name = "MyBoardID";
            txt_LRMyBoardID.Text = BoardIDDefaultValue.ToString();
            txt_LRMyBoardID.TabIndex = (int)LogicalRegisters.BoardID;
            txt_LRMyBoardID.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRMyBoardID);

            //Create Register_Version Controls
            lbl_Version.Width = Xwidth;
            lbl_Version.Height = Yheight;
            lbl_Version.Text = "R Version";
            lbl_Version.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_Version.BackColor = Color.Coral;
            this.Controls.Add(lbl_Version);
            txt_LRVersion.Width = Xwidth;
            txt_LRVersion.Height = Yheight;
            txt_LRVersion.Enabled = true;
            txt_LRVersion.BackColor = Color.White;
            txt_LRVersion.Name = "Version";
            txt_LRVersion.Text = FirmwareVersionDefaultValue.ToString();
            txt_LRVersion.TabIndex = (int)LogicalRegisters.FirmwareVersion;
            txt_LRVersion.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRVersion);

            //Create Register_HVNumAve Controls
            lbl_HVNumAve.Width = Xwidth;
            lbl_HVNumAve.Height = Yheight;
            lbl_HVNumAve.Text = "WR HV NumAvg";
            lbl_HVNumAve.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_HVNumAve.BackColor = Color.Coral;
            this.Controls.Add(lbl_HVNumAve);
            txt_LWRHVNumAve.Width = Xwidth;
            txt_LWRHVNumAve.Height = Yheight;
            txt_LWRHVNumAve.Enabled = true;
            txt_LWRHVNumAve.BackColor = Color.White;
            txt_LWRHVNumAve.Name = "HVNumAve";
            txt_LWRHVNumAve.Text = HVNumAveDefaultValue.ToString();
            txt_LWRHVNumAve.TabIndex = (int)LogicalRegisters.HVNumAvg;
            txt_LWRHVNumAve.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRHVNumAve);

            //Create Register_HVPeriodMan Controls
            lbl_HVPeriodMan.Width = Xwidth;
            lbl_HVPeriodMan.Height = Yheight;
            lbl_HVPeriodMan.Text = "WR HV PeriodMan";
            lbl_HVPeriodMan.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_HVPeriodMan.BackColor = Color.Coral;
            this.Controls.Add(lbl_HVPeriodMan);
            txt_LWRHVPeriodMan.Width = Xwidth;
            txt_LWRHVPeriodMan.Height = Yheight;
            txt_LWRHVPeriodMan.Enabled = true;
            txt_LWRHVPeriodMan.BackColor = Color.White;
            txt_LWRHVPeriodMan.Name = "HVPeriodMan";
            txt_LWRHVPeriodMan.Text = HVPeriodManualDefaultValue.ToString();
            txt_LWRHVPeriodMan.TabIndex = (int)LogicalRegisters.HVPeriodManual;
            txt_LWRHVPeriodMan.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRHVPeriodMan);

            //Create Register_HVPeriodAuto Controls
            lbl_HVPeriodAuto.Width = Xwidth;
            lbl_HVPeriodAuto.Height = Yheight;
            lbl_HVPeriodAuto.Text = "R HV PeriodAuto";
            lbl_HVPeriodAuto.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_HVPeriodAuto.BackColor = Color.Coral;
            this.Controls.Add(lbl_HVPeriodAuto);
            txt_LRHVPeriodAuto.Width = Xwidth;
            txt_LRHVPeriodAuto.Height = Yheight;
            txt_LRHVPeriodAuto.Enabled = true;
            txt_LRHVPeriodAuto.BackColor = Color.White;
            txt_LRHVPeriodAuto.Name = "HVPeriodAuto";
            txt_LRHVPeriodAuto.Text = HVPeriodAutoDefaultValue.ToString();
            txt_LRHVPeriodAuto.TabIndex = (int)LogicalRegisters.HVPeriodAuto;
            txt_LRHVPeriodAuto.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRHVPeriodAuto);

            //Create Register_HVPulseWidth Controls
            lbl_HVPulseWidth.Width = Xwidth;
            lbl_HVPulseWidth.Height = Yheight;
            lbl_HVPulseWidth.Text = "WR HV PulseWidth";
            lbl_HVPulseWidth.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_HVPulseWidth.BackColor = Color.Coral;
            this.Controls.Add(lbl_HVPulseWidth);
            txt_LWRHVPulseWidth.Width = Xwidth;
            txt_LWRHVPulseWidth.Height = Yheight;
            txt_LWRHVPulseWidth.Enabled = true;
            txt_LWRHVPulseWidth.BackColor = Color.White;
            txt_LWRHVPulseWidth.Name = "HVPulseWidth";
            txt_LWRHVPulseWidth.Text = HVPulseWidthDefaultValue.ToString();
            txt_LWRHVPulseWidth.TabIndex = (int)LogicalRegisters.HVPulseWidth;
            txt_LWRHVPulseWidth.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRHVPulseWidth);

            //Create Register_Temperature Controls
            lbl_Temperature.Width = Xwidth;
            lbl_Temperature.Height = Yheight;
            lbl_Temperature.Text = "R Temperature";
            lbl_Temperature.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_Temperature.BackColor = Color.Coral;
            this.Controls.Add(lbl_Temperature);
            txt_LRTemperature.Width = Xwidth;
            txt_LRTemperature.Height = Yheight;
            txt_LRTemperature.Enabled = true;
            txt_LRTemperature.BackColor = Color.White;
            txt_LRTemperature.Name = "Temperature";
            txt_LRTemperature.Text = TemperatureDefaultValue.ToString();
            txt_LRTemperature.TabIndex = (int)LogicalRegisters.Temperature;
            txt_LRTemperature.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRTemperature);

            //Create Register_TripXThreshold Controls
            lbl_TripXThreshold.Width = Xwidth;
            lbl_TripXThreshold.Height = Yheight;
            lbl_TripXThreshold.Text = "WR TripXThreshold";
            lbl_TripXThreshold.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_TripXThreshold.BackColor = Color.Coral;
            this.Controls.Add(lbl_TripXThreshold);
            txt_LWRTripXThreshold.Width = Xwidth;
            txt_LWRTripXThreshold.Height = Yheight;
            txt_LWRTripXThreshold.Enabled = true;
            txt_LWRTripXThreshold.BackColor = Color.White;
            txt_LWRTripXThreshold.Name = "TripXThreshold";
            txt_LWRTripXThreshold.Text = TripXThresholdDefaultValue.ToString();
            txt_LWRTripXThreshold.TabIndex = (int)LogicalRegisters.TripXThreshold;
            txt_LWRTripXThreshold.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRTripXThreshold);

            //Create Register_TripXComparators Controls
            lbl_TripXComparators.Width = Xwidth;
            lbl_TripXComparators.Height = Yheight;
            lbl_TripXComparators.Text = "R TripXComparators";
            lbl_TripXComparators.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_TripXComparators.BackColor = Color.Coral;
            this.Controls.Add(lbl_TripXComparators);
            txt_LRTripXComparators.Width = Xwidth;
            txt_LRTripXComparators.Height = Yheight;
            txt_LRTripXComparators.Enabled = true;
            txt_LRTripXComparators.BackColor = Color.White;
            txt_LRTripXComparators.Name = "TripXComparators";
            txt_LRTripXComparators.Text = TripXComparatorsDefaultValue.ToString();
            txt_LRTripXComparators.TabIndex = (int)LogicalRegisters.TripXComparators;
            txt_LRTripXComparators.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRTripXComparators);

            //Create Register_ExtTriggFound Controls    // 08.08.2008
            lbl_ExtTriggFound.Width = Xwidth;
            lbl_ExtTriggFound.Height = Yheight;
            lbl_ExtTriggFound.Text = "R ExtTriggFound";
            lbl_ExtTriggFound.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_ExtTriggFound.BackColor = Color.Coral;
            this.Controls.Add(lbl_ExtTriggFound);
            txt_LRExtTriggFound.Width = Xwidth;
            txt_LRExtTriggFound.Height = Yheight;
            txt_LRExtTriggFound.Enabled = true;
            txt_LRExtTriggFound.BackColor = Color.White;
            txt_LRExtTriggFound.Name = "ExtTriggFound";
            txt_LRExtTriggFound.Text = ExtTriggFoundDefaultValue.ToString();
            txt_LRExtTriggFound.TabIndex = (int)LogicalRegisters.ExtTriggFound;
            txt_LRExtTriggFound.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRExtTriggFound);

            //Create Register_ExtTriggRearm Controls    // 08.08.2008
            lbl_ExtTriggRearm.Width = Xwidth;
            lbl_ExtTriggRearm.Height = Yheight;
            lbl_ExtTriggRearm.Text = "WR ExtTriggRearm";
            lbl_ExtTriggRearm.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_ExtTriggRearm.BackColor = Color.Coral;
            this.Controls.Add(lbl_ExtTriggRearm);
            txt_LWRExtTriggRearm.Width = Xwidth;
            txt_LWRExtTriggRearm.Height = Yheight;
            txt_LWRExtTriggRearm.Enabled = true;
            txt_LWRExtTriggRearm.BackColor = Color.White;
            txt_LWRExtTriggRearm.Name = "ExtTriggRearm";
            txt_LWRExtTriggRearm.Text = ExtTriggFoundDefaultValue.ToString();
            txt_LWRExtTriggRearm.TabIndex = (int)LogicalRegisters.ExtTriggRearm;
            txt_LWRExtTriggRearm.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRExtTriggRearm);

            //Create Register_DiscrimEnableMaskTrip0 Controls    // 10.30.2008
            lbl_DiscrimEnableMaskTrip0.Width = Xwidth;
            lbl_DiscrimEnableMaskTrip0.Height = Yheight;
            lbl_DiscrimEnableMaskTrip0.Text = "WR DM_T0 0x";
            lbl_DiscrimEnableMaskTrip0.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_DiscrimEnableMaskTrip0.BackColor = Color.Coral;
            this.Controls.Add(lbl_DiscrimEnableMaskTrip0);
            txt_LWRDiscrimEnableMaskTrip0.Width = Xwidth;
            txt_LWRDiscrimEnableMaskTrip0.Height = Yheight;
            txt_LWRDiscrimEnableMaskTrip0.Enabled = true;
            txt_LWRDiscrimEnableMaskTrip0.BackColor = Color.White;
            txt_LWRDiscrimEnableMaskTrip0.Name = "DiscrimEnableMaskTrip0";
            txt_LWRDiscrimEnableMaskTrip0.Text = DiscrimEnableMaskTrip0DefaultValue.ToString();
            txt_LWRDiscrimEnableMaskTrip0.TabIndex = (int)LogicalRegisters.DiscrimEnableMaskTrip0;
            txt_LWRDiscrimEnableMaskTrip0.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRDiscrimEnableMaskTrip0);

            //Create Register_DiscrimEnableMaskTrip1 Controls    // 10.30.2008
            lbl_DiscrimEnableMaskTrip1.Width = Xwidth;
            lbl_DiscrimEnableMaskTrip1.Height = Yheight;
            lbl_DiscrimEnableMaskTrip1.Text = "WR DM_T1 0x";
            lbl_DiscrimEnableMaskTrip1.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_DiscrimEnableMaskTrip1.BackColor = Color.Coral;
            this.Controls.Add(lbl_DiscrimEnableMaskTrip1);
            txt_LWRDiscrimEnableMaskTrip1.Width = Xwidth;
            txt_LWRDiscrimEnableMaskTrip1.Height = Yheight;
            txt_LWRDiscrimEnableMaskTrip1.Enabled = true;
            txt_LWRDiscrimEnableMaskTrip1.BackColor = Color.White;
            txt_LWRDiscrimEnableMaskTrip1.Name = "DiscrimEnableMaskTrip1";
            txt_LWRDiscrimEnableMaskTrip1.Text = DiscrimEnableMaskTrip1DefaultValue.ToString();
            txt_LWRDiscrimEnableMaskTrip1.TabIndex = (int)LogicalRegisters.DiscrimEnableMaskTrip1;
            txt_LWRDiscrimEnableMaskTrip1.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRDiscrimEnableMaskTrip1);

            //Create Register_DiscrimEnableMaskTrip2 Controls    // 10.30.2008
            lbl_DiscrimEnableMaskTrip2.Width = Xwidth;
            lbl_DiscrimEnableMaskTrip2.Height = Yheight;
            lbl_DiscrimEnableMaskTrip2.Text = "WR DM_T2 0x";
            lbl_DiscrimEnableMaskTrip2.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_DiscrimEnableMaskTrip2.BackColor = Color.Coral;
            this.Controls.Add(lbl_DiscrimEnableMaskTrip2);
            txt_LWRDiscrimEnableMaskTrip2.Width = Xwidth;
            txt_LWRDiscrimEnableMaskTrip2.Height = Yheight;
            txt_LWRDiscrimEnableMaskTrip2.Enabled = true;
            txt_LWRDiscrimEnableMaskTrip2.BackColor = Color.White;
            txt_LWRDiscrimEnableMaskTrip2.Name = "DiscrimEnableMaskTrip2";
            txt_LWRDiscrimEnableMaskTrip2.Text = DiscrimEnableMaskTrip2DefaultValue.ToString();
            txt_LWRDiscrimEnableMaskTrip2.TabIndex = (int)LogicalRegisters.DiscrimEnableMaskTrip2;
            txt_LWRDiscrimEnableMaskTrip2.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRDiscrimEnableMaskTrip2);

            //Create Register_DiscrimEnableMaskTrip3 Controls    // 10.30.2008
            lbl_DiscrimEnableMaskTrip3.Width = Xwidth;
            lbl_DiscrimEnableMaskTrip3.Height = Yheight;
            lbl_DiscrimEnableMaskTrip3.Text = "WR DM_T3 0x";
            lbl_DiscrimEnableMaskTrip3.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_DiscrimEnableMaskTrip3.BackColor = Color.Coral;
            this.Controls.Add(lbl_DiscrimEnableMaskTrip3);
            txt_LWRDiscrimEnableMaskTrip3.Width = Xwidth;
            txt_LWRDiscrimEnableMaskTrip3.Height = Yheight;
            txt_LWRDiscrimEnableMaskTrip3.Enabled = true;
            txt_LWRDiscrimEnableMaskTrip3.BackColor = Color.White;
            txt_LWRDiscrimEnableMaskTrip3.Name = "DiscrimEnableMaskTrip3";
            txt_LWRDiscrimEnableMaskTrip3.Text = DiscrimEnableMaskTrip3DefaultValue.ToString();
            txt_LWRDiscrimEnableMaskTrip3.TabIndex = (int)LogicalRegisters.DiscrimEnableMaskTrip3;
            txt_LWRDiscrimEnableMaskTrip1.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRDiscrimEnableMaskTrip3);

            //Create Register_GateTimeStamp Controls    // 12.22.2008
            lbl_GateTimeStamp.Width = Xwidth;
            lbl_GateTimeStamp.Height = Yheight;
            lbl_GateTimeStamp.Text = "R GateTimeStamp";
            lbl_GateTimeStamp.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_GateTimeStamp.BackColor = Color.Coral;
            this.Controls.Add(lbl_GateTimeStamp);
            txt_LRGateTimeStamp.Width = Xwidth;
            txt_LRGateTimeStamp.Height = Yheight;
            txt_LRGateTimeStamp.Enabled = true;
            txt_LRGateTimeStamp.BackColor = Color.White;
            txt_LRGateTimeStamp.Name = "GateTimeStamp";
            txt_LRGateTimeStamp.Text = GateTimeStampDefaultValue.ToString();
            txt_LRGateTimeStamp.TabIndex = (int)LogicalRegisters.GateTimeStamp;
            txt_LRGateTimeStamp.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRGateTimeStamp);

            //Create Register_StatusSCMDUnknown Controls    // 11.13.2009
            lbl_StatusSCMDUnknown.Width = Xwidth;
            lbl_StatusSCMDUnknown.Height = Yheight;
            lbl_StatusSCMDUnknown.Text = "R StatSCMDErr";
            lbl_StatusSCMDUnknown.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_StatusSCMDUnknown.BackColor = Color.Coral;
            this.Controls.Add(lbl_StatusSCMDUnknown);
            txt_LRStatusSCMDUnknown.Width = Xwidth;
            txt_LRStatusSCMDUnknown.Height = Yheight;
            txt_LRStatusSCMDUnknown.Enabled = true;
            txt_LRStatusSCMDUnknown.BackColor = Color.White;
            txt_LRStatusSCMDUnknown.Name = "StatusSCMDUnknown";
            txt_LRStatusSCMDUnknown.Text = StatusSCMDUnknownDefaultValue.ToString();
            txt_LRStatusSCMDUnknown.TabIndex = (int)LogicalRegisters.StatusSCMDUnknown;
            txt_LRStatusSCMDUnknown.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRStatusSCMDUnknown);

            //Create Register_StatusFCMDUnknown Controls    // 11.13.2009
            lbl_StatusFCMDUnknown.Width = Xwidth;
            lbl_StatusFCMDUnknown.Height = Yheight;
            lbl_StatusFCMDUnknown.Text = "R StatFCMDErr";
            lbl_StatusFCMDUnknown.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_StatusFCMDUnknown.BackColor = Color.Coral;
            this.Controls.Add(lbl_StatusFCMDUnknown);
            txt_LRStatusFCMDUnknown.Width = Xwidth;
            txt_LRStatusFCMDUnknown.Height = Yheight;
            txt_LRStatusFCMDUnknown.Enabled = true;
            txt_LRStatusFCMDUnknown.BackColor = Color.White;
            txt_LRStatusFCMDUnknown.Name = "StatusFCMDUnknown";
            txt_LRStatusFCMDUnknown.Text = StatusFCMDUnknownDefaultValue.ToString();
            txt_LRStatusFCMDUnknown.TabIndex = (int)LogicalRegisters.StatusFCMDUnknown;
            txt_LRStatusFCMDUnknown.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRStatusFCMDUnknown);

            //Create Register_StatusRXLock Controls    // 11.13.2009
            lbl_StatusRXLock.Width = Xwidth;
            lbl_StatusRXLock.Height = Yheight;
            lbl_StatusRXLock.Text = "R StatRXLockErr";
            lbl_StatusRXLock.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_StatusRXLock.BackColor = Color.Coral;
            this.Controls.Add(lbl_StatusRXLock);
            txt_LRStatusRXLock.Width = Xwidth;
            txt_LRStatusRXLock.Height = Yheight;
            txt_LRStatusRXLock.Enabled = true;
            txt_LRStatusRXLock.BackColor = Color.White;
            txt_LRStatusRXLock.Name = "StatusRXLock";
            txt_LRStatusRXLock.Text = StatusRXLockDefaultValue.ToString();
            txt_LRStatusRXLock.TabIndex = (int)LogicalRegisters.StatusRXLock;
            txt_LRStatusRXLock.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRStatusRXLock);

            //Create Register_StatusTXSyncLock Controls    // 11.13.2009
            lbl_StatusTXSyncLock.Width = Xwidth;
            lbl_StatusTXSyncLock.Height = Yheight;
            lbl_StatusTXSyncLock.Text = "R StatTXLockErr";
            lbl_StatusTXSyncLock.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_StatusTXSyncLock.BackColor = Color.Coral;
            this.Controls.Add(lbl_StatusTXSyncLock);
            txt_LRStatusTXSyncLock.Width = Xwidth;
            txt_LRStatusTXSyncLock.Height = Yheight;
            txt_LRStatusTXSyncLock.Enabled = true;
            txt_LRStatusTXSyncLock.BackColor = Color.White;
            txt_LRStatusTXSyncLock.Name = "StatusTXSyncLock";
            txt_LRStatusTXSyncLock.Text = StatusTXSyncLockDefaultValue.ToString();
            txt_LRStatusTXSyncLock.TabIndex = (int)LogicalRegisters.StatusTXSyncLock;
            txt_LRStatusTXSyncLock.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LRStatusTXSyncLock);
        
        }

        public bool IsAdvancedGUI { get { return isAdvancedGUI; } }
        public UInt32 RegisterTimer
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.Timer]; }
            set { FPGALogicalReg[(int)LogicalRegisters.Timer] = value; }
        }
        public UInt32 RegisterGateStart
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.GateStart]; }
            set { FPGALogicalReg[(int)LogicalRegisters.GateStart] = value; }
        }
        public UInt32 RegisterGateLength
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.GateLength]; }
            set { FPGALogicalReg[(int)LogicalRegisters.GateLength] = value; }
        }
        public UInt32 RegisterTripPowerOff
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.TripPowerOff]; }
            set { FPGALogicalReg[(int)LogicalRegisters.TripPowerOff] = value; }
        }
        public UInt32[] RegisterInjectCount
        {
            get
            {
                UInt32[] InjectCount = new UInt32[6];
                InjectCount[0] = (byte)(FPGALogicalReg[(int)LogicalRegisters.InjectCount0] & 0x7F);
                InjectCount[1] = (byte)(FPGALogicalReg[(int)LogicalRegisters.InjectCount1] & 0x7F);
                InjectCount[2] = (byte)(FPGALogicalReg[(int)LogicalRegisters.InjectCount2] & 0x7F);
                InjectCount[3] = (byte)(FPGALogicalReg[(int)LogicalRegisters.InjectCount3] & 0x7F);
                InjectCount[4] = (byte)(FPGALogicalReg[(int)LogicalRegisters.InjectCount4] & 0x7F);
                InjectCount[5] = (byte)(FPGALogicalReg[(int)LogicalRegisters.InjectCount5] & 0x7F);
                return InjectCount;
            }
            set
            {
                FPGALogicalReg[(int)LogicalRegisters.InjectCount0] = (value[0] & 0x7F) | (FPGALogicalReg[(int)LogicalRegisters.InjectCount0] & 0x80);
                FPGALogicalReg[(int)LogicalRegisters.InjectCount1] = (value[1] & 0x7F) | (FPGALogicalReg[(int)LogicalRegisters.InjectCount1] & 0x80);
                FPGALogicalReg[(int)LogicalRegisters.InjectCount2] = (value[2] & 0x7F) | (FPGALogicalReg[(int)LogicalRegisters.InjectCount2] & 0x80);
                FPGALogicalReg[(int)LogicalRegisters.InjectCount3] = (value[3] & 0x7F) | (FPGALogicalReg[(int)LogicalRegisters.InjectCount3] & 0x80);
                FPGALogicalReg[(int)LogicalRegisters.InjectCount4] = (value[4] & 0x7F) | (FPGALogicalReg[(int)LogicalRegisters.InjectCount4] & 0x80);
                FPGALogicalReg[(int)LogicalRegisters.InjectCount5] = (value[5] & 0x7F) | (FPGALogicalReg[(int)LogicalRegisters.InjectCount5] & 0x80);
            }
        }
        public UInt32 RegisterInjectEnable
        {
            get
            {
                uint InjectEnable = 0;
                InjectEnable += (FPGALogicalReg[(int)LogicalRegisters.InjectCount0] & 0x80) >> 7;
                InjectEnable += (FPGALogicalReg[(int)LogicalRegisters.InjectCount1] & 0x80) >> 6;
                InjectEnable += (FPGALogicalReg[(int)LogicalRegisters.InjectCount2] & 0x80) >> 5;
                InjectEnable += (FPGALogicalReg[(int)LogicalRegisters.InjectCount3] & 0x80) >> 4;
                InjectEnable += (FPGALogicalReg[(int)LogicalRegisters.InjectCount4] & 0x80) >> 3;
                InjectEnable += (FPGALogicalReg[(int)LogicalRegisters.InjectCount5] & 0x80) >> 2;
                return InjectEnable;
            }
            set
            {
                FPGALogicalReg[(int)LogicalRegisters.InjectCount0] = ((value & 0x1) << 7) | (FPGALogicalReg[(int)LogicalRegisters.InjectCount0] & 0x7F);
                FPGALogicalReg[(int)LogicalRegisters.InjectCount1] = ((value & 0x2) << 6) | (FPGALogicalReg[(int)LogicalRegisters.InjectCount1] & 0x7F);
                FPGALogicalReg[(int)LogicalRegisters.InjectCount2] = ((value & 0x4) << 5) | (FPGALogicalReg[(int)LogicalRegisters.InjectCount2] & 0x7F);
                FPGALogicalReg[(int)LogicalRegisters.InjectCount3] = ((value & 0x8) << 4) | (FPGALogicalReg[(int)LogicalRegisters.InjectCount3] & 0x7F);
                FPGALogicalReg[(int)LogicalRegisters.InjectCount4] = ((value & 0x10) << 3) | (FPGALogicalReg[(int)LogicalRegisters.InjectCount4] & 0x7F);
                FPGALogicalReg[(int)LogicalRegisters.InjectCount5] = ((value & 0x20) << 2) | (FPGALogicalReg[(int)LogicalRegisters.InjectCount5] & 0x7F);
            }
        }
        public UInt32 RegisterInjectRange
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.InjectRange]; }
            set { FPGALogicalReg[(int)LogicalRegisters.InjectRange] = value; }
        }
        public UInt32 RegisterInjectPhase
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.InjectPhase]; }
            set { FPGALogicalReg[(int)LogicalRegisters.InjectPhase] = value; }
        }
        public UInt32 RegisterInjectDACValue
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.InjectDACValue]; }
            set { FPGALogicalReg[(int)LogicalRegisters.InjectDACValue] = value; }
        }
        public UInt32 RegisterInjectDACMode
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.InjectDACMode]; }
            set { FPGALogicalReg[(int)LogicalRegisters.InjectDACMode] = value; }
        }
        public UInt32 RegisterInjectDACStart
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.InjectDACStart]; }
            set { FPGALogicalReg[(int)LogicalRegisters.InjectDACStart] = value; }
        }
        public UInt32 RegisterInjectDACDone
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.InjectDACDone]; }
            set { FPGALogicalReg[(int)LogicalRegisters.InjectDACDone] = value; }
        }
        public UInt32 RegisterHVEnabled
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.HVEnabled]; }
            set { FPGALogicalReg[(int)LogicalRegisters.HVEnabled] = value; }
        }
        public UInt32 RegisterHVTarget
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.HVTarget]; }
            set { FPGALogicalReg[(int)LogicalRegisters.HVTarget] = value; }
        }
        public UInt32 RegisterHVActual
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.HVActual]; }
            set { FPGALogicalReg[(int)LogicalRegisters.HVActual] = value; }
        }
        public UInt32 RegisterHVControl
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.HVControl]; }
            set { FPGALogicalReg[(int)LogicalRegisters.HVControl] = value; }
        }
        public UInt32 RegisterHVAutoManual
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.HVAutoManual]; }
            set { FPGALogicalReg[(int)LogicalRegisters.HVAutoManual] = value; }
        }
        public UInt32 RegisterPhaseStart
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.PhaseStart]; }
            set { FPGALogicalReg[(int)LogicalRegisters.PhaseStart] = value; }
        }
        public UInt32 RegisterPhaseIncrement
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.PhaseIncrement]; }
            set { FPGALogicalReg[(int)LogicalRegisters.PhaseIncrement] = value; }
        }
        public UInt32 RegisterPhaseTicks
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.PhaseTicks]; }
            set { FPGALogicalReg[(int)LogicalRegisters.PhaseTicks] = value; }
        }
        public UInt32 RegisterDCM1Lock
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.DCM1Lock]; }
            set { FPGALogicalReg[(int)LogicalRegisters.DCM1Lock] = value; }
        }
        public UInt32 RegisterDCM2Lock
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.DCM2Lock]; }
            set { FPGALogicalReg[(int)LogicalRegisters.DCM2Lock] = value; }
        }
        public UInt32 RegisterDCM1NoClock
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.DCM1NoClock]; }
            set { FPGALogicalReg[(int)LogicalRegisters.DCM1NoClock] = value; }
        }
        public UInt32 RegisterDCM2NoClock
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.DCM2NoClock]; }
            set { FPGALogicalReg[(int)LogicalRegisters.DCM2NoClock] = value; }
        }
        public UInt32 RegisterDCM2PhaseDone
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.DCM2PhaseDone]; }
            set { FPGALogicalReg[(int)LogicalRegisters.DCM2PhaseDone] = value; }
        }
        public UInt32 RegisterDCM2PhaseTotal
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.DCM2PhaseTotal]; }
            set { FPGALogicalReg[(int)LogicalRegisters.DCM2PhaseTotal] = value; }
        }
        public UInt32 RegisterTestPulse2Bit
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.TestPulse2Bit]; }
            set { FPGALogicalReg[(int)LogicalRegisters.TestPulse2Bit] = value; }
        }
        public UInt32 RegisterTestPulseCount
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.TestPulseCount]; }
            set { FPGALogicalReg[(int)LogicalRegisters.TestPulseCount] = value; }
        }
        public UInt32 RegisterBoardID
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.BoardID]; }
            set { FPGALogicalReg[(int)LogicalRegisters.BoardID] = value; }
        }
        public UInt32 RegisterFirmwareVersion
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.FirmwareVersion]; }
            set { FPGALogicalReg[(int)LogicalRegisters.FirmwareVersion] = value; }
        }
        public UInt32 RegisterHVNumAvg
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.HVNumAvg]; }
            set { FPGALogicalReg[(int)LogicalRegisters.HVNumAvg] = value; }
        }
        public UInt32 RegisterHVPeriodManual
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.HVPeriodManual]; }
            set { FPGALogicalReg[(int)LogicalRegisters.HVPeriodManual] = value; }
        }
        public UInt32 RegisterHVPeriodAuto
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.HVPeriodAuto]; }
            set { FPGALogicalReg[(int)LogicalRegisters.HVPeriodAuto] = value; }
        }
        public UInt32 RegisterHVPulseWidth
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.HVPulseWidth]; }
            set { FPGALogicalReg[(int)LogicalRegisters.HVPulseWidth] = value; }
        }
        public UInt32 RegisterTemperature
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.Temperature]; }
            set { FPGALogicalReg[(int)LogicalRegisters.Temperature] = value; }
        }
        public UInt32 RegisterTripXThreshold
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.TripXThreshold]; }
            set { FPGALogicalReg[(int)LogicalRegisters.TripXThreshold] = value; }
        }
        public UInt32 RegisterTripXComparators
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.TripXComparators]; }
            set { FPGALogicalReg[(int)LogicalRegisters.TripXComparators] = value; }
        }
        public UInt32 RegisterExtTriggFound             // 08.08.2008
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.ExtTriggFound]; }
            set { FPGALogicalReg[(int)LogicalRegisters.ExtTriggFound] = value; }
        }
        public UInt32 RegisterExtTriggRearm             // 08.08.2008
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.ExtTriggRearm]; }
            set { FPGALogicalReg[(int)LogicalRegisters.ExtTriggRearm] = value; }
        }
        public UInt32 RegisterDiscrimEnableMaskTrip0    // 10.30.2008
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.DiscrimEnableMaskTrip0]; }
            set { FPGALogicalReg[(int)LogicalRegisters.DiscrimEnableMaskTrip0] = value; }
        }
        public UInt32 RegisterDiscrimEnableMaskTrip1    // 10.30.2008
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.DiscrimEnableMaskTrip1]; }
            set { FPGALogicalReg[(int)LogicalRegisters.DiscrimEnableMaskTrip1] = value; }
        }
        public UInt32 RegisterDiscrimEnableMaskTrip2    // 10.30.2008
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.DiscrimEnableMaskTrip2]; }
            set { FPGALogicalReg[(int)LogicalRegisters.DiscrimEnableMaskTrip2] = value; }
        }
        public UInt32 RegisterDiscrimEnableMaskTrip3    // 10.30.2008
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.DiscrimEnableMaskTrip3]; }
            set { FPGALogicalReg[(int)LogicalRegisters.DiscrimEnableMaskTrip3] = value; }
        }
        public UInt32 RegisterGateTimeStamp             // 12.22.2008
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.GateTimeStamp]; }
            set { FPGALogicalReg[(int)LogicalRegisters.GateTimeStamp] = value; }
        }
        public UInt32 RegisterStatusSCMDUnknown         // 11.13.2009
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.StatusSCMDUnknown]; }
            set { FPGALogicalReg[(int)LogicalRegisters.StatusSCMDUnknown] = value; }
        }
        public UInt32 RegisterStatusFCMDUnknown         // 11.13.2009
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.StatusFCMDUnknown]; }
            set { FPGALogicalReg[(int)LogicalRegisters.StatusFCMDUnknown] = value; }
        }
        public UInt32 RegisterStatusRXLock              // 11.13.2009
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.StatusRXLock]; }
            set { FPGALogicalReg[(int)LogicalRegisters.StatusRXLock] = value; }
        }
        public UInt32 RegisterStatusTXSyncLock          // 11.13.2009
        {
            get { return FPGALogicalReg[(int)LogicalRegisters.StatusTXSyncLock]; }
            set { FPGALogicalReg[(int)LogicalRegisters.StatusTXSyncLock] = value; }
        }

        private void control_Validating(object sender, CancelEventArgs e)
        {
            try
            {
                if (sender is TextBox)
                {
                    switch (((TextBox)sender).TabIndex)
                    {
                        case (int)LogicalRegisters.Timer:
                        case (int)LogicalRegisters.TestPulseCount:
                        case (int)LogicalRegisters.GateTimeStamp:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0xFFFFFFFF, 0, "Value must be 32 bits");
                            break;
                        case (int)LogicalRegisters.GateStart:
                        case (int)LogicalRegisters.GateLength:
                        case (int)LogicalRegisters.HVTarget:
                        case (int)LogicalRegisters.HVActual:
                        case (int)LogicalRegisters.HVPeriodManual:
                        case (int)LogicalRegisters.HVPeriodAuto:
                        case (int)LogicalRegisters.Temperature:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0xFFFF, 0, "Value must be 16 bits");
                            break;
                        case (int)LogicalRegisters.DiscrimEnableMaskTrip0:
                        case (int)LogicalRegisters.DiscrimEnableMaskTrip1:
                        case (int)LogicalRegisters.DiscrimEnableMaskTrip2:
                        case (int)LogicalRegisters.DiscrimEnableMaskTrip3:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text, 16), 0xFFFF, 0, "Value must be 16 bits");
                            break;
                        case (int)LogicalRegisters.InjectDACValue:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0xFFF, 0, "Value must be 12 bits");
                            break;
                        case (int)LogicalRegisters.DCM2PhaseTotal:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0x1FF, 0, "Value must be 9 bits");
                            break;
                        case (int)LogicalRegisters.HVControl:
                        case (int)LogicalRegisters.PhaseTicks:
                        case (int)LogicalRegisters.FirmwareVersion:
                        case (int)LogicalRegisters.HVPulseWidth:
                        case (int)LogicalRegisters.TripXThreshold:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0xFF, 0, "Value must be 8 bits");
                            break;
                        case (int)LogicalRegisters.InjectCount0:
                        case (int)LogicalRegisters.InjectCount1:
                        case (int)LogicalRegisters.InjectCount2:
                        case (int)LogicalRegisters.InjectCount3:
                        case (int)LogicalRegisters.InjectCount4:
                        case (int)LogicalRegisters.InjectCount5:
                            //cg+gnp//CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0x7F, 0, "Value must be 7 bits");
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0xFF, 0, "Value must be 8 bits");
                            break;
                        case (int)LogicalRegisters.TripPowerOff:
                        case (int)LogicalRegisters.TripXComparators:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0x3F, 0, "Value must be 6 bits");
                            break;
                        case (int)LogicalRegisters.InjectRange:
                        case (int)LogicalRegisters.BoardID:
                        case (int)LogicalRegisters.HVNumAvg:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0xF, 0, "Value must be 4 bits");
                            break;
                        case (int)LogicalRegisters.TestPulse2Bit:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0x3, 0, "Value must be 2 bits");
                            break;
                        case (int)LogicalRegisters.InjectDACDone:
                        case (int)LogicalRegisters.DCM1Lock:
                        case (int)LogicalRegisters.DCM2Lock:
                        case (int)LogicalRegisters.DCM1NoClock:
                        case (int)LogicalRegisters.DCM2NoClock:
                        case (int)LogicalRegisters.DCM2PhaseDone:
                        case (int)LogicalRegisters.ExtTriggFound:
                        case (int)LogicalRegisters.ExtTriggRearm:

                        case (int)LogicalRegisters.StatusSCMDUnknown:
                        case (int)LogicalRegisters.StatusFCMDUnknown:
                        case (int)LogicalRegisters.StatusRXLock:
                        case (int)LogicalRegisters.StatusTXSyncLock:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0x1, 0, "Value must be 1 bit");
                            break;
                    }
                }
                //Any other ComboBox and CheckBox does not need any checks inside Validating() event
                //since the SelectedIndex or the Checked properties represent exactely the data value.
                //There is ONE exception: the "TripXInjectCntPhase" needs special treatment...
                if (sender is ComboBox)
                    if (((ComboBox)sender).TabIndex == (int)LogicalRegisters.InjectPhase)
                        if (((ComboBox)sender).SelectedIndex == 4)
                        {
                            errorProvider.SetIconAlignment((Control)sender, ErrorIconAlignment.MiddleRight);
                            errorProvider.SetError((Control)sender, "Valid inputs are 1,2,4,8");
                        }
                        else
                            errorProvider.SetError((Control)sender, "");
            }
            catch (Exception e2)
            {
                errorProvider.SetError((Control)sender, e2.Message);
            }
        }

        private void CheckInput(object sender, CancelEventArgs e, Int64 Value, Int64 MaxValue, Int64 MinVal, string msg)
        {
            if (Value > MaxValue | Value < MinVal)
            {
                errorProvider.SetIconAlignment((Control)sender, ErrorIconAlignment.MiddleRight);
                errorProvider.SetError((Control)sender, msg);
            }
            else
                errorProvider.SetError((Control)sender, "");
        }

        public void UpdateFPGALogicalRegArray()
        {
            foreach (Control ctrl in this.Controls)
            {
                if (ctrl.TabIndex < NLogicalRgisters)
                {
                    try
                    {
                        if (ctrl is TextBox)
                        {
                            if (ctrl.TabIndex == (int)LogicalRegisters.Temperature)
                            {
                                //this is special update for Temperature register
                                FPGALogicalReg[ctrl.TabIndex] = Convert.ToUInt32((((TextBox)ctrl).Text).Split(',')[0]);
                            }
                            else if ((ctrl.TabIndex == (int)LogicalRegisters.DiscrimEnableMaskTrip0) |
                                (ctrl.TabIndex == (int)LogicalRegisters.DiscrimEnableMaskTrip1) |
                                (ctrl.TabIndex == (int)LogicalRegisters.DiscrimEnableMaskTrip2) |
                                (ctrl.TabIndex == (int)LogicalRegisters.DiscrimEnableMaskTrip3))
                            {
                                //this is special update for DiscrimEnableMaskTripX registers
                                FPGALogicalReg[ctrl.TabIndex] = Convert.ToUInt32((((TextBox)ctrl).Text), 16);
                            }
                            else
                                FPGALogicalReg[ctrl.TabIndex] = Convert.ToUInt32(((TextBox)ctrl).Text);
                        }
                        if (ctrl is ComboBox)
                            //"TripXInjectCntPhase" needs special treatment...
                            if (((ComboBox)ctrl).TabIndex == (int)LogicalRegisters.InjectPhase)
                            {
                                if (((ComboBox)ctrl).SelectedIndex == 4)
                                    //force binary value 0000
                                    FPGALogicalReg[ctrl.TabIndex] = 0;
                                else
                                    //force bynary values of 0001, 0010, 0100, 1000
                                    FPGALogicalReg[ctrl.TabIndex] = Convert.ToUInt32(Math.Pow(2.0, ((ComboBox)ctrl).SelectedIndex));
                            }
                            else
                                FPGALogicalReg[ctrl.TabIndex] = Convert.ToUInt32(((ComboBox)ctrl).SelectedIndex);
                        if (ctrl is CheckBox)
                            FPGALogicalReg[ctrl.TabIndex] = Convert.ToUInt32(((CheckBox)ctrl).Checked);
                    }
                    catch (Exception ee)
                    {
                        MessageBox.Show(ee.Message);
                    }
                }
            }
        }

        public void UpdateFormControls()
        {
            foreach (Control ctrl in this.Controls)
            {
                if (ctrl.TabIndex < NLogicalRgisters)
                {
                    if (ctrl is TextBox)
                    {
                        if ((ctrl.TabIndex == (int)LogicalRegisters.DiscrimEnableMaskTrip0) |
                            (ctrl.TabIndex == (int)LogicalRegisters.DiscrimEnableMaskTrip1) |
                            (ctrl.TabIndex == (int)LogicalRegisters.DiscrimEnableMaskTrip2) |
                            (ctrl.TabIndex == (int)LogicalRegisters.DiscrimEnableMaskTrip3))
                        {
                            //this is special update for DiscrimEnableMaskTripX registers
                            ((TextBox)ctrl).Text = FPGALogicalReg[ctrl.TabIndex].ToString("X4");
                        }
                        else
                            ((TextBox)ctrl).Text = FPGALogicalReg[ctrl.TabIndex].ToString();
                        control_Validating(ctrl, null);
                    }
                    if (ctrl is ComboBox)
                    {
                        //"TripXInjectCntPhase" needs special treatment...
                        if (((ComboBox)ctrl).TabIndex == (int)LogicalRegisters.InjectPhase)
                        {
                            switch ((int)FPGALogicalReg[ctrl.TabIndex])
                            {
                                case 1:
                                    ((ComboBox)ctrl).SelectedIndex = 0;
                                    errorProvider.SetError(ctrl, "");
                                    break;
                                case 2:
                                    errorProvider.SetError(ctrl, "");
                                    ((ComboBox)ctrl).SelectedIndex = 1;
                                    break;
                                case 4:
                                    errorProvider.SetError(ctrl, "");
                                    ((ComboBox)ctrl).SelectedIndex = 2;
                                    break;
                                case 8:
                                    errorProvider.SetError(ctrl, "");
                                    ((ComboBox)ctrl).SelectedIndex = 3;
                                    break;
                                default:
                                    errorProvider.SetIconAlignment(ctrl, ErrorIconAlignment.MiddleRight);
                                    errorProvider.SetError(ctrl, "Valid inputs are 1,2,4,8");
                                    ((ComboBox)ctrl).SelectedIndex = 4;
                                    break;
                            }
                        }
                        else
                            ((ComboBox)ctrl).SelectedIndex = (int)FPGALogicalReg[ctrl.TabIndex];
                    }
                    if (ctrl is CheckBox)
                        ((CheckBox)ctrl).Checked = Convert.ToBoolean(FPGALogicalReg[ctrl.TabIndex]);
                }
            }
            txt_LRTemperature.Text += ", " + Convert.ToDouble(txt_LRTemperature.Text) * 0.125 * 0.0625 + " C";
        }

        public void ShowAdvancedGUI(bool Advanced)
        {
            isAdvancedGUI = Advanced;
            int Xoffset = 10;
            int Yoffset = 10;
            foreach (Control ctrl in this.Controls)
                ctrl.Visible = false;

            if (!Advanced)
            {
                lbl_TripXPowerDown.Location = new Point(Xoffset, Yoffset);
                txt_LWRTripXPowerDown.Location = new Point(lbl_TripXPowerDown.Left + lbl_TripXPowerDown.Width + 5, lbl_TripXPowerDown.Top);
                lbl_TripXPowerDown.Visible = true;
                txt_LWRTripXPowerDown.Visible = true;
                CreateLocations(lbl_TripXPowerDown, lbl_GateStart, txt_LWRGateStart, true, true);
                CreateLocations(lbl_GateStart, lbl_GateLength, txt_LWRGateLength, true, true);
                CreateLocations(lbl_GateLength, lbl_HVEnable, cmb_LWRHVEnable, true, true);
                CreateLocations(lbl_HVEnable, lbl_HVTarget, txt_LWRHVTarget, true, true);
                CreateLocations(lbl_HVTarget, lbl_HVActual, txt_LRHVActual, true, true);
                CreateLocations(lbl_HVActual, lbl_HVAutoMan, cmb_LWRHVAutoMan, true, true);
                CreateLocations(lbl_HVAutoMan, lbl_HVNumAve, txt_LWRHVNumAve, true, true);
                CreateLocations(lbl_HVNumAve, lbl_HVPeriodMan, txt_LWRHVPeriodMan, true, true);
                CreateLocations(lbl_HVPeriodMan, lbl_HVPeriodAuto, txt_LRHVPeriodAuto, true, true);
                CreateLocations(lbl_HVPeriodAuto, lbl_HVPulseWidth, txt_LWRHVPulseWidth, true, true);
                CreateLocations(lbl_HVPulseWidth, lbl_Temperature, txt_LRTemperature, true, true);
                CreateLocations(lbl_Temperature, lbl_Version, txt_LRVersion, true, true);
                CreateLocations(lbl_Version, lbl_MyBoardID, txt_LRMyBoardID, true, true);
            }
            else
            {
                lbl_Timer.Location = new Point(Xoffset, Yoffset);
                txt_LWRTimer.Location = new Point(lbl_Timer.Left + lbl_Timer.Width + 5, lbl_Timer.Top);
                lbl_Timer.Visible = true;
                txt_LWRTimer.Visible = true;

                CreateLocations(lbl_Timer, lbl_GateStart, txt_LWRGateStart, true, true);
                CreateLocations(lbl_GateStart, lbl_GateLength, txt_LWRGateLength, true, true);
                CreateLocations(lbl_GateLength, lbl_TripXPowerDown, txt_LWRTripXPowerDown, true, true);
                CreateLocations(lbl_TripXPowerDown, lbl_Trip0InjectCnt, txt_LWRTrip0InjectCnt, true, true);
                CreateLocations(lbl_Trip0InjectCnt, lbl_Trip1InjectCnt, txt_LWRTrip1InjectCnt, true, true);
                CreateLocations(lbl_Trip1InjectCnt, lbl_Trip2InjectCnt, txt_LWRTrip2InjectCnt, true, true);
                CreateLocations(lbl_Trip2InjectCnt, lbl_Trip3InjectCnt, txt_LWRTrip3InjectCnt, true, true);
                CreateLocations(lbl_Trip3InjectCnt, lbl_Trip4InjectCnt, txt_LWRTrip4InjectCnt, true, true);
                CreateLocations(lbl_Trip4InjectCnt, lbl_Trip5InjectCnt, txt_LWRTrip5InjectCnt, true, true);
                CreateLocations(lbl_Trip5InjectCnt, lbl_TripXInjectCntRange, txt_LWRTripXInjectCntRange, true, true);
                CreateLocations(lbl_TripXInjectCntRange, lbl_TripXInjectCntPhase, cmb_LWRTripXInjectCntPhase, true, true);
                CreateLocations(lbl_TripXInjectCntPhase, lbl_TripXInjDACVal, txt_LWRTripXInjDACVal, true, true);
                CreateLocations(lbl_TripXInjDACVal, lbl_TripXInjDACMode, cmb_LWRTripXInjDACMode, true, true);
                CreateLocations(lbl_TripXInjDACMode, lbl_TripXInjDACStartClearn, cmb_LWRTripXInjDACStartClearn, true, true);
                CreateLocations(lbl_TripXInjDACStartClearn, lbl_TripXInjDACDone, txt_LRTripXInjDACDone, true, true);
                CreateLocations(lbl_TripXInjDACDone, lbl_HVEnable, cmb_LWRHVEnable, true, true);
                CreateLocations(lbl_HVEnable, lbl_HVTarget, txt_LWRHVTarget, true, true);
                CreateLocations(lbl_HVTarget, lbl_HVActual, txt_LRHVActual, true, true);
                CreateLocations(lbl_HVActual, lbl_HVControl, txt_LRHVControl, true, true);
                CreateLocations(lbl_HVControl, lbl_HVAutoMan, cmb_LWRHVAutoMan, true, true);
                CreateLocations(lbl_HVAutoMan, lbl_PHShiftStartClearn, cmb_LWRPHShiftStartClearn, true, true);
                CreateLocations(lbl_PHShiftStartClearn, lbl_PHShiftDecr0Incr1, cmb_LWRPHShiftDecr0Incr1, true, true);
                CreateLocations(lbl_PHShiftDecr0Incr1, lbl_PHShiftVal, txt_LWRPHShiftVal, true, true);
                CreateLocations(lbl_PHShiftVal, lbl_DCM1Locked, txt_LRDCM1Locked, true, true);
                CreateLocations(lbl_DCM1Locked, lbl_DCM2Locked, txt_LRDCM2Locked, true, true);
                CreateLocations(lbl_DCM2Locked, lbl_DCM1NoClk, txt_LRDCM1NoClk, true, true);
                CreateLocations(lbl_DCM1NoClk, lbl_DCM2NoClk, txt_LRDCM2NoClk, true, true);
                CreateLocations(lbl_DCM2NoClk, lbl_DCM2PHShiftDone, txt_LRDCM2PHShiftDone, true, true);
                CreateLocations(lbl_DCM2PHShiftDone, lbl_DCM2TotalPhaseShift, txt_LRDCM2TotalPhaseShift, true, true);
                CreateLocations(lbl_DCM2TotalPhaseShift, lbl_TestPulseCounter2b, txt_LRTestPulseCounter2b, true, true);
                CreateLocations(lbl_TestPulseCounter2b, lbl_TestPulseCounter, txt_LRTestPulseCounter, true, true);
                CreateLocations(lbl_TestPulseCounter, lbl_MyBoardID, txt_LRMyBoardID, true, true);
                CreateLocations(lbl_MyBoardID, lbl_Version, txt_LRVersion, true, true);
                CreateLocations(lbl_Version, lbl_HVNumAve, txt_LWRHVNumAve, true, true);
                CreateLocations(lbl_HVNumAve, lbl_HVPeriodMan, txt_LWRHVPeriodMan, true, true);
                CreateLocations(lbl_HVPeriodMan, lbl_HVPeriodAuto, txt_LRHVPeriodAuto, true, true);
                CreateLocations(lbl_HVPeriodAuto, lbl_HVPulseWidth, txt_LWRHVPulseWidth, true, true);
                CreateLocations(lbl_HVPulseWidth, lbl_Temperature, txt_LRTemperature, true, true);
                CreateLocations(lbl_Temperature, lbl_TripXThreshold, txt_LWRTripXThreshold, true, true);
                CreateLocations(lbl_TripXThreshold, lbl_TripXComparators, txt_LRTripXComparators, true, true);
                CreateLocations(lbl_TripXComparators, lbl_ExtTriggFound, txt_LRExtTriggFound, true, true);                          // 08.08.2008
                CreateLocations(lbl_ExtTriggFound, lbl_ExtTriggRearm, txt_LWRExtTriggRearm, true, true);                            // 08.08.2008
                CreateLocations(lbl_ExtTriggRearm, lbl_DiscrimEnableMaskTrip0, txt_LWRDiscrimEnableMaskTrip0, true, true);          // 10.30.2008
                CreateLocations(lbl_DiscrimEnableMaskTrip0, lbl_DiscrimEnableMaskTrip1, txt_LWRDiscrimEnableMaskTrip1, true, true); // 10.30.2008
                CreateLocations(lbl_DiscrimEnableMaskTrip1, lbl_DiscrimEnableMaskTrip2, txt_LWRDiscrimEnableMaskTrip2, true, true); // 10.30.2008
                CreateLocations(lbl_DiscrimEnableMaskTrip2, lbl_DiscrimEnableMaskTrip3, txt_LWRDiscrimEnableMaskTrip3, true, true); // 10.30.2008
                CreateLocations(lbl_DiscrimEnableMaskTrip3, lbl_GateTimeStamp, txt_LRGateTimeStamp, true, true);                    // 12.22.2008
                CreateLocations(lbl_GateTimeStamp, lbl_StatusSCMDUnknown, txt_LRStatusSCMDUnknown, true, true);         // 11.13.2009
                CreateLocations(lbl_StatusSCMDUnknown, lbl_StatusFCMDUnknown, txt_LRStatusFCMDUnknown, true, true);     // 11.13.2009
                CreateLocations(lbl_StatusFCMDUnknown, lbl_StatusRXLock, txt_LRStatusRXLock, true, true);               // 11.13.2009
                CreateLocations(lbl_StatusRXLock, lbl_StatusTXSyncLock, txt_LRStatusTXSyncLock, true, true);            // 11.13.2009
            }
        }

        private void CreateLocations(Control OffsetControl, Control FirstControl, Control SecondControl,
            bool FirstControlVisible, bool SecondControlVisible)
        {
            FirstControl.Location = new Point(OffsetControl.Left, OffsetControl.Top + OffsetControl.Height + 5);
            SecondControl.Location = new Point(FirstControl.Left + FirstControl.Width + 5, FirstControl.Top);
            FirstControl.Visible = FirstControlVisible;
            SecondControl.Visible = SecondControlVisible;
        }

    }
}
