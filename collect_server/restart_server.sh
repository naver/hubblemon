
kill `ps -ef | grep run_server.py | grep -v grep | awk '{print $2}'`
kill `ps -ef | grep run_listener.py | grep -v grep | awk '{print $2}'`


