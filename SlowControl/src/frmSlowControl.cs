using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Threading;
using System.IO;
using System.IO.Ports;
using System.Xml.Serialization;
using VMEInterfaces;
using System.Collections.Specialized;
using ConfigFiles;

namespace SlowControl
{
    public partial class frmSlowControl : Form
    {
        //bool AppendDescription = false;

        public CAEN2718 controller;
        int linkN; int boardN;
        List<CRIM> CRIMModules = new List<CRIM>();
        List<CROC> CROCModules = new List<CROC>();
        List<V1720> V1720Modules = new List<V1720>();
        List<CRIMnode> CRIMnodes = new List<CRIMnode>();
        List<CROCnode> CROCnodes = new List<CROCnode>();
        List<CHnode> CHnodes = new List<CHnode>();
        List<FEnode> FEnodes = new List<FEnode>();
        public static List<FEBSlave> FEBSlaves = new List<FEBSlave>();
        List<FEB_TPDelay> FEBTPDelayList = new List<FEB_TPDelay>();
        List<V1720node> V1720nodes = new List<V1720node>();

        MinervaDevicesInfo minervaDevicesInfo = new MinervaDevicesInfo();
        MinervaDevicesInfo xmlInfo = new MinervaDevicesInfo();

        private enum FastCommands : byte
        {
            OpenGate = 0xB1,
            ResetFPGA = 0x8D,
            //ResetTimer = 0xC5,
            //LoadTimer = 0xC9,
            ResetTimer = 0xC9,  // 03.12.2009 to make Minos CNTRST 0xC5 act as a LoadTimer
            LoadTimer = 0xC5,   // 03.12.2009 to make Minos CNTRST 0xC5 act as a LoadTimer
            TriggerFound = 0x89,
            TriggerRearm = 0x85,
            QueryFPGA = 0x91    // 04.14.2009 to make FEBs respond with NAHeader(01=2bits)+TripComp(4bits)+FEAddress(4bits)
        }

        private static EventWaitHandle vmeDone = null;

        static frmSlowControl()
        {
            vmeDone = new EventWaitHandle(true, EventResetMode.AutoReset, "MinervaVMEDone");
        }

