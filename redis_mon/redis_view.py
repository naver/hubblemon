import os, socket, sys, time
import data_loader
from datetime import datetime


hubblemon_path = os.path.abspath('..')
sys.path.append(hubblemon_path)

import common.core


redis_preset = [['memory', 'memory_human', 'memory_lua', 'memory_rss'], 'mem_frag', ['cpu_user', 'cpu_sys', 'cpu_user_children', 'cpu_sys_children'],
		'connections', (lambda x : x['keyspace_hits'] / (x['keyspace_hits'] + x['keyspace_misses']) * 100, 'hit ratio'), 'expired_keys', 'evicted_keys', 'cmds_processed',
		['cmd_get', 'cmd_set', 'cmd_mget', 'cmd_mset'], ['cmd_del', 'cmd_expire', 'cmd_checkpoint'],
		['cmd_linsert', 'cmd_lpush', 'cmd_lpop', 'cmd_llen'], ['cmd_lindex', 'cmd_lrange'],
		['cmd_sadd', 'cmd_scard', 'cmd_set', 'cmd_srem'], ['cmd_sismember', 'cmd_smembers'], 
		['cmd_zadd', 'cmd_zcard', 'cmd_zrem'], ['cmd_zrange', 'cmd_zrank', 'cmd_zscore']]


def redis_view(path, title = ''):
	return common.core.default_loader(path, redis_preset, title)



#
# chart list
#
redis_cloud_map = {}
last_ts = 0

def init_plugin():
	global redis_cloud_map
	global last_ts

	ts = time.time()
	if ts - last_ts < 300:
		return
	last_ts = ts

	print('#### redis init ########')

	system_list = common.core.get_system_list()
	for system in system_list:
		instance_list = common.core.get_data_list(system, 'redis_')
		if len(instance_list) > 0:
			redis_cloud_map[system] = instance_list	

	print (redis_cloud_map)
		
	


def get_chart_data(param):
	#print(param)
	global redis_cloud_map


	type = 'redis_stat'
	if 'type' in param:
		type = param['type']

	if 'instance' not in param or 'server' not in param:
		return None

	instance_name = param['instance']
	server_name = param['server']

	if type == 'redis_stat':
		for node in redis_cloud_map[server_name]:
			if node.startswith(instance_name):
				results = common.core.default_loader(server_name + '/' + node, redis_preset, title=node)
				break

	return results



def get_chart_list(param):
	#print(param)

	if 'type' in param:
		type = param['type']

	return (['server', 'instance'], redis_cloud_map)
	


