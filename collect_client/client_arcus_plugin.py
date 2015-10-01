
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

class arcus_stat:
	def __init__(self):
		self.name = 'arcus'
		self.type = 'rrd'
		self.addr = []

		self.collect_key_init()
		self.collect_prefix_key_init()

		self.create_key_init()
		self.flag_auto_register = False

	def __repr__(self):
		return '[%s-(%s,%s)]' % (self.addr.__repr__(), self.name, self.type)

	def auto_register(self):
		self.flag_auto_register = True

		proc1 = subprocess.Popen(shlex.split('ps -ef'), stdout=subprocess.PIPE)
		proc2 = subprocess.Popen(shlex.split('grep memcached'), stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		proc1.stdout.close()
		out, err = proc2.communicate()
		out = out.decode('utf-8')
		lines = out.split('\n')

		tmp_addr = []
		for line in lines:
			lst = line.split()

			flag = False
			port = 0
			for a in lst:
				if a == '-p':
					flag = True
					continue

				if flag == True:
					try:
						port = int(a)
					except ValueError:
						port = 0

					break

			if port > 0:
				tmp_addr.append( ('127.0.0.1', str(port)) )


		tmp_addr.sort()

		if self.addr != tmp_addr:
			print('## auto register memcached port')
			print(tmp_addr)
			self.addr = tmp_addr
			return True

		return False

	def push_addr(self, addr):
		ip, port = addr.split(':')
		ip = socket.gethostbyname(ip)
		
		self.addr.append((ip, port))

	def do_arcus_command(self, ip, port, command):
		tn = telnetlib.Telnet(ip, port)
		tn.write(bytes(command + '\r\n', 'utf-8'))
		result = tn.read_until(bytes('END', 'utf-8'), 0.2)


		result = result.decode('utf-8');
		tn.write(bytes('quit\r\n', 'utf-8'))
		tn.close()
		return result;

	def collect_stat(self, all_stats):
		for addr in self.addr:
			stat = {}

			cmds = ['stats', 'stats slabs']
			for cmd in cmds:
				result = self.do_arcus_command(addr[0], addr[1], cmd)
				lines = result.split('\r\n')

				for line in lines:
					if line == 'END':
						continue

					if line.strip() == '':
						continue

					dummy, key, value = line.split()
					if key not in self.collect_key:	 # don't send this key
						continue

					alias_key = self.collect_key[key]
		
					if key == 'rusage_user' or key == 'rusage_system':
						value = int(float(value) * 1000000) # change to micro ticks
					else:
						value = int(value)

					stat[alias_key] = value # real name in rrd file


			for k, v in self.collect_key.items():
				if v not in stat:
					stat[v] = 0

			all_stats['arcus_%s' % addr[1]] = stat

	def collect_prefix(self, all_stats):
		for addr in self.addr:
			result = self.do_arcus_command(addr[0], addr[1], 'stats detail dump')
			lines = result.split('\r\n')
			stat = {}

			if len(lines) > 32: # ignore too many prefixes
				return 

			for line in lines:
				if line == 'END':
					continue

				if line.strip() == '':
					continue

				items = line.split()
				prefix = items[1]
				
				items = items[2:] 
				tmp_stats = dict(zip(items[0::2], items[1::2]))
				stats = {}

				for k, v in tmp_stats.items():
					if k not in self.collect_prefix_key: # don't send this key
						continue

					alias_key = self.collect_prefix_key[k]
					stats[alias_key] = int(v)

					for k, v in self.collect_prefix_key.items():
						if v not in stats:
							stats[v] = 0
					
				all_stats['arcus_%s-%s' % (addr[1], prefix)] = stats


	def collect(self):
		all_stats = {}
		
		if self.flag_auto_register == True:
			if self.auto_register() == True:
				return None # for create new file
			
		self.collect_stat(all_stats)
		self.collect_prefix(all_stats)
		return all_stats
		

	def create(self):
		all_map = {}

		for addr in self.addr:
			all_map['arcus_%s' % addr[1]] = self.create_key_list # stats per port

		prefix_stat = {}
		self.collect_prefix(prefix_stat)
		for key in prefix_stat:
			all_map[key] = self.create_prefix_key_list # stats per port-prefix
	
		all_map['RRA'] = self.rra_list
		return all_map


	def create_key_init(self):
		self.create_key_list=[
				('rusage_user', 'DERIVE', 60, '0', 'U'),
				('rusage_system', 'DERIVE', 60, '0', 'U'),
				('cmd_set', 'DERIVE', 60, '0', 'U'),
				('cmd_bop_insert', 'DERIVE', 60, '0', 'U'),
				('cmd_bop_delete', 'DERIVE', 60, '0', 'U'),
				('cmd_sop_exist', 'DERIVE', 60, '0', 'U'),
				('rejected_conns', 'DERIVE', 60, '0', 'U'),
				('limit_maxbytes', 'GAUGE', 60, '0', 'U'),
				('cmd_bop_position', 'DERIVE', 60, '0', 'U'),
				('bytes', 'GAUGE', 60, '0', 'U'),
				('sop_exist_hits', 'DERIVE', 60, '0', 'U'),
				('lop_get_nhits', 'DERIVE', 60, '0', 'U'),
				('lop_delete_nhits', 'DERIVE', 60, '0', 'U'),
				('cmd_bop_update', 'DERIVE', 60, '0', 'U'),
				('cmd_bop_incr', 'DERIVE', 60, '0', 'U'),
				('cmd_lop_create', 'DERIVE', 60, '0', 'U'),
				('cmd_lop_get', 'DERIVE', 60, '0', 'U'),
				('bop_decr_nhits', 'DERIVE', 60, '0', 'U'),
				('bop_gbp_nhits', 'DERIVE', 60, '0', 'U'),
				('reclaimed', 'DERIVE', 60, '0', 'U'),
				('bop_insert_hits', 'DERIVE', 60, '0', 'U'),
				('cmd_bop_decr', 'DERIVE', 60, '0', 'U'),
				('sticky_bytes', 'GAUGE', 60, '0', 'U'),
				('lop_insert_hits', 'DERIVE', 60, '0', 'U'),
				('cmd_sop_insert', 'DERIVE', 60, '0', 'U'),
				('sop_delete_ehits', 'DERIVE', 60, '0', 'U'),
				('bytes_written', 'DERIVE', 60, '0', 'U'),
				('cmd_setattr', 'DERIVE', 60, '0', 'U'),
				('sop_create_oks', 'DERIVE', 60, '0', 'U'),
				('cmd_bop_count', 'DERIVE', 60, '0', 'U'),
				('lop_delete_ehits', 'DERIVE', 60, '0', 'U'),
				('curr_connections', 'GAUGE', 60, '0', 'U'),
				('bop_count_hits', 'DERIVE', 60, '0', 'U'),
				('bop_position_nhits', 'DERIVE', 60, '0', 'U'),
				('cmd_bop_get', 'DERIVE', 60, '0', 'U'),
				('sop_insert_hits', 'DERIVE', 60, '0', 'U'),
				('decr_hits', 'DERIVE', 60, '0', 'U'),
				('bop_smget_oks', 'DERIVE', 60, '0', 'U'),
				('getattr_hits', 'DERIVE', 60, '0', 'U'),
				('bop_incr_ehits', 'DERIVE', 60, '0', 'U'),
				('setattr_hits', 'DERIVE', 60, '0', 'U'),
				('lop_create_oks', 'DERIVE', 60, '0', 'U'),
				('incr_hits', 'DERIVE', 60, '0', 'U'),
				('cmd_bop_mget', 'DERIVE', 60, '0', 'U'),
				('cmd_sop_create', 'DERIVE', 60, '0', 'U'),
				('lop_get_ehits', 'DERIVE', 60, '0', 'U'),
				('sop_delete_nhits', 'DERIVE', 60, '0', 'U'),
				('cmd_lop_delete', 'DERIVE', 60, '0', 'U'),
				('bop_get_nhits', 'DERIVE', 60, '0', 'U'),
				('bop_update_ehits', 'DERIVE', 60, '0', 'U'),
				('bop_create_oks', 'DERIVE', 60, '0', 'U'),
				('bop_decr_ehits', 'DERIVE', 60, '0', 'U'),
				('delete_hits', 'DERIVE', 60, '0', 'U'),
				('sticky_limit', 'GAUGE', 60, '0', 'U'),
				('bop_gbp_ehits', 'DERIVE', 60, '0', 'U'),
				('bop_get_ehits', 'DERIVE', 60, '0', 'U'),
				('cmd_lop_insert', 'DERIVE', 60, '0', 'U'),
				('engine_maxbytes', 'GAUGE', 60, '0', 'U'),
				('bop_delete_nhits', 'DERIVE', 60, '0', 'U'),
				('bop_incr_nhits', 'DERIVE', 60, '0', 'U'),
				('cmd_flush', 'DERIVE', 60, '0', 'U'),
				('curr_items', 'GAUGE', 60, '0', 'U'),
				('cmd_sop_get', 'DERIVE', 60, '0', 'U'),
				('total_items', 'DERIVE', 60, '0', 'U'),
				('bop_delete_ehits', 'DERIVE', 60, '0', 'U'),
				('evictions', 'DERIVE', 60, '0', 'U'),
				('bop_update_nhits', 'DERIVE', 60, '0', 'U'),
				('bytes_read', 'DERIVE', 60, '0', 'U'),
				('get_hits', 'DERIVE', 60, '0', 'U'),
				('cmd_get', 'DERIVE', 60, '0', 'U'),
				('sticky_items', 'DERIVE', 60, '0', 'U'),
				('bop_position_ehits', 'DERIVE', 60, '0', 'U'),
				('cmd_bop_create', 'DERIVE', 60, '0', 'U'),
				('cmd_getattr', 'DERIVE', 60, '0', 'U'),
				('cas_hits', 'DERIVE', 60, '0', 'U'),
				('cas_badval', 'DERIVE', 60, '0', 'U'),
				('cmd_flush_prefix', 'DERIVE', 60, '0', 'U'),
				('cmd_bop_gbp', 'DERIVE', 60, '0', 'U'),
				('conn_yields', 'DERIVE', 60, '0', 'U'),
				('sop_get_nhits', 'DERIVE', 60, '0', 'U'),
				('cmd_bop_smget', 'DERIVE', 60, '0', 'U'),
				('cmd_sop_delete', 'DERIVE', 60, '0', 'U'),
				('sop_get_ehits', 'DERIVE', 60, '0', 'U'),
				('bop_mget_oks', 'DERIVE', 60, '0', 'U'),
				('total_malloced', 'GAUGE', 60, '0', 'U'),
				('hb_count', 'DERIVE', 60, '0', 'U'),
				('hb_latency', 'DERIVE', 60, '0', 'U'),
				#('auth_errors', 'DERIVE', 60, '0', 'U'),
				#('auth_cmds', 'DERIVE', 60, '0', 'U'),
				#('time', 'DERIVE', 60, '0', 'U'),
				#('threads', 'DERIVE', 60, '0', 'U'),
				('stat_drv_01', 'DERIVE', 60, '0', 'U'), # for additional counter & gauge
				('stat_drv_02', 'DERIVE', 60, '0', 'U'),
				('stat_drv_03', 'DERIVE', 60, '0', 'U'),
				('stat_drv_04', 'DERIVE', 60, '0', 'U'),
				('stat_drv_05', 'DERIVE', 60, '0', 'U'),
				('stat_drv_06', 'DERIVE', 60, '0', 'U'),
				('stat_drv_07', 'DERIVE', 60, '0', 'U'),
				('stat_drv_08', 'DERIVE', 60, '0', 'U'),
				('stat_drv_09', 'DERIVE', 60, '0', 'U'),
				('stat_drv_10', 'DERIVE', 60, '0', 'U'),
				('stat_drv_11', 'DERIVE', 60, '0', 'U'),
				('stat_drv_12', 'DERIVE', 60, '0', 'U'),
				('stat_drv_13', 'DERIVE', 60, '0', 'U'),
				('stat_drv_14', 'DERIVE', 60, '0', 'U'),
				('stat_drv_15', 'DERIVE', 60, '0', 'U'),
				('stat_drv_16', 'DERIVE', 60, '0', 'U'),
				('stat_drv_17', 'DERIVE', 60, '0', 'U'),
				('stat_drv_18', 'DERIVE', 60, '0', 'U'),
				('stat_drv_19', 'DERIVE', 60, '0', 'U'),
				('stat_drv_20', 'DERIVE', 60, '0', 'U'),
				('stat_gauge_01', 'GAUGE', 60, '0', 'U'),
				('stat_gauge_02', 'GAUGE', 60, '0', 'U'),
				('stat_gauge_03', 'GAUGE', 60, '0', 'U'),
				('stat_gauge_04', 'GAUGE', 60, '0', 'U'),
				('stat_gauge_05', 'GAUGE', 60, '0', 'U')]

		self.create_prefix_key_list= [	('cmd_get', 'DERIVE', 60, '0', 'U'),
					('cmd_hit', 'DERIVE', 60, '0', 'U'),
					('cmd_set', 'DERIVE', 60, '0', 'U'),
					('cmd_del', 'DERIVE', 60, '0', 'U'),
					('cmd_lop_create', 'DERIVE', 60, '0', 'U'),
					('cmd_lop_insert', 'DERIVE', 60, '0', 'U'),
					('lop_insert_hits', 'DERIVE', 60, '0', 'U'),
					('cmd_lop_delete', 'DERIVE', 60, '0', 'U'),
					('lop_delete_hits', 'DERIVE', 60, '0', 'U'),
					('cmd_lop_get', 'DERIVE', 60, '0', 'U'),
					('lop_get_hits', 'DERIVE', 60, '0', 'U'),
					('cmd_sop_create', 'DERIVE', 60, '0', 'U'),
					('cmd_sop_insert', 'DERIVE', 60, '0', 'U'),
					('sop_insert_hits', 'DERIVE', 60, '0', 'U'),
					('cmd_sop_delete', 'DERIVE', 60, '0', 'U'),
					('sop_delete_hits', 'DERIVE', 60, '0', 'U'),
					('cmd_sop_get', 'DERIVE', 60, '0', 'U'),
					('sop_get_hits', 'DERIVE', 60, '0', 'U'),
					('cmd_bop_create', 'DERIVE', 60, '0', 'U'),
					('cmd_bop_insert', 'DERIVE', 60, '0', 'U'),
					('bop_insert_hits', 'DERIVE', 60, '0', 'U'),
					('cmd_bop_update', 'DERIVE', 60, '0', 'U'),
					('bop_update_hits', 'DERIVE', 60, '0', 'U'),
					('cmd_bop_incr', 'DERIVE', 60, '0', 'U'),
					('bop_incr_hits', 'DERIVE', 60, '0', 'U'),
					('cmd_bop_decr', 'DERIVE', 60, '0', 'U'),
					('bop_decr_hits', 'DERIVE', 60, '0', 'U'),
					('cmd_bop_delete', 'DERIVE', 60, '0', 'U'),
					('bop_delete_hits', 'DERIVE', 60, '0', 'U'),
					('cmd_bop_get', 'DERIVE', 60, '0', 'U'),
					('bop_get_hits', 'DERIVE', 60, '0', 'U'),
					('cmd_bop_count', 'DERIVE', 60, '0', 'U'),
					('bop_count_hits', 'DERIVE', 60, '0', 'U'),
					('cmd_getattr', 'DERIVE', 60, '0', 'U'),
					('getattr_hits', 'DERIVE', 60, '0', 'U'),
					('prefix_derive_01', 'DERIVE', 60, '0', 'U'),
					('prefix_derive_02', 'DERIVE', 60, '0', 'U'),
					('prefix_derive_03', 'DERIVE', 60, '0', 'U'),
					('prefix_derive_04', 'DERIVE', 60, '0', 'U'),
					('prefix_derive_05', 'DERIVE', 60, '0', 'U'),
					('prefix_gauge_01', 'GAUGE', 60, '0', 'U'),
					('prefix_gauge_02', 'GAUGE', 60, '0', 'U'),
					('prefix_gauge_03', 'GAUGE', 60, '0', 'U') ]

		# used for RRA
		self.rra_list =	[  ('MAX', 0.5, 5, (3600/5)*24), 	# 5sec  (to 1day), 17280
				   ('MAX', 0.5, 60, (3600/60)*24*7), 	# 1min (to 7day), 10080
				   ('MAX', 0.5, 3600, 24*31),		# 1hour (to 1month), 744
				   ('MAX', 0.5, 3600*3, (24/3)*366*3) ]	# 3hour (to 3year), 8734


	def collect_prefix_key_init(self):
		self.collect_prefix_key = {}

		self.collect_prefix_key['get'] = 'cmd_get'
		self.collect_prefix_key['hit'] = 'cmd_hit'
		self.collect_prefix_key['set'] = 'cmd_set'
		self.collect_prefix_key['del'] = 'cmd_del'
		self.collect_prefix_key['lcs'] = 'cmd_lop_create'
		self.collect_prefix_key['lis'] = 'cmd_lop_insert'
		self.collect_prefix_key['lih'] = 'lop_insert_hits'
		self.collect_prefix_key['lds'] = 'cmd_lop_delete'
		self.collect_prefix_key['ldh'] = 'lop_delete_hits'
		self.collect_prefix_key['lgs'] = 'cmd_lop_get'
		self.collect_prefix_key['lgh'] = 'lop_get_hits'
		self.collect_prefix_key['scs'] = 'cmd_sop_create'
		self.collect_prefix_key['sis'] = 'cmd_sop_insert'
		self.collect_prefix_key['sih'] = 'sop_insert_hits'
		self.collect_prefix_key['sds'] = 'cmd_sop_delete'
		self.collect_prefix_key['sdh'] = 'sop_delete_hits'
		self.collect_prefix_key['sgs'] = 'cmd_sop_get'
		self.collect_prefix_key['sgh'] = 'sop_get_hits'
		self.collect_prefix_key['bcs'] = 'cmd_bop_create'
		self.collect_prefix_key['bis'] = 'cmd_bop_insert'
		self.collect_prefix_key['bih'] = 'bop_insert_hits'
		self.collect_prefix_key['bus'] = 'cmd_bop_update'
		self.collect_prefix_key['buh'] = 'bop_update_hits'
		self.collect_prefix_key['bps'] = 'cmd_bop_incr'
		self.collect_prefix_key['bph'] = 'bop_incr_hits'
		self.collect_prefix_key['bms'] = 'cmd_bop_decr'
		self.collect_prefix_key['bmh'] = 'bop_decr_hits'
		self.collect_prefix_key['bds'] = 'cmd_bop_delete'
		self.collect_prefix_key['bdh'] = 'bop_delete_hits'
		self.collect_prefix_key['bgs'] = 'cmd_bop_get'
		self.collect_prefix_key['bgh'] = 'bop_get_hits'
		self.collect_prefix_key['bns'] = 'cmd_bop_count'
		self.collect_prefix_key['bnh'] = 'bop_count_hits'
		self.collect_prefix_key['gas'] = 'cmd_getattr'
		self.collect_prefix_key['sas'] = 'cmd_setattr'
		self.collect_prefix_key['prefix_derive_01'] = 'prefix_derive_01' # for reserved
		self.collect_prefix_key['prefix_derive_02'] = 'prefix_derive_02'
		self.collect_prefix_key['prefix_derive_03'] = 'prefix_derive_03'
		self.collect_prefix_key['prefix_derive_04'] = 'prefix_derive_04'
		self.collect_prefix_key['prefix_derive_05'] = 'prefix_derive_05'
		self.collect_prefix_key['prefix_gauge_01'] = 'prefix_gauge_01'
		self.collect_prefix_key['prefix_gauge_02'] = 'prefix_gauge_02'
		self.collect_prefix_key['prefix_gauge_03'] = 'prefix_gauge_03'


	def collect_key_init(self):
		self.collect_key = {}

		self.collect_key['rusage_user'] = 'rusage_user'
		self.collect_key['rusage_system'] = 'rusage_system'
		self.collect_key['cmd_set'] = 'cmd_set'
		self.collect_key['cmd_bop_insert'] = 'cmd_bop_insert'
		self.collect_key['cmd_bop_delete'] = 'cmd_bop_delete'
		self.collect_key['cmd_sop_exist'] = 'cmd_sop_exist'
		self.collect_key['rejected_conns'] = 'rejected_conns'
		self.collect_key['limit_maxbytes'] = 'limit_maxbytes'
		self.collect_key['cmd_bop_position'] = 'cmd_bop_position'
		self.collect_key['bytes'] = 'bytes'
		self.collect_key['sop_exist_hits'] = 'sop_exist_hits'
		self.collect_key['lop_get_none_hits'] = 'lop_get_nhits'
		self.collect_key['lop_delete_none_hits'] = 'lop_delete_nhits'
		self.collect_key['cmd_bop_update'] = 'cmd_bop_update'
		self.collect_key['cmd_bop_incr'] = 'cmd_bop_incr'
		self.collect_key['cmd_lop_create'] = 'cmd_lop_create'
		self.collect_key['cmd_lop_get'] = 'cmd_lop_get'
		self.collect_key['bop_decr_none_hits'] = 'bop_decr_nhits'
		self.collect_key['bop_gbp_none_hits'] = 'bop_gbp_nhits'
		self.collect_key['reclaimed'] = 'reclaimed'
		self.collect_key['bop_insert_hits'] = 'bop_insert_hits'
		self.collect_key['cmd_bop_decr'] = 'cmd_bop_decr'
		self.collect_key['sticky_bytes'] = 'sticky_bytes'
		self.collect_key['lop_insert_hits'] = 'lop_insert_hits'
		self.collect_key['cmd_sop_insert'] = 'cmd_sop_insert'
		self.collect_key['sop_delete_elem_hits'] = 'sop_delete_ehits'
		self.collect_key['bytes_written'] = 'bytes_written'
		self.collect_key['cmd_setattr'] = 'cmd_setattr'
		self.collect_key['sop_create_oks'] = 'sop_create_oks'
		self.collect_key['cmd_bop_count'] = 'cmd_bop_count'
		self.collect_key['lop_delete_elem_hits'] = 'lop_delete_ehits'
		self.collect_key['curr_connections'] = 'curr_connections'
		self.collect_key['bop_count_hits'] = 'bop_count_hits'
		self.collect_key['bop_position_none_hits'] = 'bop_position_nhits'
		self.collect_key['cmd_bop_get'] = 'cmd_bop_get'
		self.collect_key['sop_insert_hits'] = 'sop_insert_hits'
		self.collect_key['decr_hits'] = 'decr_hits'
		self.collect_key['bop_smget_oks'] = 'bop_smget_oks'
		self.collect_key['getattr_hits'] = 'getattr_hits'
		self.collect_key['bop_incr_elem_hits'] = 'bop_incr_ehits'
		self.collect_key['setattr_hits'] = 'setattr_hits'
		self.collect_key['lop_create_oks'] = 'lop_create_oks'
		self.collect_key['incr_hits'] = 'incr_hits'
		self.collect_key['cmd_bop_mget'] = 'cmd_bop_mget'
		self.collect_key['cmd_sop_create'] = 'cmd_sop_create'
		self.collect_key['lop_get_elem_hits'] = 'lop_get_ehits'
		self.collect_key['sop_delete_none_hits'] = 'sop_delete_nhits'
		self.collect_key['cmd_lop_delete'] = 'cmd_lop_delete'
		self.collect_key['bop_get_none_hits'] = 'bop_get_nhits'
		self.collect_key['bop_update_elem_hits'] = 'bop_update_ehits'
		self.collect_key['bop_create_oks'] = 'bop_create_oks'
		self.collect_key['bop_decr_elem_hits'] = 'bop_decr_ehits'
		self.collect_key['delete_hits'] = 'delete_hits'
		self.collect_key['sticky_limit'] = 'sticky_limit'
		self.collect_key['bop_gbp_elem_hits'] = 'bop_gbp_ehits'
		self.collect_key['bop_get_elem_hits'] = 'bop_get_ehits'
		self.collect_key['cmd_lop_insert'] = 'cmd_lop_insert'
		self.collect_key['engine_maxbytes'] = 'engine_maxbytes'
		self.collect_key['bop_delete_none_hits'] = 'bop_delete_nhits'
		self.collect_key['bop_incr_none_hits'] = 'bop_incr_nhits'
		self.collect_key['cmd_flush'] = 'cmd_flush'
		self.collect_key['curr_items'] = 'curr_items'
		self.collect_key['cmd_sop_get'] = 'cmd_sop_get'
		self.collect_key['total_items'] = 'total_items'
		self.collect_key['bop_delete_elem_hits'] = 'bop_delete_ehits'
		self.collect_key['evictions'] = 'evictions'
		self.collect_key['bop_update_none_hits'] = 'bop_update_nhits'
		self.collect_key['bytes_read'] = 'bytes_read'
		self.collect_key['get_hits'] = 'get_hits'
		self.collect_key['cmd_get'] = 'cmd_get'
		self.collect_key['sticky_items'] = 'sticky_items'
		self.collect_key['bop_position_elem_hits'] = 'bop_position_ehits'
		self.collect_key['cmd_bop_create'] = 'cmd_bop_create'
		self.collect_key['cmd_getattr'] = 'cmd_getattr'
		self.collect_key['cas_hits'] = 'cas_hits'
		self.collect_key['cas_badval'] = 'cas_badval'
		self.collect_key['cmd_flush_prefix'] = 'cmd_flush_prefix'
		self.collect_key['cmd_bop_gbp'] = 'cmd_bop_gbp'
		self.collect_key['conn_yields'] = 'conn_yields'
		self.collect_key['sop_get_none_hits'] = 'sop_get_nhits'
		self.collect_key['cmd_bop_smget'] = 'cmd_bop_smget'
		self.collect_key['cmd_sop_delete'] = 'cmd_sop_delete'
		self.collect_key['sop_get_elem_hits'] = 'sop_get_ehits'
		self.collect_key['bop_mget_oks'] = 'bop_mget_oks'
		self.collect_key['total_malloced'] = 'total_malloced'
		self.collect_key['hb_count'] = 'hb_count'
		self.collect_key['hb_latency'] = 'hb_latency'
		#self.collect_key['auth_errors'] = 'auth_errors'
		#self.collect_key['auth_cmds'] = 'auth_cmds'
		#self.collect_key['threads'] = 'threads'
		#self.collect_key['time'] = 'time'
		self.collect_key['stat_drv_01'] = 'stat_drv_01' # for reserved
		self.collect_key['stat_drv_02'] = 'stat_drv_02'
		self.collect_key['stat_drv_03'] = 'stat_drv_03'
		self.collect_key['stat_drv_04'] = 'stat_drv_04'
		self.collect_key['stat_drv_05'] = 'stat_drv_05'
		self.collect_key['stat_drv_06'] = 'stat_drv_06'
		self.collect_key['stat_drv_07'] = 'stat_drv_07'
		self.collect_key['stat_drv_08'] = 'stat_drv_08'
		self.collect_key['stat_drv_09'] = 'stat_drv_09'
		self.collect_key['stat_drv_10'] = 'stat_drv_10'
		self.collect_key['stat_drv_11'] = 'stat_drv_11' 
		self.collect_key['stat_drv_12'] = 'stat_drv_12'
		self.collect_key['stat_drv_13'] = 'stat_drv_13'
		self.collect_key['stat_drv_14'] = 'stat_drv_14'
		self.collect_key['stat_drv_15'] = 'stat_drv_15'
		self.collect_key['stat_drv_16'] = 'stat_drv_16'
		self.collect_key['stat_drv_17'] = 'stat_drv_17'
		self.collect_key['stat_drv_18'] = 'stat_drv_18'
		self.collect_key['stat_drv_19'] = 'stat_drv_19'
		self.collect_key['stat_drv_20'] = 'stat_drv_20'
		self.collect_key['stat_gauge_01'] = 'stat_gauge_01'
		self.collect_key['stat_gauge_02'] = 'stat_gauge_02'
		self.collect_key['stat_gauge_03'] = 'stat_gauge_03'
		self.collect_key['stat_gauge_04'] = 'stat_gauge_04'
		self.collect_key['stat_gauge_05'] = 'stat_gauge_05'


