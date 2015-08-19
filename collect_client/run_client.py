
import sys, socket

from collect_client import *
from client_psutil_plugin import psutil_stat
from client_arcus_plugin import arcus_stat
from client_memcached_plugin import memcached_stat
from client_redis_plugin import redis_stat
from client_cubrid_plugin import cubrid_stat
from client_mysql_plugin import mysql_stat
from client_jstat_plugin import jstat_stat



hostname = socket.gethostname()


if True:
	c = collectd(hostname, ['127.0.0.1:30000'])
else:
	# use stacking if network response is too low
	c = collectd(hostname, ['127.0.0.1:30000'], stack=10)


"""
# arcus stat example
arcus = arcus_stat()
arcus.auto_register()
c.plugins.append(arcus)

# memcached stat example
mc = memcached_stat()
mc.auto_register()
c.plugins.append(mc)

# mysql stat example
my = mysql_stat()
my.push_db('dbname', 'mysql.sock_path', 'id', 'pw')
c.plugins.append(my)

# cubrid stat example
cub = cubrid_stat()
cub.auto_register()
c.plugins.append(cub)
"""

# system stat (psutil) example
ps = psutil_stat()
c.plugins.append(ps)

c.daemon()



