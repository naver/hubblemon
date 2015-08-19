import subprocess
import shlex

class jstat_stat:
	def __init__(self):
		self.name = 'jstat'
		self.type = 'rrd'

		self.applist = {}
		self.proc = {}

		self.collect_key_init()
		self.create_key_init()

	def __repr__(self):
		return '[%s-(%s,%s)]' % (self.applist.__repr__(), self.name, self.type)


	def push_app(self, appname, pid):
		self.applist[appname] = pid


	def collect_init(self, pid):
		if pid not in self.proc:
			self.proc[pid] = subprocess.Popen(shlex.split('jstat -gcutil %d 5000' % pid), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	def collect(self):
		all_stats = {}


		for appname, pid in self.applist.items():
			stat = {}

			self.collect_init(pid)
			proc = self.proc[pid]

			line = proc.stdout.readline()
			line = line.decode('utf-8')

			items = line.split()
			values = []

			if items[0] == 'S0':
				continue # first line

			for i in range(0, len(items)):
				alias_key = self.collect_key[i][0]
				factor = self.collect_key[i][1]

				value = float(items[i]) * factor
				stat[alias_key] = int(value)

			all_stats['jstat_%s' % appname] = stat

			#print(all_stats)

		return all_stats

		

	def create(self):
		all_map = {}

		for appname, pid in self.applist.items():
			all_map['jstat_%s' % appname] = self.create_key_list # stats per port

		all_map['RRA'] = self.rra_list
		return all_map


	def create_key_init(self):
		self.collect_key_init()

		self.create_key_list=[  ('Survivor_0', 'GAUGE', 60, '0', 'U'),
					('Survivor_1', 'GAUGE', 60, '0', 'U'),
					('Eden', 'GAUGE', 60, '0', 'U'),
					('Old', 'GAUGE', 60, '0', 'U'),
					('Permanent', 'GAUGE', 60, '0', 'U'),
					('YGC', 'DERIVE', 60, '0', 'U'),
					('YGCT', 'DERIVE', 60, '0', 'U'),
					('FGC', 'DERIVE', 60, '0', 'U'),
					('FGCT', 'DERIVE', 60, '0', 'U'),
					('GCT', 'DERIVE', 60, '0', 'U')]


		# used for RRA
		self.rra_list =	[  ('MAX', 0.5, 5, (3600/5)*24), 	# 5sec  (to 1day)
				   ('MAX', 0.5, 60, (3600/60)*24*7), 	# 30sec (to 7day)
				   ('MAX', 0.5, 3600, 24*31),		# 1hour (to 1month)
				   ('MAX', 0.5, 3600*3, (24/3)*366*3) ]	# 3hour (to 3year)



	def collect_key_init(self):
		self.collect_key = []
		 
		self.collect_key.append(('Survivor_0', 1))
		self.collect_key.append(('Survivor_1', 1))
		self.collect_key.append(('Eden', 1))
		self.collect_key.append(('Old', 1))
		self.collect_key.append(('Permanent', 1))
		self.collect_key.append(('YGC', 1000))
		self.collect_key.append(('YGCT', 1000))
		self.collect_key.append(('FGC', 1000))
		self.collect_key.append(('FGCT', 1000))
		self.collect_key.append(('GCT', 1000))


