
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

import common.core
import common.rrd_data
import common.remote_data_reader
from data_loader.loader_util import merge_loader
from data_loader.loader_util import sum_loader
from data_loader.loader_util import filter_loader
from data_loader.loader_util import draw_loader


# rrd

def get_rrd_handle(path):

	if not path.endswith('.rrd'):
		path += '.rrd'

	try:
		fd = common.core.get_local_data_handle(path)
		return common.rrd_data.rrd_data(fd.path)
	except:
		return None


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

# for tsdb layer development
def get_tsdb_test_handle(path):
	if not path.endswith('.rrd'):
		path += '.rrd'

	try:
		fd = common.core.get_local_data_handle(path)
		rrd_handle =  common.rrd_data.rrd_data(fd.path)
		return tsdb_test_handle(rrd_handle)

	except:
		return None




def get_remote_handle(host, port, file = None):
	handle = common.remote_data_reader.remote_data_reader(host, port, file)
	return handle

		
# utility
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





