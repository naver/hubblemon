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

import os, sys, time
import imp, rrdtool



class rrd_worker:
	def __init__(self, fifo_path):
		self.fifo_path = fifo_path

	def do_something(self):
		print('### do something invoked')
		start_timestamp = time.time()
		count = 0
		fifo = open(self.fifo_path, 'r')
		buffer = ''

		while True:
			before = time.time()
			tmp = fifo.read(4096)
			after = time.time()

			#print('>>> read: ', tmp)
			length = len(tmp)
			buffer += tmp

			while True:
				idx = buffer.find('\n')
				if idx < 0:
					break

				line = buffer[:idx]
				#print('>>> line: ', line)
				buffer = buffer[idx+1:]
				toks = line.split(' ', 2)

				if toks[0] == 'update':
					#print('update %s %s' % (toks[1], toks[2]))
					try:
						rrdtool.update(toks[1], toks[2])
					except rrdtool.OperationalError as e:
						#print(e)
						continue
					except Exception as e:
						print(e)
						continue
				else:
					pass

			if (after - before) > 0.1:
				time.sleep(1)

			count += 1
			if count > 50000:
				print('quit by overcounting, running sec: %d' % (time.time() - start_timestamp))
				sys.exit()

	def do_fork(self):
		print('# rrd_worker do fork')
		pid = os.fork()
		if pid == 0: # child
			while True:
				pid = os.fork()

				if pid == 0: # child
					self.do_something()
				else:
					os.wait()
		else:
			return # return to caller process



class rrd_handle:
	def __getattr__(self, name):
		return getattr(rrdtool, name)

	def __init__(self, filename, fifo, start=int(time.time()) - 10, step=5):
		self.filename = filename
		self.fifo = fifo
		self.start = start
		self.step = step
		self.DS = {}
		self.RRA = []
		self.update_count = 0


	def put_ds(self, name, type, health, min, max):
		self.DS[name] = 'DS:%s:%s:%s:%s:%s' % (name, type, str(health), str(min), str(max))
	
	def put_rra(self, type, default, num, max_rec):
		rra = 'RRA:%s:%f:%d:%d' % (type, default, num, max_rec)
		print(rra)
		self.RRA.append(rra)

	def create(self):
		args = []
		keys = list(self.DS.keys())
		keys.sort()

		for key in keys:
			#print('>> ' + key)
			args.append(self.DS[key])
	
		args += self.RRA
		print('## rrd create - %s(%d items), start: %d, step: %d' % (self.filename, len(self.DS), self.start, self.step))
		print(args)
		try:
			rrdtool.create(self.filename, '--start', '%d' % self.start, '--step', '%d' % self.step, *args)
		except rrdtool.OperationalError as e:
			print(e)


	def update(self, *params):
		result = ''
		count = 0
		#print(params)

		if len(params) == 2 and isinstance(params[1], dict): # dict input
			data = params[1]
			keys = list(data.keys())
			keys.sort()

			result = '%d:' % params[0]

			count = len(keys)
			for key in keys:
				#print('update>> ' + key)
				result += '%d:' % data[key]

		else:
			count = len(params) - 1
			for p in params:
				result += '%d:' % p

		result = result[0:-1]
		
		#print ('## rrd update %s (%d): %s' % (self.filename, count, result))

		#ret = rrdtool.update(self.filename, result)
		try:
			self.fifo.write('update %s %s\n' % (self.filename, result))
		except Exception as e:
			print('## pipe write excpetion')
			print(e)

	def read(self, ts_from, ts_to, filter = None):
		ret = rrdtool.fetch(self.filename, 'MAX', '-s', str(ts_from), '-e', str(ts_to))
		return ret





class rrd_storage_manager:
	def __init__(self, storage_path):
		if storage_path[0] != '/':
			hubblemon_path = os.path.join(os.path.dirname(__file__), '..') 
			storage_path = os.path.join(hubblemon_path, storage_path)

		self.storage_path = storage_path
		self.fifo_path = os.path.join(storage_path, 'rrd_fifo')

		try:
			os.mkfifo(self.fifo_path)
		except FileExistsError as e:
			pass

		self.fifo = None

	def optional_init(self):
		worker = rrd_worker(self.fifo_path)
		worker.do_fork()

		time.sleep(0.2)
		self.fifo = open(self.fifo_path, 'w')

	def get_handle(self, entity_table):
		if not entity_table.endswith('.rrd'):
			entity_table += '.rrd'

		try:
			fd = self.get_local_file_handle(entity_table)
			return rrd_handle(fd.path, self.fifo)
		except:
			return None

	def get_local_file_handle(self, entity_table):
		entity_path = os.path.join(self.storage_path, entity_table)

		fd = open(entity_path)
		fd.path = entity_path
		return fd


	def get_entity_list(self):
		entity_list = []

		for entity in os.listdir(self.storage_path):
			entity_path = os.path.join(self.storage_path, entity)

			if os.path.isdir(entity_path):
				entity_list.append(entity)

		return entity_list


	def get_table_list_of_entity(self, entity, prefix):
		table_list = []

		entity_path = os.path.join(self.storage_path, entity)

		for table in os.listdir(entity_path):
			if table.startswith(prefix):
				table_list.append(table)

		return table_list



	def get_all_table_list(self, prefix):
		table_list = []
		for entity in os.listdir(self.storage_path):
			entity_path = os.path.join(self.storage_path, entity)

			if os.path.isdir(entity_path):
				for table in os.listdir(entity_path):
					if table.startswith(prefix):
						table_list.append(entity + '/' + table)						

		return table_list

	# update data use member functions, it makes leak because rrdupdate has it
	def update_data(self, entity, timestamp, name_data_map):
		for table, data in name_data_map.items(): # for each section
			try:
				table += '.rrd'
				table = table.replace('/', '_') # some stat name include /
				entity_table = os.path.join(entity, table)
				handle = self.get_handle(entity_table)
				handle.update(timestamp, data)
			except Exception as e:
				print(e)
				print('on update table %s, %s (item: %d)' % (entity, table + '.rrd', len(data)))
				print(data)

		return True


	def create_data(self, entity, name_data_map):
		entity_path = os.path.join(self.storage_path, entity)

		if not os.path.exists(entity_path): # not exists, create folder
			os.makedirs(entity_path)

		rra_list = []
		if 'RRA' in name_data_map:
			rra_list = name_data_map['RRA']	

		for table, data in name_data_map.items(): # for each section
			if table == 'RRA':		# already read
				continue

			table += '.rrd'
			table = table.replace('/', '_') # some stat name include /
			entity_table = os.path.join(entity_path, table)

			if not os.path.exists(entity_table):
				handle = rrd_handle(entity_table, None)

				assert (isinstance(data, list))
				for item in data:
					handle.put_ds(*item)

				for rra in rra_list:
					handle.put_rra(*rra)

				handle.create()

		return True

