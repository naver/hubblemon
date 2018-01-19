
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

from chart.chart_data import chart_data
from data_loader.basic_loader import flot_line_renderer

import threading

def thread_load(ts_start, ts_end, loader, chart_list_list):
	chart_list = loader.load(ts_start, ts_end)
	if len(chart_list) == 0:
		return

	chart_list_list.append(chart_list)


def parallel_load(ts_start, ts_end, loaders):
	threads = []
	chart_list_list = []
	for loader in loaders:
		print(loader)
		th = threading.Thread(target=thread_load, args=(ts_start, ts_end, loader, chart_list_list))
		th.start()
		threads.append(th)

	for th in threads:
		th.join()

	return chart_list_list



class serial_loader:
	def __init__(self, loaders):
		self.loaders = loaders
		self.title = ''

	def load(self, ts_start, ts_end):
		chart_data_list = [] # merged result

		if not isinstance(self.loaders, list):
			print('# loaders (param of merge) should be list')
			return []

		chart_list_list = parallel_load(ts_start, ts_end, self.loaders)

		if self.title != '':
			title_chart = chart_data()
			title_chart.title = self.title
			chart_data_list.append(title_chart)

		for chart_list in chart_list_list:
			chart_data_list += chart_list

		return chart_data_list


class merge_loader:
	def __init__(self, loaders):
		self.loaders = loaders

	def load(self, ts_start, ts_end):
		chart_data_list = [] # merged result

		if not isinstance(self.loaders, list):
			print('# loaders (param of merge) should be list')
			return []

		chart_list_list = parallel_load(ts_start, ts_end, self.loaders)

		chart_len = -1
		for chart_list in chart_list_list:
			if chart_len == -1: # init
				chart_len = len(chart_list)
			elif chart_len != len(chart_list):
				print('# chart list length mismatch')
				return []

		for x in range(0, chart_len):
			new_chart = chart_data()

			for y in range(0, len(chart_list_list)):
				chart = chart_list_list[y][x]
				self.modify(new_chart, chart)
			
			chart_data_list.append(new_chart)

		return chart_data_list

	def modify(self, main, new):
		main.merge(new)
		main.mode = new.mode
		main.renderer = new.renderer


class sum_loader(merge_loader):
	def modify(self, main, new):
		main.sum(new)
		main.mode = new.mode
		main.renderer = new.renderer


class filter_loader:
	def __init__(self, loader, filter):
		self.loader = loader
		self.filter = filter

	def load(self, ts_start, ts_end):
		filtered_list = []
		chart_list = self.loader.load(ts_start, ts_end)

		for chart in chart_list:
			if chart.title in self.filter:
				filtered_list.append(chart)
		
		return filtered_list




class draw_loader:
	def __init__(self, range, datas):
		self.range = range
		self.datas = datas

	def load(self, ts_start, ts_end):
		chart = chart_data()
		chart.mode = 'number'
		chart.renderer = flot_line_renderer()

		for data in self.datas:
			new_data = []
			if isinstance(data, list) or isinstance(data, range):
				iter_x = iter(self.range)
				iter_y = iter(data)

				try:
					while True:
						new_data.append([next(iter_x), next(iter_y)])
				except StopIteration:
					pass

				chart.push_data('', new_data)

			else: # lambda
				for x in self.range:
					new_data.append([x, data(x)])
				
				chart.push_data('', new_data)

		return [chart]


