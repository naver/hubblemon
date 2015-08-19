
from server import *

svr = CollectServer(30000)

for i in range(1, 11):
	port = 30000 + i
	svr.put_listener('10.98.129.47:%d' % port)

svr.listen()



