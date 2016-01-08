
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

import socket, select, time, pickle
import binascii # crc32

import settings
from collect_listener import CollectListener



class CollectServer:
	def __init__(self, port):
		self.port = port;
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.sock_addr_map = {}
		self.listeners = []

	def put_listener(self, addr):
		self.listeners.append(addr)
		self.listeners.sort()
		#print(self.listeners)
		
	def select_listener(self, addr):
		ret = binascii.crc32(bytes(addr, 'utf-8'))
		n = len(self.listeners)
		idx = ret % n
		#print('#hash %s:%d % %d => %d' % (addr, ret, n, idx))
		return self.listeners[idx]

	def listen(self, count = -1):
		self.sock.bind((socket.gethostname(), self.port))
		self.sock.listen(5)

		idx = 0
		while count < 0 or idx < count:
			idx += 1

			inputs = [self.sock]
			for sock in self.sock_addr_map:
				inputs.append(sock)

			readable, writable, exceptional = select.select(inputs, [], inputs)

			for sock in readable:
				if sock == self.sock: # new client
					conn, addr = self.sock.accept()
					ret = conn.recv(4096).decode('utf-8')
					toks = ret.split(':')
					if len(toks) < 2 or toks[0] != 'name':
						print('# recv invalid: %s' % ret)
						conn.close()
						continue

					name = toks[1]
						
					listener = self.select_listener(name)
					self.sock_addr_map[conn] = name
					print ('connect by %s(%s, %s)' % (name, addr[0], conn.fileno()))
					print ('redirect to %s' % listener)

					conn.send(bytes('redirect:%s' % listener, 'utf-8'))
					continue

				else:
					print('invalid read from client: %s, maybe reconnect' % self.sock_addr_map[sock])

					'''
					ret = sock.recv(4096).decode('utf-8')
					toks = ret.split(':')
					if len(toks) < 2 or toks[0] != 'name':
						sock.close()
						continue

					name = toks[1]
						
					listener = self.select_listener(name)
					self.sock_addr_map[conn] = name
					print ('connect by %s(%s, %s)' % (name, addr[0], conn.fileno()))
					print ('redirect to %s' % listener)

					conn.send(bytes('redirect:%s' % listener, 'utf-8'))
					continue
					'''
					
					sock.close()
					del self.sock_addr_map[sock]

			for sock in exceptional:
				print ('disconnected: %s' % self.sock_addr_map[sock])
				sock.close()
				del self.sock_addr_map[sock]


