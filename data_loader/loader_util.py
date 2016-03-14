
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

class merge_loader:
	def __init__(self, loaders):
		self.loaders = loaders

	def load(self, ts_start, ts_end):
		chart_data_list = [] # merged result
		chart_list_list = []

		chart_len = -1
		for loader in self.loaders:
			chart_list = loader.load(ts_start, ts_end)
			if len(chart_list) == 0:
				continue

			chart_list_list.append(chart_list)

			if chart_len == -1: # init
				chart_len = len(chart_list)
			elif chart_len != len(chart_list):
				print('# chart list length mismatch')
				return []

		
		for x in range(0, chart_len):
			new_chart = chart_data()

			for y in range(0, len(chart_list_list)):
				chart = chart_list_list[y][x]
				new_chart.merge(chart)
				new_chart.mode = chart.mode
				new_chart.renderer = chart.renderer
			
			chart_data_list.append(new_chart)

		return chart_data_list





class sum_loader:
	def __init__(self, loaders):
		self.loaders = loaders

	def load(self, ts_start, ts_end):
		chart_data_list = [] # merged result
		chart_list_list = []

		chart_len = -1
		for loader in self.loaders:
			chart_list = loader.load(ts_start, ts_end)
			if len(chart_list) == 0:
				continue

			chart_list_list.append(chart_list)

			if chart_len == -1: # init
				chart_len = len(chart_list)
			elif chart_len != len(chart_list):
				print('# chart list length mismatch')
				return []

		
		for x in range(0, chart_len):
			new_chart = chart_data()
			
			for y in range(0, len(chart_list_list)):
				chart = chart_list_list[y][x]
				new_chart.sum(chart)
				new_chart.mode = chart.mode
				new_chart.renderer = chart.renderer

			chart_data_list.append(new_chart)

		return chart_data_list



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


