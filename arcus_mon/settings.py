


#
# alarm settings
# 


# absolute
alarm_conf_absolute = {
		'default':{ 
				'rusage_user':(500000, 1000000, None),
				'rusage_system':(500000, 1000000, None),
				'evictions':(80000, 100000, 120000),
				'reclaimed':(80000, None, None),
				'cmd_get':(40000, 80000, 200000),
				'cmd_set':(40000, 80000, 200000),
		},

		'line-home-*':{
			'evictions':(150000, 150000, 200000),
		},
	}
	


# lambda
alarm_conf_lambda = { 
		'default':{
			#lambda x, limit: (x['get_hits'] / x['cmd_get'] < limit, 'ratio of get_hits/cmd_get(%f) belows %f' % (x['get_hits'] / x['cmd_get'], limit)) : (0.80, 0.60, None),
			#lambda x, limit: (x['total_malloced'] / x['engine_maxbytes'] > limit, 'ratio of total_malloced/enging_maxbytes(%f) exceeds %f' % (x['total_malloced'] / x['engine_maxbytes'], limit)) : (0.097, None, None),
		},

		'linegame-bb2-krc':{
			lambda x, limit: (x['total_malloced'] / x['engine_maxbytes'] > limit, 'ratio of total_malloced/enging_maxbytes(%f) exceeds %f' % (x['total_malloced'] / x['engine_maxbytes'], limit)) : (0.5, 0.7, 0.75),
		},

		'linegame-*':{
			lambda x, limit: (x['total_malloced'] / x['engine_maxbytes'] > limit, 'ratio of total_malloced/enging_maxbytes(%f) exceeds %f' % (x['total_malloced'] / x['engine_maxbytes'], limit)) : (0.7, 0.7, 0.75),
		},

		'nwe-admin-krc':{
			lambda x, limit: (x['total_malloced'] / x['engine_maxbytes'] > limit, 'ratio of total_malloced/enging_maxbytes(%f) exceeds %f' % (x['total_malloced'] / x['engine_maxbytes'], limit)) : (0.7, 0.7, 0.75),
		},
	}








