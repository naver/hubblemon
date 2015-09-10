
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
from chart.chart_data import chart_data

              
class basic_loader:
	def __init__(self, handle, filter, title=''):
		self.filter = filter

		self.handle = handle

		self.title = title
		self.data = {}

		self.ts_start = None
		self.ts_end = None

	def count(self, name):
		if self.handle is None:
			return 0

		sum = 0

		if name in self.data:
			chart = self.data[name]
			item = chart.items[0] # should be 1 metric 

			for ts_value in item.data:
				if ts_value == None:
					continue

				sum += ts_value[1]
		return sum

	def avg(self, name):
		if self.handle is None:
			return 0

		sum = 0
		avg = 0

		if name in self.data:
			chart = self.data[name]
			item = chart.items[0] # should be 1 metric 

			for ts_value in item.data:
				if ts_value == None:
					continue

				sum += ts_value[1]

			avg = sum / len(item.data)

		return avg

	def max(self, name):
		if self.handle is None:
			return 0

		max = 0

		if name in self.data:
			chart = self.data[name]
			item = chart.items[0] # should be 1 metric 

			for ts_value in item.data:
				if ts_value == None:
					continue

				if ts_value[1] > max:
					max = ts_value[1]
		return max

	def min(self, name):
		if self.handle is None:
			return 0

		min = sys.maxsize

		if name in self.data:
			chart = self.data[name]
			item = chart.items[0] # should be 1 metric 

			for ts_value in item.data:
				if ts_value == None:
					continue

				if ts_value[1] < min:
					min = ts_value[1]
		return min

	def parse(self, ts_start, ts_end):
		self.ts_start = ts_start
		self.ts_end = ts_end

		if self.handle is None:
			return

		chart_data_list = self.load(ts_start, ts_end)

		self.data = {}
		for chart_data in chart_data_list:
			self.data[chart_data.title] = chart_data

	def make_chart(self, titles, tmap, items, ts_start, ts_step):
		if isinstance(titles, str):
			idx = tmap[titles]
			data = []
			ts_count = 0
			for item in items:
				ts = ts_start + ts_count * ts_step
				ts_count += 1

				if item[idx] == None:
					data.append(None)
					continue

				data.append([ts, item[idx]])

			return [(titles, data)]

		elif isinstance(titles, tuple):
			title = ''

			for func in titles:
				if not hasattr(func, '__call__'):
					title = func

			data = []
			ts_count = 0
			input = { 'prev':{} }

			for item in items:
				ts = ts_start + ts_count * ts_step
				ts_count += 1

				for name, idx in tmap.items():
					input[name] = item[idx]

				for func in titles: # only last function result is saved
					if hasattr(func, '__call__'):
						try:
							output = [ts, func(input)]
						except:
							output = None

				prev = input['prev']
				for k, v in input.items():
					if k == 'prev':
						continue

					if k not in prev:
						prev[k] = []
					
					prev[k].append(v)

				data.append(output)

			return [(title, data)]

		elif isinstance(titles, list):
			ret = []
			for title in titles:
				ret += self.make_chart(title, tmap, items, ts_start, ts_step)
		
			return ret

		return []


	def load(self, ts_start, ts_end):
		self.ts_start = ts_start
		self.ts_end = ts_end

		if self.handle is None:
			return []

		#info = self.rrd.info(self.rrd.filename)

		ret = self.handle.read(ts_start, ts_end)
		#print ('result: ', ret)
		# ((ts_start, ts_end, step), (metric1, metric2, metric3), [(0, 0, 0), (1, 1, 1)....])

		ts_start = ret[0][0] * 1000
		ts_step = ret[0][2] * 1000
		
		names = ret[1]
		items = ret[2]

		tmap = {}
		for i in range(0, len(names)):
			tmap[names[i]] = i
			

		chart_data_list = []
		if self.title != '':
			title_chart = chart_data()
			title_chart.title = self.title
			chart_data_list.append(title_chart)

		if self.filter == None: 	# select all
			self.filter = names

		#print(self.filter)
		for titles in self.filter: # for each chart
			new_chart = chart_data()

			tmp_list = self.make_chart(titles, tmap, items, ts_start, ts_step)
			for tmp in tmp_list:
				new_chart.push_data(tmp[0], tmp[1])

			chart_data_list.append(new_chart) 

		return chart_data_list






