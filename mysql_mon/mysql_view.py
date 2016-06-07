
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

mysql_preset = [['Bytes_received', 'Bytes_sent'],
		['Queries', 'Slow_queries'], 
		['Com_select', 'Com_update', 'Com_delete', 'Com_replace'],
		['Com_insert', 'Com_insert_select'],
		['Com_create_table', 'Com_drop_table'],
		['Com_commit', 'Com_rollback', 'Com_rollback_to_SP'],
		['Com_stmt_close', 'Com_stmt_execute', 'Com_stmt_fetch'],
		['Com_stmt_prepare', 'Com_stmt_reprepare', 'Com_stmt_reset'],
		['Threads_created', 'Threads_running', 'Threads_connected', 'Threads_cached', 'Connections'],
		['idb_bpool_P_total', 'idb_bpool_P_data', 'idb_bpool_P_free'],
		['idb_bpool_P_dirty', 'idb_bpool_P_flushed', 'idb_bpool_P_misc'],
		['idb_bpool_ra', 'idb_bpool_ra_evict'],
		['idb_data_read', 'idb_data_reads', 'idb_data_writes', 'idb_data_written'],
		['idb_P_created', 'idb_P_read', 'idb_P_written'],
		['idb_data_read', 'idb_data_reads', 'idb_data_writes', 'idb_data_written'],
		['idb_P_created', 'idb_P_read', 'idb_P_written'],
		['idb_log_waits', 'idb_log_wr_req', 'idb_log_writes'],
		['idb_rows_inserted', 'idb_rows_deleted', 'idb_rows_read', 'idb_rows_updated'],
		['idb_row_lock_time', 'idb_row_lck_avg', 'idb_row_lck_max']]



def mysql_view(path, title = ''):
	return common.core.loader(path, mysql_preset, title)



#
# chart list
#
mysql_cloud_map = {}
last_ts = 0

def init_plugin():
	print('#### mysql init ########')
	ret = get_chart_list({})
	print(ret)


def get_chart_data(param):
	#print(param)
	global mysql_cloud_map


	type = 'mysql_stat'
	if 'type' in param:
		type = param['type']

	if 'instance' not in param or 'server' not in param:
		return None

	instance_name = param['instance']
	server_name = param['server']

	if type == 'mysql_stat':
		for node in mysql_cloud_map[server_name]:
			if node.startswith(instance_name):
				results = common.core.loader(server_name + '/' + node, mysql_preset, title=node)
				break

	return results



def get_chart_list(param):
	#print(param)
	global mysql_cloud_map
	global last_ts

	ts = time.time()
	if ts - last_ts >= 300:
		mysql_cloud_map_tmp = {}
		client_list = common.core.get_client_list()
		for client in client_list:
			instance_list = common.core.get_data_list_of_client(client, 'mysql_')
			if len(instance_list) > 0:
				mysql_cloud_map_tmp[client] = instance_list	

		mysql_cloud_map = mysql_cloud_map_tmp


	last_ts = ts

	if 'type' in param:
		type = param['type']

	return (['server', 'instance'], mysql_cloud_map)
	

