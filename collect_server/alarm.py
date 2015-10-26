
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


import os, sys, time

#
# define alarm monitor
#


	

class alarm_node:
	def __init__(self, name, group):
		self.name = name
		self.group = group
		self.prev = None
		self.curr = None
		

class main_alarm:
	def __init__(self, suppress_sec = 0, health_check = []):
		self.plugins = []
		self.nodes = {}
		self.alarm_methods = []
		self.suppress_sec = suppress_sec
		self.last_alarm = {}

		# health check
		self.health_check = health_check
		self.last_health_check = 0
	
	def add_plugin(self, plugin):
		self.plugins.append(plugin)

	def add_node(self, name, group=''):
		node = alarm_node(name, group)
		self.nodes[name] = node

	def do_check(self, data):
		if 'client' not in data:
			print('invalid data, client info not exists')
			return

		if 'datetime' not in data:
			print('invalid data, datetime info not exists')
			return

		client = data['client']
		
		if client not in self.nodes:
			self.add_node(client)

		node = self.nodes[client]

		node.prev = node.curr
		node.curr = data

		if node.prev is None:
			return

		diff_sec = (node.curr['datetime'] - node.prev['datetime']).seconds
		if diff_sec == 0:
			print('# diff_sec of %s zero(%s, %s) ' % (node.curr['client'], str(node.curr['datetime']), str(node.prev['datetime'])))
			return

		for p in self.plugins:
			plugin_name = p.name

			for k, curr_item in node.curr.items():
				if k not in node.prev: # newaly added key
					continue

				if k.startswith(plugin_name + '_'):
					name, instance = k.split('_', 1)
					msg_head, abs_conf, lambda_conf = p.get_conf(client, instance)
					if not msg_head: # something wrong in plugin
						continue

					self.check(msg_head, node.prev[k], curr_item, abs_conf, lambda_conf, diff_sec)
					
			
		# health check
		for check_time in self.health_check:
			ret = check_time.split(':')
			if len(ret) != 2:
				print('# health check setting error: %s' % check_time)

			h = int(ret[0])
			m = int(ret[1])

			tm = time.localtime()
			ts = time.time()
			if tm.tm_hour == h:
				if tm.tm_min == m and ts > self.last_health_check + 60*2:
					self.last_health_check = ts
					for method in self.alarm_methods:
						msg = 'Arcus alarm Health check (%d:%d)' % (os.getpid(), ts)
						method.send(msg, msg)
			
	def check(self, msg_head, prev_item, curr_item, abs_conf, lambda_conf, diff_sec):
		if not isinstance(curr_item, dict):
			return

		# check absolute value
		for k, v in abs_conf.items(): # ex) k=evictions, v=(20000, 60000, 80000)
			if len(v) < len(self.alarm_methods):
				continue

			if k not in curr_item or k not in prev_item:
				continue
			
			abs_value = (curr_item[k] - prev_item[k])/diff_sec

			for i in range(len(self.alarm_methods), 0, -1):
				idx = i-1

				if v[idx] and abs_value > v[idx]:
					method = self.alarm_methods[idx]

					# msg_head: alarm message head (instance id)
					# k: stat name (like cmd_get)
					# idx: alarm level
					self.alarm(method, '[%s] absolute value of %s(%d) exceeds %s' % (msg_head, k, abs_value, v[idx]), '%s.%s(%d)' % (msg_head, k, idx))
	

		# check lambda
		for lambda_func, limits in lambda_conf.items(): # ex) lambda_func= lambda x, limit: x['total_malloced'] / x['limit_maxbytes'] > limit, limits=(0.7, 0,7, 0.90)
			if len(limits) < len(self.alarm_methods):
				continue


			for i in range(len(self.alarm_methods), 0, -1):
				idx = i-1

				if limits[idx]:
					try:
						result, message = lambda_func(curr_item, limits[idx])
					except Exception as e:
						print('# exception: %s' % str(e))
						continue


					if result == True:
						method = self.alarm_methods[idx]

						# msg_head: alarm message head (instance id)
						# message: alarm message is made by lambda function
						# idx: alarm level
						self.alarm(method, '[%s] %s' % (msg_head, message), '%s.%s(%d)' % (msg_head, str(lambda_func), idx))
			



	def alarm(self, method, msg, type=''):
		ts = time.time()

		if type in self.last_alarm:
			last_ts = self.last_alarm[type]
			if last_ts + self.suppress_sec > ts:
				return
			
		print('## alarm msg: %s' % msg)
		method.send(msg, msg)
		self.last_alarm[type] = ts
	
			

