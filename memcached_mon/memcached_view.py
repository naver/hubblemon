
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

import os, socket, sys, time
import data_loader
from datetime import datetime


hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)

import common.core

memcached_preset = [['bytes', 'total_malloced', 'limit_maxbytes'], (lambda x: x['get_hits'] / x['cmd_get'] * 100, 'hit_ratio'), ['rusage_user', 'rusage_system'], 'curr_items', 'evictions', 'reclaimed', ['bytes_read', 'bytes_written'], 'curr_connections', ['cmd_get', 'cmd_set'], 'cmd_flush', 'cmd_touch', 'auth_cmds', 'auth_errors' ]


def memcached_view(path, title = ''):
	return common.core.loader(path, memcached_preset, title)

memcached_prefix_preset = [ 'cmd_get', 'cmd_hit', 'cmd_set', 'cmd_del' ]





#
# chart list
#
memcached_cloud_map = {}
last_ts = 0

def init_plugin():
	print('#### memcached init ########')
	ret = get_chart_list({})
	print(ret)

	


def get_chart_data(param):
	#print(param)
	global memcached_cloud_map


	type = 'memcached_stat'
	if 'type' in param:
		type = param['type']

	if 'instance' not in param or 'server' not in param:
		return None

	instance_name = param['instance']
	server_name = param['server']

	if type == 'memcached_stat':
		for node in memcached_cloud_map[server_name]:
			if node.startswith(instance_name):
				results = common.core.loader(server_name + '/' + node, memcached_preset, title=node)
				break

	return results



def get_chart_list(param):
	#print(param)
	global memcached_cloud_map
	global last_ts


	ts = time.time()
	if ts - last_ts >= 300:
		memcached_cloud_map_tmp = {}
		client_list = common.core.get_client_list()
		for client in client_list:
			instance_list = common.core.get_data_list_of_client(client, 'memcached_')
			if len(instance_list) > 0:

				new_list = []
				for instance in instance_list:
					if not instance.startswith('memcached_prefix_'): # skip prefix
						new_list.append(instance)

					memcached_cloud_map_tmp[client] = new_list

		memcached_cloud_map = memcached_cloud_map_tmp

	last_ts = ts

	if 'type' in param:
		type = param['type']

	return (['server', 'instance'], memcached_cloud_map)
	


