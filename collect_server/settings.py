
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

from collect_server import alarm, alarm_mail, alarm_wget


# set alarm suppress time
alarm_suppress = 60*60*6 # 6 hour

# health check time
health_check = ['12:00']

# allocate main alarm
main_alarm = alarm.main_alarm(alarm_suppress, health_check) 


# wget callback example, change this to your environment
def wget_callback(subject, body):
	sms_url="http://sms.interface.yourcompany.com/send_sms?sms_id='%s'&sms_sender='%s'&sms_receiver=[%s]&sms_content='%s'" 
	sms_id = 'SMSID_001'
	sms_sender = '01012345678'
	sms_receivers = ['01012345678']

	recvs = ''
	for receiver in sms_receivers:
		recvs += "'%s'," % receiver

	recvs = recvs[:-1]
	return_url = sms_url % (sms_id, sms_sender, recvs, body)

	return return_url



# smtp server & other settings
mail_server = 'smtp.yourcompany.com'
mail_sender = '!arcus@yourcompany.com'
mail_receivers = ['!arcus@yourcompany.com']

mail_info = alarm_mail.alarm_mail(mail_server, mail_sender, mail_receivers, prefix='[Info]')
mail_warning = alarm_mail.alarm_mail(mail_server, mail_sender, mail_receivers, prefix='[Warning]')
sms_by_wget = alarm_wget.alarm_wget(wget_callback)



# [ mail_info, mail_warning, sms_by_wget ]
main_alarm.alarm_methods.append(mail_info)
main_alarm.alarm_methods.append(mail_warning)
main_alarm.alarm_methods.append(sms_by_wget)



# add client plugins
from arcus_mon.arcus_alarm import arcus_alarm
main_alarm.add_plugin(arcus_alarm())

from psutil_mon.psutil_alarm import psutil_alarm
main_alarm.add_plugin(psutil_alarm())

from cubrid_mon.cubrid_alarm import cubrid_alarm
main_alarm.add_plugin(cubrid_alarm())

from mysql_mon.mysql_alarm import mysql_alarm
main_alarm.add_plugin(mysql_alarm())

from memcached_mon.memcached_alarm import memcached_alarm
main_alarm.add_plugin(memcached_alarm())

from redis_mon.redis_alarm import redis_alarm
main_alarm.add_plugin(redis_alarm())


