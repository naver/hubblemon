import os
from datetime import datetime
import rrdtool

from common.rrd_data import rrd_data
from chart.chart_data import chart_data

              
class rrd_loader:
	def __init__(self, path, filter, title=''):
		self.path = path
		self.filter = filter

		if path:
			if not path.endswith('.rrd'):
				path += '.rrd'

			self.rrd = rrd_data(path)

		self.title = title
		self.data = {}

		self.ts_start = None
		self.ts_end = None

	def count(self, name):
		if not self.path:
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
		if not self.path:
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
		if not self.path:
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
		if not self.path:
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

		if not self.path:
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

		elif isinstance(titles, tuple) and hasattr(titles[0], '__call__'):
			func = titles[0]
			title = titles[1]

			data = []
			ts_count = 0
			for item in items:
				ts = ts_start + ts_count * ts_step
				ts_count += 1

				input = {}
				for name, idx in tmap.items():
					input[name] = item[idx]

				try:
					output = [ts, func(input)]
				except:
					output = None

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

		if not self.path:
			return []

		#info = self.rrd.info(self.rrd.filename)

		ret = self.rrd.read(ts_start, ts_end)
		#print ('result: ', ret)

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






