
import time

import rrdtool



class rrd_data:
	def __getattr__(self, name):
		return getattr(rrdtool, name)

	def __init__(self, filename, start=int(time.time()) - 10, step=5):
		self.filename = filename
		self.start = start
		self.step = step
		self.DS = {}
		self.RRA = []

	def put_ds(self, name, type, health, min, max):
		self.DS[name] = 'DS:%s:%s:%s:%s:%s' % (name, type, str(health), str(min), str(max))
	
	def put_rra(self, type, default, num, max_rec):
		rra = 'RRA:%s:%f:%d:%d' % (type, default, num, max_rec)
		print(rra)
		self.RRA.append(rra)

	def create(self):
		args = []
		keys = list(self.DS.keys())
		keys.sort()

		for key in keys:
			#print('>> ' + key)
			args.append(self.DS[key])
	
		args += self.RRA
		print('## rrd create - %s(%d items), start: %d, step: %d' % (self.filename, len(self.DS), self.start, self.step))
		print(args)
		rrdtool.create(self.filename, '--start', '%d' % self.start, '--step', '%d' % self.step, *args)

	def update(self, *params):
		result = ''
		count = 0
		#print(params)

		if len(params) == 2 and isinstance(params[1], dict): # dict input
			data = params[1]
			keys = list(data.keys())
			keys.sort()

			result = '%d:' % params[0]

			count = len(keys)
			for key in keys:
				#print('update>> ' + key)
				result += '%d:' % data[key]

		else:
			count = len(params) - 1
			for p in params:
				result += '%d:' % p

		result = result[0:-1]
		
		#print ('## rrd update(%d): %s' % (count, result))
		ret = rrdtool.update(self.filename, result)


	def read(self, ts_from, ts_to):
		ret = rrdtool.fetch(self.filename, 'MAX', '-s', str(ts_from), '-e', str(ts_to))
		return ret



