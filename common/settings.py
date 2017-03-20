
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
from data_loader.rrd_storage import rrd_storage_manager
from data_loader.sql_storage import sql_storage_manager
from data_loader.tsdb_storage import tsdb_storage_manager
from data_loader.remote_storage import remote_storage_manager


collect_server_port = 40000

hostname = socket.gethostname()

# should be sorted by addr
#  add listener if you want

#listener_list =[('%s:40001' % hostname, rrd_storage_manager('collect_server/listener_40001'))]
#listener_list =[('%s:40001' % hostname, sql_storage_manager('hubblemon.db'))]
listener_list =[('%s:40001' % hostname, tsdb_storage_manager('127.0.0.1:8000'))]

'''
# examples
# you can spread listeners to remote servers
listener_list =[('%s:30001' % hostname, rrd_storage_manager('/collect_server/listener_30001/'),
		('%s:30002' % hostname, rrd_storage_manager('/collect_server/listener_30002/'),
		('remoteserver1.com:30001', remote_storage_manager('remoteserver1.com:30001'),
		('remoteserver2.com:30001', remote_storage_manager('remoteserver2.com:30001'),
		('%s:30003, % hostname, sql_storage_manager('hubblemon.db')]
'''


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
		('expr', '/expr'),]


# for arcus_mon

'''
# example
arcus_zk_addrs.append('arcuscloud.yourcompany.com:17288')
'''

