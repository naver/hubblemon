
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

import sys, time

class chart_item:
	def __init__(self, title, data):
		self.title = title
		self.data =  data

	def sum(self, rhs):
		data_len = min(len(self.data), len(rhs.data))

		for idx in range(0, data_len):
			if self.data[idx] == None:
				self.data[idx] = rhs.data[idx]
			elif rhs.data[idx] == None:
				continue # keep current
			else:
				self.data[idx][1] += rhs.data[idx][1] # 0: ts, 1: value
				
  
class chart_data:
	def __init__(self):
		self.items = []
		self.title = ''
		self.mode = 'time' # or number
		self.renderer = None

	def render(self):
		if self.renderer:
			return self.renderer.render(self)

		return 'Renderer is None'

	def sum(self, rhs):
		if len(self.items) == 0: # init
			self.title = rhs.title
			self.items = rhs.items
			return

		if len(self.items) != len(rhs.items):
			print('# invalid merge len')
			return

		items_len = len(self.items)
		for idx in range(0, items_len):
			self.items[idx].sum(rhs.items[idx])
			
	def merge(self, rhs):
		if len(self.items) == 0: # init
			self.title = rhs.title

		self.items += rhs.items
		

	def push_data(self, title, data):
		if self.title != '':
			self.title += ', '
		self.title += title

		self.items.append(chart_item(title, data))

	def adjust_time(self, diff):
		diff *= 1000 # sec to msec

		for item in self.items:
			for t_v in item.data:
				if t_v and t_v[0]:
					#print(t_v)
					t_v[0] += diff
					#print(t_v)
					
	def adjust_timezone(self):
		lt = time.localtime()
		delta = lt.tm_gmtoff
		self.adjust_time(delta)

	def sampling(self, max_resolution):
		new_items = []
		for item in self.items:
			#print('## len: %d' % len(item.data))

			if len(item.data) < (max_resolution * 2):
				new_items.append(item)
			else:
				per = int(len(item.data) / max_resolution)
				#print('#### per: %d' % per)
				new_data = []

				min = [0, sys.maxsize]
				max = [0, -sys.maxsize]
				idx = 0
				for data in item.data:
					if data != None and data[1] > max[1]:
						max = data
					if data != None and data[1] < min[1]:
						min = data

					idx += 1
					if idx % per == 0 and min[0] > 0:
						#print('## %d, %d' % (idx, per))

						if min[0] < max[0]:
							new_data.append(min)
							if max[1] != min[1]: # if min == max skip (do not append)
								new_data.append(max)
						else:
							new_data.append(max)
							if max[1] != min[1]: # if min == max skip (do not append)
								new_data.append(min)
						
					
						min = [0, sys.maxsize]
						max = [0, -sys.maxsize]


				if len(new_data) < (max_resolution / 2): # too many Null datas are exists do not sampling
					pass
				else:
					item.data = new_data
					#print(item.data)
					#print('## new len: %d' % len(item.data))

				new_items.append(item)


		self.items = new_items
				

			


