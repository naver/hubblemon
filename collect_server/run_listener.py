
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


import os, sys, time

import collect_listener
import server_rrd_plugin


hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)

import common.settings


def listener(port, path):
	print('>>> start child listener %d (%d)' % (port, os.getpid()))
	lsn = collect_listener.CollectListener(port, path)
	lsn.put_plugin('default', server_rrd_plugin.server_rrd_plugin(path))
	lsn.put_plugin('rrd', server_rrd_plugin.server_rrd_plugin(path))
	
	#time.sleep(5)
	lsn.listen(50000) # set repeat count, because some leak in rrdtool
	#lsn.listen() # solve above with Process
	print('>>> stop child listener %d (%d)' % (port, os.getpid()))

	sys.exit()

def restart_listener(port, path):
	while True:
		print('>>> listener %d(%d) fork' % (port, os.getpid()))
		pid = os.fork()

		if pid == 0: # child
			listener(port, path)
		else: # parent
			print('>>> listener %d (%d) wait' % (port, pid))
			os.wait()
			print('>>> listener %d (%d) wakeup' % (port, pid))

	sys.exit()


	
for item in common.settings.listener_list:
	addr = item[0]
	path = item[1]

	if path[0] != '/': # abs
		path = os.path.join(hubblemon_path, path)
	
	ip, port = addr.split(':')
	port = int(port)


	pid = os.fork()

	if pid == 0: # child
		restart_listener(port, path)


os.wait()


