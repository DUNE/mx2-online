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
using MinervaDAQ; // For FebSlave class

namespace MinervaGUI
{
    public partial class frmMinervaGUI : Form
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

        static frmMinervaGUI()
        {
            vmeDone = new EventWaitHandle(true, EventResetMode.AutoReset, "MinervaVMEDone");
        }
        
        public frmMinervaGUI()
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

        private void treeView1_AfterSelect(object sender, TreeViewEventArgs e)
        {
            if (!AppendDescription) richTextBoxDescription.Clear();
            if (e.Node is CRIMnode)
            {
                richTextBoxDescription.Text += ((CRIM)(e.Node.Tag)).Description;
                //richTextBoxCrim.Text += "\nInterruptMask=" + ((CRIM)(e.Node.Tag)).InterruptMask;
                //richTextBoxCrim.Text += "\nTimingMode=" + ((CRIM)(e.Node.Tag)).TimingMode;
                //tabControl1.SelectTab(4);
                tabControl1.SelectTab("tabCRIM");
            }
            if (e.Node is CROCnode)
            {
                richTextBoxDescription.Text += ((CROC)(e.Node.Tag)).Description;
                //richTextBoxCroc.Text += "\nClockMode=" + ((CROC)(e.Node.Tag)).ClockMode;
                //richTextBoxCroc.Text += "\nChannelList=" + ((CROC)(e.Node.Tag)).ChannelList;
                tabControl1.SelectTab("tabCROC");
            }
            if (e.Node is CHnode)
            {
                richTextBoxDescription.Text += ((CROCFrontEndChannel)(e.Node.Tag)).Description;
                tabControl1.SelectTab("tabCH");
            }
            if (e.Node is FEnode)
            {
                lblFPGA_FEID.Text = ((FEnode)(e.Node)).BoardID.ToString();
                lblFPGA_CHID.Text = ((CROCFrontEndChannel)(((CHnode)(e.Node.Parent)).Tag)).ChannelNumber.ToString();
                lblFPGA_CROCID.Text = ((((CROC)(((CROCnode)(e.Node.Parent.Parent)).Tag)).BaseAddress) >> 16).ToString();
                //btnFPGARegRead_Click(null, null);
                //tabControl1.SelectTab("tabFPGARegs");
                richTextBoxDescription.Text += "FEid=" + lblFPGA_FEID.Text + ", CHid=" + lblFPGA_CHID.Text + ", CROCid=" + lblFPGA_CROCID.Text;
                tabControl1.SelectTab("tabFE");
            }
            if (e.Node is FPGAnode)
            {
                lblFPGA_FEID.Text = ((FEnode)(e.Node.Parent)).BoardID.ToString();
                lblFPGA_CHID.Text = ((CROCFrontEndChannel)(((CHnode)(e.Node.Parent.Parent)).Tag)).ChannelNumber.ToString();
                lblFPGA_CROCID.Text = ((((CROC)(((CROCnode)(e.Node.Parent.Parent.Parent)).Tag)).BaseAddress) >> 16).ToString();
                btn_FPGARegRead_Click(null, null);
                tabControl1.SelectTab("tabFPGARegs");
            }
            if (e.Node is TRIPnode)
            {
                lblTRIP_FEID.Text = ((FEnode)(e.Node.Parent)).BoardID.ToString();
                lblTRIP_CHID.Text = ((CROCFrontEndChannel)(((CHnode)(e.Node.Parent.Parent)).Tag)).ChannelNumber.ToString();
                lblTRIP_CROCID.Text = ((((CROC)(((CROCnode)(e.Node.Parent.Parent.Parent)).Tag)).BaseAddress) >> 16).ToString();
                btn_TRIPRegRead_Click(null, null);
                tabControl1.SelectTab("tabTRIPRegs");
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
                    xmlFileR.Close();
                }

                if ((xmlInfo.CRIMs.Count != 0 | xmlInfo.CROCs.Count != 0) &
                    (CRIMModules.Count != 0 | CROCModules.Count != 0))
                    WriteXMLToHardwareToolStripMenuItem.Enabled = true;
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
                    //// break.....//
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
            ResetGUI();
            FindCROCandCRIMModules();
            Initialize(CRIMModules);    //not needed...
            Initialize(CROCModules);    //need it to see what FEs are in each channel
            UpdateTree();
            //Initialize(FEBSlaves);      //not needed...  
            Initialize(FEnodes);        //not needed...
            if (CROCModules.Count != 0)
            {
                readVoltagesToolStripMenuItem.Enabled = true;
                zeroHVAllToolStripMenuItem.Enabled = true;
            }
            if (CRIMModules.Count != 0 | CROCModules.Count != 0)
            {
                saveConfigXmlToolStripMenuItem.Enabled = true;
                GetMinervaDevicesInfo();
                if (xmlInfo.CRIMs.Count != 0 | xmlInfo.CROCs.Count != 0)
                    WriteXMLToHardwareToolStripMenuItem.Enabled = true;
            }
            this.Cursor = Cursors.Arrow;
        }

