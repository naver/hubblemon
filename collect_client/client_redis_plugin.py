
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

class redis_stat:
	def __init__(self):
		self.name = 'redis'
		self.type = 'rrd'
		self.addr = []

		self.collect_alias_key_init()
		self.create_key_init()

	def __repr__(self):
		return '[%s-(%s,%s)]' % (self.addr.__repr__(), self.name, self.type)

	def push_addr(self, addr):
		ip, port = addr.split(':')
		ip = socket.gethostbyname(ip)
		self.addr.append((ip, port))

	def do_redis_command(self, ip, port, command):
		tn = telnetlib.Telnet(ip, port)

		tn.write(bytes(command + '\r\n', 'utf-8'))
		tn.write(bytes('quit\r\n', 'utf-8'))

		result = tn.read_until(b'+OK', 1)
		result = result.decode('utf-8')

		tn.close()

		#print(result)
		return result


	def collect_stat(self, all_stats):
		for addr in self.addr:
			stat = {}

			cmds = ['info', 'info commandstats']
			for cmd in cmds:
				result = self.do_redis_command(addr[0], addr[1], cmd)
				lines = result.split('\r\n')

				for line in lines:
					ret = line.split(':')
					if (len(ret) == 1):
						continue

					key, value = ret[0], ret[1]

					if key not in self.collect_key:	 # don't send this key
						continue

					if ',' in value: # command stat
						ret = value.split(',')
						calls = ret[0]
						dummy, value = calls.split('=')

					alias_key = self.collect_key[key]

					if value.endswith('G'):
						value = float(value[:-1]) * 1000000000
					elif value.endswith('M'):
						value = float(value[:-1]) * 1000000
					elif value.endswith('K'):
						value = float(value[:-1]) * 1000
		
		
					if key.startswith('used_cpu_'):
						value = int(float(value) * 1000) # change to milli ticks
					elif key == 'mem_fragmentation_ratio':
						value = int(float(value) * 100) # change to percentage
					else:
						value = int(value)

					stat[alias_key] = value # real name in rrd file

			#print(stat)

			for k, v in self.collect_key.items():
				if v not in stat:
					stat[v] = 0

			all_stats['redis_%s' % addr[1]] = stat

	def collect(self):
		all_stats = {}
		
		self.collect_stat(all_stats)
		return all_stats
		

	def create(self):
		all_map = {}

		for addr in self.addr:
			all_map['redis_%s' % addr[1]] = self.create_key_list # stats per port

		all_map['RRA'] = self.rra_list
		return all_map


	def create_key_init(self):
		self.create_key_list=[
				('connections', 'GAUGE', 60, '0', 'U'),
				('memory', 'GAUGE', 60, '0', 'U'),
				('memory_human', 'GAUGE', 60, '0', 'U'),
				('memory_rss', 'GAUGE', 60, '0', 'U'),
				('memory_lua', 'GAUGE', 60, '0', 'U'),
				('mem_frag', 'GAUGE', 60, '0', 'U'),
				('cmds_processed', 'DERIVE', 60, '0', 'U'),
				('expired_keys', 'DERIVE', 60, '0', 'U'),
				('evicted_keys', 'DERIVE', 60, '0', 'U'),
				('keyspace_hits', 'DERIVE', 60, '0', 'U'),
				('keyspace_misses', 'DERIVE', 60, '0', 'U'),
				('cpu_sys', 'DERIVE', 60, '0', 'U'),
				('cpu_user', 'DERIVE', 60, '0', 'U'),
				('cpu_sys_children', 'DERIVE', 60, '0', 'U'),
				('cpu_user_children', 'DERIVE', 60, '0', 'U'),
				('cmd_checkpoint', 'DERIVE', 60, '0', 'U'),
				('cmd_get', 'DERIVE', 60, '0', 'U'),
				('cmd_set', 'DERIVE', 60, '0', 'U'),
				('cmd_del', 'DERIVE', 60, '0', 'U'),
				('cmd_mget', 'DERIVE', 60, '0', 'U'),
				('cmd_mset', 'DERIVE', 60, '0', 'U'),
				('cmd_expire', 'DERIVE', 60, '0', 'U'),
				('cmd_lindex', 'DERIVE', 60, '0', 'U'),
				('cmd_linsert', 'DERIVE', 60, '0', 'U'),
				('cmd_llen', 'DERIVE', 60, '0', 'U'),
				('cmd_lpop', 'DERIVE', 60, '0', 'U'),
				('cmd_lpush', 'DERIVE', 60, '0', 'U'),
				('cmd_lrange', 'DERIVE', 60, '0', 'U'),
				('cmd_sadd', 'DERIVE', 60, '0', 'U'),
				('cmd_srem', 'DERIVE', 60, '0', 'U'),
				('cmd_scard', 'DERIVE', 60, '0', 'U'),
				('cmd_sismember', 'DERIVE', 60, '0', 'U'),
				('cmd_smembers', 'DERIVE', 60, '0', 'U'),
				('cmd_zadd', 'DERIVE', 60, '0', 'U'),
				('cmd_zcard', 'DERIVE', 60, '0', 'U'),
				('cmd_zrange', 'DERIVE', 60, '0', 'U'),
				('cmd_zrank', 'DERIVE', 60, '0', 'U'),
				('cmd_zscore', 'DERIVE', 60, '0', 'U'),
				('cmd_zrem', 'DERIVE', 60, '0', 'U'),
				# reserved
				('stat_derive_01', 'DERIVE', 60, '0', 'U'),
				('stat_derive_02', 'DERIVE', 60, '0', 'U'),
				('stat_derive_03', 'DERIVE', 60, '0', 'U'),
				('stat_derive_04', 'DERIVE', 60, '0', 'U'),
				('stat_derive_05', 'DERIVE', 60, '0', 'U'),
				('stat_gauge_01', 'GAUGE', 60, '0', 'U'),
				('stat_gauge_02', 'GAUGE', 60, '0', 'U'),
				('stat_gauge_03', 'GAUGE', 60, '0', 'U'),
				('stat_gauge_04', 'GAUGE', 60, '0', 'U'),
				('stat_gauge_05', 'GAUGE', 60, '0', 'U')]


		# used for RRA
		self.rra_list =	[  ('MAX', 0.5, 5/5, (3600/5)*24), 	# 5sec  (to 1day), 17280
				   ('MAX', 0.5, 60/5, (3600/60)*24*7), 	# 1min (to 7day), 10080
				   ('MAX', 0.5, 3600/5, 24*31),		# 1hour (to 1month), 744
				   ('MAX', 0.5, 3600*3/5, (24/3)*366*3) ]	# 3hour (to 3year), 8734



	def collect_alias_key_init(self):
		self.collect_key = {}
		self.collect_key['connected_clients'] = 'connections'
		self.collect_key['used_memory'] = 'memory'
		self.collect_key['used_memory_human'] = 'memory_human'
		self.collect_key['used_memory_rss'] = 'memory_rss'
		self.collect_key['used_memory_lua'] = 'memory_lua'
		self.collect_key['mem_fragmentation_ratio'] = 'mem_frag'
		self.collect_key['total_commands_processed'] = 'cmds_processed'
		self.collect_key['expired_keys'] = 'expired_keys'
		self.collect_key['evicted_keys'] = 'evicted_keys'
		self.collect_key['keyspace_hits'] = 'keyspace_hits'
		self.collect_key['keyspace_misses'] = 'keyspace_misses'
		self.collect_key['used_cpu_sys'] = 'cpu_sys'
		self.collect_key['used_cpu_user'] = 'cpu_user'
		self.collect_key['used_cpu_sys_children'] = 'cpu_sys_children'
		self.collect_key['used_cpu_user_children'] = 'cpu_user_children'
		self.collect_key['cmdstat_checkpoint'] = 'cmd_checkpoint'
		self.collect_key['cmdstat_get'] = 'cmd_get'
		self.collect_key['cmdstat_set'] = 'cmd_set'
		self.collect_key['cmdstat_del'] = 'cmd_del'
		self.collect_key['cmdstat_mget'] = 'cmd_mget'
		self.collect_key['cmdstat_mset'] = 'cmd_mset'
		self.collect_key['cmdstat_expire'] = 'cmd_expire'
		self.collect_key['cmdstat_lindex'] = 'cmd_lindex'
		self.collect_key['cmdstat_linsert'] = 'cmd_linsert'
		self.collect_key['cmdstat_llen'] = 'cmd_llen'
		self.collect_key['cmdstat_lpop'] = 'cmd_lpop'
		self.collect_key['cmdstat_lpush'] = 'cmd_lpush'
		self.collect_key['cmdstat_lrange'] = 'cmd_lrange'
		self.collect_key['cmdstat_sadd'] = 'cmd_sadd'
		self.collect_key['cmdstat_srem'] = 'cmd_srem'
		self.collect_key['cmdstat_scard'] = 'cmd_scard'
		self.collect_key['cmdstat_sismember'] = 'cmd_sismember'
		self.collect_key['cmdstat_smembers'] = 'cmd_smembers'
		self.collect_key['cmdstat_zadd'] = 'cmd_zadd'
		self.collect_key['cmdstat_zcard'] = 'cmd_zcard'
		self.collect_key['cmdstat_zrange'] = 'cmd_zrange'
		self.collect_key['cmdstat_zrand'] = 'cmd_zrank'
		self.collect_key['cmdstat_zscore'] = 'cmd_zscore'
		self.collect_key['cmdstat_zrem'] = 'cmd_zrem'
		# reserved
		self.collect_key['stat_derive_01'] = 'stat_derive_01'
		self.collect_key['stat_derive_02'] = 'stat_derive_02'
		self.collect_key['stat_derive_03'] = 'stat_derive_03'
		self.collect_key['stat_derive_04'] = 'stat_derive_04'
		self.collect_key['stat_derive_05'] = 'stat_derive_05'
		self.collect_key['stat_gauge_01'] = 'stat_gauge_01'
		self.collect_key['stat_gauge_02'] = 'stat_gauge_02'
		self.collect_key['stat_gauge_03'] = 'stat_gauge_03'
		self.collect_key['stat_gauge_04'] = 'stat_gauge_04'
		self.collect_key['stat_gauge_05'] = 'stat_gauge_05'


