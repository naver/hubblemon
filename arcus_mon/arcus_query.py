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

import os, sys
from syslog import syslog

hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)

import common.core
from common.core import *

import arcus_mon.arcus_view


arcus_driver_path = os.path.abspath('./arcus_mon/arcus_driver')
sys.path.append(arcus_driver_path)
from arcus import *
from arcus_mc_node import *
from arcus_util import *

from django import forms

def auth_fields(param):
	id = forms.CharField(label = 'id', required = False)
	pw = forms.CharField(label = 'pw', widget = forms.PasswordInput(), required = False)
	return [id, pw]
	
def query(param, ip):
	print(param)

	if 'cloud' not in param:
		return 'select cloud'	

	if 'server' not in param:
		return 'select server'	

	cloud = param['cloud']
	server = param['server']

	id = ''
	pw = ''
	query = ''

	if 'id' in param:
		if isinstance(param['id'], list):
			id = param['id'][0]
		else:
			id = param['id']

	if 'pw' in param:
		if isinstance(param['pw'], list):
			pw = param['pw'][0]
		else:
			pw = param['pw']

	if 'query' in param:
		query = param['query']


	if param['query_type'] == 'query':
		syslog('[hubblemon-arcus-query:%s-%s-%s(%s)] %s' % (cloud, server, id, ip, query))
		result_str = ''

		if server == '[ALL]':
			server_list = arcus_mon.arcus_view.arcus_cloud_map[cloud]
		else:
			server_list = [server]

		for server in server_list:
			addr, port = server.split('/')
			prefix, port = port.split('_')
			node = arcus_node(addr, port)
			result_str += '[%s-%s]<br>%s<br>' % (addr, port, common.core.return_as_string(node.do_arcus_command(query)))
				
		return result_str

	else: # exec
		conn = Arcus(ArcusLocator(ArcusMCNodeAllocator(ArcusTranscoder())))

		zk_addr = arcus_mon.arcus_view.arcus_cloud_list_map[cloud][0]
		conn.connect(zk_addr, cloud)
		
		p = {'conn':conn, 'result':'None' }

		syslog('[hubblemon-arcus-eval:%s-%s(%s)] %s' % (cloud, id, ip, query))
		exec(query)
		conn.disconnect()

		return p['result']
		





	
	

	


