#
# arcus-python-client - Arcus python client drvier
# Copyright 2014 NAVER Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License")
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
 

import telnetlib, os, sys
import socket
import threading



from kazoo.client import KazooClient
import kazoo
from kazoo.exceptions import *


class arcus_cache:
	def __init__(self, zk_addr, code):
		self.code = code
		self.zk_addr = zk_addr
		self.node = []
		self.active_node = []
		self.dead_node = []
		self.meta = ['', None]

	def __repr__(self):
		repr = '[Service Code: %s] (zk:%s)\n (node) %s\n (active) %s\n (dead) %s' % (self.code, self.zk_addr, self.node, self.active_node, self.dead_node)
		return repr


class arcus_node:
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port 

		self.name = ''
		self.code = ''
		self.zk_addr = ''
		self.active = False

		self.noport = False

	def __repr__(self):
		if self.name and self.code:
			return '[%s:%s-(%s,%s)]' % (self.ip, self.port, self.name, self.code)
		elif self.name:
			return '[%s:%s-(%s)]' % (self.ip, self.port, self.name)
		elif self.code:
			return '[%s:%s-(%s)]' % (self.ip, self.port, self.code)

		return '[%s:%s]' % (self.ip, self.port)

	def do_arcus_command(self, command, timeout=0.2):
		tn = telnetlib.Telnet(self.ip, self.port)
		tn.write(bytes(command + '\r\n', 'utf-8'))

		if command[0:5] == 'scrub' or command[0:5] == 'flush':
			message = 'OK'
		else:
			message = 'END'

		result = tn.read_until(bytes(message, 'utf-8'), timeout)

		result = result.decode('utf-8')
		tn.write(bytes('quit\r\n', 'utf-8'))
		tn.close()
		return result


