#
# arcus-python-client - Arcus python client drvier
# Copyright 2014 NAVER Corp.
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
 
from kazoo.client import KazooClient
import kazoo
import sys, os, time
import re
from optparse import OptionParser


def do_zookeeper_read(zk, path):
	print(path)
	data, stat = zk.get(path)
	print('node info:', data)
	print('node stat:', stat)

	children = zk.get_children(path)
	print('node children:', children)

	return (data, stat, children)


def do_zookeeper_read_tree(zk, path):
	print(path)
	data, stat = zk.get(path)
	print('node info:', data)
	print('node stat:', stat)

	children = zk.get_children(path)
	print('node children:', children)

	for child in children:
		do_zookeeper_read_tree(zk, path + '/' + child)


def do_zookeeper_create(zk, path, value):
	print(path)
	zk.create(path, bytes(value, 'utf-8'))

	do_zookeeper_read(zk, path)

def do_zookeeper_delete(zk, path):
	print(path)
	zk.delete(path)

	try:
		do_zookeeper_read(zk, path)
	except kazoo.exceptions.NoNodeError:
		print('deleted')
	
def do_zookeeper_update(zk, path, value):
	print(path)
	zk.set(path, bytes(value, 'utf-8'))

	do_zookeeper_read(zk, path)
	

def do_zookeeper_copy(zk_src, src, zk_dst, dst):
	data, stat, children = do_zookeeper_read(zk_src, path)
	print ('## copy %s -> %s (%s)' % (src, dst + src, data))
	zk_dst.create(dst + src, data)

	for child in children:
		zookeeper_copy(zk_src, src + '/' + child, zk_dst, dst)
	
	


if __name__ == '__main__':


	usage = "usage: %prog [options]"
	parser = OptionParser(usage=usage, version="%prog 1.0")
	parser.add_option('-a', '--address', dest='address', default='', help='zookeeper address')
	parser.add_option('-n', '--node', dest='node', default='', help='zookeeper node path')
	parser.add_option('-r', '--read', dest='read', default=False, help='zookeeper node read', action='store_true')
	parser.add_option('-c', '--create', dest='create', default='', help='zookeeper node create')
	parser.add_option('-d', '--delete', dest='delete', default=False, help='zookeeper node delete', action='store_true')
	parser.add_option('-u', '--update', dest='update', default='', help='zookeeper node update')
	parser.add_option('', '--copy', dest='copy', default='', help='zookeeper copy addr:port/new_path')
	parser.add_option('', '--read_tree', dest='read_tree', default=False, help='zookeeper node read tree', action='store_true')

	(options, args) = parser.parse_args()

	zk = KazooClient(options.address)
	zk.start()

	if options.read:
		do_zookeeper_read(zk, options.node)
	elif options.create != '':
		do_zookeeper_create(zk, options.node, options.create)
	elif options.delete:
		do_zookeeper_delete(zk, options.node)
	elif options.update != '':
		do_zookeeper_update(zk, options.node, options.update)
	elif options.copy != '':
		dest_addr, dest_path = options.copy.split('/', 1)
		zk_dest = KazooClient(dest_addr)
		zk_dest.start()
		do_zookeeper_copy(zk, options.node, zk_dest, '/' + dest_path)
	elif options.read_tree:
		do_zookeeper_read_tree(zk, options.node)
	else:
		parser.print_usage();

