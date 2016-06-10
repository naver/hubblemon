
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

cubrid_preset = [['N_Q_selects', 'N_Q_inserts', 'N_Q_deletes', 'N_Q_updates'], ['N_Q_sscans', 'N_Q_iscans', 'N_Q_lscans'], 'buffer_hit_ratio', 'Time_ha_rep_delay', 'N_net_req', ['N_DP_fetches', 'N_DP_dirties', 'N_DP_ioreads', 'N_DP_iowrites', 'N_DP_victims', 'N_DP_iow_for_R'], ['N_LP_ioreads', 'N_LP_iowrites'], ['N_log_append_rec', 'N_log_archives', 'N_log_wals'], ['N_log_start_CP', 'N_log_end_CP'], ['N_tran_commits', 'N_tran_rollbacks', 'N_tran_savepoints'], ['N_tran_start_topops', 'N_tran_end_topops'], ['N_file_creates', 'N_file_removes', 'N_file_ioreads', 'N_file_iowrites', 'N_file_iosynches'], ['N_btree_inserts', 'N_btree_deletes', 'N_btree_updates', 'N_btree_covered', 'N_btree_noncov', 'N_btree_MR_opt'], ['N_page_locks_acq', 'N_page_locks_conv', 'N_page_locks_rereq', 'N_page_locks_waits'], ['N_obj_locks_acq', 'N_obj_locks_conv', 'N_obj_locks_rereq', 'N_obj_locks_waits'], ['N_prior_lsa_size', 'N_prior_lsa_maxed', 'N_prior_lsa_rem'], ['N_ad_flush_P', 'N_ad_flush_log_P', 'N_ad_flush_max_P']]


def cubrid_view(path, title = ''):
	return common.core.loader(path, cubrid_preset, title)



#
# chart list
#
cubrid_cloud_map = {}
last_ts = 0

def init_plugin():
	print('#### cubrid init ########')
	ret = get_chart_list({})
	print(ret)
	
	


def get_chart_data(param):
	#print(param)
	global cubrid_cloud_map


	type = 'cubrid_stat'
	if 'type' in param:
		type = param['type']

	if 'instance' not in param or 'server' not in param:
		return None

	instance_name = param['instance']
	server_name = param['server']

	if type == 'cubrid_stat':
		for node in cubrid_cloud_map[server_name]:
			if node.startswith(instance_name):
				results = common.core.loader(server_name + '/' + node, cubrid_preset, title=node)
				break

	return results



def get_chart_list(param):
	#print(param)
	global cubrid_cloud_map
	global last_ts

	ts = time.time()
	if ts - last_ts >= 300:
		cubrid_cloud_map_tmp = {}
		client_list = common.core.get_client_list()
		for client in client_list:
			instance_list = common.core.get_data_list_of_client(client, 'cubrid_')
			if len(instance_list) > 0:
				cubrid_cloud_map_tmp[client] = instance_list	

		cubrid_cloud_map = cubrid_cloud_map_tmp


	last_ts = ts


		

	if 'type' in param:
		type = param['type']

	return (['server', 'instance'], cubrid_cloud_map)
	


