#!/usr/local/bin/python3

#
# arcus-python-client - Arcus python client drvier
# Copyright 2014 NAVER Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License")
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
 

import sys
import re
import socket

from optparse import OptionParser

from arcus_util import zookeeper
from arcus_util import arcus_node

from kazoo.client import KazooClient
import kazoo



if __name__ == '__main__':
	usage = "usage: %prog [options]"
	parser = OptionParser(usage=usage, version="%prog 1.0")
	parser.add_option('-a', '--address', dest='address', default='', help='zookeeper address')
	parser.add_option('-s', '--service', dest='service', default='', help='service code')
	parser.add_option('-n', '--node', dest='node', default='', help='node address:port')
	parser.add_option('', '--name', dest='name', default='', help='node domain name')
	parser.add_option('-c', '--command', dest='command', default='', help='add_service | del_service | add_node | del_node')
	parser.add_option('-f', '--force', dest='force', default=False, help='ignore exception', action='store_true')

	(options, args) = parser.parse_args()

	address = options.address
	service = options.service
	node = options.node
	command = options.command
	force = options.force

	ret = node.split(':')
	name = ret[0]
	if len(ret) > 1:
		port = ret[1]
	else:
		port = ''

	ip = socket.gethostbyname(name)

	if options.name != '':
		name = options.name


	zoo = zookeeper(address)
	print(zoo)

	if force:
		zoo.set_force()

	if zoo.zk_exists('/arcus') == False:
		print ('create /arcus')
		zoo.zk_create('/arcus', 'arcus')

	if zoo.zk_exists('/arcus/cache_list') == False:
		print ('create /arcus/cache_list')
		zoo.zk_create('/arcus/cache_list', 'cache_list')

	if zoo.zk_exists('/arcus/client_list') == False:
		print ('create /arcus/client_list')
		zoo.zk_create('/arcus/client_list', 'client_list')

	if zoo.zk_exists('/arcus/cache_server_mapping') == False:
		print ('create /arcus/cache_server_mapping')
		zoo.zk_create('/arcus/cache_server_mapping', 'cache_server_mapping')

	if zoo.zk_exists('/arcus/service_code_mapping') == False:
		print ('create /arcus/service_code_mapping')
		zoo.zk_create('/arcus/service_code_mapping', 'service_code_mapping')


	if command:
		if command == 'add_service' and service:
			print ('add /arcus/cache_list/' + service)
			zoo.zk_create('/arcus/cache_list/' + service, 'arcus1.8')

			print ('add /arcus/client_list/' + service)
			zoo.zk_create('/arcus/client_list/' + service, 'arcus1.8')

			print ('add /arcus/service_code_mapping/' + service)
			zoo.zk_create('/arcus/service_code_mapping/' + service, 'arcus1.8')

		elif command == 'del_service' and service:
			data, stat, children = zoo.zk_read('/arcus/service_code_mapping/' + service)

			print ('delete /arcus/service_code_mapping/' + service)
			zoo.zk_delete_tree('/arcus/service_code_mapping/' + service)

			for child in children:
				ret = '/arcus/cache_server_mapping/' + child
				print ('delete node %s' % ret)
				zoo.zk_delete_tree(ret)

			print ('delete /arcus/client_list/' + service)
			zoo.zk_delete_tree('/arcus/client_list/' + service)


		elif command == 'add_node' and service and node:
			assert port != ''

			print ('create /arcus/service_code_mapping/%s/%s:%s' % (service, ip, port))
			zoo.zk_create('/arcus/service_code_mapping/%s/%s:%s' % (service, ip, port), name)

			print ('create /arcus/cache_server_mapping/%s:%s' % (ip, port))
			zoo.zk_create('/arcus/cache_server_mapping/%s:%s' % (ip, port), name)

			print('create /arcus/cache_server_mapping/%s:%s/%s' % (ip, port, service))
			zoo.zk_create('/arcus/cache_server_mapping/%s:%s/%s' % (ip, port, service), 'arcus1.8')

		elif command == 'del_node' and service and node:
			if port != '': # delete one
				print ('delete /arcus/service_code_mapping/%s/%s:%s' % (service, ip, port))
				zoo.zk_delete_tree('/arcus/service_code_mapping/%s/%s:%s' % (service, ip, port))

				print ('delete /arcus/cache_server_mapping/%s:%s' % (ip, port))
				zoo.zk_delete_tree('/arcus/cache_server_mapping/%s:%s' % (ip, port))

			else: # delete all
				head = '/arcus/service_code_mapping/' + service
				data, stat, children = zoo.zk_read(head)

				for child in children:
					idx = len(ip)

					if child[0:idx] == ip:
						ret = head + '/' + child
						print ('delete %s' % ret)
						zoo.zk_delete_tree(ret)

				head = '/arcus/cache_server_mapping'
				data, stat, children = zoo.zk_read(head)

				for child in children:
					idx = len(ip)

					if child[0:idx] == ip:
						ret = head + '/' + child
						print ('delete %s' % ret)
						zoo.zk_delete_tree(ret)
	elif service:
		data, stat, children = zoo.zk_read('/arcus/cache_list/' + service)
		print ('## cache_list/' + service)
		print (children)
	
		data, stat, children = zoo.zk_read('/arcus/service_code_mapping/' + service)
		print ('## cache_server_mapping/' + service)
		print (children)
	else:
		data, stat, children = zoo.zk_read('/arcus/cache_list')
		print ('## cache_list')
		print (children)
	

		

			




