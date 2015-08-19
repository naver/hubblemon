#
# data path
#


# should be sorted by addr
#  add listener if you want
listener_list =[('127.0.0.1:30001', '/data1/collect_listener')]


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
		('expr', '/expr'),
		('arcus_graph', '/graph?type=arcus_graph'),
		('arcus_stat', '/chart?type=arcus_stat'),
		('arcus_prefix', '/chart?type=arcus_prefix'),
		('arcus_list', '/addon?type=arcus_list'),
		('redis_stat', '/chart?type=redis_stat'),
		('memcached_stat', '/chart?type=memcached_stat'),
		('cubrid_stat', '/chart?type=cubrid_stat'),
		('mysql_stat', '/chart?type=mysql_stat'),
		('jstat_stat', '/chart?type=jstat_stat'),
		('redis_query', '/query?type=redis_query'),
		('memcached_query', '/query?type=memcached_query'),
		('cubrid_query', '/query?type=cubrid_query'),
		('arcus_query', '/query?type=arcus_query'),
		('mysql_query', '/query?type=mysql_query') ]


# for arcus_mon
arcus_zk_addrs = []
'''
# example
arcus_zk_addrs.append('arcuscloud.yourcompany.com:17288')
'''

