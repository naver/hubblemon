
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

import socket, fnmatch, pickle, sys, os

import psutil_mon.settings


hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)
import common.settings

class psutil_alarm:
	def __init__(self):
		self.name = 'psutil'
		self.sec_interval = 5 # 5 sec interval

	def system_list_init(self):
		pass
		

	def select_conf(self, client, item, map):
		key = '%s:%s' % (client, item)

		# exact
		if key in map:
			return map[key]

		# wild card match
		for k, v in map.items():
			# overwrite if match like net-*
			if fnmatch.fnmatch(key, k):
				if 'IGNORE' in v:
					if fnmatch.fnmatch(key, v['IGNORE']): # skip IGNORE case
						continue
				return v

		return {}

	def get_conf(self, client, item): # client: machine name, item: items in psutil (ex, cpu, net, disk...)
		# select exact conf
		abs_conf = self.select_conf(client, item, psutil_mon.settings.alarm_conf_absolute)
		lambda_conf = self.select_conf(client, item, psutil_mon.settings.alarm_conf_lambda)
	
		message_head = '%s:%s' % (client, item)
		return (message_head, abs_conf, lambda_conf)



