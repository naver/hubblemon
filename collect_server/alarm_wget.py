
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


import urllib.request
import os, time



class alarm_wget:
	def __init__(self, encoder, block_time = None):
		self.encoder = encoder
		self.block_time = block_time

	def send(self, subject, body):
		if self.block_time is not None:
			start = self.block_time[0]
			ret = start.split(':')
			sm = int(ret[0])*60 + int(ret[1])
			
			end = self.block_time[1]
			ret = end.split(':')
			em = int(ret[0])*60 + int(ret[1])

			tm = time.localtime()
			cm = tm.tm_hour * 60 + tm.tm_min
		
			if em > sm: # not cross midnight
				if cm > sm and cm < em:
					print('alarm blocked')
					return
			else: # cross midnight
				if cm > sm or cm < em:
					print('alarm blocked')
					return

		url = self.encoder(subject, body)
		os.system('wget -O /dev/null "%s" > /dev/null' % url)




