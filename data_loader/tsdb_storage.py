

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
import common.settings



class tsdb_handle:
	def __init__(self, entity_table, conn_info):
		self.entity_table = entity_table

	def create(self, query):
		pass

	def put(self, query):
		pass

	def read(self, ts_from, ts_to, filter=None):
		toks = self.path.split("/")
		entity = toks[-2]
		table = toks[-1]

		if filter == None:
			query = 'get %s %s *' % (entity, table)
		else:
			pass

		query += ' %d %d' % (ts_from, ts_to)

		print(query)



class tsdb_storage_manager:
	def __init__(self, conn_info):
		self.conn_info = conn_info
		self.name = 'tsdb'
		self.handle=tsdb_handle(None, conn_info)
		self.prev_data={}
		self.gauge_list={}


	def get_handle(self, entity_table):
		try:
			return tsdb_handle(entity_table, self.conn_info)

		except:
			return None


	def get_entity_list(self):
		entity_list = []
		return entity_list
	

	def get_table_list_of_entity(self, entity, prefix):
		table_list = []
		return table_list

	def get_all_table_list(self, prefix):
		table_list = []
		return table_list


	def clone(self):
		return listener_tsdb_plugin(self.path)

	def create_data(self, basedir, name_data_map):
		for name, data in name_data_map.items():                                          
			if name =='RRA':
				continue

			query = "create %s %s" % (basedir, name)
			for attr in data:
				query += " " + attr[0]
				if attr[1] == 'GAUGE':
					self.gauge_list['%s_%s_%s' % (basedir, name, attr[0])] = True

			print(query)
			self.handle.create(query)


	def update_data(self, hostname, timestamp, name_data_map):
		for name, data in name_data_map.items():

			tmp_map = copy.deepcopy(data)
			table_name = '%s_%s' % (hostname, name)

			for attr, val in data.items():
				full_attr = '%s_%s_%s' % (hostname, name, attr)

				if full_attr in self.gauge_list:
					continue
				else:
					if table_name in self.prev_data:
						prev_data = self.prev_data[table_name]
						old = data[attr]
						data[attr] = val - prev_data[attr]

					else:
						self.prev_data[table_name] = tmp_map
						data[attr] = 0

			self.prev_data[table_name] = tmp_map

			query = "put %s %s" % (hostname, name)

			attr_query = ''
			val_query = ''

			for attr, val in data.items():
				attr_query += " " + attr
				val_query += " " + str(val)

			query += attr_query + val_query
			print(query)
			self.handle.put(query)



