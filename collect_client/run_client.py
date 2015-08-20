
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
	c = collectd(hostname, ['%s:40000' % hostname])
else:
	# use stacking if network response is too low
	c = collectd(hostname, ['%s:40000' % hostname], stack=10)


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



