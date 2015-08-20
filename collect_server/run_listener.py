
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

import collect_listener
import server_rrd_plugin


hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)

import common.settings


def listener(port, path):
	lsn = collect_listener.CollectListener(port)
	lsn.put_plugin(server_rrd_plugin.server_rrd_plugin(path))
	
	lsn.listen(200000) # set repeat count, because some leak in rrdtool
	#lsn.listen() # solve above with Process


def restart_listener(port, path):
	while True:
		pid = os.fork()

		if pid == 0: # child
			listener(port, path)
		else: # parent
			os.wait()



	
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


