#
# alarm settings
# 


# absolute

"""
# example
alarm_conf_absolute = {
		'*:*':{  # any machine, any db
			'Time_ha_rep_delay':(-100, 60*60, None),
		},
		'*:basic':{  # ex) specify any machine, basic DB
			'Time_ha_rep_delay':(-100, 60*60, None),
		},
		'sys01.db:*':{  # ex) specify 'sys01.db' machine, any DB
			'Time_ha_rep_delay':(-100, 60*60, None),
		},
	}
"""

alarm_conf_absolute = {
		'*:*':{ 
			'Time_ha_rep_delay':(60*30, 60*60, None),
			'N_net_req':(1000, 5000, None),
		},
	}
	


# lambda
alarm_conf_lambda = { 
		'*:*':{
			lambda x, limit: (x['buffer_hit_ratio'] < limit, 'hit ratio(%d) is under %d' % (x['buffer_hit_ratio'], limit)) : (0.80, 0.60, None),
		},
	}








