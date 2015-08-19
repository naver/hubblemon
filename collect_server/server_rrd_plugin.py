
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

import os, sys
from multiprocessing import Process

common_path = os.path.abspath('..')
sys.path.append(common_path)

from common.rrd_data import rrd_data


def rrd_update_data(file_path, timestamp, data):
	try:
		if os.path.exists(file_path):
			rrd_file = rrd_data(file_path)
			rrd_file.update(timestamp, data)
		else:
			print('## rrd file not found: %s' % file_path)

	except Exception as e:
		print(e)
		print('on update file %s (item: %d)' % (file_path, len(data)))
		print(data)
	
	

class server_rrd_plugin:
	def __init__(self, path):
		self.name = 'rrd'
		self.rrd_file = None
		self.path = path
		
	def clone(self):
		return server_rrd_plugin(self.path)

	

	'''
	# update data use Process
	def update_data(self, hostname, timestamp, name_data_map):
		for name, data in name_data_map.items(): # for each section
			filename = name + '.rrd'
			filename = filename.replace('/', '_')

			path = os.path.join(self.path, hostname)
			path = os.path.join(path, filename)

			p = Process(target=rrd_update_data, args=(path, timestamp, data))
			p.start()
			p.join()
	'''

	# update data use member functions, it makes leak because rrdupdate has it
	#
	def update_data(self, hostname, timestamp, name_data_map):
		for name, data in name_data_map.items(): # for each section
			try:
				filename = name + '.rrd'
				filename = filename.replace('/', '_')
				rrd_file = self.open_data(hostname, filename)
				rrd_file.update(timestamp, data)
			except Exception as e:
				print(e)
				print('on update file %s, %s (item: %d)' % (hostname, name + '.rrd', len(data)))
				print(data)

	def open_data(self, basedir, filename):
		path = os.path.join(self.path, basedir)
		path = os.path.join(path, filename)
		rrd_file = None

		if os.path.exists(path):
			rrd_file = rrd_data(path)

		return rrd_file
		

	def create_data(self, basedir, name_data_map):
		dir_path = os.path.join(self.path, basedir)

		if not os.path.exists(dir_path): # not exists, create folder
			os.makedirs(dir_path)

		rra_list = []
		if 'RRA' in name_data_map:
			rra_list = name_data_map['RRA']	

		for name, data in name_data_map.items(): # for each section
			if name == 'RRA':		# already read
				continue

			filename = name + '.rrd'
			filename = filename.replace('/', '_')
			
			path = os.path.join(dir_path, filename)

			if not os.path.exists(path):
				rrd_file = rrd_data(path)

				assert (isinstance(data, list))
				for item in data:
					rrd_file.put_ds(*item)

				for rra in rra_list:
					rrd_file.put_rra(*rra)

				rrd_file.create()


