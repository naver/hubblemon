
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

import os, sys, telnetlib
from syslog import syslog

hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)

import common.core
from common.core import * # for query eval (like, return_as_table)

from django import forms
import memcache

def auth_fields(param):
	id = forms.CharField(label = 'id', required = False)
	pw = forms.CharField(label = 'pw', widget = forms.PasswordInput(), required = False)
	return [id, pw]


def do_memcached_command(ip, port, command, timeout=0.2):
	tn = telnetlib.Telnet(ip, port)
	tn.write(bytes(command + '\r\n', 'utf-8'))

	if command[0:5] == 'scrub' or command[0:5] == 'flush':
		message = 'OK'
	else:
		message = 'END'

	result = tn.read_until(bytes(message, 'utf-8'), timeout)

	result = result.decode('utf-8')
	tn.write(bytes('quit\r\n', 'utf-8'))
	tn.close()
	return result

	
def query(param, ip):
	print(param)

	if 'server' not in param:
		return 'select server'	


	server = param['server']
	instance = param['instance']
	dummy, port_suffix = instance.split('_')
	port, suffix = port_suffix.split('.')

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
		syslog('[hubblemon-memcached-query:%s-%s(%s)] %s' % (server, id, ip, query))
		result_str = ''

		result_str += '[%s-%s]<br>%s<br>' % (server, port, common.core.return_as_string(do_memcached_command(server, port, query)))
				
		return result_str

	else: # exec
		conn = memcache.Client(['%s:%s' % (server, port)], debug=0)
		
		p = {'conn':conn, 'result':'None' }

		syslog('[hubblemon-memcached-eval:%s-%s(%s)] %s' % (server, id, ip, query))
		exec(query)

		return p['result']
		





	
	

	