        public frmSlowControl(int linkNumber, int boardNumber, out bool success)
        {
            InitializeComponent();
            Metadata.MetaData.log.FileName = "SlowControl"; // "SlowControl_L" + linkNumber + "B" + boardNumber;

            if (fpgaDevRegControl1.IsAdvancedGUI == true)
                btn_FPGAAdvancedGUI.Text = "Show Default GUI";
            else
                btn_FPGAAdvancedGUI.Text = "Show Advanced GUI";
            if (tripDevRegControl1.IsAdvancedGUI == true)
                btn_TRIPAdvancedGUI.Text = "Show Default GUI";
            else
                btn_TRIPAdvancedGUI.Text = "Show Advanced GUI";

            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    controller = new CAEN2718("CAEN VME", linkNumber, boardNumber);
                    this.Text = string.Format("Slow Control - LINK={0}, CRATE={1}", linkNumber, boardNumber);
                    StringBuilder sb = new StringBuilder();
                    Refresh();
                    controller.Initialize();
                    CAENInterface.CAENVME.BoardFWRelease(0, sb);
                    richTextBoxDescription.Text = String.Format("Controller Firmware: {0}", sb.ToString());
                    StringBuilder sw = new StringBuilder();
                    CAENInterface.CAENVME.SWRelease(sw);
                    richTextBoxDescription.AppendText(String.Format("\nDriver Library: {0}", sw.ToString()));
                    Refresh();
                    lblStatus.Text = "VME Controller initialized.";
                    linkN = linkNumber; boardN = boardNumber;
                    success = true;
                }
                catch
                {
                    prgStatus.Value = 0;
                    MessageBox.Show("Unable to initialize crate controller\nApplication will be closed.");
                    lblStatus.Text = "VME Controller NOT initialized.";
                    this.Close();
                    success = false;
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void frmSlowControl_Load(object sender, EventArgs e)
        {
            Metadata.MetaData.log.WriteToFirstLine("SlowControl Started at " + DateTime.Now);
            Metadata.MetaData.log.AddToLog();
            //FlashFrame.PageCompleted += new ProgressChangedEventHandler(ProgressReport); //10.05.2009 CG commented out because of two crates!!!
            loadHardwareToolStripMenuItem_Click(null, null);
            cmb_CRIMTimingMode.Items.Clear();
            cmb_CRIMTimingMode.Items.AddRange(Enum.GetNames(typeof(CRIM.TimingModes)));
            cmb_CRIMTimingFrequency.Items.Clear();
            cmb_CRIMTimingFrequency.Items.AddRange(Enum.GetNames(typeof(CRIM.TimingFrequencies)));
        }

        private void frmSlowControl_FormClosing(object sender, FormClosingEventArgs e)
        {
            controller.Dispose();
        }

        private void ProgressReport(object sender, ProgressChangedEventArgs e)
        {
            Application.DoEvents();
            {
                prgStatus.Value = e.ProgressPercentage;
                lblStatus.Text = e.UserState.ToString() + "  " + e.ProgressPercentage;
                Refresh();
            }
        }

        private void treeView1_AfterSelect(object sender, TreeViewEventArgs e)
        {
            //////if (!AppendDescription) richTextBoxDescription.Clear();
            if (e.Node is CRIMnode)
            {
                lblCRIM_CRIMID.Text = Convert.ToString(((CRIM)e.Node.Tag).BaseAddress >> 16);
                CrimClearLabels();
                tabControl1.SelectTab(tabCRIM);
            }
            if (e.Node is CROCnode)
            {
                lblCROC_CROCID.Text = Convert.ToString(((CROC)e.Node.Tag).BaseAddress >> 16);
                CrocClearLabels();
                tabControl1.SelectTab(tabCROC);
            }
            if (e.Node is CHnode)
            {
                lblCH_CHID.Text = ((CROCFrontEndChannel)(e.Node.Tag)).ChannelNumber.ToString();
                lblCH_CROCID.Text = ((((CROC)(((CROCnode)(e.Node.Parent)).Tag)).BaseAddress) >> 16).ToString();
                ChannelClearLabels();
                tabControl1.SelectTab(tabCH);
            }
            if (e.Node is FEnode)
            {
                richTextBoxDescription.AppendText(
                    "\nFEid=" + ((FEnode)(e.Node)).BoardID.ToString() +
                    ", CHid=" + ((CROCFrontEndChannel)(((CHnode)(e.Node.Parent)).Tag)).ChannelNumber.ToString() +
                    ", CROCid=" + ((((CROC)(((CROCnode)(e.Node.Parent.Parent)).Tag)).BaseAddress) >> 16).ToString());
                //tabControl1.SelectTab("tabFE");
                tabControl1.SelectTab(tabDescription);
            }
            if (e.Node is FPGAnode)
            {
                lblFPGA_FEID.Text = ((FEnode)(e.Node.Parent)).BoardID.ToString();
                lblFPGA_CHID.Text = ((CROCFrontEndChannel)(((CHnode)(e.Node.Parent.Parent)).Tag)).ChannelNumber.ToString();
                lblFPGA_CROCID.Text = ((((CROC)(((CROCnode)(e.Node.Parent.Parent.Parent)).Tag)).BaseAddress) >> 16).ToString();
                btn_FPGARegRead_Click(null, null);
                tabControl1.SelectTab(tabFPGARegs);
            }
            if (e.Node is TRIPnode)
            {
                lblTRIP_FEID.Text = ((FEnode)(e.Node.Parent)).BoardID.ToString();
                lblTRIP_CHID.Text = ((CROCFrontEndChannel)(((CHnode)(e.Node.Parent.Parent)).Tag)).ChannelNumber.ToString();
                lblTRIP_CROCID.Text = ((((CROC)(((CROCnode)(e.Node.Parent.Parent.Parent)).Tag)).BaseAddress) >> 16).ToString();
                cmb_TripID.SelectedIndex = 0;
                btn_TRIPRegRead_Click(null, null);
                tabControl1.SelectTab(tabTRIPRegs);
            }

            if (e.Node is FLASHnode)
            {
                lblFLASH_FEID.Text = ((FEnode)(e.Node.Parent)).BoardID.ToString();
                lblFLASH_CHID.Text = ((CROCFrontEndChannel)(((CHnode)(e.Node.Parent.Parent)).Tag)).ChannelNumber.ToString();
                lblFLASH_CROCID.Text = ((((CROC)(((CROCnode)(e.Node.Parent.Parent.Parent)).Tag)).BaseAddress) >> 16).ToString();
                tabControl1.SelectTab(tabFLASHPages);
            }
            if (e.Node is V1720node)
            {
                lblV1720_V1720ID.Text = Convert.ToString( ((V1720)(e.Node.Tag)).BaseAddress >> 16);
                tabControl1.SelectTab(tabV1720);
            }
        }

        private void UserAlert(string errMsg)
        {
            MessageBox.Show(errMsg);
            richTextBoxDescription.SelectionColor = Color.Red;
            richTextBoxDescription.AppendText(errMsg);
            richTextBoxDescription.SelectionColor = Color.Black;
        }

        private void loadConfigXmlToolStripMenuItem_Click(object sender, EventArgs e)
        {
            OpenFileDialog myOFD = new OpenFileDialog();
            myOFD.Filter = "xml files (*.xml)|*.xml|All files (*.*)|*.*";
            myOFD.FilterIndex = 1;
            myOFD.RestoreDirectory = true;
            if (myOFD.ShowDialog() == DialogResult.OK)
            {
                richTextBoxDescription.Clear();
                tabControl1.SelectTab("tabDescription");
                System.IO.StreamReader xmlFileR = System.IO.File.OpenText(myOFD.FileName);
                XmlSerializer xmlReader = new XmlSerializer(typeof(MinervaDevicesInfo));
                try
                {
                    xmlInfo = (MinervaDevicesInfo)xmlReader.Deserialize(xmlFileR);
                    xmlFileR.Close();
                    //
                    xmlFileR = System.IO.File.OpenText(myOFD.FileName);
                    richTextBoxDescription.AppendText("Loading file " + myOFD.FileName + "\n");
                    richTextBoxDescription.AppendText("\n" + xmlFileR.ReadToEnd() + "\n");
                    writeXmlToHardwareToolStripMenuItem.Enabled = true;
                }
                catch (Exception ex)
                {
                    UserAlert(ex.Message + "\n");
                }
                finally 
                { 
                    xmlFileR.Close();
                    prgStatus.Maximum = 100;
                    ProgressReport(null, new ProgressChangedEventArgs(100, string.Format("Load Configuration")));
                }
            }
        }

        private void saveConfigXmlToolStripMenuItem_Click(object sender, EventArgs e)
        {
            SaveFileDialog mySFD = new SaveFileDialog();
            mySFD.Filter = "xml files (*.xml)|*.xml|All files (*.*)|*.*";
            mySFD.FilterIndex = 1;
            mySFD.RestoreDirectory = true;
            if (mySFD.ShowDialog() == DialogResult.OK)
            {
                richTextBoxDescription.Clear();
                tabControl1.SelectTab("tabDescription");
                GetMinervaDevicesInfo();
                System.IO.StreamWriter xmlFileW = System.IO.File.CreateText(mySFD.FileName);
                XmlSerializer xmlWriter = new XmlSerializer(minervaDevicesInfo.GetType());
                try
                {
                    xmlWriter.Serialize(xmlFileW, minervaDevicesInfo);
                    xmlFileW.Close();
                    //
                    System.IO.StreamReader xmlFileR = System.IO.File.OpenText(mySFD.FileName);
                    richTextBoxDescription.AppendText("\nSaving file " + mySFD.FileName + "\n");
                    richTextBoxDescription.AppendText("\n" + xmlFileR.ReadToEnd() + "\n");
                    xmlFileR.Close();
                }
                catch (Exception ex)
                {
                    UserAlert(ex.Message + "\n");
                }
                finally
                {
                    xmlFileW.Close();
                    prgStatus.Maximum = 100;
                    ProgressReport(null, new ProgressChangedEventArgs(100, string.Format("Save Configuration")));
                }
            }
        }

        private void writeXmlToHardwareToolStripMenuItem_Click(object sender, EventArgs e)
        {
            richTextBoxDescription.Clear();
            tabControl1.SelectTab(tabDescription);
            bool crimsMatch = true;
            bool crocsMatch = true;
            bool febsMatch = true;
            try
            {
                #region Compare CRIMs in XML file to CRIMs loaded
                richTextBoxDescription.AppendText("\nComparing CRIMs in XML file to CRIMs loaded\n");
                if (xmlInfo.CRIMs.Count != minervaDevicesInfo.CRIMs.Count)
                {
                    crimsMatch = false;
                    UserAlert("Number of CRIMs in XML file is different from the Number of CRIMs loaded\nOperation aborted\n");
                    return;
                }
                foreach (CRIMInfo xmlCRIM in xmlInfo.CRIMs)
                {
                    bool crimFound = false;
                    foreach (CRIMInfo minervaCRIM in minervaDevicesInfo.CRIMs)
                    {
                        if (xmlCRIM.BaseAddress == minervaCRIM.BaseAddress)
                        {
                            crimFound = true;
                            richTextBoxDescription.AppendText(xmlCRIM.Description + " in XML file found\n");
                            break;
                        }
                    }
                    if (!crimFound)
                    {
                        crimsMatch = false;
                        UserAlert(xmlCRIM.Description + " in XML file not found\n");
                    }
                }
                if (crimsMatch) richTextBoxDescription.AppendText("Matched CRIMs in XML file to CRIMs loaded\n");
                else 
                {
                    UserAlert("ERROR : Not Matched CRIMs in XML file to CRIMs loaded\nOperation aborted\n");
                    return;
                }
                #endregion

                #region Compare CROCs in XML file to CROCs loaded
                richTextBoxDescription.AppendText("\nComparing CROCs in XML file to CROCs loaded\n");
                if (xmlInfo.CROCs.Count != minervaDevicesInfo.CROCs.Count)
                {
                    crocsMatch = false;
                    UserAlert("Number of CROCs in XML file is different from the Number of CROCs loaded\nOperation aborted\n");
                    return;
                }
                foreach (CROCInfo xmlCROC in xmlInfo.CROCs)
                {
                    bool crocFound = false;
                    foreach (CROCInfo minervaCROC in minervaDevicesInfo.CROCs)
                    {
                        if (xmlCROC.BaseAddress == minervaCROC.BaseAddress)
                        {
                            crocFound = true;
                            richTextBoxDescription.AppendText(xmlCROC.Description + " in XML file found\n");
                            break;
                        }
                    }
                    if (!crocFound)
                    {
                        crocsMatch = false;
                        UserAlert(xmlCROC.Description + " in XML file not found\n");
                    }
                }
                if (crocsMatch) richTextBoxDescription.AppendText("Matched CROCs in XML file to CROCs loaded\n");
                else
                {
                    UserAlert("ERROR : Not Matched CROCs in XML file to CROCs loaded\nOperation aborted\n");
                    return;
                }
                #endregion

                #region Compare FEBs in XML file to FEBs loaded
                richTextBoxDescription.AppendText("\nComparing FEBs in XML file to FEBs loaded\n");
                foreach (CROCInfo xmlCROC in xmlInfo.CROCs)
                {
                    foreach (CROCInfo minervaCROC in minervaDevicesInfo.CROCs)
                    {
                        if (xmlCROC.BaseAddress == minervaCROC.BaseAddress)
                        {
                            foreach (CROCChannelInfo xmlCROCChannelInfo in xmlCROC.CROCChannels)
                            {
                                foreach (CROCChannelInfo minervaCROCChannelInfo in minervaCROC.CROCChannels)
                                {
                                    if (xmlCROCChannelInfo.BaseAddress == minervaCROCChannelInfo.BaseAddress)
                                    {
                                        if (xmlCROCChannelInfo.ChainBoards.Count != minervaCROCChannelInfo.ChainBoards.Count)
                                        {
                                            febsMatch = false;
                                            UserAlert(xmlCROCChannelInfo.Description + ": Number of FEBs in XML file is different from the Number of FEBs loaded\nOperation aborted\n");
                                            return;
                                        }
                                        foreach (ChainBoardInfo xmlChainBoard in xmlCROCChannelInfo.ChainBoards)
                                        {
                                            bool febFound = false;
                                            foreach (ChainBoardInfo minervaChainBoard in minervaCROCChannelInfo.ChainBoards)
                                            {
                                                if (xmlChainBoard.BoardAddress == minervaChainBoard.BoardAddress)
                                                {
                                                    febFound = true;
                                                    richTextBoxDescription.AppendText(xmlCROCChannelInfo.Description + ":" + xmlChainBoard.BoardAddress + " in XML file found\n");
                                                    break;
                                                }
                                            }
                                            if (!febFound)
                                            {
                                                febsMatch = false;
                                                UserAlert(xmlCROCChannelInfo.Description + ":" + xmlChainBoard.BoardAddress + " in XML file not found\n");
                                            }
                                        }
                                        break; // xmlCROCChannelInfo.BaseAddress == minervaCROCChannelInfo.BaseAddress
                                    }
                                }
                            }
                            break; // xmlCROC.BaseAddress == minervaCROC.BaseAddress
                        }
                    }
                }
                if (febsMatch) richTextBoxDescription.AppendText("Matched FEBs in XML file to FEBs loaded\n");
                else
                {
                    UserAlert("ERROR : Not Matched FEBs in XML file to FEBs loaded\nOperation aborted\n");
                    return;
                }
                #endregion

                //if here, we succeed crimsMatch & crocsMatch & febsMatch == true, so let's call SetMinervaDevicesInfo();
                SetMinervaDevicesInfo();
            }
            catch (Exception ex)
            {
                UserAlert(ex.Message + "\n" +
                    "\nCRIMs match=" + crimsMatch + "\nCROCs match=" + crocsMatch + "\nFEBs match=" + febsMatch +
                    "\nCheck the current report window for RED messages and/or try again...\n");
            }
        }

        private void loadHardwareToolStripMenuItem_Click(object sender, EventArgs e)
        {
            Metadata.MetaData.log.AddToLog(string.Format("LoadHardware Started at {0}", DateTime.Now));
            //richTextBoxDescription.Clear();
            tabControl1.SelectTab(tabDescription);
            this.Cursor = Cursors.WaitCursor;
            ResetActions();
            FindVMEModules();
            Initialize(CRIMModules);    //not needed...
            Initialize(CROCModules);    //need it to see what FEs are in each channel
            UpdateTree();
            //Initialize(FEBSlaves);      //either one is used to call FEBSlave.Initialize() 
            Initialize(FEnodes);        //either one is used to call FEBSlave.Initialize() 
            GetMinervaDevicesInfo();
            //FindCRIMtoCROCCables(CRIMModules, CROCModules, CRIMtoCROCCables);
            readVoltagesToolStripMenuItem.Enabled = true;
            zeroHVAllToolStripMenuItem.Enabled = true;
            monitorVoltagesToolStripMenuItem.Enabled = true;
            saveConfigXmlToolStripMenuItem.Enabled = true;
            this.Cursor = Cursors.Arrow;
            //treeView1.ExpandAll();
            treeView1.CollapseAll();
        }

        private void ResetActions()
        {
            saveConfigXmlToolStripMenuItem.Enabled = false;
            writeXmlToHardwareToolStripMenuItem.Enabled = false;

            //For Read HV
            richTextBoxHVRead.Clear();
            readVoltagesToolStripMenuItem.Enabled = false;
            zeroHVAllToolStripMenuItem.Enabled = false;
            monitorVoltagesToolStripMenuItem.Enabled = false;
            textBoxADCThreshold.Enabled = false;
            btnReadHV.Enabled = false;
            btnSwitchToAuto.Enabled = false;
            textBoxMonitorTimer.Enabled = false;
            btnMonitorHV.Enabled = false;

            richTextBoxV1720.Clear();
        }

        private void FindVMEModules()
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    uint VMEDevsBaseAddr;
                    byte[] wData = new byte[2];
                    byte[] rData = new byte[2];
                    Random r = new Random();
                    //find any CROCs and CRIMs present on VME crate
                    CROCModules.Clear();
                    CRIMModules.Clear();
                    V1720Modules.Clear();
                    prgStatus.Minimum = 0;
                    prgStatus.Maximum = 255;
                    prgStatus.Value = 0;
                    for (VMEDevsBaseAddr = 0; VMEDevsBaseAddr <= 255; VMEDevsBaseAddr++)
                    {
                        ProgressReport(null, new ProgressChangedEventArgs((int)VMEDevsBaseAddr, string.Format("Finding VME Modules")));
                        Refresh();
                        try
                        {
                            wData[0] = (byte)r.Next(1, 255);
                            wData[1] = (byte)r.Next(1, 255);
                            FindCrocCrimModules(VMEDevsBaseAddr, wData, rData);
                            FindDigitizerModules(VMEDevsBaseAddr, wData, rData);
                        }
                        catch (Exception e)
                        {
                            if (e.Message == "Bus error") continue;
                            if (e.Message == "Communication error") throw e;
                            richTextBoxDescription.AppendText("\n\tError VMEDevsBaseAddr=" + VMEDevsBaseAddr + ", " + e.Message);
                            Metadata.MetaData.log.AddToLog("Error VMEDevsBaseAddr=" + VMEDevsBaseAddr + ", " + e.Message);
                        }
                    }
                }
                catch (Exception e)
                {
                    lblStatus.Text = "Error while finding VME Modules...";
                    richTextBoxDescription.AppendText(lblStatus.Text + "\n" + e.Message);
                    Metadata.MetaData.log.AddToLog(lblStatus.Text + "\n" + e.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void FindCrocCrimModules(uint VMEDevsBaseAddr, byte[] wData, byte[] rData)
        {
            #region Version#1 to find out CROCs and CRIMs using Write/Read through "controller" object
            try
            {
                controller.Write((VMEDevsBaseAddr << 16) + 0xF000, controller.AddressModifier,
                        controller.DataWidth, wData);
                controller.Read((VMEDevsBaseAddr << 16) + 0xF000, controller.AddressModifier,
                    controller.DataWidth, rData);
            }
            catch (Exception e)
            {
                if (e.Message == "Bus error") return;
                else throw e;
            }
            if ((rData[0] == wData[0]) && (rData[1] == wData[1]))
            {
                richTextBoxDescription.AppendText("\nVMEDevsBaseAddr = " + VMEDevsBaseAddr + " Found a CROC VME module");
                Metadata.MetaData.log.AddToLog("VMEDevsBaseAddr = " + VMEDevsBaseAddr + " Found a CROC VME module");
                CROCModules.Add(new CROC((uint)(VMEDevsBaseAddr << 16), controller, String.Format("Croc {0}", VMEDevsBaseAddr)));
            }
            if ((rData[0] == wData[0]) && (rData[1] == 0))
            {
                richTextBoxDescription.AppendText("\nVMEDevsBaseAddr = " + VMEDevsBaseAddr + " Found a CRIM VME module");
                Metadata.MetaData.log.AddToLog("VMEDevsBaseAddr = " + VMEDevsBaseAddr + " Found a CRIM VME module");
                CRIMModules.Add(new CRIM((uint)(VMEDevsBaseAddr << 16), controller, String.Format("Crim {0}", VMEDevsBaseAddr)));
            }
            #endregion
            #region Version#2 to find out CROCs and CRIMs using Write/Read directly through CAENVMElib
            //CAENVMElib.CVErrorCodes wResult = CAENInterface.CAENVME.WriteCycle(0, (VMEDevsBaseAddr << 16) + 0xF000, 
            //    wData, CAENVMElib.CVAddressModifier.cvA24_U_DATA, CAENVMElib.CVDataWidth.cvD16);
            //CAENVMElib.CVErrorCodes rResult = CAENInterface.CAENVME.ReadCycle(0, (VMEDevsBaseAddr << 16) + 0xF000, 
            //    rData, CAENVMElib.CVAddressModifier.cvA24_U_DATA, CAENVMElib.CVDataWidth.cvD16);

            //if ((rData[0] == wData[0]) && (rData[1] == wData[1]))
            //{
            //    //CROCs_VMEBaseAddress.Add(VMEBaseAddress);
            //    richTextBoxDescription.AppendText( "\nThis is a CROC VME module");
            //}
            //if ((rData[0] == wData[0]) && (rData[1] == 0))
            //{
            //    //CRIMs_VMEBaseAddress.Add(VMEBaseAddress);
            //    richTextBoxDescription.AppendText( "\nThis is a CRIM VME module");
            //}
            #endregion
        }

        private void FindDigitizerModules(uint VMEDevsBaseAddr, byte[] wData, byte[] rData)
        {
            try
            {
                controller.Write((VMEDevsBaseAddr << 16) + (uint)V1720.Registers.VMEScratch, controller.AddressModifier,
                        controller.DataWidth, wData);
                controller.Read((VMEDevsBaseAddr << 16) + (uint)V1720.Registers.VMEScratch, controller.AddressModifier,
                    controller.DataWidth, rData);
            }
            catch (Exception e)
            {
                if (e.Message == "Bus error") return;
                else throw e;
            }
            if ((rData[0] == wData[0]) && (rData[1] == wData[1]))
            {
                richTextBoxDescription.AppendText("\nVMEDevsBaseAddr = " + VMEDevsBaseAddr + " Found a DIGITIZER V1720 VME module");
                Metadata.MetaData.log.AddToLog("VMEDevsBaseAddr = " + VMEDevsBaseAddr + " Found a DIGITIZER V1720 VME module");
                V1720Modules.Add(new V1720((uint)(VMEDevsBaseAddr << 16), controller, String.Format("V1720 {0}", VMEDevsBaseAddr)));
            }
        }

        private void Initialize(List<CRIM> CRIMs)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    prgStatus.Maximum = CRIMs.Count;
                    int prg = 0;
                    foreach (CRIM crim in CRIMs)
                    {
                        crim.Initialize();
                        ProgressReport(null, new ProgressChangedEventArgs(++prg, string.Format("{0} Initialized", crim.Description)));
                    }
                }
                catch (Exception e)
                {
                    lblStatus.Text = "\nError while Initializing CRIM devices...";
                    richTextBoxDescription.AppendText(lblStatus.Text + "\n" + e.Message);
                    Metadata.MetaData.log.AddToLog(lblStatus.Text + "\n" + e.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void Initialize(List<CROC> CROCs)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    prgStatus.Maximum = CROCs.Count;
                    int prg = 0;
                    foreach (CROC croc in CROCs)
                    {
                        croc.Initialize();
                        ProgressReport(null, new ProgressChangedEventArgs(++prg, string.Format("{0} Initialized", croc.Description)));
                    }
                }
                catch (Exception e)
                {
                    lblStatus.Text = "\nError while Initializing CROC devices...";
                    richTextBoxDescription.AppendText(lblStatus.Text + "\n" + e.Message);
                    Metadata.MetaData.log.AddToLog(lblStatus.Text + "\n" + e.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        //private void Initialize(List<FEBSlave> FEBSlaves)
        //{
        //    lock (this)
        //    {
        //        vmeDone.WaitOne();
        //        try
        //        {
        //            prgStatus.Maximum = FEBSlaves.Count;
        //            int prg = 0;
        //            foreach (FEBSlave febs in FEBSlaves)
        //            {
        //                febs.Initialize();
        //                ProgressReport(null, new ProgressChangedEventArgs(++prg, (object)string.Format("{0} Initialized", febs.ToString())));
        //            }
        //        }
        //        catch (Exception e)
        //        {
        //            lblStatus.Text = "\nError while Initializing FEBSlaves devices...";
        //            richTextBoxDescription.AppendText(lblStatus.Text + "\n" + e.Message);
        //            Metadata.MetaData.log.AddToLog(lblStatus.Text + "\n" + e.Message);
        //        }
        //        finally
        //        {
        //            vmeDone.Set();
        //        }
        //    }
        //}

        private void Initialize(List<FEnode> FEnodes)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    prgStatus.Maximum = FEnodes.Count;
                    int prg = 0;
                    FEBSlaves.Clear();
                    foreach (FEnode theFEnode in FEnodes)
                    {
                        ((FEBSlave)(theFEnode.Tag)).Initialize();
                        FEBSlaves.Add((FEBSlave)(theFEnode.Tag));
                        ProgressReport(null, new ProgressChangedEventArgs(++prg, string.Format("{0}:{1} Initialized",
                            ((IFrontEndChannel)(theFEnode.Parent.Tag)).Description, (Frame.Addresses)(theFEnode.BoardID))));
                    }
                }
                catch (Exception e)
                {
                    lblStatus.Text = "\nError while Initializing FEnodes devices...";
                    richTextBoxDescription.AppendText(lblStatus.Text + "\n" + e.Message);
                    Metadata.MetaData.log.AddToLog(lblStatus.Text + "\n" + e.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        //List<CRIMtoCROCCable> CRIMtoCROCCables = new List<CRIMtoCROCCable>();
        private struct CRIMtoCROCCable
        {
        //    private uint CRIMAddr;
        //    public List<uint> CROCAddresses;
        //    public CRIMtoCROCCable(uint CRIMAddress)
        //    {
        //        CRIMAddr = CRIMAddress;
        //        CROCAddresses = new List<uint>(4);
        //    }
        //    public uint CRIMAddress { get { return CRIMAddr; } }
        }
        private void FindCRIMtoCROCCables(List<CRIM> CRIMs, List<CROC> CROCs, List<CRIMtoCROCCable> CRIMtoCROCCables)
        {
        //    CRIMtoCROCCables.Clear();
        //    lock (this)
        //    {
        //        vmeDone.WaitOne();
        //        try
        //        {
        //            foreach (CRIM theCrim in CRIMs)
        //            {
        //                CRIM.TimingModes theCrimTimingMode = theCrim.TimingMode;
        //                theCrim.TimingMode = CRIM.TimingModes.External;
        //                bool foundCable = false;
        //                CRIMtoCROCCable theCRIMtoCROCCable = new CRIMtoCROCCable(theCrim.BaseAddress);
        //                foreach (CROC theCROC in CROCs)
        //                {
        //                    CROC.ClockModes theCrocClockMode = theCROC.ClockMode;
        //                    theCROC.ClockMode = CROC.ClockModes.External;
        //                    foreach (CROCFrontEndChannel theChannel in theCROC.ChannelList)
        //                    {
        //                        foundCable = false;
        //                        if (theChannel.ChainBoards.Count != 0)
        //                        {
        //                            //found one channel with some FEs in the loop
        //                            FPGAFrame theFrame = new FPGAFrame(theChannel.ChainBoards[0], Frame.FPGAFunctions.Read, new FrameID());

        //                            theFrame.Send(theChannel);
        //                            theFrame.Receive();
        //                            uint currentGateTimeStamp = theFrame.GateTimeStamp;

        //                            theCrim.StartGate();
        //                            theCrim.EndGate();

        //                            theFrame.Send(theChannel);
        //                            theFrame.Receive();
        //                            uint newGateTimeStamp = theFrame.GateTimeStamp;

        //                            if (currentGateTimeStamp != newGateTimeStamp)
        //                            {
        //                                foundCable = true;
        //                                theCRIMtoCROCCable.CROCAddresses.Add(theCROC.BaseAddress);
        //                                lblStatus.Text = string.Format("\nFound CRIM to CROC cable from {0} to {1}", theCrim.Description, theCROC.Description);
        //                                richTextBoxDescription.AppendText(lblStatus.Text + "\n");
        //                                Metadata.MetaData.log.AddToLog(lblStatus.Text);
        //                                break;
        //                            }
        //                        }
        //                    }
        //                    //restore the original CROC settings
        //                    theCROC.ClockMode = theCrocClockMode;
        //                }
        //                if (foundCable) CRIMtoCROCCables.Add(theCRIMtoCROCCable);
        //                //restore the original CRIM settings
        //                theCrim.TimingMode = theCrimTimingMode;
        //            }
        //        }
        //        catch (Exception e)
        //        {
        //            lblStatus.Text = "\nError while finding CRIM to CROC cables...";
        //            richTextBoxDescription.AppendText(lblStatus.Text + "\n" + e.Message);
        //            Metadata.MetaData.log.AddToLog(lblStatus.Text + "\n" + e.Message);
        //        }
        //        finally
        //        {
        //            vmeDone.Set();
        //        }
        //    }
        }

        private void UpdateTree()
        {
            treeView1.Nodes.Clear();
            CRIMnodes.Clear();
            CROCnodes.Clear();
            CHnodes.Clear();
            FEnodes.Clear();
            V1720nodes.Clear();
            //create (new) root CRIM nodes
            foreach (CRIM crim in CRIMModules)
            {
                CRIMnode crimn = new CRIMnode(crim);   //create new CRIMnode : TreeNode
                CRIMnodes.Add(crimn);                  //add to the list
                treeView1.Nodes.Add(crimn);            //add to the tree
            }
            //create (new) root CROC nodes
            foreach (CROC croc in CROCModules)
            {
                CROCnode crocn = new CROCnode(croc);   //create new CROCnode : TreeNode
                CROCnodes.Add(crocn);                  //add to the list
                treeView1.Nodes.Add(crocn);            //add to the tree
                foreach (CHnode chn in crocn.CHnodes)
                {
                    CHnodes.Add(chn);                   //add to the list
                    foreach (FEnode fen in chn.FEnodes)
                    {
                        FEnodes.Add(fen);               //add to the list
                    }
                }
            }
            //create (new) root V1720 nodes
            foreach (V1720 digitizer in V1720Modules)
            {
                V1720node v1720n = new V1720node(digitizer);    //create new V1720node : TreeNode
                V1720nodes.Add(v1720n);                         //add to the list
                treeView1.Nodes.Add(v1720n);                    //add to the tree
            }
        }

        private void ClearControl(Control c)
        {
            if (c is TextBox)
                ((TextBox)c).Text = "";
            if ((c is Label) & (c.Name.Substring(0, 3) == "lbl"))
                ((Label)c).Text = "";
            if (c is ComboBox)
                ((ComboBox)c).SelectedIndex = -1;
            if (c is CheckBox)
                ((CheckBox)c).Checked = false;
            if (c is RichTextBox)
                ((RichTextBox)c).Clear();
        }

        private void greenPathsToolStripMenuItem_Click(object sender, EventArgs e)
        {
            ExpandFENodePaths(Color.Green);
        }

        private void bluePathsToolStripMenuItem_Click(object sender, EventArgs e)
        {
            ExpandFENodePaths(Color.Blue);
        }

        private void redPathsToolStripMenuItem_Click(object sender, EventArgs e)
        {
            ExpandFENodePaths(Color.Red);
        }

        private void ExpandFENodePaths(Color nodeColor)
        {
            MessageBox.Show("Under construction...");
            //treeView1.CollapseAll();
            //AppendDescription = true;
            //richTextBoxDescription.Clear();
            //if (FENodes != null)
            //{
            //    foreach (TreeNode fenode in FENodes)
            //    {
            //        if (((FEdev)fenode.Tag).StatusRGB == nodeColor.ToArgb())
            //        {
            //            //TreeViewEventArgs et = new TreeViewEventArgs(fenode, TreeViewAction.Expand);
            //            //treeView1_AfterSelect(null, et);
            //            treeView1.SelectedNode = fenode;
            //            fenode.Expand();
            //        }
            //    }
            //}
            //AppendDescription = false;
        }

        private void expandAllToolStripMenuItem_Click(object sender, EventArgs e)
        {
            treeView1.ExpandAll();
        }

        private void collapseAllToolStripMenuItem_Click(object sender, EventArgs e)
        {
            treeView1.CollapseAll();
        }

        private void toolStripMenuItemUpdateStatusString_Click(object sender, EventArgs e)
        {
            MessageBox.Show("Under construction...");
            //if (treeView1.Nodes.Count != 0)
            //{
            //    if (treeView1.SelectedNode is FENode)
            //    {
            //        ((FEdev)treeView1.SelectedNode.Tag).StatusString = richTextBoxDescription.Text;

            //    }
            //}
        }

        private void AdvancedGUI(Button sender, params Control[] slaves)
        {
            if (sender.Text == "Show Advanced GUI")
            {
                sender.Text = "Show Default GUI";
                foreach (Control cntrl in slaves)
                    cntrl.Visible = true;
                return;
            }
            if (sender.Text == "Show Default GUI")
            {
                sender.Text = "Show Advanced GUI";
                foreach (Control cntrl in slaves)
                    cntrl.Visible = false;
                return;
            }
        }

        #region Methods for filling info classes before they are serialized

        private void GetMinervaDevicesInfo()
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    minervaDevicesInfo.CRIMs.Clear();
                    minervaDevicesInfo.CROCs.Clear();
                    richTextBoxDescription.AppendText("\nGetting hardware...\n");
                    prgStatus.Maximum = CRIMModules.Count;
                    int prg = 0;
                    foreach (CRIM crim in CRIMModules)
                    {
                        richTextBoxDescription.AppendText(crim.Description + " ...");
                        ProgressReport(null, new ProgressChangedEventArgs(++prg, string.Format("{0} Getting", crim.Description)));
                        CRIMInfo crimInfo = new CRIMInfo();
                        GetCRIMInfo(crimInfo, crim);
                        minervaDevicesInfo.CRIMs.Add(crimInfo);
                        richTextBoxDescription.AppendText("done\n");
                    }
                    prgStatus.Maximum = CROCModules.Count;
                    prg = 0;
                    foreach (CROC croc in CROCModules)
                    {
                        richTextBoxDescription.AppendText(croc.Description + " ...");
                        ProgressReport(null, new ProgressChangedEventArgs(++prg, string.Format("{0} Getting", croc.Description)));
                        CROCInfo crocInfo = new CROCInfo();
                        GetCROCInfo(crocInfo, croc);
                        minervaDevicesInfo.CROCs.Add(crocInfo);
                        richTextBoxDescription.AppendText("\ndone\n");
                    }
                }
                catch (Exception e)
                {
                    lblStatus.Text = "Error while GetMinervaDevicesInfo()...";
                    UserAlert(lblStatus.Text + "\n" + e.Message + "\nOperation aborted\nPLEASE TRY AGAIN...\n");
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void GetVMEDeviceInfo(VMEDeviceInfo vmeDeviceInfo, VMEDevice vmeDevice)
        {
            vmeDeviceInfo.AddressModifier = vmeDevice.AddressModifier;
            vmeDeviceInfo.BaseAddress = vmeDevice.BaseAddress;
            //vmeDeviceInfo.Controller = vmeDevice.Controller;
            vmeDeviceInfo.ControllerBoardNumber = vmeDevice.Controller.BoardNumber;
            vmeDeviceInfo.ControllerLinkNumber = vmeDevice.Controller.LinkNumber;
            vmeDeviceInfo.DataWidth = vmeDevice.DataWidth;
            vmeDeviceInfo.Description = vmeDevice.Description;
            vmeDeviceInfo.IsInitialized = vmeDevice.IsInitialized;
            vmeDeviceInfo.SwappedDataWidth = vmeDevice.SwappedDataWidth;
        }

        private void GetCRIMInfo(CRIMInfo crimInfo, CRIM crim)
        {
            try
            {
                GetVMEDeviceInfo(crimInfo, crim);
                crimInfo.CRCEnabled = crim.CRCEnabled;
                crimInfo.Enabled = crim.Enabled;
                crimInfo.Frequency = crim.Frequency;
                crimInfo.GateWidth = crim.GateWidth;
                crimInfo.InterruptMask = crim.InterruptMask;
                crimInfo.InterruptStatus = crim.InterruptStatus;
                crimInfo.IRQLevel = crim.IRQLevel;
                crimInfo.RetransmitEnabled = crim.RetransmitEnabled;
                crimInfo.SendMessageEnabled = crim.SendMessageEnabled;
                crimInfo.TCALBDelay = crim.TCALBDelay;
                //crimInfo.Register = crim.this
                crimInfo.TimingCommandReceived = crim.TimingCommandReceived;
                crimInfo.TimingMode = crim.TimingMode;
                GetChannelInfo(crimInfo.CRIMChannelInfo, (IFrontEndChannel)crim.Channel);
            }
            catch (Exception e)
            {
                throw new Exception(crim.Description + " thrown the following exception :\n" + e.Message);
            }
        }

        private void GetCROCInfo(CROCInfo crocInfo, CROC croc)
        {
            try
            {
                GetVMEDeviceInfo(crocInfo, croc);
                crocInfo.ClockMode = croc.ClockMode;
                crocInfo.ResetAndTestMaskRegister = croc.ResetAndTestMaskRegister;
                crocInfo.TestPulseDelayEnabled = croc.TestPulseDelayEnabled;
                crocInfo.TestPulseDelayValue = croc.TestPulseDelayValue;
                crocInfo.TimingSetupRegister = croc.TimingSetupRegister;
            }
            catch (Exception e)
            {
                throw new Exception(croc.Description + " thrown the following exception :\n" + e.Message);
            }
            foreach (CROCFrontEndChannel channel in croc.ChannelList)
            {
                CROCChannelInfo crocChannelInfo = new CROCChannelInfo();
                GetCROCChannelInfo(crocChannelInfo, channel);
                crocInfo.CROCChannels.Add(crocChannelInfo);
            }
        }

        private void GetChannelInfo(ChannelInfo channelInfo, IFrontEndChannel channel)
        {
            GetVMEDeviceInfo(channelInfo, (VMEDevice)channel);
            //All the following channel members are get accessors only
            channelInfo.ChannelNumber = channel.ChannelNumber;
            channelInfo.CRCError = channel.CRCError;
            channelInfo.DeserializerLock = channel.DeserializerLock;
            channelInfo.MessageReceived = channel.MessageReceived;
            channelInfo.MessageSent = channel.MessageSent;
            channelInfo.PLLOk = channel.PLLOk;
            channelInfo.Pointer = channel.Pointer;
            channelInfo.ReceiveBufferIsFull = channel.ReceiveBufferIsFull;
            channelInfo.RFPresent = channel.RFPresent;
            channelInfo.SendBufferIsEmpty = channel.SendBufferIsEmpty;
            channelInfo.SendBufferIsFull = channel.SendBufferIsFull;
            channelInfo.SerializerSynch = channel.SerializerSynch;
            channelInfo.StatusRegister = channel.StatusRegister;
            channelInfo.TimeoutError = channel.TimeoutError;
        }

        private void GetCROCChannelInfo(CROCChannelInfo crocChannelInfo, CROCFrontEndChannel crocChannel)
        {
            try
            {
                GetChannelInfo(crocChannelInfo, crocChannel);
                crocChannelInfo.ResetEnabled = crocChannel.ResetEnabled;
                crocChannelInfo.TestPulseEnabled = crocChannel.TestPulseEnabled;
            }
            catch (Exception e)
            {
                throw new Exception(crocChannel.Description + " thrown the following exception :\n" + e.Message);
            }
            foreach (Frame.Addresses febAddress in crocChannel.ChainBoards)
            {
                richTextBoxDescription.AppendText("\n" + febAddress + " on " + crocChannel.Description + " ...");
                ChainBoardInfo chainBoardInfo = new ChainBoardInfo();
                GetChainBoardInfo(chainBoardInfo, crocChannel, febAddress);
                crocChannelInfo.ChainBoards.Add(chainBoardInfo);
                richTextBoxDescription.AppendText("done");
            }
        }

        private void GetChainBoardInfo(ChainBoardInfo chainBoardInfo, CROCFrontEndChannel crocChannel, Frame.Addresses febAddress)
        {
            try
            {
                chainBoardInfo.BoardAddress = febAddress;
                GetFPGAFrameInfo(chainBoardInfo.fpgaFrameInfo, crocChannel, febAddress);
                //TRIPFrameInfo tripFrameInfo = new TRIPFrameInfo();
                foreach (Frame.TRiPFunctions tripFunction in Enum.GetValues(typeof(Frame.TRiPFunctions)))
                {
                    if (tripFunction == Frame.TRiPFunctions.All | tripFunction == Frame.TRiPFunctions.None) continue;
                    TRIPFrameInfo tripFrameInfo = new TRIPFrameInfo();
                    GetTRIPFrameInfo(tripFrameInfo, crocChannel, febAddress, tripFunction);
                    chainBoardInfo.tripFrameInfoList.Add(tripFrameInfo);
                }
            }
            catch (Exception e)
            {
                throw new Exception(crocChannel.Description + " : " + febAddress + " thrown the following exception :\n" + e.Message);
            }
        }

        private void GetFrameInfo(FrameInfo frameInfo, Frame frame)
        {
            // These Frame class memeber are read only.  No SetFrameInfo function since members are read only

            //frameInfo.CheckResponseHeaderFlags = frame.CheckResponseHeaderFlags;
            frameInfo.Device = frame.Device;
            frameInfo.Function = frame.Function;
            frameInfo.ID = frame.ID;
            //frameInfo.Message = frame.Message; // Serialization of byte array needs to be resolved
            frameInfo.MessageSent = frame.MessageSent;
            frameInfo.Recipient = frame.Recipient;
            //frameInfo.Response = frame.Response; // Serialization of byte array needs to be resolved
            frameInfo.ResponseCRCOK = frame.ResponseCRCOK;
            frameInfo.ResponseDeviceOK = frame.ResponseDeviceOK;
            frameInfo.ResponseDirection = frame.ResponseDirection;
            frameInfo.ResponseEndHeaderOK = frame.ResponseEndHeaderOK;
            frameInfo.ResponseFunctionOK = frame.ResponseFunctionOK;
            frameInfo.ResponseHeaderOK = frame.ResponseHeaderOK;
            frameInfo.ResponseMaxLenBad = frame.ResponseMaxLenBad;
            frameInfo.ResponseNAHeaderBad = frame.ResponseNAHeaderBad;
            frameInfo.ResponseReceived = frame.ResponseReceived;
            frameInfo.ResponseSecondStartBad = frame.ResponseSecondStartBad;
            frameInfo.Timestamp = frame.Timestamp;
        }

        private void GetFPGAFrameInfo(FPGAFrameInfo fpgaFrameInfo, CROCFrontEndChannel crocChannel, Frame.Addresses febAddress)
        {
            ushort frameID = ConstructFrameID(crocChannel, febAddress);
            FPGAFrame fpgaFrame = new FPGAFrame(febAddress, Frame.FPGAFunctions.Read, new FrameID(frameID));
            fpgaFrame.Send(crocChannel);
            fpgaFrame.Receive();

            // GetFrameInfo(fpgaFrameInfo, fpgaFrame); // Uncomment to include FrameInfo
            fpgaFrameInfo.BoardID = fpgaFrame.BoardID;
            fpgaFrameInfo.CosmicTrig = fpgaFrame.CosmicTrig;
            fpgaFrameInfo.DCM1Lock = fpgaFrame.DCM1Lock;
            fpgaFrameInfo.DCM1NoClock = fpgaFrame.DCM1NoClock;
            fpgaFrameInfo.DCM2Lock = fpgaFrame.DCM2Lock;
            fpgaFrameInfo.DCM2NoClock = fpgaFrame.DCM2NoClock;
            fpgaFrameInfo.DCM2PhaseDone = fpgaFrame.DCM2PhaseDone;
            fpgaFrameInfo.DCM2PhaseTotal = fpgaFrame.DCM2PhaseTotal;
            fpgaFrameInfo.DiscrimEnableMaskTrip0 = fpgaFrame.DiscrimEnableMaskTrip0;
            fpgaFrameInfo.DiscrimEnableMaskTrip1 = fpgaFrame.DiscrimEnableMaskTrip1;
            fpgaFrameInfo.DiscrimEnableMaskTrip2 = fpgaFrame.DiscrimEnableMaskTrip2;
            fpgaFrameInfo.DiscrimEnableMaskTrip3 = fpgaFrame.DiscrimEnableMaskTrip3;
            fpgaFrameInfo.ExtTriggFound = fpgaFrame.ExtTriggFound;    //get only
            fpgaFrameInfo.ExtTriggRearm = fpgaFrame.ExtTriggRearm;
            fpgaFrameInfo.FirmwareVersion = fpgaFrame.FirmwareVersion;
            fpgaFrameInfo.GateLength = fpgaFrame.GateLength;
            fpgaFrameInfo.GateStart = fpgaFrame.GateStart;
            fpgaFrameInfo.GateTimeStamp = fpgaFrame.GateTimeStamp;
            fpgaFrameInfo.HVActual = fpgaFrame.HVActual;
            fpgaFrameInfo.HVControl = fpgaFrame.HVControl;
            fpgaFrameInfo.HVEnabled = fpgaFrame.HVEnabled;
            fpgaFrameInfo.HVManual = fpgaFrame.HVManual;
            fpgaFrameInfo.HVNumAvg = fpgaFrame.HVNumAvg;
            fpgaFrameInfo.HVPeriodAuto = fpgaFrame.HVPeriodAuto;
            fpgaFrameInfo.HVPeriodManual = fpgaFrame.HVPeriodManual;
            fpgaFrameInfo.HVPulseWidth = fpgaFrame.HVPulseWidth;
            fpgaFrameInfo.HVTarget = fpgaFrame.HVTarget;
            fpgaFrameInfo.InjectCount = fpgaFrame.InjectCount;
            fpgaFrameInfo.InjectDACDone = fpgaFrame.InjectDACDone;
            fpgaFrameInfo.InjectDACMode = fpgaFrame.InjectDACMode;
            fpgaFrameInfo.InjectDACStart = fpgaFrame.InjectDACStart;
            fpgaFrameInfo.InjectDACValue = fpgaFrame.InjectDACValue;
            fpgaFrameInfo.InjectEnable = Convert.ToByte(fpgaFrame.InjectEnable.Data);
            fpgaFrameInfo.InjectPhase = fpgaFrame.InjectPhase;
            fpgaFrameInfo.InjectRange = fpgaFrame.InjectRange;
            fpgaFrameInfo.PhaseCount = fpgaFrame.PhaseCount;
            fpgaFrameInfo.PhaseIncrement = fpgaFrame.PhaseIncrement;
            fpgaFrameInfo.PhaseSpare = fpgaFrame.PhaseSpare;
            fpgaFrameInfo.PhaseStart = fpgaFrame.PhaseStart;
            // fpgaFrameInfo.PhysicalRegisters = fpgaFrame.PhysicalRegisters; // Serialization of byte array needs to be resolved
            fpgaFrameInfo.Temperature = fpgaFrame.Temperature;
            fpgaFrameInfo.TestPulse2Bit = fpgaFrame.TestPulse2Bit;
            fpgaFrameInfo.TestPulseCount = fpgaFrame.TestPulseCount;
            fpgaFrameInfo.Timer = fpgaFrame.Timer;
            fpgaFrameInfo.TripPowerOff = fpgaFrame.TripPowerOff;
            fpgaFrameInfo.TripXCompEnc = fpgaFrame.TripXCompEnc;
            fpgaFrameInfo.VXOMuxXilinx = fpgaFrame.VXOMuxXilinx;
        }

        private void GetTRIPFrameInfo(TRIPFrameInfo tripFrameInfo, CROCFrontEndChannel crocChannel, Frame.Addresses febAddress, TripTFrame.TRiPFunctions tripFunction)
        {
            ushort frameID = ConstructFrameID(crocChannel, febAddress);
            TripTFrame tripFrame = new TripTFrame(febAddress, tripFunction, new FrameID(frameID));
            tripFrame.Send(crocChannel);
            tripFrame.Receive();

            // GetFrameInfo(tripFrameInfo, tripFrame); // Uncomment to include FrameInfo
            tripFrameInfo.TripID = (byte)(tripFunction - 2);
            tripFrameInfo.RegisterIBP = (uint)tripFrame[TripTFrame.LogicalRegisters.IBP];
            tripFrameInfo.RegisterIBBNFALL = (uint)tripFrame[TripTFrame.LogicalRegisters.IBBNFoll];
            tripFrameInfo.RegisterIFF = (uint)tripFrame[TripTFrame.LogicalRegisters.IFF];
            tripFrameInfo.RegisterIBPIFF1REF = (uint)tripFrame[TripTFrame.LogicalRegisters.IBPIFF1REF];
            tripFrameInfo.RegisterIBPOPAMP = (uint)tripFrame[TripTFrame.LogicalRegisters.IBPOPAMP];
            tripFrameInfo.RegisterIB_T = (uint)tripFrame[TripTFrame.LogicalRegisters.IBPFoll2];
            tripFrameInfo.RegisterIFFP2 = (uint)tripFrame[TripTFrame.LogicalRegisters.IFF2];
            tripFrameInfo.RegisterIBCOMP = (uint)tripFrame[TripTFrame.LogicalRegisters.IBCOMP];
            tripFrameInfo.RegisterVREF = (uint)tripFrame[TripTFrame.LogicalRegisters.VREF];
            tripFrameInfo.RegisterVTH = (uint)tripFrame[TripTFrame.LogicalRegisters.VTH];
            tripFrameInfo.RegisterGAIN = (uint)tripFrame[TripTFrame.LogicalRegisters.GAIN];
            tripFrameInfo.RegisterPIPEDEL = (uint)tripFrame[TripTFrame.LogicalRegisters.PIPEDEL];
            tripFrameInfo.RegisterIRSEL = (uint)tripFrame[TripTFrame.LogicalRegisters.IRSEL];
            tripFrameInfo.RegisterIWSEL = (uint)tripFrame[TripTFrame.LogicalRegisters.IWSEL];
            tripFrameInfo.RegisterINJEX0 = (uint)(tripFrame[TripTFrame.LogicalRegisters.INJECT] & 0x1);
            tripFrameInfo.RegisterINJB0 = (uint)(tripFrame[TripTFrame.LogicalRegisters.INJECT] & 0x1FE) >> 1;
            tripFrameInfo.RegisterINJB1 = (uint)(tripFrame[TripTFrame.LogicalRegisters.INJECT] & 0x1FE00) >> 9;
            tripFrameInfo.RegisterINJB2 = (uint)(tripFrame[TripTFrame.LogicalRegisters.INJECT] & 0x1FE0000) >> 17;
            tripFrameInfo.RegisterINJB3 = (uint)(tripFrame[TripTFrame.LogicalRegisters.INJECT] & 0x1FE000000) >> 25;
            tripFrameInfo.RegisterINJEX33 = (uint)(tripFrame[TripTFrame.LogicalRegisters.INJECT] & 0x200000000) >> 33;
        }

        private ushort ConstructFrameID(CROCFrontEndChannel crocChannel, Frame.Addresses febAddress)
        {
            return (ushort)(
                Convert.ToUInt16(febAddress.ToString().Substring(2)) << 12 |
                Convert.ToUInt16(crocChannel.ChannelNumber) << 10 |
                Convert.ToUInt16((crocChannel.BaseAddress >> 16) << 2));
        }

        #endregion

        #region Methods for applying settings from XML file to hardware

        private void SetMinervaDevicesInfo()
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    richTextBoxDescription.AppendText("\nUpdating hardware\n"); 
                    prgStatus.Maximum = CRIMModules.Count;
                    int prg = 0;
                    foreach (CRIMInfo crimInfo in xmlInfo.CRIMs)
                    {
                        foreach (CRIM crim in CRIMModules)
                        {
                            if (crimInfo.BaseAddress == crim.BaseAddress)
                            {
                                richTextBoxDescription.AppendText(crim.Description + " ...");
                                ProgressReport(null, new ProgressChangedEventArgs(++prg, string.Format("{0} Updating", crim.Description)));
                                SetCRIMInfo(crim, crimInfo);
                                richTextBoxDescription.AppendText("done\n");
                                break;
                            }
                        }
                    }
                    prgStatus.Maximum = CROCModules.Count;
                    prg = 0;
                    foreach (CROCInfo crocInfo in xmlInfo.CROCs)
                    {
                        foreach (CROC croc in CROCModules)
                        {
                            if (crocInfo.BaseAddress == croc.BaseAddress)
                            {
                                richTextBoxDescription.AppendText(croc.Description + " ...");
                                ProgressReport(null, new ProgressChangedEventArgs(++prg, string.Format("{0} Updating", croc.Description)));
                                SetCROCInfo(croc, crocInfo);
                                richTextBoxDescription.AppendText("\ndone\n");
                                break;
                            }
                        }
                    }
                }
                catch (Exception e)
                {
                    lblStatus.Text = "Error in SetMinervaDevicesInfo()...";
                    UserAlert(lblStatus.Text + "\n" + e.Message + "\nOperation aborted\nPLEASE TRY AGAIN...\n");
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void SetVMEDeviceInfo(VMEDevice vmeDevice, VMEDeviceInfo vmeDeviceInfo)
        {
            vmeDevice.AddressModifier = vmeDeviceInfo.AddressModifier;
            vmeDevice.DataWidth = vmeDeviceInfo.DataWidth;
            vmeDevice.SwappedDataWidth = vmeDeviceInfo.SwappedDataWidth;
        }

        private void SetCRIMInfo(CRIM crim, CRIMInfo crimInfo)
        {
            try
            {
                SetVMEDeviceInfo(crim, crimInfo);
                crim.CRCEnabled = crimInfo.CRCEnabled;
                crim.Enabled = crimInfo.Enabled;
                crim.Frequency = crimInfo.Frequency;
                crim.GateWidth = crimInfo.GateWidth;
                crim.InterruptMask = crimInfo.InterruptMask;
                crim.InterruptStatus = crimInfo.InterruptStatus;
                crim.IRQLevel = crimInfo.IRQLevel;
                crim.RetransmitEnabled = crimInfo.RetransmitEnabled;
                crim.SendMessageEnabled = crimInfo.SendMessageEnabled;
                crim.TCALBDelay = crimInfo.TCALBDelay;
                crim.TimingMode = crimInfo.TimingMode;
                //SetChannelInfo((IFrontEndChannel)crim.Channel, crimInfo.CRIMChannelInfo); Cannot set the value of any members in the CRIMFrontEndChannel class
            }
            catch (Exception e)
            {
                throw new Exception(crim.Description + " thrown the following exception :\n" + e.Message);
            }
        }

        private void SetCROCInfo(CROC croc, CROCInfo crocInfo)
        {
            try
            {
                SetVMEDeviceInfo(croc, crocInfo);
                croc.ClockMode = crocInfo.ClockMode;
                croc.ResetAndTestMaskRegister = crocInfo.ResetAndTestMaskRegister;
                croc.TestPulseDelayEnabled = crocInfo.TestPulseDelayEnabled;
                croc.TestPulseDelayValue = crocInfo.TestPulseDelayValue;
                croc.TimingSetupRegister = crocInfo.TimingSetupRegister;
                //croc.ChannelResetRegister = ?
                //croc.FastCommandRegister = ?
                //croc.TestPulseRegister = ?
            }
            catch (Exception e)
            {
                throw new Exception(croc.Description + " thrown the following exception :\n" + e.Message);
            }
            foreach (CROCFrontEndChannel channel in croc.ChannelList)
            {
                SetCROCChannelInfo(channel, crocInfo.CROCChannels[(int)channel.ChannelNumber - 1]);
            }
        }

        private void SetCROCChannelInfo(CROCFrontEndChannel crocChannel, CROCChannelInfo crocChannelInfo)
        {
            try
            {
                SetVMEDeviceInfo((VMEDevice)crocChannel, crocChannelInfo);
                crocChannel.ResetEnabled = crocChannelInfo.ResetEnabled;
                crocChannel.TestPulseEnabled = crocChannelInfo.TestPulseEnabled;
            }
            catch (Exception e)
            {
                throw new Exception(crocChannel.Description + " thrown the following exception :\n" + e.Message);
            }
            foreach (ChainBoardInfo chainBoardInfo in crocChannelInfo.ChainBoards)
            {
                foreach (Frame.Addresses febAddress in crocChannel.ChainBoards)
                {
                    if (chainBoardInfo.BoardAddress == febAddress)
                    {
                        richTextBoxDescription.AppendText("\n" + febAddress + " on " + crocChannel.Description + " ...");
                        SetChainBoardInfo(chainBoardInfo, crocChannel, febAddress);
                        richTextBoxDescription.AppendText("done");
                        break;
                    }
                }
            }
        }

        private void SetChainBoardInfo(ChainBoardInfo chainBoardInfo, CROCFrontEndChannel crocChannel, Frame.Addresses febAddress)
        {
            try
            {
                SetFPGAFrameInfo(chainBoardInfo.fpgaFrameInfo, crocChannel, febAddress);
                foreach (TRIPFrameInfo tripFrameInfo in chainBoardInfo.tripFrameInfoList)
                {
                    Frame.TRiPFunctions tripFunction = (Frame.TRiPFunctions)(tripFrameInfo.TripID + 2);
                    SetTRIPFrameInfo(tripFrameInfo, crocChannel, febAddress, tripFunction);
                }
            }
            catch (Exception e)
            {
                throw new Exception(crocChannel.Description + " : " + febAddress + " thrown the following exception :\n" + e.Message);
            }
        }

        private void SetFPGAFrameInfo(FPGAFrameInfo fpgaFrameInfo, CROCFrontEndChannel crocChannel, Frame.Addresses febAddress)
        {
            ushort frameID = ConstructFrameID(crocChannel, febAddress);
            FPGAFrame fpgaFrame = new FPGAFrame(febAddress, Frame.FPGAFunctions.Write, new FrameID(frameID));

            // Read/Write members only
            fpgaFrame.CosmicTrig = fpgaFrameInfo.CosmicTrig;
            fpgaFrame.DiscrimEnableMaskTrip0 = fpgaFrameInfo.DiscrimEnableMaskTrip0;
            fpgaFrame.DiscrimEnableMaskTrip1 = fpgaFrameInfo.DiscrimEnableMaskTrip1;
            fpgaFrame.DiscrimEnableMaskTrip2 = fpgaFrameInfo.DiscrimEnableMaskTrip2;
            fpgaFrame.DiscrimEnableMaskTrip3 = fpgaFrameInfo.DiscrimEnableMaskTrip3;
            fpgaFrame.ExtTriggRearm = fpgaFrameInfo.ExtTriggRearm;
            fpgaFrame.GateLength = fpgaFrameInfo.GateLength;
            fpgaFrame.GateStart = fpgaFrameInfo.GateStart;
            fpgaFrame.HVEnabled = fpgaFrameInfo.HVEnabled;
            fpgaFrame.HVManual = fpgaFrameInfo.HVManual;
            fpgaFrame.HVNumAvg = fpgaFrameInfo.HVNumAvg;
            fpgaFrame.HVPeriodManual = fpgaFrameInfo.HVPeriodManual;
            fpgaFrame.HVPulseWidth = fpgaFrameInfo.HVPulseWidth;
            fpgaFrame.HVTarget = fpgaFrameInfo.HVTarget;
            fpgaFrame.InjectCount = fpgaFrameInfo.InjectCount; // Serialization of byte array needs to be resolved
            fpgaFrame.InjectDACMode = fpgaFrameInfo.InjectDACMode;
            fpgaFrame.InjectDACStart = fpgaFrameInfo.InjectDACStart;
            fpgaFrame.InjectDACValue = fpgaFrameInfo.InjectDACValue;
            fpgaFrame.InjectEnable = new BitVector32((Int32)fpgaFrameInfo.InjectEnable);
            fpgaFrame.InjectPhase = fpgaFrameInfo.InjectPhase;
            fpgaFrame.InjectRange = fpgaFrameInfo.InjectRange;
            fpgaFrame.PhaseCount = fpgaFrameInfo.PhaseCount;
            fpgaFrame.PhaseIncrement = fpgaFrameInfo.PhaseIncrement;
            fpgaFrame.PhaseSpare = fpgaFrameInfo.PhaseSpare;
            fpgaFrame.PhaseStart = fpgaFrameInfo.PhaseStart;
            fpgaFrame.Timer = fpgaFrameInfo.Timer;
            fpgaFrame.TripPowerOff = fpgaFrameInfo.TripPowerOff;
            fpgaFrame.VXOMuxXilinx = fpgaFrameInfo.VXOMuxXilinx;

            fpgaFrame.Send(crocChannel);
            fpgaFrame.Receive();
        }

        private void SetTRIPFrameInfo(TRIPFrameInfo tripFrameInfo, CROCFrontEndChannel crocChannel, Frame.Addresses febAddress, TripTFrame.TRiPFunctions tripFunction)
        {
            ushort frameID = ConstructFrameID(crocChannel, febAddress);
            TripTFrame tripFrame = new TripTFrame(febAddress, tripFunction, new FrameID(frameID));

            tripFrame[TripTFrame.LogicalRegisters.IBP] = tripFrameInfo.RegisterIBP;
            tripFrame[TripTFrame.LogicalRegisters.IBBNFoll] = tripFrameInfo.RegisterIBBNFALL;
            tripFrame[TripTFrame.LogicalRegisters.IFF] = tripFrameInfo.RegisterIFF;
            tripFrame[TripTFrame.LogicalRegisters.IBPIFF1REF] = tripFrameInfo.RegisterIBPIFF1REF;
            tripFrame[TripTFrame.LogicalRegisters.IBPOPAMP] = tripFrameInfo.RegisterIBPOPAMP;
            tripFrame[TripTFrame.LogicalRegisters.IBPFoll2] = tripFrameInfo.RegisterIB_T;
            tripFrame[TripTFrame.LogicalRegisters.IFF2] = tripFrameInfo.RegisterIFFP2;
            tripFrame[TripTFrame.LogicalRegisters.IBCOMP] = tripFrameInfo.RegisterIBCOMP;
            tripFrame[TripTFrame.LogicalRegisters.VREF] = tripFrameInfo.RegisterVREF;
            tripFrame[TripTFrame.LogicalRegisters.VTH] = tripFrameInfo.RegisterVTH;
            tripFrame[TripTFrame.LogicalRegisters.GAIN] = tripFrameInfo.RegisterGAIN;
            tripFrame[TripTFrame.LogicalRegisters.PIPEDEL] = tripFrameInfo.RegisterPIPEDEL;
            tripFrame[TripTFrame.LogicalRegisters.IRSEL] = tripFrameInfo.RegisterIRSEL;
            tripFrame[TripTFrame.LogicalRegisters.IWSEL] = tripFrameInfo.RegisterIWSEL;
            tripFrame[TripTFrame.LogicalRegisters.INJECT] = (tripFrameInfo.RegisterINJEX33 << 33) |
                (tripFrameInfo.RegisterINJB3 << 25) | (tripFrameInfo.RegisterINJB2 << 17) |
                (tripFrameInfo.RegisterINJB1 << 9) | (tripFrameInfo.RegisterINJB0 << 1) |
                tripFrameInfo.RegisterINJEX0;

            tripFrame.Send(crocChannel);
            tripFrame.Receive();
        }

        #endregion

        #region Methods for Write/Read to/from FPGA Registers

        private void btn_AllFEsFPGARegWrite_Click(object sender, EventArgs e)
        {
            FPGAFrame frameWriteAll = new FPGAFrame(Frame.Addresses.FE15, Frame.FPGAFunctions.Write, new FrameID());
            fpgaDevRegControl1.UpdateFPGALogicalRegArray();
            AssignFPGARegsCristianToDave(fpgaDevRegControl1, frameWriteAll);
            tabControl1.SelectTab(tabDescription.Name);
            richTextBoxDescription.Text = "Writing ALL FPGADevRegs with same data...\n\n";
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    foreach (CROC croc in CROCModules)
                    {
                        foreach (IFrontEndChannel channel in croc.ChannelList)
                        {
                            foreach (Frame.Addresses feb in channel.ChainBoards)
                            {
                                try
                                {
                                    FPGAFrame theFrame = new FPGAFrame(feb, Frame.FPGAFunctions.Write, new FrameID());
                                    theFrame.Registers = frameWriteAll.Registers;
                                    theFrame.Send(channel);
                                    theFrame.Receive();
                                    richTextBoxDescription.AppendText(channel.Description + ":" + feb +
                                        ": FPGADevRegs Write Success\n");
                                }
                                catch (Exception ex)
                                {
                                    richTextBoxDescription.AppendText(channel.Description + ":" + feb + ": Error: " + ex.Message + "\n");
                                }
                            }
                            richTextBoxDescription.AppendText("\n");
                        }
                    }
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                    richTextBoxDescription.AppendText("...Done\n");
                }
            }
        }

        private void btn_FPGARegWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    Frame.Addresses theBoard = (Frame.Addresses)(((FEnode)(theNode.Parent)).BoardID);
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Parent.Parent.Tag));
                    theChannel.Reset();
                    FPGAFrame theFrame = new FPGAFrame(theBoard, Frame.FPGAFunctions.Write, new FrameID());

                    fpgaDevRegControl1.UpdateFPGALogicalRegArray();
                    AssignFPGARegsCristianToDave(fpgaDevRegControl1, theFrame);

                    theFrame.Send(theChannel);
                    theFrame.Receive();
                    AssignFPGARegsDaveToCristian(theFrame, fpgaDevRegControl1);
                    fpgaDevRegControl1.UpdateFormControls();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_FPGARegRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    Frame.Addresses theBoard = (Frame.Addresses)(((FEnode)(theNode.Parent)).BoardID);
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Parent.Parent.Tag));
                    theChannel.Reset();
                    FPGAFrame theFrame = new FPGAFrame(theBoard, Frame.FPGAFunctions.Read, new FrameID());
                    theFrame.Send(theChannel);
                    theFrame.Receive();
                    AssignFPGARegsDaveToCristian(theFrame, fpgaDevRegControl1);
                    fpgaDevRegControl1.UpdateFormControls();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void AssignFPGARegsDaveToCristian(FPGAFrame theFrame, MinervaUserControls.FPGADevRegControl theFPGAControl)
        {
            theFPGAControl.RegisterTimer = theFrame.Timer;
            theFPGAControl.RegisterGateStart = theFrame.GateStart;
            theFPGAControl.RegisterGateLength = theFrame.GateLength;
            theFPGAControl.RegisterTripPowerOff = (uint)theFrame.TripPowerOff.Data;
            UInt32[] temp = new UInt32[6];
            for (int i = 0; i < 6; i++)
                temp[i] = (uint)theFrame.InjectCount[i];
            theFPGAControl.RegisterInjectCount = temp;
            theFPGAControl.RegisterInjectEnable = (uint)theFrame.InjectEnable.Data;
            theFPGAControl.RegisterInjectRange = theFrame.InjectRange;
            theFPGAControl.RegisterInjectPhase = theFrame.InjectPhase;
            theFPGAControl.RegisterInjectDACValue = theFrame.InjectDACValue;
            theFPGAControl.RegisterInjectDACMode = theFrame.InjectDACMode;
            theFPGAControl.RegisterInjectDACStart = Convert.ToUInt32(theFrame.InjectDACStart);
            theFPGAControl.RegisterInjectDACDone = Convert.ToUInt32(theFrame.InjectDACDone);
            theFPGAControl.RegisterHVEnabled = Convert.ToUInt32(theFrame.HVEnabled);
            theFPGAControl.RegisterHVTarget = theFrame.HVTarget;
            theFPGAControl.RegisterHVActual = theFrame.HVActual;
            theFPGAControl.RegisterHVControl = theFrame.HVControl;
            theFPGAControl.RegisterHVAutoManual = Convert.ToUInt32(theFrame.HVManual);
            theFPGAControl.RegisterVXOMuxSelect = Convert.ToUInt32(theFrame.VXOMuxXilinx);
            theFPGAControl.RegisterPhaseStart = Convert.ToUInt32(theFrame.PhaseStart);
            theFPGAControl.RegisterPhaseIncrement = Convert.ToUInt32(theFrame.PhaseIncrement);
            theFPGAControl.RegisterPhaseSpare = theFrame.PhaseSpare;
            theFPGAControl.RegisterPhaseTicks = theFrame.PhaseCount;
            theFPGAControl.RegisterDCM1Lock = Convert.ToUInt32(theFrame.DCM1Lock);
            theFPGAControl.RegisterDCM2Lock = Convert.ToUInt32(theFrame.DCM2Lock);
            theFPGAControl.RegisterDCM1NoClock = Convert.ToUInt32(theFrame.DCM1NoClock);
            theFPGAControl.RegisterDCM2NoClock = Convert.ToUInt32(theFrame.DCM2NoClock);
            theFPGAControl.RegisterDCM2PhaseDone = Convert.ToUInt32(theFrame.DCM2PhaseDone);
            theFPGAControl.RegisterDCM2PhaseTotal = theFrame.DCM2PhaseTotal;
            theFPGAControl.RegisterTestPulse2Bit = theFrame.TestPulse2Bit;
            theFPGAControl.RegisterTestPulseCount = theFrame.TestPulseCount;
            theFPGAControl.RegisterBoardID = theFrame.BoardID;
            theFPGAControl.RegisterFirmwareVersion = theFrame.FirmwareVersion;
            theFPGAControl.RegisterHVNumAvg = theFrame.HVNumAvg;
            theFPGAControl.RegisterHVPeriodManual = theFrame.HVPeriodManual;
            theFPGAControl.RegisterHVPeriodAuto = theFrame.HVPeriodAuto;
            theFPGAControl.RegisterHVPulseWidth = theFrame.HVPulseWidth;
            theFPGAControl.RegisterTemperature = theFrame.Temperature;
            theFPGAControl.RegisterTripXThreshold = theFrame.CosmicTrig;
            theFPGAControl.RegisterTripXComparators = theFrame.TripXCompEnc;
            theFPGAControl.RegisterExtTriggFound = theFrame.ExtTriggFound;                  // 08.08.2008 Cristian
            theFPGAControl.RegisterExtTriggRearm = theFrame.ExtTriggRearm;                  // 08.08.2008 Cristian
            theFPGAControl.RegisterDiscrimEnableMaskTrip0 = theFrame.DiscrimEnableMaskTrip0;// 10.30.2008 Cristian
            theFPGAControl.RegisterDiscrimEnableMaskTrip1 = theFrame.DiscrimEnableMaskTrip1;// 10.30.2008 Cristian
            theFPGAControl.RegisterDiscrimEnableMaskTrip2 = theFrame.DiscrimEnableMaskTrip2;// 10.30.2008 Cristian
            theFPGAControl.RegisterDiscrimEnableMaskTrip3 = theFrame.DiscrimEnableMaskTrip3;// 10.30.2008 Cristian
            theFPGAControl.RegisterGateTimeStamp = theFrame.GateTimeStamp;                  // 12.22.2008 Cristian
        }

