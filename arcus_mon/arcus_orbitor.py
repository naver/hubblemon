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

import os, sys, time, datetime
import paramiko

hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)

from arcus_mon.arcus_driver import arcus_util
import common.settings
import collect_server.alarm_wget
import collect_server.settings


arcus_zk_addrs = common.settings.arcus_zk_addrs



# modified

def do_ssh_command(addr, command):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(addr)

	stdin, stdout, stderr = ssh.exec_command(command)
	for line in stdout.readlines():
		sys.stdout.write(line)
	ssh.close()



class arcus_orbitor:
	def __init__(self, alarm):
		self.zk_addrs = arcus_zk_addrs
		self.zk_list = []
		self.alarm = alarm

		for addr in self.zk_addrs:
			zk = arcus_util.zookeeper(addr)
			zk.load_all()
			print('###################################################')
			print('### zk: %s ' % addr)
			print('###################################################')
			print(zk)
			print('\n\n\n\n')
			zk.watch(self.watch_callback)

			self.zk_list.append(zk)


	def watch_callback(self, event, event_list):
		print('## path: %s' % event.path)
		print(event_list)
		path = event.path
		cloud = os.path.basename(path)
		created = event_list['created']
		deleted = event_list['deleted']

		for node in created:
			msg = '[Arcus] %s (%s) is up' % (node, cloud)
			self.alarm.send(msg, msg)
		
		for node in deleted:
			msg = '[Arcus] %s (%s) is down' % (node, cloud)
			self.alarm.send(msg, msg)
		



naver_sms = collect_server.alarm_wget.alarm_wget(collect_server.settings.mex_call)
ortibor = arcus_orbitor(naver_sms) # run in background

print('# orbitor launched')

last_health_check = 0

# health check
print('# health check loop')
health_check = collect_server.settings.health_check
#health_check.append('16:35')
print(health_check)

while True:
	now = datetime.datetime.now()
	print('# health check loop (%s)' % str(now))
	for check_time in health_check:
		ret = check_time.split(':')
		if len(ret) != 2:
			print('# health check setting error: %s' % check_time)

		h = int(ret[0])
		m = int(ret[1])

		tm = time.localtime()
		ts = time.time()
		if tm.tm_hour == h:
			if tm.tm_min == m and ts > last_health_check + 60*2:
				print('# orbitor health check')
				last_health_check = ts
				naver_sms.send('Orbitor Health check', 'Orbitor Health check')
				os.system("ssh cregarcus01.news.nhnsystem.com 'bash ~/health_restart.sh  > /dev/null 2>&1 &'")

	time.sleep(10)
	sys.stdout.flush()



