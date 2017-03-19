import os, sys, copy
from multiprocessing import Process

from common.tsdb_handle import tsdb_handle





class listener_tsdb_plugin:
	def __init__(self, path):
		self.name = 'tsdb'

		print('>>>>>>>> path: ', path)
		self.path = path
		self.handle=tsdb_handle(path)
		self.prev_data={}
		self.gauge_list={}

	def clone(self):
		return listener_tsdb_plugin(self.path)

	def create_data(self, basedir, name_data_map):
		for name, data in name_data_map.items():                                          
			if name =='RRA':
				continue

			query = "create %s %s" % (basedir, name)
			for attr in data:
				query += " " + attr[0]
				if attr[1] == 'GAUGE':
					self.gauge_list['%s_%s_%s' % (basedir, name, attr[0])] = True

			print(query)
			self.handle.create(query)


	def update_data(self, hostname, timestamp, name_data_map):
		for name, data in name_data_map.items():

			tmp_map = copy.deepcopy(data)
			table_name = '%s_%s' % (hostname, name)

			for attr, val in data.items():
				full_attr = '%s_%s_%s' % (hostname, name, attr)

				if full_attr in self.gauge_list:
					continue
				else:
					if table_name in self.prev_data:
						prev_data = self.prev_data[table_name]
						old = data[attr]
						data[attr] = val - prev_data[attr]

					else:
						self.prev_data[table_name] = tmp_map
						data[attr] = 0

			self.prev_data[table_name] = tmp_map

			query = "put %s %s" % (hostname, name)

			attr_query = ''
			val_query = ''

			for attr, val in data.items():
				attr_query += " " + attr
				val_query += " " + str(val)

			query += attr_query + val_query
			print(query)
			self.handle.put(query)

