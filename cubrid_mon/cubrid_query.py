
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
import CUBRIDdb
from syslog import syslog


hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)

import common.core
from common.core import * # for query eval (like, return_as_table)

from django import forms

def auth_fields(param):
	id = forms.CharField(label = 'id', required = False)
	pw = forms.CharField(label = 'pw', widget = forms.PasswordInput(), required = False)
	db = forms.CharField(label = 'db', required = False)
	port = forms.CharField(label = 'port', required = False)
	return [id, pw, db, port]

def query(param, ip):
	print(param)

	if 'server' not in param:
		return 'select server'	

	server = param['server']

	id = ''
	pw = ''
	query = ''
	dbname = ''
	port = ''

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

	if 'db' in param:
		dbname = param['db']

	if 'port' in param:
		port = param['port']

	if param['query_type'] == 'query':
		conn = CUBRIDdb.connect('CUBRID:%s:%s:%s:%s:%s:' % (server, port, dbname, id, pw))
		cursor = conn.cursor()

		syslog('[hubblemon-cubrid-query:%s-%s-%s(%s)] %s' % (server, dbname, id, ip, query))
		ret = cursor.execute(query)
		#print(ret)

		return common.core.return_as_table(cursor)
	
	else: # exec
		conn = CUBRIDdb.connect('CUBRID:%s:%s:%s:%s:%s:' % (server, port, dbname, id, pw))
		cursor = conn.cursor()

		p = {'conn':conn, 'cursor':cursor, 'result':'None' }

		syslog('[hubblemon-cubrid-eval:%s-%s-%s(%s)] %s' % (server, dbname, id, ip, query))
		exec(query)

		return p['result']
	

