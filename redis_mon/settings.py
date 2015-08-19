#
# alarm settings
# 


# absolute

"""
alarm_conf_absolute = {
		'*:*':{  # any machine, any port
			'cpu_user':(500000, 1000000, None),
		},
		# ex) specify some instance in any machine
		'*:112??':{ 
			'cpu_user':(10000, None, None),
		},
	}
"""

alarm_conf_absolute = {
		'*:*':{  # any machine, any port
			'cpu_user':(500000, 1000000, None),
			'cpu_sys':(500000, 1000000, None),
			'evicted_keys':(80000, 100000, 120000),
			'expired_keys':(80000, None, None),
			'cmd_processed':(40000, 80000, 200000),
			'mem_frag':(200, None, None),
			'memory_rss':(1000000*1000*10, None, None),
		},
	}
	

# lambda
alarm_conf_lambda = { 
		'*:*':{
			lambda x, limit: (x['keyspace_hits'] / (x['keyspace_hits'] + x['keyspace_misses']) < limit, 'keyspace hit ratio belows %f' % (x['keyspce_hits'] / (x['keyspace_hits'] + x['keyspace_misses']), limit)) : (0.80, 0.60, None),
		},
	}








