

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

import os, sys, time, copy
from data_loader.tsdb_client import tsClient
from data_loader.tsdb_client import tsException



class tsdb_handle:
	def __init__(self, entity_table, conn_info, time_range):
		self.entity_table = entity_table
		self.conn_info = conn_info
		self.time_range = time_range

		self.cl = tsClient(False)
		#self.cl = tsClient()
		self.connect()

	def connect(self):
		self.cl.connect(self.conn_info)

	def disconnect(self):
		self.cl.disconnect()

	def create(self, query):
		#print(query)

		try:
			cur = self.cl.request(query)
			ret = False

			if cur != None:
				ret = cur.next()

		except Exception as e:
			print(e)
			self.disconnect()
			self.connect()
			return False

		return ret

	def put(self, query):
		#print(query)

		try:
			cur = self.cl.request(query)
			ret = False
			if cur != None:
				ret = cur.next()

		except Exception as e:
			print(e)
			self.disconnect()
			self.connect()
			return False

		return ret

	def get(self, query):
		#print(query)

		try:
			cur = self.cl.request(query)
		except Exception as e:
			print(e)
			self.disconnect()
			self.connect()
			return None

		return cur

	def request(self, query):
		#print(query)

		cur = self.cl.request(query)
		return cur

	def read(self, ts_from, ts_to, filter=None):
		toks = self.entity_table.split("/")
		entity = toks[0]
		table = toks[1]

		if filter == None:
			query = 'get %s %s *' % (entity, table)
		else:
			pass

		query += ' %d %d' % (ts_from, ts_to)

		#print(query)
		cur = self.get(query)

		items = []
		while True:
			ret = cur.next()
			if ret == None:
				break

			if ret.ts == 0: # error
				break

			items.append([ret.ts] + ret.value)
			
		ret = ('#timestamp', cur.names[1:], items)
		#print(ret)
		return ret
		



class tsdb_storage_manager:
	def __init__(self, conn_info, time_range = 3600):
		self.conn_info = conn_info
		self.name = 'tsdb'
		self.prev_data={}
		self.gauge_list={}
		self.time_range = time_range
		self.cycle_size = time_range / 5
		self.handle=tsdb_handle(None, conn_info, time_range)


	def get_handle(self, entity_table):
		try:
			return tsdb_handle(entity_table, self.conn_info, self.time_range)

		except:
			return None


	def get_entity_list(self):
		entity_list = []

		cur = self.handle.request('list * psutil_cpu')
		while True:
			ret = cur.next()
			if ret == None:
				break

			toks = ret.value.split(' ')
			entity_list.append(toks[0])
			
		return entity_list
	

	def get_table_list_of_entity(self, entity, prefix):
		table_list = []

		cur = self.handle.request('list %s %s*' % (entity, prefix))
		while True:
			ret = cur.next()
			if ret == None:
				break

			toks = ret.value.split(' ')
			table_list.append(toks[1])

		return table_list

	def get_all_table_list(self, prefix):
		table_list = []

		cur = self.handle.request('list * %s*' % prefix)
		while True:
			ret = cur.next()
			if ret == None:
				break

			toks = ret.value.split(' ')
			table_list.append('%s/%s' % (toks[0], toks[1]))

		return table_list


	def clone(self):
		return listener_tsdb_plugin(self.path)

	def create_data(self, entity, name_data_map):
		#print(name_data_map)
		for table, data in name_data_map.items():                                          
			if table =='RRA':
				continue

			query = "create %s %s %d" % (entity, table, self.cycle_size)
			for attr in data:
				query += " " + attr[0]
				if attr[1] == 'GAUGE':
					self.gauge_list['%s_%s_%s' % (entity, table, attr[0])] = True

			ret = self.handle.create(query)
			if ret == False:
				return False

		return True

	def update_data(self, entity, timestamp, name_data_map):
		for table, data in name_data_map.items():

			tmp_map = copy.deepcopy(data)
			table_name = '%s_%s' % (entity, table)

			for attr, val in data.items():
				full_attr = '%s_%s_%s' % (entity, table, attr)

				if full_attr in self.gauge_list:
					continue
				else:
					if table_name in self.prev_data and '#timestamp' in self.prev_data:
						prev_data = self.prev_data[table_name]
						prev_timestamp = self.prev_data['#timestamp']
						if timestamp - prev_timestamp == 0:
							print('# abnormal timestamp %d of %s' % (timestamp, entity))
							data[attr] = 0

						#data[attr] = (val - prev_data[attr]) / (timestamp - prev_timestamp) # 1sec average
						data[attr] = (val - prev_data[attr]) / 5
					else:
						data[attr] = 0

			self.prev_data[table_name] = tmp_map

			query = "put %s %s" % (entity, table)

			attr_query = ''
			val_query = ' %d' % timestamp

			for attr, val in data.items():
				attr_query += " " + attr
				val_query += " %d" % val

			query += attr_query + val_query
			ret = self.handle.put(query)
			#print(ret)
			if ret == False:
				self.prev_data['#timestamp'] = timestamp
				return False

		self.prev_data['#timestamp'] = timestamp
		return True



