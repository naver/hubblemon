
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

hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)

import common.settings


def listener(port, storage_manager):
	print('>>> start child listener %d (%d)' % (port, os.getpid()))
	lsn = collect_listener.CollectListener(port)
	lsn.put_plugin('default', storage_manager)

	lsn.listen()
	print('>>> stop child listener %d (%d)' % (port, os.getpid()))
	sys.exit()

def restart_listener(port, storage_manager):
	while True:
		print('>>> listener %d(%d) fork' % (port, os.getpid()))
		pid = os.fork()

		if pid == 0: # child
			listener(port, storage_manager)
		else: # parent
			print('>>> listener %d (%d) wait' % (port, pid))
			os.wait()
			print('>>> listener %d (%d) wakeup' % (port, pid))

	sys.exit()



for item in common.settings.listener_list:
	addr = item[0]
	storage_manager = item[1]
	if hasattr(storage_manager, 'optional_init'):
		storage_manager.optional_init()

	ip, port = addr.split(':')
	port = int(port)

	pid = os.fork()

	if pid == 0: # child
		restart_listener(port, storage_manager)


os.wait()


