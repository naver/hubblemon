
import socket, fnmatch, pickle, sys, os

import psutil_mon.settings


hubblemon_path = os.path.abspath('..')
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
				return map[k]

		return {}

	def get_conf(self, client, item): # client: machine name, item: items in psutil (ex, cpu, net, disk...)
		# select exact conf
		abs_conf = self.select_conf(client, item, psutil_mon.settings.alarm_conf_absolute)
		lambda_conf = self.select_conf(client, item, psutil_mon.settings.alarm_conf_lambda)
	
		message_head = '%s:%s' % (client, item)
		return (message_head, abs_conf, lambda_conf)



