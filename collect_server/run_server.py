
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

hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)

import collect_server.server
import common.settings

def server():
	port = common.settings.collect_server_port

	print('>>> start child server %d (%d)' % (port, os.getpid()))
	svr = collect_server.server.CollectServer(port)

	for item in common.settings.listener_list:
		print('# put listener: %s' % item[0])
		svr.put_listener(item[0])

	svr.listen()
	print('>>> stop child server %d (%d)' % (port, os.getpid()))


while True:
	port = common.settings.collect_server_port

	print('>>> server %d(%d) fork' % (port, os.getpid()))
	pid = os.fork()

	if pid == 0: # child
		server()
	else:
		print('>>> server %d (%d) wait' % (port, pid))
		os.wait()
		print('>>> server %d (%d) wakeup' % (port, pid))



