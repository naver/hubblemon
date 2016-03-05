
#
# Hubblemon - Yet another general purpose system monitor
#
# Copyright 2015 NAVER Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
				'bytes_recv':(90000000, 100000000, 110000000),
				'bytes_sent':(90000000, 100000000, 110000000),
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


