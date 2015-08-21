
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

import socket, select, time, pickle, zlib

import settings


class CollectListener:
	def __init__(self, port):
		self.port = port;
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock_node_map = {}
		self.plugins = []

	def put_plugin(self, plug):
		self.plugins.append(plug)

	def listen(self, count = -1):
		print('# CollectListener listen (%s)' % (self.port))
		#print(socket.gethostname())
		#print(self.port)
		
		self.sock.bind((socket.gethostname(), self.port))
		self.sock.listen(5)

		idx = 0
		while count < 0 or idx < count:
			idx += 1

			inputs = [self.sock]
			for sock in self.sock_node_map:
				inputs.append(sock)

			readable, writable, exceptional = select.select(inputs, [], inputs)

			for sock in readable:
				if sock == self.sock: # new client
					conn, addr = self.sock.accept()
					self.sock_node_map[conn] = CollectNode(conn, self.plugins)
					print ('[%d]connect from %s(%s)' % (self.port, addr, conn.fileno()))
					continue

				else:
					#print ('select read %d' % sock.fileno())
					node = self.sock_node_map[sock]



					# for dev (to check stack trace)
					if node.do_op() == False:
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
	def __init__(self, socket, plugins):
		self.sock = socket

		self.name_plugin_map = {}
		self.plugins = []
		for p in plugins:
			self.name_plugin_map[p.name] = p
			self.plugins.append(p.clone())

	def do_op(self):
		data = self.sock.recv(4096)
		if not data:
			return False

		header, data = data.split(b'\n', 1)
		dummy, version, name, length = header.split()
		#print(header)

		remain = int(length) - len(data)
		while remain > 0:
			packet = self.sock.recv(remain)
			data += packet
			remain = int(length) - len(data)	

		#print('recv: %d' % len(data))
		result = pickle.loads(data)
		#print(result)

		hostname = result['client']
		if 'create' in result and result['create'] == True:
			for k, v in result.items():
				#print('## ', k)
				if k == 'client' or k == 'datetime':
					continue

				if k not in self.name_plugin_map:
					# TODO: error
					continue

				p = self.name_plugin_map[k]
				p.create_data(hostname, v)
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
					if k == 'client' or k == 'datetime':
						continue

					if k not in self.name_plugin_map:
						# TODO: error
						continue

					p = self.name_plugin_map[k]
					p.update_data(hostname, result['datetime'].timestamp(), v)

					# tmp: add client, ts
					v['client'] = result['client']
					v['datetime'] = result['datetime']
					settings.main_alarm.do_check(v)
		
		#print('recv: %d & done' % len(data))
		return True
		
	def disconnect(self):
		self.sock.close()


