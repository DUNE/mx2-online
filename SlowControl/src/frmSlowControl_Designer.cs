namespace SlowControl
{
    partial class frmSlowControl
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.tabDescription = new System.Windows.Forms.TabPage();
            this.richTextBoxDescription = new System.Windows.Forms.RichTextBox();
            this.tabVME = new System.Windows.Forms.TabPage();
            this.groupBoxVME_WriteRead = new System.Windows.Forms.GroupBox();
            this.txt_VMEWriteData = new System.Windows.Forms.TextBox();
            this.btn_VMERead = new System.Windows.Forms.Button();
            this.label62 = new System.Windows.Forms.Label();
            this.btn_VMEWrite = new System.Windows.Forms.Button();
            this.label60 = new System.Windows.Forms.Label();
            this.txt_VMEReadAddress = new System.Windows.Forms.TextBox();
            this.txt_VMEWriteAddress = new System.Windows.Forms.TextBox();
            this.lbl_VMEReadData = new System.Windows.Forms.Label();
            this.tabCRIM = new System.Windows.Forms.TabPage();
            this.tabControlCRIMModules = new System.Windows.Forms.TabControl();
            this.tabCRIMTimingModule = new System.Windows.Forms.TabPage();
            this.lbl_CRIMTimingGateTimeRead = new System.Windows.Forms.Label();
            this.btn_CRIMTimingGateTimeRead = new System.Windows.Forms.Button();
            this.label68 = new System.Windows.Forms.Label();
            this.txt_CRIMTimingTestRegister = new System.Windows.Forms.TextBox();
            this.btn_CRIMTimingTestRegisterRead = new System.Windows.Forms.Button();
            this.btn_CRIMTimingTestRegisterWrite = new System.Windows.Forms.Button();
            this.label66 = new System.Windows.Forms.Label();
            this.label64 = new System.Windows.Forms.Label();
            this.chk_CRIMTimingCNTRSTEnableInINTMode = new System.Windows.Forms.CheckBox();
            this.btn_CRIMTimingSeqControlLatchReset = new System.Windows.Forms.Button();
            this.btn_CRIMTimingSS_CNTRST = new System.Windows.Forms.Button();
            this.btn_CRIMTimingSS_CNTRST_SGATE_TCALB = new System.Windows.Forms.Button();
            this.label49 = new System.Windows.Forms.Label();
            this.btn_CRIMTimingSendTCALB = new System.Windows.Forms.Button();
            this.cmb_CRIMTimingMode = new System.Windows.Forms.ComboBox();
            this.btn_CRIMTimingSendStartGate = new System.Windows.Forms.Button();
            this.label50 = new System.Windows.Forms.Label();
            this.btn_CRIMTimingSendStopGate = new System.Windows.Forms.Button();
            this.btn_CRIMTimingModeWrite = new System.Windows.Forms.Button();
            this.btn_CRIMTimingSendTrigger = new System.Windows.Forms.Button();
            this.btn_CRIMTimingModeRead = new System.Windows.Forms.Button();
            this.txt_CRIMTimingTCALB = new System.Windows.Forms.TextBox();
            this.cmb_CRIMTimingFrequency = new System.Windows.Forms.ComboBox();
            this.txt_CRIMTimingGateWidth = new System.Windows.Forms.TextBox();
            this.btn_CRIMTimingFrequencyWrite = new System.Windows.Forms.Button();
            this.btn_CRIMTimingTCALBRead = new System.Windows.Forms.Button();
            this.btn_CRIMTimingFrequencyRead = new System.Windows.Forms.Button();
            this.btn_CRIMTimingTCALBWrite = new System.Windows.Forms.Button();
            this.label52 = new System.Windows.Forms.Label();
            this.btn_CRIMTimingGateWidthRead = new System.Windows.Forms.Button();
            this.label51 = new System.Windows.Forms.Label();
            this.btn_CRIMTimingGateWidthWrite = new System.Windows.Forms.Button();
            this.tabCRIMDAQModule = new System.Windows.Forms.TabPage();
            this.groupBoxCRIM_MiscRegisters = new System.Windows.Forms.GroupBox();
            this.btn_CRIMDAQSendSyncRegister = new System.Windows.Forms.Button();
            this.btn_CRIMDAQResetFIFORegister = new System.Windows.Forms.Button();
            this.lbl_CRIMDAQReadTimingCommandRegister = new System.Windows.Forms.Label();
            this.btn_CRIMDAQReadTimingCommandRegister = new System.Windows.Forms.Button();
            this.groupBoxCRIM_DAQModeRegister = new System.Windows.Forms.GroupBox();
            this.chk_CRIMDAQModeRegisterSendEn = new System.Windows.Forms.CheckBox();
            this.chk_CRIMDAQModeRegisterFETriggEn = new System.Windows.Forms.CheckBox();
            this.btn_CRIMDAQModeRegisterRead = new System.Windows.Forms.Button();
            this.btn_CRIMDAQModeRegisterWrite = new System.Windows.Forms.Button();
            this.chk_CRIMDAQModeRegisterCRCEn = new System.Windows.Forms.CheckBox();
            this.chk_CRIMDAQModeRegisterRetransmitEn = new System.Windows.Forms.CheckBox();
            this.groupBoxCRIM_DPMRegister = new System.Windows.Forms.GroupBox();
            this.btn_CRIMDAQDPMRegisterResetPointer = new System.Windows.Forms.Button();
            this.btn_CRIMDAQDPMRegisterReadPointer = new System.Windows.Forms.Button();
            this.lbl_CRIMDAQDPMRegisterReadPointer = new System.Windows.Forms.Label();
            this.groupBoxCRIM_StatusRegister = new System.Windows.Forms.GroupBox();
            this.lbl_CRIMDAQStatusEncodedCmdRcv = new System.Windows.Forms.Label();
            this.label59 = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusFERebootRcv = new System.Windows.Forms.Label();
            this.label61 = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusUnusedBit11 = new System.Windows.Forms.Label();
            this.label63 = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusUnusedBit7 = new System.Windows.Forms.Label();
            this.label65 = new System.Windows.Forms.Label();
            this.btn_CRIMDAQStatusRegisterClear = new System.Windows.Forms.Button();
            this.btn_CRIMDAQStatusRegisterRead = new System.Windows.Forms.Button();
            this.lbl_CRIMDAQStatusRegisterRead = new System.Windows.Forms.Label();
            this.label67 = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusMsgSent = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusRFPresent = new System.Windows.Forms.Label();
            this.label70 = new System.Windows.Forms.Label();
            this.label71 = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusMsgRcv = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusDPMFull = new System.Windows.Forms.Label();
            this.label74 = new System.Windows.Forms.Label();
            this.label75 = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusCRCErr = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusFIFOFull = new System.Windows.Forms.Label();
            this.label78 = new System.Windows.Forms.Label();
            this.label79 = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusTimeoutErr = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusFIFONotEmpty = new System.Windows.Forms.Label();
            this.label82 = new System.Windows.Forms.Label();
            this.label83 = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusSerializerSync = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusTestPulseRcv = new System.Windows.Forms.Label();
            this.label88 = new System.Windows.Forms.Label();
            this.label87 = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusDeserializerLock = new System.Windows.Forms.Label();
            this.lbl_CRIMDAQStatusPLLLock = new System.Windows.Forms.Label();
            this.label90 = new System.Windows.Forms.Label();
            this.groupBoxCRIM_FrameRegisters = new System.Windows.Forms.GroupBox();
            this.btn_CRIMDAQFrameFIFORegisterWrite = new System.Windows.Forms.Button();
            this.rtb_CRIMDAQFrameReadDPMBytes = new System.Windows.Forms.RichTextBox();
            this.txt_CRIMDAQFrameReadDPMBytes = new System.Windows.Forms.TextBox();
            this.txt_CRIMDAQFrameFIFORegisterAppendMessage = new System.Windows.Forms.TextBox();
            this.btn_CRIMDAQFrameReadDPMBytes = new System.Windows.Forms.Button();
            this.btn_CRIMDAQFrameSendRegister = new System.Windows.Forms.Button();
            this.btn_CRIMDAQFrameFIFORegisterAppendMessage = new System.Windows.Forms.Button();
            this.tabCRIMInterrupterModule = new System.Windows.Forms.TabPage();
            this.groupBoxCRIM_Interrupter = new System.Windows.Forms.GroupBox();
            this.btn_CRIMInterrupterConfigRead = new System.Windows.Forms.Button();
            this.txt_CRIMInterrupterLevels = new System.Windows.Forms.TextBox();
            this.label46 = new System.Windows.Forms.Label();
            this.label94 = new System.Windows.Forms.Label();
            this.label53 = new System.Windows.Forms.Label();
            this.btn_CRIMInterrupterConfigWrite = new System.Windows.Forms.Button();
            this.btn_CRIMInterrupterMaskWrite = new System.Windows.Forms.Button();
            this.label58 = new System.Windows.Forms.Label();
            this.txt_CRIMInterrupterVectInp5 = new System.Windows.Forms.TextBox();
            this.label97 = new System.Windows.Forms.Label();
            this.txt_CRIMInterrupterMask = new System.Windows.Forms.TextBox();
            this.label55 = new System.Windows.Forms.Label();
            this.btn_CRIMInterrupterClearInterrupts = new System.Windows.Forms.Button();
            this.txt_CRIMInterrupterVectInp2 = new System.Windows.Forms.TextBox();
            this.txt_CRIMInterrupterStatus = new System.Windows.Forms.TextBox();
            this.btn_CRIMInterrupterMaskRead = new System.Windows.Forms.Button();
            this.txt_CRIMInterrupterVectInp6 = new System.Windows.Forms.TextBox();
            this.label56 = new System.Windows.Forms.Label();
            this.txt_CRIMInterrupterVectInp3 = new System.Windows.Forms.TextBox();
            this.txt_CRIMInterrupterVectInp0 = new System.Windows.Forms.TextBox();
            this.label54 = new System.Windows.Forms.Label();
            this.label95 = new System.Windows.Forms.Label();
            this.chk_CRIMInterrupterGIE = new System.Windows.Forms.CheckBox();
            this.label93 = new System.Windows.Forms.Label();
            this.label96 = new System.Windows.Forms.Label();
            this.btn_CRIMInterrupterStatusWrite = new System.Windows.Forms.Button();
            this.btn_CRIMInterrupterVectInpWrite = new System.Windows.Forms.Button();
            this.txt_CRIMInterrupterVectInp4 = new System.Windows.Forms.TextBox();
            this.label92 = new System.Windows.Forms.Label();
            this.btn_CRIMInterrupterVectInpRead = new System.Windows.Forms.Button();
            this.txt_CRIMInterrupterVectInp7 = new System.Windows.Forms.TextBox();
            this.txt_CRIMInterrupterVectInp1 = new System.Windows.Forms.TextBox();
            this.btn_CRIMInterrupterStatusRead = new System.Windows.Forms.Button();
            this.tabCRIMFELoopQuery = new System.Windows.Forms.TabPage();
            this.chk_CRIMFELoopQueryMatch = new System.Windows.Forms.CheckBox();
            this.txt_CRIMFELoopQueryNTimes = new System.Windows.Forms.TextBox();
            this.label48 = new System.Windows.Forms.Label();
            this.txt_CRIMFELoopQueryCrocBaseAddr = new System.Windows.Forms.TextBox();
            this.label57 = new System.Windows.Forms.Label();
            this.txt_CRIMFELoopQueryMatch = new System.Windows.Forms.TextBox();
            this.rtb_CRIMFELoopQueryDisplay = new System.Windows.Forms.RichTextBox();
            this.btn_CRIMFELoopQueryDoQuery = new System.Windows.Forms.Button();
            this.btn_CRIMFELoopQueryConfigure = new System.Windows.Forms.Button();
            this.lblCRIM_CRIMID = new System.Windows.Forms.Label();
            this.label47 = new System.Windows.Forms.Label();
            this.btn_CRIMAdvancedGUI = new System.Windows.Forms.Button();
            this.btn_CRIMReportGateAlignmentsAllCROCs = new System.Windows.Forms.Button();
            this.tabCROC = new System.Windows.Forms.TabPage();
            this.groupBoxCROC_FEBGateDelays = new System.Windows.Forms.GroupBox();
            this.btn_CROCReportGateAlignmentsAllCROCsAndChains = new System.Windows.Forms.Button();
            this.txt_CROCGateDelayLoopChannel = new System.Windows.Forms.TextBox();
            this.txt_CROCGateDelayLoopGateStartValue = new System.Windows.Forms.TextBox();
            this.label45 = new System.Windows.Forms.Label();
            this.txt_CROCGateDelayLoopLoadTimerValue = new System.Windows.Forms.TextBox();
            this.label31 = new System.Windows.Forms.Label();
            this.txt_CROCGateDelayLoopN = new System.Windows.Forms.TextBox();
            this.label41 = new System.Windows.Forms.Label();
            this.btn_CROCReportGateAlignments = new System.Windows.Forms.Button();
            this.groupBoxCROC_LoopDelay = new System.Windows.Forms.GroupBox();
            this.btn_CROCLoopDelayClear = new System.Windows.Forms.Button();
            this.lbl_CROCLoopDelayCh4 = new System.Windows.Forms.Label();
            this.label43 = new System.Windows.Forms.Label();
            this.lbl_CROCLoopDelayCh3 = new System.Windows.Forms.Label();
            this.label39 = new System.Windows.Forms.Label();
            this.lbl_CROCLoopDelayCh2 = new System.Windows.Forms.Label();
            this.label35 = new System.Windows.Forms.Label();
            this.lbl_CROCLoopDelayCh1 = new System.Windows.Forms.Label();
            this.label23 = new System.Windows.Forms.Label();
            this.btn_CROCLoopDelayRead = new System.Windows.Forms.Button();
            this.groupBoxCROC_FastCommand = new System.Windows.Forms.GroupBox();
            this.cmb_CROCFastCommand = new System.Windows.Forms.ComboBox();
            this.btn_CROCFastCommand = new System.Windows.Forms.Button();
            this.groupBoxCROC_ResetTPMaskReg = new System.Windows.Forms.GroupBox();
            this.btn_CROCTPSend = new System.Windows.Forms.Button();
            this.btn_CROCResetSend = new System.Windows.Forms.Button();
            this.btn_CROCResetTPWrite = new System.Windows.Forms.Button();
            this.lbl_CROCResetTPRead = new System.Windows.Forms.Label();
            this.btn_CROCResetTPRead = new System.Windows.Forms.Button();
            this.chk_CROCTPulseCh4 = new System.Windows.Forms.CheckBox();
            this.chk_CROCResetCh4 = new System.Windows.Forms.CheckBox();
            this.chk_CROCTPulseCh3 = new System.Windows.Forms.CheckBox();
            this.chk_CROCResetCh3 = new System.Windows.Forms.CheckBox();
            this.chk_CROCTPulseCh2 = new System.Windows.Forms.CheckBox();
            this.chk_CROCResetCh2 = new System.Windows.Forms.CheckBox();
            this.chk_CROCTPulseCh1 = new System.Windows.Forms.CheckBox();
            this.chk_CROCResetCh1 = new System.Windows.Forms.CheckBox();
            this.groupBoxCROC_TimingSetup = new System.Windows.Forms.GroupBox();
            this.lbl_CROCTimingSetupRead = new System.Windows.Forms.Label();
            this.label20 = new System.Windows.Forms.Label();
            this.btn_CROCTimingSetupRead = new System.Windows.Forms.Button();
            this.txt_CROCTimingSetupTPDelay = new System.Windows.Forms.TextBox();
            this.cmb_CROCTimingSetupTPDelay = new System.Windows.Forms.ComboBox();
            this.cmb_CROCTimingSetupClock = new System.Windows.Forms.ComboBox();
            this.groupBoxCROC_FLASH = new System.Windows.Forms.GroupBox();
            this.btn_CROCWriteFileToSPI = new System.Windows.Forms.Button();
            this.btn_CROCReBootFEs = new System.Windows.Forms.Button();
            this.btn_CROCAdvancedGUI = new System.Windows.Forms.Button();
            this.lblCROC_CROCID = new System.Windows.Forms.Label();
            this.label12 = new System.Windows.Forms.Label();
            this.label15 = new System.Windows.Forms.Label();
            this.label17 = new System.Windows.Forms.Label();
            this.label18 = new System.Windows.Forms.Label();
            this.label19 = new System.Windows.Forms.Label();
            this.tabCH = new System.Windows.Forms.TabPage();
            this.groupBoxCH_DEBUG = new System.Windows.Forms.GroupBox();
            this.btn_CHDebugUpdatePattern = new System.Windows.Forms.Button();
            this.cmb_CHDebugBroadcastCMD = new System.Windows.Forms.ComboBox();
            this.cmb_CHDebugFEID = new System.Windows.Forms.ComboBox();
            this.cmb_CHDebugFunctionID = new System.Windows.Forms.ComboBox();
            this.cmb_CHDebugDeviceID = new System.Windows.Forms.ComboBox();
            this.cmb_CHDebugDirection = new System.Windows.Forms.ComboBox();
            this.txt_CHDebugFrameStatusID = new System.Windows.Forms.TextBox();
            this.txt_CHDebugFrameIDByte0 = new System.Windows.Forms.TextBox();
            this.label85 = new System.Windows.Forms.Label();
            this.label84 = new System.Windows.Forms.Label();
            this.label81 = new System.Windows.Forms.Label();
            this.label80 = new System.Windows.Forms.Label();
            this.txt_CHDebugFrameIDByte1 = new System.Windows.Forms.TextBox();
            this.label77 = new System.Windows.Forms.Label();
            this.label76 = new System.Windows.Forms.Label();
            this.label69 = new System.Windows.Forms.Label();
            this.txt_CHDebugFillDPMPattern = new System.Windows.Forms.TextBox();
            this.txt_CHDebugFillDPMPRepeat = new System.Windows.Forms.TextBox();
            this.btn_CHDebugFillDPM = new System.Windows.Forms.Button();
            this.rtb_CHDebug = new System.Windows.Forms.RichTextBox();
            this.txt_CHDebugNTests = new System.Windows.Forms.TextBox();
            this.label73 = new System.Windows.Forms.Label();
            this.btn_CHDebugInitializeCROCs = new System.Windows.Forms.Button();
            this.groupBoxCH_Frame = new System.Windows.Forms.GroupBox();
            this.btn_CHFIFOWriteMessage = new System.Windows.Forms.Button();
            this.rtb_CHDPMRead = new System.Windows.Forms.RichTextBox();
            this.txt_CHDPMReadLength = new System.Windows.Forms.TextBox();
            this.txt_CHFIFORegWrite = new System.Windows.Forms.TextBox();
            this.btn_CHDPMRead = new System.Windows.Forms.Button();
            this.btn_CHSendMessage = new System.Windows.Forms.Button();
            this.btn_CHFIFOAppendMessage = new System.Windows.Forms.Button();
            this.groupBoxCH_StatusRegister = new System.Windows.Forms.GroupBox();
            this.lblCH_StatUnusedBit15 = new System.Windows.Forms.Label();
            this.label33 = new System.Windows.Forms.Label();
            this.lblCH_StatUnusedBit14 = new System.Windows.Forms.Label();
            this.label29 = new System.Windows.Forms.Label();
            this.lblCH_StatUnusedBit11 = new System.Windows.Forms.Label();
            this.label25 = new System.Windows.Forms.Label();
            this.lblCH_StatUnusedBit7 = new System.Windows.Forms.Label();
            this.label21 = new System.Windows.Forms.Label();
            this.btn_CHStatusRegClear = new System.Windows.Forms.Button();
            this.btn_CHStatusRegRead = new System.Windows.Forms.Button();
            this.lblCH_StatusValue = new System.Windows.Forms.Label();
            this.label22 = new System.Windows.Forms.Label();
            this.lblCH_StatMsgSent = new System.Windows.Forms.Label();
            this.lblCH_StatRFPresent = new System.Windows.Forms.Label();
            this.label24 = new System.Windows.Forms.Label();
            this.label38 = new System.Windows.Forms.Label();
            this.lblCH_StatMsgReceived = new System.Windows.Forms.Label();
            this.lblCH_StatDPMFull = new System.Windows.Forms.Label();
            this.label26 = new System.Windows.Forms.Label();
            this.label40 = new System.Windows.Forms.Label();
            this.lblCH_StatCRCError = new System.Windows.Forms.Label();
            this.lblCH_StatFIFOFull = new System.Windows.Forms.Label();
            this.label28 = new System.Windows.Forms.Label();
            this.label42 = new System.Windows.Forms.Label();
            this.lblCH_StatTimeoutError = new System.Windows.Forms.Label();
            this.lblCH_StatFIFONotEmpty = new System.Windows.Forms.Label();
            this.label36 = new System.Windows.Forms.Label();
            this.label44 = new System.Windows.Forms.Label();
            this.lblCH_StatSerializerSYNC = new System.Windows.Forms.Label();
            this.lblCH_StatPLL1LOCK = new System.Windows.Forms.Label();
            this.label34 = new System.Windows.Forms.Label();
            this.label30 = new System.Windows.Forms.Label();
            this.lblCH_StatDeserializerLOCK = new System.Windows.Forms.Label();
            this.lblCH_StatPLL0LOCK = new System.Windows.Forms.Label();
            this.label32 = new System.Windows.Forms.Label();
            this.groupBoxCH_FLASH = new System.Windows.Forms.GroupBox();
            this.btn_CHWriteFileToSPI = new System.Windows.Forms.Button();
            this.btn_CHReBootFEs = new System.Windows.Forms.Button();
            this.groupBoxCH_DPM = new System.Windows.Forms.GroupBox();
            this.btn_CHDPMPointerReset = new System.Windows.Forms.Button();
            this.btn_CHDPMPointerRead = new System.Windows.Forms.Button();
            this.lblCH_DPMPointerValue = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.btn_CHAdvancedGUI = new System.Windows.Forms.Button();
            this.lblCH_CROCID = new System.Windows.Forms.Label();
            this.label10 = new System.Windows.Forms.Label();
            this.lblCH_CHID = new System.Windows.Forms.Label();
            this.label14 = new System.Windows.Forms.Label();
            this.label16 = new System.Windows.Forms.Label();
            this.tabFE = new System.Windows.Forms.TabPage();
            this.tabFPGARegs = new System.Windows.Forms.TabPage();
            this.btn_AllFEsFPGARegWrite = new System.Windows.Forms.Button();
            this.btn_FPGAAdvancedGUI = new System.Windows.Forms.Button();
            this.lblFPGA_CROCID = new System.Windows.Forms.Label();
            this.label7 = new System.Windows.Forms.Label();
            this.lblFPGA_CHID = new System.Windows.Forms.Label();
            this.label5 = new System.Windows.Forms.Label();
            this.lblFPGA_FEID = new System.Windows.Forms.Label();
            this.btn_FPGARegRead = new System.Windows.Forms.Button();
            this.btn_FPGARegWrite = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.fpgaDevRegControl1 = new MinervaUserControls.FPGADevRegControl();
            this.tabTRIPRegs = new System.Windows.Forms.TabPage();
            this.btn_AllFEsTRIPRegWrite = new System.Windows.Forms.Button();
            this.cmb_TripID = new System.Windows.Forms.ComboBox();
            this.btn_TRIPAdvancedGUI = new System.Windows.Forms.Button();
            this.lblTRIP_CROCID = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.lblTRIP_CHID = new System.Windows.Forms.Label();
            this.label6 = new System.Windows.Forms.Label();
            this.lblTRIP_FEID = new System.Windows.Forms.Label();
            this.btn_TRIPRegRead = new System.Windows.Forms.Button();
            this.btn_TRIPRegWrite = new System.Windows.Forms.Button();
            this.label9 = new System.Windows.Forms.Label();
            this.tripDevRegControl1 = new MinervaUserControls.TripDevRegControl();
            this.tabFLASHPages = new System.Windows.Forms.TabPage();
            this.btn_FLASHWriteFileToSPI = new System.Windows.Forms.Button();
            this.btn_FLASHAdvancedGUI = new System.Windows.Forms.Button();
            this.lblFLASH_CROCID = new System.Windows.Forms.Label();
            this.label8 = new System.Windows.Forms.Label();
            this.lblFLASH_CHID = new System.Windows.Forms.Label();
            this.label11 = new System.Windows.Forms.Label();
            this.lblFLASH_FEID = new System.Windows.Forms.Label();
            this.label13 = new System.Windows.Forms.Label();
            this.btn_FLASHReadSPIToFile = new System.Windows.Forms.Button();
            this.tabReadHV = new System.Windows.Forms.TabPage();
            this.richTextBoxHVRead = new System.Windows.Forms.RichTextBox();
            this.btnMonitorHV = new System.Windows.Forms.Button();
            this.label27 = new System.Windows.Forms.Label();
            this.textBoxMonitorTimer = new System.Windows.Forms.TextBox();
            this.btnSwitchToAuto = new System.Windows.Forms.Button();
            this.textBoxADCThreshold = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.btnReadHV = new System.Windows.Forms.Button();
            this.tabLIBox = new System.Windows.Forms.TabPage();
            this.btn_LIBoxAdvancedGUI = new System.Windows.Forms.Button();
            this.groupBoxLIBox_LICommands = new System.Windows.Forms.GroupBox();
            this.groupBoxLIBox_LICommandsHardcoded = new System.Windows.Forms.GroupBox();
            this.btn_LIBoxHardcodedInitALLSlots = new System.Windows.Forms.Button();
            this.btn_LIBoxHardcoded_X = new System.Windows.Forms.Button();
            this.btn_LIBoxHardcodedMaxPE = new System.Windows.Forms.Button();
            this.btn_LIBoxHardcodedOnePE = new System.Windows.Forms.Button();
            this.btn_LIBoxHardcodedZeroPE = new System.Windows.Forms.Button();
            this.cmb_LIBoxHardcodedLEDSlot = new System.Windows.Forms.ComboBox();
            this.btn_LIBoxHardcodedInitLEDSlot = new System.Windows.Forms.Button();
            this.btn_LIBoxIsActive = new System.Windows.Forms.Button();
            this.cmb_LIBoxLEDPulseWidth = new System.Windows.Forms.ComboBox();
            this.cmb_LIBoxLEDSlot = new System.Windows.Forms.ComboBox();
            this.btn_LIBoxSendFile = new System.Windows.Forms.Button();
            this.richTextBoxLIBox = new System.Windows.Forms.RichTextBox();
            this.txt_LIBoxLEDTriggerRate = new System.Windows.Forms.TextBox();
            this.btn_LIBoxLEDTriggerRate = new System.Windows.Forms.Button();
            this.txt_LIBoxLEDPulseHeight = new System.Windows.Forms.TextBox();
            this.btn_LIBoxLEDPulseHeight = new System.Windows.Forms.Button();
            this.btn_LIBoxTriggerExternal = new System.Windows.Forms.Button();
            this.btn_LIBoxTriggerInternal = new System.Windows.Forms.Button();
            this.btn_LIBoxLEDPulseWidth = new System.Windows.Forms.Button();
            this.btn_LIBoxLEDSlot = new System.Windows.Forms.Button();
            this.btn_LIBoxInitBox = new System.Windows.Forms.Button();
            this.groupBoxLIBox_RS232Commands = new System.Windows.Forms.GroupBox();
            this.btn_LIBoxClearRX = new System.Windows.Forms.Button();
            this.btn_LIBoxClearTX = new System.Windows.Forms.Button();
            this.richTextBoxLIWrite = new System.Windows.Forms.RichTextBox();
            this.btn_LIBoxRead = new System.Windows.Forms.Button();
            this.richTextBoxLIRead = new System.Windows.Forms.RichTextBox();
            this.btn_LIBoxWrite = new System.Windows.Forms.Button();
            this.groupBoxLIBox_RS232Settings = new System.Windows.Forms.GroupBox();
            this.txt_LIBoxReadTimeout = new System.Windows.Forms.TextBox();
            this.txt_LIBoxWriteTimeout = new System.Windows.Forms.TextBox();
            this.label37 = new System.Windows.Forms.Label();
            this.cmb_LIBoxHandshake = new System.Windows.Forms.ComboBox();
            this.cmb_LIBoxStopBits = new System.Windows.Forms.ComboBox();
            this.cmb_LIBoxDataBits = new System.Windows.Forms.ComboBox();
            this.cmb_LIBoxParity = new System.Windows.Forms.ComboBox();
            this.cmb_LIBoxBaudRate = new System.Windows.Forms.ComboBox();
            this.cmb_LIBoxPortName = new System.Windows.Forms.ComboBox();
            this.btn_LIBoxFindSerialPorts = new System.Windows.Forms.Button();
            this.btn_LIBoxConfigureSerialPort = new System.Windows.Forms.Button();
            this.tabV1720 = new System.Windows.Forms.TabPage();
            this.btn_V1720ReadAllRegisters = new System.Windows.Forms.Button();
            this.chk_V1720PrintEventStat = new System.Windows.Forms.CheckBox();
            this.chk_V1720PrintEventData = new System.Windows.Forms.CheckBox();
            this.txt_V1720TakeNEvents = new System.Windows.Forms.TextBox();
            this.btn_V1720TakeNEvents = new System.Windows.Forms.Button();
            this.richTextBoxV1720 = new System.Windows.Forms.RichTextBox();
            this.lblV1720_V1720ID = new System.Windows.Forms.Label();
            this.label72 = new System.Windows.Forms.Label();
            this.btn_V1720AdvancedGUI = new System.Windows.Forms.Button();
            this.btn_V1720LoadConfigFile = new System.Windows.Forms.Button();
            this.errMain = new System.Windows.Forms.ErrorProvider(this.components);
            this.treeView1 = new System.Windows.Forms.TreeView();
            this.contextMenuStrip1 = new System.Windows.Forms.ContextMenuStrip(this.components);
            this.toolStripMenuItemUpdateStatusString = new System.Windows.Forms.ToolStripMenuItem();
            this.toolStripSeparator2 = new System.Windows.Forms.ToolStripSeparator();
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.toolStripMenuItemFile = new System.Windows.Forms.ToolStripMenuItem();
            this.loadHardwareToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.loadConfigXmlToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.saveConfigXmlToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.writeXmlToHardwareToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.showToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.expandAllToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.collapseAllToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.toolStripSeparator1 = new System.Windows.Forms.ToolStripSeparator();
            this.redPathsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.bluePathsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.greenPathsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.actionsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.readVoltagesToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.zeroHVAllToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.monitorVoltagesToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.lightInjectionToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.statusStrip1 = new System.Windows.Forms.StatusStrip();
            this.prgStatus = new System.Windows.Forms.ToolStripProgressBar();
            this.lblStatus = new System.Windows.Forms.ToolStripStatusLabel();
            this.backgroundWorker1 = new System.ComponentModel.BackgroundWorker();
            this.timerMonitorHV = new System.Windows.Forms.Timer(this.components);
            this.tabControl1.SuspendLayout();
            this.tabDescription.SuspendLayout();
            this.tabVME.SuspendLayout();
            this.groupBoxVME_WriteRead.SuspendLayout();
            this.tabCRIM.SuspendLayout();
            this.tabControlCRIMModules.SuspendLayout();
            this.tabCRIMTimingModule.SuspendLayout();
            this.tabCRIMDAQModule.SuspendLayout();
            this.groupBoxCRIM_MiscRegisters.SuspendLayout();
            this.groupBoxCRIM_DAQModeRegister.SuspendLayout();
            this.groupBoxCRIM_DPMRegister.SuspendLayout();
            this.groupBoxCRIM_StatusRegister.SuspendLayout();
            this.groupBoxCRIM_FrameRegisters.SuspendLayout();
            this.tabCRIMInterrupterModule.SuspendLayout();
            this.groupBoxCRIM_Interrupter.SuspendLayout();
            this.tabCRIMFELoopQuery.SuspendLayout();
            this.tabCROC.SuspendLayout();
            this.groupBoxCROC_FEBGateDelays.SuspendLayout();
            this.groupBoxCROC_LoopDelay.SuspendLayout();
            this.groupBoxCROC_FastCommand.SuspendLayout();
            this.groupBoxCROC_ResetTPMaskReg.SuspendLayout();
            this.groupBoxCROC_TimingSetup.SuspendLayout();
            this.groupBoxCROC_FLASH.SuspendLayout();
            this.tabCH.SuspendLayout();
            this.groupBoxCH_DEBUG.SuspendLayout();
            this.groupBoxCH_Frame.SuspendLayout();
            this.groupBoxCH_StatusRegister.SuspendLayout();
            this.groupBoxCH_FLASH.SuspendLayout();
            this.groupBoxCH_DPM.SuspendLayout();
            this.tabFPGARegs.SuspendLayout();
            this.tabTRIPRegs.SuspendLayout();
            this.tabFLASHPages.SuspendLayout();
            this.tabReadHV.SuspendLayout();
            this.tabLIBox.SuspendLayout();
            this.groupBoxLIBox_LICommands.SuspendLayout();
            this.groupBoxLIBox_LICommandsHardcoded.SuspendLayout();
            this.groupBoxLIBox_RS232Commands.SuspendLayout();
            this.groupBoxLIBox_RS232Settings.SuspendLayout();
            this.tabV1720.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.errMain)).BeginInit();
            this.contextMenuStrip1.SuspendLayout();
            this.menuStrip1.SuspendLayout();
            this.statusStrip1.SuspendLayout();
            this.SuspendLayout();
            // 
            // tabControl1
            // 
            this.tabControl1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.tabControl1.Controls.Add(this.tabDescription);
            this.tabControl1.Controls.Add(this.tabVME);
            this.tabControl1.Controls.Add(this.tabCRIM);
            this.tabControl1.Controls.Add(this.tabCROC);
            this.tabControl1.Controls.Add(this.tabCH);
            this.tabControl1.Controls.Add(this.tabFE);
            this.tabControl1.Controls.Add(this.tabFPGARegs);
            this.tabControl1.Controls.Add(this.tabTRIPRegs);
            this.tabControl1.Controls.Add(this.tabFLASHPages);
            this.tabControl1.Controls.Add(this.tabReadHV);
            this.tabControl1.Controls.Add(this.tabLIBox);
            this.tabControl1.Controls.Add(this.tabV1720);
            this.tabControl1.Location = new System.Drawing.Point(211, 27);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(907, 528);
            this.tabControl1.TabIndex = 0;
            // 
            // tabDescription
            // 
            this.tabDescription.Controls.Add(this.richTextBoxDescription);
            this.tabDescription.Location = new System.Drawing.Point(4, 22);
            this.tabDescription.Name = "tabDescription";
            this.tabDescription.Padding = new System.Windows.Forms.Padding(3);
            this.tabDescription.Size = new System.Drawing.Size(899, 502);
            this.tabDescription.TabIndex = 3;
            this.tabDescription.Text = "Description";
            this.tabDescription.UseVisualStyleBackColor = true;
            // 
            // richTextBoxDescription
            // 
            this.richTextBoxDescription.AutoWordSelection = true;
            this.richTextBoxDescription.BackColor = System.Drawing.Color.LightSteelBlue;
            this.richTextBoxDescription.Dock = System.Windows.Forms.DockStyle.Fill;
            this.richTextBoxDescription.Location = new System.Drawing.Point(3, 3);
            this.richTextBoxDescription.Name = "richTextBoxDescription";
            this.richTextBoxDescription.Size = new System.Drawing.Size(893, 496);
            this.richTextBoxDescription.TabIndex = 0;
            this.richTextBoxDescription.Text = "";
            // 
            // tabVME
            // 
            this.tabVME.Controls.Add(this.groupBoxVME_WriteRead);
            this.tabVME.Location = new System.Drawing.Point(4, 22);
            this.tabVME.Name = "tabVME";
            this.tabVME.Size = new System.Drawing.Size(899, 502);
            this.tabVME.TabIndex = 10;
            this.tabVME.Text = "VME";
            this.tabVME.UseVisualStyleBackColor = true;
            // 
            // groupBoxVME_WriteRead
            // 
            this.groupBoxVME_WriteRead.Controls.Add(this.txt_VMEWriteData);
            this.groupBoxVME_WriteRead.Controls.Add(this.btn_VMERead);
            this.groupBoxVME_WriteRead.Controls.Add(this.label62);
            this.groupBoxVME_WriteRead.Controls.Add(this.btn_VMEWrite);
            this.groupBoxVME_WriteRead.Controls.Add(this.label60);
            this.groupBoxVME_WriteRead.Controls.Add(this.txt_VMEReadAddress);
            this.groupBoxVME_WriteRead.Controls.Add(this.txt_VMEWriteAddress);
            this.groupBoxVME_WriteRead.Controls.Add(this.lbl_VMEReadData);
            this.groupBoxVME_WriteRead.Location = new System.Drawing.Point(9, 6);
            this.groupBoxVME_WriteRead.Name = "groupBoxVME_WriteRead";
            this.groupBoxVME_WriteRead.Size = new System.Drawing.Size(173, 86);
            this.groupBoxVME_WriteRead.TabIndex = 109;
            this.groupBoxVME_WriteRead.TabStop = false;
            this.groupBoxVME_WriteRead.Text = "Write Read (hex)";
            // 
            // txt_VMEWriteData
            // 
            this.txt_VMEWriteData.Location = new System.Drawing.Point(114, 60);
            this.txt_VMEWriteData.Name = "txt_VMEWriteData";
            this.txt_VMEWriteData.Size = new System.Drawing.Size(50, 20);
            this.txt_VMEWriteData.TabIndex = 109;
            this.txt_VMEWriteData.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // btn_VMERead
            // 
            this.btn_VMERead.BackColor = System.Drawing.Color.Coral;
            this.btn_VMERead.Location = new System.Drawing.Point(6, 33);
            this.btn_VMERead.Name = "btn_VMERead";
            this.btn_VMERead.Size = new System.Drawing.Size(46, 20);
            this.btn_VMERead.TabIndex = 101;
            this.btn_VMERead.Text = "Read";
            this.btn_VMERead.UseVisualStyleBackColor = false;
            this.btn_VMERead.Click += new System.EventHandler(this.btn_VMERead_Click);
            // 
            // label62
            // 
            this.label62.BackColor = System.Drawing.Color.Coral;
            this.label62.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label62.Location = new System.Drawing.Point(114, 15);
            this.label62.Name = "label62";
            this.label62.Size = new System.Drawing.Size(50, 15);
            this.label62.TabIndex = 108;
            this.label62.Text = "Data";
            this.label62.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // btn_VMEWrite
            // 
            this.btn_VMEWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_VMEWrite.Location = new System.Drawing.Point(6, 59);
            this.btn_VMEWrite.Name = "btn_VMEWrite";
            this.btn_VMEWrite.Size = new System.Drawing.Size(46, 20);
            this.btn_VMEWrite.TabIndex = 102;
            this.btn_VMEWrite.Text = "Write";
            this.btn_VMEWrite.UseVisualStyleBackColor = false;
            this.btn_VMEWrite.Click += new System.EventHandler(this.btn_VMEWrite_Click);
            // 
            // label60
            // 
            this.label60.BackColor = System.Drawing.Color.Coral;
            this.label60.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label60.Location = new System.Drawing.Point(58, 15);
            this.label60.Name = "label60";
            this.label60.Size = new System.Drawing.Size(50, 15);
            this.label60.TabIndex = 107;
            this.label60.Text = "Addr";
            this.label60.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // txt_VMEReadAddress
            // 
            this.txt_VMEReadAddress.Location = new System.Drawing.Point(58, 33);
            this.txt_VMEReadAddress.Name = "txt_VMEReadAddress";
            this.txt_VMEReadAddress.Size = new System.Drawing.Size(50, 20);
            this.txt_VMEReadAddress.TabIndex = 103;
            // 
            // txt_VMEWriteAddress
            // 
            this.txt_VMEWriteAddress.Location = new System.Drawing.Point(58, 59);
            this.txt_VMEWriteAddress.Name = "txt_VMEWriteAddress";
            this.txt_VMEWriteAddress.Size = new System.Drawing.Size(50, 20);
            this.txt_VMEWriteAddress.TabIndex = 104;
            // 
            // lbl_VMEReadData
            // 
            this.lbl_VMEReadData.BackColor = System.Drawing.Color.White;
            this.lbl_VMEReadData.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_VMEReadData.Location = new System.Drawing.Point(114, 33);
            this.lbl_VMEReadData.Name = "lbl_VMEReadData";
            this.lbl_VMEReadData.RightToLeft = System.Windows.Forms.RightToLeft.Yes;
            this.lbl_VMEReadData.Size = new System.Drawing.Size(50, 20);
            this.lbl_VMEReadData.TabIndex = 105;
            this.lbl_VMEReadData.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // tabCRIM
            // 
            this.tabCRIM.Controls.Add(this.tabControlCRIMModules);
            this.tabCRIM.Controls.Add(this.lblCRIM_CRIMID);
            this.tabCRIM.Controls.Add(this.label47);
            this.tabCRIM.Controls.Add(this.btn_CRIMAdvancedGUI);
            this.tabCRIM.Controls.Add(this.btn_CRIMReportGateAlignmentsAllCROCs);
            this.tabCRIM.Location = new System.Drawing.Point(4, 22);
            this.tabCRIM.Name = "tabCRIM";
            this.tabCRIM.Size = new System.Drawing.Size(899, 502);
            this.tabCRIM.TabIndex = 4;
            this.tabCRIM.Text = "CRIM";
            this.tabCRIM.UseVisualStyleBackColor = true;
            // 
            // tabControlCRIMModules
            // 
            this.tabControlCRIMModules.Controls.Add(this.tabCRIMTimingModule);
            this.tabControlCRIMModules.Controls.Add(this.tabCRIMDAQModule);
            this.tabControlCRIMModules.Controls.Add(this.tabCRIMInterrupterModule);
            this.tabControlCRIMModules.Controls.Add(this.tabCRIMFELoopQuery);
            this.tabControlCRIMModules.Location = new System.Drawing.Point(3, 46);
            this.tabControlCRIMModules.Name = "tabControlCRIMModules";
            this.tabControlCRIMModules.SelectedIndex = 0;
            this.tabControlCRIMModules.Size = new System.Drawing.Size(381, 458);
            this.tabControlCRIMModules.TabIndex = 96;
            this.tabControlCRIMModules.Visible = false;
            // 
            // tabCRIMTimingModule
            // 
            this.tabCRIMTimingModule.Controls.Add(this.lbl_CRIMTimingGateTimeRead);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingGateTimeRead);
            this.tabCRIMTimingModule.Controls.Add(this.label68);
            this.tabCRIMTimingModule.Controls.Add(this.txt_CRIMTimingTestRegister);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingTestRegisterRead);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingTestRegisterWrite);
            this.tabCRIMTimingModule.Controls.Add(this.label66);
            this.tabCRIMTimingModule.Controls.Add(this.label64);
            this.tabCRIMTimingModule.Controls.Add(this.chk_CRIMTimingCNTRSTEnableInINTMode);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingSeqControlLatchReset);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingSS_CNTRST);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingSS_CNTRST_SGATE_TCALB);
            this.tabCRIMTimingModule.Controls.Add(this.label49);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingSendTCALB);
            this.tabCRIMTimingModule.Controls.Add(this.cmb_CRIMTimingMode);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingSendStartGate);
            this.tabCRIMTimingModule.Controls.Add(this.label50);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingSendStopGate);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingModeWrite);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingSendTrigger);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingModeRead);
            this.tabCRIMTimingModule.Controls.Add(this.txt_CRIMTimingTCALB);
            this.tabCRIMTimingModule.Controls.Add(this.cmb_CRIMTimingFrequency);
            this.tabCRIMTimingModule.Controls.Add(this.txt_CRIMTimingGateWidth);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingFrequencyWrite);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingTCALBRead);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingFrequencyRead);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingTCALBWrite);
            this.tabCRIMTimingModule.Controls.Add(this.label52);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingGateWidthRead);
            this.tabCRIMTimingModule.Controls.Add(this.label51);
            this.tabCRIMTimingModule.Controls.Add(this.btn_CRIMTimingGateWidthWrite);
            this.tabCRIMTimingModule.Location = new System.Drawing.Point(4, 22);
            this.tabCRIMTimingModule.Name = "tabCRIMTimingModule";
            this.tabCRIMTimingModule.Padding = new System.Windows.Forms.Padding(3);
            this.tabCRIMTimingModule.Size = new System.Drawing.Size(373, 432);
            this.tabCRIMTimingModule.TabIndex = 0;
            this.tabCRIMTimingModule.Text = "Timing Module";
            this.tabCRIMTimingModule.UseVisualStyleBackColor = true;
            // 
            // lbl_CRIMTimingGateTimeRead
            // 
            this.lbl_CRIMTimingGateTimeRead.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMTimingGateTimeRead.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMTimingGateTimeRead.Location = new System.Drawing.Point(79, 167);
            this.lbl_CRIMTimingGateTimeRead.Name = "lbl_CRIMTimingGateTimeRead";
            this.lbl_CRIMTimingGateTimeRead.Size = new System.Drawing.Size(153, 18);
            this.lbl_CRIMTimingGateTimeRead.TabIndex = 96;
            this.lbl_CRIMTimingGateTimeRead.TextAlign = System.Drawing.ContentAlignment.MiddleLeft;
            // 
            // btn_CRIMTimingGateTimeRead
            // 
            this.btn_CRIMTimingGateTimeRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingGateTimeRead.Location = new System.Drawing.Point(233, 166);
            this.btn_CRIMTimingGateTimeRead.Name = "btn_CRIMTimingGateTimeRead";
            this.btn_CRIMTimingGateTimeRead.Size = new System.Drawing.Size(46, 20);
            this.btn_CRIMTimingGateTimeRead.TabIndex = 95;
            this.btn_CRIMTimingGateTimeRead.Text = "Read";
            this.btn_CRIMTimingGateTimeRead.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingGateTimeRead.Click += new System.EventHandler(this.btn_CRIMTimingGateTimeRead_Click);
            // 
            // label68
            // 
            this.label68.BackColor = System.Drawing.Color.Coral;
            this.label68.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label68.Location = new System.Drawing.Point(13, 168);
            this.label68.Name = "label68";
            this.label68.Size = new System.Drawing.Size(64, 16);
            this.label68.TabIndex = 94;
            this.label68.Text = "Gate Time";
            this.label68.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // txt_CRIMTimingTestRegister
            // 
            this.txt_CRIMTimingTestRegister.Location = new System.Drawing.Point(79, 146);
            this.txt_CRIMTimingTestRegister.Name = "txt_CRIMTimingTestRegister";
            this.txt_CRIMTimingTestRegister.Size = new System.Drawing.Size(60, 20);
            this.txt_CRIMTimingTestRegister.TabIndex = 93;
            // 
            // btn_CRIMTimingTestRegisterRead
            // 
            this.btn_CRIMTimingTestRegisterRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingTestRegisterRead.Location = new System.Drawing.Point(186, 146);
            this.btn_CRIMTimingTestRegisterRead.Name = "btn_CRIMTimingTestRegisterRead";
            this.btn_CRIMTimingTestRegisterRead.Size = new System.Drawing.Size(46, 20);
            this.btn_CRIMTimingTestRegisterRead.TabIndex = 92;
            this.btn_CRIMTimingTestRegisterRead.Text = "Read";
            this.btn_CRIMTimingTestRegisterRead.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingTestRegisterRead.Click += new System.EventHandler(this.btn_CRIMTimingTestRegisterRead_Click);
            // 
            // btn_CRIMTimingTestRegisterWrite
            // 
            this.btn_CRIMTimingTestRegisterWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingTestRegisterWrite.Location = new System.Drawing.Point(140, 146);
            this.btn_CRIMTimingTestRegisterWrite.Name = "btn_CRIMTimingTestRegisterWrite";
            this.btn_CRIMTimingTestRegisterWrite.Size = new System.Drawing.Size(46, 20);
            this.btn_CRIMTimingTestRegisterWrite.TabIndex = 91;
            this.btn_CRIMTimingTestRegisterWrite.Text = "Write";
            this.btn_CRIMTimingTestRegisterWrite.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingTestRegisterWrite.Click += new System.EventHandler(this.btn_CRIMTimingTestRegisterWrite_Click);
            // 
            // label66
            // 
            this.label66.BackColor = System.Drawing.Color.Coral;
            this.label66.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label66.Location = new System.Drawing.Point(13, 148);
            this.label66.Name = "label66";
            this.label66.Size = new System.Drawing.Size(64, 16);
            this.label66.TabIndex = 90;
            this.label66.Text = "Test Reg";
            this.label66.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label64
            // 
            this.label64.BackColor = System.Drawing.Color.Coral;
            this.label64.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label64.Location = new System.Drawing.Point(13, 72);
            this.label64.Name = "label64";
            this.label64.Size = new System.Drawing.Size(102, 16);
            this.label64.TabIndex = 89;
            this.label64.Text = "CNTRST Enable";
            this.label64.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // chk_CRIMTimingCNTRSTEnableInINTMode
            // 
            this.chk_CRIMTimingCNTRSTEnableInINTMode.AutoSize = true;
            this.chk_CRIMTimingCNTRSTEnableInINTMode.Location = new System.Drawing.Point(121, 74);
            this.chk_CRIMTimingCNTRSTEnableInINTMode.Name = "chk_CRIMTimingCNTRSTEnableInINTMode";
            this.chk_CRIMTimingCNTRSTEnableInINTMode.Size = new System.Drawing.Size(15, 14);
            this.chk_CRIMTimingCNTRSTEnableInINTMode.TabIndex = 88;
            this.chk_CRIMTimingCNTRSTEnableInINTMode.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            this.chk_CRIMTimingCNTRSTEnableInINTMode.UseVisualStyleBackColor = true;
            // 
            // btn_CRIMTimingSeqControlLatchReset
            // 
            this.btn_CRIMTimingSeqControlLatchReset.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingSeqControlLatchReset.Location = new System.Drawing.Point(241, 90);
            this.btn_CRIMTimingSeqControlLatchReset.Name = "btn_CRIMTimingSeqControlLatchReset";
            this.btn_CRIMTimingSeqControlLatchReset.Size = new System.Drawing.Size(111, 20);
            this.btn_CRIMTimingSeqControlLatchReset.TabIndex = 86;
            this.btn_CRIMTimingSeqControlLatchReset.Text = "Seq Ctrl Latch RST";
            this.btn_CRIMTimingSeqControlLatchReset.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingSeqControlLatchReset.Click += new System.EventHandler(this.btn_CRIMTimingSeqControlLatchReset_Click);
            // 
            // btn_CRIMTimingSS_CNTRST
            // 
            this.btn_CRIMTimingSS_CNTRST.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingSS_CNTRST.Location = new System.Drawing.Point(186, 111);
            this.btn_CRIMTimingSS_CNTRST.Name = "btn_CRIMTimingSS_CNTRST";
            this.btn_CRIMTimingSS_CNTRST.Size = new System.Drawing.Size(166, 34);
            this.btn_CRIMTimingSS_CNTRST.TabIndex = 85;
            this.btn_CRIMTimingSS_CNTRST.Text = "Send CNTRST in EXT mode";
            this.btn_CRIMTimingSS_CNTRST.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingSS_CNTRST.Click += new System.EventHandler(this.btn_CRIMTimingSS_CNTRST_Click);
            // 
            // btn_CRIMTimingSS_CNTRST_SGATE_TCALB
            // 
            this.btn_CRIMTimingSS_CNTRST_SGATE_TCALB.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingSS_CNTRST_SGATE_TCALB.Location = new System.Drawing.Point(13, 111);
            this.btn_CRIMTimingSS_CNTRST_SGATE_TCALB.Name = "btn_CRIMTimingSS_CNTRST_SGATE_TCALB";
            this.btn_CRIMTimingSS_CNTRST_SGATE_TCALB.Size = new System.Drawing.Size(174, 34);
            this.btn_CRIMTimingSS_CNTRST_SGATE_TCALB.TabIndex = 84;
            this.btn_CRIMTimingSS_CNTRST_SGATE_TCALB.Text = "Send Single Seq of CNTRST, SGATE, TCALB in INT mode";
            this.btn_CRIMTimingSS_CNTRST_SGATE_TCALB.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingSS_CNTRST_SGATE_TCALB.Click += new System.EventHandler(this.btn_CRIMTimingSS_CNTRST_SGATE_TCALB_Click);
            // 
            // label49
            // 
            this.label49.BackColor = System.Drawing.Color.Coral;
            this.label49.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label49.Location = new System.Drawing.Point(13, 12);
            this.label49.Name = "label49";
            this.label49.Size = new System.Drawing.Size(64, 16);
            this.label49.TabIndex = 63;
            this.label49.Text = "Mode";
            this.label49.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // btn_CRIMTimingSendTCALB
            // 
            this.btn_CRIMTimingSendTCALB.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingSendTCALB.Location = new System.Drawing.Point(241, 30);
            this.btn_CRIMTimingSendTCALB.Name = "btn_CRIMTimingSendTCALB";
            this.btn_CRIMTimingSendTCALB.Size = new System.Drawing.Size(111, 20);
            this.btn_CRIMTimingSendTCALB.TabIndex = 83;
            this.btn_CRIMTimingSendTCALB.Text = "Send TCALB";
            this.btn_CRIMTimingSendTCALB.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingSendTCALB.Click += new System.EventHandler(this.btn_CRIMTimingSendTCALB_Click);
            // 
            // cmb_CRIMTimingMode
            // 
            this.cmb_CRIMTimingMode.FormattingEnabled = true;
            this.cmb_CRIMTimingMode.Location = new System.Drawing.Point(79, 10);
            this.cmb_CRIMTimingMode.Name = "cmb_CRIMTimingMode";
            this.cmb_CRIMTimingMode.Size = new System.Drawing.Size(60, 21);
            this.cmb_CRIMTimingMode.TabIndex = 0;
            // 
            // btn_CRIMTimingSendStartGate
            // 
            this.btn_CRIMTimingSendStartGate.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingSendStartGate.Location = new System.Drawing.Point(241, 50);
            this.btn_CRIMTimingSendStartGate.Name = "btn_CRIMTimingSendStartGate";
            this.btn_CRIMTimingSendStartGate.Size = new System.Drawing.Size(111, 20);
            this.btn_CRIMTimingSendStartGate.TabIndex = 82;
            this.btn_CRIMTimingSendStartGate.Text = "Send START Gate";
            this.btn_CRIMTimingSendStartGate.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingSendStartGate.Click += new System.EventHandler(this.btn_CRIMTimingSendStartGate_Click);
            // 
            // label50
            // 
            this.label50.BackColor = System.Drawing.Color.Coral;
            this.label50.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label50.Location = new System.Drawing.Point(13, 32);
            this.label50.Name = "label50";
            this.label50.Size = new System.Drawing.Size(64, 16);
            this.label50.TabIndex = 64;
            this.label50.Text = "Frequency";
            this.label50.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // btn_CRIMTimingSendStopGate
            // 
            this.btn_CRIMTimingSendStopGate.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingSendStopGate.Location = new System.Drawing.Point(241, 70);
            this.btn_CRIMTimingSendStopGate.Name = "btn_CRIMTimingSendStopGate";
            this.btn_CRIMTimingSendStopGate.Size = new System.Drawing.Size(111, 20);
            this.btn_CRIMTimingSendStopGate.TabIndex = 81;
            this.btn_CRIMTimingSendStopGate.Text = "Send STOP Gate";
            this.btn_CRIMTimingSendStopGate.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingSendStopGate.Click += new System.EventHandler(this.btn_CRIMTimingSendStopGate_Click);
            // 
            // btn_CRIMTimingModeWrite
            // 
            this.btn_CRIMTimingModeWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingModeWrite.Location = new System.Drawing.Point(140, 10);
            this.btn_CRIMTimingModeWrite.Name = "btn_CRIMTimingModeWrite";
            this.btn_CRIMTimingModeWrite.Size = new System.Drawing.Size(46, 20);
            this.btn_CRIMTimingModeWrite.TabIndex = 65;
            this.btn_CRIMTimingModeWrite.Text = "Write";
            this.btn_CRIMTimingModeWrite.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingModeWrite.Click += new System.EventHandler(this.btn_CRIMTimingModeWrite_Click);
            // 
            // btn_CRIMTimingSendTrigger
            // 
            this.btn_CRIMTimingSendTrigger.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingSendTrigger.Location = new System.Drawing.Point(241, 10);
            this.btn_CRIMTimingSendTrigger.Name = "btn_CRIMTimingSendTrigger";
            this.btn_CRIMTimingSendTrigger.Size = new System.Drawing.Size(111, 20);
            this.btn_CRIMTimingSendTrigger.TabIndex = 80;
            this.btn_CRIMTimingSendTrigger.Text = "Send TRIGGER";
            this.btn_CRIMTimingSendTrigger.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingSendTrigger.Click += new System.EventHandler(this.btn_CRIMTimingSendTrigger_Click);
            // 
            // btn_CRIMTimingModeRead
            // 
            this.btn_CRIMTimingModeRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingModeRead.Location = new System.Drawing.Point(186, 10);
            this.btn_CRIMTimingModeRead.Name = "btn_CRIMTimingModeRead";
            this.btn_CRIMTimingModeRead.Size = new System.Drawing.Size(46, 20);
            this.btn_CRIMTimingModeRead.TabIndex = 66;
            this.btn_CRIMTimingModeRead.Text = "Read";
            this.btn_CRIMTimingModeRead.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingModeRead.Click += new System.EventHandler(this.btn_CRIMTimingModeRead_Click);
            // 
            // txt_CRIMTimingTCALB
            // 
            this.txt_CRIMTimingTCALB.Location = new System.Drawing.Point(79, 90);
            this.txt_CRIMTimingTCALB.Name = "txt_CRIMTimingTCALB";
            this.txt_CRIMTimingTCALB.Size = new System.Drawing.Size(60, 20);
            this.txt_CRIMTimingTCALB.TabIndex = 79;
            // 
            // cmb_CRIMTimingFrequency
            // 
            this.cmb_CRIMTimingFrequency.FormattingEnabled = true;
            this.cmb_CRIMTimingFrequency.Location = new System.Drawing.Point(79, 30);
            this.cmb_CRIMTimingFrequency.Name = "cmb_CRIMTimingFrequency";
            this.cmb_CRIMTimingFrequency.Size = new System.Drawing.Size(60, 21);
            this.cmb_CRIMTimingFrequency.TabIndex = 67;
            // 
            // txt_CRIMTimingGateWidth
            // 
            this.txt_CRIMTimingGateWidth.Location = new System.Drawing.Point(79, 50);
            this.txt_CRIMTimingGateWidth.Name = "txt_CRIMTimingGateWidth";
            this.txt_CRIMTimingGateWidth.Size = new System.Drawing.Size(60, 20);
            this.txt_CRIMTimingGateWidth.TabIndex = 78;
            // 
            // btn_CRIMTimingFrequencyWrite
            // 
            this.btn_CRIMTimingFrequencyWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingFrequencyWrite.Location = new System.Drawing.Point(140, 30);
            this.btn_CRIMTimingFrequencyWrite.Name = "btn_CRIMTimingFrequencyWrite";
            this.btn_CRIMTimingFrequencyWrite.Size = new System.Drawing.Size(46, 20);
            this.btn_CRIMTimingFrequencyWrite.TabIndex = 68;
            this.btn_CRIMTimingFrequencyWrite.Text = "Write";
            this.btn_CRIMTimingFrequencyWrite.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingFrequencyWrite.Click += new System.EventHandler(this.btn_CRIMTimingFrequencyWrite_Click);
            // 
            // btn_CRIMTimingTCALBRead
            // 
            this.btn_CRIMTimingTCALBRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingTCALBRead.Location = new System.Drawing.Point(186, 90);
            this.btn_CRIMTimingTCALBRead.Name = "btn_CRIMTimingTCALBRead";
            this.btn_CRIMTimingTCALBRead.Size = new System.Drawing.Size(46, 20);
            this.btn_CRIMTimingTCALBRead.TabIndex = 77;
            this.btn_CRIMTimingTCALBRead.Text = "Read";
            this.btn_CRIMTimingTCALBRead.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingTCALBRead.Click += new System.EventHandler(this.btn_CRIMTimingTCALBRead_Click);
            // 
            // btn_CRIMTimingFrequencyRead
            // 
            this.btn_CRIMTimingFrequencyRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingFrequencyRead.Location = new System.Drawing.Point(186, 30);
            this.btn_CRIMTimingFrequencyRead.Name = "btn_CRIMTimingFrequencyRead";
            this.btn_CRIMTimingFrequencyRead.Size = new System.Drawing.Size(46, 20);
            this.btn_CRIMTimingFrequencyRead.TabIndex = 69;
            this.btn_CRIMTimingFrequencyRead.Text = "Read";
            this.btn_CRIMTimingFrequencyRead.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingFrequencyRead.Click += new System.EventHandler(this.btn_CRIMTimingFrequencyRead_Click);
            // 
            // btn_CRIMTimingTCALBWrite
            // 
            this.btn_CRIMTimingTCALBWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingTCALBWrite.Location = new System.Drawing.Point(140, 90);
            this.btn_CRIMTimingTCALBWrite.Name = "btn_CRIMTimingTCALBWrite";
            this.btn_CRIMTimingTCALBWrite.Size = new System.Drawing.Size(46, 20);
            this.btn_CRIMTimingTCALBWrite.TabIndex = 76;
            this.btn_CRIMTimingTCALBWrite.Text = "Write";
            this.btn_CRIMTimingTCALBWrite.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingTCALBWrite.Click += new System.EventHandler(this.btn_CRIMTimingTCALBWrite_Click);
            // 
            // label52
            // 
            this.label52.BackColor = System.Drawing.Color.Coral;
            this.label52.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label52.Location = new System.Drawing.Point(13, 52);
            this.label52.Name = "label52";
            this.label52.Size = new System.Drawing.Size(64, 16);
            this.label52.TabIndex = 71;
            this.label52.Text = "Gate Width";
            this.label52.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // btn_CRIMTimingGateWidthRead
            // 
            this.btn_CRIMTimingGateWidthRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingGateWidthRead.Location = new System.Drawing.Point(186, 50);
            this.btn_CRIMTimingGateWidthRead.Name = "btn_CRIMTimingGateWidthRead";
            this.btn_CRIMTimingGateWidthRead.Size = new System.Drawing.Size(46, 40);
            this.btn_CRIMTimingGateWidthRead.TabIndex = 74;
            this.btn_CRIMTimingGateWidthRead.Text = "Read";
            this.btn_CRIMTimingGateWidthRead.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingGateWidthRead.Click += new System.EventHandler(this.btn_CRIMTimingGateWidthRead_Click);
            // 
            // label51
            // 
            this.label51.BackColor = System.Drawing.Color.Coral;
            this.label51.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label51.Location = new System.Drawing.Point(13, 92);
            this.label51.Name = "label51";
            this.label51.Size = new System.Drawing.Size(64, 16);
            this.label51.TabIndex = 72;
            this.label51.Text = "TCALB Del";
            this.label51.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // btn_CRIMTimingGateWidthWrite
            // 
            this.btn_CRIMTimingGateWidthWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMTimingGateWidthWrite.Location = new System.Drawing.Point(140, 50);
            this.btn_CRIMTimingGateWidthWrite.Name = "btn_CRIMTimingGateWidthWrite";
            this.btn_CRIMTimingGateWidthWrite.Size = new System.Drawing.Size(46, 40);
            this.btn_CRIMTimingGateWidthWrite.TabIndex = 73;
            this.btn_CRIMTimingGateWidthWrite.Text = "Write";
            this.btn_CRIMTimingGateWidthWrite.UseVisualStyleBackColor = false;
            this.btn_CRIMTimingGateWidthWrite.Click += new System.EventHandler(this.btn_CRIMTimingGateWidthWrite_Click);
            // 
            // tabCRIMDAQModule
            // 
            this.tabCRIMDAQModule.Controls.Add(this.groupBoxCRIM_MiscRegisters);
            this.tabCRIMDAQModule.Controls.Add(this.groupBoxCRIM_DAQModeRegister);
            this.tabCRIMDAQModule.Controls.Add(this.groupBoxCRIM_DPMRegister);
            this.tabCRIMDAQModule.Controls.Add(this.groupBoxCRIM_StatusRegister);
            this.tabCRIMDAQModule.Controls.Add(this.groupBoxCRIM_FrameRegisters);
            this.tabCRIMDAQModule.Location = new System.Drawing.Point(4, 22);
            this.tabCRIMDAQModule.Name = "tabCRIMDAQModule";
            this.tabCRIMDAQModule.Padding = new System.Windows.Forms.Padding(3);
            this.tabCRIMDAQModule.Size = new System.Drawing.Size(373, 432);
            this.tabCRIMDAQModule.TabIndex = 1;
            this.tabCRIMDAQModule.Text = "DAQ Module";
            this.tabCRIMDAQModule.UseVisualStyleBackColor = true;
            // 
            // groupBoxCRIM_MiscRegisters
            // 
            this.groupBoxCRIM_MiscRegisters.Controls.Add(this.btn_CRIMDAQSendSyncRegister);
            this.groupBoxCRIM_MiscRegisters.Controls.Add(this.btn_CRIMDAQResetFIFORegister);
            this.groupBoxCRIM_MiscRegisters.Controls.Add(this.lbl_CRIMDAQReadTimingCommandRegister);
            this.groupBoxCRIM_MiscRegisters.Controls.Add(this.btn_CRIMDAQReadTimingCommandRegister);
            this.groupBoxCRIM_MiscRegisters.Location = new System.Drawing.Point(166, 6);
            this.groupBoxCRIM_MiscRegisters.Name = "groupBoxCRIM_MiscRegisters";
            this.groupBoxCRIM_MiscRegisters.Size = new System.Drawing.Size(182, 80);
            this.groupBoxCRIM_MiscRegisters.TabIndex = 106;
            this.groupBoxCRIM_MiscRegisters.TabStop = false;
            this.groupBoxCRIM_MiscRegisters.Text = "Misc Registers";
            // 
            // btn_CRIMDAQSendSyncRegister
            // 
            this.btn_CRIMDAQSendSyncRegister.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMDAQSendSyncRegister.Location = new System.Drawing.Point(6, 56);
            this.btn_CRIMDAQSendSyncRegister.Name = "btn_CRIMDAQSendSyncRegister";
            this.btn_CRIMDAQSendSyncRegister.Size = new System.Drawing.Size(108, 20);
            this.btn_CRIMDAQSendSyncRegister.TabIndex = 106;
            this.btn_CRIMDAQSendSyncRegister.Text = "Send SYNC";
            this.btn_CRIMDAQSendSyncRegister.UseVisualStyleBackColor = false;
            this.btn_CRIMDAQSendSyncRegister.Click += new System.EventHandler(this.btn_CRIMDAQSendSyncRegister_Click);
            // 
            // btn_CRIMDAQResetFIFORegister
            // 
            this.btn_CRIMDAQResetFIFORegister.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMDAQResetFIFORegister.Location = new System.Drawing.Point(6, 14);
            this.btn_CRIMDAQResetFIFORegister.Name = "btn_CRIMDAQResetFIFORegister";
            this.btn_CRIMDAQResetFIFORegister.Size = new System.Drawing.Size(108, 20);
            this.btn_CRIMDAQResetFIFORegister.TabIndex = 105;
            this.btn_CRIMDAQResetFIFORegister.Text = "Reset FIFO flag";
            this.btn_CRIMDAQResetFIFORegister.UseVisualStyleBackColor = false;
            this.btn_CRIMDAQResetFIFORegister.Click += new System.EventHandler(this.btn_CRIMDAQResetFIFORegister_Click);
            // 
            // lbl_CRIMDAQReadTimingCommandRegister
            // 
            this.lbl_CRIMDAQReadTimingCommandRegister.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQReadTimingCommandRegister.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQReadTimingCommandRegister.Location = new System.Drawing.Point(114, 36);
            this.lbl_CRIMDAQReadTimingCommandRegister.Name = "lbl_CRIMDAQReadTimingCommandRegister";
            this.lbl_CRIMDAQReadTimingCommandRegister.Size = new System.Drawing.Size(62, 18);
            this.lbl_CRIMDAQReadTimingCommandRegister.TabIndex = 83;
            // 
            // btn_CRIMDAQReadTimingCommandRegister
            // 
            this.btn_CRIMDAQReadTimingCommandRegister.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMDAQReadTimingCommandRegister.Location = new System.Drawing.Point(6, 35);
            this.btn_CRIMDAQReadTimingCommandRegister.Name = "btn_CRIMDAQReadTimingCommandRegister";
            this.btn_CRIMDAQReadTimingCommandRegister.Size = new System.Drawing.Size(108, 20);
            this.btn_CRIMDAQReadTimingCommandRegister.TabIndex = 83;
            this.btn_CRIMDAQReadTimingCommandRegister.Text = "Read timing cmd";
            this.btn_CRIMDAQReadTimingCommandRegister.UseVisualStyleBackColor = false;
            this.btn_CRIMDAQReadTimingCommandRegister.Click += new System.EventHandler(this.btn_CRIMDAQReadTimingCommandRegister_Click);
            // 
            // groupBoxCRIM_DAQModeRegister
            // 
            this.groupBoxCRIM_DAQModeRegister.Controls.Add(this.chk_CRIMDAQModeRegisterSendEn);
            this.groupBoxCRIM_DAQModeRegister.Controls.Add(this.chk_CRIMDAQModeRegisterFETriggEn);
            this.groupBoxCRIM_DAQModeRegister.Controls.Add(this.btn_CRIMDAQModeRegisterRead);
            this.groupBoxCRIM_DAQModeRegister.Controls.Add(this.btn_CRIMDAQModeRegisterWrite);
            this.groupBoxCRIM_DAQModeRegister.Controls.Add(this.chk_CRIMDAQModeRegisterCRCEn);
            this.groupBoxCRIM_DAQModeRegister.Controls.Add(this.chk_CRIMDAQModeRegisterRetransmitEn);
            this.groupBoxCRIM_DAQModeRegister.Location = new System.Drawing.Point(9, 6);
            this.groupBoxCRIM_DAQModeRegister.Name = "groupBoxCRIM_DAQModeRegister";
            this.groupBoxCRIM_DAQModeRegister.Size = new System.Drawing.Size(150, 78);
            this.groupBoxCRIM_DAQModeRegister.TabIndex = 91;
            this.groupBoxCRIM_DAQModeRegister.TabStop = false;
            this.groupBoxCRIM_DAQModeRegister.Text = "DAQ Mode Register";
            // 
            // chk_CRIMDAQModeRegisterSendEn
            // 
            this.chk_CRIMDAQModeRegisterSendEn.AutoSize = true;
            this.chk_CRIMDAQModeRegisterSendEn.Location = new System.Drawing.Point(6, 52);
            this.chk_CRIMDAQModeRegisterSendEn.Name = "chk_CRIMDAQModeRegisterSendEn";
            this.chk_CRIMDAQModeRegisterSendEn.Size = new System.Drawing.Size(78, 17);
            this.chk_CRIMDAQModeRegisterSendEn.TabIndex = 102;
            this.chk_CRIMDAQModeRegisterSendEn.Text = "send frame";
            this.chk_CRIMDAQModeRegisterSendEn.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.chk_CRIMDAQModeRegisterSendEn.UseVisualStyleBackColor = true;
            // 
            // chk_CRIMDAQModeRegisterFETriggEn
            // 
            this.chk_CRIMDAQModeRegisterFETriggEn.AutoSize = true;
            this.chk_CRIMDAQModeRegisterFETriggEn.Location = new System.Drawing.Point(84, 52);
            this.chk_CRIMDAQModeRegisterFETriggEn.Name = "chk_CRIMDAQModeRegisterFETriggEn";
            this.chk_CRIMDAQModeRegisterFETriggEn.Size = new System.Drawing.Size(63, 17);
            this.chk_CRIMDAQModeRegisterFETriggEn.TabIndex = 104;
            this.chk_CRIMDAQModeRegisterFETriggEn.Text = "FETrigg";
            this.chk_CRIMDAQModeRegisterFETriggEn.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.chk_CRIMDAQModeRegisterFETriggEn.UseVisualStyleBackColor = true;
            // 
            // btn_CRIMDAQModeRegisterRead
            // 
            this.btn_CRIMDAQModeRegisterRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMDAQModeRegisterRead.Location = new System.Drawing.Point(58, 16);
            this.btn_CRIMDAQModeRegisterRead.Name = "btn_CRIMDAQModeRegisterRead";
            this.btn_CRIMDAQModeRegisterRead.Size = new System.Drawing.Size(46, 20);
            this.btn_CRIMDAQModeRegisterRead.TabIndex = 100;
            this.btn_CRIMDAQModeRegisterRead.Text = "Read";
            this.btn_CRIMDAQModeRegisterRead.UseVisualStyleBackColor = false;
            this.btn_CRIMDAQModeRegisterRead.Click += new System.EventHandler(this.btn_CRIMDAQModeRegisterRead_Click);
            // 
            // btn_CRIMDAQModeRegisterWrite
            // 
            this.btn_CRIMDAQModeRegisterWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMDAQModeRegisterWrite.Location = new System.Drawing.Point(6, 16);
            this.btn_CRIMDAQModeRegisterWrite.Name = "btn_CRIMDAQModeRegisterWrite";
            this.btn_CRIMDAQModeRegisterWrite.Size = new System.Drawing.Size(46, 20);
            this.btn_CRIMDAQModeRegisterWrite.TabIndex = 99;
            this.btn_CRIMDAQModeRegisterWrite.Text = "Write";
            this.btn_CRIMDAQModeRegisterWrite.UseVisualStyleBackColor = false;
            this.btn_CRIMDAQModeRegisterWrite.Click += new System.EventHandler(this.btn_CRIMDAQModeRegisterWrite_Click);
            // 
            // chk_CRIMDAQModeRegisterCRCEn
            // 
            this.chk_CRIMDAQModeRegisterCRCEn.AutoSize = true;
            this.chk_CRIMDAQModeRegisterCRCEn.Location = new System.Drawing.Point(84, 38);
            this.chk_CRIMDAQModeRegisterCRCEn.Name = "chk_CRIMDAQModeRegisterCRCEn";
            this.chk_CRIMDAQModeRegisterCRCEn.Size = new System.Drawing.Size(48, 17);
            this.chk_CRIMDAQModeRegisterCRCEn.TabIndex = 103;
            this.chk_CRIMDAQModeRegisterCRCEn.Text = "CRC";
            this.chk_CRIMDAQModeRegisterCRCEn.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.chk_CRIMDAQModeRegisterCRCEn.UseVisualStyleBackColor = true;
            // 
            // chk_CRIMDAQModeRegisterRetransmitEn
            // 
            this.chk_CRIMDAQModeRegisterRetransmitEn.AutoSize = true;
            this.chk_CRIMDAQModeRegisterRetransmitEn.Location = new System.Drawing.Point(6, 38);
            this.chk_CRIMDAQModeRegisterRetransmitEn.Name = "chk_CRIMDAQModeRegisterRetransmitEn";
            this.chk_CRIMDAQModeRegisterRetransmitEn.Size = new System.Drawing.Size(74, 17);
            this.chk_CRIMDAQModeRegisterRetransmitEn.TabIndex = 101;
            this.chk_CRIMDAQModeRegisterRetransmitEn.Text = "re-transmit";
            this.chk_CRIMDAQModeRegisterRetransmitEn.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.chk_CRIMDAQModeRegisterRetransmitEn.UseVisualStyleBackColor = true;
            // 
            // groupBoxCRIM_DPMRegister
            // 
            this.groupBoxCRIM_DPMRegister.Controls.Add(this.btn_CRIMDAQDPMRegisterResetPointer);
            this.groupBoxCRIM_DPMRegister.Controls.Add(this.btn_CRIMDAQDPMRegisterReadPointer);
            this.groupBoxCRIM_DPMRegister.Controls.Add(this.lbl_CRIMDAQDPMRegisterReadPointer);
            this.groupBoxCRIM_DPMRegister.Location = new System.Drawing.Point(156, 92);
            this.groupBoxCRIM_DPMRegister.Name = "groupBoxCRIM_DPMRegister";
            this.groupBoxCRIM_DPMRegister.Size = new System.Drawing.Size(192, 78);
            this.groupBoxCRIM_DPMRegister.TabIndex = 90;
            this.groupBoxCRIM_DPMRegister.TabStop = false;
            this.groupBoxCRIM_DPMRegister.Text = "DPM Register";
            // 
            // btn_CRIMDAQDPMRegisterResetPointer
            // 
            this.btn_CRIMDAQDPMRegisterResetPointer.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMDAQDPMRegisterResetPointer.Location = new System.Drawing.Point(10, 20);
            this.btn_CRIMDAQDPMRegisterResetPointer.Name = "btn_CRIMDAQDPMRegisterResetPointer";
            this.btn_CRIMDAQDPMRegisterResetPointer.Size = new System.Drawing.Size(114, 20);
            this.btn_CRIMDAQDPMRegisterResetPointer.TabIndex = 82;
            this.btn_CRIMDAQDPMRegisterResetPointer.Text = "Reset DPM Pointer";
            this.btn_CRIMDAQDPMRegisterResetPointer.UseVisualStyleBackColor = false;
            this.btn_CRIMDAQDPMRegisterResetPointer.Click += new System.EventHandler(this.btn_CRIMDAQDPMRegisterResetPointer_Click);
            // 
            // btn_CRIMDAQDPMRegisterReadPointer
            // 
            this.btn_CRIMDAQDPMRegisterReadPointer.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMDAQDPMRegisterReadPointer.Location = new System.Drawing.Point(10, 42);
            this.btn_CRIMDAQDPMRegisterReadPointer.Name = "btn_CRIMDAQDPMRegisterReadPointer";
            this.btn_CRIMDAQDPMRegisterReadPointer.Size = new System.Drawing.Size(115, 20);
            this.btn_CRIMDAQDPMRegisterReadPointer.TabIndex = 80;
            this.btn_CRIMDAQDPMRegisterReadPointer.Text = "Read  DPM Pointer";
            this.btn_CRIMDAQDPMRegisterReadPointer.UseVisualStyleBackColor = false;
            this.btn_CRIMDAQDPMRegisterReadPointer.Click += new System.EventHandler(this.btn_CRIMDAQDPMRegisterReadPointer_Click);
            // 
            // lbl_CRIMDAQDPMRegisterReadPointer
            // 
            this.lbl_CRIMDAQDPMRegisterReadPointer.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQDPMRegisterReadPointer.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQDPMRegisterReadPointer.Location = new System.Drawing.Point(125, 43);
            this.lbl_CRIMDAQDPMRegisterReadPointer.Name = "lbl_CRIMDAQDPMRegisterReadPointer";
            this.lbl_CRIMDAQDPMRegisterReadPointer.Size = new System.Drawing.Size(61, 18);
            this.lbl_CRIMDAQDPMRegisterReadPointer.TabIndex = 81;
            // 
            // groupBoxCRIM_StatusRegister
            // 
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusEncodedCmdRcv);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label59);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusFERebootRcv);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label61);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusUnusedBit11);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label63);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusUnusedBit7);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label65);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.btn_CRIMDAQStatusRegisterClear);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.btn_CRIMDAQStatusRegisterRead);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusRegisterRead);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label67);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusMsgSent);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusRFPresent);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label70);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label71);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusMsgRcv);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusDPMFull);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label74);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label75);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusCRCErr);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusFIFOFull);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label78);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label79);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusTimeoutErr);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusFIFONotEmpty);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label82);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label83);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusSerializerSync);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusTestPulseRcv);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label88);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label87);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusDeserializerLock);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.lbl_CRIMDAQStatusPLLLock);
            this.groupBoxCRIM_StatusRegister.Controls.Add(this.label90);
            this.groupBoxCRIM_StatusRegister.Location = new System.Drawing.Point(9, 91);
            this.groupBoxCRIM_StatusRegister.Name = "groupBoxCRIM_StatusRegister";
            this.groupBoxCRIM_StatusRegister.Size = new System.Drawing.Size(141, 322);
            this.groupBoxCRIM_StatusRegister.TabIndex = 91;
            this.groupBoxCRIM_StatusRegister.TabStop = false;
            this.groupBoxCRIM_StatusRegister.Text = "Status Register";
            // 
            // lbl_CRIMDAQStatusEncodedCmdRcv
            // 
            this.lbl_CRIMDAQStatusEncodedCmdRcv.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusEncodedCmdRcv.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusEncodedCmdRcv.Location = new System.Drawing.Point(117, 298);
            this.lbl_CRIMDAQStatusEncodedCmdRcv.Name = "lbl_CRIMDAQStatusEncodedCmdRcv";
            this.lbl_CRIMDAQStatusEncodedCmdRcv.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusEncodedCmdRcv.TabIndex = 87;
            // 
            // label59
            // 
            this.label59.BackColor = System.Drawing.Color.Coral;
            this.label59.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label59.Location = new System.Drawing.Point(10, 298);
            this.label59.Name = "label59";
            this.label59.Size = new System.Drawing.Size(107, 15);
            this.label59.TabIndex = 86;
            this.label59.Text = "Encoded cmd rcv";
            // 
            // lbl_CRIMDAQStatusFERebootRcv
            // 
            this.lbl_CRIMDAQStatusFERebootRcv.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusFERebootRcv.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusFERebootRcv.Location = new System.Drawing.Point(117, 283);
            this.lbl_CRIMDAQStatusFERebootRcv.Name = "lbl_CRIMDAQStatusFERebootRcv";
            this.lbl_CRIMDAQStatusFERebootRcv.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusFERebootRcv.TabIndex = 85;
            // 
            // label61
            // 
            this.label61.BackColor = System.Drawing.Color.Coral;
            this.label61.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label61.Location = new System.Drawing.Point(10, 283);
            this.label61.Name = "label61";
            this.label61.Size = new System.Drawing.Size(107, 15);
            this.label61.TabIndex = 84;
            this.label61.Text = "FE reboot rcv";
            // 
            // lbl_CRIMDAQStatusUnusedBit11
            // 
            this.lbl_CRIMDAQStatusUnusedBit11.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusUnusedBit11.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusUnusedBit11.Location = new System.Drawing.Point(117, 235);
            this.lbl_CRIMDAQStatusUnusedBit11.Name = "lbl_CRIMDAQStatusUnusedBit11";
            this.lbl_CRIMDAQStatusUnusedBit11.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusUnusedBit11.TabIndex = 83;
            // 
            // label63
            // 
            this.label63.BackColor = System.Drawing.Color.Coral;
            this.label63.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label63.Location = new System.Drawing.Point(10, 235);
            this.label63.Name = "label63";
            this.label63.Size = new System.Drawing.Size(107, 15);
            this.label63.TabIndex = 82;
            this.label63.Text = "Unused";
            // 
            // lbl_CRIMDAQStatusUnusedBit7
            // 
            this.lbl_CRIMDAQStatusUnusedBit7.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusUnusedBit7.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusUnusedBit7.Location = new System.Drawing.Point(117, 172);
            this.lbl_CRIMDAQStatusUnusedBit7.Name = "lbl_CRIMDAQStatusUnusedBit7";
            this.lbl_CRIMDAQStatusUnusedBit7.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusUnusedBit7.TabIndex = 81;
            // 
            // label65
            // 
            this.label65.BackColor = System.Drawing.Color.Coral;
            this.label65.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label65.Location = new System.Drawing.Point(10, 172);
            this.label65.Name = "label65";
            this.label65.Size = new System.Drawing.Size(107, 15);
            this.label65.TabIndex = 80;
            this.label65.Text = "Unused";
            // 
            // btn_CRIMDAQStatusRegisterClear
            // 
            this.btn_CRIMDAQStatusRegisterClear.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMDAQStatusRegisterClear.Location = new System.Drawing.Point(10, 20);
            this.btn_CRIMDAQStatusRegisterClear.Name = "btn_CRIMDAQStatusRegisterClear";
            this.btn_CRIMDAQStatusRegisterClear.Size = new System.Drawing.Size(121, 20);
            this.btn_CRIMDAQStatusRegisterClear.TabIndex = 79;
            this.btn_CRIMDAQStatusRegisterClear.Text = "Clear Status Register";
            this.btn_CRIMDAQStatusRegisterClear.UseVisualStyleBackColor = false;
            this.btn_CRIMDAQStatusRegisterClear.Click += new System.EventHandler(this.btn_CRIMDAQStatusRegisterClear_Click);
            // 
            // btn_CRIMDAQStatusRegisterRead
            // 
            this.btn_CRIMDAQStatusRegisterRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMDAQStatusRegisterRead.Location = new System.Drawing.Point(10, 41);
            this.btn_CRIMDAQStatusRegisterRead.Name = "btn_CRIMDAQStatusRegisterRead";
            this.btn_CRIMDAQStatusRegisterRead.Size = new System.Drawing.Size(78, 20);
            this.btn_CRIMDAQStatusRegisterRead.TabIndex = 53;
            this.btn_CRIMDAQStatusRegisterRead.Text = "Read Status";
            this.btn_CRIMDAQStatusRegisterRead.UseVisualStyleBackColor = false;
            this.btn_CRIMDAQStatusRegisterRead.Click += new System.EventHandler(this.btn_CRIMDAQStatusRegisterRead_Click);
            // 
            // lbl_CRIMDAQStatusRegisterRead
            // 
            this.lbl_CRIMDAQStatusRegisterRead.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusRegisterRead.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusRegisterRead.Location = new System.Drawing.Point(87, 42);
            this.lbl_CRIMDAQStatusRegisterRead.Name = "lbl_CRIMDAQStatusRegisterRead";
            this.lbl_CRIMDAQStatusRegisterRead.Size = new System.Drawing.Size(44, 18);
            this.lbl_CRIMDAQStatusRegisterRead.TabIndex = 54;
            // 
            // label67
            // 
            this.label67.BackColor = System.Drawing.Color.Coral;
            this.label67.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label67.Location = new System.Drawing.Point(10, 64);
            this.label67.Name = "label67";
            this.label67.Size = new System.Drawing.Size(107, 15);
            this.label67.TabIndex = 55;
            this.label67.Text = "Msg Sent";
            // 
            // lbl_CRIMDAQStatusMsgSent
            // 
            this.lbl_CRIMDAQStatusMsgSent.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusMsgSent.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusMsgSent.Location = new System.Drawing.Point(117, 64);
            this.lbl_CRIMDAQStatusMsgSent.Name = "lbl_CRIMDAQStatusMsgSent";
            this.lbl_CRIMDAQStatusMsgSent.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusMsgSent.TabIndex = 56;
            // 
            // lbl_CRIMDAQStatusRFPresent
            // 
            this.lbl_CRIMDAQStatusRFPresent.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusRFPresent.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusRFPresent.Location = new System.Drawing.Point(117, 190);
            this.lbl_CRIMDAQStatusRFPresent.Name = "lbl_CRIMDAQStatusRFPresent";
            this.lbl_CRIMDAQStatusRFPresent.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusRFPresent.TabIndex = 78;
            // 
            // label70
            // 
            this.label70.BackColor = System.Drawing.Color.Coral;
            this.label70.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label70.Location = new System.Drawing.Point(10, 79);
            this.label70.Name = "label70";
            this.label70.Size = new System.Drawing.Size(107, 15);
            this.label70.TabIndex = 57;
            this.label70.Text = "Msg Received";
            // 
            // label71
            // 
            this.label71.BackColor = System.Drawing.Color.Coral;
            this.label71.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label71.Location = new System.Drawing.Point(10, 190);
            this.label71.Name = "label71";
            this.label71.Size = new System.Drawing.Size(107, 15);
            this.label71.TabIndex = 77;
            this.label71.Text = "RF Present";
            // 
            // lbl_CRIMDAQStatusMsgRcv
            // 
            this.lbl_CRIMDAQStatusMsgRcv.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusMsgRcv.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusMsgRcv.Location = new System.Drawing.Point(117, 79);
            this.lbl_CRIMDAQStatusMsgRcv.Name = "lbl_CRIMDAQStatusMsgRcv";
            this.lbl_CRIMDAQStatusMsgRcv.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusMsgRcv.TabIndex = 58;
            // 
            // lbl_CRIMDAQStatusDPMFull
            // 
            this.lbl_CRIMDAQStatusDPMFull.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusDPMFull.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusDPMFull.Location = new System.Drawing.Point(117, 157);
            this.lbl_CRIMDAQStatusDPMFull.Name = "lbl_CRIMDAQStatusDPMFull";
            this.lbl_CRIMDAQStatusDPMFull.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusDPMFull.TabIndex = 76;
            // 
            // label74
            // 
            this.label74.BackColor = System.Drawing.Color.Coral;
            this.label74.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label74.Location = new System.Drawing.Point(10, 94);
            this.label74.Name = "label74";
            this.label74.Size = new System.Drawing.Size(107, 15);
            this.label74.TabIndex = 59;
            this.label74.Text = "CRC Error";
            // 
            // label75
            // 
            this.label75.BackColor = System.Drawing.Color.Coral;
            this.label75.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label75.Location = new System.Drawing.Point(10, 157);
            this.label75.Name = "label75";
            this.label75.Size = new System.Drawing.Size(107, 15);
            this.label75.TabIndex = 75;
            this.label75.Text = "DPM Full";
            // 
            // lbl_CRIMDAQStatusCRCErr
            // 
            this.lbl_CRIMDAQStatusCRCErr.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusCRCErr.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusCRCErr.Location = new System.Drawing.Point(117, 94);
            this.lbl_CRIMDAQStatusCRCErr.Name = "lbl_CRIMDAQStatusCRCErr";
            this.lbl_CRIMDAQStatusCRCErr.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusCRCErr.TabIndex = 60;
            // 
            // lbl_CRIMDAQStatusFIFOFull
            // 
            this.lbl_CRIMDAQStatusFIFOFull.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusFIFOFull.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusFIFOFull.Location = new System.Drawing.Point(117, 142);
            this.lbl_CRIMDAQStatusFIFOFull.Name = "lbl_CRIMDAQStatusFIFOFull";
            this.lbl_CRIMDAQStatusFIFOFull.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusFIFOFull.TabIndex = 74;
            // 
            // label78
            // 
            this.label78.BackColor = System.Drawing.Color.Coral;
            this.label78.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label78.Location = new System.Drawing.Point(10, 109);
            this.label78.Name = "label78";
            this.label78.Size = new System.Drawing.Size(107, 15);
            this.label78.TabIndex = 61;
            this.label78.Text = "Timeout Error";
            // 
            // label79
            // 
            this.label79.BackColor = System.Drawing.Color.Coral;
            this.label79.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label79.Location = new System.Drawing.Point(10, 142);
            this.label79.Name = "label79";
            this.label79.Size = new System.Drawing.Size(107, 15);
            this.label79.TabIndex = 73;
            this.label79.Text = "FIFO Full";
            // 
            // lbl_CRIMDAQStatusTimeoutErr
            // 
            this.lbl_CRIMDAQStatusTimeoutErr.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusTimeoutErr.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusTimeoutErr.Location = new System.Drawing.Point(117, 109);
            this.lbl_CRIMDAQStatusTimeoutErr.Name = "lbl_CRIMDAQStatusTimeoutErr";
            this.lbl_CRIMDAQStatusTimeoutErr.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusTimeoutErr.TabIndex = 62;
            // 
            // lbl_CRIMDAQStatusFIFONotEmpty
            // 
            this.lbl_CRIMDAQStatusFIFONotEmpty.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusFIFONotEmpty.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusFIFONotEmpty.Location = new System.Drawing.Point(117, 127);
            this.lbl_CRIMDAQStatusFIFONotEmpty.Name = "lbl_CRIMDAQStatusFIFONotEmpty";
            this.lbl_CRIMDAQStatusFIFONotEmpty.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusFIFONotEmpty.TabIndex = 72;
            // 
            // label82
            // 
            this.label82.BackColor = System.Drawing.Color.Coral;
            this.label82.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label82.Location = new System.Drawing.Point(10, 205);
            this.label82.Name = "label82";
            this.label82.Size = new System.Drawing.Size(107, 15);
            this.label82.TabIndex = 63;
            this.label82.Text = "Serializer SYNC";
            // 
            // label83
            // 
            this.label83.BackColor = System.Drawing.Color.Coral;
            this.label83.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label83.Location = new System.Drawing.Point(10, 127);
            this.label83.Name = "label83";
            this.label83.Size = new System.Drawing.Size(107, 15);
            this.label83.TabIndex = 71;
            this.label83.Text = "FIFO Not Empty";
            // 
            // lbl_CRIMDAQStatusSerializerSync
            // 
            this.lbl_CRIMDAQStatusSerializerSync.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusSerializerSync.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusSerializerSync.Location = new System.Drawing.Point(117, 205);
            this.lbl_CRIMDAQStatusSerializerSync.Name = "lbl_CRIMDAQStatusSerializerSync";
            this.lbl_CRIMDAQStatusSerializerSync.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusSerializerSync.TabIndex = 64;
            // 
            // lbl_CRIMDAQStatusTestPulseRcv
            // 
            this.lbl_CRIMDAQStatusTestPulseRcv.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusTestPulseRcv.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusTestPulseRcv.Location = new System.Drawing.Point(117, 268);
            this.lbl_CRIMDAQStatusTestPulseRcv.Name = "lbl_CRIMDAQStatusTestPulseRcv";
            this.lbl_CRIMDAQStatusTestPulseRcv.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusTestPulseRcv.TabIndex = 70;
            // 
            // label88
            // 
            this.label88.BackColor = System.Drawing.Color.Coral;
            this.label88.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label88.Location = new System.Drawing.Point(10, 220);
            this.label88.Name = "label88";
            this.label88.Size = new System.Drawing.Size(107, 15);
            this.label88.TabIndex = 65;
            this.label88.Text = "Deserializer LOCK";
            // 
            // label87
            // 
            this.label87.BackColor = System.Drawing.Color.Coral;
            this.label87.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label87.Location = new System.Drawing.Point(10, 268);
            this.label87.Name = "label87";
            this.label87.Size = new System.Drawing.Size(107, 15);
            this.label87.TabIndex = 69;
            this.label87.Text = "Test pulse rcv";
            // 
            // lbl_CRIMDAQStatusDeserializerLock
            // 
            this.lbl_CRIMDAQStatusDeserializerLock.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusDeserializerLock.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusDeserializerLock.Location = new System.Drawing.Point(117, 220);
            this.lbl_CRIMDAQStatusDeserializerLock.Name = "lbl_CRIMDAQStatusDeserializerLock";
            this.lbl_CRIMDAQStatusDeserializerLock.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusDeserializerLock.TabIndex = 66;
            // 
            // lbl_CRIMDAQStatusPLLLock
            // 
            this.lbl_CRIMDAQStatusPLLLock.BackColor = System.Drawing.Color.White;
            this.lbl_CRIMDAQStatusPLLLock.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CRIMDAQStatusPLLLock.Location = new System.Drawing.Point(117, 253);
            this.lbl_CRIMDAQStatusPLLLock.Name = "lbl_CRIMDAQStatusPLLLock";
            this.lbl_CRIMDAQStatusPLLLock.Size = new System.Drawing.Size(15, 15);
            this.lbl_CRIMDAQStatusPLLLock.TabIndex = 68;
            // 
            // label90
            // 
            this.label90.BackColor = System.Drawing.Color.Coral;
            this.label90.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label90.Location = new System.Drawing.Point(10, 253);
            this.label90.Name = "label90";
            this.label90.Size = new System.Drawing.Size(107, 15);
            this.label90.TabIndex = 67;
            this.label90.Text = "PLL0 LOCK";
            // 
            // groupBoxCRIM_FrameRegisters
            // 
            this.groupBoxCRIM_FrameRegisters.Controls.Add(this.btn_CRIMDAQFrameFIFORegisterWrite);
            this.groupBoxCRIM_FrameRegisters.Controls.Add(this.rtb_CRIMDAQFrameReadDPMBytes);
            this.groupBoxCRIM_FrameRegisters.Controls.Add(this.txt_CRIMDAQFrameReadDPMBytes);
            this.groupBoxCRIM_FrameRegisters.Controls.Add(this.txt_CRIMDAQFrameFIFORegisterAppendMessage);
            this.groupBoxCRIM_FrameRegisters.Controls.Add(this.btn_CRIMDAQFrameReadDPMBytes);
            this.groupBoxCRIM_FrameRegisters.Controls.Add(this.btn_CRIMDAQFrameSendRegister);
            this.groupBoxCRIM_FrameRegisters.Controls.Add(this.btn_CRIMDAQFrameFIFORegisterAppendMessage);
            this.groupBoxCRIM_FrameRegisters.Location = new System.Drawing.Point(156, 178);
            this.groupBoxCRIM_FrameRegisters.Name = "groupBoxCRIM_FrameRegisters";
            this.groupBoxCRIM_FrameRegisters.Size = new System.Drawing.Size(192, 235);
            this.groupBoxCRIM_FrameRegisters.TabIndex = 92;
            this.groupBoxCRIM_FrameRegisters.TabStop = false;
            this.groupBoxCRIM_FrameRegisters.Text = "Frame Registers";
            // 
            // btn_CRIMDAQFrameFIFORegisterWrite
            // 
            this.btn_CRIMDAQFrameFIFORegisterWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMDAQFrameFIFORegisterWrite.Location = new System.Drawing.Point(11, 39);
            this.btn_CRIMDAQFrameFIFORegisterWrite.Name = "btn_CRIMDAQFrameFIFORegisterWrite";
            this.btn_CRIMDAQFrameFIFORegisterWrite.Size = new System.Drawing.Size(85, 20);
            this.btn_CRIMDAQFrameFIFORegisterWrite.TabIndex = 94;
            this.btn_CRIMDAQFrameFIFORegisterWrite.Text = "Write FIFO";
            this.btn_CRIMDAQFrameFIFORegisterWrite.UseVisualStyleBackColor = false;
            this.btn_CRIMDAQFrameFIFORegisterWrite.Click += new System.EventHandler(this.btn_CRIMDAQFrameFIFORegisterWrite_Click);
            // 
            // rtb_CRIMDAQFrameReadDPMBytes
            // 
            this.rtb_CRIMDAQFrameReadDPMBytes.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)));
            this.rtb_CRIMDAQFrameReadDPMBytes.Location = new System.Drawing.Point(10, 85);
            this.rtb_CRIMDAQFrameReadDPMBytes.Name = "rtb_CRIMDAQFrameReadDPMBytes";
            this.rtb_CRIMDAQFrameReadDPMBytes.Size = new System.Drawing.Size(171, 136);
            this.rtb_CRIMDAQFrameReadDPMBytes.TabIndex = 93;
            this.rtb_CRIMDAQFrameReadDPMBytes.Text = "";
            // 
            // txt_CRIMDAQFrameReadDPMBytes
            // 
            this.txt_CRIMDAQFrameReadDPMBytes.Location = new System.Drawing.Point(124, 60);
            this.txt_CRIMDAQFrameReadDPMBytes.Name = "txt_CRIMDAQFrameReadDPMBytes";
            this.txt_CRIMDAQFrameReadDPMBytes.Size = new System.Drawing.Size(57, 20);
            this.txt_CRIMDAQFrameReadDPMBytes.TabIndex = 92;
            // 
            // txt_CRIMDAQFrameFIFORegisterAppendMessage
            // 
            this.txt_CRIMDAQFrameFIFORegisterAppendMessage.Location = new System.Drawing.Point(124, 18);
            this.txt_CRIMDAQFrameFIFORegisterAppendMessage.Name = "txt_CRIMDAQFrameFIFORegisterAppendMessage";
            this.txt_CRIMDAQFrameFIFORegisterAppendMessage.Size = new System.Drawing.Size(57, 20);
            this.txt_CRIMDAQFrameFIFORegisterAppendMessage.TabIndex = 91;
            // 
            // btn_CRIMDAQFrameReadDPMBytes
            // 
            this.btn_CRIMDAQFrameReadDPMBytes.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMDAQFrameReadDPMBytes.Location = new System.Drawing.Point(11, 60);
            this.btn_CRIMDAQFrameReadDPMBytes.Name = "btn_CRIMDAQFrameReadDPMBytes";
            this.btn_CRIMDAQFrameReadDPMBytes.Size = new System.Drawing.Size(115, 20);
            this.btn_CRIMDAQFrameReadDPMBytes.TabIndex = 88;
            this.btn_CRIMDAQFrameReadDPMBytes.Text = "Read DPM bytes->.";
            this.btn_CRIMDAQFrameReadDPMBytes.UseVisualStyleBackColor = false;
            this.btn_CRIMDAQFrameReadDPMBytes.Click += new System.EventHandler(this.btn_CRIMDAQFrameReadDPMBytes_Click);
            // 
            // btn_CRIMDAQFrameSendRegister
            // 
            this.btn_CRIMDAQFrameSendRegister.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMDAQFrameSendRegister.Location = new System.Drawing.Point(96, 39);
            this.btn_CRIMDAQFrameSendRegister.Name = "btn_CRIMDAQFrameSendRegister";
            this.btn_CRIMDAQFrameSendRegister.Size = new System.Drawing.Size(85, 20);
            this.btn_CRIMDAQFrameSendRegister.TabIndex = 87;
            this.btn_CRIMDAQFrameSendRegister.Text = "Send Frame";
            this.btn_CRIMDAQFrameSendRegister.UseVisualStyleBackColor = false;
            this.btn_CRIMDAQFrameSendRegister.Click += new System.EventHandler(this.btn_CRIMDAQFrameSendRegister_Click);
            // 
            // btn_CRIMDAQFrameFIFORegisterAppendMessage
            // 
            this.btn_CRIMDAQFrameFIFORegisterAppendMessage.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMDAQFrameFIFORegisterAppendMessage.Location = new System.Drawing.Point(10, 18);
            this.btn_CRIMDAQFrameFIFORegisterAppendMessage.Name = "btn_CRIMDAQFrameFIFORegisterAppendMessage";
            this.btn_CRIMDAQFrameFIFORegisterAppendMessage.Size = new System.Drawing.Size(115, 20);
            this.btn_CRIMDAQFrameFIFORegisterAppendMessage.TabIndex = 85;
            this.btn_CRIMDAQFrameFIFORegisterAppendMessage.Text = "Append Msg (0x)";
            this.btn_CRIMDAQFrameFIFORegisterAppendMessage.UseVisualStyleBackColor = false;
            this.btn_CRIMDAQFrameFIFORegisterAppendMessage.Click += new System.EventHandler(this.btn_CRIMDAQFrameFIFORegisterAppendMessage_Click);
            // 
            // tabCRIMInterrupterModule
            // 
            this.tabCRIMInterrupterModule.Controls.Add(this.groupBoxCRIM_Interrupter);
            this.tabCRIMInterrupterModule.Location = new System.Drawing.Point(4, 22);
            this.tabCRIMInterrupterModule.Name = "tabCRIMInterrupterModule";
            this.tabCRIMInterrupterModule.Size = new System.Drawing.Size(373, 432);
            this.tabCRIMInterrupterModule.TabIndex = 2;
            this.tabCRIMInterrupterModule.Text = "Interrupter Module";
            this.tabCRIMInterrupterModule.UseVisualStyleBackColor = true;
            // 
            // groupBoxCRIM_Interrupter
            // 
            this.groupBoxCRIM_Interrupter.Controls.Add(this.btn_CRIMInterrupterConfigRead);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.txt_CRIMInterrupterLevels);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.label46);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.label94);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.label53);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.btn_CRIMInterrupterConfigWrite);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.btn_CRIMInterrupterMaskWrite);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.label58);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.txt_CRIMInterrupterVectInp5);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.label97);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.txt_CRIMInterrupterMask);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.label55);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.btn_CRIMInterrupterClearInterrupts);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.txt_CRIMInterrupterVectInp2);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.txt_CRIMInterrupterStatus);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.btn_CRIMInterrupterMaskRead);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.txt_CRIMInterrupterVectInp6);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.label56);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.txt_CRIMInterrupterVectInp3);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.txt_CRIMInterrupterVectInp0);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.label54);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.label95);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.chk_CRIMInterrupterGIE);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.label93);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.label96);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.btn_CRIMInterrupterStatusWrite);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.btn_CRIMInterrupterVectInpWrite);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.txt_CRIMInterrupterVectInp4);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.label92);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.btn_CRIMInterrupterVectInpRead);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.txt_CRIMInterrupterVectInp7);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.txt_CRIMInterrupterVectInp1);
            this.groupBoxCRIM_Interrupter.Controls.Add(this.btn_CRIMInterrupterStatusRead);
            this.groupBoxCRIM_Interrupter.Location = new System.Drawing.Point(9, 6);
            this.groupBoxCRIM_Interrupter.Name = "groupBoxCRIM_Interrupter";
            this.groupBoxCRIM_Interrupter.Size = new System.Drawing.Size(361, 181);
            this.groupBoxCRIM_Interrupter.TabIndex = 141;
            this.groupBoxCRIM_Interrupter.TabStop = false;
            this.groupBoxCRIM_Interrupter.Text = "Hexadecimal Data";
            // 
            // btn_CRIMInterrupterConfigRead
            // 
            this.btn_CRIMInterrupterConfigRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMInterrupterConfigRead.Location = new System.Drawing.Point(137, 54);
            this.btn_CRIMInterrupterConfigRead.Name = "btn_CRIMInterrupterConfigRead";
            this.btn_CRIMInterrupterConfigRead.Size = new System.Drawing.Size(30, 40);
            this.btn_CRIMInterrupterConfigRead.TabIndex = 141;
            this.btn_CRIMInterrupterConfigRead.Text = "R";
            this.btn_CRIMInterrupterConfigRead.UseVisualStyleBackColor = false;
            this.btn_CRIMInterrupterConfigRead.Click += new System.EventHandler(this.btn_CRIMInterrupterConfigRead_Click);
            // 
            // txt_CRIMInterrupterLevels
            // 
            this.txt_CRIMInterrupterLevels.Location = new System.Drawing.Point(81, 74);
            this.txt_CRIMInterrupterLevels.Name = "txt_CRIMInterrupterLevels";
            this.txt_CRIMInterrupterLevels.Size = new System.Drawing.Size(25, 20);
            this.txt_CRIMInterrupterLevels.TabIndex = 140;
            // 
            // label46
            // 
            this.label46.BackColor = System.Drawing.Color.Coral;
            this.label46.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label46.Location = new System.Drawing.Point(15, 16);
            this.label46.Name = "label46";
            this.label46.Size = new System.Drawing.Size(64, 16);
            this.label46.TabIndex = 87;
            this.label46.Text = "Mask";
            this.label46.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label94
            // 
            this.label94.BackColor = System.Drawing.Color.Coral;
            this.label94.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label94.Location = new System.Drawing.Point(196, 136);
            this.label94.Name = "label94";
            this.label94.Size = new System.Drawing.Size(64, 16);
            this.label94.TabIndex = 128;
            this.label94.Text = "Vect Inp 6";
            this.label94.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label53
            // 
            this.label53.BackColor = System.Drawing.Color.Coral;
            this.label53.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label53.Location = new System.Drawing.Point(15, 36);
            this.label53.Name = "label53";
            this.label53.Size = new System.Drawing.Size(64, 16);
            this.label53.TabIndex = 88;
            this.label53.Text = "Status";
            this.label53.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // btn_CRIMInterrupterConfigWrite
            // 
            this.btn_CRIMInterrupterConfigWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMInterrupterConfigWrite.Location = new System.Drawing.Point(107, 54);
            this.btn_CRIMInterrupterConfigWrite.Name = "btn_CRIMInterrupterConfigWrite";
            this.btn_CRIMInterrupterConfigWrite.Size = new System.Drawing.Size(30, 40);
            this.btn_CRIMInterrupterConfigWrite.TabIndex = 96;
            this.btn_CRIMInterrupterConfigWrite.Text = "W";
            this.btn_CRIMInterrupterConfigWrite.UseVisualStyleBackColor = false;
            this.btn_CRIMInterrupterConfigWrite.Click += new System.EventHandler(this.btn_CRIMInterrupterConfigWrite_Click);
            // 
            // btn_CRIMInterrupterMaskWrite
            // 
            this.btn_CRIMInterrupterMaskWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMInterrupterMaskWrite.Location = new System.Drawing.Point(107, 14);
            this.btn_CRIMInterrupterMaskWrite.Name = "btn_CRIMInterrupterMaskWrite";
            this.btn_CRIMInterrupterMaskWrite.Size = new System.Drawing.Size(30, 20);
            this.btn_CRIMInterrupterMaskWrite.TabIndex = 89;
            this.btn_CRIMInterrupterMaskWrite.Text = "W";
            this.btn_CRIMInterrupterMaskWrite.UseVisualStyleBackColor = false;
            this.btn_CRIMInterrupterMaskWrite.Click += new System.EventHandler(this.btn_CRIMInterrupterMaskWrite_Click);
            // 
            // label58
            // 
            this.label58.BackColor = System.Drawing.Color.Coral;
            this.label58.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label58.Location = new System.Drawing.Point(196, 76);
            this.label58.Name = "label58";
            this.label58.Size = new System.Drawing.Size(64, 16);
            this.label58.TabIndex = 116;
            this.label58.Text = "Vect Inp 3";
            this.label58.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // txt_CRIMInterrupterVectInp5
            // 
            this.txt_CRIMInterrupterVectInp5.Location = new System.Drawing.Point(262, 114);
            this.txt_CRIMInterrupterVectInp5.Name = "txt_CRIMInterrupterVectInp5";
            this.txt_CRIMInterrupterVectInp5.Size = new System.Drawing.Size(25, 20);
            this.txt_CRIMInterrupterVectInp5.TabIndex = 127;
            // 
            // label97
            // 
            this.label97.BackColor = System.Drawing.Color.Coral;
            this.label97.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label97.Location = new System.Drawing.Point(15, 76);
            this.label97.Name = "label97";
            this.label97.Size = new System.Drawing.Size(64, 16);
            this.label97.TabIndex = 137;
            this.label97.Text = "Level(1-7)";
            this.label97.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // txt_CRIMInterrupterMask
            // 
            this.txt_CRIMInterrupterMask.Location = new System.Drawing.Point(81, 14);
            this.txt_CRIMInterrupterMask.Name = "txt_CRIMInterrupterMask";
            this.txt_CRIMInterrupterMask.Size = new System.Drawing.Size(25, 20);
            this.txt_CRIMInterrupterMask.TabIndex = 106;
            // 
            // label55
            // 
            this.label55.BackColor = System.Drawing.Color.Coral;
            this.label55.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label55.Location = new System.Drawing.Point(196, 16);
            this.label55.Name = "label55";
            this.label55.Size = new System.Drawing.Size(64, 16);
            this.label55.TabIndex = 95;
            this.label55.Text = "Vect Inp 0";
            this.label55.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // btn_CRIMInterrupterClearInterrupts
            // 
            this.btn_CRIMInterrupterClearInterrupts.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMInterrupterClearInterrupts.Location = new System.Drawing.Point(15, 96);
            this.btn_CRIMInterrupterClearInterrupts.Name = "btn_CRIMInterrupterClearInterrupts";
            this.btn_CRIMInterrupterClearInterrupts.Size = new System.Drawing.Size(153, 20);
            this.btn_CRIMInterrupterClearInterrupts.TabIndex = 102;
            this.btn_CRIMInterrupterClearInterrupts.Text = "Clear pending interrupts";
            this.btn_CRIMInterrupterClearInterrupts.UseVisualStyleBackColor = false;
            this.btn_CRIMInterrupterClearInterrupts.Click += new System.EventHandler(this.btn_CRIMInterrupterClearInterrupts_Click);
            // 
            // txt_CRIMInterrupterVectInp2
            // 
            this.txt_CRIMInterrupterVectInp2.Location = new System.Drawing.Point(262, 54);
            this.txt_CRIMInterrupterVectInp2.Name = "txt_CRIMInterrupterVectInp2";
            this.txt_CRIMInterrupterVectInp2.Size = new System.Drawing.Size(25, 20);
            this.txt_CRIMInterrupterVectInp2.TabIndex = 115;
            // 
            // txt_CRIMInterrupterStatus
            // 
            this.txt_CRIMInterrupterStatus.Location = new System.Drawing.Point(81, 34);
            this.txt_CRIMInterrupterStatus.Name = "txt_CRIMInterrupterStatus";
            this.txt_CRIMInterrupterStatus.Size = new System.Drawing.Size(25, 20);
            this.txt_CRIMInterrupterStatus.TabIndex = 107;
            // 
            // btn_CRIMInterrupterMaskRead
            // 
            this.btn_CRIMInterrupterMaskRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMInterrupterMaskRead.Location = new System.Drawing.Point(137, 14);
            this.btn_CRIMInterrupterMaskRead.Name = "btn_CRIMInterrupterMaskRead";
            this.btn_CRIMInterrupterMaskRead.Size = new System.Drawing.Size(30, 20);
            this.btn_CRIMInterrupterMaskRead.TabIndex = 90;
            this.btn_CRIMInterrupterMaskRead.Text = "R";
            this.btn_CRIMInterrupterMaskRead.UseVisualStyleBackColor = false;
            this.btn_CRIMInterrupterMaskRead.Click += new System.EventHandler(this.btn_CRIMInterrupterMaskRead_Click);
            // 
            // txt_CRIMInterrupterVectInp6
            // 
            this.txt_CRIMInterrupterVectInp6.Location = new System.Drawing.Point(262, 134);
            this.txt_CRIMInterrupterVectInp6.Name = "txt_CRIMInterrupterVectInp6";
            this.txt_CRIMInterrupterVectInp6.Size = new System.Drawing.Size(25, 20);
            this.txt_CRIMInterrupterVectInp6.TabIndex = 131;
            // 
            // label56
            // 
            this.label56.BackColor = System.Drawing.Color.Coral;
            this.label56.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label56.Location = new System.Drawing.Point(196, 36);
            this.label56.Name = "label56";
            this.label56.Size = new System.Drawing.Size(64, 16);
            this.label56.TabIndex = 108;
            this.label56.Text = "Vect Inp 1";
            this.label56.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // txt_CRIMInterrupterVectInp3
            // 
            this.txt_CRIMInterrupterVectInp3.Location = new System.Drawing.Point(262, 74);
            this.txt_CRIMInterrupterVectInp3.Name = "txt_CRIMInterrupterVectInp3";
            this.txt_CRIMInterrupterVectInp3.Size = new System.Drawing.Size(25, 20);
            this.txt_CRIMInterrupterVectInp3.TabIndex = 119;
            // 
            // txt_CRIMInterrupterVectInp0
            // 
            this.txt_CRIMInterrupterVectInp0.Location = new System.Drawing.Point(262, 14);
            this.txt_CRIMInterrupterVectInp0.Name = "txt_CRIMInterrupterVectInp0";
            this.txt_CRIMInterrupterVectInp0.Size = new System.Drawing.Size(25, 20);
            this.txt_CRIMInterrupterVectInp0.TabIndex = 101;
            // 
            // label54
            // 
            this.label54.BackColor = System.Drawing.Color.Coral;
            this.label54.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label54.Location = new System.Drawing.Point(15, 56);
            this.label54.Name = "label54";
            this.label54.Size = new System.Drawing.Size(64, 16);
            this.label54.TabIndex = 94;
            this.label54.Text = "Global IE";
            this.label54.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label95
            // 
            this.label95.BackColor = System.Drawing.Color.Coral;
            this.label95.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label95.Location = new System.Drawing.Point(196, 116);
            this.label95.Name = "label95";
            this.label95.Size = new System.Drawing.Size(64, 16);
            this.label95.TabIndex = 124;
            this.label95.Text = "Vect Inp 5";
            this.label95.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // chk_CRIMInterrupterGIE
            // 
            this.chk_CRIMInterrupterGIE.AutoSize = true;
            this.chk_CRIMInterrupterGIE.Location = new System.Drawing.Point(87, 58);
            this.chk_CRIMInterrupterGIE.Name = "chk_CRIMInterrupterGIE";
            this.chk_CRIMInterrupterGIE.Size = new System.Drawing.Size(15, 14);
            this.chk_CRIMInterrupterGIE.TabIndex = 136;
            this.chk_CRIMInterrupterGIE.UseVisualStyleBackColor = true;
            // 
            // label93
            // 
            this.label93.BackColor = System.Drawing.Color.Coral;
            this.label93.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label93.Location = new System.Drawing.Point(196, 156);
            this.label93.Name = "label93";
            this.label93.Size = new System.Drawing.Size(64, 16);
            this.label93.TabIndex = 132;
            this.label93.Text = "Vect Inp 7";
            this.label93.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label96
            // 
            this.label96.BackColor = System.Drawing.Color.Coral;
            this.label96.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label96.Location = new System.Drawing.Point(196, 96);
            this.label96.Name = "label96";
            this.label96.Size = new System.Drawing.Size(64, 16);
            this.label96.TabIndex = 120;
            this.label96.Text = "Vect Inp 4";
            this.label96.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // btn_CRIMInterrupterStatusWrite
            // 
            this.btn_CRIMInterrupterStatusWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMInterrupterStatusWrite.Location = new System.Drawing.Point(107, 34);
            this.btn_CRIMInterrupterStatusWrite.Name = "btn_CRIMInterrupterStatusWrite";
            this.btn_CRIMInterrupterStatusWrite.Size = new System.Drawing.Size(30, 20);
            this.btn_CRIMInterrupterStatusWrite.TabIndex = 92;
            this.btn_CRIMInterrupterStatusWrite.Text = "W";
            this.btn_CRIMInterrupterStatusWrite.UseVisualStyleBackColor = false;
            this.btn_CRIMInterrupterStatusWrite.Click += new System.EventHandler(this.btn_CRIMInterrupterStatusWrite_Click);
            // 
            // btn_CRIMInterrupterVectInpWrite
            // 
            this.btn_CRIMInterrupterVectInpWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMInterrupterVectInpWrite.Location = new System.Drawing.Point(289, 14);
            this.btn_CRIMInterrupterVectInpWrite.Name = "btn_CRIMInterrupterVectInpWrite";
            this.btn_CRIMInterrupterVectInpWrite.Size = new System.Drawing.Size(30, 158);
            this.btn_CRIMInterrupterVectInpWrite.TabIndex = 98;
            this.btn_CRIMInterrupterVectInpWrite.Text = "W";
            this.btn_CRIMInterrupterVectInpWrite.UseVisualStyleBackColor = false;
            this.btn_CRIMInterrupterVectInpWrite.Click += new System.EventHandler(this.btn_CRIMInterrupterVectInpWrite_Click);
            // 
            // txt_CRIMInterrupterVectInp4
            // 
            this.txt_CRIMInterrupterVectInp4.Location = new System.Drawing.Point(262, 94);
            this.txt_CRIMInterrupterVectInp4.Name = "txt_CRIMInterrupterVectInp4";
            this.txt_CRIMInterrupterVectInp4.Size = new System.Drawing.Size(25, 20);
            this.txt_CRIMInterrupterVectInp4.TabIndex = 123;
            // 
            // label92
            // 
            this.label92.BackColor = System.Drawing.Color.Coral;
            this.label92.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label92.Location = new System.Drawing.Point(196, 56);
            this.label92.Name = "label92";
            this.label92.Size = new System.Drawing.Size(64, 16);
            this.label92.TabIndex = 112;
            this.label92.Text = "Vect Inp 2";
            this.label92.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // btn_CRIMInterrupterVectInpRead
            // 
            this.btn_CRIMInterrupterVectInpRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMInterrupterVectInpRead.Location = new System.Drawing.Point(319, 14);
            this.btn_CRIMInterrupterVectInpRead.Name = "btn_CRIMInterrupterVectInpRead";
            this.btn_CRIMInterrupterVectInpRead.Size = new System.Drawing.Size(30, 158);
            this.btn_CRIMInterrupterVectInpRead.TabIndex = 99;
            this.btn_CRIMInterrupterVectInpRead.Text = "R";
            this.btn_CRIMInterrupterVectInpRead.UseVisualStyleBackColor = false;
            this.btn_CRIMInterrupterVectInpRead.Click += new System.EventHandler(this.btn_CRIMInterrupterVectInpRead_Click);
            // 
            // txt_CRIMInterrupterVectInp7
            // 
            this.txt_CRIMInterrupterVectInp7.Location = new System.Drawing.Point(262, 154);
            this.txt_CRIMInterrupterVectInp7.Name = "txt_CRIMInterrupterVectInp7";
            this.txt_CRIMInterrupterVectInp7.Size = new System.Drawing.Size(25, 20);
            this.txt_CRIMInterrupterVectInp7.TabIndex = 135;
            // 
            // txt_CRIMInterrupterVectInp1
            // 
            this.txt_CRIMInterrupterVectInp1.Location = new System.Drawing.Point(262, 34);
            this.txt_CRIMInterrupterVectInp1.Name = "txt_CRIMInterrupterVectInp1";
            this.txt_CRIMInterrupterVectInp1.Size = new System.Drawing.Size(25, 20);
            this.txt_CRIMInterrupterVectInp1.TabIndex = 111;
            // 
            // btn_CRIMInterrupterStatusRead
            // 
            this.btn_CRIMInterrupterStatusRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMInterrupterStatusRead.Location = new System.Drawing.Point(137, 34);
            this.btn_CRIMInterrupterStatusRead.Name = "btn_CRIMInterrupterStatusRead";
            this.btn_CRIMInterrupterStatusRead.Size = new System.Drawing.Size(30, 20);
            this.btn_CRIMInterrupterStatusRead.TabIndex = 93;
            this.btn_CRIMInterrupterStatusRead.Text = "R";
            this.btn_CRIMInterrupterStatusRead.UseVisualStyleBackColor = false;
            this.btn_CRIMInterrupterStatusRead.Click += new System.EventHandler(this.btn_CRIMInterrupterStatusRead_Click);
            // 
            // tabCRIMFELoopQuery
            // 
            this.tabCRIMFELoopQuery.Controls.Add(this.chk_CRIMFELoopQueryMatch);
            this.tabCRIMFELoopQuery.Controls.Add(this.txt_CRIMFELoopQueryNTimes);
            this.tabCRIMFELoopQuery.Controls.Add(this.label48);
            this.tabCRIMFELoopQuery.Controls.Add(this.txt_CRIMFELoopQueryCrocBaseAddr);
            this.tabCRIMFELoopQuery.Controls.Add(this.label57);
            this.tabCRIMFELoopQuery.Controls.Add(this.txt_CRIMFELoopQueryMatch);
            this.tabCRIMFELoopQuery.Controls.Add(this.rtb_CRIMFELoopQueryDisplay);
            this.tabCRIMFELoopQuery.Controls.Add(this.btn_CRIMFELoopQueryDoQuery);
            this.tabCRIMFELoopQuery.Controls.Add(this.btn_CRIMFELoopQueryConfigure);
            this.tabCRIMFELoopQuery.Location = new System.Drawing.Point(4, 22);
            this.tabCRIMFELoopQuery.Name = "tabCRIMFELoopQuery";
            this.tabCRIMFELoopQuery.Size = new System.Drawing.Size(373, 432);
            this.tabCRIMFELoopQuery.TabIndex = 3;
            this.tabCRIMFELoopQuery.Text = "FE Loop Query";
            this.tabCRIMFELoopQuery.UseVisualStyleBackColor = true;
            // 
            // chk_CRIMFELoopQueryMatch
            // 
            this.chk_CRIMFELoopQueryMatch.AutoSize = true;
            this.chk_CRIMFELoopQueryMatch.Location = new System.Drawing.Point(346, 55);
            this.chk_CRIMFELoopQueryMatch.Name = "chk_CRIMFELoopQueryMatch";
            this.chk_CRIMFELoopQueryMatch.Size = new System.Drawing.Size(15, 14);
            this.chk_CRIMFELoopQueryMatch.TabIndex = 117;
            this.chk_CRIMFELoopQueryMatch.UseVisualStyleBackColor = true;
            // 
            // txt_CRIMFELoopQueryNTimes
            // 
            this.txt_CRIMFELoopQueryNTimes.Location = new System.Drawing.Point(305, 32);
            this.txt_CRIMFELoopQueryNTimes.Name = "txt_CRIMFELoopQueryNTimes";
            this.txt_CRIMFELoopQueryNTimes.Size = new System.Drawing.Size(56, 20);
            this.txt_CRIMFELoopQueryNTimes.TabIndex = 116;
            // 
            // label48
            // 
            this.label48.BackColor = System.Drawing.Color.Coral;
            this.label48.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label48.Location = new System.Drawing.Point(9, 34);
            this.label48.Name = "label48";
            this.label48.Size = new System.Drawing.Size(96, 16);
            this.label48.TabIndex = 112;
            this.label48.Text = "Use CROC Addr";
            this.label48.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // txt_CRIMFELoopQueryCrocBaseAddr
            // 
            this.txt_CRIMFELoopQueryCrocBaseAddr.Location = new System.Drawing.Point(105, 32);
            this.txt_CRIMFELoopQueryCrocBaseAddr.Name = "txt_CRIMFELoopQueryCrocBaseAddr";
            this.txt_CRIMFELoopQueryCrocBaseAddr.Size = new System.Drawing.Size(25, 20);
            this.txt_CRIMFELoopQueryCrocBaseAddr.TabIndex = 113;
            // 
            // label57
            // 
            this.label57.BackColor = System.Drawing.Color.Coral;
            this.label57.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label57.Location = new System.Drawing.Point(9, 55);
            this.label57.Name = "label57";
            this.label57.Size = new System.Drawing.Size(96, 16);
            this.label57.TabIndex = 114;
            this.label57.Text = "Match FE IDs";
            this.label57.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // txt_CRIMFELoopQueryMatch
            // 
            this.txt_CRIMFELoopQueryMatch.Location = new System.Drawing.Point(105, 53);
            this.txt_CRIMFELoopQueryMatch.Name = "txt_CRIMFELoopQueryMatch";
            this.txt_CRIMFELoopQueryMatch.Size = new System.Drawing.Size(240, 20);
            this.txt_CRIMFELoopQueryMatch.TabIndex = 115;
            this.txt_CRIMFELoopQueryMatch.Text = "FE10 FE9 FE8 FE7 FE6 FE5 FE4 FE3 FE2 FE1";
            // 
            // rtb_CRIMFELoopQueryDisplay
            // 
            this.rtb_CRIMFELoopQueryDisplay.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)));
            this.rtb_CRIMFELoopQueryDisplay.Location = new System.Drawing.Point(9, 106);
            this.rtb_CRIMFELoopQueryDisplay.Name = "rtb_CRIMFELoopQueryDisplay";
            this.rtb_CRIMFELoopQueryDisplay.Size = new System.Drawing.Size(352, 312);
            this.rtb_CRIMFELoopQueryDisplay.TabIndex = 106;
            this.rtb_CRIMFELoopQueryDisplay.Text = "";
            // 
            // btn_CRIMFELoopQueryDoQuery
            // 
            this.btn_CRIMFELoopQueryDoQuery.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMFELoopQueryDoQuery.Location = new System.Drawing.Point(145, 31);
            this.btn_CRIMFELoopQueryDoQuery.Name = "btn_CRIMFELoopQueryDoQuery";
            this.btn_CRIMFELoopQueryDoQuery.Size = new System.Drawing.Size(160, 20);
            this.btn_CRIMFELoopQueryDoQuery.TabIndex = 104;
            this.btn_CRIMFELoopQueryDoQuery.Text = "START Query FEs (N times)";
            this.btn_CRIMFELoopQueryDoQuery.UseVisualStyleBackColor = false;
            this.btn_CRIMFELoopQueryDoQuery.Click += new System.EventHandler(this.btn_CRIMFELoopQueryDoQuery_Click);
            // 
            // btn_CRIMFELoopQueryConfigure
            // 
            this.btn_CRIMFELoopQueryConfigure.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMFELoopQueryConfigure.Location = new System.Drawing.Point(9, 10);
            this.btn_CRIMFELoopQueryConfigure.Name = "btn_CRIMFELoopQueryConfigure";
            this.btn_CRIMFELoopQueryConfigure.Size = new System.Drawing.Size(352, 20);
            this.btn_CRIMFELoopQueryConfigure.TabIndex = 103;
            this.btn_CRIMFELoopQueryConfigure.Text = "Config CRIM for FE Loop Query";
            this.btn_CRIMFELoopQueryConfigure.UseVisualStyleBackColor = false;
            this.btn_CRIMFELoopQueryConfigure.Click += new System.EventHandler(this.btn_CRIMFELoopQueryConfigure_Click);
            // 
            // lblCRIM_CRIMID
            // 
            this.lblCRIM_CRIMID.BackColor = System.Drawing.Color.White;
            this.lblCRIM_CRIMID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCRIM_CRIMID.Location = new System.Drawing.Point(54, 16);
            this.lblCRIM_CRIMID.Name = "lblCRIM_CRIMID";
            this.lblCRIM_CRIMID.Size = new System.Drawing.Size(30, 18);
            this.lblCRIM_CRIMID.TabIndex = 90;
            // 
            // label47
            // 
            this.label47.BackColor = System.Drawing.Color.Coral;
            this.label47.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label47.Location = new System.Drawing.Point(16, 16);
            this.label47.Name = "label47";
            this.label47.Size = new System.Drawing.Size(40, 18);
            this.label47.TabIndex = 89;
            this.label47.Text = "CRIM";
            // 
            // btn_CRIMAdvancedGUI
            // 
            this.btn_CRIMAdvancedGUI.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMAdvancedGUI.Location = new System.Drawing.Point(248, 16);
            this.btn_CRIMAdvancedGUI.Name = "btn_CRIMAdvancedGUI";
            this.btn_CRIMAdvancedGUI.Size = new System.Drawing.Size(120, 20);
            this.btn_CRIMAdvancedGUI.TabIndex = 88;
            this.btn_CRIMAdvancedGUI.Text = "Show Advanced GUI";
            this.btn_CRIMAdvancedGUI.UseVisualStyleBackColor = false;
            this.btn_CRIMAdvancedGUI.Click += new System.EventHandler(this.btn_CRIMAdvancedGUI_Click);
            // 
            // btn_CRIMReportGateAlignmentsAllCROCs
            // 
            this.btn_CRIMReportGateAlignmentsAllCROCs.BackColor = System.Drawing.Color.Coral;
            this.btn_CRIMReportGateAlignmentsAllCROCs.Location = new System.Drawing.Point(87, 16);
            this.btn_CRIMReportGateAlignmentsAllCROCs.Name = "btn_CRIMReportGateAlignmentsAllCROCs";
            this.btn_CRIMReportGateAlignmentsAllCROCs.Size = new System.Drawing.Size(155, 20);
            this.btn_CRIMReportGateAlignmentsAllCROCs.TabIndex = 87;
            this.btn_CRIMReportGateAlignmentsAllCROCs.Text = "Report Alignments All CROCs";
            this.btn_CRIMReportGateAlignmentsAllCROCs.UseVisualStyleBackColor = false;
            this.btn_CRIMReportGateAlignmentsAllCROCs.Visible = false;
            this.btn_CRIMReportGateAlignmentsAllCROCs.Click += new System.EventHandler(this.btn_CRIMReportGateAlignmentsAllCROCs_Click);
            // 
            // tabCROC
            // 
            this.tabCROC.Controls.Add(this.groupBoxCROC_FEBGateDelays);
            this.tabCROC.Controls.Add(this.groupBoxCROC_LoopDelay);
            this.tabCROC.Controls.Add(this.groupBoxCROC_FastCommand);
            this.tabCROC.Controls.Add(this.groupBoxCROC_ResetTPMaskReg);
            this.tabCROC.Controls.Add(this.groupBoxCROC_TimingSetup);
            this.tabCROC.Controls.Add(this.groupBoxCROC_FLASH);
            this.tabCROC.Controls.Add(this.btn_CROCAdvancedGUI);
            this.tabCROC.Controls.Add(this.lblCROC_CROCID);
            this.tabCROC.Controls.Add(this.label12);
            this.tabCROC.Controls.Add(this.label15);
            this.tabCROC.Controls.Add(this.label17);
            this.tabCROC.Controls.Add(this.label18);
            this.tabCROC.Controls.Add(this.label19);
            this.tabCROC.Location = new System.Drawing.Point(4, 22);
            this.tabCROC.Name = "tabCROC";
            this.tabCROC.Size = new System.Drawing.Size(899, 502);
            this.tabCROC.TabIndex = 5;
            this.tabCROC.Text = "CROC";
            this.tabCROC.UseVisualStyleBackColor = true;
            // 
            // groupBoxCROC_FEBGateDelays
            // 
            this.groupBoxCROC_FEBGateDelays.Controls.Add(this.btn_CROCReportGateAlignmentsAllCROCsAndChains);
            this.groupBoxCROC_FEBGateDelays.Controls.Add(this.txt_CROCGateDelayLoopChannel);
            this.groupBoxCROC_FEBGateDelays.Controls.Add(this.txt_CROCGateDelayLoopGateStartValue);
            this.groupBoxCROC_FEBGateDelays.Controls.Add(this.label45);
            this.groupBoxCROC_FEBGateDelays.Controls.Add(this.txt_CROCGateDelayLoopLoadTimerValue);
            this.groupBoxCROC_FEBGateDelays.Controls.Add(this.label31);
            this.groupBoxCROC_FEBGateDelays.Controls.Add(this.txt_CROCGateDelayLoopN);
            this.groupBoxCROC_FEBGateDelays.Controls.Add(this.label41);
            this.groupBoxCROC_FEBGateDelays.Controls.Add(this.btn_CROCReportGateAlignments);
            this.groupBoxCROC_FEBGateDelays.Location = new System.Drawing.Point(136, 293);
            this.groupBoxCROC_FEBGateDelays.Name = "groupBoxCROC_FEBGateDelays";
            this.groupBoxCROC_FEBGateDelays.Size = new System.Drawing.Size(188, 144);
            this.groupBoxCROC_FEBGateDelays.TabIndex = 86;
            this.groupBoxCROC_FEBGateDelays.TabStop = false;
            this.groupBoxCROC_FEBGateDelays.Text = "Channel FEB Gate Delays  ";
            this.groupBoxCROC_FEBGateDelays.Visible = false;
            // 
            // btn_CROCReportGateAlignmentsAllCROCsAndChains
            // 
            this.btn_CROCReportGateAlignmentsAllCROCsAndChains.BackColor = System.Drawing.Color.Coral;
            this.btn_CROCReportGateAlignmentsAllCROCsAndChains.Location = new System.Drawing.Point(9, 97);
            this.btn_CROCReportGateAlignmentsAllCROCsAndChains.Name = "btn_CROCReportGateAlignmentsAllCROCsAndChains";
            this.btn_CROCReportGateAlignmentsAllCROCsAndChains.Size = new System.Drawing.Size(170, 20);
            this.btn_CROCReportGateAlignmentsAllCROCsAndChains.TabIndex = 86;
            this.btn_CROCReportGateAlignmentsAllCROCsAndChains.Text = "Report Alignments All Chains";
            this.btn_CROCReportGateAlignmentsAllCROCsAndChains.UseVisualStyleBackColor = false;
            this.btn_CROCReportGateAlignmentsAllCROCsAndChains.Click += new System.EventHandler(this.btn_CROCReportGateAlignmentsAllCROCsAndChains_Click);
            // 
            // txt_CROCGateDelayLoopChannel
            // 
            this.txt_CROCGateDelayLoopChannel.Location = new System.Drawing.Point(143, 14);
            this.txt_CROCGateDelayLoopChannel.Name = "txt_CROCGateDelayLoopChannel";
            this.txt_CROCGateDelayLoopChannel.Size = new System.Drawing.Size(36, 20);
            this.txt_CROCGateDelayLoopChannel.TabIndex = 85;
            this.txt_CROCGateDelayLoopChannel.Text = "1";
            // 
            // txt_CROCGateDelayLoopGateStartValue
            // 
            this.txt_CROCGateDelayLoopGateStartValue.Location = new System.Drawing.Point(123, 71);
            this.txt_CROCGateDelayLoopGateStartValue.Name = "txt_CROCGateDelayLoopGateStartValue";
            this.txt_CROCGateDelayLoopGateStartValue.Size = new System.Drawing.Size(56, 20);
            this.txt_CROCGateDelayLoopGateStartValue.TabIndex = 83;
            this.txt_CROCGateDelayLoopGateStartValue.Text = "63500";
            // 
            // label45
            // 
            this.label45.BackColor = System.Drawing.Color.Coral;
            this.label45.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label45.Location = new System.Drawing.Point(9, 73);
            this.label45.Name = "label45";
            this.label45.Size = new System.Drawing.Size(117, 16);
            this.label45.TabIndex = 84;
            this.label45.Text = "Gate Start Value";
            // 
            // txt_CROCGateDelayLoopLoadTimerValue
            // 
            this.txt_CROCGateDelayLoopLoadTimerValue.Location = new System.Drawing.Point(123, 53);
            this.txt_CROCGateDelayLoopLoadTimerValue.Name = "txt_CROCGateDelayLoopLoadTimerValue";
            this.txt_CROCGateDelayLoopLoadTimerValue.Size = new System.Drawing.Size(56, 20);
            this.txt_CROCGateDelayLoopLoadTimerValue.TabIndex = 81;
            this.txt_CROCGateDelayLoopLoadTimerValue.Text = "15";
            // 
            // label31
            // 
            this.label31.BackColor = System.Drawing.Color.Coral;
            this.label31.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label31.Location = new System.Drawing.Point(9, 55);
            this.label31.Name = "label31";
            this.label31.Size = new System.Drawing.Size(117, 16);
            this.label31.TabIndex = 82;
            this.label31.Text = "Load Timer Value";
            // 
            // txt_CROCGateDelayLoopN
            // 
            this.txt_CROCGateDelayLoopN.Location = new System.Drawing.Point(123, 35);
            this.txt_CROCGateDelayLoopN.Name = "txt_CROCGateDelayLoopN";
            this.txt_CROCGateDelayLoopN.Size = new System.Drawing.Size(56, 20);
            this.txt_CROCGateDelayLoopN.TabIndex = 63;
            this.txt_CROCGateDelayLoopN.Text = "5";
            // 
            // label41
            // 
            this.label41.BackColor = System.Drawing.Color.Coral;
            this.label41.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label41.Location = new System.Drawing.Point(8, 37);
            this.label41.Name = "label41";
            this.label41.Size = new System.Drawing.Size(118, 16);
            this.label41.TabIndex = 80;
            this.label41.Text = "N of Measurements";
            // 
            // btn_CROCReportGateAlignments
            // 
            this.btn_CROCReportGateAlignments.BackColor = System.Drawing.Color.Coral;
            this.btn_CROCReportGateAlignments.Location = new System.Drawing.Point(7, 14);
            this.btn_CROCReportGateAlignments.Name = "btn_CROCReportGateAlignments";
            this.btn_CROCReportGateAlignments.Size = new System.Drawing.Size(130, 20);
            this.btn_CROCReportGateAlignments.TabIndex = 78;
            this.btn_CROCReportGateAlignments.Text = "Report Alignments Ch#";
            this.btn_CROCReportGateAlignments.UseVisualStyleBackColor = false;
            this.btn_CROCReportGateAlignments.Click += new System.EventHandler(this.btn_CROCReportGateDelays_Click);
            // 
            // groupBoxCROC_LoopDelay
            // 
            this.groupBoxCROC_LoopDelay.Controls.Add(this.btn_CROCLoopDelayClear);
            this.groupBoxCROC_LoopDelay.Controls.Add(this.lbl_CROCLoopDelayCh4);
            this.groupBoxCROC_LoopDelay.Controls.Add(this.label43);
            this.groupBoxCROC_LoopDelay.Controls.Add(this.lbl_CROCLoopDelayCh3);
            this.groupBoxCROC_LoopDelay.Controls.Add(this.label39);
            this.groupBoxCROC_LoopDelay.Controls.Add(this.lbl_CROCLoopDelayCh2);
            this.groupBoxCROC_LoopDelay.Controls.Add(this.label35);
            this.groupBoxCROC_LoopDelay.Controls.Add(this.lbl_CROCLoopDelayCh1);
            this.groupBoxCROC_LoopDelay.Controls.Add(this.label23);
            this.groupBoxCROC_LoopDelay.Controls.Add(this.btn_CROCLoopDelayRead);
            this.groupBoxCROC_LoopDelay.Location = new System.Drawing.Point(16, 299);
            this.groupBoxCROC_LoopDelay.Name = "groupBoxCROC_LoopDelay";
            this.groupBoxCROC_LoopDelay.Size = new System.Drawing.Size(114, 138);
            this.groupBoxCROC_LoopDelay.TabIndex = 63;
            this.groupBoxCROC_LoopDelay.TabStop = false;
            this.groupBoxCROC_LoopDelay.Text = "Loop Delay";
            this.groupBoxCROC_LoopDelay.Visible = false;
            // 
            // btn_CROCLoopDelayClear
            // 
            this.btn_CROCLoopDelayClear.BackColor = System.Drawing.Color.Coral;
            this.btn_CROCLoopDelayClear.Location = new System.Drawing.Point(7, 115);
            this.btn_CROCLoopDelayClear.Name = "btn_CROCLoopDelayClear";
            this.btn_CROCLoopDelayClear.Size = new System.Drawing.Size(101, 20);
            this.btn_CROCLoopDelayClear.TabIndex = 86;
            this.btn_CROCLoopDelayClear.Text = "Clear Loop Delay";
            this.btn_CROCLoopDelayClear.UseVisualStyleBackColor = false;
            this.btn_CROCLoopDelayClear.Click += new System.EventHandler(this.btn_CROCLoopDelayClear_Click);
            // 
            // lbl_CROCLoopDelayCh4
            // 
            this.lbl_CROCLoopDelayCh4.BackColor = System.Drawing.Color.White;
            this.lbl_CROCLoopDelayCh4.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CROCLoopDelayCh4.Location = new System.Drawing.Point(37, 94);
            this.lbl_CROCLoopDelayCh4.Name = "lbl_CROCLoopDelayCh4";
            this.lbl_CROCLoopDelayCh4.Size = new System.Drawing.Size(70, 18);
            this.lbl_CROCLoopDelayCh4.TabIndex = 85;
            // 
            // label43
            // 
            this.label43.BackColor = System.Drawing.Color.Coral;
            this.label43.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label43.Location = new System.Drawing.Point(8, 95);
            this.label43.Name = "label43";
            this.label43.Size = new System.Drawing.Size(30, 16);
            this.label43.TabIndex = 84;
            this.label43.Text = "Ch4";
            // 
            // lbl_CROCLoopDelayCh3
            // 
            this.lbl_CROCLoopDelayCh3.BackColor = System.Drawing.Color.White;
            this.lbl_CROCLoopDelayCh3.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CROCLoopDelayCh3.Location = new System.Drawing.Point(37, 75);
            this.lbl_CROCLoopDelayCh3.Name = "lbl_CROCLoopDelayCh3";
            this.lbl_CROCLoopDelayCh3.Size = new System.Drawing.Size(70, 18);
            this.lbl_CROCLoopDelayCh3.TabIndex = 83;
            // 
            // label39
            // 
            this.label39.BackColor = System.Drawing.Color.Coral;
            this.label39.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label39.Location = new System.Drawing.Point(8, 76);
            this.label39.Name = "label39";
            this.label39.Size = new System.Drawing.Size(30, 16);
            this.label39.TabIndex = 82;
            this.label39.Text = "Ch3";
            // 
            // lbl_CROCLoopDelayCh2
            // 
            this.lbl_CROCLoopDelayCh2.BackColor = System.Drawing.Color.White;
            this.lbl_CROCLoopDelayCh2.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CROCLoopDelayCh2.Location = new System.Drawing.Point(37, 56);
            this.lbl_CROCLoopDelayCh2.Name = "lbl_CROCLoopDelayCh2";
            this.lbl_CROCLoopDelayCh2.Size = new System.Drawing.Size(70, 18);
            this.lbl_CROCLoopDelayCh2.TabIndex = 81;
            // 
            // label35
            // 
            this.label35.BackColor = System.Drawing.Color.Coral;
            this.label35.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label35.Location = new System.Drawing.Point(8, 57);
            this.label35.Name = "label35";
            this.label35.Size = new System.Drawing.Size(30, 16);
            this.label35.TabIndex = 80;
            this.label35.Text = "Ch2";
            // 
            // lbl_CROCLoopDelayCh1
            // 
            this.lbl_CROCLoopDelayCh1.BackColor = System.Drawing.Color.White;
            this.lbl_CROCLoopDelayCh1.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CROCLoopDelayCh1.Location = new System.Drawing.Point(36, 37);
            this.lbl_CROCLoopDelayCh1.Name = "lbl_CROCLoopDelayCh1";
            this.lbl_CROCLoopDelayCh1.Size = new System.Drawing.Size(70, 18);
            this.lbl_CROCLoopDelayCh1.TabIndex = 79;
            // 
            // label23
            // 
            this.label23.BackColor = System.Drawing.Color.Coral;
            this.label23.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label23.Location = new System.Drawing.Point(7, 38);
            this.label23.Name = "label23";
            this.label23.Size = new System.Drawing.Size(30, 16);
            this.label23.TabIndex = 64;
            this.label23.Text = "Ch1";
            // 
            // btn_CROCLoopDelayRead
            // 
            this.btn_CROCLoopDelayRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CROCLoopDelayRead.Location = new System.Drawing.Point(7, 15);
            this.btn_CROCLoopDelayRead.Name = "btn_CROCLoopDelayRead";
            this.btn_CROCLoopDelayRead.Size = new System.Drawing.Size(101, 20);
            this.btn_CROCLoopDelayRead.TabIndex = 78;
            this.btn_CROCLoopDelayRead.Text = "Read Loop Delay";
            this.btn_CROCLoopDelayRead.UseVisualStyleBackColor = false;
            this.btn_CROCLoopDelayRead.Click += new System.EventHandler(this.btn_CROCLoopDelayRead_Click);
            // 
            // groupBoxCROC_FastCommand
            // 
            this.groupBoxCROC_FastCommand.Controls.Add(this.cmb_CROCFastCommand);
            this.groupBoxCROC_FastCommand.Controls.Add(this.btn_CROCFastCommand);
            this.groupBoxCROC_FastCommand.Location = new System.Drawing.Point(16, 231);
            this.groupBoxCROC_FastCommand.Name = "groupBoxCROC_FastCommand";
            this.groupBoxCROC_FastCommand.Size = new System.Drawing.Size(114, 67);
            this.groupBoxCROC_FastCommand.TabIndex = 62;
            this.groupBoxCROC_FastCommand.TabStop = false;
            this.groupBoxCROC_FastCommand.Text = "Fast Command";
            this.groupBoxCROC_FastCommand.Visible = false;
            // 
            // cmb_CROCFastCommand
            // 
            this.cmb_CROCFastCommand.FormattingEnabled = true;
            this.cmb_CROCFastCommand.Items.AddRange(new object[] {
            "OpenGate",
            "ResetFPGA",
            "ResetTimer",
            "LoadTimer",
            "TrigFound",
            "TrigRearm",
            "QueryFPGA"});
            this.cmb_CROCFastCommand.Location = new System.Drawing.Point(7, 19);
            this.cmb_CROCFastCommand.Name = "cmb_CROCFastCommand";
            this.cmb_CROCFastCommand.Size = new System.Drawing.Size(101, 21);
            this.cmb_CROCFastCommand.TabIndex = 63;
            this.cmb_CROCFastCommand.Text = "Fast Command";
            // 
            // btn_CROCFastCommand
            // 
            this.btn_CROCFastCommand.BackColor = System.Drawing.Color.Coral;
            this.btn_CROCFastCommand.Location = new System.Drawing.Point(6, 42);
            this.btn_CROCFastCommand.Name = "btn_CROCFastCommand";
            this.btn_CROCFastCommand.Size = new System.Drawing.Size(102, 20);
            this.btn_CROCFastCommand.TabIndex = 77;
            this.btn_CROCFastCommand.Text = "Send Fast Cmd";
            this.btn_CROCFastCommand.UseVisualStyleBackColor = false;
            this.btn_CROCFastCommand.Click += new System.EventHandler(this.btn_CROCFastCommand_Click);
            // 
            // groupBoxCROC_ResetTPMaskReg
            // 
            this.groupBoxCROC_ResetTPMaskReg.Controls.Add(this.btn_CROCTPSend);
            this.groupBoxCROC_ResetTPMaskReg.Controls.Add(this.btn_CROCResetSend);
            this.groupBoxCROC_ResetTPMaskReg.Controls.Add(this.btn_CROCResetTPWrite);
            this.groupBoxCROC_ResetTPMaskReg.Controls.Add(this.lbl_CROCResetTPRead);
            this.groupBoxCROC_ResetTPMaskReg.Controls.Add(this.btn_CROCResetTPRead);
            this.groupBoxCROC_ResetTPMaskReg.Controls.Add(this.chk_CROCTPulseCh4);
            this.groupBoxCROC_ResetTPMaskReg.Controls.Add(this.chk_CROCResetCh4);
            this.groupBoxCROC_ResetTPMaskReg.Controls.Add(this.chk_CROCTPulseCh3);
            this.groupBoxCROC_ResetTPMaskReg.Controls.Add(this.chk_CROCResetCh3);
            this.groupBoxCROC_ResetTPMaskReg.Controls.Add(this.chk_CROCTPulseCh2);
            this.groupBoxCROC_ResetTPMaskReg.Controls.Add(this.chk_CROCResetCh2);
            this.groupBoxCROC_ResetTPMaskReg.Controls.Add(this.chk_CROCTPulseCh1);
            this.groupBoxCROC_ResetTPMaskReg.Controls.Add(this.chk_CROCResetCh1);
            this.groupBoxCROC_ResetTPMaskReg.Location = new System.Drawing.Point(136, 120);
            this.groupBoxCROC_ResetTPMaskReg.Name = "groupBoxCROC_ResetTPMaskReg";
            this.groupBoxCROC_ResetTPMaskReg.Size = new System.Drawing.Size(188, 167);
            this.groupBoxCROC_ResetTPMaskReg.TabIndex = 61;
            this.groupBoxCROC_ResetTPMaskReg.TabStop = false;
            this.groupBoxCROC_ResetTPMaskReg.Text = "Reset and Test Pulse";
            this.groupBoxCROC_ResetTPMaskReg.Visible = false;
            // 
            // btn_CROCTPSend
            // 
            this.btn_CROCTPSend.BackColor = System.Drawing.Color.Coral;
            this.btn_CROCTPSend.Location = new System.Drawing.Point(7, 140);
            this.btn_CROCTPSend.Name = "btn_CROCTPSend";
            this.btn_CROCTPSend.Size = new System.Drawing.Size(173, 20);
            this.btn_CROCTPSend.TabIndex = 76;
            this.btn_CROCTPSend.Text = "Send Test Pulse";
            this.btn_CROCTPSend.UseVisualStyleBackColor = false;
            this.btn_CROCTPSend.Click += new System.EventHandler(this.btn_CROCTPSend_Click);
            // 
            // btn_CROCResetSend
            // 
            this.btn_CROCResetSend.BackColor = System.Drawing.Color.Coral;
            this.btn_CROCResetSend.Location = new System.Drawing.Point(6, 119);
            this.btn_CROCResetSend.Name = "btn_CROCResetSend";
            this.btn_CROCResetSend.Size = new System.Drawing.Size(173, 20);
            this.btn_CROCResetSend.TabIndex = 75;
            this.btn_CROCResetSend.Text = "Send Reset (reload FPGA)";
            this.btn_CROCResetSend.UseVisualStyleBackColor = false;
            this.btn_CROCResetSend.Click += new System.EventHandler(this.btn_CROCResetSend_Click);
            // 
            // btn_CROCResetTPWrite
            // 
            this.btn_CROCResetTPWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_CROCResetTPWrite.Location = new System.Drawing.Point(6, 98);
            this.btn_CROCResetTPWrite.Name = "btn_CROCResetTPWrite";
            this.btn_CROCResetTPWrite.Size = new System.Drawing.Size(60, 20);
            this.btn_CROCResetTPWrite.TabIndex = 74;
            this.btn_CROCResetTPWrite.Text = "Write";
            this.btn_CROCResetTPWrite.UseVisualStyleBackColor = false;
            this.btn_CROCResetTPWrite.Click += new System.EventHandler(this.btn_CROCResetTPWrite_Click);
            // 
            // lbl_CROCResetTPRead
            // 
            this.lbl_CROCResetTPRead.BackColor = System.Drawing.Color.White;
            this.lbl_CROCResetTPRead.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CROCResetTPRead.Location = new System.Drawing.Point(123, 99);
            this.lbl_CROCResetTPRead.Name = "lbl_CROCResetTPRead";
            this.lbl_CROCResetTPRead.Size = new System.Drawing.Size(57, 18);
            this.lbl_CROCResetTPRead.TabIndex = 73;
            // 
            // btn_CROCResetTPRead
            // 
            this.btn_CROCResetTPRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CROCResetTPRead.Location = new System.Drawing.Point(68, 98);
            this.btn_CROCResetTPRead.Name = "btn_CROCResetTPRead";
            this.btn_CROCResetTPRead.Size = new System.Drawing.Size(58, 20);
            this.btn_CROCResetTPRead.TabIndex = 72;
            this.btn_CROCResetTPRead.Text = "Read";
            this.btn_CROCResetTPRead.UseVisualStyleBackColor = false;
            this.btn_CROCResetTPRead.Click += new System.EventHandler(this.btn_CROCResetTPRead_Click);
            // 
            // chk_CROCTPulseCh4
            // 
            this.chk_CROCTPulseCh4.BackColor = System.Drawing.Color.Coral;
            this.chk_CROCTPulseCh4.Location = new System.Drawing.Point(94, 79);
            this.chk_CROCTPulseCh4.Name = "chk_CROCTPulseCh4";
            this.chk_CROCTPulseCh4.Size = new System.Drawing.Size(85, 17);
            this.chk_CROCTPulseCh4.TabIndex = 71;
            this.chk_CROCTPulseCh4.Text = "TPulse Ch4";
            this.chk_CROCTPulseCh4.UseVisualStyleBackColor = false;
            // 
            // chk_CROCResetCh4
            // 
            this.chk_CROCResetCh4.BackColor = System.Drawing.Color.Coral;
            this.chk_CROCResetCh4.Location = new System.Drawing.Point(6, 79);
            this.chk_CROCResetCh4.Name = "chk_CROCResetCh4";
            this.chk_CROCResetCh4.Size = new System.Drawing.Size(85, 17);
            this.chk_CROCResetCh4.TabIndex = 70;
            this.chk_CROCResetCh4.Text = "Reset Ch4";
            this.chk_CROCResetCh4.UseVisualStyleBackColor = false;
            // 
            // chk_CROCTPulseCh3
            // 
            this.chk_CROCTPulseCh3.BackColor = System.Drawing.Color.Coral;
            this.chk_CROCTPulseCh3.Location = new System.Drawing.Point(94, 59);
            this.chk_CROCTPulseCh3.Name = "chk_CROCTPulseCh3";
            this.chk_CROCTPulseCh3.Size = new System.Drawing.Size(85, 17);
            this.chk_CROCTPulseCh3.TabIndex = 69;
            this.chk_CROCTPulseCh3.Text = "TPulse Ch3";
            this.chk_CROCTPulseCh3.UseVisualStyleBackColor = false;
            // 
            // chk_CROCResetCh3
            // 
            this.chk_CROCResetCh3.BackColor = System.Drawing.Color.Coral;
            this.chk_CROCResetCh3.Location = new System.Drawing.Point(6, 59);
            this.chk_CROCResetCh3.Name = "chk_CROCResetCh3";
            this.chk_CROCResetCh3.Size = new System.Drawing.Size(85, 17);
            this.chk_CROCResetCh3.TabIndex = 68;
            this.chk_CROCResetCh3.Text = "Reset Ch3";
            this.chk_CROCResetCh3.UseVisualStyleBackColor = false;
            // 
            // chk_CROCTPulseCh2
            // 
            this.chk_CROCTPulseCh2.BackColor = System.Drawing.Color.Coral;
            this.chk_CROCTPulseCh2.Location = new System.Drawing.Point(94, 39);
            this.chk_CROCTPulseCh2.Name = "chk_CROCTPulseCh2";
            this.chk_CROCTPulseCh2.Size = new System.Drawing.Size(85, 17);
            this.chk_CROCTPulseCh2.TabIndex = 67;
            this.chk_CROCTPulseCh2.Text = "TPulse Ch2";
            this.chk_CROCTPulseCh2.UseVisualStyleBackColor = false;
            // 
            // chk_CROCResetCh2
            // 
            this.chk_CROCResetCh2.BackColor = System.Drawing.Color.Coral;
            this.chk_CROCResetCh2.Location = new System.Drawing.Point(6, 39);
            this.chk_CROCResetCh2.Name = "chk_CROCResetCh2";
            this.chk_CROCResetCh2.Size = new System.Drawing.Size(85, 17);
            this.chk_CROCResetCh2.TabIndex = 66;
            this.chk_CROCResetCh2.Text = "Reset Ch2";
            this.chk_CROCResetCh2.UseVisualStyleBackColor = false;
            // 
            // chk_CROCTPulseCh1
            // 
            this.chk_CROCTPulseCh1.BackColor = System.Drawing.Color.Coral;
            this.chk_CROCTPulseCh1.Location = new System.Drawing.Point(94, 19);
            this.chk_CROCTPulseCh1.Name = "chk_CROCTPulseCh1";
            this.chk_CROCTPulseCh1.Size = new System.Drawing.Size(85, 17);
            this.chk_CROCTPulseCh1.TabIndex = 65;
            this.chk_CROCTPulseCh1.Text = "TPulse Ch1";
            this.chk_CROCTPulseCh1.UseVisualStyleBackColor = false;
            // 
            // chk_CROCResetCh1
            // 
            this.chk_CROCResetCh1.BackColor = System.Drawing.Color.Coral;
            this.chk_CROCResetCh1.Location = new System.Drawing.Point(6, 19);
            this.chk_CROCResetCh1.Name = "chk_CROCResetCh1";
            this.chk_CROCResetCh1.Size = new System.Drawing.Size(85, 17);
            this.chk_CROCResetCh1.TabIndex = 64;
            this.chk_CROCResetCh1.Text = "Reset Ch1";
            this.chk_CROCResetCh1.UseVisualStyleBackColor = false;
            // 
            // groupBoxCROC_TimingSetup
            // 
            this.groupBoxCROC_TimingSetup.Controls.Add(this.lbl_CROCTimingSetupRead);
            this.groupBoxCROC_TimingSetup.Controls.Add(this.label20);
            this.groupBoxCROC_TimingSetup.Controls.Add(this.btn_CROCTimingSetupRead);
            this.groupBoxCROC_TimingSetup.Controls.Add(this.txt_CROCTimingSetupTPDelay);
            this.groupBoxCROC_TimingSetup.Controls.Add(this.cmb_CROCTimingSetupTPDelay);
            this.groupBoxCROC_TimingSetup.Controls.Add(this.cmb_CROCTimingSetupClock);
            this.groupBoxCROC_TimingSetup.Location = new System.Drawing.Point(16, 120);
            this.groupBoxCROC_TimingSetup.Name = "groupBoxCROC_TimingSetup";
            this.groupBoxCROC_TimingSetup.Size = new System.Drawing.Size(114, 108);
            this.groupBoxCROC_TimingSetup.TabIndex = 60;
            this.groupBoxCROC_TimingSetup.TabStop = false;
            this.groupBoxCROC_TimingSetup.Text = "Timing Setup";
            this.groupBoxCROC_TimingSetup.Visible = false;
            // 
            // lbl_CROCTimingSetupRead
            // 
            this.lbl_CROCTimingSetupRead.BackColor = System.Drawing.Color.White;
            this.lbl_CROCTimingSetupRead.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lbl_CROCTimingSetupRead.Location = new System.Drawing.Point(50, 86);
            this.lbl_CROCTimingSetupRead.Name = "lbl_CROCTimingSetupRead";
            this.lbl_CROCTimingSetupRead.Size = new System.Drawing.Size(57, 18);
            this.lbl_CROCTimingSetupRead.TabIndex = 62;
            // 
            // label20
            // 
            this.label20.BackColor = System.Drawing.Color.Coral;
            this.label20.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label20.Location = new System.Drawing.Point(7, 67);
            this.label20.Name = "label20";
            this.label20.Size = new System.Drawing.Size(64, 16);
            this.label20.TabIndex = 61;
            this.label20.Text = "TP Delay";
            // 
            // btn_CROCTimingSetupRead
            // 
            this.btn_CROCTimingSetupRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CROCTimingSetupRead.Location = new System.Drawing.Point(7, 85);
            this.btn_CROCTimingSetupRead.Name = "btn_CROCTimingSetupRead";
            this.btn_CROCTimingSetupRead.Size = new System.Drawing.Size(46, 20);
            this.btn_CROCTimingSetupRead.TabIndex = 60;
            this.btn_CROCTimingSetupRead.Text = "Read";
            this.btn_CROCTimingSetupRead.UseVisualStyleBackColor = false;
            this.btn_CROCTimingSetupRead.Click += new System.EventHandler(this.btn_CROCTimingSetupRead_Click);
            // 
            // txt_CROCTimingSetupTPDelay
            // 
            this.txt_CROCTimingSetupTPDelay.Location = new System.Drawing.Point(70, 65);
            this.txt_CROCTimingSetupTPDelay.Name = "txt_CROCTimingSetupTPDelay";
            this.txt_CROCTimingSetupTPDelay.Size = new System.Drawing.Size(37, 20);
            this.txt_CROCTimingSetupTPDelay.TabIndex = 2;
            this.txt_CROCTimingSetupTPDelay.TextChanged += new System.EventHandler(this.txt_CROCTimingSetupTPDelay_TextChanged);
            // 
            // cmb_CROCTimingSetupTPDelay
            // 
            this.cmb_CROCTimingSetupTPDelay.FormattingEnabled = true;
            this.cmb_CROCTimingSetupTPDelay.Items.AddRange(new object[] {
            "TP Disabled",
            "TP Enabled"});
            this.cmb_CROCTimingSetupTPDelay.Location = new System.Drawing.Point(7, 43);
            this.cmb_CROCTimingSetupTPDelay.Name = "cmb_CROCTimingSetupTPDelay";
            this.cmb_CROCTimingSetupTPDelay.Size = new System.Drawing.Size(101, 21);
            this.cmb_CROCTimingSetupTPDelay.TabIndex = 1;
            this.cmb_CROCTimingSetupTPDelay.Text = "Test Pulse";
            this.cmb_CROCTimingSetupTPDelay.SelectedIndexChanged += new System.EventHandler(this.cmb_CROCTimingSetupTPDelay_SelectedIndexChanged);
            // 
            // cmb_CROCTimingSetupClock
            // 
            this.cmb_CROCTimingSetupClock.FormattingEnabled = true;
            this.cmb_CROCTimingSetupClock.Items.AddRange(new object[] {
            "CLK Internal",
            "CLK External"});
            this.cmb_CROCTimingSetupClock.Location = new System.Drawing.Point(7, 19);
            this.cmb_CROCTimingSetupClock.Name = "cmb_CROCTimingSetupClock";
            this.cmb_CROCTimingSetupClock.Size = new System.Drawing.Size(101, 21);
            this.cmb_CROCTimingSetupClock.TabIndex = 0;
            this.cmb_CROCTimingSetupClock.Text = "CLK Source";
            this.cmb_CROCTimingSetupClock.SelectedIndexChanged += new System.EventHandler(this.cmb_CROCTimingSetupClock_SelectedIndexChanged);
            // 
            // groupBoxCROC_FLASH
            // 
            this.groupBoxCROC_FLASH.Controls.Add(this.btn_CROCWriteFileToSPI);
            this.groupBoxCROC_FLASH.Controls.Add(this.btn_CROCReBootFEs);
            this.groupBoxCROC_FLASH.Location = new System.Drawing.Point(16, 42);
            this.groupBoxCROC_FLASH.Name = "groupBoxCROC_FLASH";
            this.groupBoxCROC_FLASH.Size = new System.Drawing.Size(342, 72);
            this.groupBoxCROC_FLASH.TabIndex = 59;
            this.groupBoxCROC_FLASH.TabStop = false;
            this.groupBoxCROC_FLASH.Text = "FLASH Commands";
            this.groupBoxCROC_FLASH.Visible = false;
            // 
            // btn_CROCWriteFileToSPI
            // 
            this.btn_CROCWriteFileToSPI.BackColor = System.Drawing.Color.Coral;
            this.btn_CROCWriteFileToSPI.Location = new System.Drawing.Point(6, 19);
            this.btn_CROCWriteFileToSPI.Name = "btn_CROCWriteFileToSPI";
            this.btn_CROCWriteFileToSPI.Size = new System.Drawing.Size(216, 20);
            this.btn_CROCWriteFileToSPI.TabIndex = 57;
            this.btn_CROCWriteFileToSPI.Text = "Write File To FLASH Memory";
            this.btn_CROCWriteFileToSPI.UseVisualStyleBackColor = false;
            this.btn_CROCWriteFileToSPI.Click += new System.EventHandler(this.btn_CROCWriteFileToSPI_Click);
            // 
            // btn_CROCReBootFEs
            // 
            this.btn_CROCReBootFEs.BackColor = System.Drawing.Color.Coral;
            this.btn_CROCReBootFEs.Location = new System.Drawing.Point(6, 44);
            this.btn_CROCReBootFEs.Name = "btn_CROCReBootFEs";
            this.btn_CROCReBootFEs.Size = new System.Drawing.Size(216, 20);
            this.btn_CROCReBootFEs.TabIndex = 58;
            this.btn_CROCReBootFEs.Text = "Reboot FEs (reload FLASH content)";
            this.btn_CROCReBootFEs.UseVisualStyleBackColor = false;
            this.btn_CROCReBootFEs.Click += new System.EventHandler(this.btn_CROCReBootFEs_Click);
            // 
            // btn_CROCAdvancedGUI
            // 
            this.btn_CROCAdvancedGUI.BackColor = System.Drawing.Color.Coral;
            this.btn_CROCAdvancedGUI.Location = new System.Drawing.Point(238, 16);
            this.btn_CROCAdvancedGUI.Name = "btn_CROCAdvancedGUI";
            this.btn_CROCAdvancedGUI.Size = new System.Drawing.Size(120, 20);
            this.btn_CROCAdvancedGUI.TabIndex = 56;
            this.btn_CROCAdvancedGUI.Text = "Show Advanced GUI";
            this.btn_CROCAdvancedGUI.UseVisualStyleBackColor = false;
            this.btn_CROCAdvancedGUI.Click += new System.EventHandler(this.btn_CROCAdvancedGUI_Click);
            // 
            // lblCROC_CROCID
            // 
            this.lblCROC_CROCID.BackColor = System.Drawing.Color.White;
            this.lblCROC_CROCID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCROC_CROCID.Location = new System.Drawing.Point(202, 16);
            this.lblCROC_CROCID.Name = "lblCROC_CROCID";
            this.lblCROC_CROCID.Size = new System.Drawing.Size(30, 18);
            this.lblCROC_CROCID.TabIndex = 55;
            // 
            // label12
            // 
            this.label12.BackColor = System.Drawing.Color.Coral;
            this.label12.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label12.Location = new System.Drawing.Point(164, 16);
            this.label12.Name = "label12";
            this.label12.Size = new System.Drawing.Size(40, 18);
            this.label12.TabIndex = 54;
            this.label12.Text = "CROC";
            // 
            // label15
            // 
            this.label15.BackColor = System.Drawing.Color.White;
            this.label15.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label15.Location = new System.Drawing.Point(128, 16);
            this.label15.Name = "label15";
            this.label15.Size = new System.Drawing.Size(30, 18);
            this.label15.TabIndex = 53;
            this.label15.Text = "ALL";
            // 
            // label17
            // 
            this.label17.BackColor = System.Drawing.Color.Coral;
            this.label17.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label17.Location = new System.Drawing.Point(90, 16);
            this.label17.Name = "label17";
            this.label17.Size = new System.Drawing.Size(40, 18);
            this.label17.TabIndex = 52;
            this.label17.Text = "CH";
            // 
            // label18
            // 
            this.label18.BackColor = System.Drawing.Color.White;
            this.label18.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label18.Location = new System.Drawing.Point(54, 16);
            this.label18.Name = "label18";
            this.label18.Size = new System.Drawing.Size(30, 18);
            this.label18.TabIndex = 51;
            this.label18.Text = "ALL";
            // 
            // label19
            // 
            this.label19.BackColor = System.Drawing.Color.Coral;
            this.label19.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label19.Location = new System.Drawing.Point(16, 16);
            this.label19.Name = "label19";
            this.label19.Size = new System.Drawing.Size(40, 18);
            this.label19.TabIndex = 50;
            this.label19.Text = "FE";
            // 
            // tabCH
            // 
            this.tabCH.Controls.Add(this.groupBoxCH_DEBUG);
            this.tabCH.Controls.Add(this.groupBoxCH_Frame);
            this.tabCH.Controls.Add(this.groupBoxCH_StatusRegister);
            this.tabCH.Controls.Add(this.groupBoxCH_FLASH);
            this.tabCH.Controls.Add(this.groupBoxCH_DPM);
            this.tabCH.Controls.Add(this.label4);
            this.tabCH.Controls.Add(this.btn_CHAdvancedGUI);
            this.tabCH.Controls.Add(this.lblCH_CROCID);
            this.tabCH.Controls.Add(this.label10);
            this.tabCH.Controls.Add(this.lblCH_CHID);
            this.tabCH.Controls.Add(this.label14);
            this.tabCH.Controls.Add(this.label16);
            this.tabCH.Location = new System.Drawing.Point(4, 22);
            this.tabCH.Name = "tabCH";
            this.tabCH.Size = new System.Drawing.Size(899, 502);
            this.tabCH.TabIndex = 6;
            this.tabCH.Text = "CH";
            this.tabCH.UseVisualStyleBackColor = true;
            // 
            // groupBoxCH_DEBUG
            // 
            this.groupBoxCH_DEBUG.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.groupBoxCH_DEBUG.Controls.Add(this.btn_CHDebugUpdatePattern);
            this.groupBoxCH_DEBUG.Controls.Add(this.cmb_CHDebugBroadcastCMD);
            this.groupBoxCH_DEBUG.Controls.Add(this.cmb_CHDebugFEID);
            this.groupBoxCH_DEBUG.Controls.Add(this.cmb_CHDebugFunctionID);
            this.groupBoxCH_DEBUG.Controls.Add(this.cmb_CHDebugDeviceID);
            this.groupBoxCH_DEBUG.Controls.Add(this.cmb_CHDebugDirection);
            this.groupBoxCH_DEBUG.Controls.Add(this.txt_CHDebugFrameStatusID);
            this.groupBoxCH_DEBUG.Controls.Add(this.txt_CHDebugFrameIDByte0);
            this.groupBoxCH_DEBUG.Controls.Add(this.label85);
            this.groupBoxCH_DEBUG.Controls.Add(this.label84);
            this.groupBoxCH_DEBUG.Controls.Add(this.label81);
            this.groupBoxCH_DEBUG.Controls.Add(this.label80);
            this.groupBoxCH_DEBUG.Controls.Add(this.txt_CHDebugFrameIDByte1);
            this.groupBoxCH_DEBUG.Controls.Add(this.label77);
            this.groupBoxCH_DEBUG.Controls.Add(this.label76);
            this.groupBoxCH_DEBUG.Controls.Add(this.label69);
            this.groupBoxCH_DEBUG.Controls.Add(this.txt_CHDebugFillDPMPattern);
            this.groupBoxCH_DEBUG.Controls.Add(this.txt_CHDebugFillDPMPRepeat);
            this.groupBoxCH_DEBUG.Controls.Add(this.btn_CHDebugFillDPM);
            this.groupBoxCH_DEBUG.Controls.Add(this.rtb_CHDebug);
            this.groupBoxCH_DEBUG.Controls.Add(this.txt_CHDebugNTests);
            this.groupBoxCH_DEBUG.Controls.Add(this.label73);
            this.groupBoxCH_DEBUG.Controls.Add(this.btn_CHDebugInitializeCROCs);
            this.groupBoxCH_DEBUG.Location = new System.Drawing.Point(373, 16);
            this.groupBoxCH_DEBUG.Name = "groupBoxCH_DEBUG";
            this.groupBoxCH_DEBUG.Size = new System.Drawing.Size(513, 425);
            this.groupBoxCH_DEBUG.TabIndex = 90;
            this.groupBoxCH_DEBUG.TabStop = false;
            this.groupBoxCH_DEBUG.Text = "DEBUG Tools";
            this.groupBoxCH_DEBUG.Visible = false;
            // 
            // btn_CHDebugUpdatePattern
            // 
            this.btn_CHDebugUpdatePattern.BackColor = System.Drawing.Color.Coral;
            this.btn_CHDebugUpdatePattern.Location = new System.Drawing.Point(327, 59);
            this.btn_CHDebugUpdatePattern.Name = "btn_CHDebugUpdatePattern";
            this.btn_CHDebugUpdatePattern.Size = new System.Drawing.Size(175, 55);
            this.btn_CHDebugUpdatePattern.TabIndex = 113;
            this.btn_CHDebugUpdatePattern.Text = "Update Pattern";
            this.btn_CHDebugUpdatePattern.UseVisualStyleBackColor = false;
            this.btn_CHDebugUpdatePattern.Click += new System.EventHandler(this.btn_CHDebugUpdatePattern_Click);
            // 
            // cmb_CHDebugBroadcastCMD
            // 
            this.cmb_CHDebugBroadcastCMD.FormattingEnabled = true;
            this.cmb_CHDebugBroadcastCMD.Items.AddRange(new object[] {
            "0 NA",
            "1 LoadTimer",
            "2 ResetTimer",
            "3 OpenGate",
            "4 SoftwRST",
            "5 NA",
            "6 NA",
            "7 NA"});
            this.cmb_CHDebugBroadcastCMD.Location = new System.Drawing.Point(340, 11);
            this.cmb_CHDebugBroadcastCMD.Name = "cmb_CHDebugBroadcastCMD";
            this.cmb_CHDebugBroadcastCMD.Size = new System.Drawing.Size(97, 21);
            this.cmb_CHDebugBroadcastCMD.TabIndex = 112;
            // 
            // cmb_CHDebugFEID
            // 
            this.cmb_CHDebugFEID.FormattingEnabled = true;
            this.cmb_CHDebugFEID.Items.AddRange(new object[] {
            "0 NA",
            "1 FE1",
            "2 FE2",
            "3 FE3",
            "4 FE4",
            "5 FE5",
            "6 FE6",
            "7 FE7",
            "8 FE8",
            "9 FE9",
            "10 FE10",
            "11 FE11",
            "12 FE12",
            "13 FE13",
            "14 FE14",
            "15 FE15"});
            this.cmb_CHDebugFEID.Location = new System.Drawing.Point(437, 11);
            this.cmb_CHDebugFEID.Name = "cmb_CHDebugFEID";
            this.cmb_CHDebugFEID.Size = new System.Drawing.Size(65, 21);
            this.cmb_CHDebugFEID.TabIndex = 111;
            // 
            // cmb_CHDebugFunctionID
            // 
            this.cmb_CHDebugFunctionID.FormattingEnabled = true;
            this.cmb_CHDebugFunctionID.Location = new System.Drawing.Point(387, 32);
            this.cmb_CHDebugFunctionID.Name = "cmb_CHDebugFunctionID";
            this.cmb_CHDebugFunctionID.Size = new System.Drawing.Size(115, 21);
            this.cmb_CHDebugFunctionID.TabIndex = 110;
            // 
            // cmb_CHDebugDeviceID
            // 
            this.cmb_CHDebugDeviceID.FormattingEnabled = true;
            this.cmb_CHDebugDeviceID.Items.AddRange(new object[] {
            "0 NA",
            "1 TRIP",
            "2 REG",
            "3 BRAM",
            "4 FLASH",
            "5 NA",
            "6 NA",
            "7 NA",
            "8 NA",
            "9 NA",
            "10 NA",
            "11 NA",
            "12 NA",
            "13 NA",
            "14 NA",
            "15 NA"});
            this.cmb_CHDebugDeviceID.Location = new System.Drawing.Point(287, 32);
            this.cmb_CHDebugDeviceID.Name = "cmb_CHDebugDeviceID";
            this.cmb_CHDebugDeviceID.Size = new System.Drawing.Size(100, 21);
            this.cmb_CHDebugDeviceID.TabIndex = 109;
            this.cmb_CHDebugDeviceID.SelectedIndexChanged += new System.EventHandler(this.cmb_CHDebugDeviceID_SelectedIndexChanged);
            // 
            // cmb_CHDebugDirection
            // 
            this.cmb_CHDebugDirection.FormattingEnabled = true;
            this.cmb_CHDebugDirection.Items.AddRange(new object[] {
            "0 M2S",
            "1 S2M"});
            this.cmb_CHDebugDirection.Location = new System.Drawing.Point(287, 11);
            this.cmb_CHDebugDirection.Name = "cmb_CHDebugDirection";
            this.cmb_CHDebugDirection.Size = new System.Drawing.Size(53, 21);
            this.cmb_CHDebugDirection.TabIndex = 108;
            // 
            // txt_CHDebugFrameStatusID
            // 
            this.txt_CHDebugFrameStatusID.Location = new System.Drawing.Point(287, 53);
            this.txt_CHDebugFrameStatusID.Name = "txt_CHDebugFrameStatusID";
            this.txt_CHDebugFrameStatusID.Size = new System.Drawing.Size(34, 20);
            this.txt_CHDebugFrameStatusID.TabIndex = 107;
            // 
            // txt_CHDebugFrameIDByte0
            // 
            this.txt_CHDebugFrameIDByte0.Location = new System.Drawing.Point(287, 74);
            this.txt_CHDebugFrameIDByte0.Name = "txt_CHDebugFrameIDByte0";
            this.txt_CHDebugFrameIDByte0.Size = new System.Drawing.Size(34, 20);
            this.txt_CHDebugFrameIDByte0.TabIndex = 106;
            // 
            // label85
            // 
            this.label85.BackColor = System.Drawing.Color.Coral;
            this.label85.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label85.Location = new System.Drawing.Point(208, 97);
            this.label85.Name = "label85";
            this.label85.Size = new System.Drawing.Size(73, 17);
            this.label85.TabIndex = 105;
            this.label85.Text = "Byte4 ID (0x)";
            this.label85.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label84
            // 
            this.label84.BackColor = System.Drawing.Color.Coral;
            this.label84.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label84.Location = new System.Drawing.Point(208, 76);
            this.label84.Name = "label84";
            this.label84.Size = new System.Drawing.Size(73, 17);
            this.label84.TabIndex = 104;
            this.label84.Text = "Byte3 ID (0x)";
            this.label84.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label81
            // 
            this.label81.BackColor = System.Drawing.Color.Coral;
            this.label81.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label81.Location = new System.Drawing.Point(208, 55);
            this.label81.Name = "label81";
            this.label81.Size = new System.Drawing.Size(73, 17);
            this.label81.TabIndex = 103;
            this.label81.Text = "Byte2 ST (0x)";
            this.label81.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label80
            // 
            this.label80.BackColor = System.Drawing.Color.Coral;
            this.label80.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label80.Location = new System.Drawing.Point(208, 34);
            this.label80.Name = "label80";
            this.label80.Size = new System.Drawing.Size(73, 17);
            this.label80.TabIndex = 102;
            this.label80.Text = "Byte1 DevF";
            this.label80.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // txt_CHDebugFrameIDByte1
            // 
            this.txt_CHDebugFrameIDByte1.Location = new System.Drawing.Point(287, 95);
            this.txt_CHDebugFrameIDByte1.Name = "txt_CHDebugFrameIDByte1";
            this.txt_CHDebugFrameIDByte1.Size = new System.Drawing.Size(34, 20);
            this.txt_CHDebugFrameIDByte1.TabIndex = 101;
            // 
            // label77
            // 
            this.label77.BackColor = System.Drawing.Color.Coral;
            this.label77.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label77.Location = new System.Drawing.Point(208, 13);
            this.label77.Name = "label77";
            this.label77.Size = new System.Drawing.Size(73, 17);
            this.label77.TabIndex = 100;
            this.label77.Text = "Byte0 Start";
            this.label77.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label76
            // 
            this.label76.BackColor = System.Drawing.Color.Coral;
            this.label76.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label76.Location = new System.Drawing.Point(110, 80);
            this.label76.Name = "label76";
            this.label76.Size = new System.Drawing.Size(89, 17);
            this.label76.TabIndex = 99;
            this.label76.Text = "Repeat (dec)";
            this.label76.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // label69
            // 
            this.label69.BackColor = System.Drawing.Color.Coral;
            this.label69.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label69.Location = new System.Drawing.Point(10, 80);
            this.label69.Name = "label69";
            this.label69.Size = new System.Drawing.Size(89, 17);
            this.label69.TabIndex = 98;
            this.label69.Text = "Pattern (0x)";
            this.label69.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // txt_CHDebugFillDPMPattern
            // 
            this.txt_CHDebugFillDPMPattern.Location = new System.Drawing.Point(10, 97);
            this.txt_CHDebugFillDPMPattern.Name = "txt_CHDebugFillDPMPattern";
            this.txt_CHDebugFillDPMPattern.Size = new System.Drawing.Size(89, 20);
            this.txt_CHDebugFillDPMPattern.TabIndex = 97;
            // 
            // txt_CHDebugFillDPMPRepeat
            // 
            this.txt_CHDebugFillDPMPRepeat.Location = new System.Drawing.Point(110, 97);
            this.txt_CHDebugFillDPMPRepeat.Name = "txt_CHDebugFillDPMPRepeat";
            this.txt_CHDebugFillDPMPRepeat.Size = new System.Drawing.Size(89, 20);
            this.txt_CHDebugFillDPMPRepeat.TabIndex = 96;
            // 
            // btn_CHDebugFillDPM
            // 
            this.btn_CHDebugFillDPM.BackColor = System.Drawing.Color.Coral;
            this.btn_CHDebugFillDPM.Location = new System.Drawing.Point(10, 61);
            this.btn_CHDebugFillDPM.Name = "btn_CHDebugFillDPM";
            this.btn_CHDebugFillDPM.Size = new System.Drawing.Size(189, 20);
            this.btn_CHDebugFillDPM.TabIndex = 95;
            this.btn_CHDebugFillDPM.Text = "START FillDPM";
            this.btn_CHDebugFillDPM.UseVisualStyleBackColor = false;
            this.btn_CHDebugFillDPM.Click += new System.EventHandler(this.btn_CHDebugFillDPM_Click);
            // 
            // rtb_CHDebug
            // 
            this.rtb_CHDebug.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.rtb_CHDebug.Location = new System.Drawing.Point(10, 147);
            this.rtb_CHDebug.Name = "rtb_CHDebug";
            this.rtb_CHDebug.Size = new System.Drawing.Size(494, 262);
            this.rtb_CHDebug.TabIndex = 94;
            this.rtb_CHDebug.Text = "";
            // 
            // txt_CHDebugNTests
            // 
            this.txt_CHDebugNTests.Location = new System.Drawing.Point(102, 12);
            this.txt_CHDebugNTests.Name = "txt_CHDebugNTests";
            this.txt_CHDebugNTests.Size = new System.Drawing.Size(97, 20);
            this.txt_CHDebugNTests.TabIndex = 92;
            // 
            // label73
            // 
            this.label73.BackColor = System.Drawing.Color.Coral;
            this.label73.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label73.Location = new System.Drawing.Point(10, 14);
            this.label73.Name = "label73";
            this.label73.Size = new System.Drawing.Size(89, 17);
            this.label73.TabIndex = 88;
            this.label73.Text = "Number of Tests";
            this.label73.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // btn_CHDebugInitializeCROCs
            // 
            this.btn_CHDebugInitializeCROCs.BackColor = System.Drawing.Color.Coral;
            this.btn_CHDebugInitializeCROCs.Location = new System.Drawing.Point(10, 35);
            this.btn_CHDebugInitializeCROCs.Name = "btn_CHDebugInitializeCROCs";
            this.btn_CHDebugInitializeCROCs.Size = new System.Drawing.Size(192, 20);
            this.btn_CHDebugInitializeCROCs.TabIndex = 80;
            this.btn_CHDebugInitializeCROCs.Text = "START FEsEnumeration";
            this.btn_CHDebugInitializeCROCs.UseVisualStyleBackColor = false;
            this.btn_CHDebugInitializeCROCs.Click += new System.EventHandler(this.btn_CHDebugInitializeCROCs_Click);
            // 
            // groupBoxCH_Frame
            // 
            this.groupBoxCH_Frame.Controls.Add(this.btn_CHFIFOWriteMessage);
            this.groupBoxCH_Frame.Controls.Add(this.rtb_CHDPMRead);
            this.groupBoxCH_Frame.Controls.Add(this.txt_CHDPMReadLength);
            this.groupBoxCH_Frame.Controls.Add(this.txt_CHFIFORegWrite);
            this.groupBoxCH_Frame.Controls.Add(this.btn_CHDPMRead);
            this.groupBoxCH_Frame.Controls.Add(this.btn_CHSendMessage);
            this.groupBoxCH_Frame.Controls.Add(this.btn_CHFIFOAppendMessage);
            this.groupBoxCH_Frame.Location = new System.Drawing.Point(164, 206);
            this.groupBoxCH_Frame.Name = "groupBoxCH_Frame";
            this.groupBoxCH_Frame.Size = new System.Drawing.Size(193, 235);
            this.groupBoxCH_Frame.TabIndex = 89;
            this.groupBoxCH_Frame.TabStop = false;
            this.groupBoxCH_Frame.Text = "Frame Registers";
            this.groupBoxCH_Frame.Visible = false;
            // 
            // btn_CHFIFOWriteMessage
            // 
            this.btn_CHFIFOWriteMessage.BackColor = System.Drawing.Color.Coral;
            this.btn_CHFIFOWriteMessage.Location = new System.Drawing.Point(11, 39);
            this.btn_CHFIFOWriteMessage.Name = "btn_CHFIFOWriteMessage";
            this.btn_CHFIFOWriteMessage.Size = new System.Drawing.Size(85, 20);
            this.btn_CHFIFOWriteMessage.TabIndex = 94;
            this.btn_CHFIFOWriteMessage.Text = "Write FIFO";
            this.btn_CHFIFOWriteMessage.UseVisualStyleBackColor = false;
            this.btn_CHFIFOWriteMessage.Click += new System.EventHandler(this.btn_CHFIFOWriteMessage_Click);
            // 
            // rtb_CHDPMRead
            // 
            this.rtb_CHDPMRead.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)));
            this.rtb_CHDPMRead.Location = new System.Drawing.Point(10, 85);
            this.rtb_CHDPMRead.Name = "rtb_CHDPMRead";
            this.rtb_CHDPMRead.Size = new System.Drawing.Size(171, 136);
            this.rtb_CHDPMRead.TabIndex = 93;
            this.rtb_CHDPMRead.Text = "";
            // 
            // txt_CHDPMReadLength
            // 
            this.txt_CHDPMReadLength.Location = new System.Drawing.Point(124, 60);
            this.txt_CHDPMReadLength.Name = "txt_CHDPMReadLength";
            this.txt_CHDPMReadLength.Size = new System.Drawing.Size(57, 20);
            this.txt_CHDPMReadLength.TabIndex = 92;
            // 
            // txt_CHFIFORegWrite
            // 
            this.txt_CHFIFORegWrite.Location = new System.Drawing.Point(124, 18);
            this.txt_CHFIFORegWrite.Name = "txt_CHFIFORegWrite";
            this.txt_CHFIFORegWrite.Size = new System.Drawing.Size(57, 20);
            this.txt_CHFIFORegWrite.TabIndex = 91;
            // 
            // btn_CHDPMRead
            // 
            this.btn_CHDPMRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CHDPMRead.Location = new System.Drawing.Point(11, 60);
            this.btn_CHDPMRead.Name = "btn_CHDPMRead";
            this.btn_CHDPMRead.Size = new System.Drawing.Size(115, 20);
            this.btn_CHDPMRead.TabIndex = 88;
            this.btn_CHDPMRead.Text = "Read DPM bytes->";
            this.btn_CHDPMRead.UseVisualStyleBackColor = false;
            this.btn_CHDPMRead.Click += new System.EventHandler(this.btn_CHDPMRead_Click);
            // 
            // btn_CHSendMessage
            // 
            this.btn_CHSendMessage.BackColor = System.Drawing.Color.Coral;
            this.btn_CHSendMessage.Location = new System.Drawing.Point(96, 39);
            this.btn_CHSendMessage.Name = "btn_CHSendMessage";
            this.btn_CHSendMessage.Size = new System.Drawing.Size(85, 20);
            this.btn_CHSendMessage.TabIndex = 87;
            this.btn_CHSendMessage.Text = "Send Frame";
            this.btn_CHSendMessage.UseVisualStyleBackColor = false;
            this.btn_CHSendMessage.Click += new System.EventHandler(this.btn_CHSendMessage_Click);
            // 
            // btn_CHFIFOAppendMessage
            // 
            this.btn_CHFIFOAppendMessage.BackColor = System.Drawing.Color.Coral;
            this.btn_CHFIFOAppendMessage.Location = new System.Drawing.Point(10, 18);
            this.btn_CHFIFOAppendMessage.Name = "btn_CHFIFOAppendMessage";
            this.btn_CHFIFOAppendMessage.Size = new System.Drawing.Size(115, 20);
            this.btn_CHFIFOAppendMessage.TabIndex = 85;
            this.btn_CHFIFOAppendMessage.Text = "Append Msg (0x)";
            this.btn_CHFIFOAppendMessage.UseVisualStyleBackColor = false;
            this.btn_CHFIFOAppendMessage.Click += new System.EventHandler(this.btn_CHFIFOAppendMessage_Click);
            // 
            // groupBoxCH_StatusRegister
            // 
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatUnusedBit15);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label33);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatUnusedBit14);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label29);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatUnusedBit11);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label25);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatUnusedBit7);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label21);
            this.groupBoxCH_StatusRegister.Controls.Add(this.btn_CHStatusRegClear);
            this.groupBoxCH_StatusRegister.Controls.Add(this.btn_CHStatusRegRead);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatusValue);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label22);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatMsgSent);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatRFPresent);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label24);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label38);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatMsgReceived);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatDPMFull);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label26);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label40);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatCRCError);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatFIFOFull);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label28);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label42);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatTimeoutError);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatFIFONotEmpty);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label36);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label44);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatSerializerSYNC);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatPLL1LOCK);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label34);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label30);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatDeserializerLOCK);
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatPLL0LOCK);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label32);
            this.groupBoxCH_StatusRegister.Location = new System.Drawing.Point(17, 119);
            this.groupBoxCH_StatusRegister.Name = "groupBoxCH_StatusRegister";
            this.groupBoxCH_StatusRegister.Size = new System.Drawing.Size(141, 322);
            this.groupBoxCH_StatusRegister.TabIndex = 88;
            this.groupBoxCH_StatusRegister.TabStop = false;
            this.groupBoxCH_StatusRegister.Text = "Status Register";
            this.groupBoxCH_StatusRegister.Visible = false;
            // 
            // lblCH_StatUnusedBit15
            // 
            this.lblCH_StatUnusedBit15.BackColor = System.Drawing.Color.White;
            this.lblCH_StatUnusedBit15.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatUnusedBit15.Location = new System.Drawing.Point(117, 298);
            this.lblCH_StatUnusedBit15.Name = "lblCH_StatUnusedBit15";
            this.lblCH_StatUnusedBit15.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatUnusedBit15.TabIndex = 87;
            // 
            // label33
            // 
            this.label33.BackColor = System.Drawing.Color.Coral;
            this.label33.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label33.Location = new System.Drawing.Point(10, 298);
            this.label33.Name = "label33";
            this.label33.Size = new System.Drawing.Size(107, 15);
            this.label33.TabIndex = 86;
            this.label33.Text = "Unused";
            // 
            // lblCH_StatUnusedBit14
            // 
            this.lblCH_StatUnusedBit14.BackColor = System.Drawing.Color.White;
            this.lblCH_StatUnusedBit14.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatUnusedBit14.Location = new System.Drawing.Point(117, 283);
            this.lblCH_StatUnusedBit14.Name = "lblCH_StatUnusedBit14";
            this.lblCH_StatUnusedBit14.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatUnusedBit14.TabIndex = 85;
            // 
            // label29
            // 
            this.label29.BackColor = System.Drawing.Color.Coral;
            this.label29.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label29.Location = new System.Drawing.Point(10, 283);
            this.label29.Name = "label29";
            this.label29.Size = new System.Drawing.Size(107, 15);
            this.label29.TabIndex = 84;
            this.label29.Text = "Unused";
            // 
            // lblCH_StatUnusedBit11
            // 
            this.lblCH_StatUnusedBit11.BackColor = System.Drawing.Color.White;
            this.lblCH_StatUnusedBit11.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatUnusedBit11.Location = new System.Drawing.Point(117, 235);
            this.lblCH_StatUnusedBit11.Name = "lblCH_StatUnusedBit11";
            this.lblCH_StatUnusedBit11.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatUnusedBit11.TabIndex = 83;
            // 
            // label25
            // 
            this.label25.BackColor = System.Drawing.Color.Coral;
            this.label25.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label25.Location = new System.Drawing.Point(10, 235);
            this.label25.Name = "label25";
            this.label25.Size = new System.Drawing.Size(107, 15);
            this.label25.TabIndex = 82;
            this.label25.Text = "Unused";
            // 
            // lblCH_StatUnusedBit7
            // 
            this.lblCH_StatUnusedBit7.BackColor = System.Drawing.Color.White;
            this.lblCH_StatUnusedBit7.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatUnusedBit7.Location = new System.Drawing.Point(117, 172);
            this.lblCH_StatUnusedBit7.Name = "lblCH_StatUnusedBit7";
            this.lblCH_StatUnusedBit7.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatUnusedBit7.TabIndex = 81;
            // 
            // label21
            // 
            this.label21.BackColor = System.Drawing.Color.Coral;
            this.label21.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label21.Location = new System.Drawing.Point(10, 172);
            this.label21.Name = "label21";
            this.label21.Size = new System.Drawing.Size(107, 15);
            this.label21.TabIndex = 80;
            this.label21.Text = "Unused";
            // 
            // btn_CHStatusRegClear
            // 
            this.btn_CHStatusRegClear.BackColor = System.Drawing.Color.Coral;
            this.btn_CHStatusRegClear.Location = new System.Drawing.Point(10, 20);
            this.btn_CHStatusRegClear.Name = "btn_CHStatusRegClear";
            this.btn_CHStatusRegClear.Size = new System.Drawing.Size(121, 20);
            this.btn_CHStatusRegClear.TabIndex = 79;
            this.btn_CHStatusRegClear.Text = "Clear Status Register";
            this.btn_CHStatusRegClear.UseVisualStyleBackColor = false;
            this.btn_CHStatusRegClear.Click += new System.EventHandler(this.btn_CHStatusRegClear_Click);
            // 
            // btn_CHStatusRegRead
            // 
            this.btn_CHStatusRegRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CHStatusRegRead.Location = new System.Drawing.Point(10, 41);
            this.btn_CHStatusRegRead.Name = "btn_CHStatusRegRead";
            this.btn_CHStatusRegRead.Size = new System.Drawing.Size(78, 20);
            this.btn_CHStatusRegRead.TabIndex = 53;
            this.btn_CHStatusRegRead.Text = "Read Status";
            this.btn_CHStatusRegRead.UseVisualStyleBackColor = false;
            this.btn_CHStatusRegRead.Click += new System.EventHandler(this.btn_CHStatusRegRead_Click);
            // 
            // lblCH_StatusValue
            // 
            this.lblCH_StatusValue.BackColor = System.Drawing.Color.White;
            this.lblCH_StatusValue.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatusValue.Location = new System.Drawing.Point(87, 42);
            this.lblCH_StatusValue.Name = "lblCH_StatusValue";
            this.lblCH_StatusValue.RightToLeft = System.Windows.Forms.RightToLeft.Yes;
            this.lblCH_StatusValue.Size = new System.Drawing.Size(44, 18);
            this.lblCH_StatusValue.TabIndex = 54;
            // 
            // label22
            // 
            this.label22.BackColor = System.Drawing.Color.Coral;
            this.label22.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label22.Location = new System.Drawing.Point(10, 64);
            this.label22.Name = "label22";
            this.label22.Size = new System.Drawing.Size(107, 15);
            this.label22.TabIndex = 55;
            this.label22.Text = "Msg Sent";
            // 
            // lblCH_StatMsgSent
            // 
            this.lblCH_StatMsgSent.BackColor = System.Drawing.Color.White;
            this.lblCH_StatMsgSent.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatMsgSent.Location = new System.Drawing.Point(117, 64);
            this.lblCH_StatMsgSent.Name = "lblCH_StatMsgSent";
            this.lblCH_StatMsgSent.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatMsgSent.TabIndex = 56;
            // 
            // lblCH_StatRFPresent
            // 
            this.lblCH_StatRFPresent.BackColor = System.Drawing.Color.White;
            this.lblCH_StatRFPresent.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatRFPresent.Location = new System.Drawing.Point(117, 190);
            this.lblCH_StatRFPresent.Name = "lblCH_StatRFPresent";
            this.lblCH_StatRFPresent.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatRFPresent.TabIndex = 78;
            // 
            // label24
            // 
            this.label24.BackColor = System.Drawing.Color.Coral;
            this.label24.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label24.Location = new System.Drawing.Point(10, 79);
            this.label24.Name = "label24";
            this.label24.Size = new System.Drawing.Size(107, 15);
            this.label24.TabIndex = 57;
            this.label24.Text = "Msg Received";
            // 
            // label38
            // 
            this.label38.BackColor = System.Drawing.Color.Coral;
            this.label38.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label38.Location = new System.Drawing.Point(10, 190);
            this.label38.Name = "label38";
            this.label38.Size = new System.Drawing.Size(107, 15);
            this.label38.TabIndex = 77;
            this.label38.Text = "RF Present";
            // 
            // lblCH_StatMsgReceived
            // 
            this.lblCH_StatMsgReceived.BackColor = System.Drawing.Color.White;
            this.lblCH_StatMsgReceived.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatMsgReceived.Location = new System.Drawing.Point(117, 79);
            this.lblCH_StatMsgReceived.Name = "lblCH_StatMsgReceived";
            this.lblCH_StatMsgReceived.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatMsgReceived.TabIndex = 58;
            // 
            // lblCH_StatDPMFull
            // 
            this.lblCH_StatDPMFull.BackColor = System.Drawing.Color.White;
            this.lblCH_StatDPMFull.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatDPMFull.Location = new System.Drawing.Point(117, 157);
            this.lblCH_StatDPMFull.Name = "lblCH_StatDPMFull";
            this.lblCH_StatDPMFull.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatDPMFull.TabIndex = 76;
            // 
            // label26
            // 
            this.label26.BackColor = System.Drawing.Color.Coral;
            this.label26.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label26.Location = new System.Drawing.Point(10, 94);
            this.label26.Name = "label26";
            this.label26.Size = new System.Drawing.Size(107, 15);
            this.label26.TabIndex = 59;
            this.label26.Text = "CRC Error";
            // 
            // label40
            // 
            this.label40.BackColor = System.Drawing.Color.Coral;
            this.label40.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label40.Location = new System.Drawing.Point(10, 157);
            this.label40.Name = "label40";
            this.label40.Size = new System.Drawing.Size(107, 15);
            this.label40.TabIndex = 75;
            this.label40.Text = "DPM Full";
            // 
            // lblCH_StatCRCError
            // 
            this.lblCH_StatCRCError.BackColor = System.Drawing.Color.White;
            this.lblCH_StatCRCError.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatCRCError.Location = new System.Drawing.Point(117, 94);
            this.lblCH_StatCRCError.Name = "lblCH_StatCRCError";
            this.lblCH_StatCRCError.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatCRCError.TabIndex = 60;
            // 
            // lblCH_StatFIFOFull
            // 
            this.lblCH_StatFIFOFull.BackColor = System.Drawing.Color.White;
            this.lblCH_StatFIFOFull.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatFIFOFull.Location = new System.Drawing.Point(117, 142);
            this.lblCH_StatFIFOFull.Name = "lblCH_StatFIFOFull";
            this.lblCH_StatFIFOFull.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatFIFOFull.TabIndex = 74;
            // 
            // label28
            // 
            this.label28.BackColor = System.Drawing.Color.Coral;
            this.label28.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label28.Location = new System.Drawing.Point(10, 109);
            this.label28.Name = "label28";
            this.label28.Size = new System.Drawing.Size(107, 15);
            this.label28.TabIndex = 61;
            this.label28.Text = "Timeout Error";
            // 
            // label42
            // 
            this.label42.BackColor = System.Drawing.Color.Coral;
            this.label42.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label42.Location = new System.Drawing.Point(10, 142);
            this.label42.Name = "label42";
            this.label42.Size = new System.Drawing.Size(107, 15);
            this.label42.TabIndex = 73;
            this.label42.Text = "FIFO Full";
            // 
            // lblCH_StatTimeoutError
            // 
            this.lblCH_StatTimeoutError.BackColor = System.Drawing.Color.White;
            this.lblCH_StatTimeoutError.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatTimeoutError.Location = new System.Drawing.Point(117, 109);
            this.lblCH_StatTimeoutError.Name = "lblCH_StatTimeoutError";
            this.lblCH_StatTimeoutError.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatTimeoutError.TabIndex = 62;
            // 
            // lblCH_StatFIFONotEmpty
            // 
            this.lblCH_StatFIFONotEmpty.BackColor = System.Drawing.Color.White;
            this.lblCH_StatFIFONotEmpty.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatFIFONotEmpty.Location = new System.Drawing.Point(117, 127);
            this.lblCH_StatFIFONotEmpty.Name = "lblCH_StatFIFONotEmpty";
            this.lblCH_StatFIFONotEmpty.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatFIFONotEmpty.TabIndex = 72;
            // 
            // label36
            // 
            this.label36.BackColor = System.Drawing.Color.Coral;
            this.label36.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label36.Location = new System.Drawing.Point(10, 205);
            this.label36.Name = "label36";
            this.label36.Size = new System.Drawing.Size(107, 15);
            this.label36.TabIndex = 63;
            this.label36.Text = "Serializer SYNC";
            // 
            // label44
            // 
            this.label44.BackColor = System.Drawing.Color.Coral;
            this.label44.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label44.Location = new System.Drawing.Point(10, 127);
            this.label44.Name = "label44";
            this.label44.Size = new System.Drawing.Size(107, 15);
            this.label44.TabIndex = 71;
            this.label44.Text = "FIFO Not Empty";
            // 
            // lblCH_StatSerializerSYNC
            // 
            this.lblCH_StatSerializerSYNC.BackColor = System.Drawing.Color.White;
            this.lblCH_StatSerializerSYNC.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatSerializerSYNC.Location = new System.Drawing.Point(117, 205);
            this.lblCH_StatSerializerSYNC.Name = "lblCH_StatSerializerSYNC";
            this.lblCH_StatSerializerSYNC.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatSerializerSYNC.TabIndex = 64;
            // 
            // lblCH_StatPLL1LOCK
            // 
            this.lblCH_StatPLL1LOCK.BackColor = System.Drawing.Color.White;
            this.lblCH_StatPLL1LOCK.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatPLL1LOCK.Location = new System.Drawing.Point(117, 268);
            this.lblCH_StatPLL1LOCK.Name = "lblCH_StatPLL1LOCK";
            this.lblCH_StatPLL1LOCK.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatPLL1LOCK.TabIndex = 70;
            // 
            // label34
            // 
            this.label34.BackColor = System.Drawing.Color.Coral;
            this.label34.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label34.Location = new System.Drawing.Point(10, 220);
            this.label34.Name = "label34";
            this.label34.Size = new System.Drawing.Size(107, 15);
            this.label34.TabIndex = 65;
            this.label34.Text = "Deserializer LOCK";
            // 
            // label30
            // 
            this.label30.BackColor = System.Drawing.Color.Coral;
            this.label30.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label30.Location = new System.Drawing.Point(10, 268);
            this.label30.Name = "label30";
            this.label30.Size = new System.Drawing.Size(107, 15);
            this.label30.TabIndex = 69;
            this.label30.Text = "PLL1 LOCK";
            // 
            // lblCH_StatDeserializerLOCK
            // 
            this.lblCH_StatDeserializerLOCK.BackColor = System.Drawing.Color.White;
            this.lblCH_StatDeserializerLOCK.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatDeserializerLOCK.Location = new System.Drawing.Point(117, 220);
            this.lblCH_StatDeserializerLOCK.Name = "lblCH_StatDeserializerLOCK";
            this.lblCH_StatDeserializerLOCK.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatDeserializerLOCK.TabIndex = 66;
            // 
            // lblCH_StatPLL0LOCK
            // 
            this.lblCH_StatPLL0LOCK.BackColor = System.Drawing.Color.White;
            this.lblCH_StatPLL0LOCK.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatPLL0LOCK.Location = new System.Drawing.Point(117, 253);
            this.lblCH_StatPLL0LOCK.Name = "lblCH_StatPLL0LOCK";
            this.lblCH_StatPLL0LOCK.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatPLL0LOCK.TabIndex = 68;
            // 
            // label32
            // 
            this.label32.BackColor = System.Drawing.Color.Coral;
            this.label32.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label32.Location = new System.Drawing.Point(10, 253);
            this.label32.Name = "label32";
            this.label32.Size = new System.Drawing.Size(107, 15);
            this.label32.TabIndex = 67;
            this.label32.Text = "PLL0 LOCK";
            // 
            // groupBoxCH_FLASH
            // 
            this.groupBoxCH_FLASH.Controls.Add(this.btn_CHWriteFileToSPI);
            this.groupBoxCH_FLASH.Controls.Add(this.btn_CHReBootFEs);
            this.groupBoxCH_FLASH.Location = new System.Drawing.Point(16, 42);
            this.groupBoxCH_FLASH.Name = "groupBoxCH_FLASH";
            this.groupBoxCH_FLASH.Size = new System.Drawing.Size(341, 70);
            this.groupBoxCH_FLASH.TabIndex = 87;
            this.groupBoxCH_FLASH.TabStop = false;
            this.groupBoxCH_FLASH.Text = "FLASH Commands";
            this.groupBoxCH_FLASH.Visible = false;
            // 
            // btn_CHWriteFileToSPI
            // 
            this.btn_CHWriteFileToSPI.BackColor = System.Drawing.Color.Coral;
            this.btn_CHWriteFileToSPI.Location = new System.Drawing.Point(6, 19);
            this.btn_CHWriteFileToSPI.Name = "btn_CHWriteFileToSPI";
            this.btn_CHWriteFileToSPI.Size = new System.Drawing.Size(216, 20);
            this.btn_CHWriteFileToSPI.TabIndex = 50;
            this.btn_CHWriteFileToSPI.Text = "Write File To FLASH Memory";
            this.btn_CHWriteFileToSPI.UseVisualStyleBackColor = false;
            this.btn_CHWriteFileToSPI.Click += new System.EventHandler(this.btn_CHWriteFileToSPI_Click);
            // 
            // btn_CHReBootFEs
            // 
            this.btn_CHReBootFEs.BackColor = System.Drawing.Color.Coral;
            this.btn_CHReBootFEs.Location = new System.Drawing.Point(6, 44);
            this.btn_CHReBootFEs.Name = "btn_CHReBootFEs";
            this.btn_CHReBootFEs.Size = new System.Drawing.Size(216, 20);
            this.btn_CHReBootFEs.TabIndex = 51;
            this.btn_CHReBootFEs.Text = "Reboot FEs (reload FLASH content)";
            this.btn_CHReBootFEs.UseVisualStyleBackColor = false;
            this.btn_CHReBootFEs.Click += new System.EventHandler(this.btn_CHReBootFEs_Click);
            // 
            // groupBoxCH_DPM
            // 
            this.groupBoxCH_DPM.Controls.Add(this.btn_CHDPMPointerReset);
            this.groupBoxCH_DPM.Controls.Add(this.btn_CHDPMPointerRead);
            this.groupBoxCH_DPM.Controls.Add(this.lblCH_DPMPointerValue);
            this.groupBoxCH_DPM.Location = new System.Drawing.Point(164, 120);
            this.groupBoxCH_DPM.Name = "groupBoxCH_DPM";
            this.groupBoxCH_DPM.Size = new System.Drawing.Size(193, 78);
            this.groupBoxCH_DPM.TabIndex = 85;
            this.groupBoxCH_DPM.TabStop = false;
            this.groupBoxCH_DPM.Text = "DPM Register";
            this.groupBoxCH_DPM.Visible = false;
            // 
            // btn_CHDPMPointerReset
            // 
            this.btn_CHDPMPointerReset.BackColor = System.Drawing.Color.Coral;
            this.btn_CHDPMPointerReset.Location = new System.Drawing.Point(10, 20);
            this.btn_CHDPMPointerReset.Name = "btn_CHDPMPointerReset";
            this.btn_CHDPMPointerReset.Size = new System.Drawing.Size(114, 20);
            this.btn_CHDPMPointerReset.TabIndex = 82;
            this.btn_CHDPMPointerReset.Text = "Reset DPM Pointer";
            this.btn_CHDPMPointerReset.UseVisualStyleBackColor = false;
            this.btn_CHDPMPointerReset.Click += new System.EventHandler(this.btn_CHDPMPointerReset_Click);
            // 
            // btn_CHDPMPointerRead
            // 
            this.btn_CHDPMPointerRead.BackColor = System.Drawing.Color.Coral;
            this.btn_CHDPMPointerRead.Location = new System.Drawing.Point(10, 42);
            this.btn_CHDPMPointerRead.Name = "btn_CHDPMPointerRead";
            this.btn_CHDPMPointerRead.Size = new System.Drawing.Size(115, 20);
            this.btn_CHDPMPointerRead.TabIndex = 80;
            this.btn_CHDPMPointerRead.Text = "Read  DPM Pointer";
            this.btn_CHDPMPointerRead.UseVisualStyleBackColor = false;
            this.btn_CHDPMPointerRead.Click += new System.EventHandler(this.btn_CHDPMPointerRead_Click);
            // 
            // lblCH_DPMPointerValue
            // 
            this.lblCH_DPMPointerValue.BackColor = System.Drawing.Color.White;
            this.lblCH_DPMPointerValue.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_DPMPointerValue.Location = new System.Drawing.Point(122, 43);
            this.lblCH_DPMPointerValue.Name = "lblCH_DPMPointerValue";
            this.lblCH_DPMPointerValue.RightToLeft = System.Windows.Forms.RightToLeft.Yes;
            this.lblCH_DPMPointerValue.Size = new System.Drawing.Size(57, 18);
            this.lblCH_DPMPointerValue.TabIndex = 81;
            // 
            // label4
            // 
            this.label4.BackColor = System.Drawing.Color.White;
            this.label4.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label4.Location = new System.Drawing.Point(54, 16);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(30, 18);
            this.label4.TabIndex = 52;
            this.label4.Text = "ALL";
            // 
            // btn_CHAdvancedGUI
            // 
            this.btn_CHAdvancedGUI.BackColor = System.Drawing.Color.Coral;
            this.btn_CHAdvancedGUI.Location = new System.Drawing.Point(238, 16);
            this.btn_CHAdvancedGUI.Name = "btn_CHAdvancedGUI";
            this.btn_CHAdvancedGUI.Size = new System.Drawing.Size(120, 20);
            this.btn_CHAdvancedGUI.TabIndex = 49;
            this.btn_CHAdvancedGUI.Text = "Show Advanced GUI";
            this.btn_CHAdvancedGUI.UseVisualStyleBackColor = false;
            this.btn_CHAdvancedGUI.Click += new System.EventHandler(this.btn_CHAdvancedGUI_Click);
            // 
            // lblCH_CROCID
            // 
            this.lblCH_CROCID.BackColor = System.Drawing.Color.White;
            this.lblCH_CROCID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_CROCID.Location = new System.Drawing.Point(202, 16);
            this.lblCH_CROCID.Name = "lblCH_CROCID";
            this.lblCH_CROCID.Size = new System.Drawing.Size(30, 18);
            this.lblCH_CROCID.TabIndex = 48;
            // 
            // label10
            // 
            this.label10.BackColor = System.Drawing.Color.Coral;
            this.label10.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label10.Location = new System.Drawing.Point(164, 16);
            this.label10.Name = "label10";
            this.label10.Size = new System.Drawing.Size(40, 18);
            this.label10.TabIndex = 47;
            this.label10.Text = "CROC";
            // 
            // lblCH_CHID
            // 
            this.lblCH_CHID.BackColor = System.Drawing.Color.White;
            this.lblCH_CHID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_CHID.Location = new System.Drawing.Point(128, 16);
            this.lblCH_CHID.Name = "lblCH_CHID";
            this.lblCH_CHID.Size = new System.Drawing.Size(30, 18);
            this.lblCH_CHID.TabIndex = 46;
            // 
            // label14
            // 
            this.label14.BackColor = System.Drawing.Color.Coral;
            this.label14.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label14.Location = new System.Drawing.Point(90, 16);
            this.label14.Name = "label14";
            this.label14.Size = new System.Drawing.Size(40, 18);
            this.label14.TabIndex = 45;
            this.label14.Text = "CH";
            // 
            // label16
            // 
            this.label16.BackColor = System.Drawing.Color.Coral;
            this.label16.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label16.Location = new System.Drawing.Point(16, 16);
            this.label16.Name = "label16";
            this.label16.Size = new System.Drawing.Size(40, 18);
            this.label16.TabIndex = 43;
            this.label16.Text = "FE";
            // 
            // tabFE
            // 
            this.tabFE.Location = new System.Drawing.Point(4, 22);
            this.tabFE.Name = "tabFE";
            this.tabFE.Size = new System.Drawing.Size(899, 502);
            this.tabFE.TabIndex = 7;
            this.tabFE.Text = "FE";
            this.tabFE.UseVisualStyleBackColor = true;
            // 
            // tabFPGARegs
            // 
            this.tabFPGARegs.Controls.Add(this.btn_AllFEsFPGARegWrite);
            this.tabFPGARegs.Controls.Add(this.btn_FPGAAdvancedGUI);
            this.tabFPGARegs.Controls.Add(this.lblFPGA_CROCID);
            this.tabFPGARegs.Controls.Add(this.label7);
            this.tabFPGARegs.Controls.Add(this.lblFPGA_CHID);
            this.tabFPGARegs.Controls.Add(this.label5);
            this.tabFPGARegs.Controls.Add(this.lblFPGA_FEID);
            this.tabFPGARegs.Controls.Add(this.btn_FPGARegRead);
            this.tabFPGARegs.Controls.Add(this.btn_FPGARegWrite);
            this.tabFPGARegs.Controls.Add(this.label1);
            this.tabFPGARegs.Controls.Add(this.fpgaDevRegControl1);
            this.tabFPGARegs.Location = new System.Drawing.Point(4, 22);
            this.tabFPGARegs.Name = "tabFPGARegs";
            this.tabFPGARegs.Padding = new System.Windows.Forms.Padding(3);
            this.tabFPGARegs.Size = new System.Drawing.Size(899, 502);
            this.tabFPGARegs.TabIndex = 0;
            this.tabFPGARegs.Text = "FPGA Regs";
            this.tabFPGARegs.UseVisualStyleBackColor = true;
            // 
            // btn_AllFEsFPGARegWrite
            // 
            this.btn_AllFEsFPGARegWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_AllFEsFPGARegWrite.Location = new System.Drawing.Point(303, 92);
            this.btn_AllFEsFPGARegWrite.Name = "btn_AllFEsFPGARegWrite";
            this.btn_AllFEsFPGARegWrite.Size = new System.Drawing.Size(55, 35);
            this.btn_AllFEsFPGARegWrite.TabIndex = 25;
            this.btn_AllFEsFPGARegWrite.Text = "WRITE ALL FEs";
            this.btn_AllFEsFPGARegWrite.UseVisualStyleBackColor = false;
            this.btn_AllFEsFPGARegWrite.Click += new System.EventHandler(this.btn_AllFEsFPGARegWrite_Click);
            // 
            // btn_FPGAAdvancedGUI
            // 
            this.btn_FPGAAdvancedGUI.BackColor = System.Drawing.Color.Coral;
            this.btn_FPGAAdvancedGUI.Location = new System.Drawing.Point(238, 14);
            this.btn_FPGAAdvancedGUI.Name = "btn_FPGAAdvancedGUI";
            this.btn_FPGAAdvancedGUI.Size = new System.Drawing.Size(120, 20);
            this.btn_FPGAAdvancedGUI.TabIndex = 24;
            this.btn_FPGAAdvancedGUI.Text = "Show Default GUI";
            this.btn_FPGAAdvancedGUI.UseVisualStyleBackColor = false;
            this.btn_FPGAAdvancedGUI.Click += new System.EventHandler(this.btn_FPGAAdvancedGUI_Click);
            // 
            // lblFPGA_CROCID
            // 
            this.lblFPGA_CROCID.BackColor = System.Drawing.Color.White;
            this.lblFPGA_CROCID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblFPGA_CROCID.Location = new System.Drawing.Point(202, 16);
            this.lblFPGA_CROCID.Name = "lblFPGA_CROCID";
            this.lblFPGA_CROCID.Size = new System.Drawing.Size(30, 18);
            this.lblFPGA_CROCID.TabIndex = 22;
            // 
            // label7
            // 
            this.label7.BackColor = System.Drawing.Color.Coral;
            this.label7.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label7.Location = new System.Drawing.Point(164, 16);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(40, 18);
            this.label7.TabIndex = 21;
            this.label7.Text = "CROC";
            // 
            // lblFPGA_CHID
            // 
            this.lblFPGA_CHID.BackColor = System.Drawing.Color.White;
            this.lblFPGA_CHID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblFPGA_CHID.Location = new System.Drawing.Point(128, 16);
            this.lblFPGA_CHID.Name = "lblFPGA_CHID";
            this.lblFPGA_CHID.Size = new System.Drawing.Size(30, 18);
            this.lblFPGA_CHID.TabIndex = 20;
            // 
            // label5
            // 
            this.label5.BackColor = System.Drawing.Color.Coral;
            this.label5.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label5.Location = new System.Drawing.Point(90, 16);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(40, 18);
            this.label5.TabIndex = 19;
            this.label5.Text = "CH";
            // 
            // lblFPGA_FEID
            // 
            this.lblFPGA_FEID.BackColor = System.Drawing.Color.White;
            this.lblFPGA_FEID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblFPGA_FEID.Location = new System.Drawing.Point(54, 16);
            this.lblFPGA_FEID.Name = "lblFPGA_FEID";
            this.lblFPGA_FEID.Size = new System.Drawing.Size(30, 18);
            this.lblFPGA_FEID.TabIndex = 18;
            // 
            // btn_FPGARegRead
            // 
            this.btn_FPGARegRead.BackColor = System.Drawing.Color.Coral;
            this.btn_FPGARegRead.Location = new System.Drawing.Point(303, 40);
            this.btn_FPGARegRead.Name = "btn_FPGARegRead";
            this.btn_FPGARegRead.Size = new System.Drawing.Size(55, 20);
            this.btn_FPGARegRead.TabIndex = 7;
            this.btn_FPGARegRead.Text = "READ";
            this.btn_FPGARegRead.UseVisualStyleBackColor = false;
            this.btn_FPGARegRead.Click += new System.EventHandler(this.btn_FPGARegRead_Click);
            // 
            // btn_FPGARegWrite
            // 
            this.btn_FPGARegWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_FPGARegWrite.Location = new System.Drawing.Point(303, 66);
            this.btn_FPGARegWrite.Name = "btn_FPGARegWrite";
            this.btn_FPGARegWrite.Size = new System.Drawing.Size(55, 20);
            this.btn_FPGARegWrite.TabIndex = 6;
            this.btn_FPGARegWrite.Text = "WRITE";
            this.btn_FPGARegWrite.UseVisualStyleBackColor = false;
            this.btn_FPGARegWrite.Click += new System.EventHandler(this.btn_FPGARegWrite_Click);
            // 
            // label1
            // 
            this.label1.BackColor = System.Drawing.Color.Coral;
            this.label1.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label1.Location = new System.Drawing.Point(16, 16);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(40, 18);
            this.label1.TabIndex = 1;
            this.label1.Text = "FE";
            // 
            // fpgaDevRegControl1
            // 
            this.fpgaDevRegControl1.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)));
            this.fpgaDevRegControl1.AutoScroll = true;
            this.fpgaDevRegControl1.FPGARegValues = new uint[] {
        ((uint)(12u)),
        ((uint)(65488u)),
        ((uint)(1024u)),
        ((uint)(63u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(1u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(32768u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(1u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(15u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(415029u)),
        ((uint)(415029u)),
        ((uint)(415029u)),
        ((uint)(415029u)),
        ((uint)(0u))};
            this.fpgaDevRegControl1.Location = new System.Drawing.Point(6, 37);
            this.fpgaDevRegControl1.Name = "fpgaDevRegControl1";
            this.fpgaDevRegControl1.RegisterBoardID = ((uint)(15u));
            this.fpgaDevRegControl1.RegisterDCM1Lock = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterDCM1NoClock = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterDCM2Lock = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterDCM2NoClock = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterDCM2PhaseDone = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterDCM2PhaseTotal = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterDiscrimEnableMaskTrip0 = ((uint)(415029u));
            this.fpgaDevRegControl1.RegisterDiscrimEnableMaskTrip1 = ((uint)(415029u));
            this.fpgaDevRegControl1.RegisterDiscrimEnableMaskTrip2 = ((uint)(415029u));
            this.fpgaDevRegControl1.RegisterDiscrimEnableMaskTrip3 = ((uint)(415029u));
            this.fpgaDevRegControl1.RegisterExtTriggFound = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterExtTriggRearm = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterFirmwareVersion = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterGateLength = ((uint)(1024u));
            this.fpgaDevRegControl1.RegisterGateStart = ((uint)(65488u));
            this.fpgaDevRegControl1.RegisterGateTimeStamp = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterHVActual = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterHVAutoManual = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterHVControl = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterHVEnabled = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterHVNumAvg = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterHVPeriodAuto = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterHVPeriodManual = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterHVPulseWidth = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterHVTarget = ((uint)(32768u));
            this.fpgaDevRegControl1.RegisterInjectCount = new uint[] {
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u))};
            this.fpgaDevRegControl1.RegisterInjectDACDone = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterInjectDACMode = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterInjectDACStart = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterInjectDACValue = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterInjectEnable = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterInjectPhase = ((uint)(1u));
            this.fpgaDevRegControl1.RegisterInjectRange = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterPhaseIncrement = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterPhaseSpare = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterPhaseStart = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterPhaseTicks = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterTemperature = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterTestPulse2Bit = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterTestPulseCount = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterTimer = ((uint)(12u));
            this.fpgaDevRegControl1.RegisterTripPowerOff = ((uint)(63u));
            this.fpgaDevRegControl1.RegisterTripXComparators = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterTripXThreshold = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterVXOMuxSelect = ((uint)(1u));
            this.fpgaDevRegControl1.Size = new System.Drawing.Size(250, 459);
            this.fpgaDevRegControl1.TabIndex = 23;
            // 
            // tabTRIPRegs
            // 
            this.tabTRIPRegs.Controls.Add(this.btn_AllFEsTRIPRegWrite);
            this.tabTRIPRegs.Controls.Add(this.cmb_TripID);
            this.tabTRIPRegs.Controls.Add(this.btn_TRIPAdvancedGUI);
            this.tabTRIPRegs.Controls.Add(this.lblTRIP_CROCID);
            this.tabTRIPRegs.Controls.Add(this.label3);
            this.tabTRIPRegs.Controls.Add(this.lblTRIP_CHID);
            this.tabTRIPRegs.Controls.Add(this.label6);
            this.tabTRIPRegs.Controls.Add(this.lblTRIP_FEID);
            this.tabTRIPRegs.Controls.Add(this.btn_TRIPRegRead);
            this.tabTRIPRegs.Controls.Add(this.btn_TRIPRegWrite);
            this.tabTRIPRegs.Controls.Add(this.label9);
            this.tabTRIPRegs.Controls.Add(this.tripDevRegControl1);
            this.tabTRIPRegs.Location = new System.Drawing.Point(4, 22);
            this.tabTRIPRegs.Name = "tabTRIPRegs";
            this.tabTRIPRegs.Padding = new System.Windows.Forms.Padding(3);
            this.tabTRIPRegs.Size = new System.Drawing.Size(899, 502);
            this.tabTRIPRegs.TabIndex = 1;
            this.tabTRIPRegs.Text = "TRIP Regs";
            this.tabTRIPRegs.UseVisualStyleBackColor = true;
            // 
            // btn_AllFEsTRIPRegWrite
            // 
            this.btn_AllFEsTRIPRegWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_AllFEsTRIPRegWrite.Location = new System.Drawing.Point(303, 117);
            this.btn_AllFEsTRIPRegWrite.Name = "btn_AllFEsTRIPRegWrite";
            this.btn_AllFEsTRIPRegWrite.Size = new System.Drawing.Size(55, 35);
            this.btn_AllFEsTRIPRegWrite.TabIndex = 38;
            this.btn_AllFEsTRIPRegWrite.Text = "WRITE ALL FEs";
            this.btn_AllFEsTRIPRegWrite.UseVisualStyleBackColor = false;
            this.btn_AllFEsTRIPRegWrite.Click += new System.EventHandler(this.btn_AllFEsTRIPRegWrite_Click);
            // 
            // cmb_TripID
            // 
            this.cmb_TripID.FormattingEnabled = true;
            this.cmb_TripID.Items.AddRange(new object[] {
            "T0",
            "T1",
            "T2",
            "T3",
            "T4",
            "T5"});
            this.cmb_TripID.Location = new System.Drawing.Point(303, 90);
            this.cmb_TripID.Name = "cmb_TripID";
            this.cmb_TripID.Size = new System.Drawing.Size(55, 21);
            this.cmb_TripID.TabIndex = 36;
            this.cmb_TripID.SelectedIndexChanged += new System.EventHandler(this.cmb_TripID_SelectedIndexChanged);
            // 
            // btn_TRIPAdvancedGUI
            // 
            this.btn_TRIPAdvancedGUI.BackColor = System.Drawing.Color.Coral;
            this.btn_TRIPAdvancedGUI.Location = new System.Drawing.Point(238, 14);
            this.btn_TRIPAdvancedGUI.Name = "btn_TRIPAdvancedGUI";
            this.btn_TRIPAdvancedGUI.Size = new System.Drawing.Size(120, 20);
            this.btn_TRIPAdvancedGUI.TabIndex = 34;
            this.btn_TRIPAdvancedGUI.Text = "Show Advanced GUI";
            this.btn_TRIPAdvancedGUI.UseVisualStyleBackColor = false;
            this.btn_TRIPAdvancedGUI.Click += new System.EventHandler(this.btn_TRIPAdvancedGUI_Click);
            // 
            // lblTRIP_CROCID
            // 
            this.lblTRIP_CROCID.BackColor = System.Drawing.Color.White;
            this.lblTRIP_CROCID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblTRIP_CROCID.Location = new System.Drawing.Point(202, 16);
            this.lblTRIP_CROCID.Name = "lblTRIP_CROCID";
            this.lblTRIP_CROCID.Size = new System.Drawing.Size(30, 18);
            this.lblTRIP_CROCID.TabIndex = 32;
            // 
            // label3
            // 
            this.label3.BackColor = System.Drawing.Color.Coral;
            this.label3.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label3.Location = new System.Drawing.Point(164, 16);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(40, 18);
            this.label3.TabIndex = 31;
            this.label3.Text = "CROC";
            // 
            // lblTRIP_CHID
            // 
            this.lblTRIP_CHID.BackColor = System.Drawing.Color.White;
            this.lblTRIP_CHID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblTRIP_CHID.Location = new System.Drawing.Point(128, 16);
            this.lblTRIP_CHID.Name = "lblTRIP_CHID";
            this.lblTRIP_CHID.Size = new System.Drawing.Size(30, 18);
            this.lblTRIP_CHID.TabIndex = 30;
            // 
            // label6
            // 
            this.label6.BackColor = System.Drawing.Color.Coral;
            this.label6.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label6.Location = new System.Drawing.Point(90, 16);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(40, 18);
            this.label6.TabIndex = 29;
            this.label6.Text = "CH";
            // 
            // lblTRIP_FEID
            // 
            this.lblTRIP_FEID.BackColor = System.Drawing.Color.White;
            this.lblTRIP_FEID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblTRIP_FEID.Location = new System.Drawing.Point(54, 16);
            this.lblTRIP_FEID.Name = "lblTRIP_FEID";
            this.lblTRIP_FEID.Size = new System.Drawing.Size(30, 18);
            this.lblTRIP_FEID.TabIndex = 28;
            // 
            // btn_TRIPRegRead
            // 
            this.btn_TRIPRegRead.BackColor = System.Drawing.Color.Coral;
            this.btn_TRIPRegRead.Location = new System.Drawing.Point(303, 38);
            this.btn_TRIPRegRead.Name = "btn_TRIPRegRead";
            this.btn_TRIPRegRead.Size = new System.Drawing.Size(55, 20);
            this.btn_TRIPRegRead.TabIndex = 27;
            this.btn_TRIPRegRead.Text = "READ";
            this.btn_TRIPRegRead.UseVisualStyleBackColor = false;
            this.btn_TRIPRegRead.Click += new System.EventHandler(this.btn_TRIPRegRead_Click);
            // 
            // btn_TRIPRegWrite
            // 
            this.btn_TRIPRegWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_TRIPRegWrite.Location = new System.Drawing.Point(303, 64);
            this.btn_TRIPRegWrite.Name = "btn_TRIPRegWrite";
            this.btn_TRIPRegWrite.Size = new System.Drawing.Size(55, 20);
            this.btn_TRIPRegWrite.TabIndex = 26;
            this.btn_TRIPRegWrite.Text = "WRITE";
            this.btn_TRIPRegWrite.UseVisualStyleBackColor = false;
            this.btn_TRIPRegWrite.Click += new System.EventHandler(this.btn_TRIPRegWrite_Click);
            // 
            // label9
            // 
            this.label9.BackColor = System.Drawing.Color.Coral;
            this.label9.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label9.Location = new System.Drawing.Point(16, 16);
            this.label9.Name = "label9";
            this.label9.Size = new System.Drawing.Size(40, 18);
            this.label9.TabIndex = 25;
            this.label9.Text = "FE";
            // 
            // tripDevRegControl1
            // 
            this.tripDevRegControl1.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)));
            this.tripDevRegControl1.AutoScroll = true;
            this.tripDevRegControl1.Location = new System.Drawing.Point(6, 37);
            this.tripDevRegControl1.Name = "tripDevRegControl1";
            this.tripDevRegControl1.RegisterGAIN = ((uint)(5u));
            this.tripDevRegControl1.RegisterIB_T = ((uint)(0u));
            this.tripDevRegControl1.RegisterIBBNFALL = ((uint)(120u));
            this.tripDevRegControl1.RegisterIBCOMP = ((uint)(20u));
            this.tripDevRegControl1.RegisterIBP = ((uint)(100u));
            this.tripDevRegControl1.RegisterIBPIFF1REF = ((uint)(160u));
            this.tripDevRegControl1.RegisterIBPOPAMP = ((uint)(40u));
            this.tripDevRegControl1.RegisterIFF = ((uint)(0u));
            this.tripDevRegControl1.RegisterIFFP2 = ((uint)(0u));
            this.tripDevRegControl1.RegisterINJB0 = ((uint)(0u));
            this.tripDevRegControl1.RegisterINJB1 = ((uint)(0u));
            this.tripDevRegControl1.RegisterINJB2 = ((uint)(0u));
            this.tripDevRegControl1.RegisterINJB3 = ((uint)(0u));
            this.tripDevRegControl1.RegisterINJEX0 = ((uint)(0u));
            this.tripDevRegControl1.RegisterINJEX33 = ((uint)(0u));
            this.tripDevRegControl1.RegisterIRSEL = ((uint)(3u));
            this.tripDevRegControl1.RegisterIWSEL = ((uint)(3u));
            this.tripDevRegControl1.RegisterPIPEDEL = ((uint)(1u));
            this.tripDevRegControl1.RegisterVREF = ((uint)(20u));
            this.tripDevRegControl1.RegisterVTH = ((uint)(0u));
            this.tripDevRegControl1.Size = new System.Drawing.Size(250, 467);
            this.tripDevRegControl1.TabIndex = 35;
            this.tripDevRegControl1.TRIPRegValues = new uint[] {
        ((uint)(100u)),
        ((uint)(120u)),
        ((uint)(0u)),
        ((uint)(160u)),
        ((uint)(40u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(20u)),
        ((uint)(20u)),
        ((uint)(0u)),
        ((uint)(5u)),
        ((uint)(1u)),
        ((uint)(3u)),
        ((uint)(3u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u)),
        ((uint)(0u))};
            // 
            // tabFLASHPages
            // 
            this.tabFLASHPages.Controls.Add(this.btn_FLASHWriteFileToSPI);
            this.tabFLASHPages.Controls.Add(this.btn_FLASHAdvancedGUI);
            this.tabFLASHPages.Controls.Add(this.lblFLASH_CROCID);
            this.tabFLASHPages.Controls.Add(this.label8);
            this.tabFLASHPages.Controls.Add(this.lblFLASH_CHID);
            this.tabFLASHPages.Controls.Add(this.label11);
            this.tabFLASHPages.Controls.Add(this.lblFLASH_FEID);
            this.tabFLASHPages.Controls.Add(this.label13);
            this.tabFLASHPages.Controls.Add(this.btn_FLASHReadSPIToFile);
            this.tabFLASHPages.Location = new System.Drawing.Point(4, 22);
            this.tabFLASHPages.Name = "tabFLASHPages";
            this.tabFLASHPages.Padding = new System.Windows.Forms.Padding(3);
            this.tabFLASHPages.Size = new System.Drawing.Size(899, 502);
            this.tabFLASHPages.TabIndex = 2;
            this.tabFLASHPages.Text = "FLASH";
            this.tabFLASHPages.UseVisualStyleBackColor = true;
            // 
            // btn_FLASHWriteFileToSPI
            // 
            this.btn_FLASHWriteFileToSPI.BackColor = System.Drawing.Color.Coral;
            this.btn_FLASHWriteFileToSPI.Location = new System.Drawing.Point(16, 75);
            this.btn_FLASHWriteFileToSPI.Name = "btn_FLASHWriteFileToSPI";
            this.btn_FLASHWriteFileToSPI.Size = new System.Drawing.Size(216, 20);
            this.btn_FLASHWriteFileToSPI.TabIndex = 44;
            this.btn_FLASHWriteFileToSPI.Text = "Write File To Memory";
            this.btn_FLASHWriteFileToSPI.UseVisualStyleBackColor = false;
            this.btn_FLASHWriteFileToSPI.Visible = false;
            this.btn_FLASHWriteFileToSPI.Click += new System.EventHandler(this.btn_FLASHWriteFileToSPI_Click);
            // 
            // btn_FLASHAdvancedGUI
            // 
            this.btn_FLASHAdvancedGUI.BackColor = System.Drawing.Color.Coral;
            this.btn_FLASHAdvancedGUI.Location = new System.Drawing.Point(238, 14);
            this.btn_FLASHAdvancedGUI.Name = "btn_FLASHAdvancedGUI";
            this.btn_FLASHAdvancedGUI.Size = new System.Drawing.Size(120, 20);
            this.btn_FLASHAdvancedGUI.TabIndex = 42;
            this.btn_FLASHAdvancedGUI.Text = "Show Advanced GUI";
            this.btn_FLASHAdvancedGUI.UseVisualStyleBackColor = false;
            this.btn_FLASHAdvancedGUI.Click += new System.EventHandler(this.btn_FLASHAdvancedGUI_Click);
            // 
            // lblFLASH_CROCID
            // 
            this.lblFLASH_CROCID.BackColor = System.Drawing.Color.White;
            this.lblFLASH_CROCID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblFLASH_CROCID.Location = new System.Drawing.Point(202, 16);
            this.lblFLASH_CROCID.Name = "lblFLASH_CROCID";
            this.lblFLASH_CROCID.Size = new System.Drawing.Size(30, 18);
            this.lblFLASH_CROCID.TabIndex = 41;
            // 
            // label8
            // 
            this.label8.BackColor = System.Drawing.Color.Coral;
            this.label8.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label8.Location = new System.Drawing.Point(164, 16);
            this.label8.Name = "label8";
            this.label8.Size = new System.Drawing.Size(40, 18);
            this.label8.TabIndex = 40;
            this.label8.Text = "CROC";
            // 
            // lblFLASH_CHID
            // 
            this.lblFLASH_CHID.BackColor = System.Drawing.Color.White;
            this.lblFLASH_CHID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblFLASH_CHID.Location = new System.Drawing.Point(128, 16);
            this.lblFLASH_CHID.Name = "lblFLASH_CHID";
            this.lblFLASH_CHID.Size = new System.Drawing.Size(30, 18);
            this.lblFLASH_CHID.TabIndex = 39;
            // 
            // label11
            // 
            this.label11.BackColor = System.Drawing.Color.Coral;
            this.label11.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label11.Location = new System.Drawing.Point(90, 16);
            this.label11.Name = "label11";
            this.label11.Size = new System.Drawing.Size(40, 18);
            this.label11.TabIndex = 38;
            this.label11.Text = "CH";
            // 
            // lblFLASH_FEID
            // 
            this.lblFLASH_FEID.BackColor = System.Drawing.Color.White;
            this.lblFLASH_FEID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblFLASH_FEID.Location = new System.Drawing.Point(54, 16);
            this.lblFLASH_FEID.Name = "lblFLASH_FEID";
            this.lblFLASH_FEID.Size = new System.Drawing.Size(30, 18);
            this.lblFLASH_FEID.TabIndex = 37;
            // 
            // label13
            // 
            this.label13.BackColor = System.Drawing.Color.Coral;
            this.label13.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label13.Location = new System.Drawing.Point(16, 16);
            this.label13.Name = "label13";
            this.label13.Size = new System.Drawing.Size(40, 18);
            this.label13.TabIndex = 36;
            this.label13.Text = "FE";
            // 
            // btn_FLASHReadSPIToFile
            // 
            this.btn_FLASHReadSPIToFile.BackColor = System.Drawing.Color.Coral;
            this.btn_FLASHReadSPIToFile.Location = new System.Drawing.Point(16, 50);
            this.btn_FLASHReadSPIToFile.Name = "btn_FLASHReadSPIToFile";
            this.btn_FLASHReadSPIToFile.Size = new System.Drawing.Size(216, 20);
            this.btn_FLASHReadSPIToFile.TabIndex = 35;
            this.btn_FLASHReadSPIToFile.Text = "Read Memory To File";
            this.btn_FLASHReadSPIToFile.UseVisualStyleBackColor = false;
            this.btn_FLASHReadSPIToFile.Visible = false;
            this.btn_FLASHReadSPIToFile.Click += new System.EventHandler(this.btn_FLASHReadSPIToFile_Click);
            // 
            // tabReadHV
            // 
            this.tabReadHV.Controls.Add(this.richTextBoxHVRead);
            this.tabReadHV.Controls.Add(this.btnMonitorHV);
            this.tabReadHV.Controls.Add(this.label27);
            this.tabReadHV.Controls.Add(this.textBoxMonitorTimer);
            this.tabReadHV.Controls.Add(this.btnSwitchToAuto);
            this.tabReadHV.Controls.Add(this.textBoxADCThreshold);
            this.tabReadHV.Controls.Add(this.label2);
            this.tabReadHV.Controls.Add(this.btnReadHV);
            this.tabReadHV.Location = new System.Drawing.Point(4, 22);
            this.tabReadHV.Name = "tabReadHV";
            this.tabReadHV.Size = new System.Drawing.Size(899, 502);
            this.tabReadHV.TabIndex = 8;
            this.tabReadHV.Text = "Read HV";
            this.tabReadHV.UseVisualStyleBackColor = true;
            // 
            // richTextBoxHVRead
            // 
            this.richTextBoxHVRead.Location = new System.Drawing.Point(3, 3);
            this.richTextBoxHVRead.Name = "richTextBoxHVRead";
            this.richTextBoxHVRead.Size = new System.Drawing.Size(458, 446);
            this.richTextBoxHVRead.TabIndex = 11;
            this.richTextBoxHVRead.Text = "";
            // 
            // btnMonitorHV
            // 
            this.btnMonitorHV.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.btnMonitorHV.Enabled = false;
            this.btnMonitorHV.Location = new System.Drawing.Point(158, 479);
            this.btnMonitorHV.Name = "btnMonitorHV";
            this.btnMonitorHV.Size = new System.Drawing.Size(76, 20);
            this.btnMonitorHV.TabIndex = 10;
            this.btnMonitorHV.Text = "Monitor";
            this.btnMonitorHV.UseVisualStyleBackColor = true;
            this.btnMonitorHV.Click += new System.EventHandler(this.btnMonitorHV_Click);
            // 
            // label27
            // 
            this.label27.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.label27.AutoSize = true;
            this.label27.Location = new System.Drawing.Point(56, 483);
            this.label27.Name = "label27";
            this.label27.Size = new System.Drawing.Size(97, 13);
            this.label27.TabIndex = 9;
            this.label27.Text = "Monitor Timer (sec)";
            // 
            // textBoxMonitorTimer
            // 
            this.textBoxMonitorTimer.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.textBoxMonitorTimer.Enabled = false;
            this.textBoxMonitorTimer.Location = new System.Drawing.Point(13, 480);
            this.textBoxMonitorTimer.Name = "textBoxMonitorTimer";
            this.textBoxMonitorTimer.Size = new System.Drawing.Size(37, 20);
            this.textBoxMonitorTimer.TabIndex = 8;
            this.textBoxMonitorTimer.TextChanged += new System.EventHandler(this.textBoxMonitorTimer_TextChanged);
            // 
            // btnSwitchToAuto
            // 
            this.btnSwitchToAuto.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.btnSwitchToAuto.Enabled = false;
            this.btnSwitchToAuto.Location = new System.Drawing.Point(240, 455);
            this.btnSwitchToAuto.Name = "btnSwitchToAuto";
            this.btnSwitchToAuto.Size = new System.Drawing.Size(102, 20);
            this.btnSwitchToAuto.TabIndex = 7;
            this.btnSwitchToAuto.Text = "Switch to Auto";
            this.btnSwitchToAuto.UseVisualStyleBackColor = true;
            this.btnSwitchToAuto.Click += new System.EventHandler(this.btnSwitchToAuto_Click);
            // 
            // textBoxADCThreshold
            // 
            this.textBoxADCThreshold.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.textBoxADCThreshold.Enabled = false;
            this.textBoxADCThreshold.Location = new System.Drawing.Point(13, 455);
            this.textBoxADCThreshold.Name = "textBoxADCThreshold";
            this.textBoxADCThreshold.Size = new System.Drawing.Size(68, 20);
            this.textBoxADCThreshold.TabIndex = 6;
            // 
            // label2
            // 
            this.label2.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(87, 458);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(65, 13);
            this.label2.TabIndex = 5;
            this.label2.Text = "ADC Counts";
            // 
            // btnReadHV
            // 
            this.btnReadHV.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.btnReadHV.Enabled = false;
            this.btnReadHV.Location = new System.Drawing.Point(158, 455);
            this.btnReadHV.Name = "btnReadHV";
            this.btnReadHV.Size = new System.Drawing.Size(76, 20);
            this.btnReadHV.TabIndex = 3;
            this.btnReadHV.Text = "Read";
            this.btnReadHV.UseVisualStyleBackColor = true;
            this.btnReadHV.Click += new System.EventHandler(this.btnReadHV_Click);
            // 
            // tabLIBox
            // 
            this.tabLIBox.Controls.Add(this.btn_LIBoxAdvancedGUI);
            this.tabLIBox.Controls.Add(this.groupBoxLIBox_LICommands);
            this.tabLIBox.Controls.Add(this.groupBoxLIBox_RS232Commands);
            this.tabLIBox.Controls.Add(this.groupBoxLIBox_RS232Settings);
            this.tabLIBox.Location = new System.Drawing.Point(4, 22);
            this.tabLIBox.Name = "tabLIBox";
            this.tabLIBox.Size = new System.Drawing.Size(899, 502);
            this.tabLIBox.TabIndex = 9;
            this.tabLIBox.Text = "LI Box";
            this.tabLIBox.UseVisualStyleBackColor = true;
            // 
            // btn_LIBoxAdvancedGUI
            // 
            this.btn_LIBoxAdvancedGUI.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxAdvancedGUI.Location = new System.Drawing.Point(238, 14);
            this.btn_LIBoxAdvancedGUI.Name = "btn_LIBoxAdvancedGUI";
            this.btn_LIBoxAdvancedGUI.Size = new System.Drawing.Size(120, 20);
            this.btn_LIBoxAdvancedGUI.TabIndex = 77;
            this.btn_LIBoxAdvancedGUI.Text = "Show Advanced GUI";
            this.btn_LIBoxAdvancedGUI.UseVisualStyleBackColor = false;
            this.btn_LIBoxAdvancedGUI.Click += new System.EventHandler(this.btn_LIBoxAdvancedGUI_Click);
            // 
            // groupBoxLIBox_LICommands
            // 
            this.groupBoxLIBox_LICommands.Controls.Add(this.groupBoxLIBox_LICommandsHardcoded);
            this.groupBoxLIBox_LICommands.Controls.Add(this.btn_LIBoxIsActive);
            this.groupBoxLIBox_LICommands.Controls.Add(this.cmb_LIBoxLEDPulseWidth);
            this.groupBoxLIBox_LICommands.Controls.Add(this.cmb_LIBoxLEDSlot);
            this.groupBoxLIBox_LICommands.Controls.Add(this.btn_LIBoxSendFile);
            this.groupBoxLIBox_LICommands.Controls.Add(this.richTextBoxLIBox);
            this.groupBoxLIBox_LICommands.Controls.Add(this.txt_LIBoxLEDTriggerRate);
            this.groupBoxLIBox_LICommands.Controls.Add(this.btn_LIBoxLEDTriggerRate);
            this.groupBoxLIBox_LICommands.Controls.Add(this.txt_LIBoxLEDPulseHeight);
            this.groupBoxLIBox_LICommands.Controls.Add(this.btn_LIBoxLEDPulseHeight);
            this.groupBoxLIBox_LICommands.Controls.Add(this.btn_LIBoxTriggerExternal);
            this.groupBoxLIBox_LICommands.Controls.Add(this.btn_LIBoxTriggerInternal);
            this.groupBoxLIBox_LICommands.Controls.Add(this.btn_LIBoxLEDPulseWidth);
            this.groupBoxLIBox_LICommands.Controls.Add(this.btn_LIBoxLEDSlot);
            this.groupBoxLIBox_LICommands.Controls.Add(this.btn_LIBoxInitBox);
            this.groupBoxLIBox_LICommands.Location = new System.Drawing.Point(3, 37);
            this.groupBoxLIBox_LICommands.Name = "groupBoxLIBox_LICommands";
            this.groupBoxLIBox_LICommands.Size = new System.Drawing.Size(381, 204);
            this.groupBoxLIBox_LICommands.TabIndex = 76;
            this.groupBoxLIBox_LICommands.TabStop = false;
            this.groupBoxLIBox_LICommands.Text = "LI Commands (hex values)";
            // 
            // groupBoxLIBox_LICommandsHardcoded
            // 
            this.groupBoxLIBox_LICommandsHardcoded.Controls.Add(this.btn_LIBoxHardcodedInitALLSlots);
            this.groupBoxLIBox_LICommandsHardcoded.Controls.Add(this.btn_LIBoxHardcoded_X);
            this.groupBoxLIBox_LICommandsHardcoded.Controls.Add(this.btn_LIBoxHardcodedMaxPE);
            this.groupBoxLIBox_LICommandsHardcoded.Controls.Add(this.btn_LIBoxHardcodedOnePE);
            this.groupBoxLIBox_LICommandsHardcoded.Controls.Add(this.btn_LIBoxHardcodedZeroPE);
            this.groupBoxLIBox_LICommandsHardcoded.Controls.Add(this.cmb_LIBoxHardcodedLEDSlot);
            this.groupBoxLIBox_LICommandsHardcoded.Controls.Add(this.btn_LIBoxHardcodedInitLEDSlot);
            this.groupBoxLIBox_LICommandsHardcoded.Location = new System.Drawing.Point(3, 120);
            this.groupBoxLIBox_LICommandsHardcoded.Name = "groupBoxLIBox_LICommandsHardcoded";
            this.groupBoxLIBox_LICommandsHardcoded.Size = new System.Drawing.Size(222, 78);
            this.groupBoxLIBox_LICommandsHardcoded.TabIndex = 92;
            this.groupBoxLIBox_LICommandsHardcoded.TabStop = false;
            this.groupBoxLIBox_LICommandsHardcoded.Text = "LI Commands Hardcoded";
            // 
            // btn_LIBoxHardcodedInitALLSlots
            // 
            this.btn_LIBoxHardcodedInitALLSlots.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxHardcodedInitALLSlots.Location = new System.Drawing.Point(129, 17);
            this.btn_LIBoxHardcodedInitALLSlots.Name = "btn_LIBoxHardcodedInitALLSlots";
            this.btn_LIBoxHardcodedInitALLSlots.Size = new System.Drawing.Size(91, 20);
            this.btn_LIBoxHardcodedInitALLSlots.TabIndex = 99;
            this.btn_LIBoxHardcodedInitALLSlots.Text = "Init ALL Slots";
            this.btn_LIBoxHardcodedInitALLSlots.UseVisualStyleBackColor = false;
            this.btn_LIBoxHardcodedInitALLSlots.Click += new System.EventHandler(this.btn_LIBoxHardcodedInitALLSlots_Click);
            // 
            // btn_LIBoxHardcoded_X
            // 
            this.btn_LIBoxHardcoded_X.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxHardcoded_X.Location = new System.Drawing.Point(6, 58);
            this.btn_LIBoxHardcoded_X.Name = "btn_LIBoxHardcoded_X";
            this.btn_LIBoxHardcoded_X.Size = new System.Drawing.Size(70, 20);
            this.btn_LIBoxHardcoded_X.TabIndex = 98;
            this.btn_LIBoxHardcoded_X.Text = "-X";
            this.btn_LIBoxHardcoded_X.UseVisualStyleBackColor = false;
            this.btn_LIBoxHardcoded_X.Click += new System.EventHandler(this.btn_LIBoxHardcoded_X_Click);
            // 
            // btn_LIBoxHardcodedMaxPE
            // 
            this.btn_LIBoxHardcodedMaxPE.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxHardcodedMaxPE.Location = new System.Drawing.Point(148, 37);
            this.btn_LIBoxHardcodedMaxPE.Name = "btn_LIBoxHardcodedMaxPE";
            this.btn_LIBoxHardcodedMaxPE.Size = new System.Drawing.Size(70, 20);
            this.btn_LIBoxHardcodedMaxPE.TabIndex = 97;
            this.btn_LIBoxHardcodedMaxPE.Text = "Max PE";
            this.btn_LIBoxHardcodedMaxPE.UseVisualStyleBackColor = false;
            this.btn_LIBoxHardcodedMaxPE.Click += new System.EventHandler(this.btn_LIBoxHardcodedMaxPE_Click);
            // 
            // btn_LIBoxHardcodedOnePE
            // 
            this.btn_LIBoxHardcodedOnePE.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxHardcodedOnePE.Location = new System.Drawing.Point(77, 37);
            this.btn_LIBoxHardcodedOnePE.Name = "btn_LIBoxHardcodedOnePE";
            this.btn_LIBoxHardcodedOnePE.Size = new System.Drawing.Size(70, 20);
            this.btn_LIBoxHardcodedOnePE.TabIndex = 96;
            this.btn_LIBoxHardcodedOnePE.Text = "One PE";
            this.btn_LIBoxHardcodedOnePE.UseVisualStyleBackColor = false;
            this.btn_LIBoxHardcodedOnePE.Click += new System.EventHandler(this.btn_LIBoxHardcodedOnePE_Click);
            // 
            // btn_LIBoxHardcodedZeroPE
            // 
            this.btn_LIBoxHardcodedZeroPE.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxHardcodedZeroPE.Location = new System.Drawing.Point(6, 37);
            this.btn_LIBoxHardcodedZeroPE.Name = "btn_LIBoxHardcodedZeroPE";
            this.btn_LIBoxHardcodedZeroPE.Size = new System.Drawing.Size(70, 20);
            this.btn_LIBoxHardcodedZeroPE.TabIndex = 95;
            this.btn_LIBoxHardcodedZeroPE.Text = "Zero PE";
            this.btn_LIBoxHardcodedZeroPE.UseVisualStyleBackColor = false;
            this.btn_LIBoxHardcodedZeroPE.Click += new System.EventHandler(this.btn_LIBoxHardcodedZeroPE_Click);
            // 
            // cmb_LIBoxHardcodedLEDSlot
            // 
            this.cmb_LIBoxHardcodedLEDSlot.AutoCompleteCustomSource.AddRange(new string[] {
            "0",
            "1",
            "2"});
            this.cmb_LIBoxHardcodedLEDSlot.FormattingEnabled = true;
            this.cmb_LIBoxHardcodedLEDSlot.Items.AddRange(new object[] {
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v"});
            this.cmb_LIBoxHardcodedLEDSlot.Location = new System.Drawing.Point(96, 15);
            this.cmb_LIBoxHardcodedLEDSlot.Name = "cmb_LIBoxHardcodedLEDSlot";
            this.cmb_LIBoxHardcodedLEDSlot.Size = new System.Drawing.Size(32, 21);
            this.cmb_LIBoxHardcodedLEDSlot.TabIndex = 94;
            // 
            // btn_LIBoxHardcodedInitLEDSlot
            // 
            this.btn_LIBoxHardcodedInitLEDSlot.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxHardcodedInitLEDSlot.Location = new System.Drawing.Point(6, 17);
            this.btn_LIBoxHardcodedInitLEDSlot.Name = "btn_LIBoxHardcodedInitLEDSlot";
            this.btn_LIBoxHardcodedInitLEDSlot.Size = new System.Drawing.Size(91, 20);
            this.btn_LIBoxHardcodedInitLEDSlot.TabIndex = 93;
            this.btn_LIBoxHardcodedInitLEDSlot.Text = "Init LED Slot";
            this.btn_LIBoxHardcodedInitLEDSlot.UseVisualStyleBackColor = false;
            this.btn_LIBoxHardcodedInitLEDSlot.Click += new System.EventHandler(this.btn_LIBoxHardcodedInitLEDSlot_Click);
            // 
            // btn_LIBoxIsActive
            // 
            this.btn_LIBoxIsActive.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxIsActive.Location = new System.Drawing.Point(132, 57);
            this.btn_LIBoxIsActive.Name = "btn_LIBoxIsActive";
            this.btn_LIBoxIsActive.Size = new System.Drawing.Size(91, 20);
            this.btn_LIBoxIsActive.TabIndex = 91;
            this.btn_LIBoxIsActive.Text = "LI Active Is OFF";
            this.btn_LIBoxIsActive.UseVisualStyleBackColor = false;
            this.btn_LIBoxIsActive.Click += new System.EventHandler(this.btn_LIBoxIsActive_Click);
            // 
            // cmb_LIBoxLEDPulseWidth
            // 
            this.cmb_LIBoxLEDPulseWidth.AutoCompleteCustomSource.AddRange(new string[] {
            "0",
            "1",
            "2"});
            this.cmb_LIBoxLEDPulseWidth.FormattingEnabled = true;
            this.cmb_LIBoxLEDPulseWidth.Items.AddRange(new object[] {
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7"});
            this.cmb_LIBoxLEDPulseWidth.Location = new System.Drawing.Point(96, 57);
            this.cmb_LIBoxLEDPulseWidth.Name = "cmb_LIBoxLEDPulseWidth";
            this.cmb_LIBoxLEDPulseWidth.Size = new System.Drawing.Size(32, 21);
            this.cmb_LIBoxLEDPulseWidth.TabIndex = 90;
            // 
            // cmb_LIBoxLEDSlot
            // 
            this.cmb_LIBoxLEDSlot.AutoCompleteCustomSource.AddRange(new string[] {
            "0",
            "1",
            "2"});
            this.cmb_LIBoxLEDSlot.FormattingEnabled = true;
            this.cmb_LIBoxLEDSlot.Items.AddRange(new object[] {
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v"});
            this.cmb_LIBoxLEDSlot.Location = new System.Drawing.Point(96, 36);
            this.cmb_LIBoxLEDSlot.Name = "cmb_LIBoxLEDSlot";
            this.cmb_LIBoxLEDSlot.Size = new System.Drawing.Size(32, 21);
            this.cmb_LIBoxLEDSlot.TabIndex = 89;
            // 
            // btn_LIBoxSendFile
            // 
            this.btn_LIBoxSendFile.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxSendFile.Location = new System.Drawing.Point(131, 77);
            this.btn_LIBoxSendFile.Name = "btn_LIBoxSendFile";
            this.btn_LIBoxSendFile.Size = new System.Drawing.Size(91, 20);
            this.btn_LIBoxSendFile.TabIndex = 88;
            this.btn_LIBoxSendFile.Text = "Send File";
            this.btn_LIBoxSendFile.UseVisualStyleBackColor = false;
            this.btn_LIBoxSendFile.Click += new System.EventHandler(this.btn_LIBoxSendFile_Click);
            // 
            // richTextBoxLIBox
            // 
            this.richTextBoxLIBox.Location = new System.Drawing.Point(229, 19);
            this.richTextBoxLIBox.Name = "richTextBoxLIBox";
            this.richTextBoxLIBox.Size = new System.Drawing.Size(146, 179);
            this.richTextBoxLIBox.TabIndex = 1;
            this.richTextBoxLIBox.Text = "";
            // 
            // txt_LIBoxLEDTriggerRate
            // 
            this.txt_LIBoxLEDTriggerRate.Location = new System.Drawing.Point(96, 98);
            this.txt_LIBoxLEDTriggerRate.Name = "txt_LIBoxLEDTriggerRate";
            this.txt_LIBoxLEDTriggerRate.Size = new System.Drawing.Size(32, 20);
            this.txt_LIBoxLEDTriggerRate.TabIndex = 87;
            this.txt_LIBoxLEDTriggerRate.Text = "FFFF";
            // 
            // btn_LIBoxLEDTriggerRate
            // 
            this.btn_LIBoxLEDTriggerRate.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxLEDTriggerRate.Location = new System.Drawing.Point(6, 97);
            this.btn_LIBoxLEDTriggerRate.Name = "btn_LIBoxLEDTriggerRate";
            this.btn_LIBoxLEDTriggerRate.Size = new System.Drawing.Size(91, 20);
            this.btn_LIBoxLEDTriggerRate.TabIndex = 86;
            this.btn_LIBoxLEDTriggerRate.Text = "Trigger Rate";
            this.btn_LIBoxLEDTriggerRate.UseVisualStyleBackColor = false;
            this.btn_LIBoxLEDTriggerRate.Click += new System.EventHandler(this.btn_LIBoxLEDTriggerRate_Click);
            // 
            // txt_LIBoxLEDPulseHeight
            // 
            this.txt_LIBoxLEDPulseHeight.Location = new System.Drawing.Point(96, 78);
            this.txt_LIBoxLEDPulseHeight.Name = "txt_LIBoxLEDPulseHeight";
            this.txt_LIBoxLEDPulseHeight.Size = new System.Drawing.Size(32, 20);
            this.txt_LIBoxLEDPulseHeight.TabIndex = 85;
            this.txt_LIBoxLEDPulseHeight.Text = "3FF";
            // 
            // btn_LIBoxLEDPulseHeight
            // 
            this.btn_LIBoxLEDPulseHeight.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxLEDPulseHeight.Location = new System.Drawing.Point(6, 77);
            this.btn_LIBoxLEDPulseHeight.Name = "btn_LIBoxLEDPulseHeight";
            this.btn_LIBoxLEDPulseHeight.Size = new System.Drawing.Size(91, 20);
            this.btn_LIBoxLEDPulseHeight.TabIndex = 84;
            this.btn_LIBoxLEDPulseHeight.Text = "Pulse Height";
            this.btn_LIBoxLEDPulseHeight.UseVisualStyleBackColor = false;
            this.btn_LIBoxLEDPulseHeight.Click += new System.EventHandler(this.btn_LIBoxLEDPulseHeight_Click);
            // 
            // btn_LIBoxTriggerExternal
            // 
            this.btn_LIBoxTriggerExternal.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxTriggerExternal.Location = new System.Drawing.Point(132, 37);
            this.btn_LIBoxTriggerExternal.Name = "btn_LIBoxTriggerExternal";
            this.btn_LIBoxTriggerExternal.Size = new System.Drawing.Size(91, 20);
            this.btn_LIBoxTriggerExternal.TabIndex = 83;
            this.btn_LIBoxTriggerExternal.Text = "Trigger External";
            this.btn_LIBoxTriggerExternal.UseVisualStyleBackColor = false;
            this.btn_LIBoxTriggerExternal.Click += new System.EventHandler(this.btn_LIBoxTriggerExternal_Click);
            // 
            // btn_LIBoxTriggerInternal
            // 
            this.btn_LIBoxTriggerInternal.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxTriggerInternal.Location = new System.Drawing.Point(132, 17);
            this.btn_LIBoxTriggerInternal.Name = "btn_LIBoxTriggerInternal";
            this.btn_LIBoxTriggerInternal.Size = new System.Drawing.Size(91, 20);
            this.btn_LIBoxTriggerInternal.TabIndex = 82;
            this.btn_LIBoxTriggerInternal.Text = "Trigger Internal";
            this.btn_LIBoxTriggerInternal.UseVisualStyleBackColor = false;
            this.btn_LIBoxTriggerInternal.Click += new System.EventHandler(this.btn_LIBoxTriggerInternal_Click);
            // 
            // btn_LIBoxLEDPulseWidth
            // 
            this.btn_LIBoxLEDPulseWidth.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxLEDPulseWidth.Location = new System.Drawing.Point(6, 57);
            this.btn_LIBoxLEDPulseWidth.Name = "btn_LIBoxLEDPulseWidth";
            this.btn_LIBoxLEDPulseWidth.Size = new System.Drawing.Size(91, 20);
            this.btn_LIBoxLEDPulseWidth.TabIndex = 80;
            this.btn_LIBoxLEDPulseWidth.Text = "Pulse Width";
            this.btn_LIBoxLEDPulseWidth.UseVisualStyleBackColor = false;
            this.btn_LIBoxLEDPulseWidth.Click += new System.EventHandler(this.btn_LIBoxLEDPulseWidth_Click);
            // 
            // btn_LIBoxLEDSlot
            // 
            this.btn_LIBoxLEDSlot.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxLEDSlot.Location = new System.Drawing.Point(6, 37);
            this.btn_LIBoxLEDSlot.Name = "btn_LIBoxLEDSlot";
            this.btn_LIBoxLEDSlot.Size = new System.Drawing.Size(91, 20);
            this.btn_LIBoxLEDSlot.TabIndex = 78;
            this.btn_LIBoxLEDSlot.Text = "Select LED Slot";
            this.btn_LIBoxLEDSlot.UseVisualStyleBackColor = false;
            this.btn_LIBoxLEDSlot.Click += new System.EventHandler(this.btn_LIBoxLEDSlot_Click);
            // 
            // btn_LIBoxInitBox
            // 
            this.btn_LIBoxInitBox.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxInitBox.Location = new System.Drawing.Point(6, 17);
            this.btn_LIBoxInitBox.Name = "btn_LIBoxInitBox";
            this.btn_LIBoxInitBox.Size = new System.Drawing.Size(91, 20);
            this.btn_LIBoxInitBox.TabIndex = 77;
            this.btn_LIBoxInitBox.Text = "Initialize LI Box";
            this.btn_LIBoxInitBox.UseVisualStyleBackColor = false;
            this.btn_LIBoxInitBox.Click += new System.EventHandler(this.btn_LIBoxInitBox_Click);
            // 
            // groupBoxLIBox_RS232Commands
            // 
            this.groupBoxLIBox_RS232Commands.Controls.Add(this.btn_LIBoxClearRX);
            this.groupBoxLIBox_RS232Commands.Controls.Add(this.btn_LIBoxClearTX);
            this.groupBoxLIBox_RS232Commands.Controls.Add(this.richTextBoxLIWrite);
            this.groupBoxLIBox_RS232Commands.Controls.Add(this.btn_LIBoxRead);
            this.groupBoxLIBox_RS232Commands.Controls.Add(this.richTextBoxLIRead);
            this.groupBoxLIBox_RS232Commands.Controls.Add(this.btn_LIBoxWrite);
            this.groupBoxLIBox_RS232Commands.Location = new System.Drawing.Point(3, 247);
            this.groupBoxLIBox_RS232Commands.Name = "groupBoxLIBox_RS232Commands";
            this.groupBoxLIBox_RS232Commands.Size = new System.Drawing.Size(381, 122);
            this.groupBoxLIBox_RS232Commands.TabIndex = 75;
            this.groupBoxLIBox_RS232Commands.TabStop = false;
            this.groupBoxLIBox_RS232Commands.Text = "RS-232 ASCII message";
            this.groupBoxLIBox_RS232Commands.Visible = false;
            // 
            // btn_LIBoxClearRX
            // 
            this.btn_LIBoxClearRX.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxClearRX.Location = new System.Drawing.Point(6, 91);
            this.btn_LIBoxClearRX.Name = "btn_LIBoxClearRX";
            this.btn_LIBoxClearRX.Size = new System.Drawing.Size(63, 20);
            this.btn_LIBoxClearRX.TabIndex = 76;
            this.btn_LIBoxClearRX.Text = "Clear RX";
            this.btn_LIBoxClearRX.UseVisualStyleBackColor = false;
            this.btn_LIBoxClearRX.Click += new System.EventHandler(this.btn_LIBoxClearRX_Click);
            // 
            // btn_LIBoxClearTX
            // 
            this.btn_LIBoxClearTX.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxClearTX.Location = new System.Drawing.Point(6, 38);
            this.btn_LIBoxClearTX.Name = "btn_LIBoxClearTX";
            this.btn_LIBoxClearTX.Size = new System.Drawing.Size(63, 20);
            this.btn_LIBoxClearTX.TabIndex = 75;
            this.btn_LIBoxClearTX.Text = "Clear TX";
            this.btn_LIBoxClearTX.UseVisualStyleBackColor = false;
            this.btn_LIBoxClearTX.Click += new System.EventHandler(this.btn_LIBoxClearTX_Click);
            // 
            // richTextBoxLIWrite
            // 
            this.richTextBoxLIWrite.Location = new System.Drawing.Point(70, 14);
            this.richTextBoxLIWrite.Name = "richTextBoxLIWrite";
            this.richTextBoxLIWrite.Size = new System.Drawing.Size(305, 50);
            this.richTextBoxLIWrite.TabIndex = 73;
            this.richTextBoxLIWrite.Text = "";
            // 
            // btn_LIBoxRead
            // 
            this.btn_LIBoxRead.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxRead.Location = new System.Drawing.Point(6, 71);
            this.btn_LIBoxRead.Name = "btn_LIBoxRead";
            this.btn_LIBoxRead.Size = new System.Drawing.Size(63, 20);
            this.btn_LIBoxRead.TabIndex = 71;
            this.btn_LIBoxRead.Text = "Read";
            this.btn_LIBoxRead.UseVisualStyleBackColor = false;
            this.btn_LIBoxRead.Click += new System.EventHandler(this.btn_LIBoxRead_Click);
            // 
            // richTextBoxLIRead
            // 
            this.richTextBoxLIRead.Location = new System.Drawing.Point(70, 66);
            this.richTextBoxLIRead.Name = "richTextBoxLIRead";
            this.richTextBoxLIRead.Size = new System.Drawing.Size(305, 50);
            this.richTextBoxLIRead.TabIndex = 74;
            this.richTextBoxLIRead.Text = "";
            // 
            // btn_LIBoxWrite
            // 
            this.btn_LIBoxWrite.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxWrite.Location = new System.Drawing.Point(6, 18);
            this.btn_LIBoxWrite.Name = "btn_LIBoxWrite";
            this.btn_LIBoxWrite.Size = new System.Drawing.Size(63, 20);
            this.btn_LIBoxWrite.TabIndex = 70;
            this.btn_LIBoxWrite.Text = "Write";
            this.btn_LIBoxWrite.UseVisualStyleBackColor = false;
            this.btn_LIBoxWrite.Click += new System.EventHandler(this.btn_LIBoxWrite_Click);
            // 
            // groupBoxLIBox_RS232Settings
            // 
            this.groupBoxLIBox_RS232Settings.Controls.Add(this.txt_LIBoxReadTimeout);
            this.groupBoxLIBox_RS232Settings.Controls.Add(this.txt_LIBoxWriteTimeout);
            this.groupBoxLIBox_RS232Settings.Controls.Add(this.label37);
            this.groupBoxLIBox_RS232Settings.Controls.Add(this.cmb_LIBoxHandshake);
            this.groupBoxLIBox_RS232Settings.Controls.Add(this.cmb_LIBoxStopBits);
            this.groupBoxLIBox_RS232Settings.Controls.Add(this.cmb_LIBoxDataBits);
            this.groupBoxLIBox_RS232Settings.Controls.Add(this.cmb_LIBoxParity);
            this.groupBoxLIBox_RS232Settings.Controls.Add(this.cmb_LIBoxBaudRate);
            this.groupBoxLIBox_RS232Settings.Controls.Add(this.cmb_LIBoxPortName);
            this.groupBoxLIBox_RS232Settings.Controls.Add(this.btn_LIBoxFindSerialPorts);
            this.groupBoxLIBox_RS232Settings.Controls.Add(this.btn_LIBoxConfigureSerialPort);
            this.groupBoxLIBox_RS232Settings.Location = new System.Drawing.Point(6, 375);
            this.groupBoxLIBox_RS232Settings.Name = "groupBoxLIBox_RS232Settings";
            this.groupBoxLIBox_RS232Settings.Size = new System.Drawing.Size(381, 73);
            this.groupBoxLIBox_RS232Settings.TabIndex = 60;
            this.groupBoxLIBox_RS232Settings.TabStop = false;
            this.groupBoxLIBox_RS232Settings.Text = "RS-232 Settings";
            this.groupBoxLIBox_RS232Settings.Visible = false;
            // 
            // txt_LIBoxReadTimeout
            // 
            this.txt_LIBoxReadTimeout.Location = new System.Drawing.Point(297, 19);
            this.txt_LIBoxReadTimeout.Name = "txt_LIBoxReadTimeout";
            this.txt_LIBoxReadTimeout.Size = new System.Drawing.Size(38, 20);
            this.txt_LIBoxReadTimeout.TabIndex = 69;
            this.txt_LIBoxReadTimeout.Text = "100";
            // 
            // txt_LIBoxWriteTimeout
            // 
            this.txt_LIBoxWriteTimeout.Location = new System.Drawing.Point(336, 19);
            this.txt_LIBoxWriteTimeout.Name = "txt_LIBoxWriteTimeout";
            this.txt_LIBoxWriteTimeout.Size = new System.Drawing.Size(38, 20);
            this.txt_LIBoxWriteTimeout.TabIndex = 68;
            this.txt_LIBoxWriteTimeout.Text = "100";
            // 
            // label37
            // 
            this.label37.BackColor = System.Drawing.Color.Coral;
            this.label37.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label37.Location = new System.Drawing.Point(196, 20);
            this.label37.Name = "label37";
            this.label37.Size = new System.Drawing.Size(100, 18);
            this.label37.TabIndex = 65;
            this.label37.Text = "Timeout(ms): R,W";
            // 
            // cmb_LIBoxHandshake
            // 
            this.cmb_LIBoxHandshake.FormattingEnabled = true;
            this.cmb_LIBoxHandshake.Location = new System.Drawing.Point(286, 44);
            this.cmb_LIBoxHandshake.Name = "cmb_LIBoxHandshake";
            this.cmb_LIBoxHandshake.Size = new System.Drawing.Size(89, 21);
            this.cmb_LIBoxHandshake.TabIndex = 64;
            // 
            // cmb_LIBoxStopBits
            // 
            this.cmb_LIBoxStopBits.FormattingEnabled = true;
            this.cmb_LIBoxStopBits.Location = new System.Drawing.Point(228, 44);
            this.cmb_LIBoxStopBits.Name = "cmb_LIBoxStopBits";
            this.cmb_LIBoxStopBits.Size = new System.Drawing.Size(52, 21);
            this.cmb_LIBoxStopBits.TabIndex = 63;
            // 
            // cmb_LIBoxDataBits
            // 
            this.cmb_LIBoxDataBits.FormattingEnabled = true;
            this.cmb_LIBoxDataBits.Location = new System.Drawing.Point(189, 44);
            this.cmb_LIBoxDataBits.Name = "cmb_LIBoxDataBits";
            this.cmb_LIBoxDataBits.Size = new System.Drawing.Size(33, 21);
            this.cmb_LIBoxDataBits.TabIndex = 62;
            // 
            // cmb_LIBoxParity
            // 
            this.cmb_LIBoxParity.FormattingEnabled = true;
            this.cmb_LIBoxParity.Location = new System.Drawing.Point(132, 44);
            this.cmb_LIBoxParity.Name = "cmb_LIBoxParity";
            this.cmb_LIBoxParity.Size = new System.Drawing.Size(51, 21);
            this.cmb_LIBoxParity.TabIndex = 61;
            // 
            // cmb_LIBoxBaudRate
            // 
            this.cmb_LIBoxBaudRate.FormattingEnabled = true;
            this.cmb_LIBoxBaudRate.Location = new System.Drawing.Point(69, 44);
            this.cmb_LIBoxBaudRate.Name = "cmb_LIBoxBaudRate";
            this.cmb_LIBoxBaudRate.Size = new System.Drawing.Size(57, 21);
            this.cmb_LIBoxBaudRate.TabIndex = 60;
            // 
            // cmb_LIBoxPortName
            // 
            this.cmb_LIBoxPortName.FormattingEnabled = true;
            this.cmb_LIBoxPortName.Location = new System.Drawing.Point(6, 44);
            this.cmb_LIBoxPortName.Name = "cmb_LIBoxPortName";
            this.cmb_LIBoxPortName.Size = new System.Drawing.Size(57, 21);
            this.cmb_LIBoxPortName.TabIndex = 59;
            // 
            // btn_LIBoxFindSerialPorts
            // 
            this.btn_LIBoxFindSerialPorts.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxFindSerialPorts.Location = new System.Drawing.Point(6, 19);
            this.btn_LIBoxFindSerialPorts.Name = "btn_LIBoxFindSerialPorts";
            this.btn_LIBoxFindSerialPorts.Size = new System.Drawing.Size(91, 20);
            this.btn_LIBoxFindSerialPorts.TabIndex = 57;
            this.btn_LIBoxFindSerialPorts.Text = "Find Serial Ports";
            this.btn_LIBoxFindSerialPorts.UseVisualStyleBackColor = false;
            this.btn_LIBoxFindSerialPorts.Click += new System.EventHandler(this.btn_LIBoxFindSerialPorts_Click);
            // 
            // btn_LIBoxConfigureSerialPort
            // 
            this.btn_LIBoxConfigureSerialPort.BackColor = System.Drawing.Color.Coral;
            this.btn_LIBoxConfigureSerialPort.Location = new System.Drawing.Point(98, 19);
            this.btn_LIBoxConfigureSerialPort.Name = "btn_LIBoxConfigureSerialPort";
            this.btn_LIBoxConfigureSerialPort.Size = new System.Drawing.Size(97, 20);
            this.btn_LIBoxConfigureSerialPort.TabIndex = 58;
            this.btn_LIBoxConfigureSerialPort.TabStop = false;
            this.btn_LIBoxConfigureSerialPort.Text = "Config Serial Port";
            this.btn_LIBoxConfigureSerialPort.UseVisualStyleBackColor = false;
            this.btn_LIBoxConfigureSerialPort.Click += new System.EventHandler(this.btn_LIBoxConfigureSerialPort_Click);
            // 
            // tabV1720
            // 
            this.tabV1720.Controls.Add(this.btn_V1720ReadAllRegisters);
            this.tabV1720.Controls.Add(this.chk_V1720PrintEventStat);
            this.tabV1720.Controls.Add(this.chk_V1720PrintEventData);
            this.tabV1720.Controls.Add(this.txt_V1720TakeNEvents);
            this.tabV1720.Controls.Add(this.btn_V1720TakeNEvents);
            this.tabV1720.Controls.Add(this.richTextBoxV1720);
            this.tabV1720.Controls.Add(this.lblV1720_V1720ID);
            this.tabV1720.Controls.Add(this.label72);
            this.tabV1720.Controls.Add(this.btn_V1720AdvancedGUI);
            this.tabV1720.Controls.Add(this.btn_V1720LoadConfigFile);
            this.tabV1720.Location = new System.Drawing.Point(4, 22);
            this.tabV1720.Name = "tabV1720";
            this.tabV1720.Size = new System.Drawing.Size(899, 502);
            this.tabV1720.TabIndex = 11;
            this.tabV1720.Text = "V1720";
            this.tabV1720.UseVisualStyleBackColor = true;
            // 
            // btn_V1720ReadAllRegisters
            // 
            this.btn_V1720ReadAllRegisters.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.btn_V1720ReadAllRegisters.BackColor = System.Drawing.Color.Coral;
            this.btn_V1720ReadAllRegisters.Location = new System.Drawing.Point(16, 477);
            this.btn_V1720ReadAllRegisters.Name = "btn_V1720ReadAllRegisters";
            this.btn_V1720ReadAllRegisters.Size = new System.Drawing.Size(106, 20);
            this.btn_V1720ReadAllRegisters.TabIndex = 104;
            this.btn_V1720ReadAllRegisters.Text = "Read All Registers";
            this.btn_V1720ReadAllRegisters.UseVisualStyleBackColor = false;
            this.btn_V1720ReadAllRegisters.Visible = false;
            this.btn_V1720ReadAllRegisters.Click += new System.EventHandler(this.btn_V1720ReadAllRegisters_Click);
            // 
            // chk_V1720PrintEventStat
            // 
            this.chk_V1720PrintEventStat.AutoSize = true;
            this.chk_V1720PrintEventStat.Location = new System.Drawing.Point(292, 39);
            this.chk_V1720PrintEventStat.Name = "chk_V1720PrintEventStat";
            this.chk_V1720PrintEventStat.Size = new System.Drawing.Size(73, 17);
            this.chk_V1720PrintEventStat.TabIndex = 103;
            this.chk_V1720PrintEventStat.Text = "event stat";
            this.chk_V1720PrintEventStat.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.chk_V1720PrintEventStat.UseVisualStyleBackColor = true;
            // 
            // chk_V1720PrintEventData
            // 
            this.chk_V1720PrintEventData.AutoSize = true;
            this.chk_V1720PrintEventData.Location = new System.Drawing.Point(201, 39);
            this.chk_V1720PrintEventData.Name = "chk_V1720PrintEventData";
            this.chk_V1720PrintEventData.Size = new System.Drawing.Size(77, 17);
            this.chk_V1720PrintEventData.TabIndex = 102;
            this.chk_V1720PrintEventData.Text = "event data";
            this.chk_V1720PrintEventData.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.chk_V1720PrintEventData.UseVisualStyleBackColor = true;
            // 
            // txt_V1720TakeNEvents
            // 
            this.txt_V1720TakeNEvents.Location = new System.Drawing.Point(145, 37);
            this.txt_V1720TakeNEvents.Name = "txt_V1720TakeNEvents";
            this.txt_V1720TakeNEvents.Size = new System.Drawing.Size(45, 20);
            this.txt_V1720TakeNEvents.TabIndex = 97;
            this.txt_V1720TakeNEvents.Text = "10";
            // 
            // btn_V1720TakeNEvents
            // 
            this.btn_V1720TakeNEvents.BackColor = System.Drawing.Color.Coral;
            this.btn_V1720TakeNEvents.Location = new System.Drawing.Point(16, 37);
            this.btn_V1720TakeNEvents.Name = "btn_V1720TakeNEvents";
            this.btn_V1720TakeNEvents.Size = new System.Drawing.Size(130, 20);
            this.btn_V1720TakeNEvents.TabIndex = 96;
            this.btn_V1720TakeNEvents.Text = "START Take N Events";
            this.btn_V1720TakeNEvents.UseVisualStyleBackColor = false;
            this.btn_V1720TakeNEvents.Click += new System.EventHandler(this.btn_V1720TakeNEvents_Click);
            // 
            // richTextBoxV1720
            // 
            this.richTextBoxV1720.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.richTextBoxV1720.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(204)));
            this.richTextBoxV1720.Location = new System.Drawing.Point(1, 63);
            this.richTextBoxV1720.Name = "richTextBoxV1720";
            this.richTextBoxV1720.Size = new System.Drawing.Size(455, 398);
            this.richTextBoxV1720.TabIndex = 95;
            this.richTextBoxV1720.Text = "";
            // 
            // lblV1720_V1720ID
            // 
            this.lblV1720_V1720ID.BackColor = System.Drawing.Color.White;
            this.lblV1720_V1720ID.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblV1720_V1720ID.Location = new System.Drawing.Point(54, 16);
            this.lblV1720_V1720ID.Name = "lblV1720_V1720ID";
            this.lblV1720_V1720ID.Size = new System.Drawing.Size(30, 18);
            this.lblV1720_V1720ID.TabIndex = 94;
            // 
            // label72
            // 
            this.label72.BackColor = System.Drawing.Color.Coral;
            this.label72.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label72.Location = new System.Drawing.Point(16, 16);
            this.label72.Name = "label72";
            this.label72.Size = new System.Drawing.Size(40, 18);
            this.label72.TabIndex = 93;
            this.label72.Text = "V1720";
            // 
            // btn_V1720AdvancedGUI
            // 
            this.btn_V1720AdvancedGUI.BackColor = System.Drawing.Color.Coral;
            this.btn_V1720AdvancedGUI.Location = new System.Drawing.Point(248, 16);
            this.btn_V1720AdvancedGUI.Name = "btn_V1720AdvancedGUI";
            this.btn_V1720AdvancedGUI.Size = new System.Drawing.Size(120, 20);
            this.btn_V1720AdvancedGUI.TabIndex = 92;
            this.btn_V1720AdvancedGUI.Text = "Show Advanced GUI";
            this.btn_V1720AdvancedGUI.UseVisualStyleBackColor = false;
            this.btn_V1720AdvancedGUI.Click += new System.EventHandler(this.btn_V1720AdvancedGUI_Click);
            // 
            // btn_V1720LoadConfigFile
            // 
            this.btn_V1720LoadConfigFile.BackColor = System.Drawing.Color.Coral;
            this.btn_V1720LoadConfigFile.Location = new System.Drawing.Point(87, 16);
            this.btn_V1720LoadConfigFile.Name = "btn_V1720LoadConfigFile";
            this.btn_V1720LoadConfigFile.Size = new System.Drawing.Size(155, 20);
            this.btn_V1720LoadConfigFile.TabIndex = 91;
            this.btn_V1720LoadConfigFile.Text = "Load Configuration File";
            this.btn_V1720LoadConfigFile.UseVisualStyleBackColor = false;
            this.btn_V1720LoadConfigFile.Click += new System.EventHandler(this.btn_V1720LoadConfigFile_Click);
            // 
            // errMain
            // 
            this.errMain.ContainerControl = this;
            // 
            // treeView1
            // 
            this.treeView1.AccessibleDescription = "";
            this.treeView1.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)));
            this.treeView1.ContextMenuStrip = this.contextMenuStrip1;
            this.treeView1.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.treeView1.Location = new System.Drawing.Point(5, 27);
            this.treeView1.Name = "treeView1";
            this.treeView1.ShowNodeToolTips = true;
            this.treeView1.Size = new System.Drawing.Size(200, 528);
            this.treeView1.TabIndex = 1;
            this.treeView1.AfterSelect += new System.Windows.Forms.TreeViewEventHandler(this.treeView1_AfterSelect);
            // 
            // contextMenuStrip1
            // 
            this.contextMenuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.toolStripMenuItemUpdateStatusString,
            this.toolStripSeparator2});
            this.contextMenuStrip1.Name = "contextMenuStrip1";
            this.contextMenuStrip1.Size = new System.Drawing.Size(182, 32);
            // 
            // toolStripMenuItemUpdateStatusString
            // 
            this.toolStripMenuItemUpdateStatusString.Name = "toolStripMenuItemUpdateStatusString";
            this.toolStripMenuItemUpdateStatusString.Size = new System.Drawing.Size(181, 22);
            this.toolStripMenuItemUpdateStatusString.Text = "Update Status String";
            this.toolStripMenuItemUpdateStatusString.Click += new System.EventHandler(this.toolStripMenuItemUpdateStatusString_Click);
            // 
            // toolStripSeparator2
            // 
            this.toolStripSeparator2.Name = "toolStripSeparator2";
            this.toolStripSeparator2.Size = new System.Drawing.Size(178, 6);
            // 
            // menuStrip1
            // 
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.toolStripMenuItemFile,
            this.showToolStripMenuItem,
            this.actionsToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(1130, 24);
            this.menuStrip1.TabIndex = 2;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // toolStripMenuItemFile
            // 
            this.toolStripMenuItemFile.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.loadHardwareToolStripMenuItem,
            this.loadConfigXmlToolStripMenuItem,
            this.saveConfigXmlToolStripMenuItem,
            this.writeXmlToHardwareToolStripMenuItem});
            this.toolStripMenuItemFile.Name = "toolStripMenuItemFile";
            this.toolStripMenuItemFile.ShowShortcutKeys = false;
            this.toolStripMenuItemFile.Size = new System.Drawing.Size(37, 20);
            this.toolStripMenuItemFile.Text = "File";
            // 
            // loadHardwareToolStripMenuItem
            // 
            this.loadHardwareToolStripMenuItem.Name = "loadHardwareToolStripMenuItem";
            this.loadHardwareToolStripMenuItem.Size = new System.Drawing.Size(197, 22);
            this.loadHardwareToolStripMenuItem.Text = "Load Hardware";
            this.loadHardwareToolStripMenuItem.Click += new System.EventHandler(this.loadHardwareToolStripMenuItem_Click);
            // 
            // loadConfigXmlToolStripMenuItem
            // 
            this.loadConfigXmlToolStripMenuItem.Name = "loadConfigXmlToolStripMenuItem";
            this.loadConfigXmlToolStripMenuItem.Size = new System.Drawing.Size(197, 22);
            this.loadConfigXmlToolStripMenuItem.Text = "Load Config Xml";
            this.loadConfigXmlToolStripMenuItem.Click += new System.EventHandler(this.loadConfigXmlToolStripMenuItem_Click);
            // 
            // saveConfigXmlToolStripMenuItem
            // 
            this.saveConfigXmlToolStripMenuItem.Enabled = false;
            this.saveConfigXmlToolStripMenuItem.Name = "saveConfigXmlToolStripMenuItem";
            this.saveConfigXmlToolStripMenuItem.Size = new System.Drawing.Size(197, 22);
            this.saveConfigXmlToolStripMenuItem.Text = "Save Config Xml";
            this.saveConfigXmlToolStripMenuItem.Click += new System.EventHandler(this.saveConfigXmlToolStripMenuItem_Click);
            // 
            // writeXmlToHardwareToolStripMenuItem
            // 
            this.writeXmlToHardwareToolStripMenuItem.Enabled = false;
            this.writeXmlToHardwareToolStripMenuItem.Name = "writeXmlToHardwareToolStripMenuItem";
            this.writeXmlToHardwareToolStripMenuItem.Size = new System.Drawing.Size(197, 22);
            this.writeXmlToHardwareToolStripMenuItem.Text = "Write Xml To Hardware";
            this.writeXmlToHardwareToolStripMenuItem.Click += new System.EventHandler(this.writeXmlToHardwareToolStripMenuItem_Click);
            // 
            // showToolStripMenuItem
            // 
            this.showToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.expandAllToolStripMenuItem,
            this.collapseAllToolStripMenuItem,
            this.toolStripSeparator1,
            this.redPathsToolStripMenuItem,
            this.bluePathsToolStripMenuItem,
            this.greenPathsToolStripMenuItem});
            this.showToolStripMenuItem.Name = "showToolStripMenuItem";
            this.showToolStripMenuItem.Size = new System.Drawing.Size(48, 20);
            this.showToolStripMenuItem.Text = "Show";
            // 
            // expandAllToolStripMenuItem
            // 
            this.expandAllToolStripMenuItem.Name = "expandAllToolStripMenuItem";
            this.expandAllToolStripMenuItem.Size = new System.Drawing.Size(137, 22);
            this.expandAllToolStripMenuItem.Text = "Expand All";
            this.expandAllToolStripMenuItem.Click += new System.EventHandler(this.expandAllToolStripMenuItem_Click);
            // 
            // collapseAllToolStripMenuItem
            // 
            this.collapseAllToolStripMenuItem.Name = "collapseAllToolStripMenuItem";
            this.collapseAllToolStripMenuItem.Size = new System.Drawing.Size(137, 22);
            this.collapseAllToolStripMenuItem.Text = "Collapse All";
            this.collapseAllToolStripMenuItem.Click += new System.EventHandler(this.collapseAllToolStripMenuItem_Click);
            // 
            // toolStripSeparator1
            // 
            this.toolStripSeparator1.Name = "toolStripSeparator1";
            this.toolStripSeparator1.Size = new System.Drawing.Size(134, 6);
            // 
            // redPathsToolStripMenuItem
            // 
            this.redPathsToolStripMenuItem.Name = "redPathsToolStripMenuItem";
            this.redPathsToolStripMenuItem.Size = new System.Drawing.Size(137, 22);
            this.redPathsToolStripMenuItem.Text = "Red paths";
            this.redPathsToolStripMenuItem.Visible = false;
            this.redPathsToolStripMenuItem.Click += new System.EventHandler(this.redPathsToolStripMenuItem_Click);
            // 
            // bluePathsToolStripMenuItem
            // 
            this.bluePathsToolStripMenuItem.Name = "bluePathsToolStripMenuItem";
            this.bluePathsToolStripMenuItem.Size = new System.Drawing.Size(137, 22);
            this.bluePathsToolStripMenuItem.Text = "Blue paths";
            this.bluePathsToolStripMenuItem.Visible = false;
            this.bluePathsToolStripMenuItem.Click += new System.EventHandler(this.bluePathsToolStripMenuItem_Click);
            // 
            // greenPathsToolStripMenuItem
            // 
            this.greenPathsToolStripMenuItem.Name = "greenPathsToolStripMenuItem";
            this.greenPathsToolStripMenuItem.Size = new System.Drawing.Size(137, 22);
            this.greenPathsToolStripMenuItem.Text = "Green paths";
            this.greenPathsToolStripMenuItem.Visible = false;
            this.greenPathsToolStripMenuItem.Click += new System.EventHandler(this.greenPathsToolStripMenuItem_Click);
            // 
            // actionsToolStripMenuItem
            // 
            this.actionsToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.readVoltagesToolStripMenuItem,
            this.zeroHVAllToolStripMenuItem,
            this.monitorVoltagesToolStripMenuItem,
            this.lightInjectionToolStripMenuItem});
            this.actionsToolStripMenuItem.Name = "actionsToolStripMenuItem";
            this.actionsToolStripMenuItem.Size = new System.Drawing.Size(59, 20);
            this.actionsToolStripMenuItem.Text = "Actions";
            // 
            // readVoltagesToolStripMenuItem
            // 
            this.readVoltagesToolStripMenuItem.Enabled = false;
            this.readVoltagesToolStripMenuItem.Name = "readVoltagesToolStripMenuItem";
            this.readVoltagesToolStripMenuItem.Size = new System.Drawing.Size(165, 22);
            this.readVoltagesToolStripMenuItem.Text = "Read Voltages";
            this.readVoltagesToolStripMenuItem.Click += new System.EventHandler(this.readVoltagesToolStripMenuItem_Click);
            // 
            // zeroHVAllToolStripMenuItem
            // 
            this.zeroHVAllToolStripMenuItem.Enabled = false;
            this.zeroHVAllToolStripMenuItem.Name = "zeroHVAllToolStripMenuItem";
            this.zeroHVAllToolStripMenuItem.Size = new System.Drawing.Size(165, 22);
            this.zeroHVAllToolStripMenuItem.Text = "Zero HV All";
            this.zeroHVAllToolStripMenuItem.Click += new System.EventHandler(this.zeroHVAllToolStripMenuItem_Click);
            // 
            // monitorVoltagesToolStripMenuItem
            // 
            this.monitorVoltagesToolStripMenuItem.Enabled = false;
            this.monitorVoltagesToolStripMenuItem.Name = "monitorVoltagesToolStripMenuItem";
            this.monitorVoltagesToolStripMenuItem.Size = new System.Drawing.Size(165, 22);
            this.monitorVoltagesToolStripMenuItem.Text = "Monitor Voltages";
            this.monitorVoltagesToolStripMenuItem.Click += new System.EventHandler(this.monitorVoltagesToolStripMenuItem_Click);
            // 
            // lightInjectionToolStripMenuItem
            // 
            this.lightInjectionToolStripMenuItem.Name = "lightInjectionToolStripMenuItem";
            this.lightInjectionToolStripMenuItem.Size = new System.Drawing.Size(165, 22);
            this.lightInjectionToolStripMenuItem.Text = "Light Injection";
            this.lightInjectionToolStripMenuItem.Click += new System.EventHandler(this.lightInjectionToolStripMenuItem_Click);
            // 
            // statusStrip1
            // 
            this.statusStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.prgStatus,
            this.lblStatus});
            this.statusStrip1.Location = new System.Drawing.Point(0, 558);
            this.statusStrip1.Name = "statusStrip1";
            this.statusStrip1.Size = new System.Drawing.Size(1130, 22);
            this.statusStrip1.TabIndex = 3;
            this.statusStrip1.Text = "statusStrip1";
            // 
            // prgStatus
            // 
            this.prgStatus.Name = "prgStatus";
            this.prgStatus.Size = new System.Drawing.Size(100, 16);
            // 
            // lblStatus
            // 
            this.lblStatus.Name = "lblStatus";
            this.lblStatus.Size = new System.Drawing.Size(1013, 17);
            this.lblStatus.Spring = true;
            this.lblStatus.Text = "lblStatus";
            // 
            // backgroundWorker1
            // 
            this.backgroundWorker1.WorkerReportsProgress = true;
            this.backgroundWorker1.WorkerSupportsCancellation = true;
            this.backgroundWorker1.DoWork += new System.ComponentModel.DoWorkEventHandler(this.backgroundWorker1_DoWork);
            this.backgroundWorker1.RunWorkerCompleted += new System.ComponentModel.RunWorkerCompletedEventHandler(this.backgroundWorker1_RunWorkerCompleted);
            this.backgroundWorker1.ProgressChanged += new System.ComponentModel.ProgressChangedEventHandler(this.backgroundWorker1_ProgressChanged);
            // 
            // timerMonitorHV
            // 
            this.timerMonitorHV.Tick += new System.EventHandler(this.timerMonitorHV_Tick);
            // 
            // frmSlowControl
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1130, 580);
            this.Controls.Add(this.statusStrip1);
            this.Controls.Add(this.treeView1);
            this.Controls.Add(this.menuStrip1);
            this.Controls.Add(this.tabControl1);
            this.MainMenuStrip = this.menuStrip1;
            this.Name = "frmSlowControl";
            this.Text = "Minerva Slow Control";
            this.Load += new System.EventHandler(this.frmSlowControl_Load);
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.frmSlowControl_FormClosing);
            this.tabControl1.ResumeLayout(false);
            this.tabDescription.ResumeLayout(false);
            this.tabVME.ResumeLayout(false);
            this.groupBoxVME_WriteRead.ResumeLayout(false);
            this.groupBoxVME_WriteRead.PerformLayout();
            this.tabCRIM.ResumeLayout(false);
            this.tabControlCRIMModules.ResumeLayout(false);
            this.tabCRIMTimingModule.ResumeLayout(false);
            this.tabCRIMTimingModule.PerformLayout();
            this.tabCRIMDAQModule.ResumeLayout(false);
            this.groupBoxCRIM_MiscRegisters.ResumeLayout(false);
            this.groupBoxCRIM_DAQModeRegister.ResumeLayout(false);
            this.groupBoxCRIM_DAQModeRegister.PerformLayout();
            this.groupBoxCRIM_DPMRegister.ResumeLayout(false);
            this.groupBoxCRIM_StatusRegister.ResumeLayout(false);
            this.groupBoxCRIM_FrameRegisters.ResumeLayout(false);
            this.groupBoxCRIM_FrameRegisters.PerformLayout();
            this.tabCRIMInterrupterModule.ResumeLayout(false);
            this.groupBoxCRIM_Interrupter.ResumeLayout(false);
            this.groupBoxCRIM_Interrupter.PerformLayout();
            this.tabCRIMFELoopQuery.ResumeLayout(false);
            this.tabCRIMFELoopQuery.PerformLayout();
            this.tabCROC.ResumeLayout(false);
            this.groupBoxCROC_FEBGateDelays.ResumeLayout(false);
            this.groupBoxCROC_FEBGateDelays.PerformLayout();
            this.groupBoxCROC_LoopDelay.ResumeLayout(false);
            this.groupBoxCROC_FastCommand.ResumeLayout(false);
            this.groupBoxCROC_ResetTPMaskReg.ResumeLayout(false);
            this.groupBoxCROC_TimingSetup.ResumeLayout(false);
            this.groupBoxCROC_TimingSetup.PerformLayout();
            this.groupBoxCROC_FLASH.ResumeLayout(false);
            this.tabCH.ResumeLayout(false);
            this.groupBoxCH_DEBUG.ResumeLayout(false);
            this.groupBoxCH_DEBUG.PerformLayout();
            this.groupBoxCH_Frame.ResumeLayout(false);
            this.groupBoxCH_Frame.PerformLayout();
            this.groupBoxCH_StatusRegister.ResumeLayout(false);
            this.groupBoxCH_FLASH.ResumeLayout(false);
            this.groupBoxCH_DPM.ResumeLayout(false);
            this.tabFPGARegs.ResumeLayout(false);
            this.tabTRIPRegs.ResumeLayout(false);
            this.tabFLASHPages.ResumeLayout(false);
            this.tabReadHV.ResumeLayout(false);
            this.tabReadHV.PerformLayout();
            this.tabLIBox.ResumeLayout(false);
            this.groupBoxLIBox_LICommands.ResumeLayout(false);
            this.groupBoxLIBox_LICommands.PerformLayout();
            this.groupBoxLIBox_LICommandsHardcoded.ResumeLayout(false);
            this.groupBoxLIBox_RS232Commands.ResumeLayout(false);
            this.groupBoxLIBox_RS232Settings.ResumeLayout(false);
            this.groupBoxLIBox_RS232Settings.PerformLayout();
            this.tabV1720.ResumeLayout(false);
            this.tabV1720.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.errMain)).EndInit();
            this.contextMenuStrip1.ResumeLayout(false);
            this.menuStrip1.ResumeLayout(false);
            this.menuStrip1.PerformLayout();
            this.statusStrip1.ResumeLayout(false);
            this.statusStrip1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage tabTRIPRegs;
        private System.Windows.Forms.ErrorProvider errMain;
        private System.Windows.Forms.TreeView treeView1;
        private System.Windows.Forms.MenuStrip menuStrip1;
        private System.Windows.Forms.ToolStripMenuItem toolStripMenuItemFile;
        private System.Windows.Forms.ToolStripMenuItem loadConfigXmlToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem saveConfigXmlToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem loadHardwareToolStripMenuItem;
        private System.Windows.Forms.TabPage tabFLASHPages;
        private System.Windows.Forms.TabPage tabDescription;
        private System.Windows.Forms.RichTextBox richTextBoxDescription;
        private System.Windows.Forms.ToolStripMenuItem showToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem greenPathsToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem bluePathsToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem redPathsToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem expandAllToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem collapseAllToolStripMenuItem;
        private System.Windows.Forms.ToolStripSeparator toolStripSeparator1;
        private System.Windows.Forms.ContextMenuStrip contextMenuStrip1;
        private System.Windows.Forms.ToolStripMenuItem toolStripMenuItemUpdateStatusString;
        private System.Windows.Forms.ToolStripSeparator toolStripSeparator2;
        private System.Windows.Forms.StatusStrip statusStrip1;
        private System.Windows.Forms.ToolStripProgressBar prgStatus;
        private System.Windows.Forms.ToolStripStatusLabel lblStatus;
        private System.Windows.Forms.TabPage tabCRIM;
        private System.Windows.Forms.TabPage tabCROC;
        private System.Windows.Forms.TabPage tabCH;
        private System.Windows.Forms.TabPage tabFE;
        private MinervaUserControls.TripDevRegControl tripDevRegControl1;
        private System.Windows.Forms.Button btn_TRIPAdvancedGUI;
        private System.Windows.Forms.Label lblTRIP_CROCID;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label lblTRIP_CHID;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.Label lblTRIP_FEID;
        private System.Windows.Forms.Button btn_TRIPRegRead;
        private System.Windows.Forms.Button btn_TRIPRegWrite;
        private System.Windows.Forms.Label label9;
        private System.Windows.Forms.TabPage tabFPGARegs;
        private System.Windows.Forms.Button btn_FPGAAdvancedGUI;
        private System.Windows.Forms.Label lblFPGA_CROCID;
        private System.Windows.Forms.Label label7;
        private System.Windows.Forms.Label lblFPGA_CHID;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.Label lblFPGA_FEID;
        private System.Windows.Forms.Button btn_FPGARegRead;
        private System.Windows.Forms.Button btn_FPGARegWrite;
        private System.Windows.Forms.Label label1;
        private MinervaUserControls.FPGADevRegControl fpgaDevRegControl1;
        private System.Windows.Forms.TabPage tabReadHV;
        private System.Windows.Forms.Button btnReadHV;
        private System.ComponentModel.BackgroundWorker backgroundWorker1;
        private System.Windows.Forms.ToolStripMenuItem actionsToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem readVoltagesToolStripMenuItem;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.ToolStripMenuItem zeroHVAllToolStripMenuItem;
        private System.Windows.Forms.TextBox textBoxADCThreshold;
        private System.Windows.Forms.ComboBox cmb_TripID;
        private System.Windows.Forms.Button btnSwitchToAuto;
        private System.Windows.Forms.Button btn_AllFEsFPGARegWrite;
        private System.Windows.Forms.Button btn_AllFEsTRIPRegWrite;
        private System.Windows.Forms.Button btn_FLASHReadSPIToFile;
        private System.Windows.Forms.Label lblFLASH_CROCID;
        private System.Windows.Forms.Label label8;
        private System.Windows.Forms.Label lblFLASH_CHID;
        private System.Windows.Forms.Label label11;
        private System.Windows.Forms.Label lblFLASH_FEID;
        private System.Windows.Forms.Label label13;
        private System.Windows.Forms.Button btn_FLASHAdvancedGUI;
        private System.Windows.Forms.Button btn_FLASHWriteFileToSPI;
        private System.Windows.Forms.Button btn_CHAdvancedGUI;
        private System.Windows.Forms.Label lblCH_CROCID;
        private System.Windows.Forms.Label label10;
        private System.Windows.Forms.Label lblCH_CHID;
        private System.Windows.Forms.Label label14;
        private System.Windows.Forms.Label label16;
        private System.Windows.Forms.Button btn_CHWriteFileToSPI;
        private System.Windows.Forms.Button btn_CHReBootFEs;
        private System.Windows.Forms.Button btn_CROCAdvancedGUI;
        private System.Windows.Forms.Label lblCROC_CROCID;
        private System.Windows.Forms.Label label12;
        private System.Windows.Forms.Label label15;
        private System.Windows.Forms.Label label17;
        private System.Windows.Forms.Label label18;
        private System.Windows.Forms.Label label19;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.Button btn_CROCReBootFEs;
        private System.Windows.Forms.Button btn_CROCWriteFileToSPI;
        private System.Windows.Forms.Label lblCH_StatusValue;
        private System.Windows.Forms.Button btn_CHStatusRegRead;
        private System.Windows.Forms.Label lblCH_StatMsgSent;
        private System.Windows.Forms.Label label22;
        private System.Windows.Forms.Label lblCH_StatRFPresent;
        private System.Windows.Forms.Label label38;
        private System.Windows.Forms.Label lblCH_StatDPMFull;
        private System.Windows.Forms.Label label40;
        private System.Windows.Forms.Label lblCH_StatFIFOFull;
        private System.Windows.Forms.Label label42;
        private System.Windows.Forms.Label lblCH_StatFIFONotEmpty;
        private System.Windows.Forms.Label label44;
        private System.Windows.Forms.Label lblCH_StatPLL1LOCK;
        private System.Windows.Forms.Label label30;
        private System.Windows.Forms.Label lblCH_StatPLL0LOCK;
        private System.Windows.Forms.Label label32;
        private System.Windows.Forms.Label lblCH_StatDeserializerLOCK;
        private System.Windows.Forms.Label label34;
        private System.Windows.Forms.Label lblCH_StatSerializerSYNC;
        private System.Windows.Forms.Label label36;
        private System.Windows.Forms.Label lblCH_StatTimeoutError;
        private System.Windows.Forms.Label label28;
        private System.Windows.Forms.Label lblCH_StatCRCError;
        private System.Windows.Forms.Label label26;
        private System.Windows.Forms.Label lblCH_StatMsgReceived;
        private System.Windows.Forms.Label label24;
        private System.Windows.Forms.Button btn_CHStatusRegClear;
        private System.Windows.Forms.Button btn_CHDPMPointerReset;
        private System.Windows.Forms.Label lblCH_DPMPointerValue;
        private System.Windows.Forms.Button btn_CHDPMPointerRead;
        private System.Windows.Forms.GroupBox groupBoxCH_DPM;
        private System.Windows.Forms.GroupBox groupBoxCH_StatusRegister;
        private System.Windows.Forms.GroupBox groupBoxCH_FLASH;
        private System.Windows.Forms.GroupBox groupBoxCROC_FLASH;
        private System.Windows.Forms.Label lblCH_StatUnusedBit11;
        private System.Windows.Forms.Label label25;
        private System.Windows.Forms.Label lblCH_StatUnusedBit7;
        private System.Windows.Forms.Label label21;
        private System.Windows.Forms.Label lblCH_StatUnusedBit15;
        private System.Windows.Forms.Label label33;
        private System.Windows.Forms.Label lblCH_StatUnusedBit14;
        private System.Windows.Forms.Label label29;
        private System.Windows.Forms.GroupBox groupBoxCH_Frame;
        private System.Windows.Forms.Button btn_CHDPMRead;
        private System.Windows.Forms.Button btn_CHSendMessage;
        private System.Windows.Forms.Button btn_CHFIFOAppendMessage;
        private System.Windows.Forms.TextBox txt_CHDPMReadLength;
        private System.Windows.Forms.TextBox txt_CHFIFORegWrite;
        private System.Windows.Forms.RichTextBox rtb_CHDPMRead;
        private System.Windows.Forms.Button btn_CHFIFOWriteMessage;
        private System.Windows.Forms.GroupBox groupBoxCROC_TimingSetup;
        private System.Windows.Forms.TextBox txt_CROCTimingSetupTPDelay;
        private System.Windows.Forms.ComboBox cmb_CROCTimingSetupTPDelay;
        private System.Windows.Forms.ComboBox cmb_CROCTimingSetupClock;
        private System.Windows.Forms.Button btn_CROCTimingSetupRead;
        private System.Windows.Forms.Label label20;
        private System.Windows.Forms.Label lbl_CROCTimingSetupRead;
        private System.Windows.Forms.GroupBox groupBoxCROC_ResetTPMaskReg;
        private System.Windows.Forms.CheckBox chk_CROCResetCh1;
        private System.Windows.Forms.CheckBox chk_CROCTPulseCh1;
        private System.Windows.Forms.CheckBox chk_CROCTPulseCh4;
        private System.Windows.Forms.CheckBox chk_CROCResetCh4;
        private System.Windows.Forms.CheckBox chk_CROCTPulseCh3;
        private System.Windows.Forms.CheckBox chk_CROCResetCh3;
        private System.Windows.Forms.CheckBox chk_CROCTPulseCh2;
        private System.Windows.Forms.CheckBox chk_CROCResetCh2;
        private System.Windows.Forms.Button btn_CROCResetTPWrite;
        private System.Windows.Forms.Label lbl_CROCResetTPRead;
        private System.Windows.Forms.Button btn_CROCResetTPRead;
        private System.Windows.Forms.Button btn_CROCTPSend;
        private System.Windows.Forms.Button btn_CROCResetSend;
        private System.Windows.Forms.GroupBox groupBoxCROC_FastCommand;
        private System.Windows.Forms.ComboBox cmb_CROCFastCommand;
        private System.Windows.Forms.Button btn_CROCFastCommand;
        private System.Windows.Forms.GroupBox groupBoxCROC_LoopDelay;
        private System.Windows.Forms.Button btn_CROCLoopDelayRead;
        private System.Windows.Forms.Label label23;
        private System.Windows.Forms.Label lbl_CROCLoopDelayCh4;
        private System.Windows.Forms.Label label43;
        private System.Windows.Forms.Label lbl_CROCLoopDelayCh3;
        private System.Windows.Forms.Label label39;
        private System.Windows.Forms.Label lbl_CROCLoopDelayCh2;
        private System.Windows.Forms.Label label35;
        private System.Windows.Forms.Label lbl_CROCLoopDelayCh1;
        private System.Windows.Forms.Label label27;
        private System.Windows.Forms.TextBox textBoxMonitorTimer;
        private System.Windows.Forms.ToolStripMenuItem monitorVoltagesToolStripMenuItem;
        private System.Windows.Forms.Button btnMonitorHV;
        private System.Windows.Forms.Timer timerMonitorHV;
        private System.Windows.Forms.TabPage tabLIBox;
        private System.Windows.Forms.ToolStripMenuItem lightInjectionToolStripMenuItem;
        private System.Windows.Forms.RichTextBox richTextBoxLIBox;
        private System.Windows.Forms.GroupBox groupBoxLIBox_RS232Settings;
        private System.Windows.Forms.Button btn_LIBoxFindSerialPorts;
        private System.Windows.Forms.Button btn_LIBoxConfigureSerialPort;
        private System.Windows.Forms.ComboBox cmb_LIBoxDataBits;
        private System.Windows.Forms.ComboBox cmb_LIBoxParity;
        private System.Windows.Forms.ComboBox cmb_LIBoxBaudRate;
        private System.Windows.Forms.ComboBox cmb_LIBoxPortName;
        private System.Windows.Forms.ComboBox cmb_LIBoxHandshake;
        private System.Windows.Forms.ComboBox cmb_LIBoxStopBits;
        private System.Windows.Forms.TextBox txt_LIBoxReadTimeout;
        private System.Windows.Forms.TextBox txt_LIBoxWriteTimeout;
        private System.Windows.Forms.Label label37;
        private System.Windows.Forms.Button btn_LIBoxRead;
        private System.Windows.Forms.Button btn_LIBoxWrite;
        private System.Windows.Forms.RichTextBox richTextBoxLIRead;
        private System.Windows.Forms.RichTextBox richTextBoxLIWrite;
        private System.Windows.Forms.GroupBox groupBoxLIBox_RS232Commands;
        private System.Windows.Forms.Button btn_LIBoxClearRX;
        private System.Windows.Forms.Button btn_LIBoxClearTX;
        private System.Windows.Forms.GroupBox groupBoxLIBox_LICommands;
        private System.Windows.Forms.Button btn_LIBoxInitBox;
        private System.Windows.Forms.Button btn_LIBoxLEDSlot;
        private System.Windows.Forms.Button btn_LIBoxLEDPulseWidth;
        private System.Windows.Forms.Button btn_LIBoxTriggerExternal;
        private System.Windows.Forms.Button btn_LIBoxTriggerInternal;
        private System.Windows.Forms.TextBox txt_LIBoxLEDPulseHeight;
        private System.Windows.Forms.Button btn_LIBoxLEDPulseHeight;
        private System.Windows.Forms.TextBox txt_LIBoxLEDTriggerRate;
        private System.Windows.Forms.Button btn_LIBoxLEDTriggerRate;
        private System.Windows.Forms.Button btn_LIBoxSendFile;
        private System.Windows.Forms.ComboBox cmb_LIBoxLEDSlot;
        private System.Windows.Forms.ComboBox cmb_LIBoxLEDPulseWidth;
        private System.Windows.Forms.Button btn_LIBoxIsActive;
        private System.Windows.Forms.Button btn_LIBoxAdvancedGUI;
        private System.Windows.Forms.GroupBox groupBoxLIBox_LICommandsHardcoded;
        private System.Windows.Forms.Button btn_LIBoxHardcodedMaxPE;
        private System.Windows.Forms.Button btn_LIBoxHardcodedOnePE;
        private System.Windows.Forms.Button btn_LIBoxHardcodedZeroPE;
        private System.Windows.Forms.ComboBox cmb_LIBoxHardcodedLEDSlot;
        private System.Windows.Forms.Button btn_LIBoxHardcodedInitLEDSlot;
        private System.Windows.Forms.Button btn_LIBoxHardcoded_X;
        private System.Windows.Forms.Button btn_LIBoxHardcodedInitALLSlots;
        private System.Windows.Forms.GroupBox groupBoxCROC_FEBGateDelays;
        private System.Windows.Forms.Button btn_CROCReportGateAlignments;
        private System.Windows.Forms.Label label41;
        private System.Windows.Forms.TextBox txt_CROCGateDelayLoopN;
        private System.Windows.Forms.TextBox txt_CROCGateDelayLoopGateStartValue;
        private System.Windows.Forms.Label label45;
        private System.Windows.Forms.TextBox txt_CROCGateDelayLoopLoadTimerValue;
        private System.Windows.Forms.Label label31;
        private System.Windows.Forms.TextBox txt_CROCGateDelayLoopChannel;
        private System.Windows.Forms.Button btn_CROCLoopDelayClear;
        private System.Windows.Forms.Button btn_CROCReportGateAlignmentsAllCROCsAndChains;
        private System.Windows.Forms.Button btn_CRIMReportGateAlignmentsAllCROCs;
        private System.Windows.Forms.Label lblCRIM_CRIMID;
        private System.Windows.Forms.Label label47;
        private System.Windows.Forms.Button btn_CRIMAdvancedGUI;
        private System.Windows.Forms.ComboBox cmb_CRIMTimingMode;
        private System.Windows.Forms.ComboBox cmb_CRIMTimingFrequency;
        private System.Windows.Forms.Button btn_CRIMTimingModeRead;
        private System.Windows.Forms.Button btn_CRIMTimingModeWrite;
        private System.Windows.Forms.Label label50;
        private System.Windows.Forms.Label label49;
        private System.Windows.Forms.Button btn_CRIMTimingFrequencyRead;
        private System.Windows.Forms.Button btn_CRIMTimingFrequencyWrite;
        private System.Windows.Forms.Button btn_CRIMTimingTCALBRead;
        private System.Windows.Forms.Button btn_CRIMTimingTCALBWrite;
        private System.Windows.Forms.Button btn_CRIMTimingGateWidthRead;
        private System.Windows.Forms.Button btn_CRIMTimingGateWidthWrite;
        private System.Windows.Forms.Label label51;
        private System.Windows.Forms.Label label52;
        private System.Windows.Forms.TextBox txt_CRIMTimingTCALB;
        private System.Windows.Forms.TextBox txt_CRIMTimingGateWidth;
        private System.Windows.Forms.Button btn_CRIMTimingSendTCALB;
        private System.Windows.Forms.Button btn_CRIMTimingSendStartGate;
        private System.Windows.Forms.Button btn_CRIMTimingSendStopGate;
        private System.Windows.Forms.Button btn_CRIMTimingSendTrigger;
        private System.Windows.Forms.Button btn_CRIMTimingSS_CNTRST;
        private System.Windows.Forms.Button btn_CRIMTimingSS_CNTRST_SGATE_TCALB;
        private System.Windows.Forms.TabControl tabControlCRIMModules;
        private System.Windows.Forms.TabPage tabCRIMTimingModule;
        private System.Windows.Forms.TabPage tabCRIMDAQModule;
        private System.Windows.Forms.TabPage tabCRIMInterrupterModule;
        private System.Windows.Forms.Label lbl_CRIMDAQReadTimingCommandRegister;
        private System.Windows.Forms.GroupBox groupBoxCRIM_DAQModeRegister;
        private System.Windows.Forms.CheckBox chk_CRIMDAQModeRegisterSendEn;
        private System.Windows.Forms.CheckBox chk_CRIMDAQModeRegisterFETriggEn;
        private System.Windows.Forms.Button btn_CRIMDAQModeRegisterRead;
        private System.Windows.Forms.Button btn_CRIMDAQModeRegisterWrite;
        private System.Windows.Forms.CheckBox chk_CRIMDAQModeRegisterCRCEn;
        private System.Windows.Forms.CheckBox chk_CRIMDAQModeRegisterRetransmitEn;
        private System.Windows.Forms.Button btn_CRIMDAQResetFIFORegister;
        private System.Windows.Forms.GroupBox groupBoxCRIM_DPMRegister;
        private System.Windows.Forms.Button btn_CRIMDAQDPMRegisterResetPointer;
        private System.Windows.Forms.Button btn_CRIMDAQDPMRegisterReadPointer;
        private System.Windows.Forms.Label lbl_CRIMDAQDPMRegisterReadPointer;
        private System.Windows.Forms.Button btn_CRIMDAQReadTimingCommandRegister;
        private System.Windows.Forms.GroupBox groupBoxCRIM_StatusRegister;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusEncodedCmdRcv;
        private System.Windows.Forms.Label label59;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusFERebootRcv;
        private System.Windows.Forms.Label label61;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusUnusedBit11;
        private System.Windows.Forms.Label label63;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusUnusedBit7;
        private System.Windows.Forms.Label label65;
        private System.Windows.Forms.Button btn_CRIMDAQStatusRegisterClear;
        private System.Windows.Forms.Button btn_CRIMDAQStatusRegisterRead;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusRegisterRead;
        private System.Windows.Forms.Label label67;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusMsgSent;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusRFPresent;
        private System.Windows.Forms.Label label70;
        private System.Windows.Forms.Label label71;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusMsgRcv;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusDPMFull;
        private System.Windows.Forms.Label label74;
        private System.Windows.Forms.Label label75;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusCRCErr;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusFIFOFull;
        private System.Windows.Forms.Label label78;
        private System.Windows.Forms.Label label79;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusTimeoutErr;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusFIFONotEmpty;
        private System.Windows.Forms.Label label82;
        private System.Windows.Forms.Label label83;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusSerializerSync;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusTestPulseRcv;
        private System.Windows.Forms.Label label88;
        private System.Windows.Forms.Label label87;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusDeserializerLock;
        private System.Windows.Forms.Label lbl_CRIMDAQStatusPLLLock;
        private System.Windows.Forms.Label label90;
        private System.Windows.Forms.GroupBox groupBoxCRIM_FrameRegisters;
        private System.Windows.Forms.Button btn_CRIMDAQFrameFIFORegisterWrite;
        private System.Windows.Forms.RichTextBox rtb_CRIMDAQFrameReadDPMBytes;
        private System.Windows.Forms.TextBox txt_CRIMDAQFrameReadDPMBytes;
        private System.Windows.Forms.TextBox txt_CRIMDAQFrameFIFORegisterAppendMessage;
        private System.Windows.Forms.Button btn_CRIMDAQFrameReadDPMBytes;
        private System.Windows.Forms.Button btn_CRIMDAQFrameSendRegister;
        private System.Windows.Forms.Button btn_CRIMDAQFrameFIFORegisterAppendMessage;
        private System.Windows.Forms.GroupBox groupBoxCRIM_MiscRegisters;
        private System.Windows.Forms.Label label46;
        private System.Windows.Forms.Label label53;
        private System.Windows.Forms.Button btn_CRIMInterrupterMaskWrite;
        private System.Windows.Forms.Button btn_CRIMInterrupterClearInterrupts;
        private System.Windows.Forms.Button btn_CRIMInterrupterMaskRead;
        private System.Windows.Forms.TextBox txt_CRIMInterrupterVectInp0;
        private System.Windows.Forms.Button btn_CRIMInterrupterStatusWrite;
        private System.Windows.Forms.Button btn_CRIMInterrupterVectInpRead;
        private System.Windows.Forms.Button btn_CRIMInterrupterStatusRead;
        private System.Windows.Forms.Button btn_CRIMInterrupterVectInpWrite;
        private System.Windows.Forms.Label label54;
        private System.Windows.Forms.Label label55;
        private System.Windows.Forms.Button btn_CRIMInterrupterConfigWrite;
        private System.Windows.Forms.TextBox txt_CRIMInterrupterStatus;
        private System.Windows.Forms.TextBox txt_CRIMInterrupterMask;
        private System.Windows.Forms.TextBox txt_CRIMInterrupterVectInp7;
        private System.Windows.Forms.Label label93;
        private System.Windows.Forms.TextBox txt_CRIMInterrupterVectInp6;
        private System.Windows.Forms.Label label94;
        private System.Windows.Forms.TextBox txt_CRIMInterrupterVectInp5;
        private System.Windows.Forms.Label label95;
        private System.Windows.Forms.TextBox txt_CRIMInterrupterVectInp4;
        private System.Windows.Forms.Label label96;
        private System.Windows.Forms.TextBox txt_CRIMInterrupterVectInp3;
        private System.Windows.Forms.Label label58;
        private System.Windows.Forms.TextBox txt_CRIMInterrupterVectInp2;
        private System.Windows.Forms.Label label92;
        private System.Windows.Forms.TextBox txt_CRIMInterrupterVectInp1;
        private System.Windows.Forms.Label label56;
        private System.Windows.Forms.Label label97;
        private System.Windows.Forms.CheckBox chk_CRIMInterrupterGIE;
        private System.Windows.Forms.Button btn_CRIMDAQSendSyncRegister;
        private System.Windows.Forms.TabPage tabVME;
        private System.Windows.Forms.Label lbl_VMEReadData;
        private System.Windows.Forms.TextBox txt_VMEWriteAddress;
        private System.Windows.Forms.TextBox txt_VMEReadAddress;
        private System.Windows.Forms.Button btn_VMEWrite;
        private System.Windows.Forms.Button btn_VMERead;
        private System.Windows.Forms.GroupBox groupBoxVME_WriteRead;
        private System.Windows.Forms.Label label62;
        private System.Windows.Forms.Label label60;
        private System.Windows.Forms.TextBox txt_VMEWriteData;
        private System.Windows.Forms.TabPage tabCRIMFELoopQuery;
        private System.Windows.Forms.Button btn_CRIMFELoopQueryConfigure;
        private System.Windows.Forms.RichTextBox rtb_CRIMFELoopQueryDisplay;
        private System.Windows.Forms.Label label48;
        private System.Windows.Forms.TextBox txt_CRIMFELoopQueryCrocBaseAddr;
        private System.Windows.Forms.Label label57;
        private System.Windows.Forms.TextBox txt_CRIMFELoopQueryMatch;
        private System.Windows.Forms.TextBox txt_CRIMFELoopQueryNTimes;
        private System.Windows.Forms.Button btn_CRIMFELoopQueryDoQuery;
        private System.Windows.Forms.CheckBox chk_CRIMFELoopQueryMatch;
        private System.Windows.Forms.GroupBox groupBoxCRIM_Interrupter;
        private System.Windows.Forms.TextBox txt_CRIMInterrupterLevels;
        private System.Windows.Forms.Button btn_CRIMTimingSeqControlLatchReset;
        private System.Windows.Forms.CheckBox chk_CRIMTimingCNTRSTEnableInINTMode;
        private System.Windows.Forms.Label label64;
        private System.Windows.Forms.Button btn_CRIMTimingTestRegisterRead;
        private System.Windows.Forms.Button btn_CRIMTimingTestRegisterWrite;
        private System.Windows.Forms.Label label66;
        private System.Windows.Forms.TextBox txt_CRIMTimingTestRegister;
        private System.Windows.Forms.Button btn_CRIMInterrupterConfigRead;
        private System.Windows.Forms.Button btn_CRIMTimingGateTimeRead;
        private System.Windows.Forms.Label label68;
        private System.Windows.Forms.Label lbl_CRIMTimingGateTimeRead;
        private System.Windows.Forms.ToolStripMenuItem writeXmlToHardwareToolStripMenuItem;
        private System.Windows.Forms.TabPage tabV1720;
        private System.Windows.Forms.Label lblV1720_V1720ID;
        private System.Windows.Forms.Label label72;
        private System.Windows.Forms.Button btn_V1720AdvancedGUI;
        private System.Windows.Forms.Button btn_V1720LoadConfigFile;
        private System.Windows.Forms.RichTextBox richTextBoxV1720;
        private System.Windows.Forms.TextBox txt_V1720TakeNEvents;
        private System.Windows.Forms.Button btn_V1720TakeNEvents;
        private System.Windows.Forms.CheckBox chk_V1720PrintEventStat;
        private System.Windows.Forms.CheckBox chk_V1720PrintEventData;
        private System.Windows.Forms.Button btn_V1720ReadAllRegisters;
        private System.Windows.Forms.GroupBox groupBoxCH_DEBUG;
        private System.Windows.Forms.Button btn_CHDebugInitializeCROCs;
        private System.Windows.Forms.TextBox txt_CHDebugNTests;
        private System.Windows.Forms.Label label73;
        private System.Windows.Forms.RichTextBox rtb_CHDebug;
        private System.Windows.Forms.Button btn_CHDebugFillDPM;
        private System.Windows.Forms.TextBox txt_CHDebugFillDPMPattern;
        private System.Windows.Forms.TextBox txt_CHDebugFillDPMPRepeat;
        private System.Windows.Forms.Label label76;
        private System.Windows.Forms.Label label69;
        private System.Windows.Forms.TextBox txt_CHDebugFrameIDByte1;
        private System.Windows.Forms.Label label77;
        private System.Windows.Forms.Label label85;
        private System.Windows.Forms.Label label84;
        private System.Windows.Forms.Label label81;
        private System.Windows.Forms.Label label80;
        private System.Windows.Forms.TextBox txt_CHDebugFrameStatusID;
        private System.Windows.Forms.TextBox txt_CHDebugFrameIDByte0;
        private System.Windows.Forms.ComboBox cmb_CHDebugBroadcastCMD;
        private System.Windows.Forms.ComboBox cmb_CHDebugFEID;
        private System.Windows.Forms.ComboBox cmb_CHDebugFunctionID;
        private System.Windows.Forms.ComboBox cmb_CHDebugDeviceID;
        private System.Windows.Forms.ComboBox cmb_CHDebugDirection;
        private System.Windows.Forms.Button btn_CHDebugUpdatePattern;
        private System.Windows.Forms.RichTextBox richTextBoxHVRead;

    }
}
