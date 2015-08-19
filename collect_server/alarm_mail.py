
import smtplib
import time, datetime
from email.mime.text import MIMEText



class alarm_mail:
	def __init__(self, server, fr, to, prefix=None):
		self.server = server
		self.fr = fr
		self.to = to
		self.prefix=prefix
	

	def send(self, subject, body, attr={}):
		now = datetime.datetime.now()
		body_msg = '%s (%s)' % (body, str(now))
		msg = MIMEText(body_msg)

		if self.prefix:
			subject = '%s %s' % (self.prefix, subject)

		msg['Subject'] = subject
		msg['From'] = self.fr
		for k, v in attr.items():
			msg[k] = v

		to_str = ''
		for t in self.to:
			to_str += t + ','
			
		msg['To'] = to_str

		for i in range(0, 5):
			try:
				self.smtp = smtplib.SMTP(self.server)
				self.smtp.set_debuglevel(1)
				ret = self.smtp.sendmail(self.fr, self.to, msg.as_string())
				print(ret)
				self.smtp.quit()
				break
			except Exception as e:
				print(e)
				continue
			
		
	def close(self):
		self.smtp.quit()





		
