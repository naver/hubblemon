import os, sys
from multiprocessing import Process

from common.sql_data import sql_gw





class server_sql_plugin:
	def __init__(self, path):                                                             
		self.name = 'sql'                                                                 
		self.path = path
		self.sql_manager=sql_gw(path)                                                             

	def clone(self):
		return server_sql_plugin(self.path)
	def create_data(self, basedir, name_data_map):
		print(basedir)
		
		for name, data in name_data_map.items():                                          
			if name =='RRA':                                                              
				continue                                                                  
			
			name =name.replace('-', '_')
			name = "D_"+basedir+"_"+name
			check_table ="SELECT count(*) FROM sqlite_master WHERE type='table' AND name='" + name + "'"
			is_exist=self.sql_manager.select(check_table)[0][0]
			if(is_exist==0):
				query = "CREATE TABLE " + name
				attr_query= "(timestamp BIGINT PRIMARY KEY"                                   
				for attr in data:
					tmp_query=", " + attr[0] + " BIGINT"                                       
					attr_query= attr_query + tmp_query                                        
			   
				query= query+attr_query+")"

				print (query)
				self.sql_manager.create(query)


	def update_data(self, hostname, timestamp, name_data_map):
		for name, data in name_data_map.items():

			name = name.replace('-', '_')
			name = "D_"+hostname+"_"+name
			query = "INSERT INTO " + name
			attr_query ="("+"timestamp"
			val_query=" VALUES(" + str(int(timestamp))

			for attr, val in data.items():
				attr_query = attr_query + ", " + attr
				val_query = val_query + ", " + str(val)

			attr_query += ")"
			val_query += ")"

			query = query+ attr_query + val_query
			self.sql_manager.insert(name, query)