        private void AssignFPGARegsCristianToDave(MinervaUserControls.FPGADevRegControl theFPGAControl, FPGAFrame theFrame)
        {
            theFrame.Timer = theFPGAControl.RegisterTimer;
            theFrame.GateStart = (ushort)theFPGAControl.RegisterGateStart;
            theFrame.GateLength = (ushort)theFPGAControl.RegisterGateLength;
            theFrame.TripPowerOff = new BitVector32((int)theFPGAControl.RegisterTripPowerOff);
            byte[] tempbyte = new byte[6];
            uint[] tempuint = new uint[6];
            tempuint = theFPGAControl.RegisterInjectCount;
            for (int i = 0; i < 6; i++)
                tempbyte[i] = (byte)tempuint[i];
            theFrame.InjectCount = tempbyte;
            theFrame.InjectEnable = new BitVector32((int)theFPGAControl.RegisterInjectEnable);
            theFrame.InjectRange = (byte)theFPGAControl.RegisterInjectRange;
            theFrame.InjectPhase = (byte)theFPGAControl.RegisterInjectPhase;

            theFrame.InjectDACValue = (ushort)theFPGAControl.RegisterInjectDACValue;
            theFrame.InjectDACMode = (byte)theFPGAControl.RegisterInjectDACMode;
            theFrame.InjectDACStart = Convert.ToBoolean(theFPGAControl.RegisterInjectDACStart);
            //theFrame.InjectDACDone = theFPGAControl.RegisterInjectDACDone;            READ ONLY
            theFrame.HVEnabled = Convert.ToBoolean(theFPGAControl.RegisterHVEnabled);
            theFrame.HVTarget = (ushort)theFPGAControl.RegisterHVTarget;
            //theFrame.HVActual = theFPGAControl.RegisterHVActual;                      READ ONLY
            //theFrame.HVControl = theFPGAControl.RegisterHVControl;                    READ ONLY
            theFrame.HVManual = Convert.ToBoolean(theFPGAControl.RegisterHVAutoManual);
            theFrame.VXOMuxXilinx = Convert.ToBoolean(theFPGAControl.RegisterVXOMuxSelect);
            theFrame.PhaseStart = Convert.ToBoolean(theFPGAControl.RegisterPhaseStart);
            theFrame.PhaseIncrement = Convert.ToBoolean(theFPGAControl.RegisterPhaseIncrement);
            theFrame.PhaseSpare = (byte)theFPGAControl.RegisterPhaseSpare;
            theFrame.PhaseCount = (byte)theFPGAControl.RegisterPhaseTicks;
            //theFrame.DCM1Lock = theFPGAControl.RegisterDCM1Lock;                      READ ONLY
            //theFrame.DCM2Lock = theFPGAControl.RegisterDCM2Lock;                      READ ONLY
            //theFrame.DCM1NoClock = theFPGAControl.RegisterDCM1NoClock;                READ ONLY
            //theFrame.DCM2NoClock = theFPGAControl.RegisterDCM2NoClock;                READ ONLY
            //theFrame.DCM2PhaseDone = theFPGAControl.RegisterDCM2PhaseDone;            READ ONLY
            //theFrame.DCM2PhaseTotal = theFPGAControl.RegisterDCM2PhaseTotal;          READ ONLY
            //theFrame.TestPulse2Bit = theFPGAControl.RegisterTestPulse2Bit;            READ ONLY
            //theFrame.TestPulseCount = theFPGAControl.RegisterTestPulseCount;          READ ONLY
            //theFrame.BoardID = (byte)theFPGAControl.RegisterBoardID;                  READ ONLY
            //theFrame.FirmwareVersion = theFPGAControl.RegisterFirmwareVersion;        READ ONLY
            theFrame.HVNumAvg = (byte)theFPGAControl.RegisterHVNumAvg;
            theFrame.HVPeriodManual = (ushort)theFPGAControl.RegisterHVPeriodManual;
            //theFrame.HVPeriodAuto = (ushort)theFPGAControl.RegisterHVPeriodAuto;      READ ONLY
            theFrame.HVPulseWidth = (byte)theFPGAControl.RegisterHVPulseWidth;
            //theFrame.Temperature = (ushort)theFPGAControl.RegisterTemperature;        READ ONLY
            theFrame.CosmicTrig = (byte)theFPGAControl.RegisterTripXThreshold;
            //theFrame.TripXCompEnc = (byte)theFPGAControl.RegisterTripXComparators;    READ ONLY
            //theFrame.ExtTriggFound = (byte)theFPGAControl.RegisterExtTriggFound;      READ ONLY   // 08.08.2008 Cristian
            theFrame.ExtTriggRearm = (byte)theFPGAControl.RegisterExtTriggRearm;                    // 08.08.2008 Cristian
            theFrame.DiscrimEnableMaskTrip0 = (ushort)theFPGAControl.RegisterDiscrimEnableMaskTrip0;// 10.30.2008 Cristian
            theFrame.DiscrimEnableMaskTrip1 = (ushort)theFPGAControl.RegisterDiscrimEnableMaskTrip1;// 10.30.2008 Cristian
            theFrame.DiscrimEnableMaskTrip2 = (ushort)theFPGAControl.RegisterDiscrimEnableMaskTrip2;// 10.30.2008 Cristian
            theFrame.DiscrimEnableMaskTrip3 = (ushort)theFPGAControl.RegisterDiscrimEnableMaskTrip3;// 10.30.2008 Cristian
            //theFrame.GateTimeStamp = theFPGAControl.RegisterGateTimeStamp;            READ ONLY   // 12.22.2008 Cristian  
        }

        private void btn_FPGAAdvancedGUI_Click(object sender, EventArgs e)
        {
            if (btn_FPGAAdvancedGUI.Text == "Show Advanced GUI")
            {
                fpgaDevRegControl1.ShowAdvancedGUI(true);
                btn_FPGAAdvancedGUI.Text = "Show Default GUI";
                return;
            }
            if (btn_FPGAAdvancedGUI.Text == "Show Default GUI")
            {
                fpgaDevRegControl1.ShowAdvancedGUI(false);
                btn_FPGAAdvancedGUI.Text = "Show Advanced GUI";
                return;
            }
        }

        #endregion

        #region Methods for Write/Read to/from TRIP Registers

