import socket, fnmatch, pickle, sys, os

hubblemon_path = os.path.abspath('..')
sys.path.append(hubblemon_path)

import cubrid_mon.settings
import common.settings
import common.core

class cubrid_alarm:
	def __init__(self):
		self.name = 'cubrid'
		self.sec_interval = 5 # 5 sec interval


	def select_db_conf(self, client, instance, map):
		key = '%s:%s' % (client, instance)

		# exact
		if key in map:
			return map[key]

		# wild card match
		for k, v in map.items():
			# overwrite if match like *
			if fnmatch.fnmatch(key, k):
				return map[k]

		return {}

	
	def get_conf(self, client, instance): # client: machine name, instance: dbname
		# select exact conf
		abs_conf = self.select_db_conf(client, instance, cubrid_mon.settings.alarm_conf_absolute)
		lambda_conf = self.select_db_conf(client, instance, cubrid_mon.settings.alarm_conf_lambda)
	
		message_head = '%s:%s' % (client, instance)
		return (message_head, abs_conf, lambda_conf)


