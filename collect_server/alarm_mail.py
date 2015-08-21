
#
# Hubblemon - Yet another general purpose system monitor
#
# Copyright 2015 NAVER Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
				print('# smtp ret: %s' % ret)
				self.smtp.quit()
				break
			except Exception as e:
				print('# smtp exception: %s' % str(e))
				continue
			
		
	def close(self):
		self.smtp.quit()





		