        private void btn_AllFEsTRIPRegWrite_Click(object sender, EventArgs e)
        {
            tripDevRegControl1.UpdateTRIPLogicalRegArray();
            tabControl1.SelectTab(tabDescription.Name);
            richTextBoxDescription.Text = "Writing ALL Trips on ALL FEs with same data...\n\n";
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    foreach (CROC croc in CROCModules)
                    {
                        foreach (IFrontEndChannel channel in croc.ChannelList)
                        {
                            foreach (Frame.Addresses feb in channel.ChainBoards)
                            {
                                foreach (Frame.TRiPFunctions function in Enum.GetValues(typeof(Frame.TRiPFunctions)))
                                {
                                    try
                                    {

                                        if (function == Frame.TRiPFunctions.All || function == Frame.TRiPFunctions.None) continue;
                                        TripTFrame theFrame = new TripTFrame(feb, function, new FrameID());
                                        AssignTRIPRegsCristianToDave(tripDevRegControl1, theFrame);
                                        theFrame.Send(channel);
                                        theFrame.Receive();
                                        richTextBoxDescription.AppendText(channel.Description + ":" + feb +
                                            ":" + function + ": TripTDevRegs Write Success\n");
                                    }
                                    catch (Exception ex)
                                    {
                                        richTextBoxDescription.AppendText(channel.Description + ":" + feb +
                                            ":" + function + ": Error: " + ex.Message + "\n");
                                    }
                                }
                                richTextBoxDescription.AppendText("\n");
                            }
                            richTextBoxDescription.AppendText("\n");
                        }
                    }
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                    richTextBoxDescription.AppendText("...Done\n");
                }
            }
        }

        private void btn_TRIPRegWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    Frame.Addresses theBoard = (Frame.Addresses)(((FEnode)(theNode.Parent)).BoardID);
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Parent.Parent.Tag));
                    theChannel.Reset();
                    Frame.TRiPFunctions tf = (Frame.TRiPFunctions)(cmb_TripID.SelectedIndex) + 2;
                    TripTFrame theFrame = new TripTFrame(theBoard, tf, new FrameID());

                    tripDevRegControl1.UpdateTRIPLogicalRegArray();
                    AssignTRIPRegsCristianToDave(tripDevRegControl1, theFrame);
                    theFrame.Send(theChannel);
                    theFrame.Receive();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_TRIPRegRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    Frame.Addresses theBoard = (Frame.Addresses)(((FEnode)(theNode.Parent)).BoardID);
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Parent.Parent.Tag));
                    theChannel.Reset();

                    Frame.TRiPFunctions tf = (Frame.TRiPFunctions)(cmb_TripID.SelectedIndex) + 2;
                    TripTFrame theFrame = new TripTFrame(theBoard, tf, new FrameID());
                    theFrame.Send(theChannel);
                    theFrame.Receive();
                    AssignTRIPRegsDaveToCristian(theFrame, tripDevRegControl1);
                    tripDevRegControl1.UpdateFormControls();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void AssignTRIPRegsDaveToCristian(TripTFrame theFrame, MinervaUserControls.TripDevRegControl theTRIPControl)
        {
            theTRIPControl.RegisterIBP = (uint)theFrame[TripTFrame.LogicalRegisters.IBP];
            theTRIPControl.RegisterIBBNFALL = (uint)theFrame[TripTFrame.LogicalRegisters.IBBNFoll];
            theTRIPControl.RegisterIFF = (uint)theFrame[TripTFrame.LogicalRegisters.IFF];
            theTRIPControl.RegisterIBPIFF1REF = (uint)theFrame[TripTFrame.LogicalRegisters.IBPIFF1REF];
            theTRIPControl.RegisterIBPOPAMP = (uint)theFrame[TripTFrame.LogicalRegisters.IBPOPAMP];
            theTRIPControl.RegisterIB_T = (uint)theFrame[TripTFrame.LogicalRegisters.IBPFoll2];
            theTRIPControl.RegisterIFFP2 = (uint)theFrame[TripTFrame.LogicalRegisters.IFF2];
            theTRIPControl.RegisterIBCOMP = (uint)theFrame[TripTFrame.LogicalRegisters.IBCOMP];
            theTRIPControl.RegisterVREF = (uint)theFrame[TripTFrame.LogicalRegisters.VREF];
            theTRIPControl.RegisterVTH = (uint)theFrame[TripTFrame.LogicalRegisters.VTH];
            theTRIPControl.RegisterGAIN = (uint)theFrame[TripTFrame.LogicalRegisters.GAIN];
            theTRIPControl.RegisterPIPEDEL = (uint)theFrame[TripTFrame.LogicalRegisters.PIPEDEL];
            theTRIPControl.RegisterIRSEL = (uint)theFrame[TripTFrame.LogicalRegisters.IRSEL];
            theTRIPControl.RegisterIWSEL = (uint)theFrame[TripTFrame.LogicalRegisters.IWSEL];
            theTRIPControl.RegisterINJEX0 = (uint)(theFrame[TripTFrame.LogicalRegisters.INJECT] & 0x1);
            theTRIPControl.RegisterINJB0 = (uint)(theFrame[TripTFrame.LogicalRegisters.INJECT] & 0x1FE) >> 1;
            theTRIPControl.RegisterINJB1 = (uint)(theFrame[TripTFrame.LogicalRegisters.INJECT] & 0x1FE00) >> 9;
            theTRIPControl.RegisterINJB2 = (uint)(theFrame[TripTFrame.LogicalRegisters.INJECT] & 0x1FE0000) >> 17;
            theTRIPControl.RegisterINJB3 = (uint)(theFrame[TripTFrame.LogicalRegisters.INJECT] & 0x1FE000000) >> 25;
            theTRIPControl.RegisterINJEX33 = (uint)(theFrame[TripTFrame.LogicalRegisters.INJECT] & 0x200000000) >> 33;
        }

        private void AssignTRIPRegsCristianToDave(MinervaUserControls.TripDevRegControl theTRIPControl, TripTFrame theFrame)
        {
            theFrame[TripTFrame.LogicalRegisters.IBP] = theTRIPControl.RegisterIBP;
            theFrame[TripTFrame.LogicalRegisters.IBBNFoll] = theTRIPControl.RegisterIBBNFALL;
            theFrame[TripTFrame.LogicalRegisters.IFF] = theTRIPControl.RegisterIFF;
            theFrame[TripTFrame.LogicalRegisters.IBPIFF1REF] = theTRIPControl.RegisterIBPIFF1REF;
            theFrame[TripTFrame.LogicalRegisters.IBPOPAMP] = theTRIPControl.RegisterIBPOPAMP;
            theFrame[TripTFrame.LogicalRegisters.IBPFoll2] = theTRIPControl.RegisterIB_T;
            theFrame[TripTFrame.LogicalRegisters.IFF2] = theTRIPControl.RegisterIFFP2;
            theFrame[TripTFrame.LogicalRegisters.IBCOMP] = theTRIPControl.RegisterIBCOMP;
            theFrame[TripTFrame.LogicalRegisters.VREF] = theTRIPControl.RegisterVREF;
            theFrame[TripTFrame.LogicalRegisters.VTH] = theTRIPControl.RegisterVTH;
            theFrame[TripTFrame.LogicalRegisters.GAIN] = theTRIPControl.RegisterGAIN;
            theFrame[TripTFrame.LogicalRegisters.PIPEDEL] = theTRIPControl.RegisterPIPEDEL;
            theFrame[TripTFrame.LogicalRegisters.IRSEL] = theTRIPControl.RegisterIRSEL;
            theFrame[TripTFrame.LogicalRegisters.IWSEL] = theTRIPControl.RegisterIWSEL;
            theFrame[TripTFrame.LogicalRegisters.INJECT] = (theTRIPControl.RegisterINJEX33 << 33) |
                (theTRIPControl.RegisterINJB3 << 25) | (theTRIPControl.RegisterINJB2 << 17) |
                (theTRIPControl.RegisterINJB1 << 9) | (theTRIPControl.RegisterINJB0 << 1) |
                theTRIPControl.RegisterINJEX0;
        }

        private void btn_TRIPAdvancedGUI_Click(object sender, EventArgs e)
        {
            if (btn_TRIPAdvancedGUI.Text == "Show Advanced GUI")
            {
                tripDevRegControl1.ShowAdvancedGUI(true);
                btn_TRIPAdvancedGUI.Text = "Show Default GUI";
                return;
            }
            if (btn_TRIPAdvancedGUI.Text == "Show Default GUI")
            {
                tripDevRegControl1.ShowAdvancedGUI(false);
                btn_TRIPAdvancedGUI.Text = "Show Advanced GUI";
                return;
            }
        }

        private void cmb_TripID_SelectedIndexChanged(object sender, EventArgs e)
        {
            btn_TRIPRegRead_Click(null, null);
        }

        #endregion

        #region Methods for reading HVActual on FEBs

        ushort adcThreshold;
        string outputText;

        private void readVoltagesToolStripMenuItem_Click(object sender, EventArgs e)
        {
            richTextBoxHVRead.Text = "Displays FEBs with HVActual differing from HVTarget \nby an amount greater than that specified below";
            tabControl1.SelectTab(tabReadHV);
            textBoxADCThreshold.Enabled = true;
            btnReadHV.Enabled = true;
            btnSwitchToAuto.Enabled = true;
            textBoxMonitorTimer.Enabled = false;
            btnMonitorHV.Enabled = false;
        }

        private void btnReadHV_Click(object sender, EventArgs e)
        {
            if (btnReadHV.Text == "Read")
            {
                try { adcThreshold = Convert.ToUInt16(textBoxADCThreshold.Text); }
                catch (Exception exe)
                {
                    richTextBoxHVRead.Text = exe.Message;
                    return;
                }
                readVoltagesToolStripMenuItem.Enabled = false;
                textBoxADCThreshold.Enabled = false;
                btnReadHV.Text = "Stop";
                backgroundWorker1.RunWorkerAsync();
            }
            else backgroundWorker1.CancelAsync();
        }

        private void backgroundWorker1_DoWork(object sender, DoWorkEventArgs e)
        {
            while (true)
            {
                ReadHVChannelFEBs();
                backgroundWorker1.ReportProgress(100);
                if (backgroundWorker1.CancellationPending) return;
                System.Threading.Thread.Sleep(1000);
            }
        }

        private void backgroundWorker1_ProgressChanged(object sender, ProgressChangedEventArgs e)
        {
            richTextBoxHVRead.Text = outputText;
        }

        private void backgroundWorker1_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            btnReadHV.Text = "Read";
            readVoltagesToolStripMenuItem.Enabled = true;
            textBoxADCThreshold.Enabled = true;
        }

        private void ReadHVChannelFEBs()
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    outputText = "Croc:CH:FE: HVActual, HVTarget, HVActual - HVTarget, HVPeriodAuto\n\n";
                    foreach (CROC croc in CROCModules)
                    {
                        foreach (IFrontEndChannel channel in croc.ChannelList)
                        {
                            foreach (Frame.Addresses feb in channel.ChainBoards)
                            {
                                try
                                {
                                    FPGAFrame frame = new FPGAFrame(feb, Frame.FPGAFunctions.Read, new FrameID());
                                    frame.Send(channel);
                                    frame.Receive();
                                    if (Math.Abs(frame.HVActual - frame.HVTarget) < adcThreshold) continue;
                                    outputText += channel.Description + ":" + feb + ": " +
                                                  frame.HVActual.ToString() + ", " + frame.HVTarget.ToString() + ", " +
                                                  Convert.ToString(frame.HVActual - frame.HVTarget) + ", " +
                                                  Convert.ToString(frame.HVPeriodAuto) + "\n";
                                }
                                catch (Exception e)
                                {
                                    outputText += channel.Description + ":" + feb + ": Error: " + e.Message + "\n";
                                }
                            }
                            outputText += "\n";
                        }
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                    //richTextBoxHVRead.Text += "...Done\n"; reported error in VisualStudio 2008...
                }
            }
        }

        private void zeroHVAllToolStripMenuItem_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    DialogResult answer = MessageBox.Show("WARNING \n You are about to set HVTarget on all FEBs to zero. \n Do you wish to continue?", "Confirm Zero HVTarget on all FEBs",
                        MessageBoxButtons.YesNo, MessageBoxIcon.Warning, MessageBoxDefaultButton.Button2);
                    if (answer != DialogResult.Yes) return;
                    tabControl1.SelectTab(tabReadHV);
                    richTextBoxHVRead.Text = "Setting HVTarget on FEBs to zero\n\n";
                    foreach (CROC croc in CROCModules)
                    {
                        foreach (IFrontEndChannel channel in croc.ChannelList)
                        {
                            foreach (Frame.Addresses feb in channel.ChainBoards)
                            {
                                try
                                {
                                    FPGAFrame frameRead = new FPGAFrame(feb, Frame.FPGAFunctions.Read, new FrameID());
                                    frameRead.Send(channel);
                                    frameRead.Receive();

                                    FPGAFrame frameWrite = new FPGAFrame(feb, Frame.FPGAFunctions.Write, new FrameID());

                                    frameWrite.Registers = frameRead.Registers;

                                    frameWrite.HVTarget = 0;
                                    frameWrite.Send(channel);
                                    frameWrite.Receive();
                                    richTextBoxHVRead.Text += channel.Description + ":" + feb +
                                        ": HVTarget set to " + frameWrite.HVTarget.ToString() + "\n";
                                }
                                catch (Exception ez)
                                {
                                    richTextBoxHVRead.Text += channel.Description + ":" + feb + ": Error: " + ez.Message + "\n";
                                }
                            }
                            richTextBoxHVRead.Text += "\n";
                        }
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                    richTextBoxHVRead.Text += "...Done\n";
                }
            }
        }

        private void btnSwitchToAuto_Click(object sender, EventArgs e)
        {
            if (btnSwitchToAuto.Text == "Switch to Auto")
            {
                HVSwitchToAuto(true);
                btnSwitchToAuto.Text = "Switch to Man";
                return;
            }
            if (btnSwitchToAuto.Text == "Switch to Man")
            {
                HVSwitchToAuto(false);
                btnSwitchToAuto.Text = "Switch to Auto";
                return;
            }
        }

        private void HVSwitchToAuto(bool SwitchToAuto)
        {
            richTextBoxHVRead.Text = "Switching HV to ";
            if (SwitchToAuto) richTextBoxHVRead.Text += "Auto mode...\n\n";
            else richTextBoxHVRead.Text += "Manual mode...\n\n";
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    foreach (CROC croc in CROCModules)
                    {
                        foreach (IFrontEndChannel channel in croc.ChannelList)
                        {
                            foreach (Frame.Addresses feb in channel.ChainBoards)
                            {
                                try
                                {
                                    FPGAFrame frameRead = new FPGAFrame(feb, Frame.FPGAFunctions.Read, new FrameID());
                                    frameRead.Send(channel);
                                    frameRead.Receive();

                                    FPGAFrame frameWrite = new FPGAFrame(feb, Frame.FPGAFunctions.Write, new FrameID());
                                    frameWrite.Registers = frameRead.Registers;
                                    if (SwitchToAuto) frameWrite.HVManual = false;
                                    else frameWrite.HVManual = true;
                                    frameWrite.Send(channel);
                                    frameWrite.Receive();

                                    if (frameWrite.HVManual == SwitchToAuto)
                                    {
                                        richTextBoxHVRead.Text += channel.Description + ":" + feb + "  unable to set to ";
                                        if (SwitchToAuto) richTextBoxHVRead.Text += "Auto mode\n";
                                        else richTextBoxHVRead.Text += "Manual mode\n";
                                    }
                                    else
                                    {
                                        richTextBoxHVRead.Text += channel.Description + ":" + feb +
                                            ": HVManual set to " + frameWrite.HVManual.ToString() + "\n";
                                    }
                                }
                                catch (Exception e)
                                {
                                    richTextBoxHVRead.Text += channel.Description + ":" + feb + ": Error: " + e.Message + "\n";
                                }
                            }
                            richTextBoxHVRead.Text += "\n";
                        }
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                    richTextBoxHVRead.Text += "...Done\n";
                }
            }
        }

        private void monitorVoltagesToolStripMenuItem_Click(object sender, EventArgs e)
        {
            richTextBoxHVRead.Text = "Monitor FEBs' HV at time interval defined by Monitor Timer (sec) ";
            tabControl1.SelectTab(tabReadHV);
            textBoxMonitorTimer.Enabled = true;
            btnMonitorHV.Enabled = true;
            textBoxADCThreshold.Enabled = false;
            btnReadHV.Enabled = false;
            btnSwitchToAuto.Enabled = false;
        }

        private void textBoxMonitorTimer_TextChanged(object sender, EventArgs e)
        {
            try
            {
                timerMonitorHV.Interval = 1000 * Convert.ToInt16(textBoxMonitorTimer.Text);
            }
            catch (Exception em)
            {
                MessageBox.Show(em.Message);
                textBoxMonitorTimer.Text = timerMonitorHV.Interval.ToString();
            }
        }

        private void btnMonitorHV_Click(object sender, EventArgs e)
        {
            if (btnMonitorHV.Text == "Monitor")
            {
                richTextBoxHVRead.Clear();
                timerMonitorHV.Start();
                btnMonitorHV.Text = "Stop";
                return;
            }
            if (btnMonitorHV.Text == "Stop")
            {
                timerMonitorHV.Stop();
                btnMonitorHV.Text = "Monitor";
                return;
            }
        }

        private void timerMonitorHV_Tick(object sender, EventArgs e)
        {
            //lock (this)
            //{
            //    vmeDone.WaitOne();
            //    try
            //    {
            ReadHVChannelFEBs();
            richTextBoxHVRead.Text = DateTime.Now + "\n" + outputText;
            //    }
            //    catch (Exception ex)
            //    {
            //        MessageBox.Show(ex.Message);
            //    }
            //    finally
            //    {
            //        vmeDone.Set();
            //    }
            //}        
        }

        #endregion

        #region Methods for Write/Read to/from FLASH Memory

        private void btn_FLASHAdvancedGUI_Click(object sender, EventArgs e)
        {
            AdvancedGUI((Button)sender, btn_FLASHReadSPIToFile, btn_FLASHWriteFileToSPI);
        }

        private void btn_FLASHReadSPIToFile_Click(object sender, EventArgs e)
        {
            tabControl1.SelectTab(tabDescription);
            richTextBoxDescription.Clear();
            this.Cursor = Cursors.WaitCursor;
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    SaveFileDialog mySFD = new SaveFileDialog();
                    mySFD.Filter = "spi files (*.spidata)|*.spidata|All files (*.*)|*.*";
                    mySFD.FilterIndex = 1;
                    mySFD.RestoreDirectory = true;
                    if (mySFD.ShowDialog() == DialogResult.OK)
                    {
                        TreeNode theNode = treeView1.SelectedNode;
                        Frame.Addresses theBoard = (Frame.Addresses)(((FEnode)(theNode.Parent)).BoardID);
                        IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Parent.Parent.Tag));
                        FlashFrameReadMemoryToFile(mySFD, theBoard, theChannel);
                    }
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
            this.Cursor = Cursors.Arrow;
        }

        private void btn_FLASHWriteFileToSPI_Click(object sender, EventArgs e)
        {
            tabControl1.SelectTab(tabDescription);
            richTextBoxDescription.Clear();
            this.Cursor = Cursors.WaitCursor;
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    OpenFileDialog myOFD = new OpenFileDialog();
                    myOFD.Filter = "spi files (*.spidata)|*.spidata|All files (*.*)|*.*";
                    myOFD.FilterIndex = 1;
                    myOFD.RestoreDirectory = true;
                    if (myOFD.ShowDialog() == DialogResult.OK)
                    {
                        TreeNode theNode = treeView1.SelectedNode;
                        Frame.Addresses theBoard = (Frame.Addresses)(((FEnode)(theNode.Parent)).BoardID);
                        IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Parent.Parent.Tag));
                        FlashFrameWriteMemoryFromFile(myOFD, theBoard, theChannel);
                    }
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
            this.Cursor = Cursors.Arrow;
        }

        private void FlashFrameWriteMemoryFromFile(OpenFileDialog OFD, Frame.Addresses theBoard, IFrontEndChannel theChannel)
        {
            StringBuilder msg = new StringBuilder();
            prgStatus.Minimum = 0;
            prgStatus.Maximum = FlashFrame.Spartan_3E_Npages;
            prgStatus.Value = 0;
            richTextBoxDescription.AppendText(theChannel.Description + ":" + theBoard +
            ": FLASH Write Begin " + DateTime.Now.ToString() + "\n");
            theChannel.Reset();
            //FlashFrame.WriteMemoryFromFile(theChannel, theBoard, OFD.FileName);   //Dave's original  
            FlashFrame.PageCompleted += new ProgressChangedEventHandler(ProgressReport);    //10.05.2009 CG           
            FlashFrame.WriteMemoryFromFile(theChannel, theBoard, OFD.FileName, out msg);    //04.14.2009 CG patch
            FlashFrame.PageCompleted -= new ProgressChangedEventHandler(ProgressReport);    //10.05.2009 CG
            richTextBoxDescription.AppendText(msg.ToString());
            richTextBoxDescription.AppendText(theChannel.Description + ":" + theBoard +
            ": FLASH Write   End " + DateTime.Now.ToString() + "\n");
        }

        private void FlashFrameReadMemoryToFile(SaveFileDialog SFD, Frame.Addresses theBoard, IFrontEndChannel theChannel)
        {
            StringBuilder msg = new StringBuilder();
            prgStatus.Minimum = 0;
            prgStatus.Maximum = FlashFrame.Spartan_3E_Npages;
            prgStatus.Value = 0;
            richTextBoxDescription.AppendText(theChannel.Description + ":" + theBoard +
            ": FLASH Read Begin " + DateTime.Now.ToString() + "\n");
            theChannel.Reset();
            //FlashFrame.ReadMemoryToFile(theChannel, theBoard, SFD.FileName);        //Dave's original
            FlashFrame.PageCompleted += new ProgressChangedEventHandler(ProgressReport);    //10.05.2009 CG
            FlashFrame.ReadMemoryToFile(theChannel, theBoard, SFD.FileName, out msg);       //04.14.2009 CG
            FlashFrame.PageCompleted -= new ProgressChangedEventHandler(ProgressReport);    //10.05.2009 CG
            richTextBoxDescription.AppendText(msg.ToString());
            richTextBoxDescription.AppendText(theChannel.Description + ":" + theBoard +
            ": FLASH Read   End " + DateTime.Now.ToString() + "\n");
        }

        #endregion

        #region Methods for Write/Read to/from CHANNEL

        private void btn_CHAdvancedGUI_Click(object sender, EventArgs e)
        {
            AdvancedGUI((Button)sender, groupBoxCH_FLASH, groupBoxCH_StatusRegister,
                groupBoxCH_DPM, groupBoxCH_Frame, groupBoxCH_DEBUG);
        }

        private void btn_CHWriteFileToSPI_Click(object sender, EventArgs e)
        {
            tabControl1.SelectTab(tabDescription);
            richTextBoxDescription.Clear();
            this.Cursor = Cursors.WaitCursor;
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    OpenFileDialog myOFD = new OpenFileDialog();
                    myOFD.Filter = "spi files (*.spidata)|*.spidata|All files (*.*)|*.*";
                    myOFD.FilterIndex = 1;
                    myOFD.RestoreDirectory = true;
                    if (myOFD.ShowDialog() == DialogResult.OK)
                    {
                        TreeNode theNode = treeView1.SelectedNode;
                        IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Tag));
                        theChannel.Reset();
                        ChannelWriteFileToFEsFlash(myOFD, theChannel);
                    }
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
            this.Cursor = Cursors.Arrow;
        }

        private void btn_CHReBootFEs_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Tag));
                    CROC theCroc = (CROC)(theNode.Parent.Tag);
                    ChannelReBootFEs(theChannel, theCroc, true);
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void ChannelWriteFileToFEsFlash(OpenFileDialog myOFD, IFrontEndChannel theChannel)
        {
            richTextBoxDescription.AppendText("\nWriting ALL FEBs FLASH on " + theChannel.Description +
                " with the following data file :\n\n" + myOFD.FileName + "\n\n");
            foreach (Frame.Addresses feb in theChannel.ChainBoards)
                FlashFrameWriteMemoryFromFile(myOFD, feb, theChannel);
            richTextBoxDescription.AppendText("\n...Done " + DateTime.Now.ToString() + "\n");
        }

        private void ChannelReBootFEs(IFrontEndChannel theChannel, CROC theCroc, bool withChannelReset)
        {
            //Dave's code in CROCFrontEndChannel.cs defines SendReset() as private, so I can't call it...
            //The following is Cristian's adaptation...
            ushort ResetMask = (ushort)(((ushort)0x0001) << ((ushort)(8 + theChannel.ChannelNumber - 1)));
            // Enable reset on this channel
            controller.Write(theCroc.BaseAddress + (uint)CROC.Registers.ResetAndTestMask, controller.AddressModifier,
                controller.DataWidth, BitConverter.GetBytes(ResetMask));
            // Send the command
            controller.Write(theCroc.BaseAddress + (uint)CROC.Registers.ChannelReset, controller.AddressModifier,
                controller.DataWidth, CROC.ChannelResetRegisterValue);
            // Clear the enable register
            controller.Write(theCroc.BaseAddress + (uint)CROC.Registers.ResetAndTestMask, controller.AddressModifier,
                controller.DataWidth, CROC.NullValue);

            //Cristian's note: I need to call the theChannel.Reset() to turn off ANY reminded RED LEDs on CROC...
            if (withChannelReset)
            {
                Thread.Sleep(3000);
                theChannel.Reset();
            }
        }

        private void ChannelUpdateStatusLabels(CROCFrontEndChannel.StatusBits chStatus)
        {
            lblCH_StatMsgSent.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.MessageSent);
            lblCH_StatMsgReceived.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.MessageReceived);
            lblCH_StatCRCError.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.CRCError);
            lblCH_StatTimeoutError.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.TimeoutError);
            lblCH_StatFIFONotEmpty.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.FIFONotEmpty);
            lblCH_StatFIFOFull.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.FIFOFull);
            lblCH_StatDPMFull.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.DPMFull);
            lblCH_StatUnusedBit7.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.UnusedBit7);
            lblCH_StatRFPresent.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.RFPresent);
            lblCH_StatSerializerSYNC.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.SerializerSynch);
            lblCH_StatDeserializerLOCK.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.DeserializerLock);
            lblCH_StatUnusedBit11.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.UnusedBit11);
            lblCH_StatPLL0LOCK.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.PLLLocked);
            //some little abuse here from Dave... these CRIM bits should NOT be defined as CROCFrontEndChannel.StatusBits ...
            lblCH_StatPLL1LOCK.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.TestPulseReceived);
            lblCH_StatUnusedBit14.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.ResetReceived);
            lblCH_StatUnusedBit15.Text = CheckStatusBit(chStatus, CROCFrontEndChannel.StatusBits.EncodedCommandReceived);
        }

        private string CheckStatusBit(CROCFrontEndChannel.StatusBits status, CROCFrontEndChannel.StatusBits bit)
        {
            return (bit == (status & bit)) ? "1" : "0";
        }

        private void ChannelClearLabels()
        {
            foreach (Control c in tabCH.Controls)
                if (c is GroupBox)
                {
                    if (c == groupBoxCH_DEBUG) continue;
                        foreach (Control cc in c.Controls)
                            ClearControl(cc);
                }
        }

        private void btn_CHStatusRegRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Tag));
                    CROCFrontEndChannel.StatusBits chStatus = theChannel.StatusRegister;
                    lblCH_StatusValue.Text = "0x" + chStatus.ToString("X");
                    ChannelUpdateStatusLabels(chStatus);
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CHStatusRegClear_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Tag));
                    theChannel.ClearStatus();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CHDPMPointerRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Tag));
                    bool messageSent = false;
                    bool messageReceived = false;
                    bool crcError = false;
                    bool timeoutError = false;
                    bool sendBufferEmpty = false;
                    bool sendBufferFull = false;
                    bool receiveBufferFull = false;
                    bool rfPresent = false;
                    bool serializerSynch = false;
                    bool deserializerLock = false;
                    bool pllOk = false;
                    ushort pointer = 0;
                    theChannel.ReadStatusAndPointer(out messageSent, out messageReceived, out crcError, out timeoutError,
                        out sendBufferEmpty, out sendBufferFull, out receiveBufferFull, out rfPresent, out serializerSynch,
                        out deserializerLock, out pllOk, out pointer);
                    lblCH_DPMPointerValue.Text = "0x" + pointer.ToString("X");
                    //ChannelUpdateStatusLabels(theChannel.StatusRegister);
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CHDPMPointerReset_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Tag));
                    theChannel.ResetPointer();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CHFIFOAppendMessage_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Tag));
                    txt_CHFIFORegWrite.Text = txt_CHFIFORegWrite.Text.ToUpper();
                    AppendMessage(txt_CHFIFORegWrite.Text, theChannel);
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void AppendMessage(string theMessage, IFrontEndChannel theChannel)
        {
            if ((theMessage.Length % 2) == 0)
            {
                byte[] message = new byte[theMessage.Length / 2];
                for (int i = 0; i < message.Length; i++)
                    message[i] = Convert.ToByte(theMessage.Substring(2 * i, 2), 16);
                theChannel.FillMessage(message.Length, message);
            }
            else MessageBox.Show("The number of hex characters must be even\nOperation aborted");
        }

        private void btn_CHFIFOWriteMessage_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Tag));
                    theChannel.WriteMessage();
                    //theChannel.WriteMessageCRIM();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CHSendMessage_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Tag));
                    theChannel.SendMessage();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CHDPMRead_Click(object sender, EventArgs e)
        {
            CHDPMRead();
        }
        private byte[] CHDPMRead()
        {
            byte[] response = null;
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Tag));
                    int responseLength = Convert.ToInt32(txt_CHDPMReadLength.Text);
                    if ((2 <= responseLength) & (responseLength <= CROCFrontEndChannel.MemoryMaxSize))
                    {
                        response = theChannel.ReadMemoryCRIM(responseLength);
                        rtb_CHDPMRead.Text = DisplayMessage(theChannel.ReadMemoryCRIM(responseLength), responseLength);
                    }
                    else
                        MessageBox.Show("attempt to read more than maximum DPM depth = " +
                            CROCFrontEndChannel.MemoryMaxSize + "or less than 2\nOperation aborted");
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
            return response;
        }

        private string DisplayMessage(byte[] response, int responseLength)
        {
            StringBuilder readMessage = new StringBuilder();
            readMessage.Append("0000" + "  " +
                response[0].ToString("X2") +
                response[1].ToString("X2") +
                " -> dec=" + (response[1] * 256 + response[0]) + "\n");
            for (int i = 2; i < responseLength; i += 8)
            {
                readMessage.Append(i.ToString("X4") + "  ");
                for (int j = 0; j < 8; j++)
                    if (i + j < responseLength)
                        readMessage.Append(response[i + j].ToString("X2"));
                readMessage.Append("\n");
            }
            return readMessage.ToString();
        }

        #endregion

        #region Methods for Write/Read to/from CROC

        private void btn_CROCAdvancedGUI_Click(object sender, EventArgs e)
        {
            AdvancedGUI((Button)sender, groupBoxCROC_FLASH, groupBoxCROC_TimingSetup,
                groupBoxCROC_ResetTPMaskReg, groupBoxCROC_FastCommand, groupBoxCROC_LoopDelay,
                groupBoxCROC_FEBGateDelays);
        }

        private void btn_CROCWriteFileToSPI_Click(object sender, EventArgs e)
        {
            tabControl1.SelectTab(tabDescription);
            richTextBoxDescription.Clear();
            this.Cursor = Cursors.WaitCursor;
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    OpenFileDialog myOFD = new OpenFileDialog();
                    myOFD.Filter = "spi files (*.spidata)|*.spidata|All files (*.*)|*.*";
                    myOFD.FilterIndex = 1;
                    myOFD.RestoreDirectory = true;
                    if (myOFD.ShowDialog() == DialogResult.OK)
                    {
                        TreeNode theNode = treeView1.SelectedNode;
                        CROC theCROC = ((CROC)(theNode.Tag));
                        foreach (CROCFrontEndChannel theChannel in theCROC.ChannelList)
                        {
                            theChannel.Reset();
                            ChannelWriteFileToFEsFlash(myOFD, theChannel);
                        }
                    }
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
            this.Cursor = Cursors.Arrow;
        }

        private void btn_CROCReBootFEs_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    CROC theCROC = ((CROC)(theNode.Tag));
                    foreach (CROCFrontEndChannel theChannel in theCROC.ChannelList)
                        ChannelReBootFEs(theChannel, theCROC, false);
                    //Cristian's note: I need to call the theCROC.Reset() to turn off ANY reminded RED LEDs on CROC...
                    Thread.Sleep(3000); //let all FEs reboot and send any garbage to CROC...
                    theCROC.Reset();
                    //UInt32 status = 0;
                    //foreach (CROCFrontEndChannel theChannel in theCROC.ChannelList)
                    //{
                    //    theChannel.Reset();
                    //    status = Convert.ToUInt32(theChannel.StatusRegister);
                    //    while (status != 0x3700)
                    //    {
                    //        Thread.Sleep(1000); //just wait more... 
                    //        theChannel.Reset();
                    //        status = Convert.ToUInt32(theChannel.StatusRegister);
                    //    }
                    //}
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void CrocClearLabels()
        {
            foreach (Control c in tabCROC.Controls)
                if (c is GroupBox)
                    foreach (Control cc in c.Controls)
                        ClearControl(cc);
        }

        private void cmb_CROCTimingSetupClock_SelectedIndexChanged(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    CROC theCroc = ((CROC)(theNode.Tag));
                    if (cmb_CROCTimingSetupClock.SelectedIndex == 0)
                        theCroc.ClockMode = CROC.ClockModes.Internal;
                    if (cmb_CROCTimingSetupClock.SelectedIndex == 1)
                        theCroc.ClockMode = CROC.ClockModes.External;
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void cmb_CROCTimingSetupTPDelay_SelectedIndexChanged(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    CROC theCroc = ((CROC)(theNode.Tag));
                    if (cmb_CROCTimingSetupTPDelay.SelectedIndex == 0)
                        theCroc.TestPulseDelayEnabled = false;
                    if (cmb_CROCTimingSetupTPDelay.SelectedIndex == 1)
                        theCroc.TestPulseDelayEnabled = true;
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void txt_CROCTimingSetupTPDelay_TextChanged(object sender, EventArgs e)
        {
            if (txt_CROCTimingSetupTPDelay.Text == "") return;
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    CROC theCroc = ((CROC)(theNode.Tag));
                    theCroc.TestPulseDelayValue = Convert.ToUInt16(txt_CROCTimingSetupTPDelay.Text, 16);
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CROCTimingSetupRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    CROC theCroc = ((CROC)(theNode.Tag));
                    lbl_CROCTimingSetupRead.Text = "0x" + (theCroc.TimingSetupRegister & 0x93FF).ToString("X");
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CROCResetTPWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    CROC theCroc = ((CROC)(theNode.Tag));
                    ushort ResetAndTestMask = (ushort)
                        (Convert.ToUInt16(chk_CROCResetCh4.Checked) << 11 |
                        Convert.ToUInt16(chk_CROCResetCh3.Checked) << 10 |
                        Convert.ToUInt16(chk_CROCResetCh2.Checked) << 9 |
                        Convert.ToUInt16(chk_CROCResetCh1.Checked) << 8 |
                        Convert.ToUInt16(chk_CROCTPulseCh4.Checked) << 3 |
                        Convert.ToUInt16(chk_CROCTPulseCh3.Checked) << 2 |
                        Convert.ToUInt16(chk_CROCTPulseCh2.Checked) << 1 |
                        Convert.ToUInt16(chk_CROCTPulseCh1.Checked) << 0);
                    theCroc.ResetAndTestMaskRegister = ResetAndTestMask;
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CROCResetTPRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    CROC theCroc = ((CROC)(theNode.Tag));
                    lbl_CROCResetTPRead.Text = "0x" + theCroc.ResetAndTestMaskRegister.ToString("X");
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CROCResetSend_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    CROC theCroc = ((CROC)(theNode.Tag));
                    theCroc.ChannelResetRegister = BitConverter.ToUInt16(CROC.ChannelResetRegisterValue, 0);
                    //Cristian's note: I need to call the theChannel.Reset() to turn off ANY reminded RED LEDs on CROC...
                    //see also private void ChannelReBootFEs()
                    Thread.Sleep(3000);
                    foreach (CROCFrontEndChannel theChannel in theCroc.ChannelList)
                        theChannel.Reset();
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CROCTPSend_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    CROC theCroc = ((CROC)(theNode.Tag));
                    theCroc.TestPulseRegister = BitConverter.ToUInt16(CROC.TestPulseRegisterValue, 0);
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
            btn_CROCLoopDelayRead_Click(null, null);
        }

        private void btn_CROCFastCommand_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    CROC theCroc = ((CROC)(theNode.Tag));
                    switch (cmb_CROCFastCommand.SelectedIndex)
                    {
                        case 0: //OpenGate
                            theCroc.FastCommandRegister = (ushort)FastCommands.OpenGate;    // 0xB1;
                            break;
                        case 1: //ResetFPGA
                            theCroc.FastCommandRegister = (ushort)FastCommands.ResetFPGA;   // 0x8D;
                            break;
                        case 2: //ResetTimer
                            theCroc.FastCommandRegister = (ushort)FastCommands.ResetTimer;  // 0xC9;
                            break;
                        case 3: //LoadTimer
                            theCroc.FastCommandRegister = (ushort)FastCommands.LoadTimer;   // 0xC5;
                            break;
                        case 4: //TriggerFound
                            theCroc.FastCommandRegister = (ushort)FastCommands.TriggerFound;// 0x89;
                            break;
                        case 5: //TriggerRearm
                            theCroc.FastCommandRegister = (ushort)FastCommands.TriggerRearm;// 0x85;
                            break;
                        case 6: //QueryFPGA
                            theCroc.FastCommandRegister = (ushort)FastCommands.QueryFPGA;  // 0x91;
                            break;
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CROCLoopDelayRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    CROC theCroc = ((CROC)(theNode.Tag));
                    byte[] loopDelay = new byte[2];
                    Label[] loopDelayLabels = { lbl_CROCLoopDelayCh1, lbl_CROCLoopDelayCh2, lbl_CROCLoopDelayCh3, lbl_CROCLoopDelayCh4 };
                    foreach (CROCFrontEndChannel theChannel in theCroc.ChannelList)
                    {
                        loopDelay = BitConverter.GetBytes(0);
                        controller.Read(theCroc.BaseAddress + (uint)CROCFrontEndChannel.Registers.LoopDelay +
                            ((uint)0x4000 * (uint)(theChannel.ChannelNumber - 1)),
                            controller.AddressModifier, controller.DataWidth, loopDelay);
                        loopDelayLabels[(uint)(theChannel.ChannelNumber - 1)].Text =
                            (loopDelay[0] & 0x7F).ToString();
                    }

                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CROCLoopDelayClear_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    TreeNode theNode = treeView1.SelectedNode;
                    CROC theCroc = ((CROC)(theNode.Tag));
                    foreach (CROCFrontEndChannel theChannel in theCroc.ChannelList)
                        theChannel.ClearStatus();
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
            btn_CROCLoopDelayRead_Click(null, null);
        }

        #endregion

        #region Methods for Light Injection Box
        SerialPort LISerialPort = new SerialPort();
        bool LIBoxIsActive = false;

        private void btn_LIBoxAdvancedGUI_Click(object sender, EventArgs e)
        {
            AdvancedGUI((Button)sender, groupBoxLIBox_RS232Commands,
                groupBoxLIBox_RS232Settings);
        }

        private void lightInjectionToolStripMenuItem_Click(object sender, EventArgs e)
        {
            tabControl1.SelectTab(tabLIBox);
            LI_FindSerialPorts();
            LI_ConfigureSerialPort(LISerialPort);
            if (!LISerialPort.IsOpen) LISerialPort.Open();
        }

        private void LI_FindSerialPorts()
        {
            try
            {
                //PortName
                string[] ports = SerialPort.GetPortNames();
                ////cmb_LIBoxPortName.Items.Clear();
                if (ports.Length > 0)
                    //foreach (string port in ports)
                    //    cmb_LIBoxPortName.Items.Add(port);
                    cmb_LIBoxPortName.DataSource = ports;
                cmb_LIBoxPortName.SelectedIndex = 0;
                // BaudRate
                int[] baudRate = { 300, 600, 1200, 2400, 9600, 14400, 19200, 38400, 57600, 115200, 128000 };
                cmb_LIBoxBaudRate.DataSource = baudRate;
                cmb_LIBoxBaudRate.SelectedIndex = 4;
                // Parity
                string[] parity = Enum.GetNames(typeof(Parity));
                cmb_LIBoxParity.DataSource = parity;
                cmb_LIBoxParity.SelectedIndex = Convert.ToInt16(Parity.None);
                // DataBits
                int[] dataBits = { 8 };
                cmb_LIBoxDataBits.DataSource = dataBits;
                // StopBits
                string[] stopBits = Enum.GetNames(typeof(StopBits));
                cmb_LIBoxStopBits.DataSource = stopBits;
                cmb_LIBoxStopBits.SelectedIndex = Convert.ToInt16(StopBits.One);
                // Handshake
                string[] handshake = Enum.GetNames(typeof(Handshake));
                cmb_LIBoxHandshake.DataSource = handshake;
                cmb_LIBoxHandshake.SelectedIndex = Convert.ToInt16(Handshake.None);
            }
            catch (Exception e)
            {
                MessageBox.Show(e.Message);
            }
        }

        private void LI_ConfigureSerialPort(SerialPort LISerialPort)
        {
            try
            {
                if (LISerialPort.IsOpen) LISerialPort.Close();
                LISerialPort.PortName = (string)cmb_LIBoxPortName.SelectedItem;
                LISerialPort.BaudRate = (int)cmb_LIBoxBaudRate.SelectedItem;
                LISerialPort.Parity = (Parity)cmb_LIBoxParity.SelectedIndex;
                LISerialPort.DataBits = (int)cmb_LIBoxDataBits.SelectedItem;
                LISerialPort.StopBits = (StopBits)cmb_LIBoxStopBits.SelectedIndex;
                LISerialPort.Handshake = (Handshake)cmb_LIBoxHandshake.SelectedIndex;
                LISerialPort.ReadTimeout = int.Parse(txt_LIBoxReadTimeout.Text);
                LISerialPort.WriteTimeout = int.Parse(txt_LIBoxWriteTimeout.Text);
                LISerialPort.Open();
            }
            catch (Exception e)
            {
                MessageBox.Show(e.Message);
            }
        }

        private void btn_LIBoxConfigureSerialPort_Click(object sender, EventArgs e)
        {
            LI_ConfigureSerialPort(LISerialPort);
        }

        private void btn_LIBoxFindSerialPorts_Click(object sender, EventArgs e)
        {
            LI_FindSerialPorts();
        }

        public bool LI_ReadLine(SerialPort LISerialPort, ref string message)
        {
            try
            {
                char[] charBuffer = new char[10];
                //message = LISerialPort.ReadLine();
                //message = LISerialPort.ReadTo(readto);
                System.Threading.Thread.Sleep(100);
                LISerialPort.Read(charBuffer, 0, 10);
                foreach (char c in charBuffer)
                    if (c != '\0') message += c;
                return true;
            }
            catch (Exception e)
            {
                MessageBox.Show(e.Message);
                return false;
            }
        }

        public bool LI_WriteLine(SerialPort LISerialPort, string message)
        {
            try
            {
                LISerialPort.WriteLine(message);
                return true;
            }
            catch (Exception e)
            {
                MessageBox.Show(e.Message);
                return false;
            }
        }

        private void btn_LIBoxRead_Click(object sender, EventArgs e)
        {
            string message = "";
            LI_ReadLine(LISerialPort, ref message);
            richTextBoxLIRead.Text += "RX:" + message + "\n";
        }

        private void btn_LIBoxWrite_Click(object sender, EventArgs e)
        {
            LI_WriteLine(LISerialPort, richTextBoxLIWrite.Text);
        }

        private void btn_LIBoxClearRX_Click(object sender, EventArgs e)
        {
            try { LISerialPort.DiscardInBuffer(); richTextBoxLIRead.Clear(); }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }

        private void btn_LIBoxClearTX_Click(object sender, EventArgs e)
        {
            try { LISerialPort.DiscardOutBuffer(); richTextBoxLIWrite.Clear(); }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }

        private void btn_LIBoxInitBox_Click(object sender, EventArgs e)
        {
            string msgRX = "";
            richTextBoxLIBox.Clear();
            LI_WriteReadBack(LISerialPort, "aA", ref msgRX, 1, richTextBoxLIBox);
        }

        private void btn_LIBoxTriggerInternal_Click(object sender, EventArgs e)
        {
            //exit the "active" mode, if any...
            LIBoxActiveOFF();
            //set trigger internal
            string msgTX = "aK";
            string msgRX = "";
            if (LI_WriteReadBack(LISerialPort, msgTX, ref msgRX, 1, richTextBoxLIBox))
                LIBoxActiveON();
        }

        private void btn_LIBoxTriggerExternal_Click(object sender, EventArgs e)
        {
            //exit the "active" mode, if any...
            LIBoxActiveOFF();
            //set trigger external
            string msgTX = "aQ";
            string msgRX = "";
            if (LI_WriteReadBack(LISerialPort, msgTX, ref msgRX, 1, richTextBoxLIBox))
                LIBoxActiveON();
        }

        private void btn_LIBoxSendFile_Click(object sender, EventArgs e)
        {
            if (LIBoxIsActive)
            {
                if (MessageBox.Show("LI LED Active is ON." +
                    "\nIn order to execute a script file, the Active LED will be turned OFF" +
                    "\nDo you want to continue?",
                    "WARNING!", MessageBoxButtons.YesNo) == DialogResult.No) return;
                LIBoxActiveOFF();
            }
            OpenFileDialog myOFD = new OpenFileDialog();
            StreamReader mySR = null;
            myOFD.Filter = "LI files (*.txt)|*.txt|All files (*.*)|*.*";
            myOFD.FilterIndex = 1;
            myOFD.RestoreDirectory = true;
            if (myOFD.ShowDialog() == DialogResult.OK)
            {
                try
                {
                    mySR = File.OpenText(myOFD.FileName);
                    string msgTX = "";
                    string msgRX = "";
                    richTextBoxLIBox.Clear();
                    while (!mySR.EndOfStream)
                    {
                        msgTX = mySR.ReadLine();
                        msgRX = "";
                        switch (msgTX.Substring(0, 2))
                        {
                            case "aA":
                            case "aE":
                            case "aD":
                            case "aO":
                            case "aB":
                                LI_WriteReadBack(LISerialPort, msgTX, ref msgRX, 1, richTextBoxLIBox);
                                break;
                            case "aK":
                            case "aQ":
                                if (LI_WriteReadBack(LISerialPort, msgTX, ref msgRX, 1, richTextBoxLIBox))
                                    LIBoxActiveON();
                                break;
                            case "_X":
                                if (LIBoxIsActive)
                                    LIBoxActiveOFF();
                                break;
                            case "aC":
                            case "aH":
                            case "aI":
                                LI_WriteReadBack(LISerialPort, msgTX, ref msgRX, 2, richTextBoxLIBox);
                                break;
                            default:
                                MessageBox.Show("Unknown number of 'K's in response to " + msgTX + " message.");
                                break;
                        }
                    }
                }
                catch (Exception ex) { MessageBox.Show(ex.Message); }
                finally { mySR.Close(); }
            }
        }

        private void btn_LIBoxLEDSlot_Click(object sender, EventArgs e)
        {
            if (cmb_LIBoxLEDSlot.SelectedIndex < 0 || cmb_LIBoxLEDSlot.SelectedIndex > 21)
            {
                MessageBox.Show("Invalid LED Slot\nOperation aborted");
                return;
            }
            richTextBoxLIBox.Clear();
            string msgRX = "";
            string msgTX = "aE" + (string)cmb_LIBoxLEDSlot.SelectedItem;
            LI_WriteReadBack(LISerialPort, msgTX, ref msgRX, 1, richTextBoxLIBox);
        }

        private void btn_LIBoxLEDPulseWidth_Click(object sender, EventArgs e)
        {
            if (cmb_LIBoxLEDPulseWidth.SelectedIndex < 0 || cmb_LIBoxLEDPulseWidth.SelectedIndex > 7)
            {
                MessageBox.Show("Invalid LED PulseWidth\nOperation aborted");
                return;
            }
            richTextBoxLIBox.Clear();
            string msgRX = "";
            string msgTX = "aD" + cmb_LIBoxLEDPulseWidth.SelectedIndex;
            LI_WriteReadBack(LISerialPort, msgTX, ref msgRX, 1, richTextBoxLIBox);
        }

        private void btn_LIBoxLEDPulseHeight_Click(object sender, EventArgs e)
        {
            try
            {
                string msgRX = "";
                string msgTX = "";
                if (Convert.ToUInt16(txt_LIBoxLEDPulseHeight.Text, 16) < 0 | Convert.ToUInt16(txt_LIBoxLEDPulseHeight.Text, 16) > 0x3FF)
                {
                    MessageBox.Show("Invalid LED PulseHeight\nOperation aborted");
                    return;
                }
                richTextBoxLIBox.Clear();
                string PulseHeight = txt_LIBoxLEDPulseHeight.Text.PadLeft(3, '0').ToLower();
                //sending first command...
                msgRX = "";
                msgTX = "aB" + PulseHeight[0];
                LI_WriteReadBack(LISerialPort, msgTX, ref msgRX, 1, richTextBoxLIBox);
                //sending second command...
                msgRX = "";
                msgTX = "aC" + PulseHeight[1] + "_" + PulseHeight[2];
                LI_WriteReadBack(LISerialPort, msgTX, ref msgRX, 2, richTextBoxLIBox);
                //sending third command...
                msgRX = "";
                msgTX = "aO";
                LI_WriteReadBack(LISerialPort, msgTX, ref msgRX, 1, richTextBoxLIBox);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void btn_LIBoxLEDTriggerRate_Click(object sender, EventArgs e)
        {
            try
            {
                string msgRX = "";
                string msgTX = "";
                if (Convert.ToUInt32(txt_LIBoxLEDTriggerRate.Text, 16) < 0 || Convert.ToUInt32(txt_LIBoxLEDTriggerRate.Text, 16) > 0xFFFF)
                {
                    MessageBox.Show("Invalid LED TriggerRate\nOperation aborted");
                    return;
                }
                if (Convert.ToUInt32(txt_LIBoxLEDTriggerRate.Text, 16) >= 0 && Convert.ToUInt32(txt_LIBoxLEDTriggerRate.Text, 16) <= 0x01FF)
                {
                    if (MessageBox.Show("Setting TriggerRate < 0x1FF can burn the LED\nAre you sure you want to continue?",
                        "WARNING!", MessageBoxButtons.YesNo) == DialogResult.No) return;
                }
                richTextBoxLIBox.Clear();
                string TriggerRate = txt_LIBoxLEDTriggerRate.Text.PadLeft(4, '0').ToLower();
                //sending first command...
                msgRX = "";
                msgTX = "aH" + TriggerRate[0] + "_" + TriggerRate[1];
                LI_WriteReadBack(LISerialPort, msgTX, ref msgRX, 1, richTextBoxLIBox);
                //sending second command...
                msgRX = "";
                msgTX = "aI" + TriggerRate[2] + "_" + TriggerRate[3];
                LI_WriteReadBack(LISerialPort, msgTX, ref msgRX, 2, richTextBoxLIBox);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private bool LI_WriteReadBack(SerialPort serialPort, string msgTX,
            ref string msgRX, int msgRXNKs, RichTextBox rtbDiplay)
        {
            rtbDiplay.Text += "TX:" + msgTX + "\n";
            if (!LI_WriteLine(serialPort, msgTX))
            {
                rtbDiplay.Text += "ERROR : Write method failed for " + msgTX + " command\n";
                return false;
            }
            if (!LI_ReadLine(LISerialPort, ref msgRX))
            {
                rtbDiplay.Text += "ERROR : Read method failed RX:" + msgRX + "\n";
                return false;
            }
            rtbDiplay.Text += "RX:" + msgRX + "\n";
            if (CneckNKsExpected(msgRX, msgRXNKs)) return true;
            else return false;
        }

        private void btn_LIBoxIsActive_Click(object sender, EventArgs e)
        {
            //can only turn OFF the "active" LED
            LIBoxActiveOFF();
        }

        private void LIBoxActiveOFF()
        {
            richTextBoxLIBox.Clear();
            if (LIBoxIsActive)
            {
                //deactivate it!
                string msgRX = "";
                string msgTX = "_X";
                if (LI_WriteReadBack(LISerialPort, msgTX, ref msgRX, 1, richTextBoxLIBox))
                {
                    LIBoxIsActive = false;
                    LIBoxIsActiveChanged();
                }
                return;
            }
        }

        private void LIBoxActiveON()
        {
            LIBoxIsActive = true;
            LIBoxIsActiveChanged();
        }

        private void LIBoxIsActiveChanged()
        {
            if (LIBoxIsActive)
            {
                btn_LIBoxIsActive.Text = "LI Active Is ON";
                btn_LIBoxIsActive.BackColor = Color.LightBlue;
                btn_LIBoxInitBox.Enabled = false;
                btn_LIBoxLEDSlot.Enabled = false;
                btn_LIBoxLEDPulseWidth.Enabled = false;
                btn_LIBoxLEDPulseHeight.Enabled = false;
                btn_LIBoxLEDTriggerRate.Enabled = false;
                return;
            }
            else
            {
                btn_LIBoxIsActive.Text = "LI Active Is OFF";
                btn_LIBoxIsActive.BackColor = Color.Coral;
                btn_LIBoxInitBox.Enabled = true;
                btn_LIBoxLEDSlot.Enabled = true;
                btn_LIBoxLEDPulseWidth.Enabled = true;
                btn_LIBoxLEDPulseHeight.Enabled = true;
                btn_LIBoxLEDTriggerRate.Enabled = true;
                return;
            }
        }

        private bool CneckNKsExpected(string msgRX, int nks)
        {
            try
            {
                StringBuilder str = new StringBuilder("KKKKKKK", 0, nks, nks);
                if (msgRX.CompareTo(str.ToString()) == 0) return true;
                MessageBox.Show("Icorect number of 'K's in response message...");
                return false;
            }
            catch (Exception e)
            {
                MessageBox.Show(e.Message);
                return false;
            }
        }

        #region LI Box Harcoded buttons

        private void btn_LIBoxHardcodedInitLEDSlot_Click(object sender, EventArgs e)
        {
            if (cmb_LIBoxHardcodedLEDSlot.SelectedIndex < 0 || cmb_LIBoxHardcodedLEDSlot.SelectedIndex > 21)
            {
                MessageBox.Show("Invalid LED Slot\nOperation aborted");
                return;
            }
            richTextBoxLIBox.Clear();
            string msgRX = "";
            //string[] msgTX = { "aA", "aE" + (string)cmb_LIBoxHardcodedLEDSlot.SelectedItem, "aD7", "aH0_2", "aI2_0" };
            //int[] msgRXNKs ={ 1, 1, 1, 2, 2 };
            //for(int i=0; i<5;i++)
            //{
            //    msgRX = "";
            //    if (LI_WriteReadBack(LISerialPort, msgTX[i], ref msgRX, richTextBoxLIBox))
            //        CneckNKsExpected(msgRX, msgRXNKs[i]);
            //}
            // brutal way...
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aA", ref msgRX, 1, richTextBoxLIBox);
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aE" + (string)cmb_LIBoxHardcodedLEDSlot.SelectedItem, ref msgRX, 1, richTextBoxLIBox);
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aD7", ref msgRX, 1, richTextBoxLIBox);
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aH0_2", ref msgRX, 2, richTextBoxLIBox);
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aI2_0", ref msgRX, 2, richTextBoxLIBox);
        }

        private void btn_LIBoxHardcodedInitALLSlots_Click(object sender, EventArgs e)
        {
            for (int i = 0; i < cmb_LIBoxHardcodedLEDSlot.Items.Count; i++)
            {
                cmb_LIBoxHardcodedLEDSlot.SelectedIndex = i;
                btn_LIBoxHardcodedInitLEDSlot_Click(null, null);
            }
        }

        private void btn_LIBoxHardcodedZeroPE_Click(object sender, EventArgs e)
        {
            richTextBoxLIBox.Clear();
            string msgRX = ""; if (LIBoxIsActive) LIBoxActiveOFF();
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aB0", ref msgRX, 1, richTextBoxLIBox);
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aC0_0", ref msgRX, 2, richTextBoxLIBox);
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aO", ref msgRX, 1, richTextBoxLIBox);
            msgRX = ""; if (LI_WriteReadBack(LISerialPort, "aQ", ref msgRX, 1, richTextBoxLIBox)) LIBoxActiveON();
        }

        private void btn_LIBoxHardcodedOnePE_Click(object sender, EventArgs e)
        {
            richTextBoxLIBox.Clear();
            string msgRX = ""; if (LIBoxIsActive) LIBoxActiveOFF();
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aB0", ref msgRX, 1, richTextBoxLIBox);
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aC3_8", ref msgRX, 2, richTextBoxLIBox);
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aO", ref msgRX, 1, richTextBoxLIBox);
            msgRX = ""; if (LI_WriteReadBack(LISerialPort, "aQ", ref msgRX, 1, richTextBoxLIBox)) LIBoxActiveON();
        }

        private void btn_LIBoxHardcodedMaxPE_Click(object sender, EventArgs e)
        {
            richTextBoxLIBox.Clear();
            string msgRX = ""; if (LIBoxIsActive) LIBoxActiveOFF();
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aB3", ref msgRX, 1, richTextBoxLIBox);
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aCf_f", ref msgRX, 2, richTextBoxLIBox);
            msgRX = ""; LI_WriteReadBack(LISerialPort, "aO", ref msgRX, 1, richTextBoxLIBox);
            msgRX = ""; if (LI_WriteReadBack(LISerialPort, "aQ", ref msgRX, 1, richTextBoxLIBox)) LIBoxActiveON();
        }

        private void btn_LIBoxHardcoded_X_Click(object sender, EventArgs e)
        {
            if (LIBoxIsActive) LIBoxActiveOFF();
        }

        #endregion

        #endregion

        #region Methods for Gate Alignment using CROC

        private struct FEB_TPDelay
        {
            private uint _CrocAddress;
            private uint _ChannelNumber;
            private Frame.Addresses _FEBAddr;
            private double _TPDelay;
            public double TPDelayRelative;

            public FEB_TPDelay(uint CrocAddress, uint ChannelNumber, Frame.Addresses FEBAddr, double TPDelay)
            {
                _CrocAddress = CrocAddress;
                _ChannelNumber = ChannelNumber;
                _FEBAddr = FEBAddr;
                _TPDelay = TPDelay;
                this.TPDelayRelative = 0;
            }

            public uint CrocAddress { get { return _CrocAddress; } }
            public uint ChannelNumber { get { return _ChannelNumber; } }
            public Frame.Addresses FEBAddr { get { return _FEBAddr; } }
            public double TPDelay { get { return _TPDelay; } }
            public override string ToString()
            {
                return "CROC" + (_CrocAddress >> 16) + " CH" + _ChannelNumber + " " + _FEBAddr.ToString() +
                    " TPDelAbs: " + _TPDelay.ToString("0000000.00") + " TPDelRel: " + TPDelayRelative.ToString("00.00");
            }
        }

        private List<FEB_TPDelay> FEBTPDelayListUpdateRelatives(List<FEB_TPDelay> FEBTPDelayList)
        {
            List<FEB_TPDelay> returnlist = new List<FEB_TPDelay>();
            FEB_TPDelay newfebtpdelay;
            try
            {
                //Find the minimum test point delay time. This is the last feb in the physical chain.
                double TPDelayMin = double.MaxValue;
                foreach (FEB_TPDelay fe in FEBTPDelayList)
                    if (fe.TPDelay < TPDelayMin) TPDelayMin = fe.TPDelay;
                //UpdateRelatives
                foreach (FEB_TPDelay fe in FEBTPDelayList)
                {
                    //newfebtpdelay = new FEB_TPDelay(fe.CrocAddress, fe.ChannelNumber, fe.FEBAddr, fe.TPDelay);
                    newfebtpdelay = fe;
                    newfebtpdelay.TPDelayRelative = fe.TPDelay - TPDelayMin;
                    returnlist.Add(newfebtpdelay);
                }
            }
            catch (Exception e)
            {
                richTextBoxDescription.AppendText(e.Message + "\n");
                richTextBoxDescription.AppendText(e.Source + "\n");
            }
            return returnlist;
        }

        private void PrintDelayList(FEB_TPDelay[] FEBTPDelayList)
        {
            foreach (FEB_TPDelay fe in FEBTPDelayList)
                richTextBoxDescription.AppendText(fe.ToString() + "\n");
        }

        private void SetLoadTimersGateStarts(uint LoadTimer, ushort GateStart, CROC theCroc, CROCFrontEndChannel theChannel)
        {
            foreach (Frame.Addresses feb in theChannel.ChainBoards)
            {
                try
                {
                    FPGAFrame rFrame = new FPGAFrame(feb, Frame.FPGAFunctions.Read, new FrameID());
                    rFrame.Send(theChannel);
                    rFrame.Receive();
                    //write new values
                    FPGAFrame wFrame = new FPGAFrame(feb, Frame.FPGAFunctions.Write, new FrameID());
                    wFrame.Registers = rFrame.Registers;
                    wFrame.Timer = LoadTimer;
                    wFrame.GateStart = GateStart;
                    wFrame.Send(theChannel);
                    wFrame.Receive();
                }
                catch (Exception e)
                {
                    richTextBoxDescription.AppendText(theChannel.Description + ":" + feb + ": Error: " + e.Message + "\n");
                }
            }
        }

        private void SetLoadTimersGateStarts(FEB_TPDelay[] FEB_TPDelayArray, CROC theCroc, CROCFrontEndChannel theChannel)
        {
            foreach (FEB_TPDelay tpdelay in FEB_TPDelayArray)
            {
                try
                {
                    FPGAFrame rFrame = new FPGAFrame(tpdelay.FEBAddr, Frame.FPGAFunctions.Read, new FrameID());
                    rFrame.Send(theChannel);
                    rFrame.Receive();
                    //write new values
                    FPGAFrame wFrame = new FPGAFrame(tpdelay.FEBAddr, Frame.FPGAFunctions.Write, new FrameID());
                    wFrame.Registers = rFrame.Registers;
                    wFrame.Timer -= Convert.ToUInt32(tpdelay.TPDelayRelative / 2.0);
                    wFrame.GateStart -= Convert.ToUInt16(tpdelay.TPDelayRelative / 2.0);
                    wFrame.Send(theChannel);
                    wFrame.Receive();
                }
                catch (Exception e)
                {
                    richTextBoxDescription.AppendText(theChannel.Description + ":" + tpdelay.FEBAddr + ": Error: " + e.Message + "\n");
                }
            }
        }

        private void btn_CROCReportGateDelays_Click(object sender, EventArgs e)
        {
            AlignGateDelays();
        }

        private void btn_CROCReportGateAlignmentsAllCROCsAndChains_Click(object sender, EventArgs e)
        {
            foreach (CROC theCroc in CROCModules)
            {
                foreach (CROCFrontEndChannel theChannel in theCroc.ChannelList)
                {
                    txt_CROCGateDelayLoopChannel.Text = theChannel.ChannelNumber.ToString();
                    AlignGateDelays();
                }
            }
        }

        private void AlignGateDelays()
        {
            tabControl1.SelectTab(tabDescription);
            richTextBoxDescription.Text =
                "\nReporting FEBs' gate alignment based on Test Pulse measurements:\n\n";
            tabControl1.SelectedTab.Refresh();

            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    int NGateDelayLoop = Convert.ToInt16(txt_CROCGateDelayLoopN.Text);
                    TreeNode theNode = treeView1.SelectedNode;
                    CROC theCroc = ((CROC)(theNode.Tag));
                    CROCFrontEndChannel theChannel = (CROCFrontEndChannel)theCroc.ChannelList[Convert.ToUInt16(txt_CROCGateDelayLoopChannel.Text) - 1];
                    List<FEB_TPDelay>[] FEBTPDelayListArray = new List<FEB_TPDelay>[NGateDelayLoop];

                    //Set LoadTimerValue and GateStartValue equal for ALL boards in this channel
                    SetLoadTimersGateStarts(Convert.ToUInt32(txt_CROCGateDelayLoopLoadTimerValue.Text),
                        Convert.ToUInt16(txt_CROCGateDelayLoopGateStartValue.Text), theCroc, theChannel);
                    for (int i = 0; i < NGateDelayLoop; i++)
                    {
                        List<FEB_TPDelay> FEBTPDelayList = new List<FEB_TPDelay>();
                        //LoadTimer
                        theCroc.FastCommandRegister = (ushort)FastCommands.LoadTimer;
                        //Write TP
                        theCroc.ResetAndTestMaskRegister = Convert.ToUInt16(1 << (int)(theChannel.ChannelNumber - 1));
                        //Send TP
                        theCroc.TestPulseRegister = BitConverter.ToUInt16(CROC.TestPulseRegisterValue, 0);
                        //
                        if (MeasureTPDelays(ref FEBTPDelayList, theCroc, theChannel))
                            FEBTPDelayListArray[i] = FEBTPDelayList;
                        else throw new Exception(string.Format(theChannel.Description + " MeasureTPDelays#{0} FAIL. Please try again.", i));
                    }
                    //Write TP=0
                    theCroc.ResetAndTestMaskRegister = 0;
                    //Calculate relative delays and their average value for ALL measurements
                    FEB_TPDelay[] FEB_TPDelayArray = CalculateTPDelasy(FEBTPDelayListArray);
                    //Update new values of FPGAs' Timer and GateStart based on previous calculated delays 
                    SetLoadTimersGateStarts(FEB_TPDelayArray, theCroc, theChannel);
                    //LoadTimer with new settings
                    theCroc.FastCommandRegister = (ushort)FastCommands.LoadTimer;
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private FEB_TPDelay[] CalculateTPDelasy(List<FEB_TPDelay>[] FEBTPDelayListArray)
        {
            //Print ALL measurements: array of lists of FEB_TPDelay structures
            for (int i = 0; i < FEBTPDelayListArray.GetLength(0); i++)
            {
                richTextBoxDescription.AppendText("Measurements #" + i.ToString("000") + "\n");
                FEBTPDelayListArray[i] = FEBTPDelayListUpdateRelatives(FEBTPDelayListArray[i]);
                PrintDelayList(FEBTPDelayListArray[i].ToArray());
            }
            //Calculate Average Values
            //1. Create an array of FEB_TPDelay structures
            FEB_TPDelay[] arr = new FEB_TPDelay[FEBTPDelayListArray[0].Count];
            //2. Initialize FEBTPDelayListAveraged with first measurement of FEBTPDelayListArray
            //arr = FEBTPDelayListArray[0].ToArray();
            for (int j = 0; j < FEBTPDelayListArray[0].Count; j++)
            {
                arr[j] = new FEB_TPDelay(FEBTPDelayListArray[0][j].CrocAddress,
                    FEBTPDelayListArray[0][j].ChannelNumber, FEBTPDelayListArray[0][j].FEBAddr, 0);
                arr[j].TPDelayRelative = FEBTPDelayListArray[0][j].TPDelayRelative;
            }

            //3. Sum the TPDelayRelative values over ALL measurements
            for (int i = 1; i < FEBTPDelayListArray.GetLength(0); i++)
                for (int j = 0; j < FEBTPDelayListArray[0].Count; j++)
                {
                    if ((arr[j].CrocAddress == FEBTPDelayListArray[i][j].CrocAddress) &
                        (arr[j].ChannelNumber == FEBTPDelayListArray[i][j].ChannelNumber) &
                        (arr[j].FEBAddr == FEBTPDelayListArray[i][j].FEBAddr))
                        arr[j].TPDelayRelative += FEBTPDelayListArray[i][j].TPDelayRelative;
                    else
                        richTextBoxDescription.AppendText("i=" + i.ToString("000") + "j=" + j.ToString("000") +
                            " statistic calculation error for arr \n");
                }
            //4. Divide the TPDelayRelative with the number of measurements
            for (int j = 0; j < arr.GetLength(0); j++)
                arr[j].TPDelayRelative /= FEBTPDelayListArray.GetLength(0);
            //5. Print results
            richTextBoxDescription.AppendText("Averaged delays\n");
            PrintDelayList(arr);
            //
            return arr;
        }

        private bool MeasureTPDelays(ref List<FEB_TPDelay> FEBTPDelayList, CROC theCroc, CROCFrontEndChannel theChannel)
        {
            foreach (Frame.Addresses feb in theChannel.ChainBoards)
            {
                try
                {
                    FPGAFrame theFrame = new FPGAFrame(feb, Frame.FPGAFunctions.Read, new FrameID());
                    theFrame.Send(theChannel);
                    theFrame.Receive();
                    if (theFrame.TestPulse2Bit == 0) FEBTPDelayList.Add(new FEB_TPDelay(
                        theCroc.BaseAddress, theChannel.ChannelNumber, feb, theFrame.TestPulseCount + 1));
                    else FEBTPDelayList.Add(new FEB_TPDelay(
                        theCroc.BaseAddress, theChannel.ChannelNumber, feb, theFrame.TestPulseCount + 0.25 * theFrame.TestPulse2Bit));
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(theChannel.Description + ":" + feb + ": Error: " + ex.Message + "\n");
                    return false;
                }
            }
            return true;
        }

        #endregion

        #region Methods for Gate Alignment using CRIM

        private void btn_CRIMReportGateAlignmentsAllCROCs_Click(object sender, EventArgs e)
        {
            MessageBox.Show("Under Construction..."); return;
            //try
            //{
            //    TreeNode theNode = treeView1.SelectedNode;
            //    CRIM theCrim = ((CRIM)(theNode.Tag));

            //    tabControl1.SelectTab(tabDescription);
            //    richTextBoxDescription.Text = string.Format(
            //        "\nReporting FEBs' gate alignment based on {0} Test Pulse measurements:\n\n", theCrim.Description);
            //    tabControl1.SelectedTab.Refresh();

            //    if (!ConfigureCRIMForGateAlignment(theCrim, 100, 50)) return;

            //    theCrim.SingleSeqStart();


            //}
            //catch (Exception ex)
            //{
            //    richTextBoxDescription.AppendText(ex.Message + "\n");
            //    MessageBox.Show(ex.Message);
            //}
        }

        public bool ConfigureCRIMForGateAlignment(CRIM theCrim, ushort GateWidth, ushort TCALBDelay)
        {
            bool success = false;
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    theCrim.TimingMode = CRIM.TimingModes.Internal;
                    theCrim.Frequency = 0; //no frequency selected
                    theCrim.GateWidth = GateWidth;
                    theCrim.TCALBDelay = TCALBDelay;
                    success = true;
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
            return success;
        }

        #endregion

        #region Methods for Write/Read to/from CRIM

        private void btn_CRIMAdvancedGUI_Click(object sender, EventArgs e)
        {
            AdvancedGUI((Button)sender, tabControlCRIMModules);
        }

        private void CrimClearLabels()
        {
            foreach (TabPage tabpage in tabControlCRIMModules.TabPages)
            {
                foreach (Control c in tabpage.Controls)
                {
                    ClearControl(c);
                    if (c is GroupBox)
                        foreach (Control cc in c.Controls)
                            ClearControl(cc);
                }
            }
        }

        #region Timing Module

        private void btn_CRIMTimingModeWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    theCrim.TimingMode = (CRIM.TimingModes)Enum.Parse(typeof(CRIM.TimingModes), cmb_CRIMTimingMode.SelectedItem.ToString());
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingModeRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    cmb_CRIMTimingMode.SelectedIndex = cmb_CRIMTimingMode.FindString(theCrim.TimingMode.ToString());
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingFrequencyWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    theCrim.TimingFrequency = (CRIM.TimingFrequencies)Enum.Parse(typeof(CRIM.TimingFrequencies), cmb_CRIMTimingFrequency.SelectedItem.ToString());
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingFrequencyRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    cmb_CRIMTimingFrequency.SelectedIndex = cmb_CRIMTimingFrequency.FindString(theCrim.TimingFrequency.ToString());
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingGateWidthWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    if (theCrim.TimingMode == CRIM.TimingModes.Internal)
                    {
                        theCrim.GateWidth = ushort.Parse(txt_CRIMTimingGateWidth.Text);
                        theCrim.CounterResetEnableInINTMode = chk_CRIMTimingCNTRSTEnableInINTMode.Checked;
                    }
                    else
                    {
                        if (MessageBox.Show("CRIM must be switched to \"Internal\" mode. Do you want to continue?",
                            "CRIM", MessageBoxButtons.OKCancel) == DialogResult.OK)
                        {
                            theCrim.TimingMode = CRIM.TimingModes.Internal;
                            theCrim.GateWidth = ushort.Parse(txt_CRIMTimingGateWidth.Text);
                            theCrim.CounterResetEnableInINTMode = chk_CRIMTimingCNTRSTEnableInINTMode.Checked;
                        }
                    }
                    cmb_CRIMTimingMode.SelectedIndex = cmb_CRIMTimingMode.FindString(theCrim.TimingMode.ToString());
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingGateWidthRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    txt_CRIMTimingGateWidth.Text = theCrim.GateWidth.ToString();
                    chk_CRIMTimingCNTRSTEnableInINTMode.Checked = theCrim.CounterResetEnableInINTMode;
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingTCALBWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    if (theCrim.TimingMode == CRIM.TimingModes.Internal)
                        theCrim.TCALBDelay = ushort.Parse(txt_CRIMTimingTCALB.Text);
                    else
                    {
                        if (MessageBox.Show("CRIM must be switched to \"Internal\" mode. Do you want to continue?",
                            "CRIM", MessageBoxButtons.OKCancel) == DialogResult.OK)
                        {
                            theCrim.TimingMode = CRIM.TimingModes.Internal;
                            theCrim.TCALBDelay = ushort.Parse(txt_CRIMTimingTCALB.Text);
                        }
                    }
                    cmb_CRIMTimingMode.SelectedIndex = cmb_CRIMTimingMode.FindString(theCrim.TimingMode.ToString());

                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingTCALBRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    txt_CRIMTimingTCALB.Text = theCrim.TCALBDelay.ToString();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingSendTrigger_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    theCrim.TriggerPulse();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingSendTCALB_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    if (theCrim.TimingMode == CRIM.TimingModes.External)
                        theCrim.TCALBPulse();
                    else
                    {
                        if (MessageBox.Show("CRIM must be switched to \"External\" mode. Do you want to continue?",
                            "CRIM", MessageBoxButtons.OKCancel) == DialogResult.OK)
                        {
                            theCrim.TimingMode = CRIM.TimingModes.External;
                            theCrim.TCALBPulse();
                        }
                    }
                    cmb_CRIMTimingMode.SelectedIndex = cmb_CRIMTimingMode.FindString(theCrim.TimingMode.ToString());
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingSendStartGate_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    if (theCrim.TimingMode == CRIM.TimingModes.External)
                        theCrim.StartGate();
                    else
                    {
                        if (MessageBox.Show("CRIM must be switched to \"External\" mode. Do you want to continue?",
                            "CRIM", MessageBoxButtons.OKCancel) == DialogResult.OK)
                        {
                            theCrim.TimingMode = CRIM.TimingModes.External;
                            theCrim.StartGate();
                        }
                    }
                    cmb_CRIMTimingMode.SelectedIndex = cmb_CRIMTimingMode.FindString(theCrim.TimingMode.ToString());
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingSendStopGate_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    if (theCrim.TimingMode == CRIM.TimingModes.External)
                        theCrim.EndGate();
                    else
                    {
                        if (MessageBox.Show("CRIM must be switched to \"External\" mode. Do you want to continue?",
                            "CRIM", MessageBoxButtons.OKCancel) == DialogResult.OK)
                        {
                            theCrim.TimingMode = CRIM.TimingModes.External;
                            theCrim.EndGate();
                        }
                    }
                    cmb_CRIMTimingMode.SelectedIndex = cmb_CRIMTimingMode.FindString(theCrim.TimingMode.ToString());
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingSS_CNTRST_SGATE_TCALB_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    if ((theCrim.TimingMode == CRIM.TimingModes.Internal) && (theCrim.TimingFrequency == CRIM.TimingFrequencies.None))
                        theCrim.SingleSeqStart();
                    else
                    {
                        if (MessageBox.Show(string.Format("CRIM must be switched to \"{0}\" mode and Frequency set to \n{1}\". Do you want to continue?",
                            CRIM.TimingModes.Internal, CRIM.TimingFrequencies.None), "CRIM", MessageBoxButtons.OKCancel) == DialogResult.OK)
                        {
                            theCrim.TimingMode = CRIM.TimingModes.Internal;
                            theCrim.TimingFrequency = CRIM.TimingFrequencies.None;
                            theCrim.SingleSeqStart();
                        }
                    }
                    cmb_CRIMTimingMode.SelectedIndex = cmb_CRIMTimingMode.FindString(theCrim.TimingMode.ToString());
                    cmb_CRIMTimingFrequency.SelectedIndex = cmb_CRIMTimingFrequency.FindString(theCrim.TimingFrequency.ToString());

                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingSS_CNTRST_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    if (theCrim.TimingMode == CRIM.TimingModes.External)
                        theCrim.CounterReset();
                    else
                    {
                        if (MessageBox.Show("CRIM must be switched to \"External\" mode. Do you want to continue?",
                            "CRIM", MessageBoxButtons.OKCancel) == DialogResult.OK)
                        {
                            theCrim.TimingMode = CRIM.TimingModes.External;
                            theCrim.CounterReset();
                        }
                    }
                    cmb_CRIMTimingMode.SelectedIndex = cmb_CRIMTimingMode.FindString(theCrim.TimingMode.ToString());
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingSeqControlLatchReset_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    theCrim.SequencerControlLatchReset();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingTestRegisterWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    theCrim.TestRegister = ushort.Parse(txt_CRIMTimingTestRegister.Text);
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingTestRegisterRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    txt_CRIMTimingTestRegister.Text = theCrim.TestRegister.ToString();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMTimingGateTimeRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    lbl_CRIMTimingGateTimeRead.Text =string.Format("{0}, 0x{1}", theCrim.GateTime.ToString().Trim(), theCrim.GateTime.ToString("X8"));
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        #endregion Timing Module

        #region DAQ Module

        private void btn_CRIMDAQModeRegisterWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    theCrim.RetransmitEnabled = chk_CRIMDAQModeRegisterRetransmitEn.Checked;
                    theCrim.SendMessageEnabled = chk_CRIMDAQModeRegisterSendEn.Checked;
                    theCrim.CRCEnabled = chk_CRIMDAQModeRegisterCRCEn.Checked;
                    theCrim.FETriggerEnabled = chk_CRIMDAQModeRegisterFETriggEn.Checked;
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMDAQModeRegisterRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    chk_CRIMDAQModeRegisterRetransmitEn.Checked = theCrim.RetransmitEnabled;
                    chk_CRIMDAQModeRegisterSendEn.Checked = theCrim.SendMessageEnabled;
                    chk_CRIMDAQModeRegisterCRCEn.Checked = theCrim.CRCEnabled;
                    chk_CRIMDAQModeRegisterFETriggEn.Checked = theCrim.FETriggerEnabled;
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMDAQDPMRegisterResetPointer_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    theCrim.Channel.ResetPointer();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMDAQDPMRegisterReadPointer_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    lbl_CRIMDAQDPMRegisterReadPointer.Text = theCrim.Channel.Pointer.ToString();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMDAQResetFIFORegister_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    ((CRIMFrontEndChannel)(theCrim.Channel)).ResetFIFO();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMDAQReadTimingCommandRegister_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    lbl_CRIMDAQReadTimingCommandRegister.Text = string.Format("0x{0:X2}", theCrim.TimingCommandReceived);
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMDAQSendSyncRegister_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    ((CRIMFrontEndChannel)(theCrim.Channel)).SendSynch();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMDAQStatusRegisterClear_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    theCrim.Channel.ClearStatus();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMDAQStatusRegisterRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    CROCFrontEndChannel.StatusBits theStatus = theCrim.Channel.StatusRegister;
                    lbl_CRIMDAQStatusRegisterRead.Text = "0x" + ((short)theStatus).ToString("X4");
                    lbl_CRIMDAQStatusMsgSent.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.MessageSent);
                    lbl_CRIMDAQStatusMsgRcv.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.MessageReceived);
                    lbl_CRIMDAQStatusCRCErr.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.CRCError);
                    lbl_CRIMDAQStatusTimeoutErr.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.TimeoutError);
                    lbl_CRIMDAQStatusFIFONotEmpty.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.FIFONotEmpty);
                    lbl_CRIMDAQStatusFIFOFull.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.FIFOFull);
                    lbl_CRIMDAQStatusDPMFull.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.DPMFull);
                    lbl_CRIMDAQStatusUnusedBit7.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.UnusedBit7);
                    lbl_CRIMDAQStatusRFPresent.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.RFPresent);
                    lbl_CRIMDAQStatusSerializerSync.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.SerializerSynch);
                    lbl_CRIMDAQStatusDeserializerLock.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.DeserializerLock);
                    lbl_CRIMDAQStatusUnusedBit11.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.UnusedBit11);
                    lbl_CRIMDAQStatusPLLLock.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.PLLLocked);
                    lbl_CRIMDAQStatusTestPulseRcv.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.TestPulseReceived);
                    lbl_CRIMDAQStatusFERebootRcv.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.ResetReceived);
                    lbl_CRIMDAQStatusEncodedCmdRcv.Text = CheckStatusBit(theStatus, CROCFrontEndChannel.StatusBits.EncodedCommandReceived);
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMDAQFrameFIFORegisterAppendMessage_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    txt_CRIMDAQFrameFIFORegisterAppendMessage.Text = txt_CRIMDAQFrameFIFORegisterAppendMessage.Text.ToUpper();
                    AppendMessage(txt_CRIMDAQFrameFIFORegisterAppendMessage.Text, theCrim.Channel);
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMDAQFrameFIFORegisterWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    theCrim.Channel.WriteMessageCRIM();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMDAQFrameSendRegister_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    theCrim.Channel.SendMessage();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMDAQFrameReadDPMBytes_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    int responseLength = Convert.ToInt32(txt_CRIMDAQFrameReadDPMBytes.Text);
                    if ((2 <= responseLength) & (responseLength <= CROCFrontEndChannel.MemoryMaxSize))
                        rtb_CRIMDAQFrameReadDPMBytes.Text = DisplayMessage(theCrim.Channel.ReadMemoryCRIM(responseLength), responseLength);
                    else
                        MessageBox.Show("attempt to read more than maximum DPM depth = " +
                            CROCFrontEndChannel.MemoryMaxSize + "or less than 2\nOperation aborted");
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        #endregion DAQ Module

        #region Interrupter Module

        private void btn_CRIMInterrupterMaskWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    txt_CRIMInterrupterMask.Text = txt_CRIMInterrupterMask.Text.PadLeft(2, '0');
                    theCrim.InterruptMask = byte.Parse(txt_CRIMInterrupterMask.Text, System.Globalization.NumberStyles.HexNumber);
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }
        
        private void btn_CRIMInterrupterMaskRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    txt_CRIMInterrupterMask.Text = theCrim.InterruptMask.ToString("X2");
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMInterrupterStatusWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    txt_CRIMInterrupterStatus.Text = txt_CRIMInterrupterStatus.Text.PadLeft(2, '0');
                    theCrim.InterruptStatus = byte.Parse(txt_CRIMInterrupterStatus.Text, System.Globalization.NumberStyles.HexNumber);
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMInterrupterStatusRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    txt_CRIMInterrupterStatus.Text = theCrim.InterruptStatus.ToString("X2");
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMInterrupterConfigWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    txt_CRIMInterrupterLevels.Text = txt_CRIMInterrupterLevels.Text.PadLeft(2, '0');
                    byte IRQLevel = Convert.ToByte(txt_CRIMInterrupterLevels.Text, 16);
                    if (IRQLevel < 1 | IRQLevel > 7) throw new ArgumentOutOfRangeException("IRQ Level must be integer from 1 to 7");
                    theCrim.InterruptConfig = (byte)(Convert.ToByte(chk_CRIMInterrupterGIE.Checked) << 7 | IRQLevel);
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMInterrupterConfigRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    byte InterruptConfig = theCrim.InterruptConfig;
                    txt_CRIMInterrupterLevels.Text = Convert.ToString(InterruptConfig & 0x07, 16).PadLeft(2, '0');
                    chk_CRIMInterrupterGIE.Checked = Convert.ToBoolean(InterruptConfig >> 7);
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMInterrupterClearInterrupts_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    theCrim.InterruptClear();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMInterrupterVectInpWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    byte[] VectInpValues = new byte[8];
                    VectInpValues[0] = Convert.ToByte(txt_CRIMInterrupterVectInp0.Text, 16);
                    VectInpValues[1] = Convert.ToByte(txt_CRIMInterrupterVectInp1.Text, 16);
                    VectInpValues[2] = Convert.ToByte(txt_CRIMInterrupterVectInp2.Text, 16);
                    VectInpValues[3] = Convert.ToByte(txt_CRIMInterrupterVectInp3.Text, 16);
                    VectInpValues[4] = Convert.ToByte(txt_CRIMInterrupterVectInp4.Text, 16);
                    VectInpValues[5] = Convert.ToByte(txt_CRIMInterrupterVectInp5.Text, 16);
                    VectInpValues[6] = Convert.ToByte(txt_CRIMInterrupterVectInp6.Text, 16);
                    VectInpValues[7] = Convert.ToByte(txt_CRIMInterrupterVectInp7.Text, 16);
                    theCrim.InterruptVectors = VectInpValues;
                    txt_CRIMInterrupterVectInp0.Text = txt_CRIMInterrupterVectInp0.Text.PadLeft(2, '0');
                    txt_CRIMInterrupterVectInp1.Text = txt_CRIMInterrupterVectInp1.Text.PadLeft(2, '0');
                    txt_CRIMInterrupterVectInp2.Text = txt_CRIMInterrupterVectInp2.Text.PadLeft(2, '0');
                    txt_CRIMInterrupterVectInp3.Text = txt_CRIMInterrupterVectInp3.Text.PadLeft(2, '0');
                    txt_CRIMInterrupterVectInp4.Text = txt_CRIMInterrupterVectInp4.Text.PadLeft(2, '0');
                    txt_CRIMInterrupterVectInp5.Text = txt_CRIMInterrupterVectInp5.Text.PadLeft(2, '0');
                    txt_CRIMInterrupterVectInp6.Text = txt_CRIMInterrupterVectInp6.Text.PadLeft(2, '0');
                    txt_CRIMInterrupterVectInp7.Text = txt_CRIMInterrupterVectInp7.Text.PadLeft(2, '0');
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_CRIMInterrupterVectInpRead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    byte[] VectInpValues = theCrim.InterruptVectors;
                    txt_CRIMInterrupterVectInp0.Text = VectInpValues[0].ToString("X2");
                    txt_CRIMInterrupterVectInp1.Text = VectInpValues[1].ToString("X2");
                    txt_CRIMInterrupterVectInp2.Text = VectInpValues[2].ToString("X2");
                    txt_CRIMInterrupterVectInp3.Text = VectInpValues[3].ToString("X2");
                    txt_CRIMInterrupterVectInp4.Text = VectInpValues[4].ToString("X2");
                    txt_CRIMInterrupterVectInp5.Text = VectInpValues[5].ToString("X2");
                    txt_CRIMInterrupterVectInp6.Text = VectInpValues[6].ToString("X2");
                    txt_CRIMInterrupterVectInp7.Text = VectInpValues[7].ToString("X2");
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText("\n" + ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        #endregion Interrupter Module

        # region LoopQuery

        private void btn_CRIMFELoopQueryConfigure_Click(object sender, EventArgs e)
        {
            cmb_CRIMTimingMode.SelectedIndex = cmb_CRIMTimingMode.FindString(CRIM.TimingModes.DAQ.ToString(), 0);
            cmb_CRIMTimingFrequency.SelectedIndex = cmb_CRIMTimingFrequency.FindString(CRIM.TimingFrequencies.None.ToString(), 0);
            btn_CRIMTimingModeWrite_Click(sender, e);
            btn_CRIMTimingFrequencyWrite_Click(sender, e);
            chk_CRIMDAQModeRegisterRetransmitEn.Checked = true;
            chk_CRIMDAQModeRegisterSendEn.Checked = false;
            chk_CRIMDAQModeRegisterCRCEn.Checked = false;
            chk_CRIMDAQModeRegisterFETriggEn.Checked = true;
            btn_CRIMDAQModeRegisterWrite_Click(sender, e);
        }
        
        private bool MatchCROC(CROC croc)
        {
            return croc.BaseAddress == uint.Parse(txt_CRIMFELoopQueryCrocBaseAddr.Text) << 16;
        }

        private void btn_CRIMFELoopQueryDoQuery_Click(object sender, EventArgs e)
        {
            if (btn_CRIMFELoopQueryDoQuery.Text == "START Query FEs (N times)")
            {
                btn_CRIMFELoopQueryDoQuery.Text = "STOP Query FEs (N times)";
                btn_CRIMFELoopQueryDoQuery.BackColor = Color.LightBlue;
                CRIMFELoopQuery();
                btn_CRIMFELoopQueryDoQuery.Text = "START Query FEs (N times)";
                btn_CRIMFELoopQueryDoQuery.BackColor = Color.Coral;
                return;
            }
            else
            {
                btn_CRIMFELoopQueryDoQuery.Text = "START Query FEs (N times)";
                return;
            }
        }

        private void CRIMFELoopQuery()
        {
            uint iTry=0;
            this.Cursor = Cursors.WaitCursor;
            lock (this)
            {
                vmeDone.WaitOne();
                string msg = "";
                try
                {
                    rtb_CRIMFELoopQueryDisplay.Clear();
                    CRIM theCrim = ((CRIM)(treeView1.SelectedNode.Tag));
                    //CROC theCroc = CROCModules.Find(delegate(CROC croc) 
                    //    { return croc.BaseAddress == uint.Parse(txt_CRIMFELoopQueryCrocBaseAddr.Text) << 16; });
                    CROC theCroc = CROCModules.Find(MatchCROC);
                    if (theCroc == null)
                        throw new ArgumentNullException(string.Format("CROC {0} is not present in the hardware. Operation abborted\n", txt_CRIMFELoopQueryCrocBaseAddr.Text));
                    uint NTry = uint.Parse(txt_CRIMFELoopQueryNTimes.Text);
                    prgStatus.Maximum = (int)NTry;
                    msg = string.Format("FE Query : Begin {0}\n", DateTime.Now);
                    rtb_CRIMFELoopQueryDisplay.Text = msg; Metadata.MetaData.log.AddToLog(msg);
                    for (iTry = 0; iTry < NTry; iTry++)
                    {
                        //msg = TestCodeForAllFastCommandCombinations(iTry, msg, theCroc);
                        //clear the status of CRIM_DAQ 
                        theCrim.Channel.ClearStatus();
                        //check the status of CRIM_DAQ
                        CROCFrontEndChannel.StatusBits crimStatus = theCrim.Channel.StatusRegister;
                        if (crimStatus != (CROCFrontEndChannel.StatusBits.PLLLocked |
                            CROCFrontEndChannel.StatusBits.DeserializerLock |
                            CROCFrontEndChannel.StatusBits.SerializerSynch |
                            CROCFrontEndChannel.StatusBits.RFPresent))
                        {
                            msg = string.Format("{0} {1} DAQ status register can not be cleared properly : {2}\n", iTry, DateTime.Now, crimStatus); 
                            rtb_CRIMFELoopQueryDisplay.AppendText(msg); Metadata.MetaData.log.AddToLog(msg);
                            if ((crimStatus & CROCFrontEndChannel.StatusBits.EncodedCommandReceived) == CROCFrontEndChannel.StatusBits.EncodedCommandReceived)
                            {
                                msg = string.Format("TimingCommandReceived = 0x{0}\n", theCrim.TimingCommandReceived.ToString("X2"));
                                rtb_CRIMFELoopQueryDisplay.AppendText(msg); Metadata.MetaData.log.AddToLog(msg);
                            }
                        }
                        //reset DPM Pointer of CRIM_DAQ 
                        theCrim.Channel.ResetPointer();
                        //check DPM Pointer of CRIM_DAQ
                        if (theCrim.Channel.Pointer != 0)
                        {
                            msg = string.Format("{0} {1} DAQ pointer register can not be reset properly : {2}\n", iTry, DateTime.Now, theCrim.Channel.Pointer);
                            rtb_CRIMFELoopQueryDisplay.AppendText(msg); Metadata.MetaData.log.AddToLog(msg);
                        }
                        //send the fast command QueryFPGA from the CROC that owns the FE Boards' Loop 
                        theCroc.FastCommandRegister = (ushort)FastCommands.QueryFPGA;
                        //check the status of CRIM_DAQ 
                        crimStatus = theCrim.Channel.StatusRegister;
                        if (crimStatus != (CROCFrontEndChannel.StatusBits.EncodedCommandReceived |
                            CROCFrontEndChannel.StatusBits.PLLLocked |
                            CROCFrontEndChannel.StatusBits.DeserializerLock |
                            CROCFrontEndChannel.StatusBits.SerializerSynch |
                            CROCFrontEndChannel.StatusBits.RFPresent))
                        {
                            msg = string.Format("{0} {1} DAQ status register ERROR after FastCommands.QueryFPGA  : {2}\n", iTry, DateTime.Now, crimStatus);
                            rtb_CRIMFELoopQueryDisplay.AppendText(msg); Metadata.MetaData.log.AddToLog(msg);
                        }
                        //read the decoded timing command register of CRIM_DAQ 
                        byte theTimingCommandReceived = theCrim.TimingCommandReceived;
                        if (theTimingCommandReceived != (byte)FastCommands.QueryFPGA)
                        {
                            msg = string.Format("{0} {1} DAQ fast cmd register ERROR unexpected value : 0x{2}\n",
                                iTry, DateTime.Now, theTimingCommandReceived.ToString("X2"));
                            rtb_CRIMFELoopQueryDisplay.AppendText(msg); Metadata.MetaData.log.AddToLog(msg);
                        }
                        //read DPM Pointer of CRIM_DAQ
                        ushort nFEs = theCrim.Channel.Pointer;
                        if (nFEs == 0)
                        {
                            msg = string.Format("{0} {1} NO FEs present on loop\n", iTry, DateTime.Now);
                            rtb_CRIMFELoopQueryDisplay.AppendText(msg); Metadata.MetaData.log.AddToLog(msg);
                        }
                        else
                        {
                            //read DPM content
                            byte[] response = theCrim.Channel.ReadMemoryCRIM(nFEs);
                            StringBuilder FEsFound = new StringBuilder();
                            for (int iFE = 0; iFE < nFEs; iFE++) FEsFound.Append(string.Format("{0} ", (Frame.Addresses)response[iFE]));
                            if ((!chk_CRIMFELoopQueryMatch.Checked) || (FEsFound.ToString().Trim() != txt_CRIMFELoopQueryMatch.Text.Trim()))
                            {
                                msg = string.Format("{0} {1} Found : {2}\n", iTry, DateTime.Now, FEsFound.ToString());
                                rtb_CRIMFELoopQueryDisplay.AppendText(msg); Metadata.MetaData.log.AddToLog(msg);
                            }
                        }
                        ProgressReport(null, new ProgressChangedEventArgs((int)iTry, string.Format("Loop Query")));
                        if (btn_CRIMFELoopQueryDoQuery.Text == "START Query FEs (N times)") throw new Exception("User aborted operation");
                    }
                }
                catch (Exception ex)
                {
                    msg = "\ni=" + iTry + " " +  ex.Message + "\n";

                    //msg = "\n" + ex.Message + "\n";
                    rtb_CRIMFELoopQueryDisplay.AppendText(msg); Metadata.MetaData.log.AddToLog(msg);
                    richTextBoxDescription.AppendText(msg);
                    //MessageBox.Show(ex.Message);
                }
                finally
                {
                    msg = string.Format("FE Query : End {0}", DateTime.Now);
                    rtb_CRIMFELoopQueryDisplay.AppendText(msg); Metadata.MetaData.log.AddToLog(msg);
                    vmeDone.Set();
                }
            }
            this.Cursor = Cursors.Arrow;
        }
        
        private string TestCodeForAllFastCommandCombinations(uint iTry, string msg, CROC theCroc)
        {
            ////TEST CODE FOR ALL FAST COMMANDS COMBINATIONS
            CROCFrontEndChannel.StatusBits crocStatus;
            CROCFrontEndChannel.StatusBits crocStatusOK = CROCFrontEndChannel.StatusBits.RFPresent |
                    CROCFrontEndChannel.StatusBits.SerializerSynch |
                    CROCFrontEndChannel.StatusBits.DeserializerLock |
                    CROCFrontEndChannel.StatusBits.PLLLocked |
                    CROCFrontEndChannel.StatusBits.TestPulseReceived |
                    CROCFrontEndChannel.StatusBits.MessageSent |
                    CROCFrontEndChannel.StatusBits.MessageReceived;
            Frame.Addresses theFEBoard = Frame.Addresses.FE12;
            IFrontEndChannel theCROCChannel = theCroc.Channel(CROC.Channels.Ch1);
            FPGAFrame theFrame = new FPGAFrame(theFEBoard, Frame.FPGAFunctions.Read, new FrameID());
            int msWait = 100;
            ushort iFastCmd;
            //1. Send a FAST CMD and check STATUS
            iFastCmd = (ushort)((ushort)iTry | 0x81);
            theCroc.FastCommandRegister = iFastCmd;
            System.Threading.Thread.Sleep(msWait);
            crocStatus = theCROCChannel.StatusRegister;
            if (crocStatus != crocStatusOK)
            {
                msg = string.Format("{0} CROC stat after FAST CMD: \n{1}\n0x{2}\n", iTry, crocStatus, iFastCmd.ToString("X").PadLeft(2, '0'));
                rtb_CRIMFELoopQueryDisplay.AppendText(msg); Metadata.MetaData.log.AddToLog(msg);
            }
            //2. Wait for FEBs to recover after CLK PLL distorsion
            //System.Threading.Thread.Sleep(msWait);
            //3. Do the usual READ FPGA FRAME and check STATUS
            theCROCChannel.Reset();
            theFrame.Send(theCROCChannel);
            System.Threading.Thread.Sleep(1);
            crocStatus = theCROCChannel.StatusRegister;
            if (crocStatus != crocStatusOK)
            {
                msg = string.Format("{0} CROC stat after SEND: \n{1}\n", iTry, crocStatus);
                rtb_CRIMFELoopQueryDisplay.AppendText(msg); Metadata.MetaData.log.AddToLog(msg);
            }
            ////TEST CODE FOR ALL FAST COMMANDS COMBINATIONS
            return msg;
        }
        
        #endregion

        #endregion

        #region VME

        private void btn_VMERead_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    txt_VMEReadAddress.Text = txt_VMEReadAddress.Text.ToUpper();
                    uint theAddress = Convert.ToUInt32(txt_VMEReadAddress.Text, 16);
                    byte[] theData = new byte[2];
                    controller.Read(theAddress, controller.AddressModifier, controller.DataWidth, theData);
                    lbl_VMEReadData.Text = BitConverter.ToUInt16(theData, 0).ToString("X4");
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_VMEWrite_Click(object sender, EventArgs e)
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    txt_VMEWriteAddress.Text = txt_VMEWriteAddress.Text.ToUpper();
                    txt_VMEWriteData.Text = txt_VMEWriteData.Text.ToUpper();
                    uint theAddress = Convert.ToUInt32(txt_VMEWriteAddress.Text, 16);
                    byte[] theData = BitConverter.GetBytes(Convert.ToUInt16(txt_VMEWriteData.Text, 16));
                    controller.Write(theAddress, controller.AddressModifier, controller.DataWidth, theData);
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.AppendText(ex.Message + "\n");
                    MessageBox.Show(ex.Message);
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        #endregion VME

        #region Methods for Write/Read to/from V1720

        private ConfigV1720 ConfigFileV1720;

        private void btn_V1720AdvancedGUI_Click(object sender, EventArgs e)
        {
            AdvancedGUI((Button)sender, btn_V1720ReadAllRegisters);
        }

        private void btn_V1720ReadAllRegisters_Click(object sender, EventArgs e)
        {
            if (ConfigFileV1720 != null)
            {
                richTextBoxV1720.Text += ConfigFileV1720.Digitizer.ReadContentOfAllRegistersV1720();
                richTextBoxV1720.Text += ConfigFileV1720.Digitizer.ReadContentOfAllRegistersV1720Channels();
            }
            else
                richTextBoxV1720.Text += "\nERROR: There is NO Configuration File loaded.";
        }

        private void btn_V1720LoadConfigFile_Click(object sender, EventArgs e)
        {
            if (V1720Modules.Count == 0)
            {
                richTextBoxV1720.Text = string.Format("\nNo V1720 module present. Operation aborted.");
                return;
            }
            OpenFileDialog OFD = new System.Windows.Forms.OpenFileDialog();
            OFD.Title = "Open a V1720 Configuration File";
            if (OFD.ShowDialog() != System.Windows.Forms.DialogResult.OK) return;
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    ConfigFileV1720 = new ConfigFiles.ConfigV1720(OFD.FileName, controller, (V1720)(treeView1.SelectedNode.Tag));
                    richTextBoxV1720.Text = string.Format("\nOpening Configuration File : \n{0}\n", OFD.FileName);
                    //richTextBoxV1720.Text += ConfigFileV1720.ConfigFileContent;
                    richTextBoxV1720.Text += string.Format("\nExecuting Configuration File ...\n");
                    ConfigFileV1720.ExecuteConfigurationFile();
                    richTextBoxV1720.Text += string.Format("\n... Configuration File Execution : Success\n", OFD.FileName);
                    UpdateBufferSize8bit(true);
                }
                catch (Exception ex)
                {
                    richTextBoxV1720.Text += string.Format("\nERROR : {0}\n", ex.Message);
                    richTextBoxV1720.Text += string.Format("\n... Configuration File Execution : Aborted\n", OFD.FileName);
                    if (ConfigFileV1720 != null && ConfigFileV1720.StreamWriterEvent != null) ConfigFileV1720.StreamWriterEvent.Close();
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void btn_V1720TakeNEvents_Click(object sender, EventArgs e)
        {
            if (btn_V1720TakeNEvents.Text == "START Take N Events")
            {
                btn_V1720TakeNEvents.Text = "STOP Take N Events)";
                btn_V1720TakeNEvents.BackColor = Color.LightBlue;
                TakeNEvents();
                btn_V1720TakeNEvents.Text = "START Take N Events";
                btn_V1720TakeNEvents.BackColor = Color.Coral;
                return;
            }
            else
            {
                btn_V1720TakeNEvents.Text = "START Take N Events";
                return;
            }
        }

        private void TakeNEvents()
        {
            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    if (ConfigFileV1720.ReadoutMode == ConfigV1720.READOUT_MODE.D32)
                    {
                        richTextBoxV1720.Text += string.Format("Readout Mode {0} not implemented yet", ConfigV1720.READOUT_MODE.D32.ToString());
                    }
                    if (ConfigFileV1720.ReadoutMode == ConfigV1720.READOUT_MODE.BLT32)
                    {
                        ConfigFileV1720.Digitizer.AcquisitionCtrlRunStop = V1720.AcqCtrlRunStop.Run;
                        ReadoutBLT32();
                    }
                    if (ConfigFileV1720.ReadoutMode == ConfigV1720.READOUT_MODE.MBLT64)
                        richTextBoxV1720.Text += string.Format("Readout Mode {0} not implemented yet", ConfigV1720.READOUT_MODE.MBLT64.ToString());
                }
                catch (Exception ex)
                {
                    richTextBoxV1720.Text += string.Format("\nERROR : {0}\n", ex.Message);
                }
                finally
                {
                    try
                    {
                        ConfigFileV1720.Digitizer.AcquisitionCtrlRunStop = V1720.AcqCtrlRunStop.Stop;
                        ConfigFileV1720.StreamWriterEvent.Flush();
                    }
                    catch (Exception ex)
                    {
                        richTextBoxV1720.Text += string.Format("\nERROR : {0}\n", ex.Message);
                    }
                    //if (ConfigFileV1720 != null)
                    //{
                    //    ConfigFileV1720.Digitizer.AcquisitionCtrlRunStop = V1720.AcqCtrlRunStop.Stop;
                    //    if (ConfigFileV1720.StreamWriterEvent != null) ConfigFileV1720.StreamWriterEvent.Flush();
                    //}
                    vmeDone.Set();
                }
            }
        }
        /// <summary>Updates the VME readout Buffer Size, in bytes.</summary>
        private uint UpdateBufferSize8bit(bool displayResults)
        {
            byte MemorySizeMBperChannel; 
            string BoardType;
            ConfigFileV1720.Digitizer.BoardInfo(out MemorySizeMBperChannel, out BoardType);
            V1720.BufferCode BufferCode = ConfigFileV1720.Digitizer.BufferOrganization;
            V1720.ChannelsEnabled ChannelEnableMask = ConfigFileV1720.Digitizer.ChannelEnableMask;
            // Calculate Expected Event Size in 32bit Words (including Header) IN STANDARD MODE
            uint ExpectedEventSize32 = (uint)(((MemorySizeMBperChannel * Math.Pow(2, 20)) / (int)Math.Pow(2, (int)BufferCode))
                * Multiplicity((int)ChannelEnableMask) + 16) / 4;  //the +16 bytes are for the Event Header
            // Calculate the BufferSize in bytes
            uint BufferSize8bit = (ConfigFileV1720.Digitizer.VMEControlBusError == V1720.VMECtrlBusError.Enabled)
                & (ConfigFileV1720.Digitizer.BLTEventNumber != 0) ?
                (ExpectedEventSize32 * ConfigFileV1720.Digitizer.BLTEventNumber * 4) : (ExpectedEventSize32 * 4); // Bytes
            // Add BLTSize more bytes as instructed by Configuration File ????? WHY????
            BufferSize8bit += ConfigFileV1720.BLTSize;
            //BufferData32 = new BitVector32[BufferSize8bit / 4];
            if (displayResults)
            {
                richTextBoxV1720.Text += string.Format("\nBoard Info Register :" +
                    "\n\tBoard Type : {0}\n\tMemory Size : {1} MByte per channel", BoardType, MemorySizeMBperChannel);
                richTextBoxV1720.Text += string.Format("\nChannel Enable Mask Register : 0x{0}", ((uint)ChannelEnableMask).ToString("X"));
                richTextBoxV1720.Text += string.Format("\nBuffer Organization Register :" +
                    "\n\tBuffers : {0}\n\tExpected Event Size : {1} 32-bit words (including header)", BufferCode, ExpectedEventSize32);
                richTextBoxV1720.Text += string.Format("\nReadout Buffer Size = {0} (bytes)", BufferSize8bit);
            }
            return BufferSize8bit;
        }
        /// <summary>Multiplicity: calculate the number of channels that partecipate to one event</summary>
        /// <param name="mask">Channel Mask</param>
        /// <returns>number of channels</returns>
        private int Multiplicity(int mask)
        {
            int i, m = 0;
            for (i = 0; i < 8; i++)
                if (((mask >> i) & 1) == 1) m++;
            return m;
        }

        private void ReadoutBLT32()
        {
            double[] iPedestalAvg = new double[8]; //new int[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] iPulseIntegral = new double[8]; //new int[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] iPulseAvg = new double[8]; //new int[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] SumPedestalAvg = new double[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] SumPulseIntegral = new double[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] SumPulseAvg = new double[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] Sum2PedestalAvg = new double[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] Sum2PulseIntegral = new double[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] Sum2PulseAvg = new double[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] MeanPedestalAvg = new double[8]; //new int[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] MeanPulseIntegral = new double[8]; //new int[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] MeanPulseAvg = new double[8]; //new int[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] StDevPedestalAvg = new double[8]; //new int[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] StDevPulseIntegral = new double[8]; //new int[Enum.GetValues(typeof(V1720.Channels)).Length];
            double[] StDevPulseAvg = new double[8]; //new int[Enum.GetValues(typeof(V1720.Channels)).Length];
            Event theEvent;
            string msg = string.Empty;
            richTextBoxV1720.Text = msg;
            uint iEvent = 0;
            uint nEvent = 0;
            uint.TryParse(txt_V1720TakeNEvents.Text, out nEvent);
            byte[] first32BitWord = new byte[4];
            uint firstWord;
            uint eventSize8;
            prgStatus.Minimum = 0;
            prgStatus.Maximum = (int)nEvent;
            prgStatus.Value = 0;
            try
            {
                msg = string.Format("\nBEGIN Taking Events : {0}", DateTime.Now);
                richTextBoxV1720.Text = "\n" + msg; ConfigFileV1720.StreamWriterEvent.WriteLine(msg);
                while (iEvent < nEvent)
                {
                    //Console.WriteLine("_digitizer.EventStored = " + ConfigFileV1720.Digitizer.EventStored);
                    //byte[] first32BitWord = new byte[4];
                    //uint firstWord; uint eventSize8;
                    controller.Reads(ConfigFileV1720.Digitizer.BaseAddress, AddressModifiers.A24, DataWidths.D32, first32BitWord);
                    firstWord = BitConverter.ToUInt32(first32BitWord, 0);
                    if (firstWord != 0xFFFFFFFF)
                    {
                        eventSize8 = (firstWord & 0x0FFFFFFF) * 4;
                        BitVector32[] eventData = new BitVector32[eventSize8 / 4];
                        int itmp = 0;
                        eventData[itmp++] = new BitVector32((int)firstWord);
                        int Count;
                        byte[] Data = new byte[4000];
                        do
                        {
                            controller.ReadBlocks(ConfigFileV1720.Digitizer.BaseAddress, AddressModifiers.A24, DataWidths.D32,
                            4000, Data, out Count);
                            for (int i = 0; i < Count; i += 4)
                                eventData[itmp++] = new BitVector32((int)BitConverter.ToUInt32(Data, i));
                        }
                        while (Count == 4000);

                        theEvent = new Event(eventData, ConfigFileV1720.Digitizer.ConfigurationPack25);
                        iEvent++;

                        if (chk_V1720PrintEventData.Checked || chk_V1720PrintEventStat.Checked)
                        {
                            msg = string.Format("\niEvent={0} Date={1}", iEvent, DateTime.Now);
                            richTextBoxV1720.Text += "\n" + msg; ConfigFileV1720.StreamWriterEvent.WriteLine(msg);
                        }
                        if (chk_V1720PrintEventData.Checked)
                        {
                            msg = theEvent.ToString(ConfigFileV1720.OutputFormat);
                            richTextBoxV1720.Text += "\n" + msg; ConfigFileV1720.StreamWriterEvent.WriteLine(msg);
                        }
                        msg = theEvent.ToStringUVModel(0, 0.45, 0.45, 0.55, 0.55, 1, out iPedestalAvg, out iPulseIntegral, out iPulseAvg);
                        if (chk_V1720PrintEventStat.Checked)
                        {
                            richTextBoxV1720.Text += "\n" + msg; ConfigFileV1720.StreamWriterEvent.WriteLine(msg);
                        }
                        
                        for (int i = 0; i < 7; i++)
                        {
                            SumPedestalAvg[i] += iPedestalAvg[i];
                            SumPulseIntegral[i] += iPulseIntegral[i];
                            SumPulseAvg[i] += iPulseAvg[i];
                            Sum2PedestalAvg[i] += Math.Pow(iPedestalAvg[i], 2);
                            Sum2PulseIntegral[i] += Math.Pow(iPulseIntegral[i], 2);
                            Sum2PulseAvg[i] += Math.Pow(iPulseAvg[i], 2);
                        }
                        if (iEvent >= nEvent)
                        {
                            msg = string.Format("\n{0} Found {1} events, and the average of averages are: ", DateTime.Now, iEvent);
                            richTextBoxV1720.Text += "\n" + msg; ConfigFileV1720.StreamWriterEvent.WriteLine(msg);
                            for (int i = 0; i < 8; i++)
                            {
                                MeanPedestalAvg[i] = SumPedestalAvg[i] / iEvent;
                                MeanPulseIntegral[i] = SumPulseIntegral[i] / iEvent;
                                MeanPulseAvg[i] = SumPulseAvg[i] / iEvent;
                                StDevPedestalAvg[i] = Math.Sqrt(Sum2PedestalAvg[i] / iEvent - Math.Pow(MeanPedestalAvg[i], 2));
                                StDevPulseIntegral[i] = Math.Sqrt(Sum2PulseIntegral[i] / iEvent - Math.Pow(MeanPulseIntegral[i], 2));
                                StDevPulseAvg[i] = Math.Sqrt(Sum2PulseAvg[i] / iEvent - Math.Pow(MeanPulseAvg[i], 2));
                                if (MeanPedestalAvg[i] != 0)
                                {
                                    msg = string.Format("Ch{0} Ped = {1} +- {2}, PulseIntegral = {3} +- {4}, PulseAvg = {5} +- {6}",
                                        i, MeanPedestalAvg[i].ToString("0000.0000"), StDevPedestalAvg[i].ToString("0.0000"),
                                        MeanPulseIntegral[i].ToString("0000.0000"), StDevPulseIntegral[i].ToString("0.0000"),
                                        MeanPulseAvg[i].ToString("0.0000"), StDevPulseAvg[i].ToString("0.0000"));
                                    richTextBoxV1720.Text += "\n" + msg; ConfigFileV1720.StreamWriterEvent.WriteLine(msg);
                                }
                            }
                            for (int i = 0; i < 8; i++)
                            {
                                SumPedestalAvg[i] = 0;
                                SumPulseIntegral[i] = 0;
                                SumPulseAvg[i] = 0;
                                Sum2PedestalAvg[i] = 0;
                                Sum2PulseIntegral[i] = 0;
                                Sum2PulseAvg[i] = 0;
                            }
                        }
                        ProgressReport(null, new ProgressChangedEventArgs((int)iEvent, "Readout Event"));
                        if (btn_V1720TakeNEvents.Text == "START Take N Events") throw new Exception("User aborted operation");
                    }
                }
                msg = string.Format("\nEND Taking Events : {0}", DateTime.Now);
                richTextBoxV1720.Text += "\n" + msg; ConfigFileV1720.StreamWriterEvent.WriteLine(msg);
            }
            catch (Exception e)
            {
                richTextBoxV1720.Text += string.Format("\nERROR : {0}\n", e.Message);
            }

        }

        #endregion

        #region Methods for DEBUG on CHANNEL tab

        private void btn_CHDebugInitializeCROCs_Click(object sender, EventArgs e)
        {
            string testCaption = "FEsEnumeration";
            if (((Button)sender).Text == "START " + testCaption)
            {
                ((Button)sender).Text = "STOP " + testCaption;
                ((Button)sender).BackColor = Color.LightBlue;
                Refresh();
                FEsEnumeration();
                ((Button)sender).Text = "START " + testCaption;
                ((Button)sender).BackColor = Color.Coral;
                return;
            }
            else
            {
                ((Button)sender).Text = "START " + testCaption;
                return;
            }
        }
        private void FEsEnumeration()
        {
            this.Cursor = Cursors.WaitCursor;
            try
            {
                int nTimes;
                int.TryParse(txt_CHDebugNTests.Text, out nTimes);
                string referenceList = GetAllFEs(CROCModules);
                string currentList ="";
                rtb_CHDebug.AppendText(string.Format("\n{0} Refernce list of ALL FEs:\n{1}", DateTime.Now, referenceList));
                for (int i = 1; i <= nTimes; i++)
                {
                    Initialize(CROCModules);    //need it to see what FEs are in each channel
                    currentList = GetAllFEs(CROCModules);
                    if (currentList != referenceList)
                        throw new Exception(string.Format("\n{0} i={1} Found a different list:\n{2}", DateTime.Now, i, currentList));
                    prgStatus.Maximum = nTimes;
                    ProgressReport(null, new ProgressChangedEventArgs(i, "ReInitializing CROCs..."));
                    if (btn_CHDebugInitializeCROCs.Text == "START FEsEnumeration")
                        throw new Exception(string.Format("\n{0} i = {1} User aborted operation", DateTime.Now, i));
                }
            }
            catch (Exception ex)
            {
                rtb_CHDebug.AppendText("\n!!!!!" + ex.Message + "\n!!!!!");
                MessageBox.Show(ex.Message);
            }
            finally
            {
                vmeDone.Set();
            }
            this.Cursor = Cursors.Arrow;
        }
        private string GetAllFEs(List<CROC> CROCModules)
        {
            StringBuilder listAllFEs = new StringBuilder();
            foreach (CROC croc in CROCModules)
                foreach (IFrontEndChannel channel in croc.ChannelList)
                {
                    if (channel.ChainBoards.Count != 0)
                    {
                        listAllFEs.Append(channel.Description + ":");
                        foreach (Frame.Addresses feb in channel.ChainBoards)
                            listAllFEs.Append(" " + feb);
                    }
                }
            return listAllFEs.ToString();
        }

        private void btn_CHDebugFillDPM_Click(object sender, EventArgs e)
        {
            string testCaption = "FillDPM";
            if (((Button)sender).Text == "START " + testCaption)
            {
                ((Button)sender).Text = "STOP " + testCaption;
                ((Button)sender).BackColor = Color.LightBlue;
                Refresh();
                FillDPM();
                ((Button)sender).Text = "START " + testCaption;
                ((Button)sender).BackColor = Color.Coral;
                return;
            }
            else
            {
                ((Button)sender).Text = "START " + testCaption;
                return;
            }
        }
        private void FillDPM()
        {
            this.Cursor = Cursors.WaitCursor;
            try
            {
                int nTimes; StringBuilder dpmPattern; int dpmRepeat;
                int.TryParse(txt_CHDebugNTests.Text, out nTimes);
                int.TryParse(txt_CHDebugFillDPMPRepeat.Text, out dpmRepeat);
                dpmPattern = new StringBuilder(txt_CHDebugFillDPMPattern.Text.Trim());
                //repeat the dpmPattern dpmRepeat times
                dpmPattern = dpmPattern.Insert(dpmPattern.Length, dpmPattern.ToString(), dpmRepeat);
                //check for even number of bytes
                int nchar = dpmPattern.Length;
                if (nchar % 4 != 0) dpmPattern.Append('0', 4 - (nchar % 4));

                string msgSent = dpmPattern.ToString().ToUpper();
                StringBuilder msgReceived = new StringBuilder();
                byte[] bytesReceived = null;
                string err = string.Empty;
                rtb_CHDebug.Text = string.Empty;

                prgStatus.Minimum = 0; prgStatus.Maximum = nTimes - 1; prgStatus.Value = 0;
                for (int i = 0; i < nTimes; i++)
                {
                    //Clear and check DPM Pointer
                    btn_CHDPMPointerReset_Click(null, null);
                    btn_CHDPMPointerRead_Click(null, null);
                    if (lblCH_DPMPointerValue.Text != "0x2")
                        throw new Exception(string.Format("\n{0} i={1} DPM pointer not cleared -> {2}", 
                            DateTime.Now, i, lblCH_DPMPointerValue.Text));
                    
                    //Clear and check Status
                    btn_CHStatusRegClear_Click(null, null);
                    btn_CHStatusRegRead_Click(null, null);
                    if (lblCH_StatusValue.Text != "0x3700")
                        throw new Exception(string.Format("\n{0} i={1} Status register not cleared -> {2}", 
                            DateTime.Now, i, lblCH_StatusValue.Text));
                    
                    //Fill readout library message buffer
                    TreeNode theNode = treeView1.SelectedNode;
                    IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Tag));
                    AppendMessage(msgSent, theChannel);
                    
                    //Write the message into CROC's FIFO and check status for FIFO flags
                    btn_CHFIFOWriteMessage_Click(null, null);
                    btn_CHStatusRegRead_Click(null, null);
                    if (lblCH_StatusValue.Text != "0x3710")
                        throw new Exception(string.Format("\n{0} i={1} Status register not 0x3710 -> {2}",
                            DateTime.Now, i, lblCH_StatusValue.Text));

                    //Send the message and check status(null, null);
                    btn_CHSendMessage_Click(null, null);
                    btn_CHStatusRegRead_Click(null, null);
                    if (lblCH_StatusValue.Text != "0x3703")
                        throw new Exception(string.Format("\n{0} i={1} Status register not 0x3703 -> {2}",
                             DateTime.Now, i, lblCH_StatusValue.Text));

                    //Read the message received
                    txt_CHDPMReadLength.Text = Convert.ToString(msgSent.Length / 2 + 2); //one byte is two hex characters plus two bytes for message length
                    bytesReceived = CHDPMRead();

                    //Check that message sent and received are identical
                    msgReceived = new StringBuilder();
                    for (int j = 0; j < bytesReceived.Length; j++)
                        msgReceived.Append(Convert.ToString(bytesReceived[j], 16).ToUpper().PadLeft(2, '0'));  // Convert.ToByte(theMessage.Substring(2 * i, 2), 16);
                    if (msgReceived.ToString().Substring(4) != msgSent)
                        throw new Exception(string.Format("\n{0} i={1} Message sent <> Message received:\nSent:\n{2}\nReceived: Length=0x{3}\n{4}",
                             DateTime.Now, i, msgSent, msgReceived.ToString().Substring(0, 4), msgReceived.ToString().Substring(4)));

                    ProgressReport(null, new ProgressChangedEventArgs(i, "Message..."));
                    //Exit loop test
                    if (btn_CHDebugFillDPM.Text == "START FillDPM")
                        throw new Exception(DateTime.Now + " i = " + i + " User aborted operation");
                }
            }
            catch (Exception ex)
            {
                rtb_CHDebug.AppendText("\n!!!!!" + ex.Message + "\n!!!!!");
                MessageBox.Show(ex.Message);
            }
            this.Cursor = Cursors.Arrow;
        }

        private void cmb_CHDebugDeviceID_SelectedIndexChanged(object sender, EventArgs e)
        {
            switch (cmb_CHDebugDeviceID.SelectedIndex)
            {
                case 1:     //TRIPs
                    cmb_CHDebugFunctionID.Items.Clear();
                    cmb_CHDebugFunctionID.Items.Add("0 NA");
                    cmb_CHDebugFunctionID.Items.Add("1 WR ALL");
                    for (int i = 2; i <= 7; i++)
                        cmb_CHDebugFunctionID.Items.Add(i + " WR T" + (i - 2));
                    for (int i = 8; i <= 15; i++)
                        cmb_CHDebugFunctionID.Items.Add(i + " NA");
                    break;
                case 2:     //Registers 
                    cmb_CHDebugFunctionID.Items.Clear();
                    cmb_CHDebugFunctionID.Items.Add("0 NA");
                    cmb_CHDebugFunctionID.Items.Add("1 W");
                    cmb_CHDebugFunctionID.Items.Add("2 R");
                    for (int i = 3; i <= 15; i++)
                        cmb_CHDebugFunctionID.Items.Add(i + " NA");
                    break;
                case 3:     //BRAMs
                    cmb_CHDebugFunctionID.Items.Clear();
                    cmb_CHDebugFunctionID.Items.Add("0 NA");
                    for (int i = 1; i <= 6; i++)
                        cmb_CHDebugFunctionID.Items.Add(i + " RHit" + (i - 1));
                    cmb_CHDebugFunctionID.Items.Add("7 RDiscr");
                    for (int i = 8; i <= 13; i++)
                        cmb_CHDebugFunctionID.Items.Add(i + " RBRAM" + (i - 8));
                    for (int i = 14; i <= 15; i++)
                        cmb_CHDebugFunctionID.Items.Add(i + " RHit" + (i - 8));
                    break;
                case 4:     //FLASH
                    cmb_CHDebugFunctionID.Items.Clear();
                    cmb_CHDebugFunctionID.Items.Add("0 NA");
                    cmb_CHDebugFunctionID.Items.Add("1 Command");
                    cmb_CHDebugFunctionID.Items.Add("2 SetReset");
                    for (int i = 3; i <= 15; i++)
                        cmb_CHDebugFunctionID.Items.Add(i + " NA");
                    break;
                default:
                    cmb_CHDebugFunctionID.Items.Clear();
                    for (int i = 0; i <= 15; i++)
                        cmb_CHDebugFunctionID.Items.Add(i + " NA");
                    break;
            }
            cmb_CHDebugFunctionID.SelectedIndex = 0;
        }
        private void btn_CHDebugUpdatePattern_Click(object sender, EventArgs e)
        {
            StringBuilder newPattern = new StringBuilder();
            byte b0 = (byte)((cmb_CHDebugDirection.SelectedIndex << 7) |
                        (cmb_CHDebugBroadcastCMD.SelectedIndex << 4) |
                        (cmb_CHDebugFEID.SelectedIndex));
            byte b1 = (byte)((cmb_CHDebugDeviceID.SelectedIndex << 4) |
                        (cmb_CHDebugFunctionID.SelectedIndex));
            newPattern.Append(Convert.ToString(b0, 16).ToUpper().PadLeft(2, '0'));
            newPattern.Append(Convert.ToString(b1, 16).ToUpper().PadLeft(2, '0'));
            newPattern.Append(txt_CHDebugFrameStatusID.Text.ToUpper().PadLeft(2, '0').Substring(0,2));
            newPattern.Append(txt_CHDebugFrameIDByte0.Text.ToUpper().PadLeft(2, '0').Substring(0, 2));
            newPattern.Append(txt_CHDebugFrameIDByte1.Text.ToUpper().PadLeft(2, '0').Substring(0, 2));
            txt_CHDebugFillDPMPattern.Text = newPattern.ToString();
        }
        /* TOOL TIPS content - deleted because compatibility issues...???
        The number of times you want to loop through when you click a button that embeds a loop test.  
        Starts enumerating the FEBs on this VME Crate. This includes ALL Chains of ALL CROCs that were previously detected. If you want to update CROCs and CRIMs, do a "File->LoadHardware". 
        Starts the following sequence of processes:
            1. Creates a message frame using the content of the "Pattern" field (in hex) repeated "Repeat" times (in decimal).
            2. Do "Clear Status Register", then "Read Status Register". If its content is not 0x3700 raise an error.
            3. Do "Reset DPM Pointer", then "Read DPM Pointer". If it is not 0x02 raise an error.
            3. Fill the CROC FIFO with the message created at (1). Do "Read Status Register". If its content is not 0x3710 raise an error.
            4. Do "Send Frame", then "Read Status Register". If its content is not 0x3703 raise an error.
            5. Read N+2 bytes from CROC's DPM, where N=the number of bytes in the sent message. 
               Compare the last N bytes of the received message with the sent message. If not identical raise an error. 
         Select the "Frame.Direction" bit.
         Select the "Frame.BroadcastCommand" (3bits).
         Select the "Frame.FEAddress" (4bits).
         Select the "Frame.Device" (4bits).
         Select the "Frame.DeviceFunction" (4bits).
         Hex value of the "Frame.FrameStatusBits" (8bits).
         Hex value of the "Frame.FrameIDByte0" (8bits).
         Hex value of the "Frame.FrameIDByte1" (8bits).
         Clears and Updates the content of "Pattern (0x)" TextBox with a new value according to the content of "Byte0" to "Byte4" fields.
        */
        #endregion



        //private void button1_Click(object sender, EventArgs e)
        //{
        //    //WINDOWS / LINUX comparison speed test
        //    CAENVMElib.CVErrorCodes myErrorCode;
        //    uint myAddress = 0;
        //    AddressModifiers myModifier = AddressModifiers.A24;
        //    DataWidths myWidth = DataWidths.D16;
        //    byte[] myData = new byte[2];

        //    //WRITE - to clear status and reset DPM register
        //    myAddress = 0x012030;
        //    myData[0] = 0x0A;
        //    myData[1] = 0x0A;
        //    //controller.Write(myAddress, myModifier, myWidth, myData);
        //    myErrorCode = CAENInterface.CAENVME.WriteCycle(0, myAddress, myData, CAENVMElib.CVAddressModifier.cvA24_U_DATA, CAENVMElib.CVDataWidth.cvD16);

        //    //READ - to check the status register
        //    myAddress = 0x012020;
        //    myData[0] = 0x0;
        //    myData[1] = 0x0;
        //    //controller.Read(myAddress, myModifier, myWidth, myData);
        //    myErrorCode = CAENInterface.CAENVME.ReadCycle(0, myAddress, myData, CAENVMElib.CVAddressModifier.cvA24_U_DATA, CAENVMElib.CVDataWidth.cvD16);
        //    //if ((myData[0]!=0x00)|(myData[1]!=0x37)) Console.WriteLine("status register error - 1");

        //    //WRITE - to DPM register
        //    myAddress = 0x012000;
        //    myData[0] = 0x01;
        //    myData[1] = 0x31;
        //    //controller.Write(myAddress, myModifier, myWidth, myData);
        //    myErrorCode = CAENInterface.CAENVME.WriteCycle(0, myAddress, myData, CAENVMElib.CVAddressModifier.cvA24_U_DATA, CAENVMElib.CVDataWidth.cvD16);
        //    myData[0] = 0x00;
        //    myData[1] = 0x00;
        //    for (int i = 0; i < 3; i++)
        //    {
        //        //controller.Write(myAddress, myModifier, myWidth, myData);
        //        myErrorCode = CAENInterface.CAENVME.WriteCycle(0, myAddress, myData, CAENVMElib.CVAddressModifier.cvA24_U_DATA, CAENVMElib.CVDataWidth.cvD16);
        //    }

        //    //READ - to check the status register
        //    myAddress = 0x012020;
        //    myData[0] = 0x0;
        //    myData[1] = 0x0;
        //    for (int i = 0; i < 3; i++)
        //    {
        //        //controller.Read(myAddress, myModifier, myWidth, myData);
        //        myErrorCode = CAENInterface.CAENVME.ReadCycle(0, myAddress, myData, CAENVMElib.CVAddressModifier.cvA24_U_DATA, CAENVMElib.CVDataWidth.cvD16);
        //        //if ((myData[0] != 0x10) | (myData[1] != 0x37)) Console.WriteLine("status register error - 2");
        //    }

        //    //WRITE - to SEND MESSAGE register
        //    myAddress = 0x012010;
        //    myData[0] = 0x01;
        //    myData[1] = 0x01;
        //    //controller.Write(myAddress, myModifier, myWidth, myData);
        //    myErrorCode = CAENInterface.CAENVME.WriteCycle(0, myAddress, myData, CAENVMElib.CVAddressModifier.cvA24_U_DATA, CAENVMElib.CVDataWidth.cvD16);

        //    //READ - to check the status register
        //    myAddress = 0x012020;
        //    myData[0] = 0x0;
        //    myData[1] = 0x0;
        //    //controller.Read(myAddress, myModifier, myWidth, myData);
        //    myErrorCode = CAENInterface.CAENVME.ReadCycle(0, myAddress, myData, CAENVMElib.CVAddressModifier.cvA24_U_DATA, CAENVMElib.CVDataWidth.cvD16);
        //    //if ((myData[0] != 0x03) | (myData[1] != 0x37)) Console.WriteLine("status register error - 3");
        //}

    }

    #region Tree Nodes

    /// <summary>
    /// Encapsulates a CRIM object into Tag property of the TreeNode
    /// </summary>
    public class CRIMnode : TreeNode
    {
        public CRIMnode(CRIM crim)
        {
            base.Tag = crim;
            base.Text = crim.Description;   // "CRIM:0x" + Convert.ToString(crim.BaseAddress >> 16, 16).ToUpper();
        }
    }

    /// <summary>
    /// Encapsulates a CROC object into Tag property of the TreeNode
    /// </summary>
    public class CROCnode : TreeNode
    {
        private List<CHnode> chnodes = new List<CHnode>();
        public CROCnode(CROC croc)
        {
            base.Tag = croc;
            base.Text = croc.Description;
            foreach (IFrontEndChannel ch in croc.ChannelList)
            {
                //create the CHnode : TreeNode for this CROCnode : TreeNode
                CHnode chn = new CHnode(ch);
                chnodes.Add(chn);
                base.Nodes.Add(chn);
            }
        }
        public List<CHnode> CHnodes { get { return chnodes; } }
    }

    /// <summary>
    /// Encapsulates an IFrontEndChannel object into Tag property of the TreeNode
    /// </summary>
    public class CHnode : TreeNode
    {
        private List<FEnode> fenodes = new List<FEnode>();
        public CHnode(IFrontEndChannel ch)
        {
            base.Tag = ch;
            base.Text = ch.Description;
            foreach (Frame.Addresses boardID in ch.ChainBoards)
            {
                //create the FEnode : TreeNode for this CHnode : TreeNode
                FEnode fen = new FEnode(ch, boardID);
                fenodes.Add(fen);
                base.Nodes.Add(fen);
            }
        }
        public List<FEnode> FEnodes { get { return fenodes; } }
    }

    /// <summary>
    /// Encapsulates a FEBSlave object into Tag property of the TreeNode
    /// </summary>
    public class FEnode : TreeNode
    {
        private byte ID = 0;
        private FPGAnode FPGARegs = new FPGAnode();
        private TRIPnode TripRegs = new TRIPnode();
        private FLASHnode FlashPages = new FLASHnode();

        public FEnode(IFrontEndChannel channel, Frame.Addresses boardID)
        {
            FEBSlave theFEB = new FEBSlave(channel, boardID);
            ID = (byte)boardID;
            base.Tag = theFEB;
            base.Text = boardID.ToString();
            frmSlowControl.FEBSlaves.Add(theFEB);
            FPGARegs.Text = "FPGA";
            TripRegs.Text = "TRIP";
            FlashPages.Text = "FLAH";
            this.Nodes.Add(FPGARegs);
            this.Nodes.Add(TripRegs);
            this.Nodes.Add(FlashPages);
        }
        /// <summary>
        /// Get the Frame.Addresses boardID
        /// </summary>
        public byte BoardID { get { return ID; } }
    }

    public class FPGAnode : TreeNode
    {
    }
    public class TRIPnode : TreeNode
    {
    }
    public class FLASHnode : TreeNode
    {
    }

    ///// <summary>
    ///// Contains two lists of TreeNode objects: CRIMnodes and CROCnodes
    ///// </summary>
    //public class MinervaTreeeNodes
    //{
    //    public List<CRIMnode> CRIMnodes = null;
    //    public List<CROCnode> CROCnodes = null;
    //}

    /// <summary>Encapsulates a IV1720 object into Tag property of the TreeNode</summary>
    public class V1720node : TreeNode
    {
        private TreeNode registers = new TreeNode();
        private TreeNode channels = new TreeNode();
        private List<V1720CHnode> chnodes = new List<V1720CHnode>();
        private List<V1720REGnode> regnodes = new List<V1720REGnode>();
        public V1720node(IV1720 digitizer)
        {
            base.Tag = digitizer;
            base.Text = digitizer.Description;
            registers.Text = "Registers";
            base.Nodes.Add(registers);
            foreach (V1720.Registers register in Enum.GetValues(typeof(V1720.Registers)))
            {
                //create the V1720REGnode : TreeNode for this TreeNode registers
                V1720REGnode regnode = new V1720REGnode(register.ToString(), (ushort)register);
                regnodes.Add(regnode);
                registers.Nodes.Add(regnode);
            }
            channels.Text = "Channels";
            base.Nodes.Add(channels);
            foreach (V1720.Channels ch in Enum.GetValues(typeof(V1720.Channels)))
            {
                //create the V1720CHnode : TreeNode for this V1720node : TreeNode
                V1720CHnode chn = new V1720CHnode(digitizer[ch]);
                chnodes.Add(chn);
                channels.Nodes.Add(chn);
            }
        }
        //public TreeNode V1720REGnode { get { return registers; } }
        //public TreeNode V1720CHnode { get { return channels; } }
        //public List<V1720REGnode> V1720REGnodes { get { return regnodes; } }
        //public List<V1720CHnode> V1720CHnodes { get { return chnodes; } }
    }
    /// <summary>Encapsulates an IV1720Channel object into Tag property of the TreeNode</summary>
    public class V1720CHnode : TreeNode
    {
        private TreeNode registers = new TreeNode();
        private List<V1720REGnode> regnodes = new List<V1720REGnode>();
        public V1720CHnode(IV1720Channel ch)
        {
            base.Tag = ch;
            base.Text = ch.Description;
            registers.Text = "Registers";
            base.Nodes.Add(registers);
            foreach (string register in ch.ChannelRegisters.Keys)
            {
                //create the V1720REGnode : TreeNode for this V1720CHnode : TreeNode
                V1720REGnode regnode = new V1720REGnode(register, ch.ChannelRegisters[register]);
                regnodes.Add(regnode);
                registers.Nodes.Add(regnode);
            }
        }
        //public TreeNode V1720CHREGnode { get { return registers; } }
        //public List<V1720REGnode> V1720CHREGnodes { get { return regnodes; } }
    }
    public class V1720REGnode : TreeNode
    {
        private string name;
        private ushort address;
        public V1720REGnode(string name, ushort address)
        {
            this.name = name;
            this.address = address;
            base.Text = string.Format("{0} : 0x{1}", name, address.ToString("X").PadLeft(4,'0'));
        }
        public string REGname { get { return name; } }
        public ushort REGaddr { get { return address; } }
    }

    #endregion

    #region Info classes that are serialized

    public class MinervaDevicesInfo
    {
        public List<CRIMInfo> CRIMs = new List<CRIMInfo>();
        public List<CROCInfo> CROCs = new List<CROCInfo>();
    }

    public class VMEDeviceInfo
    {
        public AddressModifiers AddressModifier;
        public uint BaseAddress;
        public int ControllerBoardNumber; //public IVMEController Controller;
        public int ControllerLinkNumber; //public IVMEController Controller;
        public DataWidths DataWidth;
        public String Description;
        public bool IsInitialized;
        public DataWidths SwappedDataWidth;
    }

    public class CRIMInfo : VMEDeviceInfo
    {
        public bool CRCEnabled;
        public bool Enabled;
        public ushort Frequency;
        public ushort GateWidth;
        public byte InterruptMask;
        public byte InterruptStatus;
        public IRQLevels IRQLevel;
        public bool RetransmitEnabled;
        public bool SendMessageEnabled;
        public ushort TCALBDelay;
        //public ushort Register;
        public byte TimingCommandReceived;
        public CRIM.TimingModes TimingMode;
        public ChannelInfo CRIMChannelInfo = new ChannelInfo();
    }

    public class CROCInfo : VMEDeviceInfo
    {
        //public ushort ChannelResetRegister; // Write Only
        public CROC.ClockModes ClockMode;
        //public ushort FastCommandRegister; // Write Only
        public ushort ResetAndTestMaskRegister;
        public bool TestPulseDelayEnabled;
        public ushort TestPulseDelayValue;
        //public ushort TestPulseRegister; // Write Only
        public ushort TimingSetupRegister;
        public List<CROCChannelInfo> CROCChannels = new List<CROCChannelInfo>();
    }

    public class ChannelInfo : VMEDeviceInfo
    {
        public uint ChannelNumber;
        public bool CRCError;
        public bool DeserializerLock;
        public bool MessageReceived;
        public bool MessageSent;
        public bool PLLOk;
        public ushort Pointer;
        public bool ReceiveBufferIsFull;
        public bool RFPresent;
        public bool SendBufferIsEmpty;
        public bool SendBufferIsFull;
        public bool SerializerSynch;
        public CROCFrontEndChannel.StatusBits StatusRegister;
        public bool TimeoutError;
    }

    public class CROCChannelInfo : ChannelInfo
    {
        public bool ResetEnabled;
        public bool TestPulseEnabled;
        public List<ChainBoardInfo> ChainBoards = new List<ChainBoardInfo>();
    }

    public class ChainBoardInfo
    {
        public Frame.Addresses BoardAddress;
        public FPGAFrameInfo fpgaFrameInfo = new FPGAFrameInfo();
        public List<TRIPFrameInfo> tripFrameInfoList = new List<TRIPFrameInfo>();
    }

    public class FrameInfo  // All members are read only
    {
        //public bool CheckResponseHeaderFlags;
        public Frame.Devices Device;
        public byte Function;
        public FrameID ID;
        // public byte[] Message; // Serialization of byte array needs to be resolved
        public bool MessageSent;
        public Frame.Addresses Recipient;
        // public byte[] Response; // Serialization of byte array needs to be resolved
        public bool ResponseCRCOK;
        public bool ResponseDeviceOK;
        public Frame.Directions ResponseDirection;
        public bool ResponseEndHeaderOK;
        public bool ResponseFunctionOK;
        public bool ResponseHeaderOK;
        public bool ResponseMaxLenBad;
        public bool ResponseNAHeaderBad;
        public bool ResponseReceived;
        public bool ResponseSecondStartBad;
        public uint Timestamp;
    }

    public class FPGAFrameInfo // : FrameInfo // Uncomment to include FrameInfo
    {
        public byte BoardID;
        public byte CosmicTrig;
        public bool DCM1Lock;
        public bool DCM1NoClock;
        public bool DCM2Lock;
        public bool DCM2NoClock;
        public bool DCM2PhaseDone;
        public ushort DCM2PhaseTotal;
        public ushort DiscrimEnableMaskTrip0;
        public ushort DiscrimEnableMaskTrip1;
        public ushort DiscrimEnableMaskTrip2;
        public ushort DiscrimEnableMaskTrip3;
        public ushort ExtTriggFound;
        public byte ExtTriggRearm;
        public byte FirmwareVersion;
        public ushort GateLength;
        public ushort GateStart;
        public uint GateTimeStamp;
        public ushort HVActual;
        public byte HVControl;
        public bool HVEnabled;
        public bool HVManual;
        public byte HVNumAvg;
        public ushort HVPeriodAuto;
        public ushort HVPeriodManual;
        public byte HVPulseWidth;
        public ushort HVTarget;
        public byte[] InjectCount;
        public bool InjectDACDone;
        public byte InjectDACMode;
        public bool InjectDACStart;
        public ushort InjectDACValue;
        public byte InjectEnable;
        public byte InjectPhase;
        public byte InjectRange;
        public byte PhaseCount;
        public bool PhaseIncrement;
        public byte PhaseSpare;
        public bool PhaseStart;
        // public byte[] PhysicalRegisters; // Serialization of byte array needs to be resolved
        // public Dictionary<LogicalRegisters, BitVector32> Registers; // Get accessor only.  Dictionary<> cannot be serialized
        public ushort Temperature;
        public byte TestPulse2Bit;
        public uint TestPulseCount;
        public uint Timer;
        public BitVector32 TripPowerOff;
        public byte TripXCompEnc;
        public bool VXOMuxXilinx;
        // public bool VXOOff; // Not needed 
    }

    public class TRIPFrameInfo // : FrameInfo // Uncomment to include FrameInfo
    {
        public byte TripID;
        public uint RegisterIBP;
        public uint RegisterIBBNFALL;
        public uint RegisterIFF;
        public uint RegisterIBPIFF1REF;
        public uint RegisterIBPOPAMP;
        public uint RegisterIB_T;
        public uint RegisterIFFP2;
        public uint RegisterIBCOMP;
        public uint RegisterVREF;
        public uint RegisterVTH;
        public uint RegisterGAIN;
        public uint RegisterPIPEDEL;
        public uint RegisterIRSEL;
        public uint RegisterIWSEL;

        // ATTENTION: Reading the inject register is not possible.  TripTFrame will set these members to zero
        public uint RegisterINJEX0;
        public uint RegisterINJB0;
        public uint RegisterINJB1;
        public uint RegisterINJB2;
        public uint RegisterINJB3;
        public uint RegisterINJEX33;
    }

    #endregion

}
