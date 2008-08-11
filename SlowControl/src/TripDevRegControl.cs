using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Text;
using System.Windows.Forms;

namespace MinervaUserControls
{
    public partial class TripDevRegControl : UserControl
    {
        private const int NLogicalRgisters = 20;
        private UInt32[] TRIPLogicalReg = new UInt32[NLogicalRgisters];
        private bool isAdvancedGUI = false;

        #region Define Logical Registers
        public enum LogicalRegisters : byte
        {
            IBP = 0,        // 8 bits     0
            IBBNFALL = 1,   // 8 bits     1     
            IFF = 2,        // 8 bits     2
            IBPIFF1REF = 3, // 8 bits     3
            IBPOPAMP = 4,   // 8 bits     4
            IB_T = 5,       // 8 bits     5
            IFFP2 = 6,      // 8 bits     6
            IBCOMP = 7,     // 8 bits     7
            VREF = 8,       // 8 bits     8
            VTH = 9,        // 8 bits     9
            GAIN = 10,      // 4 bits     10
            PIPEDEL = 11,   // 6 bits     11
            IRSEL = 12,     // 2 bits     12
            IWSEL = 13,     // 2 bits     13
            INJEX0 = 14,    // 1 bit      14
            INJB0 = 15,     // 8 bit      15
            INJB1 = 16,     // 8 bits     16
            INJB2 = 17,     // 8 bits     17
            INJB3 = 18,     // 8 bits     18
            INJEX33 = 19,   // 1 bit      19
        }
        #endregion

        #region Define Default Logical Values
        private const UInt32 IBPDefaultValue = 100;
        private const UInt32 IBBNFALLDefaultValue = 120;
        private const UInt32 IFFDefaultValue = 0;
        private const UInt32 IBPIFF1REFDefaultValue = 160;
        private const UInt32 IBPOPAMPDefaultValue = 40;
        private const UInt32 IB_TDefaultValue = 0;
        private const UInt32 IFFP2DefaultValue = 0;
        private const UInt32 IBCOMPDefaultValue = 20;
        private const UInt32 VREFDefaultValue = 20;
        private const UInt32 VTHDefaultValue = 0;
        private const UInt32 GAINDefaultValue = 5;
        private const UInt32 PIPEDELDefaultValue = 1;
        private const UInt32 IRSELDefaultValue = 3;
        private const UInt32 IWSELDefaultValue = 3;
        private const UInt32 INJEX0DefaultValue = 0;
        private const UInt32 INJB0DefaultValue = 0;
        private const UInt32 INJB1DefaultValue = 0;
        private const UInt32 INJB2DefaultValue = 0;
        private const UInt32 INJB3DefaultValue = 0;
        private const UInt32 INJEX33DefaultValue = 0;
        #endregion

