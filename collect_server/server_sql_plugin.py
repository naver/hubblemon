import os, sys, copy
from multiprocessing import Process

from common.sql_data import sql_gw





class server_sql_plugin:
	def __init__(self, path):                                                             
		self.name = 'sql'                                                                 
		self.path = path
		self.sql_manager=sql_gw(path)
		self.prev_data={}
		self.gauge_list={}

	def clone(self):
		return server_sql_plugin(self.path)
	def create_data(self, basedir, name_data_map):
		for name, data in name_data_map.items():                                          
			if name =='RRA':                                                              
				continue                                                                  
			
			table_name = '"D_'+basedir+"_"+name+'"'
			check_table ="SELECT count(*) FROM sqlite_master WHERE type='table' AND name=" + table_name
			is_exist=self.sql_manager.select(check_table)[0][0]
			query = "CREATE TABLE " + table_name
			attr_query= "(timestamp BIGINT PRIMARY KEY"                                   
			for attr in data:
				tmp_query=", " + attr[0] + " BIGINT"                                       
				attr_query= attr_query + tmp_query
				if attr[1] == 'GAUGE':
					self.gauge_list['%s_%s' % (table_name, attr[0])] = True

			query = query+attr_query+")"
			if is_exist==0:
				self.sql_manager.create(query)


	def update_data(self, hostname, timestamp, name_data_map):
		for name, data in name_data_map.items():

			table_name = '"D_'+hostname+"_"+name+'"'
			tmp_map = copy.deepcopy(data)

			for attr, val in data.items():
				full_attr = '%s_%s' % (table_name, attr)
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

			query = "INSERT INTO " + table_name
			attr_query ="("+"timestamp"
			val_query=" VALUES(" + str(int(timestamp))

			for attr, val in data.items():
				attr_query = attr_query + ", " + attr
				val_query = val_query + ", " + str(val)

			attr_query += ")"
			val_query += ")"

			query = query+ attr_query + val_query
			self.sql_manager.insert(table_name, query)
