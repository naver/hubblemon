import os, sys
import pymysql
from syslog import syslog


hubblemon_path = os.path.abspath('..')
sys.path.append(hubblemon_path)

import common.core
from common.core import * # for query eval (like, return_as_table)

from django import forms

def auth_fields(param):
	id = forms.CharField(label = 'id', required = False)
	pw = forms.CharField(label = 'pw', widget = forms.PasswordInput(), required = False)
	db = forms.CharField(label = 'db', required = False)
	return [id, pw, db]

def query(param, ip):
	print(param)

	if 'server' not in param:
		return 'select server'	

	server = param['server']

	id = ''
	pw = ''
	query = ''
	dbname = ''

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

	if param['query_type'] == 'query':
		conn = pymysql.connect(host=server, user=id, passwd=pw, db=dbname)
		cursor = conn.cursor()

		syslog('[hubblemon-mysql-query:%s-%s-%s(%s)] %s' % (server, dbname, id, ip, query))
		ret = cursor.execute(query)
		#print(ret)

		return common.core.return_as_table(cursor)

	
	else: # exec
		conn = pymysql.connect(host=server, user=id, passwd=pw, db=dbname)
		cursor = conn.cursor()

		p = {'conn':conn, 'cursor':cursor, 'result':'None' }

		syslog('[hubblemon-mysql-eval:%s-%s-%s(%s)] %s' % (server, dbname, id, ip, query))
		exec(query)

		result = p['result']
	

