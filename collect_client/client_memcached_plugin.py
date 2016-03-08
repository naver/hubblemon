
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

class memcached_stat:
	def __init__(self):
		self.name = 'memcached'
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

	def push_addr(self, addr):
		ip, port = addr.split(':')
		ip = socket.gethostbyname(ip)
		
		self.addr.append((ip, port))

	def do_memcached_command(self, ip, port, command):
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
				result = self.do_memcached_command(addr[0], addr[1], cmd)
				lines = result.split('\n')

				for line in lines:
					if line == 'END':
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

			all_stats["memcached_%s" % addr[1]] = stat

	def collect_prefix(self, all_stats):
		for addr in self.addr:
			result = self.do_memcached_command(addr[0], addr[1], 'stats detail dump')
			lines = result.split('\n')
			stat = {}

			if len(lines) > 32: # ignore too many prefixes
				return 

			for line in lines:
				if line == 'END':
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
					
				all_stats['memcached_prefix_%s-%s' % (addr[1], prefix)] = stats


	def collect(self):
		all_stats = {}
		
		if self.flag_auto_register == True:
			if self.auto_register() == True:
				return None # for create new file

		self.collect_stat(all_stats)
		self.collect_prefix(all_stats)
		#print(all_stats)
		return all_stats
		

	def create(self):
		all_map = {}

		for addr in self.addr:
			all_map['memcached_%s' % addr[1]] = self.create_key_list # stats per port

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
				('curr_connections', 'GAUGE', 60, '0', 'U'),
				('cmd_get', 'DERIVE', 60, '0', 'U'),
				('cmd_set', 'DERIVE', 60, '0', 'U'),
				('cmd_flush', 'DERIVE', 60, '0', 'U'),
				('cmd_touch', 'DERIVE', 60, '0', 'U'),
				('get_hits', 'DERIVE', 60, '0', 'U'),
				('delete_hits', 'DERIVE', 60, '0', 'U'),
				('incr_hits', 'DERIVE', 60, '0', 'U'),
				('decr_hits', 'DERIVE', 60, '0', 'U'),
				('cas_hits', 'DERIVE', 60, '0', 'U'),
				('cas_badval', 'DERIVE', 60, '0', 'U'),
				('touch_hits', 'DERIVE', 60, '0', 'U'),
				('auth_cmds', 'DERIVE', 60, '0', 'U'),
				('auth_errors', 'DERIVE', 60, '0', 'U'),
				('bytes_read', 'DERIVE', 60, '0', 'U'),
				('bytes_written', 'DERIVE', 60, '0', 'U'),
				('limit_maxbytes', 'GAUGE', 60, '0', 'U'),
				('bytes', 'GAUGE', 60, '0', 'U'),
				('curr_items', 'GAUGE', 60, '0', 'U'),
				('total_items', 'DERIVE', 60, '0', 'U'),
				('evictions', 'DERIVE', 60, '0', 'U'),
				('reclaimed', 'DERIVE', 60, '0', 'U'),
				('total_malloced', 'GAUGE', 60, '0', 'U')]


		self.create_prefix_key_list= [	('cmd_get', 'DERIVE', 60, '0', 'U'),
					('cmd_hit', 'DERIVE', 60, '0', 'U'),
					('cmd_set', 'DERIVE', 60, '0', 'U'),
					('cmd_del', 'DERIVE', 60, '0', 'U')]

		# used for RRA
		self.rra_list =	[  ('MAX', 0.5, 5/5, (3600/5)*24), 	# 5sec  (to 1day), 17280
				   ('MAX', 0.5, 60/5, (3600/60)*24*7), 	# 1min (to 7day), 10080
				   ('MAX', 0.5, 3600/5, 24*31),		# 1hour (to 1month), 744
				   ('MAX', 0.5, 3600*3/5, (24/3)*366*3) ]	# 3hour (to 3year), 8734


	def collect_prefix_key_init(self):
		self.collect_prefix_key = {}

		self.collect_prefix_key['get'] = 'cmd_get'
		self.collect_prefix_key['hit'] = 'cmd_hit'
		self.collect_prefix_key['set'] = 'cmd_set'
		self.collect_prefix_key['del'] = 'cmd_del'


	def collect_key_init(self):
		self.collect_key = {}

		self.collect_key['rusage_user'] = 'rusage_user'
		self.collect_key['rusage_system'] = 'rusage_system'
		self.collect_key['curr_connections'] = 'curr_connections'
		self.collect_key['cmd_get'] = 'cmd_get'
		self.collect_key['cmd_set'] = 'cmd_set'
		self.collect_key['cmd_flush'] = 'cmd_flush'
		self.collect_key['cmd_touch'] = 'cmd_touch'
		self.collect_key['get_hits'] = 'get_hits'
		self.collect_key['delete_hits'] = 'delete_hits'
		self.collect_key['incr_hits'] = 'incr_hits'
		self.collect_key['decr_hits'] = 'decr_hits'
		self.collect_key['cas_hits'] = 'cas_hits'
		self.collect_key['cas_badval'] = 'cas_badval'
		self.collect_key['touch_hits'] = 'touch_hits'
		self.collect_key['auth_cmds'] = 'auth_cmds'
		self.collect_key['auth_errors'] = 'auth_errors'
		self.collect_key['bytes_read'] = 'bytes_read'
		self.collect_key['bytes_written'] = 'bytes_written'
		self.collect_key['limit_maxbytes'] = 'limit_maxbytes'
		self.collect_key['bytes'] = 'bytes'
		self.collect_key['curr_items'] = 'curr_items'
		self.collect_key['total_items'] = 'total_items'
		self.collect_key['evictions'] = 'evictions'
		self.collect_key['reclaimed'] = 'reclaimed'
		self.collect_key['total_malloced'] = 'total_malloced'


