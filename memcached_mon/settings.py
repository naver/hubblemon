#
# alarm settings
# 


# absolute
"""
# example
alarm_conf_absolute = {
		'*:*':{  # any machine, any port
			'rusage_user':(1, None, None),
		},
		# ex) specify some instance in any machine
		'*:112??':{ 
			'rusage_user':(10000000, None, None),
		},
	}
"""

alarm_conf_absolute = {
		'*:*':{  # any machine, any port
			'rusage_user':(500000, 1000000, None),
			'rusage_system':(500000, 1000000, None),
			'evictions':(80000, 100000, 120000),
			'reclaimed':(80000, None, None),
			'cmd_get':(40000, 80000, 200000),
			'cmd_set':(40000, 80000, 200000),
		},
	}
	

# lambda
alarm_conf_lambda = { 
		'*:*':{
			lambda x, limit: (x['get_hits'] / x['cmd_get'] < limit, 'ratio of get_hits/cmd_get(%f) belows %f' % (x['get_hits'] / x['cmd_get'], limit)) : (0.80, 0.60, None),
		},
	}








