
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


import pymysql

class mysql_stat:
	def __init__(self):
		self.name = 'mysql'
		self.type = 'rrd'

		self.name_sock_map = {}
		self.name_conn_map = {}

		self.collect_key_init()
		self.create_key_init()

			

	def __repr__(self):
		return '[%s-(%s,%s)]' % (self.name_sock_map.__repr__(), self.name, self.type)

	def push_db(self, name, unix_sock, id, pw):
		self.name_sock_map[name] = (unix_sock, id, pw)
		self.name_conn_map[name] = pymysql.connect(host='127.0.0.1', unix_socket=unix_sock, user=id, passwd=pw)



	def collect(self):
		all_stats = {}
		for name, conn in self.name_conn_map.items():
			stat = {}

			try:
				curr = conn.cursor()
				ret = curr.execute('show status')
				#print(ret)
				for resp in curr:
					key, value = resp[0], resp[1]

					if key not in self.collect_key:	 # don't send this key
						continue

					alias_key = self.collect_key[key]
					value = int(float(value))

					stat[alias_key] = value # real name in rrd file

					for k, v in self.collect_key.items():
						if v not in stat:
							stat[v] = 0
						
				all_stats['mysql_%s' % name] = stat
				curr.close()

			except: # reconnect
				ret = self.name_sock_map[name]
				self.name_conn_map[name] = pymysql.connect(host='127.0.0.1', unix_socket=ret[0], user=ret[1], passwd=ret[2])

		#print(all_stats)
		return all_stats

		

	def create(self):
		all_map = {}

		for name, sock in self.name_sock_map.items():
			all_map['mysql_%s' % name] = self.create_key_list # stats per port

		all_map['RRA'] = self.rra_list
		return all_map


	def create_key_init(self):
		self.collect_key_init()

		self.create_key_list=[ (self.collect_key['Binlog_cache_disk_use'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Binlog_cache_use'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Bytes_received'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Bytes_sent'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_alter_table'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_call_procedure'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_commit'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_create_table'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_dealloc_sql'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_delete'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_delete_multi'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_do'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_drop_table'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_execute_sql'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_flush'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_insert'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_insert_select'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_prepare_sql'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_release_savepoint'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_rename_table'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_replace'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_replace_select'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_rollback'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_rollback_to_savepoint'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_savepoint'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_select'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_stmt_close'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_stmt_execute'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_stmt_fetch'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_stmt_prepare'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_stmt_reprepare'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_stmt_reset'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_truncate'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_update'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Com_update_multi'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Connections'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_buffer_pool_pages_data'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Innodb_buffer_pool_pages_dirty'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Innodb_buffer_pool_pages_flushed'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_buffer_pool_pages_free'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Innodb_buffer_pool_pages_misc'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Innodb_buffer_pool_pages_total'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Innodb_buffer_pool_read_ahead'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_buffer_pool_read_ahead_evicted'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_buffer_pool_read_requests'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_buffer_pool_reads'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_buffer_pool_wait_free'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_buffer_pool_write_requests'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_data_fsyncs'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_data_pending_fsyncs'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Innodb_data_pending_reads'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Innodb_data_pending_writes'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Innodb_data_read'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_data_reads'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_data_writes'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_data_written'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_dblwr_pages_written'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_dblwr_writes'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_log_waits'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_log_write_requests'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_log_writes'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_pages_created'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_pages_read'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_pages_written'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_row_lock_current_waits'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_row_lock_time'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_row_lock_time_avg'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_row_lock_time_max'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_row_lock_waits'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_rows_deleted'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_rows_inserted'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_rows_read'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Innodb_rows_updated'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Not_flushed_delayed_rows'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Opened_files'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Opened_table_definitions'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Opened_tables'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Prepared_stmt_count'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Qcache_free_blocks'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Qcache_free_memory'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Qcache_hits'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Qcache_inserts'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Qcache_lowmem_prunes'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Qcache_not_cached'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Qcache_queries_in_cache'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Qcache_total_blocks'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Queries'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Select_full_join'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Select_full_range_join'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Select_range'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Select_range_check'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Select_scan'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Slow_queries'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Sort_merge_passes'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Sort_range'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Sort_rows'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Sort_scan'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Table_locks_immediate'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Table_locks_waited'], 'DERIVE', 60, '0', 'U'),
				(self.collect_key['Threads_cached'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Threads_connected'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Threads_created'], 'GAUGE', 60, '0', 'U'),
				(self.collect_key['Threads_running'], 'GAUGE', 60, '0', 'U')]


		# used for RRA
		self.rra_list =	[  ('MAX', 0.5, 5/5, (3600/5)*24), 	# 5sec  (to 1day)
				   ('MAX', 0.5, 60/5, (3600/60)*24*7), 	# 30sec (to 7day)
				   ('MAX', 0.5, 3600/5, 24*31),		# 1hour (to 1month)
				   ('MAX', 0.5, 3600*3/5, (24/3)*366*3) ]	# 3hour (to 3year)



	def collect_key_init(self):
		self.collect_key = {}

		self.collect_key['Binlog_cache_disk_use'] = 'Binlog_cache_disk'
		self.collect_key['Binlog_cache_use'] = 'Binlog_cache'
		self.collect_key['Bytes_received'] = 'Bytes_received'
		self.collect_key['Bytes_sent'] = 'Bytes_sent'
		self.collect_key['Com_alter_table'] = 'Com_alter_table'
		self.collect_key['Com_call_procedure'] = 'Com_call_proc'
		self.collect_key['Com_commit'] = 'Com_commit'
		self.collect_key['Com_create_table'] = 'Com_create_table'
		self.collect_key['Com_dealloc_sql'] = 'Com_dealloc_sql'
		self.collect_key['Com_delete'] = 'Com_delete'
		self.collect_key['Com_delete_multi'] = 'Com_delete_multi'
		self.collect_key['Com_do'] = 'Com_do'
		self.collect_key['Com_drop_table'] = 'Com_drop_table'
		self.collect_key['Com_execute_sql'] = 'Com_execute_sql'
		self.collect_key['Com_flush'] = 'Com_flush'
		self.collect_key['Com_insert'] = 'Com_insert'
		self.collect_key['Com_insert_select'] = 'Com_insert_select'
		self.collect_key['Com_prepare_sql'] = 'Com_prepare_sql'
		self.collect_key['Com_release_savepoint'] = 'Com_release_SP'
		self.collect_key['Com_rename_table'] = 'Com_rename_table'
		self.collect_key['Com_replace'] = 'Com_replace'
		self.collect_key['Com_replace_select'] = 'Com_replace_select'
		self.collect_key['Com_rollback'] = 'Com_rollback'
		self.collect_key['Com_rollback_to_savepoint'] = 'Com_rollback_to_SP'
		self.collect_key['Com_savepoint'] = 'Com_savepoint'
		self.collect_key['Com_select'] = 'Com_select'
		self.collect_key['Com_stmt_close'] = 'Com_stmt_close'
		self.collect_key['Com_stmt_execute'] = 'Com_stmt_execute'
		self.collect_key['Com_stmt_fetch'] = 'Com_stmt_fetch'
		self.collect_key['Com_stmt_prepare'] = 'Com_stmt_prepare'
		self.collect_key['Com_stmt_reprepare'] = 'Com_stmt_reprepare'
		self.collect_key['Com_stmt_reset'] = 'Com_stmt_reset'
		self.collect_key['Com_truncate'] = 'Com_truncate'
		self.collect_key['Com_update'] = 'Com_update'
		self.collect_key['Com_update_multi'] = 'Com_update_multi'
		self.collect_key['Connections'] = 'Connections'
		self.collect_key['Innodb_buffer_pool_pages_data'] = 'idb_bpool_P_data'
		self.collect_key['Innodb_buffer_pool_pages_dirty'] = 'idb_bpool_P_dirty'
		self.collect_key['Innodb_buffer_pool_pages_flushed'] = 'idb_bpool_P_flushed'
		self.collect_key['Innodb_buffer_pool_pages_free'] = 'idb_bpool_P_free'
		self.collect_key['Innodb_buffer_pool_pages_misc'] = 'idb_bpool_P_misc'
		self.collect_key['Innodb_buffer_pool_pages_total'] = 'idb_bpool_P_total'
		self.collect_key['Innodb_buffer_pool_read_ahead'] = 'idb_bpool_ra'
		self.collect_key['Innodb_buffer_pool_read_ahead_evicted'] = 'idb_bpool_ra_evict'
		self.collect_key['Innodb_buffer_pool_read_requests'] = 'idb_bpool_read_req'
		self.collect_key['Innodb_buffer_pool_reads'] = 'idb_bpool_reads'
		self.collect_key['Innodb_buffer_pool_wait_free'] = 'idb_bpool_wait_free'
		self.collect_key['Innodb_buffer_pool_write_requests'] = 'idb_bpool_write_req'
		self.collect_key['Innodb_data_fsyncs'] = 'idb_data_fsyncs'
		self.collect_key['Innodb_data_pending_fsyncs'] = 'idb_data_pend_fsync'
		self.collect_key['Innodb_data_pending_reads'] = 'idb_data_pend_rds'
		self.collect_key['Innodb_data_pending_writes'] = 'idb_data_pend_wrs'
		self.collect_key['Innodb_data_read'] = 'idb_data_read'
		self.collect_key['Innodb_data_reads'] = 'idb_data_reads'
		self.collect_key['Innodb_data_writes'] = 'idb_data_writes'
		self.collect_key['Innodb_data_written'] = 'idb_data_written'
		self.collect_key['Innodb_dblwr_pages_written'] = 'idb_dblwr_P_written'
		self.collect_key['Innodb_dblwr_writes'] = 'idb_dblwr_writes'
		self.collect_key['Innodb_log_waits'] = 'idb_log_waits'
		self.collect_key['Innodb_log_write_requests'] = 'idb_log_wr_req'
		self.collect_key['Innodb_log_writes'] = 'idb_log_writes'
		self.collect_key['Innodb_pages_created'] = 'idb_P_created'
		self.collect_key['Innodb_pages_read'] = 'idb_P_read'
		self.collect_key['Innodb_pages_written'] = 'idb_P_written'
		self.collect_key['Innodb_row_lock_current_waits'] = 'idb_row_lck_C_waits'
		self.collect_key['Innodb_row_lock_time'] = 'idb_row_lock_time'
		self.collect_key['Innodb_row_lock_time_avg'] = 'idb_row_lck_avg'
		self.collect_key['Innodb_row_lock_time_max'] = 'idb_row_lck_max'
		self.collect_key['Innodb_row_lock_waits'] = 'idb_row_lck_waits'
		self.collect_key['Innodb_rows_deleted'] = 'idb_rows_deleted'
		self.collect_key['Innodb_rows_inserted'] = 'idb_rows_inserted'
		self.collect_key['Innodb_rows_read'] = 'idb_rows_read'
		self.collect_key['Innodb_rows_updated'] = 'idb_rows_updated'
		self.collect_key['Not_flushed_delayed_rows'] = 'Not_flu_delayed_R'
		self.collect_key['Opened_files'] = 'Opened_files'
		self.collect_key['Opened_table_definitions'] = 'Opened_table_def'
		self.collect_key['Opened_tables'] = 'Opened_tables'
		self.collect_key['Prepared_stmt_count'] = 'Prepared_stmt_count'
		self.collect_key['Qcache_free_blocks'] = 'Qcache_free_blocks'
		self.collect_key['Qcache_free_memory'] = 'Qcache_free_memory'
		self.collect_key['Qcache_hits'] = 'Qcache_hits'
		self.collect_key['Qcache_inserts'] = 'Qcache_inserts'
		self.collect_key['Qcache_lowmem_prunes'] = 'Qcache_lowm_prunes'
		self.collect_key['Qcache_not_cached'] = 'Qcache_not_cached'
		self.collect_key['Qcache_queries_in_cache'] = 'Qcache_Q_in_cache'
		self.collect_key['Qcache_total_blocks'] = 'Qcache_total_blocks'
		self.collect_key['Queries'] = 'Queries'
		self.collect_key['Select_full_join'] = 'Select_full_join'
		self.collect_key['Select_full_range_join'] = 'Select_F_range_join'
		self.collect_key['Select_range'] = 'Select_range'
		self.collect_key['Select_range_check'] = 'Select_range_check'
		self.collect_key['Select_scan'] = 'Select_scan'
		self.collect_key['Slow_queries'] = 'Slow_queries'
		self.collect_key['Sort_merge_passes'] = 'Sort_merge_passes'
		self.collect_key['Sort_range'] = 'Sort_range'
		self.collect_key['Sort_rows'] = 'Sort_rows'
		self.collect_key['Sort_scan'] = 'Sort_scan'
		self.collect_key['Table_locks_immediate'] = 'Table_locks_imme'
		self.collect_key['Table_locks_waited'] = 'Table_locks_waited'
		self.collect_key['Threads_cached'] = 'Threads_cached'
		self.collect_key['Threads_connected'] = 'Threads_connected'
		self.collect_key['Threads_created'] = 'Threads_created'
		self.collect_key['Threads_running'] = 'Threads_running'



