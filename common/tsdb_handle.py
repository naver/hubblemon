import time
import common.settings



class tsdb_handle:
	def __init__(self, path):
		#self.type = common.settings.tsdb_type
		#self.handle = common.settings.conn
		self.path=path

	def create(self, query):
		pass

	def put(self, query):
		pass

	def read(self, ts_from, ts_to, filter=None):
		toks = self.path.split("/")
		entity = toks[-2]
		table = toks[-1]

		if filter == None:
			query = 'get %s %s *' % (entity, table)
		else:
			pass

		query += ' %d %d' % (ts_from, ts_to)

		print(query)

