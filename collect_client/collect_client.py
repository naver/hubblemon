
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

import time
import socket
import pickle
import psutil
import zlib

from datetime import datetime


class listener:
	def __init__(self, addr, name, sleep, plugins):
		self.addr = addr
		self.name = name
		self.sleep = sleep
		self.plugins = plugins

		self.ip, self.port = addr.split(':')
		self.ip = socket.gethostbyname(self.ip)
		self.port = int(self.port)
		print (self.ip, self.port)

		self.connected = False

	def connect(self):
		try:
			self.sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			self.sock_server.connect((self.ip, self.port))
			self.sock_server.send(bytes('name:%s' % self.name, 'utf-8'))

			ret = self.sock_server.recv(4096)
			ret = ret.decode('utf-8')
			print('# sock_server recv: %s' % ret)

			toks = ret.split(':')
			if toks[0] == 'redirect':
				ip = toks[1]
				port = toks[2]
				print('# sock redirect: %s, %s' % (ip, port))
				self.sock_listener.connect((ip, int(port)))
			else:
				self.sock_server.close()
				self.connected = False

			self.connected = True

			# initial create 
			result = self.create()
			result['datetime'] = datetime.now()
			result['client'] = self.name
			result['create'] = True

			data = pickle.dumps(result)
			self.send_stat(data)
			ret = self.sock_listener.recv(2) # recv ok
			#print(ret)
			time.sleep(self.sleep)


		except Exception as e:
			print('# %s:%d' % (self.ip, self.port))
			print(e)
			self.sock_server.close();
			self.sock_listener.close();

			
	def close(self):
		self.sock_server.close()
		self.sock_listener.close()

	def create(self):
		stat = {}

		for p in self.plugins:
			result = p.create()
			if p.type not in stat:
				stat[p.type] = {}

			for k, v in result.items():
				stat[p.type][k] = v

		return stat

	def send_stat(self, data):
		if self.connected == False:
			return # skip

		header = 'STAT %s %s %d\n' % (0.1, self.name, len(data))
		#print('# header: %s' % header)

		try:
			self.sock_listener.send(bytes(header, 'utf-8'))
			self.sock_listener.send(data)
		except Exception as e:
			print(e)
			self.connected = False # reconnect later


class collectd:
	def __init__(self, name, addrs, sleep=5, stack=1):
		self.name = name
		self.addrs = addrs

		self.sleep = sleep
		self.stack=stack

		self.plugins = []
		self.listeners = []

		for addr in addrs:
			lst = listener(addr, name, sleep, self.plugins)
			self.listeners.append(lst)
			
	def connect(self):
		for listener in self.listeners:
			if listener.connected == True:
				continue

			listener.connect()

			
	def collect(self):
		stat = {}

		for p in self.plugins:
			result = p.collect()
			if result == None: # recreate signal from plugin
				self.close()
				return None

			if p.type not in stat:
				stat[p.type] = {}

			for k, v in result.items():
				stat[p.type][k] = v

		return stat

	def send_stat_all(self, stat):
		data = pickle.dumps(stat)
		#ret = pickle.loads(data)

		for lst in self.listeners:
			lst.send_stat(data)
			


	def close(self):
		for lst in self.listeners:
			lst.close()

	def daemon(self):
		for p in self.plugins:
			p.sleep_info = self.sleep

		while True:
			try:
				self.connect(); # try connect if disconnect

				result = {}

				if self.stack > 1:
					stats = []
					for i in range(0, self.stack):
						#print('# stack %d' % i)
						stat = self.collect()
						if stat == None:
							continue

						stat['datetime'] = datetime.now()
						stat['client'] = self.name
						stats.append(stat)

						if i < self.stack-1: # skip last sleep
							time.sleep(self.sleep)

					stats = pickle.dumps(stats) 
					stats_zip = zlib.compress(stats)
					result['__stack__'] = stats_zip
				else:
					result = self.collect()
					if result == None:
						continue

				result['datetime'] = datetime.now()
				result['client'] = self.name

				#print(result)
				self.send_stat_all(result)
				time.sleep(self.sleep)

			except Exception as e:
				print(e)
				self.close()
				time.sleep(self.sleep)
				continue

