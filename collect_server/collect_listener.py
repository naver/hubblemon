
# See the License for the specific language governing permissions and
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

import os, sys
import socket, select, time, pickle, zlib

import settings

hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)

import common.core

class CollectListener:
	def __init__(self, port):
		self.port = port;
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock_node_map = {}
		self.plugins = {}

	def put_plugin(self, name, plug):
		self.plugins[name] = plug

	def listen(self, count = -1):
		print('# CollectListener listen (%s)' % (self.port))
		#print(socket.gethostname())
		#print(self.port)
		
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((socket.gethostname(), self.port))
		self.sock.listen(5)

		while True:
			inputs = [self.sock]
			for sock in self.sock_node_map:
				inputs.append(sock)

			readable, writable, exceptional = select.select(inputs, [], inputs)

			for sock in readable:
				if sock == self.sock: # new client
					conn, addr = self.sock.accept()
					self.sock_node_map[conn] = CollectNode(conn, addr, self.plugins)
					print ('[%d]connect from %s(%s)' % (self.port, addr, conn.fileno()))
					continue

				else:
					#print ('select read %d' % sock.fileno())
					node = self.sock_node_map[sock]



					# for dev (to check stack trace)
					if node.do_op() == False:
						print ('disconnected by exception: %d' % sock.fileno())
						node.disconnect()
						del self.sock_node_map[sock]

					'''
					# for real
					try:
						if node.do_op() == False:
							node.disconnect()
							del self.sock_node_map[sock]
					except Exception as e:
						print(e)
						node.disconnect()
						del self.sock_node_map[sock]
					'''

					

			for sock in exceptional:
				print ('disconnected: %d' % sock.fileno())
				node.disconnect()
				del self.sock_node_map[sock]





class CollectNode:
	def __init__(self, socket, addr, plugins):
		self.sock = socket
		self.addr = addr

		self.plugins = plugins
		#for k, v in plugins.items():
		#	self.plugins[k] = v.clone()

		self.addr = addr

	def do_op(self):
		packet = self.sock.recv(128)
		#if self.addr[0] == '127.0.0.1':
			#print(packet)

		#print(packet)
		if not packet:
			return False

		if packet.find(b'\n') < 0:
			print('>> protocol error (stat): %s' % packet)
			return False

		header, body = packet.split(b'\n', 1)
		try:
			header = header.decode('utf-8')
		except UnicodeDecodeError as e:
			print('>> protocol utf-8 error (stat): %s' % packet)
			print(e)
			print(header)
			return False

		if header.count(' ') != 3:
			print('>> protocol error (stat-header): %s' % header)
			return False

		type, version, cmd, length = header.split(' ', 3)

		length = int(length)
		remain = length - len(body)
		while remain > 0:
			packet = self.sock.recv(remain)
			body += packet
			remain = length - len(body)	

		# STAT VERSION HOST LENGTH
		if type == 'STAT':
			#print('recv: %d' % len(body))
			ret = self.do_stat(version, body)
			if ret == False:
				return False

		# GET VERSION CMD INFO
		elif type == 'GET':
			ret = self.do_get(version, cmd, body.decode('utf-8'))
			if ret is None:
				return False

			data = pickle.dumps(ret)
			print('RET GET DATA %d\n' % len(data))
			self.sock.send(bytes('RET GET DATA %d\n' % len(data), 'utf-8')) 
			self.sock.send(data)

	def do_get(self, version, cmd, info):
		if cmd == 'DATA':
			if info.count(':') != 3:
				print('>> protocol error (get): %s' % info)
				return None

			path, start_ts, end_ts, filter = info.split(':', 3)

			handle = common.core.get_default_local_handle(path)
			ret = handle.read(start_ts, end_ts)
			return ret
		else:
			print('protocol error (cmd): %s' % cmd)
			return None


		'''
		elif cmd == 'ENTITY_LIST':
			entity_list = []
			for dir in os.listdir(self.basedir):
				dir_path = os.path.join(self.basedir, dir)
				if os.path.isdir(dir_path):
					entity_list.append(dir)
			
			return entity_list
		
		elif cmd == 'TABLE_LIST_OF_ENTITY':
			table_list = []
			client, prefix = info.split('/')
			path = os.path.join(self.basedir, client)

			for file in os.listdir(path):
				if file.startswith(prefix):
					table_list.append(file)

			return table_list

		elif cmd == 'ALL_TABLE_LIST':
			table_list = []
			for dir in os.listdir(self.basedir):
				dir_path = os.path.join(self.basedir, dir)

				if os.path.isdir(dir_path):
					for file in os.listdir(dir_path):
						if file.startswith(prefix):
							table_list.append(dir + '/' + file)

			return table_list
		'''


	def do_stat(self, version, data):
		result = pickle.loads(data)
		#print(result)

		hostname = result['client']
		if 'create' in result and result['create'] == True:
			for k, v in result.items():
				#print('## ', k)
				if k == 'client' or k == 'datetime' or k == 'create':
					continue

				if k not in self.plugins:
					k = 'default' # retry as 'defaut'

				if k not in self.plugins:
					# TODO: error
					continue

				p = self.plugins[k]
				ret = p.create_data(hostname, v)
				if ret == False:
					return False

				self.sock.send(b'OK')
		else:
			if '__stack__' in result:
				zip_data = result['__stack__']
				pick_data = zlib.decompress(zip_data)
				results = pickle.loads(pick_data)
			else:
				results = [ result ]

			for result in results:
				for k, v in result.items():
					#print('## ', k)
					if k == 'client' or k == 'datetime' or k == 'create':
						continue

					if k not in self.plugins:
						k = 'default' # retry as 'defaut'

					if k not in self.plugins:
						# TODO: error
						continue

					p = self.plugins[k]
					ret = p.update_data(hostname, result['datetime'].timestamp(), v)
					if ret == False:
						return False

					# tmp: add client, ts
					v['client'] = result['client']
					v['datetime'] = result['datetime']
					settings.main_alarm.do_check(v)
		
		#print('recv: %d & done' % len(data))
		return True
		
	def disconnect(self):
		self.sock.close()


