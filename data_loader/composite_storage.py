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
from datetime import datetime


class composite_handle:
	def __init__(self, handles):
		self.handles = handles

	def read(self, ts_from, ts_to, filter = None):
		now_ts = datetime.now().timestamp()
		range = now_ts - ts_from

		for handle in self.handles:
			if hasattr(handle, 'time_range'):
				if handle.time_range < range:
					print('time range skip')
					continue

			ret = handle.read(ts_from, ts_to, filter)
			return ret




class composite_storage_manager:
	def __init__(self, mgrs):
		self.mgrs = mgrs

	def optional_init(self):
		for mgr in self.mgrs:
			if hasattr(mgr, 'optional_init'):
				mgr.optional_init()

	def get_handle(self, entity_table):
		handles = []
		for mgr in self.mgrs:
			handle = mgr.get_handle(entity_table)
			if handle != None:
				handles.append(handle)

		return composite_handle(handles)

	def get_entity_list(self):
		return self.mgrs[0].get_entity_list()


	def get_table_list_of_entity(self, entity, prefix):
		return self.mgrs[0].get_table_list_of_entity(entity, prefix)

	def get_all_table_list(self, prefix):
		return self.mgrs[0].get_all_table_list(prefix)

	# update data use member functions, it makes leak because compositeupdate has it
	def update_data(self, entity, timestamp, name_data_map):
		for mgr in self.mgrs:
			ret = mgr.update_data(entity, timestamp, name_data_map)
			if ret == False:
				return False

		return True


	def create_data(self, entity, name_data_map):
		for mgr in self.mgrs:
			ret = mgr.create_data(entity, name_data_map)
			if ret == False:
				return False

		return True



