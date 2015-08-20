
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
alarm_conf_absolute = {
		'default':{ 
				'rusage_user':(500000, 1000000, None),
				'rusage_system':(500000, 1000000, None),
				'evictions':(80000, 100000, 120000),
				'reclaimed':(80000, None, None),
				'cmd_get':(40000, 80000, 200000),
				'cmd_set':(40000, 80000, 200000),
		},

		'band':{
			'evictions':(150000, 150000, 200000),
		},
	}
	


# lambda
alarm_conf_lambda = { 
		'default':{
			#lambda x, limit: (x['get_hits'] / x['cmd_get'] < limit, 'ratio of get_hits/cmd_get(%f) belows %f' % (x['get_hits'] / x['cmd_get'], limit)) : (0.80, 0.60, None),
			#lambda x, limit: (x['total_malloced'] / x['engine_maxbytes'] > limit, 'ratio of total_malloced/enging_maxbytes(%f) exceeds %f' % (x['total_malloced'] / x['engine_maxbytes'], limit)) : (0.097, None, None),
		},

		'linegame-*':{
			lambda x, limit: (x['total_malloced'] / x['engine_maxbytes'] > limit, 'ratio of total_malloced/enging_maxbytes(%f) exceeds %f' % (x['total_malloced'] / x['engine_maxbytes'], limit)) : (0.7, 0.7, 0.75),
		},

	}








