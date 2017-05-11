
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


import os, sys, time, threading
import datetime

import common.settings
import binascii, socket
import data_loader.basic_loader
import data_loader.loader_factory


mod_cache = {}
mod_query_cache = {}

#
# default loader settings
#

def loader(entity_table, filter = None, title = ''):
	results = []

	info = _get_listener_info(entity_table)

	lisnter = info[0]
	storage_manager = info[1]

	handle = storage_manager.get_handle(entity_table)

	try:
		return data_loader.basic_loader.basic_loader(handle, filter, title)
	except:
		return data_loader.basic_loader.basic_loader(None, [])

	
#
# data, system handling
#
def _get_listener_info(entity_table):
	#print(entity_table)
	entity = entity_table.split('/')[0]
	#ip = socket.gethostbyname(entity)

	ret = binascii.crc32(bytes(entity, 'utf-8'))
	n = len(common.settings.listener_list)
	idx = ret % n

	return common.settings.listener_list[idx]
	



# local or remote
def get_entity_list():
	entity_map = {}

	for item in common.settings.listener_list:
		storage_manager = item[1]
		entities = storage_manager.get_entity_list()
		for entity in entities:
			entity_map[entity] = 1

	return list(entity_map.keys())


# local or remote
def get_table_list_of_entity(entity, prefix):
	info = _get_listener_info(entity)
	data_list = []

	storage_manager = info[1]
	data_list += storage_manager.get_table_list_of_entity(entity, prefix)

	return data_list
	

# local or remote
def get_all_table_list(prefix):
	table_list = []

	for item in common.settings.listener_list:
		storage_manager = item[1]
		table_list += storage_manager.get_all_table_list(prefix)

	return table_list


#
# plugins
#
def get_chart_list(param):
	if 'type' not in param:
		return ([], {})

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	return mod_cache[type].get_chart_list(param)


def get_chart_data(param):
	if 'type' not in param:
		return None

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	return mod_cache[type].get_chart_data(param)


def get_graph_list(param):
	if 'type' not in param:
		return ([], {})

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	return mod_cache[type].get_graph_list(param)


def get_graph_data(param):
	if 'type' not in param:
		return None

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	return mod_cache[type].get_graph_data(param)

def auth_fields(param):
	if 'type' not in param:
		return None

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	if type not in mod_query_cache:
		pkg = __import__('%s_mon.%s_query' % (type, type))
		mod = getattr(pkg, '%s_query' % type)
		mod_query_cache[type] = mod

	return mod_query_cache[type].auth_fields(param)


def query(param, ip):
	if 'type' not in param:
		return None

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	if type not in mod_query_cache:
		pkg = __import__('%s_mon.%s_query' % (type, type))
		mod = getattr(pkg, '%s_query' % type)
		mod_query_cache[type] = mod

	return mod_query_cache[type].query(param, ip)


def get_addon_page(param):
	if 'type' not in param:
		return ''

	type = param['type']
	type = type.split('_')[0]

	if type not in mod_cache:
		pkg = __import__('%s_mon.%s_view' % (type, type))
		mod = getattr(pkg, '%s_view' % type)
		mod.init_plugin()
		mod_cache[type] = mod

	return mod_cache[type].get_addon_page(param)




#
# functions that used for expr
#

import psutil_mon.psutil_view
import arcus_mon.arcus_view
import redis_mon.redis_view
import fnmatch


def system_view(entity, item = 'brief', type='serial'):
	if isinstance(entity, str):
		if '*' in entity or '?' in entity: # wild card
			entity_list = []
			all_entities = get_entity_list()

			for c in all_entities:
				if fnmatch.fnmatch(c, entity):
					entity_list.append(c)
		else:
			entity_list = [ entity ]
	else: # list, tuple
		entity_list = entity

	ret = []
	for entity in entity_list:
		ret.append(psutil_mon.psutil_view.system_view(entity, item))

	if type == 'merge':
		return data_loader.loader_factory.merge_loader(ret)

	return data_loader.loader_factory.serial_loader(ret)

def arcus_view(instance): # entity/arcus_port
	if isinstance(instance, str):
		instances = [ instance ]
	else: # list, tuple
		instances = instance

	ret = []
	for instance in instances:
		ret.append(arcus_mon.arcus_view.arcus_view(instance))

	return data_loader.loader_factory.serial_loader(ret)


def arcus_instance_list(name):
	if isinstance(name, str):
		names = [ name ]
	else: # list, tuple
		names = name

	node_list = []
	for name in names:
		node_list += arcus_mon.arcus_view.arcus_cloud_map[name]

	return node_list



def arcus_cloud_list(zk = None):
	if zk == None:
		return list(arcus_mon.arcus_view.arcus_cloud_map.keys())
		
	if zk in arcus_mon.arcus_view.arcus_zk_map:
		return arcus_mon.arcus_view.arcus_zk_map[zk]

	return None





def for_each(name, filter, fun, start_ts = int(time.time())-60*30, end_ts = int(time.time())):

	# change to timestamp
	if isinstance(start_ts, str):
		start_date = datetime.datetime.strptime(start_ts, '%Y-%m-%d %H:%M')
		start_ts = int(start_date.timestamp())
	elif isinstance(start_ts, datetime.datetime):
		start_ts = int(start_ts.timestamp())
		
	if isinstance(end_ts, str):
		end_date = datetime.datetime.strptime(end_ts, '%Y-%m-%d %H:%M')
		end_ts = int(end_date.timestamp())
	elif isinstance(end_ts, datetime.datetime):
		send_ts = int(end_ts.timestamp())



	if isinstance(name, str):
		names = [ name ]
	else: # list, tuple
		names = name

	selected = []
	for name in names:
		ldr = loader(name)
		ldr.parse(start_ts, end_ts)
			
		if filter(ldr):
			selected.append(name)

	print('# selected: ' + str(selected))
	result = []
	for i in selected:
		ret = fun(i)
		if isinstance(ret, list):
			result += ret
		else:
			result.append(ret)

	#print(result)
	return result




	

#
# functions that used for query eval
# 

def return_as_string(result, p = {}):
	result = str(result)

	result = result.replace('\n', '<br>')
	result = result.replace(' ', '&nbsp')
	p['result'] = result
	return p['result']
	

def return_as_textarea(result, p = {}):
	p['result'] = '<textarea>%s</textarea>' % result
	return p['result']

def return_as_table(result, p = {}):
	tr = ''

	# cursor meta info 
	if hasattr(result, 'description'):
		td = ''
		for d in result.description:
			td += '<td>%s</td>' % d[0]
		tr += '<tr>%s</tr>' % td

	# values
	for row in result:
		td = ''
		for item in row:
			td += '<td>%s</td>' % item
		tr += '<tr>%s</tr>' % td

	p['result'] = '<table border="1">%s</table>' % tr
	return p['result']
			
		
	
	



# result zookeeper.load_all()
from arcus_mon.arcus_driver.arcus_util import zookeeper

def get_arcus_zk_load_all(addr):
	zoo = zookeeper(addr)
	zoo.load_all()
	return zoo

def get_arcus_zk_node_cloud_map(addr):
	arcus_node_cloud_map = {}

	zoo = zookeeper(addr)
	nodes = zoo.get_arcus_node_all()
	for node in nodes:
		arcus_node_cloud_map[node.ip + ":" + node.port] = node.code

	return arcus_node_cloud_map
	

	
	

