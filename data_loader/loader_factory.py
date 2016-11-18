
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

import common.rrd_data
import common.remote_data_reader
import common.sql_data
from data_loader.loader_util import serial_loader
from data_loader.loader_util import merge_loader
from data_loader.loader_util import sum_loader
from data_loader.loader_util import filter_loader
from data_loader.loader_util import draw_loader


# rrd

class rrd_storage_manager:
	def __init__(self, hubblemon_path):
		self.hubblemon_path = hubblemon_path

	def get_handle(self, base, path):
		if not path.endswith('.rrd'):
			path += '.rrd'

		try:
			fd = self.get_local_data_handle(base, path)
			return common.rrd_data.rrd_data(fd.path)
		except:
			return None

	def get_local_data_handle(self, base, path):
		if base[0] != '/':
			base = os.path.join(self.hubblemon_path, base)
		
		path = os.path.join(base, path)

		fd = open(path)
		fd.path = path
		return fd


	def get_client_list(self, base):
		client_list = []

		if base[0] != '/':
			base = os.path.join(self.hubblemon_path, base)

		for dir in os.listdir(base):
			dir_path = os.path.join(base, dir)

			if os.path.isdir(dir_path):
				client_list.append(dir)

		return client_list

	def get_data_of_client(self, base, client, name):
		if base[0] != '/':
			base = os.path.join(self.hubblemon_path, base)

		path = os.path.join(base, client)

		for file in os.listdir(path):
			if file == name:
				break
		return file


	def get_data_list_of_client(self, base, client, prefix):
		data_list = []

		if base[0] != '/':
			base = os.path.join(self.hubblemon_path, base)

		path = os.path.join(base, client)

		for file in os.listdir(path):
			if file.startswith(prefix):
				data_list.append(file)

		return data_list



	def get_all_data_list(self, base, prefix):
		data_list = []
		for dir in os.listdir(base):
			dir_path = os.path.join(base, dir)

			if os.path.isdir(dir_path):
				for file in os.listdir(dir_path):
					if file.startswith(prefix):
						data_list.append(dir + '/' + file)						

		return data_list


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

	def get_handle(self, base, path):
		if not path.endswith('.rrd'):
			path += '.rrd'

		try:
			fd = self.get_local_data_handle(base, path)
			rrd_handle =  common.rrd_data.rrd_data(fd.path)
			return tsdb_test_handle(rrd_handle)

		except:
			return None


class sql_storage_manager:
	def __init__(self, db_path):
			self.db_path = db_path
			self.sql_manager=common.sql_data.sql_gw(db_path)


	def get_handle(self, base, path):
			try:
					return common.sql_data.sql_gw(path)

			except:
					return None


	def get_client_list(self, param):
			client_list = []
			query = "SELECT name FROM sqlite_master WHERE type='table'"
			table_list =self.sql_manager.select(query);
			for table in table_list:
				client_name = table[0].split("_")[1]
				if client_name not in client_list:
					client_list.append(client_name)

			#print ("client_list:", client_list)
			return client_list
	
	def get_data_of_client(self, param, client, name):
			query = "SELECT name FROM sqlite_master WHERE type='table'"
			table_list =self.sql_manager.select(query);
			target_name ="D_"+client+"_"+name
			for table in table_list:
				table=table[0]
				if (table==target_name):
					break
			#print ("data_client: ", table)
			return table 
			

	def get_data_list_of_client(self, param, client, prefix):
			data_list = []
			# select name from sqlite_master where type = 'table' and name like 'D_%s_%s%%' % (client, prefix)
			query = "SELECT name FROM sqlite_master WHERE type='table'"
			table_list =self.sql_manager.select(query);
			target_name ="D_"+client+"_"+prefix
			for table in table_list:
				table=table[0]
				if table.startswith(target_name):
					data_list.append(table)
			#print ("data_list_of_client_list:", data_list)
			return data_list

	def get_all_data_list(self, param, prefix):
			data_list = []
			# select name from sqlite_master where type = 'table' and name like 'D_%%_%s%%' % (prefix)
			query = "SELECT name FROM sqlite_master WHERE type='table'"
			table_list =self.sql_manager.select(query);
			for table in table_list:
				table=table[0]
				client_name = table.split("_")[1]
				target_name = "D_"+client_name+"_"+prefix
				if table.startswith(target_name):
					data_list.append(table)
			#print ("all_data_list:", data_list)
			return data_list




class remote_manager:
	def __init__(self):
		pass

	def get_handle(host, port, file = None):
		handle = common.remote_data_reader.remote_data_reader(host, port, file)
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





