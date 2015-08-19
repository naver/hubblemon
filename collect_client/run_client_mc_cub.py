
import sys, socket

from collect_client import *
from client_psutil_plugin import psutil_stat
from client_memcached_plugin import memcached_stat
from client_cubrid_plugin import cubrid_stat


hostname = socket.gethostname()
c = collectd(hostname, ['10.98.129.47:30000'])

'''
arcus = arcus_stat()
arcus.auto_register()
print(arcus.addr)
c.plugins.append(arcus)
'''

mc = memcached_stat()
mc.auto_register()
c.plugins.append(mc)

cub = cubrid_stat()
cub.auto_register()
c.plugins.append(cub)

ps = psutil_stat()
c.plugins.append(ps)

c.daemon()



