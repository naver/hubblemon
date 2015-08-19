
import socket, fnmatch, pickle, sys, os

import arcus_mon.settings
import arcus_mon.arcus_driver.arcus_util


hubblemon_path = os.path.abspath('..')
sys.path.append(hubblemon_path)
import common.settings
import common.core

class arcus_alarm:
	def __init__(self):
		self.name = 'arcus'
		self.sec_interval = 5 # 5 sec interval
		self.node_cloud_map = {}
		self.node_cloud_map_init()

	def node_cloud_map_init(self):
		try:
			print('## load node cloud map from file')
			nc_file = open('node_cloud_map.dat', 'rb')
			self.node_cloud_map = pickle.load(nc_file)
			nc_file.close()
			#print(self.node_cloud_map)
			return 

		except Exception:
			print('## load node cloud map from zookeeper')
		
				
		for addr in common.settings.arcus_zk_addrs:
			zoo = common.core.get_zk_load_all(addr)
			self.node_cloud_map.update(zoo.arcus_node_map)

		nc_file = open('node_cloud_map.dat', 'wb')
		pickle.dump(self.node_cloud_map, nc_file)
		nc_file.close()
		

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

		return self.node_cloud_map[key].code
		

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


