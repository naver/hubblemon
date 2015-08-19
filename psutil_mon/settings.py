#
# alarm settings
# 

# absolute

"""
# example
alarm_conf_absolute = {
		'*:net-*':{  # any machine, any net if
				'bytes_recv':(50000000, 60000000, 90000000),
		},

		# ex) for specipy machine or machine group
		'sys01.db:resource':{ 
				'retransmit':(50, 200, 800),
		},
		'sys??.db:resource':{ 
				'retransmit':(1, 1, 1),
		},
	}
"""

alarm_conf_absolute = {
		'*:net-*':{ 
				'bytes_recv':(50000000, 60000000, 90000000),
				'bytes_sent':(50000000, 60000000, 90000000),
		},

		'*:resource': {
				'retransmit':(5, 20, 80),
		},

	}

# ratio

alarm_conf_lambda = { 
		'*:memory':{
			lambda x, limit: (x['used'] / x['total'] > limit, 'ratio of used/total(%f) exceeds %f' % (x['used'] / x['total'], limit)) : (0.95, None, None),
		},
	}


