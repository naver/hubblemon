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

import time
import socket
import pickle



class remote_handle:
	def __init__(self, entity_table, host, port):
		self.host = host
		self.port = port
		self.entity_table = entity_table

		self.sock = None
		self.version = 0.1

	def connect(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.host, self.port))

	def command(self, cmd, body):
		if self.sock is None:
			self.connect()

		self.sock.send(bytes(cmd, 'utf-8'))
		self.sock.send(bytes(body, 'utf-8'))
		
		packet = self.sock.recv(4096) # RET GET DATA len \n body'

		if packet.find(b'\n') < 0:
			print('>> protocol error: %s' % packet)

		#print(packet)
		header, body = packet.split(b'\n', 1)
		header = header.decode('utf-8')

		if header.count(' ') != 2:
			print('>> protocol error (header): %s' % header)

		RET, GET, CMD, length = header.split()
		length = int(length)

		remain = length - len(body)
		while remain > 0:
			packet = self.sock.recv(remain)
			body += packet
			remain = length - len(body)

		result = pickle.loads(body)
		#print(result)
		return result


	def read(self, ts_from, ts_to, filter = 'None'):

		body = '%s:%d:%d:%s' % (self.entity_table, ts_from, ts_to, filter)
		cmd = 'GET %s %s %d\n' % (self.version, 'DATA', len(body))

		return self.command(cmd, body)


	def get_entity_list(self):
		if self.sock is None:
			self.connect()

		body = 'dummy'
		cmd = 'GET %s %s %d\n' % (self.version, 'ENTITY_LIST', len(body))

		return self.command(cmd, body)

	def get_table_list_of_entity(self, entity, prefix):
		if self.sock is None:
			self.connect()

		body = '%s/%s' % (entity, prefix)
		cmd = 'GET %s %s %d\n' % (self.version, 'TABLE_LIST_OF_ENTITY', len(body))

		return self.command(cmd, body)


	def get_all_table_list(self, prefix):
		if self.sock is None:
			self.connect()

		body = prefix
		cmd = 'GET %s %s %d\n' % (self.version, 'ALL_TABLE_LIST', len(body))

		return self.command(cmd, body)



class remote_storage_manager:
	def __init__(self, addr):
		self.addr = addr
		toks = addr.split(':')
		self.host = toks[0]
		self.port = int(toks[1])

		self.handle = remote_handle(None, self.host, self.port)

	def get_handle(entity_table):
		handle = remote_handle(entity_table, self.host, self.port)
		return handle

	def get_entity_list(self):
		return self.handle.get_entity_list()

	def get_table_list_of_entity(self, entity, prefix):
		return self.handle.get_table_list_of_entity(entity, prefix)

	def get_all_table_list(self, prefix):
		return self.handle.get_all_table_list(prefix)



