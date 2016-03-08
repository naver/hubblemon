
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
import psutil

import subprocess, shlex # retransmit, tcp_open


class psutil_stat:
	def __init__(self):
		self.key_init()
		self.name = 'psutil'
		self.type = 'rrd'

	def collect_cpu(self, stat):
		cpu = psutil.cpu_times(percpu=False)
		
		stat['psutil_cpu'] = { 'user':cpu.user * 1000,
				'system':cpu.system * 1000,
				'idle':cpu.idle * 1000,
				'nice':cpu.nice * 1000,
				'iowait':cpu.iowait * 1000,
				'irq':cpu.irq * 1000,
				'softirq':cpu.softirq * 1000 }


		cpus = psutil.cpu_times(percpu=True)

		i = 0
		for cpu in cpus:
			stat['psutil_cpu-%d' % i] = { 'user':cpu.user * 1000,
					'system':cpu.system * 1000,
					'idle':cpu.idle * 1000,
					'nice':cpu.nice * 1000,
					'iowait':cpu.iowait * 1000,
					'irq':cpu.irq * 1000,
					'softirq':cpu.softirq * 1000 }
			i += 1

	def collect_memory(self, stat):
		mem = psutil.virtual_memory()
		stat['psutil_memory'] = {	'total':mem.total,
					'available':mem.available,
					'percent':mem.percent,
					'used':mem.used,
					'free':mem.free }

		swap = psutil.swap_memory()
		stat['psutil_swap'] = {	'total':swap.total,
					'used':swap.used,
					'free':swap.free,
					'percent':swap.percent,
					'sin':swap.sin,
					'sout':swap.sout }
	
	def collect_disk(self, stat):
		d = psutil.disk_io_counters(perdisk=False)
		stat['psutil_disk'] = {	'read_count':d.read_count,
					'write_count':d.write_count,
					'read_bytes':d.read_bytes,
					'write_bytes':d.write_bytes,
					'read_time':d.read_time,
					'write_time':d.write_time }
			
		ds = psutil.disk_io_counters(perdisk=True)
		for k, d in ds.items():
			stat['psutil_disk-%s' % k] = {	'read_count':d.read_count,
						'write_count':d.write_count,
						'read_bytes':d.read_bytes,
						'write_bytes':d.write_bytes,
						'read_time':d.read_time,
						'write_time':d.write_time }


	def get_retransmit(self):
		proc1 = subprocess.Popen(shlex.split('netstat -s'), stdout=subprocess.PIPE)
		proc2 = subprocess.Popen(shlex.split('grep retransmited'), stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		proc1.stdout.close()
		out, err = proc2.communicate()
		out = out.decode('utf-8')

		words = out.strip().split(' ')
		retrans = int(words[0])

		return retrans


	def get_tcp_open(self):
		proc1 = subprocess.Popen(shlex.split('netstat -s'), stdout=subprocess.PIPE)
		proc2 = subprocess.Popen(shlex.split('grep established'), stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		proc1.stdout.close()
		out, err = proc2.communicate()
		out = out.decode('utf-8')

		words = out.strip().split(' ')
		tcp_open = int(words[0])

		return tcp_open

	def collect_network(self, stat):
		n = psutil.net_io_counters(pernic=False)
		stat['psutil_net'] = {	'bytes_sent':n.bytes_sent,
				'bytes_recv':n.bytes_recv,
				'packets_sent':n.packets_sent,
				'packets_recv':n.packets_recv,
				'errin':n.errin,
				'errout':n.errout,
				'dropin':n.dropin,
				'dropout':n.dropout,
				} 

		ns = psutil.net_io_counters(pernic=True)
		for k, n in ns.items():
			if k == 'lo': # skip loopback
				continue

			stat['psutil_net-%s' % k] = {	'bytes_sent':n.bytes_sent,
						'bytes_recv':n.bytes_recv,
						'packets_sent':n.packets_sent,
						'packets_recv':n.packets_recv,
						'errin':n.errin,
						'errout':n.errout,
						'dropin':n.dropin,
						'dropout':n.dropout,
						}


	def collect_resource(self, stat):
		retransmit = self.get_retransmit()
		tcp_open = self.get_tcp_open()

		p_count = 0
		t_count = 0
		f_count = 0
		h_count = 0
		ctx_count = 0
		
		for p in psutil.process_iter():
			try:
				p_count += 1
				t_count += p.get_num_threads()
				f_count += p.get_num_fds()
				ctx_count += p.get_ctx_switches()
				h_count += p.get_num_handles()
			except Exception as e:
				continue
		
		stat['psutil_resource'] = { 	'process':p_count,
					'thread':t_count,
					'fd':f_count,
					'handle':h_count,
					'ctx_switch':ctx_count,
					'retransmit':retransmit,
					'tcp_open':tcp_open,
					}

	def collect(self):
		stat = {}
		self.collect_cpu(stat)
		self.collect_memory(stat)
		self.collect_disk(stat)
		self.collect_network(stat)
		self.collect_resource(stat)

		return stat
		

	def create(self):
		stat = self.collect()

		create_map = {}

		for k, v in stat.items():
			prefix = k.split('-')[0]

			if prefix in self.key:
				create_map[k] = self.key[prefix]
				
		create_map['RRA'] = self.key['RRA']
		return create_map

	def key_init(self):
		self.key = {}

		self.key['psutil_cpu'] = [('user', 'DERIVE', 60, '0', 'U'),
				   ('system', 'DERIVE', 60, '0', 'U'),
				   ('idle', 'DERIVE', 60, '0', 'U'),
				   ('nice', 'DERIVE', 60, '0', 'U'),
				   ('iowait', 'DERIVE', 60, '0', 'U'),
				   ('irq', 'DERIVE', 60, '0', 'U'),
				   ('softirq', 'DERIVE', 60, '0', 'U')]

		self.key['psutil_memory'] = [('total', 'GAUGE', 60, '0', 'U'),
				   ('available', 'GAUGE', 60, '0', 'U'),
				   ('percent', 'GAUGE', 60, '0', 'U'),
				   ('used', 'GAUGE', 60, '0', 'U'),
				   ('free', 'GAUGE', 60, '0', 'U')]

		self.key['psutil_swap'] = [('total', 'GAUGE', 60, '0', 'U'),
				   ('used', 'GAUGE', 60, '0', 'U'),
				   ('free', 'GAUGE', 60, '0', 'U'),
				   ('percent', 'GAUGE', 60, '0', 'U'),
				   ('sin', 'DERIVE', 60, '0', 'U'),
				   ('sout', 'DERIVE', 60, '0', 'U')]


		self.key['psutil_disk'] = [('read_count', 'DERIVE', 60, '0', 'U'),
				   ('write_count', 'DERIVE', 60, '0', 'U'),
				   ('read_bytes', 'DERIVE', 60, '0', 'U'),
				   ('write_bytes', 'DERIVE', 60, '0', 'U'),
				   ('read_time', 'DERIVE', 60, '0', 'U'),
				   ('write_time', 'DERIVE', 60, '0', 'U')]


		self.key['psutil_net'] = [('bytes_sent', 'DERIVE', 60, '0', 'U'),
				   ('bytes_recv', 'DERIVE', 60, '0', 'U'),
				   ('packets_sent', 'DERIVE', 60, '0', 'U'),
				   ('packets_recv', 'DERIVE', 60, '0', 'U'),
				   ('errin', 'DERIVE', 60, '0', 'U'),
				   ('errout', 'DERIVE', 60, '0', 'U'),
				   ('dropin', 'DERIVE', 60, '0', 'U'),
				   ('dropout', 'DERIVE', 60, '0', 'U')]

		self.key['psutil_resource'] = [('process', 'GAUGE', 60, '0', 'U'),
				   ('thread', 'GAUGE', 60, '0', 'U'),
				   ('fd', 'GAUGE', 60, '0', 'U'),
				   ('handle', 'GAUGE', 60, '0', 'U'),
				   ('ctx_switch', 'GAUGE', 60, '0', 'U'),
				   ('tcp_open', 'GAUGE', 60, '0', 'U'),
				   ('retransmit', 'DERIVE', 60, '0', 'U')]


		self.key['RRA'] = [('MAX', 0.5, 5/5, (3600/5)*24), 	# 5sec  (to 1day)
				   ('MAX', 0.5, 60/5, (3600/60)*24*7), 	# 1min (to 7day)
				   ('MAX', 0.5, 3600/5, 24*31),		# 1hour (to 1month)
				   ('MAX', 0.5, 3600*3/5, (24/3)*366*3) ]	# 3hour (to 3year)





