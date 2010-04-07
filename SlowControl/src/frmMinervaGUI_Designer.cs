namespace MinervaGUI
{
    partial class frmMinervaGUI
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
            this.tabCRIM = new System.Windows.Forms.TabPage();
            this.richTextBoxCrim = new System.Windows.Forms.RichTextBox();
            this.tabCROC = new System.Windows.Forms.TabPage();
            this.richTextBoxCroc = new System.Windows.Forms.RichTextBox();
            this.tabCH = new System.Windows.Forms.TabPage();
            this.tabFE = new System.Windows.Forms.TabPage();
            this.tabFPGARegs = new System.Windows.Forms.TabPage();
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
            this.tripDevRegControl1 = new MinervaUserControls.TripDevRegControl();
            this.btn_TRIPAdvancedGUI = new System.Windows.Forms.Button();
            this.lblTRIP_CROCID = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.lblTRIP_CHID = new System.Windows.Forms.Label();
            this.label6 = new System.Windows.Forms.Label();
            this.lblTRIP_FEID = new System.Windows.Forms.Label();
            this.btn_TRIPRegRead = new System.Windows.Forms.Button();
            this.btn_TRIPRegWrite = new System.Windows.Forms.Button();
            this.label9 = new System.Windows.Forms.Label();
            this.tabFLASH = new System.Windows.Forms.TabPage();
            this.errMain = new System.Windows.Forms.ErrorProvider(this.components);
            this.treeView1 = new System.Windows.Forms.TreeView();
            this.contextMenuStrip1 = new System.Windows.Forms.ContextMenuStrip(this.components);
            this.toolStripMenuItemUpdateStatusString = new System.Windows.Forms.ToolStripMenuItem();
            this.toolStripSeparator2 = new System.Windows.Forms.ToolStripSeparator();
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.toolStripMenuItemFile = new System.Windows.Forms.ToolStripMenuItem();
            this.LoadHardwareToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.loadConfigXmlToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.saveConfigXmlToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.WriteXMLToHardwareToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.showToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.expandAllToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.collapseAllToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.toolStripSeparator1 = new System.Windows.Forms.ToolStripSeparator();
            this.redPathsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.bluePathsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.greenPathsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.statusStrip1 = new System.Windows.Forms.StatusStrip();
            this.prgStatus = new System.Windows.Forms.ToolStripProgressBar();
            this.lblStatus = new System.Windows.Forms.ToolStripStatusLabel();
            this.tabControl1.SuspendLayout();
            this.tabDescription.SuspendLayout();
            this.tabCRIM.SuspendLayout();
            this.tabCROC.SuspendLayout();
            this.tabFPGARegs.SuspendLayout();
            this.tabTRIPRegs.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.errMain)).BeginInit();
            this.contextMenuStrip1.SuspendLayout();
            this.menuStrip1.SuspendLayout();
            this.statusStrip1.SuspendLayout();
            this.SuspendLayout();
            // 
            // tabControl1
            // 
            this.tabControl1.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.tabControl1.Controls.Add(this.tabDescription);
            this.tabControl1.Controls.Add(this.tabCRIM);
            this.tabControl1.Controls.Add(this.tabCROC);
            this.tabControl1.Controls.Add(this.tabCH);
            this.tabControl1.Controls.Add(this.tabFE);
            this.tabControl1.Controls.Add(this.tabFPGARegs);
            this.tabControl1.Controls.Add(this.tabTRIPRegs);
            this.tabControl1.Controls.Add(this.tabFLASH);
            this.tabControl1.Location = new System.Drawing.Point(316, 27);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(395, 461);
            this.tabControl1.TabIndex = 0;
            // 
            // tabDescription
            // 
            this.tabDescription.Controls.Add(this.richTextBoxDescription);
            this.tabDescription.Location = new System.Drawing.Point(4, 22);
            this.tabDescription.Name = "tabDescription";
            this.tabDescription.Padding = new System.Windows.Forms.Padding(3);
            this.tabDescription.Size = new System.Drawing.Size(387, 435);
            this.tabDescription.TabIndex = 3;
            this.tabDescription.Text = "Description";
            this.tabDescription.UseVisualStyleBackColor = true;
            // 
            // richTextBoxDescription
            // 
            this.richTextBoxDescription.BackColor = System.Drawing.SystemColors.InactiveCaptionText;
            this.richTextBoxDescription.Dock = System.Windows.Forms.DockStyle.Fill;
            this.richTextBoxDescription.Location = new System.Drawing.Point(3, 3);
            this.richTextBoxDescription.Name = "richTextBoxDescription";
            this.richTextBoxDescription.Size = new System.Drawing.Size(381, 429);
            this.richTextBoxDescription.TabIndex = 0;
            this.richTextBoxDescription.Text = "";
            // 
            // tabCRIM
            // 
            this.tabCRIM.Controls.Add(this.richTextBoxCrim);
            this.tabCRIM.Location = new System.Drawing.Point(4, 22);
            this.tabCRIM.Name = "tabCRIM";
            this.tabCRIM.Size = new System.Drawing.Size(387, 435);
            this.tabCRIM.TabIndex = 4;
            this.tabCRIM.Text = "CRIM";
            this.tabCRIM.UseVisualStyleBackColor = true;
            // 
            // richTextBoxCrim
            // 
            this.richTextBoxCrim.Location = new System.Drawing.Point(25, 48);
            this.richTextBoxCrim.Name = "richTextBoxCrim";
            this.richTextBoxCrim.Size = new System.Drawing.Size(179, 240);
            this.richTextBoxCrim.TabIndex = 0;
            this.richTextBoxCrim.Text = "";
            // 
            // tabCROC
            // 
            this.tabCROC.Controls.Add(this.richTextBoxCroc);
            this.tabCROC.Location = new System.Drawing.Point(4, 22);
            this.tabCROC.Name = "tabCROC";
            this.tabCROC.Size = new System.Drawing.Size(387, 435);
            this.tabCROC.TabIndex = 5;
            this.tabCROC.Text = "CROC";
            this.tabCROC.UseVisualStyleBackColor = true;
            // 
            // richTextBoxCroc
            // 
            this.richTextBoxCroc.Location = new System.Drawing.Point(16, 42);
            this.richTextBoxCroc.Name = "richTextBoxCroc";
            this.richTextBoxCroc.Size = new System.Drawing.Size(352, 182);
            this.richTextBoxCroc.TabIndex = 2;
            this.richTextBoxCroc.Text = "";
            // 
            // tabCH
            // 
            this.tabCH.Location = new System.Drawing.Point(4, 22);
            this.tabCH.Name = "tabCH";
            this.tabCH.Size = new System.Drawing.Size(387, 435);
            this.tabCH.TabIndex = 6;
            this.tabCH.Text = "CH";
            this.tabCH.UseVisualStyleBackColor = true;
            // 
            // tabFE
            // 
            this.tabFE.Location = new System.Drawing.Point(4, 22);
            this.tabFE.Name = "tabFE";
            this.tabFE.Size = new System.Drawing.Size(387, 435);
            this.tabFE.TabIndex = 7;
            this.tabFE.Text = "FE";
            this.tabFE.UseVisualStyleBackColor = true;
            // 
            // tabFPGARegs
            // 
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
            this.tabFPGARegs.Size = new System.Drawing.Size(387, 435);
            this.tabFPGARegs.TabIndex = 0;
            this.tabFPGARegs.Text = "FPGA Regs";
            this.tabFPGARegs.UseVisualStyleBackColor = true;
            // 
            // btn_FPGAAdvancedGUI
            // 
            this.btn_FPGAAdvancedGUI.BackColor = System.Drawing.Color.Coral;
            this.btn_FPGAAdvancedGUI.Location = new System.Drawing.Point(238, 14);
            this.btn_FPGAAdvancedGUI.Name = "btn_FPGAAdvancedGUI";
            this.btn_FPGAAdvancedGUI.Size = new System.Drawing.Size(103, 20);
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
            this.btn_FPGARegRead.Location = new System.Drawing.Point(286, 40);
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
            this.btn_FPGARegWrite.Location = new System.Drawing.Point(286, 66);
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
            this.fpgaDevRegControl1.RegisterFirmwareVersion = ((uint)(0u));
            this.fpgaDevRegControl1.RegisterGateLength = ((uint)(1024u));
            this.fpgaDevRegControl1.RegisterGateStart = ((uint)(65488u));
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
            this.fpgaDevRegControl1.Size = new System.Drawing.Size(265, 390);
            this.fpgaDevRegControl1.TabIndex = 23;
            // 
            // tabTRIPRegs
            // 
            this.tabTRIPRegs.Controls.Add(this.tripDevRegControl1);
            this.tabTRIPRegs.Controls.Add(this.btn_TRIPAdvancedGUI);
            this.tabTRIPRegs.Controls.Add(this.lblTRIP_CROCID);
            this.tabTRIPRegs.Controls.Add(this.label3);
            this.tabTRIPRegs.Controls.Add(this.lblTRIP_CHID);
            this.tabTRIPRegs.Controls.Add(this.label6);
            this.tabTRIPRegs.Controls.Add(this.lblTRIP_FEID);
            this.tabTRIPRegs.Controls.Add(this.btn_TRIPRegRead);
            this.tabTRIPRegs.Controls.Add(this.btn_TRIPRegWrite);
            this.tabTRIPRegs.Controls.Add(this.label9);
            this.tabTRIPRegs.Location = new System.Drawing.Point(4, 22);
            this.tabTRIPRegs.Name = "tabTRIPRegs";
            this.tabTRIPRegs.Padding = new System.Windows.Forms.Padding(3);
            this.tabTRIPRegs.Size = new System.Drawing.Size(387, 435);
            this.tabTRIPRegs.TabIndex = 1;
            this.tabTRIPRegs.Text = "TRIP Regs";
            this.tabTRIPRegs.UseVisualStyleBackColor = true;
            // 
            // tripDevRegControl1
            // 
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
            this.tripDevRegControl1.Size = new System.Drawing.Size(265, 390);
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
            // btn_TRIPAdvancedGUI
            // 
            this.btn_TRIPAdvancedGUI.BackColor = System.Drawing.Color.Coral;
            this.btn_TRIPAdvancedGUI.Location = new System.Drawing.Point(238, 14);
            this.btn_TRIPAdvancedGUI.Name = "btn_TRIPAdvancedGUI";
            this.btn_TRIPAdvancedGUI.Size = new System.Drawing.Size(103, 20);
            this.btn_TRIPAdvancedGUI.TabIndex = 34;
            this.btn_TRIPAdvancedGUI.Text = "Show Default GUI";
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
            this.btn_TRIPRegRead.Location = new System.Drawing.Point(286, 40);
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
            this.btn_TRIPRegWrite.Location = new System.Drawing.Point(286, 66);
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
            // tabFLASH
            // 
            this.tabFLASH.Location = new System.Drawing.Point(4, 22);
            this.tabFLASH.Name = "tabFLASH";
            this.tabFLASH.Padding = new System.Windows.Forms.Padding(3);
            this.tabFLASH.Size = new System.Drawing.Size(387, 435);
            this.tabFLASH.TabIndex = 2;
            this.tabFLASH.Text = "FLASH";
            this.tabFLASH.UseVisualStyleBackColor = true;
            // 
            // errMain
            // 
            this.errMain.ContainerControl = this;
            // 
            // treeView1
            // 
            this.treeView1.AccessibleDescription = "";
            this.treeView1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)
                        | System.Windows.Forms.AnchorStyles.Right)));
            this.treeView1.ContextMenuStrip = this.contextMenuStrip1;
            this.treeView1.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.treeView1.Location = new System.Drawing.Point(5, 27);
            this.treeView1.Name = "treeView1";
            this.treeView1.ShowNodeToolTips = true;
            this.treeView1.Size = new System.Drawing.Size(305, 461);
            this.treeView1.TabIndex = 1;
            this.treeView1.AfterSelect += new System.Windows.Forms.TreeViewEventHandler(this.treeView1_AfterSelect);
            // 
            // contextMenuStrip1
            // 
            this.contextMenuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.toolStripMenuItemUpdateStatusString,
            this.toolStripSeparator2});
            this.contextMenuStrip1.Name = "contextMenuStrip1";
            this.contextMenuStrip1.Size = new System.Drawing.Size(175, 32);
            // 
            // toolStripMenuItemUpdateStatusString
            // 
            this.toolStripMenuItemUpdateStatusString.Name = "toolStripMenuItemUpdateStatusString";
            this.toolStripMenuItemUpdateStatusString.Size = new System.Drawing.Size(174, 22);
            this.toolStripMenuItemUpdateStatusString.Text = "Update Status String";
            this.toolStripMenuItemUpdateStatusString.Click += new System.EventHandler(this.toolStripMenuItemUpdateStatusString_Click);
            // 
            // toolStripSeparator2
            // 
            this.toolStripSeparator2.Name = "toolStripSeparator2";
            this.toolStripSeparator2.Size = new System.Drawing.Size(171, 6);
            // 
            // menuStrip1
            // 
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.toolStripMenuItemFile,
            this.showToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(723, 24);
            this.menuStrip1.TabIndex = 2;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // toolStripMenuItemFile
            // 
            this.toolStripMenuItemFile.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.LoadHardwareToolStripMenuItem,
            this.loadConfigXmlToolStripMenuItem,
            this.saveConfigXmlToolStripMenuItem,
            this.WriteXMLToHardwareToolStripMenuItem});
            this.toolStripMenuItemFile.Name = "toolStripMenuItemFile";
            this.toolStripMenuItemFile.ShowShortcutKeys = false;
            this.toolStripMenuItemFile.Size = new System.Drawing.Size(35, 20);
            this.toolStripMenuItemFile.Text = "File";
            // 
            // LoadHardwareToolStripMenuItem
            // 
            this.LoadHardwareToolStripMenuItem.Name = "LoadHardwareToolStripMenuItem";
            this.LoadHardwareToolStripMenuItem.Size = new System.Drawing.Size(185, 22);
            this.LoadHardwareToolStripMenuItem.Text = "Load Hardware";
            this.LoadHardwareToolStripMenuItem.Click += new System.EventHandler(this.LoadHardwareToolStripMenuItem_Click);
            // 
            // loadConfigXmlToolStripMenuItem
            // 
            this.loadConfigXmlToolStripMenuItem.Name = "loadConfigXmlToolStripMenuItem";
            this.loadConfigXmlToolStripMenuItem.Size = new System.Drawing.Size(185, 22);
            this.loadConfigXmlToolStripMenuItem.Text = "Load Config Xml";
            this.loadConfigXmlToolStripMenuItem.Click += new System.EventHandler(this.loadConfigXmlToolStripMenuItem_Click);
            // 
            // saveConfigXmlToolStripMenuItem
            // 
            this.saveConfigXmlToolStripMenuItem.Enabled = false;
            this.saveConfigXmlToolStripMenuItem.Name = "saveConfigXmlToolStripMenuItem";
            this.saveConfigXmlToolStripMenuItem.Size = new System.Drawing.Size(185, 22);
            this.saveConfigXmlToolStripMenuItem.Text = "Save Config Xml";
            this.saveConfigXmlToolStripMenuItem.Click += new System.EventHandler(this.saveConfigXmlToolStripMenuItem_Click);
            // 
            // WriteXMLToHardwareToolStripMenuItem
            // 
            this.WriteXMLToHardwareToolStripMenuItem.Enabled = false;
            this.WriteXMLToHardwareToolStripMenuItem.Name = "WriteXMLToHardwareToolStripMenuItem";
            this.WriteXMLToHardwareToolStripMenuItem.Size = new System.Drawing.Size(185, 22);
            this.WriteXMLToHardwareToolStripMenuItem.Text = "Write XML to Hardware";
            this.WriteXMLToHardwareToolStripMenuItem.Click += new System.EventHandler(this.WriteXMLToHardwareToolStripMenuItem_Click);
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
            this.showToolStripMenuItem.Size = new System.Drawing.Size(45, 20);
            this.showToolStripMenuItem.Text = "Show";
            // 
            // expandAllToolStripMenuItem
            // 
            this.expandAllToolStripMenuItem.Name = "expandAllToolStripMenuItem";
            this.expandAllToolStripMenuItem.Size = new System.Drawing.Size(133, 22);
            this.expandAllToolStripMenuItem.Text = "Expand All";
            this.expandAllToolStripMenuItem.Click += new System.EventHandler(this.expandAllToolStripMenuItem_Click);
            // 
            // collapseAllToolStripMenuItem
            // 
            this.collapseAllToolStripMenuItem.Name = "collapseAllToolStripMenuItem";
            this.collapseAllToolStripMenuItem.Size = new System.Drawing.Size(133, 22);
            this.collapseAllToolStripMenuItem.Text = "Collapse All";
            this.collapseAllToolStripMenuItem.Click += new System.EventHandler(this.collapseAllToolStripMenuItem_Click);
            // 
            // toolStripSeparator1
            // 
            this.toolStripSeparator1.Name = "toolStripSeparator1";
            this.toolStripSeparator1.Size = new System.Drawing.Size(130, 6);
            // 
            // redPathsToolStripMenuItem
            // 
            this.redPathsToolStripMenuItem.Name = "redPathsToolStripMenuItem";
            this.redPathsToolStripMenuItem.Size = new System.Drawing.Size(133, 22);
            this.redPathsToolStripMenuItem.Text = "Red paths";
            this.redPathsToolStripMenuItem.Click += new System.EventHandler(this.redPathsToolStripMenuItem_Click);
            // 
            // bluePathsToolStripMenuItem
            // 
            this.bluePathsToolStripMenuItem.Name = "bluePathsToolStripMenuItem";
            this.bluePathsToolStripMenuItem.Size = new System.Drawing.Size(133, 22);
            this.bluePathsToolStripMenuItem.Text = "Blue paths";
            this.bluePathsToolStripMenuItem.Click += new System.EventHandler(this.bluePathsToolStripMenuItem_Click);
            // 
            // greenPathsToolStripMenuItem
            // 
            this.greenPathsToolStripMenuItem.Name = "greenPathsToolStripMenuItem";
            this.greenPathsToolStripMenuItem.Size = new System.Drawing.Size(133, 22);
            this.greenPathsToolStripMenuItem.Text = "Green paths";
            this.greenPathsToolStripMenuItem.Click += new System.EventHandler(this.greenPathsToolStripMenuItem_Click);
            // 
            // statusStrip1
            // 
            this.statusStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.prgStatus,
            this.lblStatus});
            this.statusStrip1.Location = new System.Drawing.Point(0, 494);
            this.statusStrip1.Name = "statusStrip1";
            this.statusStrip1.Size = new System.Drawing.Size(723, 22);
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
            this.lblStatus.Size = new System.Drawing.Size(606, 17);
            this.lblStatus.Spring = true;
            this.lblStatus.Text = "lblStatus";
            // 
            // frmMinervaGUI
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(723, 516);
            this.Controls.Add(this.statusStrip1);
            this.Controls.Add(this.treeView1);
            this.Controls.Add(this.tabControl1);
            this.Controls.Add(this.menuStrip1);
            this.MainMenuStrip = this.menuStrip1;
            this.Name = "frmMinervaGUI";
            this.Text = "Minerva Slow Control";
            this.tabControl1.ResumeLayout(false);
            this.tabDescription.ResumeLayout(false);
            this.tabCRIM.ResumeLayout(false);
            this.tabCROC.ResumeLayout(false);
            this.tabFPGARegs.ResumeLayout(false);
            this.tabTRIPRegs.ResumeLayout(false);
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
        private System.Windows.Forms.ToolStripMenuItem LoadHardwareToolStripMenuItem;
        private System.Windows.Forms.TabPage tabFLASH;
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
        private System.Windows.Forms.RichTextBox richTextBoxCrim;
        private System.Windows.Forms.RichTextBox richTextBoxCroc;
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
        private System.Windows.Forms.ToolStripMenuItem WriteXMLToHardwareToolStripMenuItem;
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

    }
}

