
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

import os

import common.rrd_handle
import common.remote_handle
import common.sql_handle
import common.tsdb_handle
from data_loader.loader_util import serial_loader
from data_loader.loader_util import merge_loader
from data_loader.loader_util import sum_loader
from data_loader.loader_util import filter_loader
from data_loader.loader_util import draw_loader

# tsdb storage
# partition_info not used
class tsdb_storage_manager:
	def __init__(self, conn_info):
			self.conn_info = conn_info
			self.handle=common.tsdb_handle.tsdb_handle(conn_info)


	def get_handle(self, partition_info, entity_table):
			try:
					return common.tsdb_handle.tsdb_handle(entity_table)

			except:
					return None


	def get_entity_list(self, param):
			entity_list = []
			return entity_list
	

	def get_table_list_of_entity(self, partition_info, entity, prefix):
			table_list = []
			return table_list

	def get_all_table_list(self, partition_info, prefix):
		table_list = []
		return table_list



# rrd
# use patition_info as basedir (to use different physical drive)
class rrd_storage_manager:
	def __init__(self, hubblemon_path):
		self.hubblemon_path = hubblemon_path

	def get_handle(self, partition_info, path):
		if not path.endswith('.rrd'):
			path += '.rrd'

		try:
			fd = self.get_local_file_handle(partition_info, path)
			return common.rrd_handle.rrd_handle(fd.path)
		except:
			return None

	def get_local_file_handle(self, partition_info, path):
		if partition_info[0] != '/':
			partition_info = os.path.join(self.hubblemon_path, partition_info)
		
		path = os.path.join(partition_info, path)

		fd = open(path)
		fd.path = path
		return fd


	def get_entity_list(self, partition_info):
		entity_list = []

		if partition_info[0] != '/':
			partition_info = os.path.join(self.hubblemon_path, partition_info)

		for dir in os.listdir(partition_info):
			dir_path = os.path.join(partition_info, dir)

			if os.path.isdir(dir_path):
				entity_list.append(dir)

		return entity_list


	def get_table_list_of_entity(self, partition_info, entity, prefix):
		table_list = []

		if partion_info[0] != '/':
			partition_info = os.path.join(self.hubblemon_path, partition_info)

		path = os.path.join(partition_info, entity)

		for file in os.listdir(path):
			if file.startswith(prefix):
				table_list.append(file)

		return table_list



	def get_all_table_list(self, partition_info, prefix):
		table_list = []
		for dir in os.listdir(partition_info):
			dir_path = os.path.join(partition_info, dir)

			if os.path.isdir(dir_path):
				for file in os.listdir(dir_path):
					if file.startswith(prefix):
						table_list.append(dir + '/' + file)						

		return table_list


# test for tsdb storage
class tsdb_test_handle:
	def __init__(self, rrd):
		self.rrd = rrd

	def read(self, start, end):
		ret = self.rrd.read(start, end)
		# ((start, end, step), (metric1, metric2, metric3), [(0, 0, 0), (1, 1, 1), ...]
		range = ret[0]
		start = range[0]
		step = range[2]

		names = ret[1]
		items = ret[2]

		ts = start
		result = []
		for item in items:
			new_item = (ts,) + item
			result.append(new_item)
			ts += step
		
		return ('#timestamp', names, result)


class tsdb_test_storage_manager(rrd_storage_manager):
	def __init__(self, hubblemon_path):
		self.hubblemon_path = hubblemon_path
		rrd_storage_manager.__init__(self, hubblemon_path)

	def get_handle(self, partition_info, path):
		if not path.endswith('.rrd'):
			path += '.rrd'

		try:
			fd = self.get_local_file_handle(partition_info, path)
			rrd_handle =  common.rrd_handle.rrd_handle(fd.path)
			return tsdb_test_handle(rrd_handle)

		except:
			return None


# partition_info not used
class sql_storage_manager:
	def __init__(self, db_path):
			self.db_path = db_path
			self.handle=common.sql_handle.sql_handle(db_path)


	def get_handle(self, partition_info, path):
			try:
					return common.sql_handle.sql_handle(path)

			except:
					return None


	def get_entity_list(self, param):
			entity_list = []
			query = "SELECT name FROM sqlite_master WHERE type='table'"
			dbtable_list =self.handle.select(query);
			for table in dbtable_list:
				entity_name = table[0].split("_")[1]
				if entity_name not in entity_list:
					entity_list.append(entity_name)

			#print ("entity_list:", entity_list)
			return entity_list
	

	def get_table_list_of_entity(self, partition_info, entity, prefix):
			table_list = []
			# select name from sqlite_master where type = 'table' and name like 'D_%s_%s%%' % (entity, prefix)
			query = "SELECT name FROM sqlite_master WHERE type='table'"
			dbtable_list =self.handle.select(query);
			target_name ="D_"+entity+"_"+prefix
			for table in dbtable_list:
				table=table[0]
				if table.startswith(target_name):
					table_list.append(table)
			#print ("table_list_of_entity:", table_list)
			return table_list

	def get_all_table_list(self, partition_info, prefix):
			table_list = []
			# select name from sqlite_master where type = 'table' and name like 'D_%%_%s%%' % (prefix)
			query = "SELECT name FROM sqlite_master WHERE type='table'"
			dbtable_list =self.handle.select(query);
			for table in dbtable_list:
				table=table[0]
				entity_name = table.split("_")[1]
				target_name = "D_"+entity_name+"_"+prefix
				if table.startswith(target_name):
					table_list.append(table)
			#print ("all_table_list:", table_list)
			return table_list




class remote_manager:
	def __init__(self):
		pass

	def get_handle(host, port, file = None):
		handle = common.remote_handle.remote_handle(host, port, file)
		return handle

		
# utility
def serial(loaders):
	ret = serial_loader(loaders)
	return ret

def merge(loaders):
	ret = merge_loader(loaders)
	return ret
	
def sum_all(loaders):
	ret = sum_loader(loaders)
	return ret

def filter(loaders, *filters):
	ret = filter_loader(loaders, filters)
	return ret
	
def draw(range, *datas):
	ret = draw_loader(range, datas)
	return ret


# add functions to use at chart_page





