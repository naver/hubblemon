
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

jstat_preset = [['Survivor_0', 'Survivor_1', 'Eden', 'Old', 'Permanent'], 'YGC', 'YGCT', 'FGC', 'FGCT', 'GCT', ['YGC', 'FGC', 'GCT'], ['YGCT', 'FGCT']]

def jstat_view(path, title = ''):
	return common.core.loader(path, jstat_preset, title)


#
# chart list
#
jstat_cloud_map = {}
last_ts = 0

def init_plugin():
	print('#### jstat init ########')
	ret = get_chart_list({})
	print(ret)
		
	


def get_chart_data(param):
	#print(param)
	global jstat_cloud_map


	type = 'jstat_stat'
	if 'type' in param:
		type = param['type']

	if 'instance' not in param or 'server' not in param:
		return None

	instance_name = param['instance']
	server_name = param['server']

	if type == 'jstat_stat':
		for node in jstat_cloud_map[server_name]:
			if node.startswith(instance_name):
				results = common.core.loader(server_name + '/' + node, jstat_preset, title=node)
				break

	return results



def get_chart_list(param):
	#print(param)
	global jstat_cloud_map
	global last_ts

	# refresh every 5 min
	ts = time.time()
	if ts - last_ts >= 300:
		jstat_cloud_map_tmp = {}
		client_list = common.core.get_client_list()
		for client in client_list:
			instance_list = common.core.get_data_list_of_client(client, 'jstat_')
			if len(instance_list) > 0:
				jstat_cloud_map_tmp[client] = instance_list	

		jstat_cloud_map = jstat_cloud_map_tmp

	last_ts = ts

	if 'type' in param:
		type = param['type']

	return (['server', 'instance'], jstat_cloud_map)
	


