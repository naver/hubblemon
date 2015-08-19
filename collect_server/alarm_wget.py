import urllib.request
import os



class alarm_wget:
	def __init__(self, encoder):
		self.encoder = encoder

	def send(self, subject, body):
		url = self.encoder(subject, body)
		os.system('wget -O /dev/null "%s" > /dev/null' % url)




