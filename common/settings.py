
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
# data path
#

import os, sys, socket


collect_server_port = 40000

# should be sorted by addr
#  add listener if you want

"""
listener_list =[('%s:30001' % socket.gethostname(), 'collect_server/listener_30001', 'local')]

'''
# you can spread listeners to remote servers
listener_list =[('%s.com:30001' % socket.gethostname(), '/collect_server/listener_30001/', 'local'),
		('%s.com:30002' % socket.gethostname(), '/collect_server/listener_30002/', 'local'),
		('remoteserver1.com:30001', '/data2/collect_listener/', 'remote'),
		('remoteserver2.com:30002', '/data3/collect_listener/', 'remote')]
'''
"""

listener_list =[('%s.com:40001' % socket.gethostname(), '/data1/collect_listener/', 'local'),
		('%s.com:40002' % socket.gethostname(), '/data2/collect_listener/', 'local'),
		('%s.com:40003' % socket.gethostname(), '/data3/collect_listener/', 'local'),
		('%s.com:40004' % socket.gethostname(), '/data4/collect_listener/', 'local'),
		('%s.com:40005' % socket.gethostname(), '/data5/collect_listener/', 'local'),
		('%s.com:40006' % socket.gethostname(), '/data6/collect_listener/', 'local'),
		('%s.com:40007' % socket.gethostname(), '/data7/collect_listener/', 'local'),
		('%s.com:40008' % socket.gethostname(), '/data8/collect_listener/', 'local'),
		('%s.com:40009' % socket.gethostname(), '/data9/collect_listener/', 'local'),
		('%s.com:40010' % socket.gethostname(), '/data10/collect_listener/', 'local')]

#
# setting values
#

chart_resolution = 400


#
# main link settings
# 
# remove or add links you want
#
main_link = [	('system', '/system'),
		('expr', '/expr'),
		('arcus_graph', '/graph?type=arcus_graph'),
		('arcus_stat', '/chart?type=arcus_stat'),
		('arcus_prefix', '/chart?type=arcus_prefix'),
		('arcus_list', '/addon?type=arcus_list'),
		('redis_stat', '/chart?type=redis_stat'),
		('memcached_stat', '/chart?type=memcached_stat'),
		('cubrid_stat', '/chart?type=cubrid_stat'),
		('mysql_stat', '/chart?type=mysql_stat'),
		('jstat_stat', '/chart?type=jstat_stat'),
		('redis_query', '/query?type=redis_query'),
		('memcached_query', '/query?type=memcached_query'),
		('cubrid_query', '/query?type=cubrid_query'),
		('arcus_query', '/query?type=arcus_query'),
		('mysql_query', '/query?type=mysql_query') ]


# for arcus_mon
arcus_zk_addrs = []
arcus_zk_addrs.append('gasan.arcuscloud.nhncorp.com:17288')
'''
# example
arcus_zk_addrs.append('arcuscloud.yourcompany.com:17288')
'''

