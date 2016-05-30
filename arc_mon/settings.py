
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
			lambda x, limit: (x['keyspace_hits'] / (x['keyspace_hits'] + x['keyspace_misses']) < limit, 'keyspace hit ratio(%f) belows %f' % (x['keyspace_hits'] / (x['keyspace_hits'] + x['keyspace_misses']), limit)) : (0.80, 0.60, None),
		},
	}






