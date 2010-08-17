import smtplib
import email.mime
from email.Utils import COMMASPACE, formatdate
import os

from mnvruncontrol.configuration import Configuration

def sendMail(fro, to, subject, text, files=[], server="localhost"):
	""" Sends an e-mail with optional text file attachments. """ 
	assert type(to) == list
	assert type(files) == list
	
	msg = email.mime.Multipart.MIMEMultipart("mixed")
	msg['From'] = fro
	msg['To'] = COMMASPACE.join(to)
	msg['Date'] = formatdate(localtime=True)
	msg['Subject'] = subject
	msg.attach( email.mime.Text.MIMEText(text) )
	for file in files:
		part = email.mime.Text.MIMEText(open(file,"rb").read(), "plain")
		part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
		msg.attach(part)
	smtp = smtplib.SMTP(server)
	smtp.sendmail(fro, to, msg.as_string() )
	smtp.close()