        #region Define Control-type members (TextBox, ComboBox and Label)
        private TextBox txt_LWRIBP = new TextBox(); private Label lbl_IBP = new Label();
        private TextBox txt_LWRIBBNFALL = new TextBox(); private Label lbl_IBBNFALL = new Label();
        private TextBox txt_LWRIFF = new TextBox(); private Label lbl_IFF = new Label();
        private TextBox txt_LWRIBPIFF1REF = new TextBox(); private Label lbl_IBPIFF1REF = new Label();
        private TextBox txt_LWRIBPOPAMP = new TextBox(); private Label lbl_IBPOPAMP = new Label();
        private TextBox txt_LWRIB_T = new TextBox(); private Label lbl_IB_T = new Label();
        private TextBox txt_LWRIFFP2 = new TextBox(); private Label lbl_IFFP2 = new Label();
        private TextBox txt_LWRIBCOMP = new TextBox(); private Label lbl_IBCOMP = new Label();
        private TextBox txt_LWRVREF = new TextBox(); private Label lbl_VREF = new Label();
        private TextBox txt_LWRVTH = new TextBox(); private Label lbl_VTH = new Label();
        private TextBox txt_LWRGAIN= new TextBox(); private Label lbl_GAIN = new Label();
        private TextBox txt_LWRPIPEDEL = new TextBox(); private Label lbl_PIPEDEL = new Label();
        private TextBox txt_LWRIRSEL = new TextBox(); private Label lbl_IRSEL = new Label();
        private TextBox txt_LWRIWSEL = new TextBox(); private Label lbl_IWSEL = new Label();
        private TextBox txt_LWINJEX0 = new TextBox(); private Label lbl_INJEX0 = new Label();
        private TextBox txt_LWINJB0 = new TextBox(); private Label lbl_INJB0 = new Label();
        private TextBox txt_LWINJB1 = new TextBox(); private Label lbl_INJB1 = new Label();
        private TextBox txt_LWINJB2 = new TextBox(); private Label lbl_INJB2 = new Label();
        private TextBox txt_LWINJB3 = new TextBox(); private Label lbl_INJB3 = new Label();
        private TextBox txt_LWINJEX33 = new TextBox(); private Label lbl_INJEX33 = new Label();
        #endregion   
     
        
        public int NRegs
        {
            get { return NLogicalRgisters; }
        }
        public UInt32[] TRIPRegValues
        {
            get
            {
                UpdateTRIPLogicalRegArray();
                return TRIPLogicalReg;
            }
            set
            {
                value.CopyTo(TRIPLogicalReg, 0);
                UpdateFormControls();
            }
        }
        public UInt32 TRIPGetRegValue(UInt32 index)
        {
            UpdateTRIPLogicalRegArray();
            return TRIPLogicalReg[index];
        }
        public void TRIPSetRegValue(UInt32 index, UInt32 value)
        {
            TRIPLogicalReg[index] = value;
            UpdateFormControls();
        }
        
