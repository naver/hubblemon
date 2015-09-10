
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


def system_view_brief(client, title = ''):
	loader_list = []

	file_path = os.path.join(client, 'psutil_cpu')
	loader_list.append(common.core.loader(file_path, cpu_filter, 'cpu'))
	
	file_path = os.path.join(client, 'psutil_memory')
	loader_list.append(common.core.loader(file_path, mem_filter, 'memory'))

	file_path = os.path.join(client, 'psutil_swap')
	loader_list.append(common.core.loader(file_path, swap_filter, 'swap'))

	file_path = os.path.join(client, 'psutil_disk')
	loader_list.append(common.core.loader(file_path, disk_filter, 'disk'))
	
	file_path = os.path.join(client, 'psutil_net')
	loader_list.append(common.core.loader(file_path, net_filter, 'net'))

	file_path = os.path.join(client, 'psutil_resource')
	loader_list.append(common.core.loader(file_path, resource_filter, 'resource'))
		
	return loader_list


def system_view(client, item, title = ''):
	if item == 'brief':
		return system_view_brief(client, title)

	loader_file_list = []
	loader_list = []

	loader_file_list = common.core.get_data_list_of_client(client, 'psutil_' + item)

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
		
	
	for loader_file in loader_file_list:
		print(loader_file)
		loader_list.append(common.core.loader(os.path.join(client, loader_file), filter, loader_file.split('.')[0]))

	return loader_list


