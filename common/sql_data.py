import time
import common.settings



class sql_gw:
	def __init__(self, filename):
		self.type = common.settings.sql_type
		self.handle = common.settings.conn
		self.filename=filename

	def execute(self, query):
		cursor = self.handle.cursor()
		cursor.execute(query)

	def create(self, query):
		cursor = self.handle.cursor()
		cursor.execute(query)

	def select(self, query):
		print("lets select!\n")
		cursor = self.handle.cursor()
		cursor.execute(query)
		return cursor.fetchall()

	def insert(self, table_name, query):
		print (query)
		cursor = self.handle.cursor()
		cursor.execute(query)

	def read(self, ts_from, ts_to, filter=None):

		filename_list = filename.split("/")
		table_name = filename_list[-1].split(".")[0]
		table_name = table_name.replace('-', '_')
		table_name = "D_"+filename_list[-2]+"_"+table_name
		query = "SELECT * FROM " + table_name
		self.select(query)
		names = [description[0] for description in cursor.description]
		names = tuple(names[1:])


		query += " WHERE "
		cond = "timestamp>=" + ts_from + "and" + "timestamp<" +ts_to
		query = query + cond

		result =self.select(query)
		result = ('#timestamp', names, result)
		print("read!!!")
		print(result)
		return result
