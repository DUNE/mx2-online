using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Threading;
using System.Xml.Serialization;
using VMEInterfaces;
using MinervaUserControls;
using System.Collections.Specialized; // For BitVector32
//using MinervaDAQ; // For FebSlave class

namespace MinervaGUI
{
    public partial class frmSlowControl : Form
    {
        bool AppendDescription = false;

        CAEN2718 controller;
        List<CRIM> CRIMModules = new List<CRIM>();
        List<CROC> CROCModules = new List<CROC>();
        List<CRIMnode> CRIMnodes = new List<CRIMnode>();
        List<CROCnode> CROCnodes = new List<CROCnode>();
        List<CHnode> CHnodes = new List<CHnode>();
        List<FEnode> FEnodes = new List<FEnode>();
        public static List<FEBSlave> FEBSlaves = new List<FEBSlave>();

        MinervaDevicesInfo minervaDevicesInfo = new MinervaDevicesInfo();
        MinervaDevicesInfo xmlInfo = new MinervaDevicesInfo();

        private static EventWaitHandle vmeDone = null;

        static frmSlowControl()
        {
            vmeDone = new EventWaitHandle(true, EventResetMode.AutoReset, "MinervaVMEDone");
        }
        
        public frmSlowControl()
        {
            InitializeComponent();

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
                    controller = new CAEN2718("CAEN VME", 0, 0);
                    StringBuilder sb = new StringBuilder();
                    //if (txtDelay.Text != String.Empty) CAEN2718.GlobalDelayMs = Convert.ToInt32(txtDelay.Text);
                    //prgStatus.Value = 50;
                    Refresh();
                    controller.Initialize();
                    CAENInterface.CAENVME.BoardFWRelease(0, sb);
                    richTextBoxDescription.Text = String.Format("Controller Firmware: {0}", sb.ToString());
                    StringBuilder sw = new StringBuilder();
                    CAENInterface.CAENVME.SWRelease(sw);
                    richTextBoxDescription.Text += String.Format("\nDriver Library: {0}", sw.ToString());
                    //prgStatus.Value = 100;
                    Refresh();
                    lblStatus.Text = "VME Controller initialized.";
                }
                catch
                {
                    prgStatus.Value = 0;
                    MessageBox.Show("Unable to initialize crate controller");
                    lblStatus.Text = "VME Controller NOT initialized.";
                    //this.Close();
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void frmSlowControl_Load(object sender, EventArgs e)
        {
            LoadHardwareToolStripMenuItem_Click(null, null);
            //treeView1.ExpandAll();
        }

        private void treeView1_AfterSelect(object sender, TreeViewEventArgs e)
        {
            if (!AppendDescription) richTextBoxDescription.Clear();
            if (e.Node is CRIMnode)
            {
                richTextBoxDescription.Text += ((CRIM)(e.Node.Tag)).Description;
                //richTextBoxCrim.Text += "\nInterruptMask=" + ((CRIM)(e.Node.Tag)).InterruptMask;
                //richTextBoxCrim.Text += "\nTimingMode=" + ((CRIM)(e.Node.Tag)).TimingMode;
                //tabControl1.SelectTab("tabCRIM");
                tabControl1.SelectTab(tabDescription);
            }
            if (e.Node is CROCnode)
            {
                //richTextBoxDescription.Text += ((CROC)(e.Node.Tag)).Description;
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
                richTextBoxDescription.Text += 
                    "FEid=" + ((FEnode)(e.Node)).BoardID.ToString() +
                    ", CHid=" + ((CROCFrontEndChannel)(((CHnode)(e.Node.Parent)).Tag)).ChannelNumber.ToString() +
                    ", CROCid=" + ((((CROC)(((CROCnode)(e.Node.Parent.Parent)).Tag)).BaseAddress) >> 16).ToString();
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
                    richTextBoxDescription.Text = "Loading file " + myOFD.FileName + "\n";
                    richTextBoxDescription.Text += xmlFileR.ReadToEnd();
                    WriteXMLToHardwareToolStripMenuItem.Enabled = true;
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    Console.WriteLine(ex.InnerException.Message);
                    richTextBoxDescription.Text += "\n" + ex.Message;
                    richTextBoxDescription.Text += "\n" + ex.InnerException.Message;
                }
                finally { xmlFileR.Close(); }
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
                    richTextBoxDescription.Text = "Saving file " + mySFD.FileName + "\n";
                    richTextBoxDescription.Text += xmlFileR.ReadToEnd();
                    xmlFileR.Close();
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                    Console.WriteLine(ex.InnerException.Message);
                    richTextBoxDescription.Text += "\n" + ex.Message;
                    richTextBoxDescription.Text += "\n" + ex.InnerException.Message;
                }
                finally
                {
                    xmlFileW.Close();
                }
            }
        }

