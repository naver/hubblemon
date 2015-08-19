
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


import sys

from collect_listener import *
from server_rrd_plugin import *

port = int(sys.argv[1])
path = sys.argv[2]

lsn = CollectListener(port)
lsn.put_plugin(server_rrd_plugin(path)) 

lsn.listen(200000) # set repeat count, because some leak in rrdtool
#lsn.listen() # solve above with Process




