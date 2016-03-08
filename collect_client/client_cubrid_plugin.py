
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


import socket
import telnetlib
import subprocess
import shlex

class cubrid_stat:
	def __init__(self):
		self.name = 'cubrid'
		self.type = 'rrd'
		self.dblist = []

		self.proc = {}

		self.collect_key_init()
		self.create_key_init()
		self.flag_auto_register = False

	def __repr__(self):
		return '[%s-(%s,%s)]' % (self.dblist.__repr__(), self.name, self.type)

	def auto_register(self):
		self.flag_auto_register = True

		proc1 = subprocess.Popen(shlex.split('ps -ef'), stdout=subprocess.PIPE)
		proc2 = subprocess.Popen(shlex.split('grep cub_server'), stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		proc1.stdout.close()
		out, err = proc2.communicate()
		out = out.decode('utf-8')
		lines = out.split('\n')

		tmp_dblist = []
		for line in lines:
			dbname = None
			lst = line.split()

			flag = False
			for a in lst:
				if a == 'grep':
					flag = False
					break

				if a == 'cub_server':
					flag = True
					continue

				if flag == True:
					dbname = a
					break

			if dbname is not None:
				tmp_dblist.append(dbname)
 
		tmp_dblist.sort()

		if self.dblist != tmp_dblist:
			print('## auto register cubrid')
			print(tmp_dblist)
			self.dblist = tmp_dblist
			return True

		return False

	def push_dbname(self, dbname):
		self.dblist.append(dbname)


	def collect_init(self, dbname):
		if dbname not in self.proc:
			self.proc[dbname] = subprocess.Popen(shlex.split('cubrid statdump -i 5 -c %s' % dbname), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	def collect(self):
		all_stats = {}

		if self.flag_auto_register == True:
			if self.auto_register() == True:
				return None # for create new file

		for dbname in self.dblist:
			stat = {}

			self.collect_init(dbname)
			proc = self.proc[dbname]

			while True:
				line = proc.stdout.readline()
				line = line.decode('utf-8')
				if line.strip() == '*** SERVER EXECUTION STATISTICS ***':
					break

				if '=' not in line:
					continue

				key, value = line.split('=')
				key = key.strip()
				value = value.strip()

				if key not in self.collect_key:	 # don't send this key
					continue

				alias_key = self.collect_key[key]
				value = int(float(value))

				stat[alias_key] = value # real name in rrd file

				for k, v in self.collect_key.items():
					if v not in stat:
						stat[v] = 0
					
			all_stats['cubrid_%s' % dbname] = stat

		return all_stats

		

	def create(self):
		all_map = {}

		for dbname in self.dblist:
			all_map['cubrid_%s' % dbname] = self.create_key_list # stats per port

		all_map['RRA'] = self.rra_list
		return all_map


	def create_key_init(self):
		self.collect_key_init()

		self.create_key_list=[ (self.collect_key['Num_file_creates'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_file_removes'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_file_ioreads'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_file_iowrites'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_file_iosynches'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_data_page_fetches'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_data_page_dirties'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_data_page_ioreads'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_data_page_iowrites'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_data_page_victims'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_data_page_iowrites_for_replacement'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_log_page_ioreads'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_log_page_iowrites'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_log_append_records'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_log_archives'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_log_start_checkpoints'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_log_end_checkpoints'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_log_wals'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_page_locks_acquired'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_object_locks_acquired'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_page_locks_converted'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_object_locks_converted'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_page_locks_re-requested'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_object_locks_re-requested'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_page_locks_waits'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_object_locks_waits'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_tran_commits'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_tran_rollbacks'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_tran_savepoints'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_tran_start_topops'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_tran_end_topops'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_tran_interrupts'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_btree_inserts'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_btree_deletes'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_btree_updates'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_btree_covered'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_btree_noncovered'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_btree_resumes'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_btree_multirange_optimization'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_query_selects'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_query_inserts'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_query_deletes'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_query_updates'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_query_sscans'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_query_iscans'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_query_lscans'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_query_setscans'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_query_methscans'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_query_nljoins'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_query_mjoins'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_query_objfetches'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_query_holdable_cursors'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_sort_io_pages'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_sort_data_pages'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_network_requests'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_adaptive_flush_pages'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_adaptive_flush_log_pages'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_adaptive_flush_max_pages'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_prior_lsa_list_size'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_prior_lsa_list_maxed'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_prior_lsa_list_removed'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_heap_stats_bestspace_entries'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Num_heap_stats_bestspace_maxed'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Time_ha_replication_delay'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Data_page_buffer_hit_ratio'], 'GAUGE', 60, '0', 'U')]


		# used for RRA
		self.rra_list =	[  ('MAX', 0.5, 5/5, (3600/5)*24), 	# 5sec  (to 1day)
				   ('MAX', 0.5, 60/5, (3600/60)*24*7), 	# 30sec (to 7day)
				   ('MAX', 0.5, 3600/5, 24*31),		# 1hour (to 1month)
				   ('MAX', 0.5, 3600*3/5, (24/3)*366*3) ]	# 3hour (to 3year)



	def collect_key_init(self):
		self.collect_key = {}

		self.collect_key['Num_file_creates'] = 'N_file_creates'
		self.collect_key['Num_file_removes'] = 'N_file_removes'
		self.collect_key['Num_file_ioreads'] = 'N_file_ioreads'
		self.collect_key['Num_file_iowrites'] = 'N_file_iowrites'
		self.collect_key['Num_file_iosynches'] = 'N_file_iosynches'
		self.collect_key['Num_data_page_fetches'] = 'N_DP_fetches'
		self.collect_key['Num_data_page_dirties'] = 'N_DP_dirties'
		self.collect_key['Num_data_page_ioreads'] = 'N_DP_ioreads'
		self.collect_key['Num_data_page_iowrites'] = 'N_DP_iowrites'
		self.collect_key['Num_data_page_victims'] = 'N_DP_victims'
		self.collect_key['Num_data_page_iowrites_for_replacement'] = 'N_DP_iow_for_R'
		self.collect_key['Num_log_page_ioreads'] = 'N_LP_ioreads'
		self.collect_key['Num_log_page_iowrites'] = 'N_LP_iowrites'
		self.collect_key['Num_log_append_records'] = 'N_log_append_rec'
		self.collect_key['Num_log_archives'] = 'N_log_archives'
		self.collect_key['Num_log_start_checkpoints'] = 'N_log_start_CP'
		self.collect_key['Num_log_end_checkpoints'] = 'N_log_end_CP'
		self.collect_key['Num_log_wals'] = 'N_log_wals'
		self.collect_key['Num_page_locks_acquired'] = 'N_page_locks_acq'
		self.collect_key['Num_object_locks_acquired'] = 'N_obj_locks_acq'
		self.collect_key['Num_page_locks_converted'] = 'N_page_locks_conv'
		self.collect_key['Num_object_locks_converted'] = 'N_obj_locks_conv'
		self.collect_key['Num_page_locks_re-requested'] = 'N_page_locks_rereq'
		self.collect_key['Num_object_locks_re-requested'] = 'N_obj_locks_rereq'
		self.collect_key['Num_page_locks_waits'] = 'N_page_locks_waits'
		self.collect_key['Num_object_locks_waits'] = 'N_obj_locks_waits'
		self.collect_key['Num_tran_commits'] = 'N_tran_commits'
		self.collect_key['Num_tran_rollbacks'] = 'N_tran_rollbacks'
		self.collect_key['Num_tran_savepoints'] = 'N_tran_savepoints'
		self.collect_key['Num_tran_start_topops'] = 'N_tran_start_topops'
		self.collect_key['Num_tran_end_topops'] = 'N_tran_end_topops'
		self.collect_key['Num_tran_interrupts'] = 'N_tran_interrupts'
		self.collect_key['Num_btree_inserts'] = 'N_btree_inserts'
		self.collect_key['Num_btree_deletes'] = 'N_btree_deletes'
		self.collect_key['Num_btree_updates'] = 'N_btree_updates'
		self.collect_key['Num_btree_covered'] = 'N_btree_covered'
		self.collect_key['Num_btree_noncovered'] = 'N_btree_noncov'
		self.collect_key['Num_btree_resumes'] = 'N_btree_resumes'
		self.collect_key['Num_btree_multirange_optimization'] = 'N_btree_MR_opt'
		self.collect_key['Num_query_selects'] = 'N_Q_selects'
		self.collect_key['Num_query_inserts'] = 'N_Q_inserts'
		self.collect_key['Num_query_deletes'] = 'N_Q_deletes'
		self.collect_key['Num_query_updates'] = 'N_Q_updates'
		self.collect_key['Num_query_sscans'] = 'N_Q_sscans'
		self.collect_key['Num_query_iscans'] = 'N_Q_iscans'
		self.collect_key['Num_query_lscans'] = 'N_Q_lscans'
		self.collect_key['Num_query_setscans'] = 'N_Q_setscans'
		self.collect_key['Num_query_methscans'] = 'N_Q_methscans'
		self.collect_key['Num_query_nljoins'] = 'N_Q_nljoins'
		self.collect_key['Num_query_mjoins'] = 'N_Q_mjoins'
		self.collect_key['Num_query_objfetches'] = 'N_Q_objfetches'
		self.collect_key['Num_query_holdable_cursors'] = 'N_Q_holdable_cur'
		self.collect_key['Num_sort_io_pages'] = 'N_sort_io_P'
		self.collect_key['Num_sort_data_pages'] = 'N_sort_data_P'
		self.collect_key['Num_network_requests'] = 'N_net_req'
		self.collect_key['Num_adaptive_flush_pages'] = 'N_ad_flush_P'
		self.collect_key['Num_adaptive_flush_log_pages'] = 'N_ad_flush_log_P'
		self.collect_key['Num_adaptive_flush_max_pages'] = 'N_ad_flush_max_P'
		self.collect_key['Num_prior_lsa_list_size'] = 'N_prior_lsa_size'
		self.collect_key['Num_prior_lsa_list_maxed'] = 'N_prior_lsa_maxed'
		self.collect_key['Num_prior_lsa_list_removed'] = 'N_prior_lsa_rem'
		self.collect_key['Num_heap_stats_bestspace_entries'] = 'N_heap_best_ent'
		self.collect_key['Num_heap_stats_bestspace_maxed'] = 'N_heap_BS_max'
		self.collect_key['Time_ha_replication_delay'] = 'Time_ha_rep_delay'
		self.collect_key['Data_page_buffer_hit_ratio'] = 'buffer_hit_ratio'