        private void WriteXMLToHardwareToolStripMenuItem_Click(object sender, EventArgs e)
        {
            richTextBoxDescription.Clear();
            tabControl1.SelectTab("tabDescription");
            bool crimsMatch = true; // ... false....
            bool crocsMatch = true;
            bool febsMatch = true;

            #region Compare CRIMs in XML file to CRIMs loaded

            richTextBoxDescription.Text = "Comparing CRIMs in XML file to CRIMs loaded\n";
            if (xmlInfo.CRIMs.Count != minervaDevicesInfo.CRIMs.Count)
            {
                crimsMatch = false;
                richTextBoxDescription.SelectionColor = Color.Red;
                richTextBoxDescription.Text += "\nNumber of CRIMs in XML file is different from the Number of CRIMs loaded\n";
                richTextBoxDescription.SelectionColor = Color.Black;
            }
            foreach (CRIMInfo xmlCRIM in xmlInfo.CRIMs)
            {
                bool crimFound = false;
                foreach (CRIMInfo minervaCRIM in minervaDevicesInfo.CRIMs)
                {
                    if (xmlCRIM.BaseAddress == minervaCRIM.BaseAddress)
                    {
                        crimFound = true;
                        richTextBoxDescription.Text += "\n" + xmlCRIM.Description + " in XML file found";
                        break;
                    }
                }
                if (!crimFound)
                {
                    crimsMatch = false;
                    richTextBoxDescription.SelectionColor = Color.Red;
                    richTextBoxDescription.Text += "\n" + xmlCRIM.Description + " in XML file not found";
                    richTextBoxDescription.SelectionColor = Color.Black;
                }
            }
            if (crimsMatch) richTextBoxDescription.Text += "\n\nMatched CRIMs in XML file to CRIMs loaded";

            #endregion

            #region Compare CROCs in XML file to CROCs loaded

            richTextBoxDescription.Text += "\n\nComparing CROCs in XML file to CROCs loaded\n";
            if (xmlInfo.CROCs.Count != minervaDevicesInfo.CROCs.Count)
            {
                crocsMatch = false;
                richTextBoxDescription.SelectionColor = Color.Red;
                richTextBoxDescription.Text += "\nNumber of CROCs in XML file is different from the Number of CROCs loaded\n";
                richTextBoxDescription.SelectionColor = Color.Black;
            }
            foreach (CROCInfo xmlCROC in xmlInfo.CROCs)
            {
                bool crocFound = false;
                foreach (CROCInfo minervaCROC in minervaDevicesInfo.CROCs)
                {
                    if (xmlCROC.BaseAddress == minervaCROC.BaseAddress)
                    {
                        crocFound = true;
                        richTextBoxDescription.Text += "\n" + xmlCROC.Description + " in XML file found";
                        break;
                    }
                }
                if (!crocFound)
                {
                    crocsMatch = false;
                    richTextBoxDescription.SelectionColor = Color.Red;
                    richTextBoxDescription.Text += "\n" + xmlCROC.Description + " in XML file not found";
                    richTextBoxDescription.SelectionColor = Color.Black;
                }
            }
            if (crocsMatch) richTextBoxDescription.Text += "\n\nMatched CROCs in XML file to CROCs loaded";

            #endregion

            #region Compare FEBs in XML file to FEBs loaded

            richTextBoxDescription.Text += "\n\nComparing FEBs in XML file to FEBs loaded\n";

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
                                        richTextBoxDescription.SelectionColor = Color.Red;
                                        richTextBoxDescription.Text += "\n" + xmlCROCChannelInfo.Description + ": Number of FEBs in XML file is different from the Number of FEBs loaded\n";
                                        richTextBoxDescription.SelectionColor = Color.Black;
                                    }
                                    foreach (ChainBoardInfo xmlChainBoard in xmlCROCChannelInfo.ChainBoards)
                                    {
                                        bool febFound = false;
                                        foreach (ChainBoardInfo minervaChainBoard in minervaCROCChannelInfo.ChainBoards)
                                        {
                                            if (xmlChainBoard.BoardAddress == minervaChainBoard.BoardAddress)
                                            {
                                                febFound = true;
                                                richTextBoxDescription.Text += "\n" + xmlCROCChannelInfo.Description + ":" + xmlChainBoard.BoardAddress + " in XML file found";
                                                break;
                                            }
                                        }
                                        if (!febFound)
                                        {
                                            febsMatch = false;
                                            richTextBoxDescription.SelectionColor = Color.White;
                                            richTextBoxDescription.Text += "\n" + xmlCROCChannelInfo.Description + ":" + xmlChainBoard.BoardAddress + " in XML file not found";
                                            richTextBoxDescription.SelectionColor = Color.Black;
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
            if (febsMatch) richTextBoxDescription.Text += "\nMatched FEBs in XML file to FEBs loaded";

            #endregion

            if (crimsMatch & crocsMatch & febsMatch) SetMinervaDevicesInfo();
        }

        private void LoadHardwareToolStripMenuItem_Click(object sender, EventArgs e)
        {
            this.Cursor = Cursors.WaitCursor;
            ResetActions();
            FindCROCandCRIMModules();
            Initialize(CRIMModules);    //not needed...
            Initialize(CROCModules);    //need it to see what FEs are in each channel
            UpdateTree();
            //Initialize(FEBSlaves);      //not needed...  
            Initialize(FEnodes);        //not needed...

            GetMinervaDevicesInfo(); 
            readVoltagesToolStripMenuItem.Enabled = true;
            zeroHVAllToolStripMenuItem.Enabled = true;
            monitorVoltagesToolStripMenuItem.Enabled = true;
            saveConfigXmlToolStripMenuItem.Enabled = true;

            this.Cursor = Cursors.Arrow;
        }

        private void ResetActions()
        {
            saveConfigXmlToolStripMenuItem.Enabled = false;
            WriteXMLToHardwareToolStripMenuItem.Enabled = false;

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
        }

        private void FindCROCandCRIMModules()
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
                    for (VMEDevsBaseAddr = 0; VMEDevsBaseAddr <= 255; VMEDevsBaseAddr++)
                    {
                        try
                        {
                            wData[0] = (byte)r.Next(1, 255);
                            wData[1] = (byte)r.Next(1, 255);
                            #region Version#1 to find out CROCs and CRIMs using Write/Read through "controller" object
                            controller.Write((VMEDevsBaseAddr << 16) + 0xF000, controller.AddressModifier,
                                    controller.DataWidth, wData);
                            controller.Read((VMEDevsBaseAddr << 16) + 0xF000, controller.AddressModifier,
                                controller.DataWidth, rData);

                            if ((rData[0] == wData[0]) && (rData[1] == wData[1]))
                            {
                                richTextBoxDescription.Text += "\nVMEDevsBaseAddr = " + VMEDevsBaseAddr + " Found a CROC VME module";
                                CROCModules.Add(new CROC((uint)(VMEDevsBaseAddr << 16), controller, String.Format("Croc {0}", VMEDevsBaseAddr)));
                            }
                            if ((rData[0] == wData[0]) && (rData[1] == 0))
                            {
                                richTextBoxDescription.Text += "\nVMEDevsBaseAddr = " + VMEDevsBaseAddr + " Found a CRIM VME module";
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
                            //    richTextBoxDescription.Text += "\nThis is a CROC VME module";
                            //}
                            //if ((rData[0] == wData[0]) && (rData[1] == 0))
                            //{
                            //    //CRIMs_VMEBaseAddress.Add(VMEBaseAddress);
                            //    richTextBoxDescription.Text += "\nThis is a CRIM VME module";
                            //}
                            #endregion

                        }
                        catch (Exception e)
                        {
                            //richTextBoxDescription.Text += "\n\tVMEDevsBaseAddr=" + VMEDevsBaseAddr;
                            if (e.Message == "Bus error") continue;
                            //throw new VMEException("CROCs can not be found....");
                        }
                    }
                }
                catch (Exception e)
                {
                    richTextBoxDescription.Text += "\n" + e.Message;
                    lblStatus.Text = "Error while finding CROC and CRIM devices...";
                }
                finally
                {
                    vmeDone.Set();
                }
            }
        }

        private void Initialize(List<CRIM> CRIMs)
        {
            foreach (CRIM crim in CRIMs)
                crim.Initialize();
        }

        private void Initialize(List<CROC> CROCs)
        {
            foreach (CROC croc in CROCs)
                croc.Initialize();
        }

        private void Initialize(List<FEBSlave> FEBSlaves)
        {
            foreach (FEBSlave febs in FEBSlaves)
                febs.Initialize();
        }

        private void Initialize(List<FEnode> FEnodes)
        {
            FEBSlaves.Clear();
            foreach (FEnode theFEnode in FEnodes)
            {
                ((FEBSlave)(theFEnode.Tag)).Initialize();
                FEBSlaves.Add((FEBSlave)(theFEnode.Tag));
            }
        }

        private void UpdateTree()
        {
            treeView1.Nodes.Clear();
            CRIMnodes.Clear();
            CROCnodes.Clear();
            CHnodes.Clear();
            FEnodes.Clear();
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
            minervaDevicesInfo.CRIMs.Clear();
            minervaDevicesInfo.CROCs.Clear();
            foreach (CRIM crim in CRIMModules)
            {
                CRIMInfo crimInfo = new CRIMInfo();
                GetCRIMInfo(crimInfo, crim);
                minervaDevicesInfo.CRIMs.Add(crimInfo);
            }
            foreach (CROC croc in CROCModules)
            {
                CROCInfo crocInfo = new CROCInfo();
                GetCROCInfo(crocInfo, croc);
                minervaDevicesInfo.CROCs.Add(crocInfo);
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

        private void GetCROCInfo(CROCInfo crocInfo, CROC croc)
        {
            GetVMEDeviceInfo(crocInfo, croc);
            crocInfo.ClockMode = croc.ClockMode;
            crocInfo.ResetAndTestMaskRegister = croc.ResetAndTestMaskRegister;
            crocInfo.TestPulseDelayEnabled = croc.TestPulseDelayEnabled;
            crocInfo.TestPulseDelayValue = croc.TestPulseDelayValue;
            crocInfo.TimingSetupRegister = croc.TimingSetupRegister;

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
            GetChannelInfo(crocChannelInfo, crocChannel);
            crocChannelInfo.ResetEnabled = crocChannel.ResetEnabled;
            crocChannelInfo.TestPulseEnabled = crocChannel.TestPulseEnabled;
            foreach(Frame.Addresses febAddress in crocChannel.ChainBoards)
            {
                ChainBoardInfo chainBoardInfo = new ChainBoardInfo();
                GetChainBoardInfo(chainBoardInfo, crocChannel, febAddress);
                crocChannelInfo.ChainBoards.Add(chainBoardInfo);
            }
        }

        private void GetChainBoardInfo(ChainBoardInfo chainBoardInfo, CROCFrontEndChannel crocChannel, Frame.Addresses febAddress)
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
            fpgaFrameInfo.FirmwareVersion = fpgaFrame.FirmwareVersion;
            fpgaFrameInfo.GateLength = fpgaFrame.GateLength;
            fpgaFrameInfo.GateStart = fpgaFrame.GateStart;
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
            foreach (CRIMInfo crimInfo in xmlInfo.CRIMs)
            {
                foreach (CRIM crim in CRIMModules)
                {
                    if (crimInfo.BaseAddress == crim.BaseAddress)
                    {
                        Console.WriteLine("Updating " + crim.Description); 
                        SetCRIMInfo(crim, crimInfo);
                        break;
                    }
                }
            }
            foreach (CROCInfo crocInfo in xmlInfo.CROCs)
            {
                foreach (CROC croc in CROCModules)
                {
                    if (crocInfo.BaseAddress == croc.BaseAddress)
                    {
                        Console.WriteLine("Updating " + croc.Description);
                        SetCROCInfo(croc, crocInfo);
                        break;
                    }
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

        private void SetCROCInfo(CROC croc, CROCInfo crocInfo)
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

            foreach (CROCFrontEndChannel channel in croc.ChannelList)
            {
                SetCROCChannelInfo(channel, crocInfo.CROCChannels[(int)channel.ChannelNumber - 1]);
            }
        }

        private void SetCROCChannelInfo(CROCFrontEndChannel crocChannel, CROCChannelInfo crocChannelInfo)
        {
            SetVMEDeviceInfo((VMEDevice)crocChannel, crocChannelInfo);
            crocChannel.ResetEnabled = crocChannelInfo.ResetEnabled;
            crocChannel.TestPulseEnabled = crocChannelInfo.TestPulseEnabled;
            foreach (ChainBoardInfo chainBoardInfo in crocChannelInfo.ChainBoards)
            {
                foreach (Frame.Addresses febAddress in crocChannel.ChainBoards)
                {
                    if (chainBoardInfo.BoardAddress == febAddress)
                    {
                        Console.WriteLine("Updating " + febAddress + " on " + crocChannel.Description);
                        SetChainBoardInfo(chainBoardInfo, crocChannel, febAddress);
                        break;
                    }
                }
            }
        }

        private void SetChainBoardInfo(ChainBoardInfo chainBoardInfo, CROCFrontEndChannel crocChannel, Frame.Addresses febAddress)
        {
            SetFPGAFrameInfo(chainBoardInfo.fpgaFrameInfo, crocChannel, febAddress);
            foreach (TRIPFrameInfo tripFrameInfo in chainBoardInfo.tripFrameInfoList)
            {
                Frame.TRiPFunctions tripFunction = (Frame.TRiPFunctions)(tripFrameInfo.TripID + 2);
                SetTRIPFrameInfo(tripFrameInfo, crocChannel, febAddress, tripFunction);
            }
        }

        private void SetFPGAFrameInfo(FPGAFrameInfo fpgaFrameInfo, CROCFrontEndChannel crocChannel, Frame.Addresses febAddress)
        {
            ushort frameID = ConstructFrameID(crocChannel, febAddress);
            FPGAFrame fpgaFrame = new FPGAFrame(febAddress, Frame.FPGAFunctions.Write, new FrameID(frameID));

            // Read/Write members only
            fpgaFrame.CosmicTrig = fpgaFrameInfo.CosmicTrig;
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
                                    richTextBoxDescription.Text += channel.Description + ":" + feb +
                                        ": FPGADevRegs Write Success\n";
                                }
                                catch (Exception ex)
                                {
                                    richTextBoxDescription.Text += channel.Description + ":" + feb + ": Error: " + ex.Message + "\n";
                                }
                            }
                            richTextBoxDescription.Text += "\n";
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
                    richTextBoxDescription.Text += "...Done\n";
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
            theFPGAControl.RegisterVXOMuxSelect= Convert.ToUInt32(theFrame.VXOMuxXilinx);
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
                                        richTextBoxDescription.Text += channel.Description + ":" + feb +
                                            ":" + function + ": TripTDevRegs Write Success\n";
                                    }
                                    catch (Exception ex)
                                    {
                                        richTextBoxDescription.Text += channel.Description + ":" + feb +
                                            ":" + function + ": Error: " + ex.Message + "\n";
                                    }
                                }
                                richTextBoxDescription.Text += "\n";
                            }
                            richTextBoxDescription.Text += "\n";
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
                    richTextBoxDescription.Text += "...Done\n";
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


            lock (this)
            {
                vmeDone.WaitOne();
                try
                {
                    ReadHVChannelFEBs();
                    richTextBoxHVRead.Text = DateTime.Now + "\n" + outputText;
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



        #endregion

        #region Methods for Write/Read to/from FLASH Memory

        private void btn_FLASHAdvancedGUI_Click(object sender, EventArgs e)
        {
            AdvancedGUI((Button)sender, btn_FLASHReadSPIToFile, btn_FLASHWriteFileToSPI);
        }

        private void btn_FLASHReadSPIToFile_Click(object sender, EventArgs e)
        {
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
                        theChannel.Reset();
                        FlashFrame.ReadMemoryToFile(theChannel, theBoard, mySFD.FileName);
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
            this.Cursor = Cursors.Arrow;
        }

        private void btn_FLASHWriteFileToSPI_Click(object sender, EventArgs e)
        {
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
                        theChannel.Reset();
                        FlashFrame.WriteMemoryFromFile(theChannel, theBoard, myOFD.FileName);
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
            this.Cursor = Cursors.Arrow;
        }

        #endregion

        #region Methods for Write/Read to/from CHANNEL

        private void btn_CHAdvancedGUI_Click(object sender, EventArgs e)
        {
            AdvancedGUI((Button)sender, groupBoxCH_FLASH, groupBoxCH_StatusRegister, 
                groupBoxCH_DPM, groupBoxCH_Frame);
        }

        private void btn_CHWriteFileToSPI_Click(object sender, EventArgs e)
        {
            this.Cursor = Cursors.WaitCursor;
            OpenFileDialog myOFD = new OpenFileDialog();
            myOFD.Filter = "spi files (*.spidata)|*.spidata|All files (*.*)|*.*";
            myOFD.FilterIndex = 1;
            myOFD.RestoreDirectory = true;
            if (myOFD.ShowDialog() == DialogResult.OK)
            {
                lock (this)
                {
                    vmeDone.WaitOne();
                    try
                    {
                        TreeNode theNode = treeView1.SelectedNode;
                        IFrontEndChannel theChannel = ((IFrontEndChannel)(theNode.Tag));
                        theChannel.Reset();
                        ChannelWriteFileToFEsFlash(myOFD, theChannel);
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show(ex.Message);
                    }
                    finally
                    {
                        vmeDone.Set();
                        richTextBoxDescription.Text += "\n...Done " + DateTime.Now.ToString() + "\n";
                    }
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

            tabControl1.SelectTab(tabDescription);
            richTextBoxDescription.Text += "Writing ALL FEBs FLASH on " + theChannel.Description +
                " with the following data file :\n\n" + myOFD.FileName + "\n\n";
            tabControl1.SelectedTab.Refresh();

            foreach (Frame.Addresses feb in theChannel.ChainBoards)
            {
                try
                {
                    richTextBoxDescription.Text += theChannel.Description + ":" + feb +
                        ": FLASH Write      Begin " + DateTime.Now.ToString() + "\n";
                    tabControl1.SelectedTab.Refresh();
                    FlashFrame.WriteMemoryFromFile(theChannel, feb, myOFD.FileName);
                    richTextBoxDescription.Text += theChannel.Description + ":" + feb +
                        ": FLASH Write Success " + DateTime.Now.ToString() + "\n";
                    tabControl1.SelectedTab.Refresh();
                    //this is not quite safe... but for window's screen update is necessary...
                    Application.DoEvents();
                }
                catch (Exception ex)
                {
                    richTextBoxDescription.Text += theChannel.Description + ":" + feb + ": Error: " + ex.Message + "\n";
                }
            }
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
            if ((chStatus & CROCFrontEndChannel.StatusBits.CRCError) == CROCFrontEndChannel.StatusBits.CRCError)
                lblCH_StatCRCError.Text = "1";
            else lblCH_StatCRCError.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.DeserializerLock) == CROCFrontEndChannel.StatusBits.DeserializerLock)
                lblCH_StatDeserializerLOCK.Text = "1";
            else lblCH_StatDeserializerLOCK.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.DPMFull) == CROCFrontEndChannel.StatusBits.DPMFull)
                lblCH_StatDPMFull.Text = "1";
            else lblCH_StatDPMFull.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.FIFOFull) == CROCFrontEndChannel.StatusBits.FIFOFull)
                lblCH_StatFIFOFull.Text = "1";
            else lblCH_StatFIFOFull.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.FIFONotEmpty) == CROCFrontEndChannel.StatusBits.FIFONotEmpty)
                lblCH_StatFIFONotEmpty.Text = "1";
            else lblCH_StatFIFONotEmpty.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.MessageReceived) == CROCFrontEndChannel.StatusBits.MessageReceived)
                lblCH_StatMsgReceived.Text = "1";
            else lblCH_StatMsgReceived.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.MessageSent) == CROCFrontEndChannel.StatusBits.MessageSent)
                lblCH_StatMsgSent.Text = "1";
            else lblCH_StatMsgSent.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.PLLLocked) == CROCFrontEndChannel.StatusBits.PLLLocked)
                lblCH_StatPLL0LOCK.Text = "1";
            else lblCH_StatPLL0LOCK.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.RFPresent) == CROCFrontEndChannel.StatusBits.RFPresent)
                lblCH_StatRFPresent.Text = "1";
            else lblCH_StatRFPresent.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.SerializerSynch) == CROCFrontEndChannel.StatusBits.SerializerSynch)
                lblCH_StatSerializerSYNC.Text = "1";
            else lblCH_StatSerializerSYNC.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.TimeoutError) == CROCFrontEndChannel.StatusBits.TimeoutError)
                lblCH_StatTimeoutError.Text = "1";
            else lblCH_StatTimeoutError.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.UnusedBit1) == CROCFrontEndChannel.StatusBits.UnusedBit1)
                lblCH_StatUnusedBit1.Text = "1";
            else lblCH_StatUnusedBit1.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.UnusedBit2) == CROCFrontEndChannel.StatusBits.UnusedBit2)
                lblCH_StatUnusedBit2.Text = "1";
            else lblCH_StatUnusedBit2.Text = "0";
            //some litle abuse here... these (CRIM bits) should NOT be defined as CROCFrontEndChannel.StatusBits ....... 
            if ((chStatus & CROCFrontEndChannel.StatusBits.TestPulseReceived) == CROCFrontEndChannel.StatusBits.TestPulseReceived)
                lblCH_StatPLL1LOCK.Text = "1";
            else lblCH_StatPLL1LOCK.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.ResetReceived) == CROCFrontEndChannel.StatusBits.ResetReceived)
                lblCH_StatUnusedBit3.Text = "1";
            else lblCH_StatUnusedBit3.Text = "0";
            if ((chStatus & CROCFrontEndChannel.StatusBits.EncodedCommandReceived) == CROCFrontEndChannel.StatusBits.EncodedCommandReceived)
                lblCH_StatUnusedBit4.Text = "1";
            else lblCH_StatUnusedBit4.Text = "0";
        }

        private void ChannelClearLabels()
        {
            CROCFrontEndChannel.StatusBits chStatusZero = (CROCFrontEndChannel.StatusBits)0;
            ChannelUpdateStatusLabels(chStatusZero);
            lblCH_StatusValue.Text = "";
            lblCH_DPMPointerValue.Text = "";
            txt_CHFIFORegWrite.Text = "";
            txt_CHFIFORegWrite.Text = "";
            txt_CHDPMReadLength.Text = "";
            rtb_CHDPMRead.Clear();
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
                    if ((txt_CHFIFORegWrite.Text.Length % 2) == 0) 
                    {
                        byte[] message = new byte[txt_CHFIFORegWrite.Text.Length / 2];
                        for (int i = 0; i < message.Length; i++)
                            message[i] = Convert.ToByte(txt_CHFIFORegWrite.Text.Substring(2 * i, 2), 16);
                        theChannel.FillMessage(message.Length, message);
                    }
                    else MessageBox.Show("The number of hex characters must be even\nOperation aborted");
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
                        byte[] response = new byte[responseLength];
                        theChannel.ReadMemory(responseLength, response);
                        rtb_CHDPMRead.Clear();
                        rtb_CHDPMRead.Text += "0000" + "  " +
                                response[0].ToString("X").PadLeft(2, '0') +
                                response[1].ToString("X").PadLeft(2, '0') +
                                " -> dec=" + (response[1] * 256 + response[0]) + "\n";
                        for (int i = 2; i < responseLength; i += 8)
                        {
                            rtb_CHDPMRead.Text += i.ToString("X").PadLeft(4, '0') + "  ";
                            for (int j = 0; j < 8; j++)
                                if (i + j < responseLength)
                                    rtb_CHDPMRead.Text += (response[i + j].ToString("X")).PadLeft(2, '0');
                            rtb_CHDPMRead.Text += "\n";
                        }

                    }
                    else
                        MessageBox.Show("attempt to read more than maximum DPM depth = " +
                            CROCFrontEndChannel.MemoryMaxSize + "or less than 2\nOperation aborted");
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

        #endregion
            
        #region Methods for Write/Read to/from CROC

        private void btn_CROCAdvancedGUI_Click(object sender, EventArgs e)
        {
            AdvancedGUI((Button)sender, groupBoxCROC_FLASH, groupBoxCROC_TimingSetup,
                groupBoxCROC_ResetTPMaskReg, groupBoxCROC_FastCommand, groupBoxCROC_LoopDelay);
        }

        private void btn_CROCWriteFileToSPI_Click(object sender, EventArgs e)
        {
            this.Cursor = Cursors.WaitCursor;
            OpenFileDialog myOFD = new OpenFileDialog();
            myOFD.Filter = "spi files (*.spidata)|*.spidata|All files (*.*)|*.*";
            myOFD.FilterIndex = 1;
            myOFD.RestoreDirectory = true;
            if (myOFD.ShowDialog() == DialogResult.OK)
            {
                lock (this)
                {
                    vmeDone.WaitOne();
                    try
                    {
                        TreeNode theNode = treeView1.SelectedNode;
                        CROC theCROC = ((CROC)(theNode.Tag));
                        foreach (CROCFrontEndChannel theChannel in theCROC.ChannelList)
                        {
                            theChannel.Reset();
                            ChannelWriteFileToFEsFlash(myOFD, theChannel);
                        }
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show(ex.Message);
                    }
                    finally
                    {
                        vmeDone.Set();
                        richTextBoxDescription.Text += "\n...Done " + DateTime.Now.ToString() + "\n";
                    }
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
            cmb_CROCTimingSetupClock.SelectedIndex = -1;
            cmb_CROCTimingSetupTPDelay.SelectedIndex = -1;
            txt_CROCTimingSetupTPDelay.Text = "";
            lbl_CROCTimingSetupRead.Text = "";
            chk_CROCResetCh4.Checked = false; chk_CROCTPulseCh4.Checked = false;
            chk_CROCResetCh3.Checked = false; chk_CROCTPulseCh3.Checked = false;
            chk_CROCResetCh2.Checked = false; chk_CROCTPulseCh2.Checked = false;
            chk_CROCResetCh1.Checked = false; chk_CROCTPulseCh1.Checked = false;
            lbl_CROCResetTPRead.Text = "";
            cmb_CROCFastCommand.SelectedIndex = -1;
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
                            theCroc.FastCommandRegister = 0xB1;
                            break;
                        case 1: //ResetFPGA
                            theCroc.FastCommandRegister = 0x8D;
                            break;
                        case 2: //ResetTimer
                            theCroc.FastCommandRegister = 0xC5;
                            break;
                        case 3: //LoadTimer
                            theCroc.FastCommandRegister = 0xC9;
                            break;
                        case 4: //TriggerFound
                            theCroc.FastCommandRegister = 0x89;
                            break;
                        case 5: //TriggerRearm
                            theCroc.FastCommandRegister = 0x85;
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

        private void btn_CROCLoopDelay_Click(object sender, EventArgs e)
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
                        loopDelayLabels[(uint)(theChannel.ChannelNumber-1)].Text = 
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

        #endregion


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

    /// <summary>
    /// Contains two lists of TreeNode objects: CRIMnodes and CROCnodes
    /// </summary>
    public class MinervaTreeeNodes
    {
        public List<CRIMnode> CRIMnodes = null;
        public List<CROCnode> CROCnodes = null;
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
        public byte FirmwareVersion;
        public ushort GateLength;
        public ushort GateStart;
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
