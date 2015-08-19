
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








