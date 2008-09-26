namespace MinervaGUI
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
            this.tabCRIM = new System.Windows.Forms.TabPage();
            this.tabCROC = new System.Windows.Forms.TabPage();
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
            this.groupBoxCH_StatusRegister = new System.Windows.Forms.GroupBox();
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
            this.lblCH_StatFFONotEmpty = new System.Windows.Forms.Label();
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
            this.groupBoxCH_LoopDelay = new System.Windows.Forms.GroupBox();
            this.btn_CHReadLoopDelay = new System.Windows.Forms.Button();
            this.lblCH_LoopDelayValue = new System.Windows.Forms.Label();
            this.groupBoxCH_DPM = new System.Windows.Forms.GroupBox();
            this.btn_CHResetDPMPointer = new System.Windows.Forms.Button();
            this.btn_CHReadDPMPointer = new System.Windows.Forms.Button();
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
            this.btnSwitchToAuto = new System.Windows.Forms.Button();
            this.textBoxADCThreshold = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.btnReadHV = new System.Windows.Forms.Button();
            this.richTextBoxHVRead = new System.Windows.Forms.RichTextBox();
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
            this.actionsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.readVoltagesToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.zeroHVAllToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.statusStrip1 = new System.Windows.Forms.StatusStrip();
            this.prgStatus = new System.Windows.Forms.ToolStripProgressBar();
            this.lblStatus = new System.Windows.Forms.ToolStripStatusLabel();
            this.backgroundWorker1 = new System.ComponentModel.BackgroundWorker();
            this.label20 = new System.Windows.Forms.Label();
            this.label21 = new System.Windows.Forms.Label();
            this.label23 = new System.Windows.Forms.Label();
            this.label25 = new System.Windows.Forms.Label();
            this.label27 = new System.Windows.Forms.Label();
            this.label29 = new System.Windows.Forms.Label();
            this.label31 = new System.Windows.Forms.Label();
            this.label33 = new System.Windows.Forms.Label();
            this.tabControl1.SuspendLayout();
            this.tabDescription.SuspendLayout();
            this.tabCROC.SuspendLayout();
            this.groupBoxCROC_FLASH.SuspendLayout();
            this.tabCH.SuspendLayout();
            this.groupBoxCH_StatusRegister.SuspendLayout();
            this.groupBoxCH_FLASH.SuspendLayout();
            this.groupBoxCH_LoopDelay.SuspendLayout();
            this.groupBoxCH_DPM.SuspendLayout();
            this.tabFPGARegs.SuspendLayout();
            this.tabTRIPRegs.SuspendLayout();
            this.tabFLASHPages.SuspendLayout();
            this.tabReadHV.SuspendLayout();
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
            this.tabControl1.Controls.Add(this.tabFLASHPages);
            this.tabControl1.Controls.Add(this.tabReadHV);
            this.tabControl1.Location = new System.Drawing.Point(324, 27);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(395, 497);
            this.tabControl1.TabIndex = 0;
            // 
            // tabDescription
            // 
            this.tabDescription.Controls.Add(this.richTextBoxDescription);
            this.tabDescription.Location = new System.Drawing.Point(4, 22);
            this.tabDescription.Name = "tabDescription";
            this.tabDescription.Padding = new System.Windows.Forms.Padding(3);
            this.tabDescription.Size = new System.Drawing.Size(387, 404);
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
            this.richTextBoxDescription.Size = new System.Drawing.Size(381, 398);
            this.richTextBoxDescription.TabIndex = 0;
            this.richTextBoxDescription.Text = "";
            // 
            // tabCRIM
            // 
            this.tabCRIM.Location = new System.Drawing.Point(4, 22);
            this.tabCRIM.Name = "tabCRIM";
            this.tabCRIM.Size = new System.Drawing.Size(387, 404);
            this.tabCRIM.TabIndex = 4;
            this.tabCRIM.Text = "CRIM";
            this.tabCRIM.UseVisualStyleBackColor = true;
            // 
            // tabCROC
            // 
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
            this.tabCROC.Size = new System.Drawing.Size(387, 404);
            this.tabCROC.TabIndex = 5;
            this.tabCROC.Text = "CROC";
            this.tabCROC.UseVisualStyleBackColor = true;
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
            this.tabCH.Controls.Add(this.groupBoxCH_StatusRegister);
            this.tabCH.Controls.Add(this.groupBoxCH_FLASH);
            this.tabCH.Controls.Add(this.groupBoxCH_LoopDelay);
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
            this.tabCH.Size = new System.Drawing.Size(387, 471);
            this.tabCH.TabIndex = 6;
            this.tabCH.Text = "CH";
            this.tabCH.UseVisualStyleBackColor = true;
            // 
            // groupBoxCH_StatusRegister
            // 
            this.groupBoxCH_StatusRegister.Controls.Add(this.label31);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label33);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label27);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label29);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label23);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label25);
            this.groupBoxCH_StatusRegister.Controls.Add(this.label20);
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
            this.groupBoxCH_StatusRegister.Controls.Add(this.lblCH_StatFFONotEmpty);
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
            // lblCH_StatFFONotEmpty
            // 
            this.lblCH_StatFFONotEmpty.BackColor = System.Drawing.Color.White;
            this.lblCH_StatFFONotEmpty.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_StatFFONotEmpty.Location = new System.Drawing.Point(117, 127);
            this.lblCH_StatFFONotEmpty.Name = "lblCH_StatFFONotEmpty";
            this.lblCH_StatFFONotEmpty.Size = new System.Drawing.Size(15, 15);
            this.lblCH_StatFFONotEmpty.TabIndex = 72;
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
            // groupBoxCH_LoopDelay
            // 
            this.groupBoxCH_LoopDelay.Controls.Add(this.btn_CHReadLoopDelay);
            this.groupBoxCH_LoopDelay.Controls.Add(this.lblCH_LoopDelayValue);
            this.groupBoxCH_LoopDelay.Location = new System.Drawing.Point(164, 119);
            this.groupBoxCH_LoopDelay.Name = "groupBoxCH_LoopDelay";
            this.groupBoxCH_LoopDelay.Size = new System.Drawing.Size(193, 59);
            this.groupBoxCH_LoopDelay.TabIndex = 86;
            this.groupBoxCH_LoopDelay.TabStop = false;
            this.groupBoxCH_LoopDelay.Text = "Loop Delay Register";
            this.groupBoxCH_LoopDelay.Visible = false;
            // 
            // btn_CHReadLoopDelay
            // 
            this.btn_CHReadLoopDelay.BackColor = System.Drawing.Color.Coral;
            this.btn_CHReadLoopDelay.Location = new System.Drawing.Point(10, 20);
            this.btn_CHReadLoopDelay.Name = "btn_CHReadLoopDelay";
            this.btn_CHReadLoopDelay.Size = new System.Drawing.Size(115, 20);
            this.btn_CHReadLoopDelay.TabIndex = 83;
            this.btn_CHReadLoopDelay.Text = "Read Loop Delay";
            this.btn_CHReadLoopDelay.UseVisualStyleBackColor = false;
            // 
            // lblCH_LoopDelayValue
            // 
            this.lblCH_LoopDelayValue.BackColor = System.Drawing.Color.White;
            this.lblCH_LoopDelayValue.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_LoopDelayValue.Location = new System.Drawing.Point(122, 21);
            this.lblCH_LoopDelayValue.Name = "lblCH_LoopDelayValue";
            this.lblCH_LoopDelayValue.RightToLeft = System.Windows.Forms.RightToLeft.Yes;
            this.lblCH_LoopDelayValue.Size = new System.Drawing.Size(44, 18);
            this.lblCH_LoopDelayValue.TabIndex = 84;
            this.lblCH_LoopDelayValue.Text = "0xFFFF";
            // 
            // groupBoxCH_DPM
            // 
            this.groupBoxCH_DPM.Controls.Add(this.btn_CHResetDPMPointer);
            this.groupBoxCH_DPM.Controls.Add(this.btn_CHReadDPMPointer);
            this.groupBoxCH_DPM.Controls.Add(this.lblCH_DPMPointerValue);
            this.groupBoxCH_DPM.Location = new System.Drawing.Point(164, 183);
            this.groupBoxCH_DPM.Name = "groupBoxCH_DPM";
            this.groupBoxCH_DPM.Size = new System.Drawing.Size(193, 78);
            this.groupBoxCH_DPM.TabIndex = 85;
            this.groupBoxCH_DPM.TabStop = false;
            this.groupBoxCH_DPM.Text = "DPM Register";
            this.groupBoxCH_DPM.Visible = false;
            // 
            // btn_CHResetDPMPointer
            // 
            this.btn_CHResetDPMPointer.BackColor = System.Drawing.Color.Coral;
            this.btn_CHResetDPMPointer.Location = new System.Drawing.Point(10, 20);
            this.btn_CHResetDPMPointer.Name = "btn_CHResetDPMPointer";
            this.btn_CHResetDPMPointer.Size = new System.Drawing.Size(114, 20);
            this.btn_CHResetDPMPointer.TabIndex = 82;
            this.btn_CHResetDPMPointer.Text = "Reset DPM Pointer";
            this.btn_CHResetDPMPointer.UseVisualStyleBackColor = false;
            // 
            // btn_CHReadDPMPointer
            // 
            this.btn_CHReadDPMPointer.BackColor = System.Drawing.Color.Coral;
            this.btn_CHReadDPMPointer.Location = new System.Drawing.Point(10, 42);
            this.btn_CHReadDPMPointer.Name = "btn_CHReadDPMPointer";
            this.btn_CHReadDPMPointer.Size = new System.Drawing.Size(115, 20);
            this.btn_CHReadDPMPointer.TabIndex = 80;
            this.btn_CHReadDPMPointer.Text = "Read  DPM Pointer";
            this.btn_CHReadDPMPointer.UseVisualStyleBackColor = false;
            // 
            // lblCH_DPMPointerValue
            // 
            this.lblCH_DPMPointerValue.BackColor = System.Drawing.Color.White;
            this.lblCH_DPMPointerValue.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.lblCH_DPMPointerValue.Location = new System.Drawing.Point(122, 43);
            this.lblCH_DPMPointerValue.Name = "lblCH_DPMPointerValue";
            this.lblCH_DPMPointerValue.RightToLeft = System.Windows.Forms.RightToLeft.Yes;
            this.lblCH_DPMPointerValue.Size = new System.Drawing.Size(44, 18);
            this.lblCH_DPMPointerValue.TabIndex = 81;
            this.lblCH_DPMPointerValue.Text = "0xFFFF";
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
            this.tabFE.Size = new System.Drawing.Size(387, 404);
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
            this.tabFPGARegs.Size = new System.Drawing.Size(387, 404);
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
            this.fpgaDevRegControl1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)
                        | System.Windows.Forms.AnchorStyles.Right)));
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
            this.tabTRIPRegs.Size = new System.Drawing.Size(387, 404);
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
            this.tripDevRegControl1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
                        | System.Windows.Forms.AnchorStyles.Left)
                        | System.Windows.Forms.AnchorStyles.Right)));
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
            this.tabFLASHPages.Size = new System.Drawing.Size(387, 404);
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
            this.btn_FLASHAdvancedGUI.Location = new System.Drawing.Point(238, 16);
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
            this.tabReadHV.Controls.Add(this.btnSwitchToAuto);
            this.tabReadHV.Controls.Add(this.textBoxADCThreshold);
            this.tabReadHV.Controls.Add(this.label2);
            this.tabReadHV.Controls.Add(this.btnReadHV);
            this.tabReadHV.Controls.Add(this.richTextBoxHVRead);
            this.tabReadHV.Location = new System.Drawing.Point(4, 22);
            this.tabReadHV.Name = "tabReadHV";
            this.tabReadHV.Size = new System.Drawing.Size(387, 404);
            this.tabReadHV.TabIndex = 8;
            this.tabReadHV.Text = "Read HV";
            this.tabReadHV.UseVisualStyleBackColor = true;
            // 
            // btnSwitchToAuto
            // 
            this.btnSwitchToAuto.Location = new System.Drawing.Point(240, 403);
            this.btnSwitchToAuto.Name = "btnSwitchToAuto";
            this.btnSwitchToAuto.Size = new System.Drawing.Size(102, 20);
            this.btnSwitchToAuto.TabIndex = 7;
            this.btnSwitchToAuto.Text = "Switch to Auto";
            this.btnSwitchToAuto.UseVisualStyleBackColor = true;
            this.btnSwitchToAuto.Click += new System.EventHandler(this.btnSwitchToAuto_Click);
            // 
            // textBoxADCThreshold
            // 
            this.textBoxADCThreshold.Enabled = false;
            this.textBoxADCThreshold.Location = new System.Drawing.Point(13, 403);
            this.textBoxADCThreshold.Name = "textBoxADCThreshold";
            this.textBoxADCThreshold.Size = new System.Drawing.Size(68, 20);
            this.textBoxADCThreshold.TabIndex = 6;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(87, 406);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(65, 13);
            this.label2.TabIndex = 5;
            this.label2.Text = "ADC Counts";
            // 
            // btnReadHV
            // 
            this.btnReadHV.Enabled = false;
            this.btnReadHV.Location = new System.Drawing.Point(158, 403);
            this.btnReadHV.Name = "btnReadHV";
            this.btnReadHV.Size = new System.Drawing.Size(76, 20);
            this.btnReadHV.TabIndex = 3;
            this.btnReadHV.Text = "Read";
            this.btnReadHV.UseVisualStyleBackColor = true;
            this.btnReadHV.Click += new System.EventHandler(this.btnReadHV_Click);
            // 
            // richTextBoxHVRead
            // 
            this.richTextBoxHVRead.Location = new System.Drawing.Point(0, 3);
            this.richTextBoxHVRead.Name = "richTextBoxHVRead";
            this.richTextBoxHVRead.Size = new System.Drawing.Size(384, 394);
            this.richTextBoxHVRead.TabIndex = 0;
            this.richTextBoxHVRead.Text = "";
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
            this.treeView1.Size = new System.Drawing.Size(313, 497);
            this.treeView1.TabIndex = 1;
            this.treeView1.AfterSelect += new System.Windows.Forms.TreeViewEventHandler(this.treeView1_AfterSelect);
            // 
            // contextMenuStrip1
            // 
            this.contextMenuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.toolStripMenuItemUpdateStatusString,
            this.toolStripSeparator2});
            this.contextMenuStrip1.Name = "contextMenuStrip1";
            this.contextMenuStrip1.Size = new System.Drawing.Size(186, 32);
            // 
            // toolStripMenuItemUpdateStatusString
            // 
            this.toolStripMenuItemUpdateStatusString.Name = "toolStripMenuItemUpdateStatusString";
            this.toolStripMenuItemUpdateStatusString.Size = new System.Drawing.Size(185, 22);
            this.toolStripMenuItemUpdateStatusString.Text = "Update Status String";
            this.toolStripMenuItemUpdateStatusString.Click += new System.EventHandler(this.toolStripMenuItemUpdateStatusString_Click);
            // 
            // toolStripSeparator2
            // 
            this.toolStripSeparator2.Name = "toolStripSeparator2";
            this.toolStripSeparator2.Size = new System.Drawing.Size(182, 6);
            // 
            // menuStrip1
            // 
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.toolStripMenuItemFile,
            this.showToolStripMenuItem,
            this.actionsToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(731, 24);
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
            this.LoadHardwareToolStripMenuItem.Size = new System.Drawing.Size(196, 22);
            this.LoadHardwareToolStripMenuItem.Text = "Load Hardware";
            this.LoadHardwareToolStripMenuItem.Click += new System.EventHandler(this.LoadHardwareToolStripMenuItem_Click);
            // 
            // loadConfigXmlToolStripMenuItem
            // 
            this.loadConfigXmlToolStripMenuItem.Name = "loadConfigXmlToolStripMenuItem";
            this.loadConfigXmlToolStripMenuItem.Size = new System.Drawing.Size(196, 22);
            this.loadConfigXmlToolStripMenuItem.Text = "Load Config Xml";
            this.loadConfigXmlToolStripMenuItem.Click += new System.EventHandler(this.loadConfigXmlToolStripMenuItem_Click);
            // 
            // saveConfigXmlToolStripMenuItem
            // 
            this.saveConfigXmlToolStripMenuItem.Enabled = false;
            this.saveConfigXmlToolStripMenuItem.Name = "saveConfigXmlToolStripMenuItem";
            this.saveConfigXmlToolStripMenuItem.Size = new System.Drawing.Size(196, 22);
            this.saveConfigXmlToolStripMenuItem.Text = "Save Config Xml";
            this.saveConfigXmlToolStripMenuItem.Click += new System.EventHandler(this.saveConfigXmlToolStripMenuItem_Click);
            // 
            // WriteXMLToHardwareToolStripMenuItem
            // 
            this.WriteXMLToHardwareToolStripMenuItem.Enabled = false;
            this.WriteXMLToHardwareToolStripMenuItem.Name = "WriteXMLToHardwareToolStripMenuItem";
            this.WriteXMLToHardwareToolStripMenuItem.Size = new System.Drawing.Size(196, 22);
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
            this.expandAllToolStripMenuItem.Size = new System.Drawing.Size(144, 22);
            this.expandAllToolStripMenuItem.Text = "Expand All";
            this.expandAllToolStripMenuItem.Click += new System.EventHandler(this.expandAllToolStripMenuItem_Click);
            // 
            // collapseAllToolStripMenuItem
            // 
            this.collapseAllToolStripMenuItem.Name = "collapseAllToolStripMenuItem";
            this.collapseAllToolStripMenuItem.Size = new System.Drawing.Size(144, 22);
            this.collapseAllToolStripMenuItem.Text = "Collapse All";
            this.collapseAllToolStripMenuItem.Click += new System.EventHandler(this.collapseAllToolStripMenuItem_Click);
            // 
            // toolStripSeparator1
            // 
            this.toolStripSeparator1.Name = "toolStripSeparator1";
            this.toolStripSeparator1.Size = new System.Drawing.Size(141, 6);
            // 
            // redPathsToolStripMenuItem
            // 
            this.redPathsToolStripMenuItem.Name = "redPathsToolStripMenuItem";
            this.redPathsToolStripMenuItem.Size = new System.Drawing.Size(144, 22);
            this.redPathsToolStripMenuItem.Text = "Red paths";
            this.redPathsToolStripMenuItem.Click += new System.EventHandler(this.redPathsToolStripMenuItem_Click);
            // 
            // bluePathsToolStripMenuItem
            // 
            this.bluePathsToolStripMenuItem.Name = "bluePathsToolStripMenuItem";
            this.bluePathsToolStripMenuItem.Size = new System.Drawing.Size(144, 22);
            this.bluePathsToolStripMenuItem.Text = "Blue paths";
            this.bluePathsToolStripMenuItem.Click += new System.EventHandler(this.bluePathsToolStripMenuItem_Click);
            // 
            // greenPathsToolStripMenuItem
            // 
            this.greenPathsToolStripMenuItem.Name = "greenPathsToolStripMenuItem";
            this.greenPathsToolStripMenuItem.Size = new System.Drawing.Size(144, 22);
            this.greenPathsToolStripMenuItem.Text = "Green paths";
            this.greenPathsToolStripMenuItem.Click += new System.EventHandler(this.greenPathsToolStripMenuItem_Click);
            // 
            // actionsToolStripMenuItem
            // 
            this.actionsToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.readVoltagesToolStripMenuItem,
            this.zeroHVAllToolStripMenuItem});
            this.actionsToolStripMenuItem.Name = "actionsToolStripMenuItem";
            this.actionsToolStripMenuItem.Size = new System.Drawing.Size(54, 20);
            this.actionsToolStripMenuItem.Text = "Actions";
            // 
            // readVoltagesToolStripMenuItem
            // 
            this.readVoltagesToolStripMenuItem.Enabled = false;
            this.readVoltagesToolStripMenuItem.Name = "readVoltagesToolStripMenuItem";
            this.readVoltagesToolStripMenuItem.Size = new System.Drawing.Size(154, 22);
            this.readVoltagesToolStripMenuItem.Text = "Read Voltages";
            this.readVoltagesToolStripMenuItem.Click += new System.EventHandler(this.readVoltagesToolStripMenuItem_Click);
            // 
            // zeroHVAllToolStripMenuItem
            // 
            this.zeroHVAllToolStripMenuItem.Enabled = false;
            this.zeroHVAllToolStripMenuItem.Name = "zeroHVAllToolStripMenuItem";
            this.zeroHVAllToolStripMenuItem.Size = new System.Drawing.Size(154, 22);
            this.zeroHVAllToolStripMenuItem.Text = "Zero HV All";
            this.zeroHVAllToolStripMenuItem.Click += new System.EventHandler(this.zeroHVAllToolStripMenuItem_Click);
            // 
            // statusStrip1
            // 
            this.statusStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.prgStatus,
            this.lblStatus});
            this.statusStrip1.Location = new System.Drawing.Point(0, 530);
            this.statusStrip1.Name = "statusStrip1";
            this.statusStrip1.Size = new System.Drawing.Size(731, 22);
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
            this.lblStatus.Size = new System.Drawing.Size(614, 17);
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
            // label20
            // 
            this.label20.BackColor = System.Drawing.Color.White;
            this.label20.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label20.Location = new System.Drawing.Point(117, 172);
            this.label20.Name = "label20";
            this.label20.Size = new System.Drawing.Size(15, 15);
            this.label20.TabIndex = 81;
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
            // label23
            // 
            this.label23.BackColor = System.Drawing.Color.White;
            this.label23.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label23.Location = new System.Drawing.Point(117, 235);
            this.label23.Name = "label23";
            this.label23.Size = new System.Drawing.Size(15, 15);
            this.label23.TabIndex = 83;
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
            // label27
            // 
            this.label27.BackColor = System.Drawing.Color.White;
            this.label27.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label27.Location = new System.Drawing.Point(117, 283);
            this.label27.Name = "label27";
            this.label27.Size = new System.Drawing.Size(15, 15);
            this.label27.TabIndex = 85;
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
            // label31
            // 
            this.label31.BackColor = System.Drawing.Color.White;
            this.label31.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.label31.Location = new System.Drawing.Point(117, 298);
            this.label31.Name = "label31";
            this.label31.Size = new System.Drawing.Size(15, 15);
            this.label31.TabIndex = 87;
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
            // frmSlowControl
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(731, 552);
            this.Controls.Add(this.statusStrip1);
            this.Controls.Add(this.treeView1);
            this.Controls.Add(this.tabControl1);
            this.Controls.Add(this.menuStrip1);
            this.MainMenuStrip = this.menuStrip1;
            this.Name = "frmSlowControl";
            this.Text = "Minerva Slow Control";
            this.Load += new System.EventHandler(this.frmSlowControl_Load);
            this.tabControl1.ResumeLayout(false);
            this.tabDescription.ResumeLayout(false);
            this.tabCROC.ResumeLayout(false);
            this.groupBoxCROC_FLASH.ResumeLayout(false);
            this.tabCH.ResumeLayout(false);
            this.groupBoxCH_StatusRegister.ResumeLayout(false);
            this.groupBoxCH_FLASH.ResumeLayout(false);
            this.groupBoxCH_LoopDelay.ResumeLayout(false);
            this.groupBoxCH_DPM.ResumeLayout(false);
            this.tabFPGARegs.ResumeLayout(false);
            this.tabTRIPRegs.ResumeLayout(false);
            this.tabFLASHPages.ResumeLayout(false);
            this.tabReadHV.ResumeLayout(false);
            this.tabReadHV.PerformLayout();
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
        private System.Windows.Forms.TabPage tabReadHV;
        private System.Windows.Forms.RichTextBox richTextBoxHVRead;
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
        private System.Windows.Forms.Label lblCH_StatFFONotEmpty;
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
        private System.Windows.Forms.Button btn_CHResetDPMPointer;
        private System.Windows.Forms.Label lblCH_DPMPointerValue;
        private System.Windows.Forms.Button btn_CHReadDPMPointer;
        private System.Windows.Forms.Label lblCH_LoopDelayValue;
        private System.Windows.Forms.Button btn_CHReadLoopDelay;
        private System.Windows.Forms.GroupBox groupBoxCH_LoopDelay;
        private System.Windows.Forms.GroupBox groupBoxCH_DPM;
        private System.Windows.Forms.GroupBox groupBoxCH_StatusRegister;
        private System.Windows.Forms.GroupBox groupBoxCH_FLASH;
        private System.Windows.Forms.GroupBox groupBoxCROC_FLASH;
        private System.Windows.Forms.Label label23;
        private System.Windows.Forms.Label label25;
        private System.Windows.Forms.Label label20;
        private System.Windows.Forms.Label label21;
        private System.Windows.Forms.Label label31;
        private System.Windows.Forms.Label label33;
        private System.Windows.Forms.Label label27;
        private System.Windows.Forms.Label label29;

    }
}
