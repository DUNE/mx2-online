namespace SlowControl
{
    partial class frmMain
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
            this.btn_ShowFirstCrate = new System.Windows.Forms.Button();
            this.btn_ShowSecondCrate = new System.Windows.Forms.Button();
            this.btn_ResetFirstCrate = new System.Windows.Forms.Button();
            this.btn_ResetSecondCrate = new System.Windows.Forms.Button();
            this.chk_FirstCrate = new System.Windows.Forms.CheckBox();
            this.chk_SecondCrate = new System.Windows.Forms.CheckBox();
            this.label1 = new System.Windows.Forms.Label();
            this.SuspendLayout();
            // 
            // btn_ShowFirstCrate
            // 
            this.btn_ShowFirstCrate.BackColor = System.Drawing.Color.Coral;
            this.btn_ShowFirstCrate.Enabled = false;
            this.btn_ShowFirstCrate.Location = new System.Drawing.Point(35, 30);
            this.btn_ShowFirstCrate.Name = "btn_ShowFirstCrate";
            this.btn_ShowFirstCrate.Size = new System.Drawing.Size(150, 20);
            this.btn_ShowFirstCrate.TabIndex = 103;
            this.btn_ShowFirstCrate.Text = "Show First Crate";
            this.btn_ShowFirstCrate.UseVisualStyleBackColor = false;
            this.btn_ShowFirstCrate.Click += new System.EventHandler(this.btn_ShowFirstCrate_Click);
            // 
            // btn_ShowSecondCrate
            // 
            this.btn_ShowSecondCrate.BackColor = System.Drawing.Color.Coral;
            this.btn_ShowSecondCrate.Enabled = false;
            this.btn_ShowSecondCrate.Location = new System.Drawing.Point(35, 56);
            this.btn_ShowSecondCrate.Name = "btn_ShowSecondCrate";
            this.btn_ShowSecondCrate.Size = new System.Drawing.Size(150, 20);
            this.btn_ShowSecondCrate.TabIndex = 104;
            this.btn_ShowSecondCrate.Text = "Show Second Crate";
            this.btn_ShowSecondCrate.UseVisualStyleBackColor = false;
            this.btn_ShowSecondCrate.Click += new System.EventHandler(this.btn_ShowSecondCrate_Click);
            // 
            // btn_ResetFirstCrate
            // 
            this.btn_ResetFirstCrate.BackColor = System.Drawing.Color.Coral;
            this.btn_ResetFirstCrate.Enabled = false;
            this.btn_ResetFirstCrate.Location = new System.Drawing.Point(191, 30);
            this.btn_ResetFirstCrate.Name = "btn_ResetFirstCrate";
            this.btn_ResetFirstCrate.Size = new System.Drawing.Size(76, 20);
            this.btn_ResetFirstCrate.TabIndex = 105;
            this.btn_ResetFirstCrate.Text = "RST Crate";
            this.btn_ResetFirstCrate.UseVisualStyleBackColor = false;
            this.btn_ResetFirstCrate.Click += new System.EventHandler(this.btn_ResetFirstCrate_Click);
            // 
            // btn_ResetSecondCrate
            // 
            this.btn_ResetSecondCrate.BackColor = System.Drawing.Color.Coral;
            this.btn_ResetSecondCrate.Enabled = false;
            this.btn_ResetSecondCrate.Location = new System.Drawing.Point(191, 56);
            this.btn_ResetSecondCrate.Name = "btn_ResetSecondCrate";
            this.btn_ResetSecondCrate.Size = new System.Drawing.Size(76, 20);
            this.btn_ResetSecondCrate.TabIndex = 106;
            this.btn_ResetSecondCrate.Text = "RST Crate";
            this.btn_ResetSecondCrate.UseVisualStyleBackColor = false;
            this.btn_ResetSecondCrate.Click += new System.EventHandler(this.btn_ResetSecondCrate_Click);
            // 
            // chk_FirstCrate
            // 
            this.chk_FirstCrate.AutoSize = true;
            this.chk_FirstCrate.Location = new System.Drawing.Point(13, 34);
            this.chk_FirstCrate.Name = "chk_FirstCrate";
            this.chk_FirstCrate.Size = new System.Drawing.Size(15, 14);
            this.chk_FirstCrate.TabIndex = 107;
            this.chk_FirstCrate.UseVisualStyleBackColor = true;
            this.chk_FirstCrate.CheckedChanged += new System.EventHandler(this.chk_FirstCrate_CheckedChanged);
            // 
            // chk_SecondCrate
            // 
            this.chk_SecondCrate.AutoSize = true;
            this.chk_SecondCrate.Location = new System.Drawing.Point(13, 60);
            this.chk_SecondCrate.Name = "chk_SecondCrate";
            this.chk_SecondCrate.Size = new System.Drawing.Size(15, 14);
            this.chk_SecondCrate.TabIndex = 108;
            this.chk_SecondCrate.UseVisualStyleBackColor = true;
            this.chk_SecondCrate.CheckedChanged += new System.EventHandler(this.chk_SecondCrate_CheckedChanged);
            // 
            // label1
            // 
            this.label1.BackColor = System.Drawing.Color.Coral;
            this.label1.Location = new System.Drawing.Point(10, 9);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(257, 15);
            this.label1.TabIndex = 109;
            this.label1.Text = "Select VME Crate to communicate with";
            this.label1.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // frmMain
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(291, 88);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.chk_SecondCrate);
            this.Controls.Add(this.chk_FirstCrate);
            this.Controls.Add(this.btn_ResetSecondCrate);
            this.Controls.Add(this.btn_ResetFirstCrate);
            this.Controls.Add(this.btn_ShowFirstCrate);
            this.Controls.Add(this.btn_ShowSecondCrate);
            this.Name = "frmMain";
            this.StartPosition = System.Windows.Forms.FormStartPosition.Manual;
            this.Text = "VME Crates";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button btn_ShowFirstCrate;
        private System.Windows.Forms.Button btn_ShowSecondCrate;
        private System.Windows.Forms.Button btn_ResetFirstCrate;
        private System.Windows.Forms.Button btn_ResetSecondCrate;
        private System.Windows.Forms.CheckBox chk_FirstCrate;
        private System.Windows.Forms.CheckBox chk_SecondCrate;
        private System.Windows.Forms.Label label1;

    }
}