
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

import os, socket
import common.settings
import common.core
import data_loader

psutil_preset = []

cpu_filter = [['system', 'user'], ['irq', 'softirq'], 'idle', 'iowait', 'nice']
mem_filter = [['total', 'available', 'free', 'used'], 'percent']
swap_filter = [['total', 'used', 'free'], ['sin', 'sout'], 'percent']
disk_filter = [['read_bytes', 'write_bytes'], ['read_count', 'write_count'], ['read_time', 'write_time']]
net_filter = [['bytes_recv', 'bytes_sent'], ['packets_recv', 'packets_sent'], ['dropin', 'dropout'], ['errin', 'errout']]
resource_filter = [['tcp_open', 'fd', 'handle'], ['process', 'thread'], 'retransmit', 'ctx_switch']


def system_view_brief(entity, title = ''):
	if title == '':
		title = entity

	loader_list = []

	entity_table = os.path.join(entity, 'psutil_cpu')
	loader_list.append(common.core.loader(entity_table, cpu_filter, 'cpu'))
	
	entity_table = os.path.join(entity, 'psutil_memory')
	loader_list.append(common.core.loader(entity_table, mem_filter, 'memory'))

	entity_table = os.path.join(entity, 'psutil_swap')
	loader_list.append(common.core.loader(entity_table, swap_filter, 'swap'))

	entity_table = os.path.join(entity, 'psutil_disk')
	loader_list.append(common.core.loader(entity_table, disk_filter, 'disk'))
	
	entity_table = os.path.join(entity, 'psutil_net')
	loader_list.append(common.core.loader(entity_table, net_filter, 'net'))

	entity_table = os.path.join(entity, 'psutil_resource')
	loader_list.append(common.core.loader(entity_table, resource_filter, 'resource'))

	loader = data_loader.loader_factory.serial(loader_list)
	loader.title = title
	return loader


def system_view(entity, item = 'brief', title = ''):
	if title == '':
		title = entity

	if item == 'brief':
		return system_view_brief(entity, title)

	table_list = []
	loader_list = []

	table_list = common.core.get_table_list_of_entity(entity, 'psutil_' + item)

	filter = None
	if item == 'cpu':
		filter = cpu_filter
	elif item == 'memory':
		filter = mem_filter
	elif item == 'swap':
		filter = swap_filter
	elif item == 'disk':
		filter = disk_filter
	elif item == 'net':
		filter = net_filter
	elif item == 'resource':
		filter = resource_filter
		
	for table in table_list:
		print(table)
		loader_list.append(common.core.loader(os.path.join(entity, table), filter, table.split('.')[0]))

	loader = data_loader.loader_factory.serial(loader_list)
	loader.title = title
	return loader


