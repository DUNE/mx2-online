using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Threading;

namespace SlowControl
{
    public partial class frmMain : Form
    {
        frmSlowControl scFirstCrate;
        frmSlowControl scSecondCrate;
        bool scFormSuccess = false;
        
        public frmMain()
        {
            InitializeComponent();
            this.AutoSizeMode = AutoSizeMode.GrowAndShrink;
            this.StartPosition = FormStartPosition.Manual;
            this.Location = new Point((Screen.PrimaryScreen.Bounds.Width - this.Width) / 2, 
                Screen.PrimaryScreen.Bounds.Height/100);
        }

        private void chk_FirstCrate_CheckedChanged(object sender, EventArgs e)
        {
            //try
            //{
                if (((CheckBox)sender).Checked)
                {
                    scFirstCrate = new frmSlowControl(0, 0, out scFormSuccess);
                    if (scFormSuccess)
                    {
                        scFirstCrate.ControlBox = false;
                        scFirstCrate.StartPosition = FormStartPosition.Manual;
                        scFirstCrate.Location = new Point(0, this.Bottom);
                        scFirstCrate.Width = Screen.PrimaryScreen.Bounds.Width / 2;
                        btn_ShowFirstCrate.Enabled = true;
                        btn_ResetFirstCrate.Enabled = true;
                    }
                    else
                    {
                        ((CheckBox)sender).Checked = false;
                        return;
                    }
                }
                else
                {
                    scFirstCrate.Close();
                    btn_ShowFirstCrate.Text = "Show First Crate";
                    btn_ShowFirstCrate.BackColor = Color.Coral;
                    btn_ShowFirstCrate.Enabled = false;
                    btn_ResetFirstCrate.Enabled = false;
                }
            //}
            //catch (Exception ex)
            //{
            //    MessageBox.Show(ex.Message);
            //    ((CheckBox)sender).Checked = false;
            //}
        }

        private void chk_SecondCrate_CheckedChanged(object sender, EventArgs e)
        {
            //try
            //{
                if (((CheckBox)sender).Checked)
                {
                    scSecondCrate = new frmSlowControl(0, 1, out scFormSuccess);
                    if (scFormSuccess)
                    {
                        scSecondCrate.ControlBox = false;
                        scSecondCrate.StartPosition = FormStartPosition.Manual;
                        scSecondCrate.Location = new Point(Screen.PrimaryScreen.Bounds.Width / 2, this.Bottom);
                        scSecondCrate.Width = Screen.PrimaryScreen.Bounds.Width / 2;
                        btn_ShowSecondCrate.Enabled = true;
                        btn_ResetSecondCrate.Enabled = true;
                    }
                    else
                    {
                        ((CheckBox)sender).Checked = false;
                        return;
                    }
                }
                else
                {
                    scSecondCrate.Close();
                    btn_ShowSecondCrate.Text = "Show Second Crate";
                    btn_ShowSecondCrate.BackColor = Color.Coral;
                    btn_ShowSecondCrate.Enabled = false;
                    btn_ResetSecondCrate.Enabled = false;
                }
            //}
            //catch (Exception ex)
            //{
            //    MessageBox.Show(ex.Message);
            //    ((CheckBox)sender).Checked = false;
            //}
        }
        
        private void btn_ShowFirstCrate_Click(object sender, EventArgs e)
        {
            if (btn_ShowFirstCrate.Text == "Show First Crate")
            {
                btn_ShowFirstCrate.Text = "Loading... First Crate";
                btn_ShowFirstCrate.BackColor = Color.LightBlue;
                Refresh();
                scFirstCrate.Show();
                btn_ShowFirstCrate.Text = "Hide First Crate";
                return;
            }
            if (btn_ShowFirstCrate.Text == "Hide First Crate")
            {
                btn_ShowFirstCrate.Text = "Show First Crate";
                btn_ShowFirstCrate.BackColor = Color.Coral;
                scFirstCrate.Hide();
                return;
            }
        }

        private void btn_ShowSecondCrate_Click(object sender, EventArgs e)
        {
            if (btn_ShowSecondCrate.Text == "Show Second Crate")
            {
                btn_ShowSecondCrate.Text = "Loading... Second Crate";
                btn_ShowSecondCrate.BackColor = Color.LightBlue;
                Refresh();
                if (scSecondCrate != null) scSecondCrate.Show();
                btn_ShowSecondCrate.Text = "Hide Second Crate";
                return;
            }
            if (btn_ShowSecondCrate.Text == "Hide Second Crate")
            {
                btn_ShowSecondCrate.Text = "Show Second Crate";
                btn_ShowSecondCrate.BackColor = Color.Coral;
                scSecondCrate.Hide();
                return;
            }
        }

        private void btn_ResetFirstCrate_Click(object sender, EventArgs e)
        {
            scFirstCrate.controller.Reset();
        }

        private void btn_ResetSecondCrate_Click(object sender, EventArgs e)
        {
            scSecondCrate.controller.Reset();
        }

 
    }
}
