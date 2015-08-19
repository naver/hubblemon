import socket, fnmatch, pickle, sys, os

hubblemon_path = os.path.abspath('..')
sys.path.append(hubblemon_path)

import memcached_mon.settings
import common.settings
import common.core

class memcached_alarm:
	def __init__(self):
		self.name = 'memcached'
		self.sec_interval = 5 # 5 sec interval


	def select_mc_conf(self, client, instance, map):
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

	
	def get_conf(self, client, instance): # client: machine name, instance: port
		# select exact conf
		abs_conf = self.select_mc_conf(client, instance, memcached_mon.settings.alarm_conf_absolute)
		lambda_conf = self.select_mc_conf(client, instance, memcached_mon.settings.alarm_conf_lambda)
	
		message_head = '%s:%s' % (client, instance)
		return (message_head, abs_conf, lambda_conf)


