
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



