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

import socket, fnmatch, pickle, sys, os, threading

import arcus_mon.settings
import arcus_mon.arcus_driver.arcus_util
from arcus_mon.arcus_driver.arcus_util import zookeeper


hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)
import common.settings
import common.core

class arcus_alarm:
	def __init__(self):
		self.name = 'arcus'
		self.sec_interval = 5 # 5 sec interval
		self.node_cloud_map = {}
		self.node_cloud_map_init()

	def _node_cloud_map_init(self, addr):
		zoo = zookeeper(addr)
		nodes = zoo.get_arcus_node_all()
		for node in nodes:
			self.node_cloud_map[node.ip + ":" + node.port] = node.code

	def node_cloud_map_init(self):
		print('# cloud map init')
		threads = []
		for addr in common.settings.arcus_zk_addrs:
			th = threading.Thread(target = self._node_cloud_map_init, args = (addr,))
			th.start()
			threads.append(th)

		for th in threads:
			th.join()
		print('# cloud map init done')
	
	def get_cloud_of_node(self, name, port):
		try:
			ip = socket.gethostbyname(name)
		except Exception as e:
			print(e)
			print('# exception: %s' % name)
			return None

		key = ip + ':' + port
		if key not in self.node_cloud_map:
			# retry with ip:0 # implicit define
			key = ip + ':0'
			if key not in self.node_cloud_map:
				return None

		return self.node_cloud_map[key]
		

	def select_cloud_conf(self, cloud, map):
		ret = {}
		if 'default' in map:
			ret = map['default'].copy()

		# exact
		if cloud in map:
			# overwrite
			for k, v in map[cloud].items():
				ret[k] = v
		else:
			# wild card match
			for key, value in map.items():
				# overwrite if match like linegame-*
				if fnmatch.fnmatch(cloud, key):
					for k, v in value.items():
						ret[k] = v

		return ret
	
	def get_conf(self, client, instance): # client: machine name, instance: arcus port
		if not instance.isnumeric(): # TODO: ignore prefix
			return (None, None, None)
			
		cloud = self.get_cloud_of_node(client, instance) 

		if cloud == None:
			print('## None type of node cloud mapping %s, %s' % (client, instance))
			return (None, None, None)

		# select exact conf
		abs_conf = self.select_cloud_conf(cloud, arcus_mon.settings.alarm_conf_absolute)
		lambda_conf = self.select_cloud_conf(cloud, arcus_mon.settings.alarm_conf_lambda)
	
		instance_id = '%s:%s-%s' % (cloud, client, instance)
		return (instance_id, abs_conf, lambda_conf)