        public TripDevRegControl()
        {
            InitializeComponent();
            myInitializeComponent();
            ShowAdvancedGUI(isAdvancedGUI);
            //DisableReadControls();
            TRIPLogicalReg[(int)LogicalRegisters.IBP] = IBPDefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.IBBNFALL] = IBBNFALLDefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.IFF] = IFFDefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.IBPIFF1REF] = IBPIFF1REFDefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.IBPOPAMP] = IBPOPAMPDefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.IB_T] = IB_TDefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.IFFP2] = IFFP2DefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.IBCOMP] = IBCOMPDefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.VREF] = VREFDefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.VTH] = VTHDefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.GAIN] = GAINDefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.PIPEDEL] = PIPEDELDefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.IRSEL] = IRSELDefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.IWSEL] = IWSELDefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.INJEX0] = INJEX0DefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.INJB0] = INJB0DefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.INJB1] = INJB1DefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.INJB2] = INJB2DefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.INJB3] = INJB3DefaultValue;
            TRIPLogicalReg[(int)LogicalRegisters.INJEX33] = INJEX33DefaultValue;
        }

        private void myInitializeComponent()
        {
            int Xwidth = 100;
            int Yheight = 15;

            lbl_IBP.Width = Xwidth;
            lbl_IBP.Height = Yheight;
            lbl_IBP.Text = "IBP";
            lbl_IBP.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_IBP.BackColor = Color.Coral;
            this.Controls.Add(lbl_IBP);
            txt_LWRIBP.Width = Xwidth;
            txt_LWRIBP.Height = Yheight;
            txt_LWRIBP.Enabled = true;
            txt_LWRIBP.BackColor = Color.White;
            txt_LWRIBP.Name = "IBP";
            txt_LWRIBP.Text = IBPDefaultValue.ToString();
            txt_LWRIBP.TabIndex = (int)LogicalRegisters.IBP;
            txt_LWRIBP.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRIBP);

            lbl_IBBNFALL.Width = Xwidth;
            lbl_IBBNFALL.Height = Yheight;
            lbl_IBBNFALL.Text = "IBBNFALL";
            lbl_IBBNFALL.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_IBBNFALL.BackColor = Color.Coral;
            this.Controls.Add(lbl_IBBNFALL);
            txt_LWRIBBNFALL.Width = Xwidth;
            txt_LWRIBBNFALL.Height = Yheight;
            txt_LWRIBBNFALL.Enabled = true;
            txt_LWRIBBNFALL.BackColor = Color.White;
            txt_LWRIBBNFALL.Name = "IBBNFALL";
            txt_LWRIBBNFALL.Text = IBBNFALLDefaultValue.ToString();
            txt_LWRIBBNFALL.TabIndex = (int)LogicalRegisters.IBBNFALL;
            txt_LWRIBBNFALL.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRIBBNFALL);

            lbl_IFF.Width = Xwidth;
            lbl_IFF.Height = Yheight;
            lbl_IFF.Text = "IFF";
            lbl_IFF.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_IFF.BackColor = Color.Coral;
            this.Controls.Add(lbl_IFF);
            txt_LWRIFF.Width = Xwidth;
            txt_LWRIFF.Height = Yheight;
            txt_LWRIFF.Enabled = true;
            txt_LWRIFF.BackColor = Color.White;
            txt_LWRIFF.Name = "IFF";
            txt_LWRIFF.Text = IFFDefaultValue.ToString();
            txt_LWRIFF.TabIndex = (int)LogicalRegisters.IFF;
            txt_LWRIFF.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRIFF);

            lbl_IBPIFF1REF.Width = Xwidth;
            lbl_IBPIFF1REF.Height = Yheight;
            lbl_IBPIFF1REF.Text = "IBPIFF1REF";
            lbl_IBPIFF1REF.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_IBPIFF1REF.BackColor = Color.Coral;
            this.Controls.Add(lbl_IBPIFF1REF);
            txt_LWRIBPIFF1REF.Width = Xwidth;
            txt_LWRIBPIFF1REF.Height = Yheight;
            txt_LWRIBPIFF1REF.Enabled = true;
            txt_LWRIBPIFF1REF.BackColor = Color.White;
            txt_LWRIBPIFF1REF.Name = "IBPIFF1REF";
            txt_LWRIBPIFF1REF.Text = IBPIFF1REFDefaultValue.ToString();
            txt_LWRIBPIFF1REF.TabIndex = (int)LogicalRegisters.IBPIFF1REF;
            txt_LWRIBPIFF1REF.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRIBPIFF1REF);

            lbl_IBPOPAMP.Width = Xwidth;
            lbl_IBPOPAMP.Height = Yheight;
            lbl_IBPOPAMP.Text = "IBPOPAMP";
            lbl_IBPOPAMP.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_IBPOPAMP.BackColor = Color.Coral;
            this.Controls.Add(lbl_IBPOPAMP);
            txt_LWRIBPOPAMP.Width = Xwidth;
            txt_LWRIBPOPAMP.Height = Yheight;
            txt_LWRIBPOPAMP.Enabled = true;
            txt_LWRIBPOPAMP.BackColor = Color.White;
            txt_LWRIBPOPAMP.Name = "IBPOPAMP";
            txt_LWRIBPOPAMP.Text = IBPOPAMPDefaultValue.ToString();
            txt_LWRIBPOPAMP.TabIndex = (int)LogicalRegisters.IBPOPAMP;
            txt_LWRIBPOPAMP.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRIBPOPAMP);

            lbl_IB_T.Width = Xwidth;
            lbl_IB_T.Height = Yheight;
            lbl_IB_T.Text = "IB_T";
            lbl_IB_T.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_IB_T.BackColor = Color.Coral;
            this.Controls.Add(lbl_IB_T);
            txt_LWRIB_T.Width = Xwidth;
            txt_LWRIB_T.Height = Yheight;
            txt_LWRIB_T.Enabled = true;
            txt_LWRIB_T.BackColor = Color.White;
            txt_LWRIB_T.Name = "IB_T";
            txt_LWRIB_T.Text = IB_TDefaultValue.ToString();
            txt_LWRIB_T.TabIndex = (int)LogicalRegisters.IB_T;
            txt_LWRIB_T.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRIB_T);

            lbl_IFFP2.Width = Xwidth;
            lbl_IFFP2.Height = Yheight;
            lbl_IFFP2.Text = "IFFP2";
            lbl_IFFP2.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_IFFP2.BackColor = Color.Coral;
            this.Controls.Add(lbl_IFFP2);
            txt_LWRIFFP2.Width = Xwidth;
            txt_LWRIFFP2.Height = Yheight;
            txt_LWRIFFP2.Enabled = true;
            txt_LWRIFFP2.BackColor = Color.White;
            txt_LWRIFFP2.Name = "IFFP2";
            txt_LWRIFFP2.Text = IFFP2DefaultValue.ToString();
            txt_LWRIFFP2.TabIndex = (int)LogicalRegisters.IFFP2;
            txt_LWRIFFP2.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRIFFP2);

            lbl_IBCOMP.Width = Xwidth;
            lbl_IBCOMP.Height = Yheight;
            lbl_IBCOMP.Text = "IBCOMP";
            lbl_IBCOMP.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_IBCOMP.BackColor = Color.Coral;
            this.Controls.Add(lbl_IBCOMP);
            txt_LWRIBCOMP.Width = Xwidth;
            txt_LWRIBCOMP.Height = Yheight;
            txt_LWRIBCOMP.Enabled = true;
            txt_LWRIBCOMP.BackColor = Color.White;
            txt_LWRIBCOMP.Name = "IBCOMP";
            txt_LWRIBCOMP.Text = IBCOMPDefaultValue.ToString();
            txt_LWRIBCOMP.TabIndex = (int)LogicalRegisters.IBCOMP;
            txt_LWRIBCOMP.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRIBCOMP);

            lbl_VREF.Width = Xwidth;
            lbl_VREF.Height = Yheight;
            lbl_VREF.Text = "VREF";
            lbl_VREF.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_VREF.BackColor = Color.Coral;
            this.Controls.Add(lbl_VREF);
            txt_LWRVREF.Width = Xwidth;
            txt_LWRVREF.Height = Yheight;
            txt_LWRVREF.Enabled = true;
            txt_LWRVREF.BackColor = Color.White;
            txt_LWRVREF.Name = "VREF";
            txt_LWRVREF.Text = VREFDefaultValue.ToString();
            txt_LWRVREF.TabIndex = (int)LogicalRegisters.VREF;
            txt_LWRVREF.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRVREF);

            lbl_VTH.Width = Xwidth;
            lbl_VTH.Height = Yheight;
            lbl_VTH.Text = "VTH";
            lbl_VTH.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_VTH.BackColor = Color.Coral;
            this.Controls.Add(lbl_VTH);
            txt_LWRVTH.Width = Xwidth;
            txt_LWRVTH.Height = Yheight;
            txt_LWRVTH.Enabled = true;
            txt_LWRVTH.BackColor = Color.White;
            txt_LWRVTH.Name = "VTH";
            txt_LWRVTH.Text = VTHDefaultValue.ToString();
            txt_LWRVTH.TabIndex = (int)LogicalRegisters.VTH;
            txt_LWRVTH.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRVTH);

            lbl_GAIN.Width = Xwidth;
            lbl_GAIN.Height = Yheight;
            lbl_GAIN.Text = "GAIN";
            lbl_GAIN.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_GAIN.BackColor = Color.Coral;
            this.Controls.Add(lbl_GAIN);
            txt_LWRGAIN.Width = Xwidth;
            txt_LWRGAIN.Height = Yheight;
            txt_LWRGAIN.Enabled = true;
            txt_LWRGAIN.BackColor = Color.White;
            txt_LWRGAIN.Name = "GAIN";
            txt_LWRGAIN.Text = GAINDefaultValue.ToString();
            txt_LWRGAIN.TabIndex = (int)LogicalRegisters.GAIN;
            txt_LWRGAIN.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRGAIN);

            lbl_PIPEDEL.Width = Xwidth;
            lbl_PIPEDEL.Height = Yheight;
            lbl_PIPEDEL.Text = "PIPEDEL";
            lbl_PIPEDEL.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_PIPEDEL.BackColor = Color.Coral;
            this.Controls.Add(lbl_PIPEDEL);
            txt_LWRPIPEDEL.Width = Xwidth;
            txt_LWRPIPEDEL.Height = Yheight;
            txt_LWRPIPEDEL.Enabled = true;
            txt_LWRPIPEDEL.BackColor = Color.White;
            txt_LWRPIPEDEL.Name = "PIPEDEL";
            txt_LWRPIPEDEL.Text = PIPEDELDefaultValue.ToString();
            txt_LWRPIPEDEL.TabIndex = (int)LogicalRegisters.PIPEDEL;
            txt_LWRPIPEDEL.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRPIPEDEL);

            lbl_IRSEL.Width = Xwidth;
            lbl_IRSEL.Height = Yheight;
            lbl_IRSEL.Text = "IRSEL";
            lbl_IRSEL.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_IRSEL.BackColor = Color.Coral;
            this.Controls.Add(lbl_IRSEL);
            txt_LWRIRSEL.Width = Xwidth;
            txt_LWRIRSEL.Height = Yheight;
            txt_LWRIRSEL.Enabled = true;
            txt_LWRIRSEL.BackColor = Color.White;
            txt_LWRIRSEL.Name = "IRSEL";
            txt_LWRIRSEL.Text = IRSELDefaultValue.ToString();
            txt_LWRIRSEL.TabIndex = (int)LogicalRegisters.IRSEL;
            txt_LWRIRSEL.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRIRSEL);

            lbl_IWSEL.Width = Xwidth;
            lbl_IWSEL.Height = Yheight;
            lbl_IWSEL.Text = "IWSEL";
            lbl_IWSEL.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_IWSEL.BackColor = Color.Coral;
            this.Controls.Add(lbl_IWSEL);
            txt_LWRIWSEL.Width = Xwidth;
            txt_LWRIWSEL.Height = Yheight;
            txt_LWRIWSEL.Enabled = true;
            txt_LWRIWSEL.BackColor = Color.White;
            txt_LWRIWSEL.Name = "IWSEL";
            txt_LWRIWSEL.Text = IWSELDefaultValue.ToString();
            txt_LWRIWSEL.TabIndex = (int)LogicalRegisters.IWSEL;
            txt_LWRIWSEL.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWRIWSEL);

            lbl_INJEX0.Width = Xwidth;
            lbl_INJEX0.Height = Yheight;
            lbl_INJEX0.Text = "INJEX0";
            lbl_INJEX0.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_INJEX0.BackColor = Color.Coral;
            this.Controls.Add(lbl_INJEX0);
            txt_LWINJEX0.Width = Xwidth;
            txt_LWINJEX0.Height = Yheight;
            txt_LWINJEX0.Enabled = true;
            txt_LWINJEX0.BackColor = Color.White;
            txt_LWINJEX0.Name = "INJEX0";
            txt_LWINJEX0.Text = INJEX0DefaultValue.ToString();
            txt_LWINJEX0.TabIndex = (int)LogicalRegisters.INJEX0;
            txt_LWINJEX0.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWINJEX0);

            lbl_INJB0.Width = Xwidth;
            lbl_INJB0.Height = Yheight;
            lbl_INJB0.Text = "INJB0";
            lbl_INJB0.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_INJB0.BackColor = Color.Coral;
            this.Controls.Add(lbl_INJB0);
            txt_LWINJB0.Width = Xwidth;
            txt_LWINJB0.Height = Yheight;
            txt_LWINJB0.Enabled = true;
            txt_LWINJB0.BackColor = Color.White;
            txt_LWINJB0.Name = "INJB0";
            txt_LWINJB0.Text = INJB0DefaultValue.ToString();
            txt_LWINJB0.TabIndex = (int)LogicalRegisters.INJB0;
            txt_LWINJB0.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWINJB0);

            lbl_INJB1.Width = Xwidth;
            lbl_INJB1.Height = Yheight;
            lbl_INJB1.Text = "INJB1";
            lbl_INJB1.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_INJB1.BackColor = Color.Coral;
            this.Controls.Add(lbl_INJB1);
            txt_LWINJB1.Width = Xwidth;
            txt_LWINJB1.Height = Yheight;
            txt_LWINJB1.Enabled = true;
            txt_LWINJB1.BackColor = Color.White;
            txt_LWINJB1.Name = "INJB1";
            txt_LWINJB1.Text = INJB1DefaultValue.ToString();
            txt_LWINJB1.TabIndex = (int)LogicalRegisters.INJB1;
            txt_LWINJB1.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWINJB1);

            lbl_INJB2.Width = Xwidth;
            lbl_INJB2.Height = Yheight;
            lbl_INJB2.Text = "INJB2";
            lbl_INJB2.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_INJB2.BackColor = Color.Coral;
            this.Controls.Add(lbl_INJB2);
            txt_LWINJB2.Width = Xwidth;
            txt_LWINJB2.Height = Yheight;
            txt_LWINJB2.Enabled = true;
            txt_LWINJB2.BackColor = Color.White;
            txt_LWINJB2.Name = "INJB2";
            txt_LWINJB2.Text = INJB2DefaultValue.ToString();
            txt_LWINJB2.TabIndex = (int)LogicalRegisters.INJB2;
            txt_LWINJB2.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWINJB2);

            lbl_INJB3.Width = Xwidth;
            lbl_INJB3.Height = Yheight;
            lbl_INJB3.Text = "INJB3";
            lbl_INJB3.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_INJB3.BackColor = Color.Coral;
            this.Controls.Add(lbl_INJB3);
            txt_LWINJB3.Width = Xwidth;
            txt_LWINJB3.Height = Yheight;
            txt_LWINJB3.Enabled = true;
            txt_LWINJB3.BackColor = Color.White;
            txt_LWINJB3.Name = "INJB3";
            txt_LWINJB3.Text = INJB3DefaultValue.ToString();
            txt_LWINJB3.TabIndex = (int)LogicalRegisters.INJB3;
            txt_LWINJB3.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWINJB3);

            lbl_INJEX33.Width = Xwidth;
            lbl_INJEX33.Height = Yheight;
            lbl_INJEX33.Text = "INJEX33";
            lbl_INJEX33.Font = new Font("Microsoft Sans Serif", 7, FontStyle.Italic);
            lbl_INJEX33.BackColor = Color.Coral;
            this.Controls.Add(lbl_INJEX33);
            txt_LWINJEX33.Width = Xwidth;
            txt_LWINJEX33.Height = Yheight;
            txt_LWINJEX33.Enabled = true;
            txt_LWINJEX33.BackColor = Color.White;
            txt_LWINJEX33.Name = "INJEX33";
            txt_LWINJEX33.Text = INJEX33DefaultValue.ToString();
            txt_LWINJEX33.TabIndex = (int)LogicalRegisters.INJEX33;
            txt_LWINJEX33.Validating += new CancelEventHandler(control_Validating);
            this.Controls.Add(txt_LWINJEX33);
        }

        public bool IsAdvancedGUI { get { return isAdvancedGUI; } }
        public UInt32 RegisterIBP
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.IBP]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.IBP] = value; }
        }
        public UInt32 RegisterIBBNFALL
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.IBBNFALL]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.IBBNFALL] = value; }
        }
        public UInt32 RegisterIFF
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.IFF]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.IFF] = value; }
        }
        public UInt32 RegisterIBPIFF1REF
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.IBPIFF1REF]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.IBPIFF1REF] = value; }
        }
        public UInt32 RegisterIBPOPAMP
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.IBPOPAMP]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.IBPOPAMP] = value; }
        }
        public UInt32 RegisterIB_T
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.IB_T]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.IB_T] = value; }
        }
        public UInt32 RegisterIFFP2
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.IFFP2]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.IFFP2] = value; }
        }
        public UInt32 RegisterIBCOMP
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.IBCOMP]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.IBCOMP] = value; }
        }
        public UInt32 RegisterVREF
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.VREF]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.VREF] = value; }
        }
        public UInt32 RegisterVTH
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.VTH]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.VTH] = value; }
        }
        public UInt32 RegisterGAIN
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.GAIN]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.GAIN] = value; }
        }
        public UInt32 RegisterPIPEDEL
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.PIPEDEL]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.PIPEDEL] = value; }
        }
        public UInt32 RegisterIRSEL
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.IRSEL]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.IRSEL] = value; }
        }
        public UInt32 RegisterIWSEL
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.IWSEL]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.IWSEL] = value; }
        }
        public UInt32 RegisterINJEX0
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.INJEX0]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.INJEX0] = value; }
        }
        public UInt32 RegisterINJB0
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.INJB0]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.INJB0] = value; }
        }
        public UInt32 RegisterINJB1
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.INJB1]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.INJB1] = value; }
        }
        public UInt32 RegisterINJB2
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.INJB2]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.INJB2] = value; }
        }
        public UInt32 RegisterINJB3
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.INJB3]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.INJB3] = value; }
        }
        public UInt32 RegisterINJEX33
        {
            get { return TRIPLogicalReg[(int)LogicalRegisters.INJEX33]; }
            set { TRIPLogicalReg[(int)LogicalRegisters.INJEX33] = value; }
        }

        private void control_Validating(object sender, CancelEventArgs e)
        {
            try
            {
                if (sender is TextBox)
                {
                    switch (((TextBox)sender).TabIndex)
                    {
                        case (int)LogicalRegisters.IBP:
                        case (int)LogicalRegisters.IBBNFALL:
                        case (int)LogicalRegisters.IFF:
                        case (int)LogicalRegisters.IBPIFF1REF:
                        case (int)LogicalRegisters.IBPOPAMP:
                        case (int)LogicalRegisters.IB_T:
                        case (int)LogicalRegisters.IFFP2:
                        case (int)LogicalRegisters.IBCOMP:
                        case (int)LogicalRegisters.VREF:
                        case (int)LogicalRegisters.VTH:
                        case (int)LogicalRegisters.INJB0:
                        case (int)LogicalRegisters.INJB1:
                        case (int)LogicalRegisters.INJB2:
                        case (int)LogicalRegisters.INJB3:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0xFF, 0, "Value must be 8 bits");
                            break;
                        case (int)LogicalRegisters.PIPEDEL:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0x3F, 0, "Value must be 6 bits");
                            break;
                        case (int)LogicalRegisters.GAIN:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0xF, 0, "Value must be 4 bits");
                            break;
                        case (int)LogicalRegisters.IRSEL:
                        case (int)LogicalRegisters.IWSEL:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0x3, 0, "Value must be 2 bits");
                            break;
                        case (int)LogicalRegisters.INJEX0:
                        case (int)LogicalRegisters.INJEX33:
                            CheckInput(sender, e, Convert.ToInt64(((TextBox)sender).Text), 0x1, 0, "Value must be 1 bit");
                            break;
                    }
                }
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

        public void UpdateTRIPLogicalRegArray()
        {
            foreach (Control ctrl in this.Controls)
            {
                if (ctrl.TabIndex < NLogicalRgisters)
                {
                    try
                    {
                        if (ctrl is TextBox)
                            TRIPLogicalReg[ctrl.TabIndex] = Convert.ToUInt32(((TextBox)ctrl).Text);
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
                        ((TextBox)ctrl).Text = TRIPLogicalReg[ctrl.TabIndex].ToString();
                        control_Validating(ctrl, null);
                    }
                }
            }
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
                lbl_VTH.Location = new Point(Xoffset, Yoffset);
                txt_LWRVTH.Location = new Point(lbl_VTH.Left + lbl_VTH.Width + 5, lbl_VTH.Top);
                lbl_VTH.Visible = true;
                txt_LWRVTH.Visible = true;

                CreateLocations(lbl_VTH, lbl_GAIN, txt_LWRGAIN, true, true);
                CreateLocations(lbl_GAIN, lbl_PIPEDEL, txt_LWRPIPEDEL, true, true);
            }
            else
            {
                lbl_IBP.Location = new Point(Xoffset, Yoffset); 
                txt_LWRIBP.Location = new Point(lbl_IBP.Left + lbl_IBP.Width + 5, lbl_IBP.Top);
                lbl_IBP.Visible = true;
                txt_LWRIBP.Visible = true;

                CreateLocations(lbl_IBP, lbl_IBBNFALL, txt_LWRIBBNFALL, true, true);
                CreateLocations(lbl_IBBNFALL, lbl_IFF, txt_LWRIFF, true, true);
                CreateLocations(lbl_IFF, lbl_IBPIFF1REF, txt_LWRIBPIFF1REF, true, true);
                CreateLocations(lbl_IBPIFF1REF, lbl_IBPOPAMP, txt_LWRIBPOPAMP, true, true);
                CreateLocations(lbl_IBPOPAMP, lbl_IB_T, txt_LWRIB_T, true, true);
                CreateLocations(lbl_IB_T, lbl_IFFP2, txt_LWRIFFP2, true, true);
                CreateLocations(lbl_IFFP2, lbl_IBCOMP, txt_LWRIBCOMP, true, true);
                CreateLocations(lbl_IBCOMP, lbl_VREF, txt_LWRVREF, true, true);
                CreateLocations(lbl_VREF, lbl_VTH, txt_LWRVTH, true, true);
                CreateLocations(lbl_VTH, lbl_GAIN, txt_LWRGAIN, true, true);
                CreateLocations(lbl_GAIN, lbl_PIPEDEL, txt_LWRPIPEDEL, true, true);
                CreateLocations(lbl_PIPEDEL, lbl_IRSEL, txt_LWRIRSEL, true, true);
                CreateLocations(lbl_IRSEL, lbl_IWSEL, txt_LWRIWSEL, true, true);
                CreateLocations(lbl_IWSEL, lbl_INJEX0, txt_LWINJEX0, true, true);
                CreateLocations(lbl_INJEX0, lbl_INJB0, txt_LWINJB0, true, true);
                CreateLocations(lbl_INJB0, lbl_INJB1, txt_LWINJB1, true, true);
                CreateLocations(lbl_INJB1, lbl_INJB2, txt_LWINJB2, true, true);
                CreateLocations(lbl_INJB2, lbl_INJB3, txt_LWINJB3, true, true);
                CreateLocations(lbl_INJB3, lbl_INJEX33, txt_LWINJEX33, true, true);
            }

        }

        private void CreateLocations(Control OffsetControl, Label FirstControl, TextBox SecondControl,
            bool FirstControlVisible, bool SecondControlVisible)
        {
            FirstControl.Location = new Point(OffsetControl.Left, OffsetControl.Top + OffsetControl.Height + 5);
            SecondControl.Location = new Point(FirstControl.Left + FirstControl.Width + 5, FirstControl.Top);
            FirstControl.Visible = FirstControlVisible;
            SecondControl.Visible = SecondControlVisible;
        }

    }
}
