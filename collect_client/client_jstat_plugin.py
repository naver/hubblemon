import subprocess
import shlex

class jstat_stat:
	def __init__(self):
		self.name = 'jstat'
		self.type = 'rrd'

		self.pidlist = []
		self.proc = {}

		self.collect_key_init()
		self.create_key_init()
		self.flag_auto_register = False
		self.auto_register_filters = None

	def __repr__(self):
		return '[%s-(%s,%s)]' % (self.applist.__repr__(), self.name, self.type)

	def auto_register(self, filters = ['java']):
		self.flag_auto_register = True
		self.auto_register_filters = filters

		proc1 = subprocess.Popen(shlex.split('ps -ef'), stdout=subprocess.PIPE)
		proc2 = subprocess.Popen(shlex.split('grep java'), stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		proc1.stdout.close()
		out, err = proc2.communicate()
		out = out.decode('utf-8')
		lines = out.split('\n')

		tmp_pidlist = []
		for line in lines:
			flag = True
			for filter in filters:
				if line.find(filter) < 0:
					flag = False

			if line.find('grep') >= 0: # ignore grep
				flag = False

			if flag == True:
				lst = line.split()
				if lst[1].isnumeric():
					tmp_pidlist.append(int(lst[1]))


		tmp_pidlist.sort()
		if self.pidlist != tmp_pidlist:
			print('## auto register java')
			print(tmp_pidlist)
			self.pidlist = tmp_pidlist
			return True

		return False


	def push_pid(self, pid):
		self.pidlist.append(pid)


	def collect_init(self, pid):
		if pid not in self.proc:
			self.proc[pid] = subprocess.Popen(shlex.split('jstat -gcutil %d 5000' % pid), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	def collect(self):
		all_stats = {}

		if self.flag_auto_register == True:
			if self.auto_register(self.auto_register_filters) == True:
				return None # for create new file

		for pid in self.pidlist:
			stat = {}

			self.collect_init(pid)
			proc = self.proc[pid]

			line = proc.stdout.readline()
			line = line.decode('utf-8')

			items = line.split()
			values = []

			if len(items) > 0 and items[0] == 'S0':
				print(line)
				continue # first line

			if len(items) != len(self.collect_key):
				print(line)
				continue # somthine wrong

			for i in range(0, len(items)):
				alias_key = self.collect_key[i][0]
				factor = self.collect_key[i][1]

				value = float(items[i]) * factor
				stat[alias_key] = int(value)

			all_stats['jstat_%d' % pid] = stat

			#print(all_stats)

		return all_stats

		

	def create(self):
		all_map = {}

		for pid in self.pidlist:
			all_map['jstat_%d' % pid] = self.create_key_list # stats per port

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
		self.rra_list =	[  ('MAX', 0.5, 5/5, (3600/5)*24), 	# 5sec  (to 1day)
				   ('MAX', 0.5, 60/5, (3600/60)*24*7), 	# 30sec (to 7day)
				   ('MAX', 0.5, 3600/5, 24*31),		# 1hour (to 1month)
				   ('MAX', 0.5, 3600*3/5, (24/3)*366*3) ]	# 3hour (to 3year)



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