class zookeeper:
	def __init__(self, address):
		self.address = address
		self.zk = KazooClient(address)
		self.zk.start()

		self.arcus_cache_map = {} 
		self.arcus_node_map = {}

		self.force = False
		self.meta = ('', None)
		self.meta_mtime = None

	def __repr__(self):
		repr = '[ZooKeeper: %s] %s, %s' % (self.address, self.meta[0], str(self.meta[1]))

		for code, cache in self.arcus_cache_map.items():
			repr = '%s\n\n%s' % (repr, cache)

		return repr

	def set_force(self):
		self.force = True

	def zk_read(self, path):
		data, stat = self.zk.get(path)
		children = self.zk.get_children(path)
		return data, stat, children

	def zk_children(self, path, watch=None):
		if watch != None:
			return self.zk.get_children(path, watch = watch)
		else:
			return self.zk.get_children(path)

	def zk_children_if_exists(self, path, watch=None):
		if self.zk_exists(path) == False:
			return []

		return self.zk_children(path, watch)
	
	def zk_exists(self, path):
		if self.zk.exists(path) == None:
			return False

		return True

	def zk_create(self, path, value):
		try:
			self.zk.create(path, bytes(value, 'utf-8'))
		except NodeExistsError:
			if self.force == False:
				raise NodeExistsError
		
	def zk_delete(self, path):
		try:
			self.zk.delete(path)
		except NoNodeError:
			if self.force == False:
				raise NoNodeError
		
	def zk_delete_tree(self, path):
		try:
			self.zk.delete(path, recursive=True)
		except NoNodeError:
			if self.force == False:
				raise NoNodeError

	def zk_update(self, path, value):
		try:
			self.zk.set(path, bytes(value, 'utf-8'))
		except NoNodeError:
			if self.force == False:
				raise NoNodeError

	def get_arcus_cache_list(self):
		children = self.zk_children_if_exists('/arcus/cache_list/')
		children += self.zk_children_if_exists('/arcus_repl/cache_list/')

		return children

	def get_arcus_node_of_code(self, code, server):
		# repl case
		children = self.zk_children_if_exists('/arcus_repl/cache_list/' + code)
		children += self.zk_children_if_exists('/arcus/cache_list/' + code)
		ret = []
		for child in children:
			tmp = child.split('^', 2) # remove repl info
			if len(tmp) == 3:
				child = tmp[2]

			addr, name = child.split('-', 1)
			ip, port = addr.split(':', 1)

			if server != '' and (server != ip and server != name):
				continue # skip this

			node = arcus_node(ip, port)
			node.name = name
			ret.append(node)


		return ret

	def get_arcus_node_of_server(self, addr):
		ip = socket.gethostbyname(addr)

		children = self.zk_children_if_exists('/arcus_repl/cache_server_mapping/')
		children += self.zk_children_if_exists('/arcus/cache_server_mapping/')
		ret = []
		for child in children:
			l = len(ip)
			if child[:l] == ip:
				code = self.zk_children_if_exists('/arcus_repl/cache_server_mapping/' + child)
				if len(code) == 0:
					code = self.zk_children_if_exists('/arcus/cache_server_mapping/' + child)

				code = code[0]

				tmp = code.split('^') # remove repl info
				code = tmp[0]
				
				try:
					ip, port = child.split(':')
				except ValueError:
					print('No port defined in cache_server_mapping: %s' % child)
					continue

				node = arcus_node(ip, port)
				node.code = code
				ret.append(node)

		return ret

	def _get_arcus_node(self, child, results):
		code = self.zk_children_if_exists('/arcus_repl/cache_server_mapping/' + child)
		if len(code) == 0:
			code = self.zk_children_if_exists('/arcus/cache_server_mapping/' + child)

		if len(code) == 0:
			print('no childrens in cache_server_mapping error: %s' % child)
			print(code)
			return

		code = code[0]

		tmp = code.split('^') # remove repl info
		code = tmp[0]

		try:
			ip, port = child.split(':')
		except ValueError:
			print('No port defined in cache_server_mapping: %s' % child)
			ip = child
			port = '0'


		node = arcus_node(ip, port)
		node.code = code
		results.append(node)

	def get_arcus_node_all(self):
		children = self.zk_children_if_exists('/arcus_repl/cache_server_mapping/')
		children += self.zk_children_if_exists('/arcus/cache_server_mapping/')

		ret = []
		threads = []

		#print(children)
		for child in children:
			th = threading.Thread(target = self._get_arcus_node, args = (child, ret))
			th.start()
			threads.append(th)

		for th in threads:
			th.join()

		return ret

	def _get_arcus_meta(self, child, results):
		data, stat, children = self.zk_read('/arcus/meta/' + child)
		results[child] = [data.decode('utf-8'), stat]


	def get_arcus_meta_all(self):
		if self.zk.exists('/arcus/meta') == None:
			self.zk.create('/arcus/meta', b'arcus meta info')

		children = self.zk.get_children('/arcus/meta')
		print('# children')
		print(children)

		threads = []
		ret = {}

		#print(children)
		for child in children:
			th = threading.Thread(target = self._get_arcus_meta, args = (child, ret))
			th.start()
			threads.append(th)

		for th in threads:
			th.join()

		return ret


	def _match_code_and_nodes(self, code, cache, meta):
		#repl case
		children = self.zk_children_if_exists('/arcus_repl/cache_list/' + code)
		children += self.zk_children_if_exists('/arcus/cache_list/' + code)
		for child in children:
			tmp = child.split('^', 2) # remove repl info
			if len(tmp) == 3:
				child = tmp[2]

			addr, name = child.split('-')
			try:
				node = self.arcus_node_map[addr]
			except KeyError:
				print('%s of %s is not defined in cache_server_mapping' % (addr, code))
				ip, port = addr.split(':')
				node = arcus_node(ip, port)
				node.noport = True
		
			node.active = True
			cache.active_node.append(node)

		
		for node in cache.node:
			if node.active == False:
				cache.dead_node.append(node)

		if code in meta:
			cache.meta = meta[code]



	def load_all(self):
		codes = self.get_arcus_cache_list()
		for code in codes:
			cache = arcus_cache(self.address, code)
			self.arcus_cache_map[code] = cache

		print('# get_arcus_node_all()')
		nodes = self.get_arcus_node_all()
		print('# done')

		for node in nodes:
			self.arcus_node_map[node.ip + ":" + node.port] = node
			self.arcus_cache_map[node.code].node.append(node)

		# meta info 
		print('# get_arcus_meta_all()')
		meta = self.get_arcus_meta_all()
		print('# done')

		print('# match code & nodes')
		threads = []
		
		for code, cache in self.arcus_cache_map.items():
			th = threading.Thread(target = self._match_code_and_nodes, args = (code, cache, meta))
			th.start()
			threads.append(th)

		for th in threads:
			th.join()

		print('#done')

		if 'zookeeper' in meta:
			self.meta = meta['zookeeper']
			

	def _callback(self, event):
		child_list = self.zk.get_children(event.path)
		cloud = os.path.basename(event.path)
		cache = self.arcus_cache_map[cloud]

		event_list = { 'created':[], 'deleted':[] }
		current = {}
		print('##### active node')
		print(cache.active_node)

		children = []
		for child in child_list:
			addr = child.split('-')[0]
			children.append(addr)
		
		print('#### children')
		print(children)

		for node in cache.active_node:
			current[node.ip + ':' + node.port] = True

		print('##### current')
		print(current)

		for node in cache.active_node:
			addr = node.ip + ':' + node.port
			if addr not in children:
				event_list['deleted'].append(addr)
				cache.active_node.remove(node)


		for child in children:
			if child not in current:
				event_list['created'].append(child)
				ip, port = child.split(':')
				node = arcus_node(ip, port)
				cache.active_node.append(node)


		print('####### result')
		print(cache.active_node)

		self.callback(event, event_list)
		children = self.zk.get_children(event.path, watch = self._callback)
		

	def watch(self, callback):
		self.callback = callback
		for code, cache in self.arcus_cache_map.items():
			children = self.zk_children_if_exists('/arcus/cache_list/' + code, watch=self._callback)
			children += self.zk_children_if_exists('/arcus_repl/cache_list/' + code, watch=self._callback)

				

				

		

		
		




