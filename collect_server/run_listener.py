import sys

from collect_listener import *
from server_rrd_plugin import *

port = int(sys.argv[1])
path = sys.argv[2]

lsn = CollectListener(port)
lsn.put_plugin(server_rrd_plugin(path)) 

lsn.listen(200000) # set repeat count, because some leak in rrdtool
#lsn.listen() # solve above with Process