        private void ResetGUI()
        {
            saveConfigXmlToolStripMenuItem.Enabled = false;
            WriteXMLToHardwareToolStripMenuItem.Enabled = false;

            //For Read HV
            readVoltagesToolStripMenuItem.Enabled = false;
            richTextBoxHVRead.Clear();
            textBoxADCThreshold.Enabled = false;
            btnReadHV.Enabled = false;

            zeroHVAllToolStripMenuItem.Enabled = false;
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
                //FPGAFrame theFrame = new FPGAFrame((Frame.Addresses)theFEnode.BoardID, Frame.FPGAFunctions.Read, new FrameID());
                //theFrame.Send((CROCFrontEndChannel)(theFEnode.Parent.Tag));
                //theFrame.Receive();
                FEBSlaves.Add((FEBSlave)(theFEnode.Tag));
            }

            ////FEBSlave.MaxHits = maxHits;
            //febList = new List<FEBSlave>();
            //frameList = new List<FPGAFrame>();
            //foreach (CROC croc in CROCModules)
            //{
            //    foreach (IFrontEndChannel channel in croc.ChannelList)
            //    {
            //        foreach (Frame.Addresses boardID in channel.ChainBoards)
            //        {
            //            FEBSlave theFEB = new FEBSlave(channel, boardID);
            //            theFEB.Initialize();
            //            febList.Add(theFEB);

            //            FPGAFrame theFrame = new FPGAFrame(boardID, Frame.FPGAFunctions.Read, new FrameID());
            //            theFrame.Send(channel);
            //            theFrame.Receive();
            //            frameList.Add(theFrame);
            //        }
            //    }
            //}
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
            if (treeView1.Nodes.Count != 0)
            {
                //if (treeView1.SelectedNode is FENode)
                //{
                //    ((FEdev)treeView1.SelectedNode.Tag).StatusString = richTextBoxDescription.Text;

                //}
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
            //GetTripFrameInfo();
        }

