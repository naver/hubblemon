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
import copy
import sqlite3

#
# moved from listener_sql_plugin.py & sql_data.py of harry2636
#

def get_sql_handle(entity_table, conn_info):
	# change if you want another db
	return sqlite_handle(entity_table, conn_info)


class sqlite_handle:
	def __init__(self, entity_table, conn_info):
		self.entity_table=entity_table

		if conn_info[0] != '/':
			hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
			conn_info = os.path.join(hubblemon_path, conn_info)

		self.conn_info = conn_info

		self.handle=sqlite3.connect(self.conn_info, check_same_thread=False, isolation_level=None)
		

	def execute(self, query):
		#print(query)
		cursor = self.handle.cursor()
		cursor.execute(query)

	def create(self, query):
		#print(query)
		cursor = self.handle.cursor()
		cursor.execute(query)

	def select(self, query):
		#print(query)
		cursor = self.handle.cursor()
		cursor.execute(query)
		return cursor.fetchall()

	def insert(self, query):
		#print(query)
		cursor = self.handle.cursor()
		cursor.execute(query)

	def read(self, ts_from, ts_to, filter=None):
		toks = self.entity_table.split("/")
		entity = toks[0]
		table = toks[1]

		table_name = '"D_%s_%s"' % (entity, table)
		query = "SELECT * FROM " + table_name
		cursor=self.handle.cursor()
		cursor.execute(query)
		names = [description[0] for description in cursor.description]
		names = tuple(names[1:])


		query += " WHERE "
		cond = "timestamp>=" + str(ts_from) + " and " + "timestamp<" +str(ts_to)
		query = query + cond

		result =self.select(query)
		result = ('#timestamp', names, result)
		#print(result)
		return result



class sql_storage_manager:
	def __init__(self, conn_info):
		self.conn_info = conn_info
		self.handle=get_sql_handle(None, conn_info)
		self.name = 'sql'                                                                 

		self.prev_data={}
		self.gauge_list={}


	def get_handle(self, entity_table):
		try:
			return get_sql_handle(entity_table, self.conn_info)

		except:
			return None


	def get_entity_list(self):
		entity_list = []
		query = "SELECT name FROM sqlite_master WHERE type='table'"
		dbtable_list =self.handle.select(query);
		for table in dbtable_list:
			entity_name = table[0].split("_")[1]
			if entity_name not in entity_list:
				entity_list.append(entity_name)

		#print ("entity_list:", entity_list)
		return entity_list
	

	def get_table_list_of_entity(self, entity, prefix):
		table_list = []
		# select name from sqlite_master where type = 'table' and name like 'D_%s_%s%%' % (entity, prefix)
		query = "SELECT name FROM sqlite_master WHERE type='table'"
		dbtable_list =self.handle.select(query);
		target_name ='D_%s_%s' % (entity, prefix)
		for table in dbtable_list:
			table=table[0]
			if table.startswith(target_name):
				toks = table.split('_', 2)
				table = toks[-1]
				table_list.append(table)
		#print ("table_list_of_entity:", table_list)
		return table_list

	def get_all_table_list(self, prefix):
		table_list = []
		# select name from sqlite_master where type = 'table' and name like 'D_%%_%s%%' % (prefix)
		query = "SELECT name FROM sqlite_master WHERE type='table'"
		dbtable_list =self.handle.select(query);
		for table in dbtable_list:
			table=table[0]
			entity = table.split("_")[1]
			target_name = 'D_%s_%s' % (entity, prefix)
			if table.startswith(target_name):
				toks = table.split('_', 2)
				table = toks[-1]
				table_list.append(table)
		#print ("all_table_list:", table_list)
		return table_list


	def create_data(self, entity, name_data_map):
		for table, data in name_data_map.items():                                          
			if table =='RRA':                                                              
				continue                                                                  
			
			table_name = '"D_%s_%s"' % (entity, table)
			check_table ="SELECT count(*) FROM sqlite_master WHERE type='table' AND name=" + table_name
			is_exist=self.handle.select(check_table)[0][0]
			query = "CREATE TABLE " + table_name
			attr_query= "(timestamp BIGINT PRIMARY KEY"                                   
			for attr in data:
				tmp_query=", " + attr[0] + " BIGINT"                                       
				attr_query= attr_query + tmp_query
				if attr[1] == 'GAUGE':
					self.gauge_list['%s_%s' % (table_name, attr[0])] = True

			query = query+attr_query+")"
			if is_exist==0:
				self.handle.create(query)

		return True


	def update_data(self, entity, timestamp, name_data_map):
		for table, data in name_data_map.items():

			table_name = '"D_%s_%s"' % (entity, table)
			tmp_map = copy.deepcopy(data)

			for attr, val in data.items():
				full_attr = '%s_%s' % (table_name, attr)
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

			query = "INSERT INTO " + table_name
			attr_query ="("+"timestamp"
			val_query=" VALUES(" + str(int(timestamp))

			for attr, val in data.items():
				attr_query = attr_query + ", " + attr
				val_query = val_query + ", " + str(val)

			attr_query += ")"
			val_query += ")"

			query = query+ attr_query + val_query
			self.handle.insert(query)

		return True




