

kill `ps -ef | grep orbitor | grep -v grep | awk '{print $2}'`

rm -rf nohup*.out

nohup python3 arcus_orbitor.py > nohup_orbitor.out 2>&1 &

