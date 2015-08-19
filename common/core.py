import os, sys, time, threading
import datetime

import common.settings
import binascii, socket
import data_loader.basic_loader


#
# default loader settings
#
default_loader = data_loader.basic_loader.rrd


#
# data, system handling
#
def _get_data_path(file):
	#print(file)
	name = file.split('/')[0]
	#ip = socket.gethostbyname(name)

	ret = binascii.crc32(bytes(name, 'utf-8'))
	n = len(common.settings.listener_list)
	idx = ret % n

	data_path = common.settings.listener_list[idx][1]
	return os.path.join(data_path, file)


def _get_system_pathes():
	result = []
	for item in common.settings.listener_list:
		result.append(item[1])

	return result


def get_data_list(path, prefix):
	path = _get_data_path(path)
	instance_list = []

	for file in os.listdir(path):
		if file.startswith(prefix):
			instance_list.append(file)

	return instance_list
	

def get_data_handle(path):
	path = _get_data_path(path)
	fd = open(path)
	fd.path = path
	return fd


def get_system_list(postfix=None):
	system_list = []

	pathes = _get_system_pathes()
	for path in pathes:
		for dir in os.listdir(path):
			dir_path = os.path.join(path, dir)

			if os.path.isdir(dir_path):
				if postfix:
					system_list.append(dir + '/' + postfix)
				else:
					system_list.append(dir)

	return system_list



#
# plugins
#
def get_chart_list(param):
	if 'type' not in param:
		return ([], {})

	type = param['type']
	type = type.split('_')[0]

	pkg = __import__('%s_mon.%s_view' % (type, type))
	mod = getattr(pkg, '%s_view' % type)
	mod.init_plugin()
	return mod.get_chart_list(param)


def get_chart_data(param):
	if 'type' not in param:
		return None

	type = param['type']
	type = type.split('_')[0]

	pkg = __import__('%s_mon.%s_view' % (type, type))
	mod = getattr(pkg, '%s_view' % type)
	mod.init_plugin()
	return mod.get_chart_data(param)


def get_graph_list(param):
	if 'type' not in param:
		return ([], {})

	type = param['type']
	type = type.split('_')[0]

	pkg = __import__('%s_mon.%s_view' % (type, type))
	mod = getattr(pkg, '%s_view' % type)
	mod.init_plugin()
	return mod.get_graph_list(param)

def get_graph_data(param):
	if 'type' not in param:
		return None

	type = param['type']
	type = type.split('_')[0]

	pkg = __import__('%s_mon.%s_view' % (type, type))
	mod = getattr(pkg, '%s_view' % type)
	mod.init_plugin()
	return mod.get_graph_data(param)

def auth_fields(param):
	if 'type' not in param:
		return None

	type = param['type']
	type = type.split('_')[0]

	pkg = __import__('%s_mon.%s_view' % (type, type))
	mod = getattr(pkg, '%s_view' % type)
	mod.init_plugin()

	pkg = __import__('%s_mon.%s_query' % (type, type))
	mod = getattr(pkg, '%s_query' % type)
	return mod.auth_fields(param)


def query(param, ip):
	if 'type' not in param:
		return None

	type = param['type']
	type = type.split('_')[0]

	pkg = __import__('%s_mon.%s_view' % (type, type))
	mod = getattr(pkg, '%s_view' % type)
	mod.init_plugin()

	pkg = __import__('%s_mon.%s_query' % (type, type))
	mod = getattr(pkg, '%s_query' % type)
	return mod.query(param, ip)


def get_addon_page(param):
	if 'type' not in param:
		return ''

	type = param['type']
	type = type.split('_')[0]

	pkg = __import__('%s_mon.%s_view' % (type, type))
	mod = getattr(pkg, '%s_view' % type)
	mod.init_plugin()
	return mod.get_addon_page(param)




#
# functions that used for expr
#

import psutil_mon.psutil_view
import arcus_mon.arcus_view
import redis_mon.redis_view


def system_view(file, item):
	if isinstance(file, str):
		files = [ file ]
	else: # list, tuple
		files = file

	ret = []
	for file in files:
		path = _get_data_path(file)
		ret += psutil_mon.psutil_view.system_view(path, item)

	return ret


def arcus_view(file):
	if isinstance(file, str):
		files = [ file ]
	else: # list, tuple
		files = file

	ret = []
	for file in files:
		path = _get_data_path(file)
		ret.append(arcus_mon.arcus_view.arcus_view(path))

	return ret


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
		path = _get_data_path(name)
		loader = default_loader(path)
		loader.parse(start_ts, end_ts)
			
		if filter(loader):
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

arcus_zk_cache = {}

def get_zk_load_all(addr):
	global arcus_zk_cache

	if addr not in arcus_zk_cache:
		zoo = zookeeper(addr)
		zoo.load_all()
		arcus_zk_cache[addr] = [zoo, time.time()]

	# always in
	zoo, last_ts = arcus_zk_cache[addr][0], arcus_zk_cache[addr][1]
	ts = time.time()

	if ts - arcus_zk_cache[addr][1] > 60*30: # refresh every 30mins
		arcus_zk_cache[addr][1] = ts
		threading.Thread(target=zk_load_background, args=(addr,))

	return zoo

def zk_load_background(addr):
	global arcus_zk_cache

	zoo = zookeeper(addr)
	zoo.load_all()
	arcus_zk_cache[addr] = (zoo, time.time())
	
	

