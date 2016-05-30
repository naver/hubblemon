
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



import os, socket, sys, time, copy, datetime, threading
import data_loader

hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)

import arc_mon
import redis_mon
import common.settings
import common.core
import telnetlib, json
from graph.node import graph_pool


arc_preset = redis_mon.redis_view.redis_preset


def arc_view(path, title = ''):
	return common.core.loader(path, arc_preset, title)




#
# chart list
#
arc_cluster_map = {}
arc_cluster_list_map = {}
last_ts = 0

	


def _read_json(tn, cmd):
	timeout = 1
	tn.write(bytes(cmd + '\r\n', 'utf-8'))
	result = tn.read_until(bytes('\r\n', 'utf-8'), timeout)
	result = json.loads(result.decode('utf-8'))	
	return result

def _conf_master_load(addr, cluster_map, cluster_list_map):
	print('# conf master %s load' % addr)
	ip, port = addr.split(':')

	tn = telnetlib.Telnet(ip, port)
	js = _read_json(tn, 'cluster_ls')
	cluster_list = js['data']['list']
	#print(cluster_list)

	for cluster in cluster_list:
		pgs_str_list = []

		js = _read_json(tn, 'pgs_ls %s' % cluster)
		pgs_list = js['data']['list']
		#print(pgs_list)

		for pgs in pgs_list:
			js = _read_json(tn, 'pgs_info %s %s' % (cluster, pgs))
			ip = js['data']['pm_IP']
			try:
				hostname = socket.gethostbyaddr(ip)[0]
			except Exception as e:
				hostname = ip

			port = js['data']['backend_Port_Of_Redis']
			pgs_str_list.append('%s-%s/redis_%d' % (pgs, hostname, port))

		
		
		#print(ci.name, ci.pgs_list)
		cluster_map[cluster] = pgs_str_list
		cluster_list_map[cluster] = [addr, pgs_str_list]
		#print(cluster_map)
	
	
	


def init_plugin():
	global arc_cluster_map
	global arc_cluster_list_map
	global last_ts

	ts = time.time()
	if ts - last_ts < 600:
		return
	last_ts = ts

	print('#### cluster init ########')

	arc_cluster_map_tmp = {}
	arc_cluster_list_map_tmp = {}

	threads = []
	#for addr in ['gasan.arccluster.nhncorp.com:17288']:
	for addr in common.settings.arc_conf_masters:
		th = threading.Thread(target = _conf_master_load, args = (addr, arc_cluster_map_tmp, arc_cluster_list_map_tmp))
		th.start()
		threads.append(th)

	for th in threads:
		th.join()
		

	arc_cluster_map = arc_cluster_map_tmp
	arc_cluster_list_map = arc_cluster_list_map_tmp
	#print (arc_cluster_map)
	#print (arc_cluster_list_map)
	


def get_chart_data(param):
	#print(param)
	global arc_cluster_map


	type = 'arc_stat'
	if 'type' in param:
		type = param['type']

	if 'cluster' not in param or 'instance' not in param:
		return None

	cluster_name = param['cluster']
	instance_name = param['instance']

	if cluster_name not in arc_cluster_map and cluster_name != '[SUM]':
		return None

	if type == 'arc_stat':
		if instance_name == '[SUM]':
			loader_list = []
			for node in arc_cluster_map[cluster_name]:
				if node.startswith('['):
					continue # skip

				loader = common.core.loader(node, arc_preset, title=node)
				loader_list.append(loader)

			results = data_loader.loader_factory.sum_all(loader_list)
			
		elif instance_name == '[EACH]':
			loader_list = []
			for node in arc_cluster_map[cluster_name]:
				if node.startswith('['):
					continue # skip

				loader = common.core.loader(node, arc_preset, title=node)
				loader_list.append(loader)

			results = data_loader.loader_factory.merge(loader_list)

		else:
			for node in arc_cluster_map[cluster_name]:
				if node.startswith(instance_name):
					node = node.split('-')[1]
					results = common.core.loader(node, arc_preset, title=node)
					break

	return results


def get_chart_list(param):
	print(param)

	type = 'arc_stat'
	if 'type' in param:
		type = param['type']

	cluster = ''
	instance = ''

	if 'cluster' in param:
		cluster = param['cluster']

	if 'instance' in param:
		instance = param['instance']

	if type == 'arc_stat':
		if cluster == '':
			return (['cluster', 'instance'], arc_cluster_map)
		else:
			str_list = copy.copy(arc_cluster_map[cluster])
			str_list.insert(0, '[SUM]')
			str_list.insert(0, '[EACH]')
			return (['cluster', 'instance'], {cluster:str_list})


	return (['cluster', 'instance'], arc_cluster_map)


def get_graph_list(param):
	#print(param)
	ret = {}
	for cm in common.settings.arc_conf_masters:
		ret[cm] = True

	return (['cm'], ret)


def get_graph_data(param):
	#print(param)
	addr = param['cm']
	cm_map = {}
	cm_list_map = {}
	_conf_master_load(addr, cm_map, cm_list_map)

	# make graph data
	results = []
	graph_data = render_arc_graph(addr, cm_map)
	return graph_data


def render_arc_graph(addr, cm_map):
	ts_start = time.time()

	position = 20 # yaxis
	pool = graph_pool(position)

	node_cm = pool.get_node(addr)
	node_cm.weight = 300
	node_cm.color = '0000FF'

	for cluster, pgs in cm_map.items():
		node_cluster = pool.get_node(cluster)
		node_cluster.weight = 200
		node_cluster.color = '00FF00'
		node_cluster.link(node_cm)
		
	for cluster, pgs in cm_map.items():
		node_cluster = pool.get_node(cluster)

		for pg in pgs:
			pgid, addr = pg.split('-')
			host, port = addr.split('/')
					
			node_pg = pool.get_node(host)
			node_pg.weight = 100
			node_pg.color = '00FFFF'
			node_pg.link(node_cluster, port, '00FF00')

	result = pool.render()

	ts_end = time.time()
	print('## %s elapsed: %f' % (addr, ts_end - ts_start))
	return result


def get_addon_page(param):
	print(param)
	global arc_cluster_list_map

	cluster_list = ''
	color = '#EEEEFF'

	idx = 1 
	for cluster_name, v in sorted(arc_cluster_list_map.items()):
		cm = v[0]
		node_str_list = v[1]
		
		if color == '#EEEEFF':
			color = '#EEFFEE'
		else:
			color = '#EEEEFF'

		tmp ="""<div style="float:left; width:3%%;">%d</div>
			<div style="float:left; width:12%%;"><a href="/chart?type=arc_stat&cluster=%s&instance=[EACH]">%s</a></div>
			<div style="float:left; width:25%%;"><a href="/graph?type=arc_graph&cm=%s">%s</a></div>
			""" % (idx, cluster_name, cluster_name, cm, cm)
		idx += 1

		tmp_instance = ''
		for node in v[1]:
			tmp_instance +="""<div><a href="/chart?type=arc_stat&cluster=%s&instance=%s">%s</a></div>""" % (cluster_name, node, node)


		tmp_instance += "<div><b>total instances: %d</b></div>" % len(node_str_list)
		

		tmp += '<div style="float:left; width:20%%;">%s</div>' % (tmp_instance)

		cluster_list += '<div style="width:100%%; background:%s;">%s</div><div style="clear:both;"></div><div>&nbsp</div>' % (color, tmp)
		
		
	return cluster_list