        private void GetFrameInfo(FrameInfo frameInfo, Frame frame)
        {
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
            ushort frameID = (ushort)(
                Convert.ToUInt16(febAddress.ToString().Substring(2)) << 12 |
                Convert.ToUInt16(crocChannel.ChannelNumber) << 10 | 
                Convert.ToUInt16((crocChannel.BaseAddress >> 16) << 2));
            FPGAFrame fpgaFrame = new FPGAFrame(febAddress, Frame.FPGAFunctions.Read, new FrameID(frameID));
            fpgaFrame.Send(crocChannel);
            fpgaFrame.Receive();

            GetFrameInfo(fpgaFrameInfo, fpgaFrame);
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
            // fpgaFrameInfo.InjectCount = fpgaFrame.InjectCount; // Serialization of byte array needs to be resolved
            fpgaFrameInfo.InjectDACDone = fpgaFrame.InjectDACDone;
            fpgaFrameInfo.InjectDACMode = fpgaFrame.InjectDACMode;
            fpgaFrameInfo.InjectDACStart = fpgaFrame.InjectDACStart;
            fpgaFrameInfo.InjectDACValue = fpgaFrame.InjectDACValue;
            fpgaFrameInfo.InjectEnable = fpgaFrame.InjectEnable;
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
                        SetFPGAFrameInfo(chainBoardInfo.fpgaFrameInfo, crocChannel, febAddress);
                        break;
                    }
                }
            }
        }

        private void SetFPGAFrameInfo(FPGAFrameInfo fpgaFrameInfo, CROCFrontEndChannel crocChannel, Frame.Addresses febAddress)
        {
            ushort frameID = (ushort)(
                Convert.ToUInt16(febAddress.ToString().Substring(2)) << 12 |
                Convert.ToUInt16(crocChannel.ChannelNumber) << 10 |
                Convert.ToUInt16((crocChannel.BaseAddress >> 16) << 2));
            FPGAFrame fpgaFrame = new FPGAFrame(febAddress, Frame.FPGAFunctions.Write, new FrameID(frameID));
            //fpgaFrame.Send(crocChannel);
            //fpgaFrame.Receive();

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
            // fpgaFrame.InjectCount = fpgaFrameInfo.InjectCount; // Serialization of byte array needs to be resolved
            fpgaFrame.InjectDACMode = fpgaFrameInfo.InjectDACMode;
            fpgaFrame.InjectDACStart = fpgaFrameInfo.InjectDACStart;
            fpgaFrame.InjectDACValue = fpgaFrameInfo.InjectDACValue;
            fpgaFrame.InjectEnable = fpgaFrameInfo.InjectEnable;
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

            //AssignFPGARegsDaveToCristian(fpgaFrame, fpgaDevRegControl1);
            //fpgaDevRegControl1.UpdateFormControls();

            //lblFPGA_FEID.Text = febAddress.ToString().Substring(2);
            //lblFPGA_CHID.Text = crocChannel.ChannelNumber.ToString();
            //lblFPGA_CROCID.Text = (crocChannel.BaseAddress >> 16).ToString();


        }

        #endregion

        #region Methods for Write/Read to/from FPGA Registers
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
        private void btn_TRIPRegWrite_Click(object sender, EventArgs e)
        {
            MessageBox.Show("under construction...");
        }

        private void btn_TRIPRegRead_Click(object sender, EventArgs e)
        {
            MessageBox.Show("under construction...");
        }

        private void AssignTRIPRegsDaveToCristian(TripTFrame theFrame, MinervaUserControls.TripDevRegControl theTRIPControl)
        {
            MessageBox.Show("under construction...");

            //theFPGAControl.RegisterTimer = theFrame.Timer;
            //theFPGAControl.RegisterGateStart = theFrame.GateStart;
            //theFPGAControl.RegisterGateLength = theFrame.GateLength;
            //theFPGAControl.RegisterTripPowerOff = (uint)theFrame.TripPowerOff.Data;
            //UInt32[] temp = new UInt32[6];
            //for (int i = 0; i < 6; i++)
            //    temp[i] = (uint)theFrame.InjectCount[i];
            //theFPGAControl.RegisterInjectCount = temp;
            //theFPGAControl.RegisterInjectEnable = (uint)theFrame.InjectEnable.Data;
            //theFPGAControl.RegisterInjectRange = theFrame.InjectRange;
            //theFPGAControl.RegisterInjectPhase = theFrame.InjectPhase;
            //theFPGAControl.RegisterInjectDACValue = theFrame.InjectDACValue;
            //theFPGAControl.RegisterInjectDACMode = theFrame.InjectDACMode;
            //theFPGAControl.RegisterInjectDACStart = Convert.ToUInt32(theFrame.InjectDACStart);
            //theFPGAControl.RegisterInjectDACDone = Convert.ToUInt32(theFrame.InjectDACDone);
            //theFPGAControl.RegisterHVEnabled = Convert.ToUInt32(theFrame.HVEnabled);
            //theFPGAControl.RegisterHVTarget = theFrame.HVTarget;
            //theFPGAControl.RegisterHVActual = theFrame.HVActual;
            //theFPGAControl.RegisterHVControl = theFrame.HVControl;
            //theFPGAControl.RegisterHVAutoManual = Convert.ToUInt32(theFrame.HVManual);
            //theFPGAControl.RegisterVXOMuxSelect = Convert.ToUInt32(theFrame.VXOMuxXilinx);
            //theFPGAControl.RegisterPhaseStart = Convert.ToUInt32(theFrame.PhaseStart);
            //theFPGAControl.RegisterPhaseIncrement = Convert.ToUInt32(theFrame.PhaseIncrement);
            //theFPGAControl.RegisterPhaseSpare = theFrame.PhaseSpare;
            //theFPGAControl.RegisterPhaseTicks = theFrame.PhaseCount;
            //theFPGAControl.RegisterDCM1Lock = Convert.ToUInt32(theFrame.DCM1Lock);
            //theFPGAControl.RegisterDCM2Lock = Convert.ToUInt32(theFrame.DCM2Lock);
            //theFPGAControl.RegisterDCM1NoClock = Convert.ToUInt32(theFrame.DCM1NoClock);
            //theFPGAControl.RegisterDCM2NoClock = Convert.ToUInt32(theFrame.DCM2NoClock);
            //theFPGAControl.RegisterDCM2PhaseDone = Convert.ToUInt32(theFrame.DCM2PhaseDone);
            //theFPGAControl.RegisterDCM2PhaseTotal = theFrame.DCM2PhaseTotal;
            //theFPGAControl.RegisterTestPulse2Bit = theFrame.TestPulse2Bit;
            //theFPGAControl.RegisterTestPulseCount = theFrame.TestPulseCount;
            //theFPGAControl.RegisterBoardID = theFrame.BoardID;
            //theFPGAControl.RegisterFirmwareVersion = theFrame.FirmwareVersion;
            //theFPGAControl.RegisterHVNumAvg = theFrame.HVNumAvg;
            //theFPGAControl.RegisterHVPeriodManual = theFrame.HVPeriodManual;
            //theFPGAControl.RegisterHVPeriodAuto = theFrame.HVPeriodAuto;
            //theFPGAControl.RegisterHVPulseWidth = theFrame.HVPulseWidth;
            //theFPGAControl.RegisterTemperature = theFrame.Temperature;
            //theFPGAControl.RegisterTripXThreshold = theFrame.CosmicTrig;
            //theFPGAControl.RegisterTripXComparators = theFrame.TripXCompEnc;
        }

        private void AssignTRIPRegsCristianToDave(MinervaUserControls.TripDevRegControl theTRIPControl, TripTFrame theFrame)
        {
            MessageBox.Show("under construction...");

            //theFrame.Timer = theFPGAControl.RegisterTimer;
            //theFrame.GateStart = (ushort)theFPGAControl.RegisterGateStart;
            //theFrame.GateLength = (ushort)theFPGAControl.RegisterGateLength;
            //theFrame.TripPowerOff = new BitVector32((int)theFPGAControl.RegisterTripPowerOff);
            //byte[] tempbyte = new byte[6];
            //uint[] tempuint = new uint[6];
            //tempuint = theFPGAControl.RegisterInjectCount;
            //for (int i = 0; i < 6; i++)
            //    tempbyte[i] = (byte)tempuint[i];
            //theFrame.InjectCount = tempbyte;
            //theFrame.InjectEnable = new BitVector32((int)theFPGAControl.RegisterInjectEnable);
            //theFrame.InjectRange = (byte)theFPGAControl.RegisterInjectRange;
            //theFrame.InjectPhase = (byte)theFPGAControl.RegisterInjectPhase;

            //theFrame.InjectDACValue = (ushort)theFPGAControl.RegisterInjectDACValue;
            //theFrame.InjectDACMode = (byte)theFPGAControl.RegisterInjectDACMode;
            //theFrame.InjectDACStart = Convert.ToBoolean(theFPGAControl.RegisterInjectDACStart);
            ////theFrame.InjectDACDone = theFPGAControl.RegisterInjectDACDone;            READ ONLY
            //theFrame.HVEnabled = Convert.ToBoolean(theFPGAControl.RegisterHVEnabled);
            //theFrame.HVTarget = (ushort)theFPGAControl.RegisterHVTarget;
            ////theFrame.HVActual = theFPGAControl.RegisterHVActual;                      READ ONLY
            ////theFrame.HVControl = theFPGAControl.RegisterHVControl;                    READ ONLY
            //theFrame.HVManual = Convert.ToBoolean(theFPGAControl.RegisterHVAutoManual);
            //theFrame.VXOMuxXilinx = Convert.ToBoolean(theFPGAControl.RegisterVXOMuxSelect);
            //theFrame.PhaseStart = Convert.ToBoolean(theFPGAControl.RegisterPhaseStart);
            //theFrame.PhaseIncrement = Convert.ToBoolean(theFPGAControl.RegisterPhaseIncrement);
            //theFrame.PhaseSpare = (byte)theFPGAControl.RegisterPhaseSpare;
            //theFrame.PhaseCount = (byte)theFPGAControl.RegisterPhaseTicks;
            ////theFrame.DCM1Lock = theFPGAControl.RegisterDCM1Lock;                      READ ONLY
            ////theFrame.DCM2Lock = theFPGAControl.RegisterDCM2Lock;                      READ ONLY
            ////theFrame.DCM1NoClock = theFPGAControl.RegisterDCM1NoClock;                READ ONLY
            ////theFrame.DCM2NoClock = theFPGAControl.RegisterDCM2NoClock;                READ ONLY
            ////theFrame.DCM2PhaseDone = theFPGAControl.RegisterDCM2PhaseDone;            READ ONLY
            ////theFrame.DCM2PhaseTotal = theFPGAControl.RegisterDCM2PhaseTotal;          READ ONLY
            ////theFrame.TestPulse2Bit = theFPGAControl.RegisterTestPulse2Bit;            READ ONLY
            ////theFrame.TestPulseCount = theFPGAControl.RegisterTestPulseCount;          READ ONLY
            ////theFrame.BoardID = (byte)theFPGAControl.RegisterBoardID;                  READ ONLY
            ////theFrame.FirmwareVersion = theFPGAControl.RegisterFirmwareVersion;        READ ONLY
            //theFrame.HVNumAvg = (byte)theFPGAControl.RegisterHVNumAvg;
            //theFrame.HVPeriodManual = (ushort)theFPGAControl.RegisterHVPeriodManual;
            ////theFrame.HVPeriodAuto = (ushort)theFPGAControl.RegisterHVPeriodAuto;      READ ONLY
            //theFrame.HVPulseWidth = (byte)theFPGAControl.RegisterHVPulseWidth;
            ////theFrame.Temperature = (ushort)theFPGAControl.RegisterTemperature;        READ ONLY
            //theFrame.CosmicTrig = (byte)theFPGAControl.RegisterTripXThreshold;
            ////theFrame.TripXCompEnc = (byte)theFPGAControl.RegisterTripXComparators;    READ ONLY
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

        #endregion

        #region Methods for reading HVActual on FEBs

        private void readVoltagesToolStripMenuItem_Click(object sender, EventArgs e)
        {
            richTextBoxHVRead.Text = "Displays FEBs with HVActual differing from HVTarget \nby an amount greater than that specified below";
            tabControl1.SelectTab("tabReadHV");
            textBoxADCThreshold.Enabled = true;
            btnReadHV.Enabled = true; 
        }

        private void tabReadHV_Click(object sender, EventArgs e)
        {

        }

        ushort adcThreshold;
        string outputText;

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
            richTextBoxHVRead.Clear();
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
            outputText = "Croc:CH:FE: HVActual, HVTarget, HVActual - HVTarget\n\n";
            foreach (CROC croc in CROCModules)
            {
                foreach (IFrontEndChannel channel in croc.ChannelList)
                {
                    foreach (Frame.Addresses feb in channel.ChainBoards)
                    {
                        FPGAFrame frame = new FPGAFrame(feb, Frame.FPGAFunctions.Read, new FrameID());
                        frame.Send(channel);
                        frame.Receive();
                        if (Math.Abs(frame.HVActual - frame.HVTarget) < adcThreshold) continue;
                        outputText += channel.Description + ":" + feb + ": " +
                                      frame.HVActual.ToString() + ", " + frame.HVTarget.ToString() + ", " +
                                      Convert.ToString(frame.HVActual - frame.HVTarget) + "\n";
                    }
                    outputText += "\n";
                }
            }
        }

        private void zeroHVAllToolStripMenuItem_Click(object sender, EventArgs e)
        {
            DialogResult answer = MessageBox.Show("WARNING \n You are about to set HVTarget on all FEBs to zero. \n Do you wish to continue?", "Confirm Zero HVTarget on all FEBs", MessageBoxButtons.YesNo, MessageBoxIcon.Warning, MessageBoxDefaultButton.Button2);
            if (answer != DialogResult.Yes) return;
            tabControl1.SelectTab("tabDescription");
            richTextBoxDescription.Text = "Setting HVTarget on FEBs to zero\n\n";
            foreach (CROC croc in CROCModules)
            {
                foreach (IFrontEndChannel channel in croc.ChannelList)
                {
                    foreach (Frame.Addresses feb in channel.ChainBoards)
                    {
                        FPGAFrame frame = new FPGAFrame(feb, Frame.FPGAFunctions.Write, new FrameID());
                        frame.HVTarget = 0;
                        frame.Send(channel);
                        frame.Receive();
                        richTextBoxDescription.Text += channel.Description + ":" + feb + ": HVTarget set to " +
                                                       frame.HVTarget.ToString() + "\n";
                    }
                    richTextBoxDescription.Text += "\n";
                }
            }
        }

        private void frmMinervaGUI_Load(object sender, EventArgs e)
        {

        }

        #endregion

    }


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
        public FEnode(IFrontEndChannel channel, Frame.Addresses boardID)
        {
            FEBSlave theFEB = new FEBSlave(channel, boardID);
            ID = (byte)boardID;
            base.Tag = theFEB;
            base.Text = boardID.ToString();
            frmMinervaGUI.FEBSlaves.Add(theFEB);
            FPGARegs.Text = "FPGA";
            TripRegs.Text = "TRIP";
            this.Nodes.Add(FPGARegs);
            this.Nodes.Add(TripRegs);
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

    /// <summary>
    /// Contains two lists of TreeNode objects: CRIMnodes and CROCnodes
    /// </summary>
    public class MinervaTreeeNodes
    {
        public List<CRIMnode> CRIMnodes = null;
        public List<CROCnode> CROCnodes = null;
        ////public List<CHnode> CHnodes = null;
        ////public List<FEnode> FEnodes = null;
    }

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
        public bool CRCEnabled; //Control = 0x2070
        public bool Enabled; //InterruptConfig = 0xF040
        public ushort Frequency; //TimingSetup = 0xC010
        public ushort GateWidth; //SGATEWidth = 0xC020
        public byte InterruptMask; //InterruptMask = 0xF000
        public byte InterruptStatus; //InterruptStatus = 0xF010
        public IRQLevels IRQLevel; //InterruptConfig = 0xF040
        public bool RetransmitEnabled; //Control = 0x2070
        public bool SendMessageEnabled; //Control = 0x2070
        public ushort TCALBDelay;
        //public ushort Register;
        public byte TimingCommandReceived; //DecodedCommand = 0x2060
        public CRIM.TimingModes TimingMode; //TimingSetup = 0xC010
        public ChannelInfo CRIMChannelInfo = new ChannelInfo();
    }

    public class CROCInfo : VMEDeviceInfo
    {
        //public ushort ChannelResetRegister;
        public CROC.ClockModes ClockMode;
        //public ushort FastCommandRegister;
        public ushort ResetAndTestMaskRegister;
        public bool TestPulseDelayEnabled;
        public ushort TestPulseDelayValue;
        //public ushort TestPulseRegister;
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
        //public TripTFrameInfo 
    }

    public class FrameInfo
    {

        // All members are read only

        //public bool CheckResponseHeaderFlags;
        public Frame.Devices Device;
        public byte Function;
        public FrameID ID;
        // public byte[] test = new byte[4] { 1, 2, 3, 4 };
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

    public class FPGAFrameInfo : FrameInfo
    {
        public byte BoardID; // Keep
        public byte CosmicTrig; // Keep
        public bool DCM1Lock; // Keep
        public bool DCM1NoClock; // Keep
        public bool DCM2Lock; // Keep
        public bool DCM2NoClock; // Keep
        public bool DCM2PhaseDone; // Keep
        public ushort DCM2PhaseTotal; // Keep
        //private int ExpectedResponseLength;
        public byte FirmwareVersion; // Keep
        public ushort GateLength; // Keep
        public ushort GateStart; // Keep
        public ushort HVActual; // Keep
        public byte HVControl; // Keep
        public bool HVEnabled; // Keep
        public bool HVManual; // Keep
        public byte HVNumAvg; // Keep
        public ushort HVPeriodAuto; // Keep
        public ushort HVPeriodManual; // Keep
        public byte HVPulseWidth; // Keep
        public ushort HVTarget; // Keep
        // public byte[] InjectCount; // Keep // Serialization of byte array needs to be resolved
        public bool InjectDACDone; // Keep
        public byte InjectDACMode; // Keep
        public bool InjectDACStart; // Keep
        public ushort InjectDACValue; // Keep
        public BitVector32 InjectEnable; // Keep
        public byte InjectPhase; // Keep
        public byte InjectRange; // Keep
        public byte PhaseCount; // Keep
        public bool PhaseIncrement; // Keep
        public byte PhaseSpare; // Keep
        public bool PhaseStart; // Keep
        // public byte[] PhysicalRegisters; // Serialization of byte array needs to be resolved
        // public Dictionary<LogicalRegisters, BitVector32> Registers; // Get accessor only.  Dictionary<> cannot be serialized
        public ushort Temperature; // Keep
        public byte TestPulse2Bit; // Keep
        public uint TestPulseCount; // Keep
        public uint Timer; // Keep
        public BitVector32 TripPowerOff; // Keep
        public byte TripXCompEnc; // Keep
        public bool VXOMuxXilinx; // Keep
        // public bool VXOOff; // Not needed
    }

    #endregion

}