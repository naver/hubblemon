#
# arcus-python-client - Arcus python client drvier
# Copyright 2014 NAVER Corp.
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


#
# sys.argv[1] : connection url for Arcus cloud (zookeeper address:port)
# sys.argv[2] : Arcus cloud service code
#
# USAGE: python3 test.py your.arcuscloud.com:11223 service_code
#

from arcus import *
from arcus_mc_node import ArcusMCNodeAllocator
from arcus_mc_node import EflagFilter
import datetime, time, sys

#enable_log()

timeout = 20


# client which use arcus memcached node & default arcus transcoder
client = Arcus(ArcusLocator(ArcusMCNodeAllocator(ArcusTranscoder())))

print('### connect to client')
client.connect(sys.argv[1], sys.argv[2])


#####################################################################################################
#
# TEST 1: primitive type
#
#####################################################################################################
ret = client.set('test:string1', 'test...', timeout)
print(ret.get_result())
assert ret.get_result() == True

ret = client.get('test:string1')
print(ret.get_result())
assert ret.get_result() == 'test...'

ret = client.set('test:string2', 'test...2', timeout)
print(ret.get_result())
assert ret.get_result() == True

ret = client.get('test:string2')
print(ret.get_result())
assert ret.get_result() == 'test...2'

ret = client.set('test:int', 1, timeout)
print(ret.get_result())
assert ret.get_result() == True

ret = client.get('test:int')
print(ret.get_result())
assert ret.get_result() == 1

ret = client.set('test:float', 1.2, timeout)
print(ret.get_result())
assert ret.get_result() == True

ret = client.get('test:float')
print(ret.get_result())
assert ret.get_result() == 1.2

ret = client.set('test:bool', True, timeout)
print(ret.get_result())
assert ret.get_result() == True

ret = client.get('test:bool')
print(ret.get_result())
assert ret.get_result() == True

now = datetime.datetime.now()
ret = client.set('test:date', now, timeout)
print(ret.get_result())
assert ret.get_result() == True

ret = client.get('test:date')
print(ret.get_result())
print(now)
assert (abs(ret.get_result() - now)) < datetime.timedelta(1000)

ret = client.set('test:bytearray', b'bytes array', timeout)
print(ret.get_result())
assert ret.get_result() == True

ret = client.get('test:bytearray')
print(ret.get_result())
assert ret.get_result() == b'bytes array'


ret = client.set('test:incr', '1', timeout)
print(ret.get_result())
assert ret.get_result() == True

ret = client.incr('test:incr', 10)
print(ret.get_result())
assert ret.get_result() == 11

ret = client.decr('test:incr', 3)
print(ret.get_result())
assert ret.get_result() == 11-3

ret = client.decr('test:incr', 100)
print(ret.get_result())
assert ret.get_result() == 0 # minimum value is 0


#####################################################################################################
#
# TEST 2: list
#
#####################################################################################################
ret = client.lop_create('test:list_1', ArcusTranscoder.FLAG_STRING, timeout)
print(ret.get_result())
assert ret.get_result() == True

items = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5', 'item 6']

for item in items:
	ret = client.lop_insert('test:list_1', -1, item)
	print(ret.get_result())
	assert ret.get_result() == True

ret = client.lop_get('test:list_1', (0, -1))
print(ret.get_result())
assert ret.get_result() == items

ret = client.lop_get('test:list_1', (2, 4))
print(ret.get_result())
assert ret.get_result() == items[2:4+1]

ret = client.lop_get('test:list_1', (1, -2))
print(ret.get_result())
assert ret.get_result() == items[1:-2+1]



#####################################################################################################
#
# TEST 3: set
#
#####################################################################################################
ret = client.sop_create('test:set_1', ArcusTranscoder.FLAG_STRING, timeout)
print(ret.get_result())
assert ret.get_result() == True

items = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5', 'item 6']
set_items = set()
for item in items:
	set_items.add(item)

for item in set_items:
	ret = client.sop_insert('test:set_1', item)
	print(ret.get_result())
	assert ret.get_result() == True

ret = client.sop_get('test:set_1')
print(ret.get_result())
assert ret.get_result() == set_items

for item in set_items:
	ret = client.sop_exist('test:set_1', item)
	print(ret.get_result())
	assert ret.get_result() == True

ret = client.sop_exist('test:set_1', 'item 100')
print(ret.get_result())
assert ret.get_result() == False



#####################################################################################################
#
# TEST 4: btree
#
#####################################################################################################
def itoh(i):
	h = hex(i)
	if len(h) % 2 == 1:
		h = '0x0%s' % h[2:].upper()
	else:
		h = '0x%s' % h[2:].upper()

	return h
	


# int key
ret = client.bop_create('test:btree_int', ArcusTranscoder.FLAG_INTEGER, timeout)
print (ret.get_result())
assert ret.get_result() == True

for i in range(0, 1000):
	ret = client.bop_insert('test:btree_int', i, i, itoh(i))
	print(ret.get_result())
	assert ret.get_result() == True

ret = client.bop_get('test:btree_int', (200, 400))
print(ret.get_result())

result = ret.get_result()
for i in range(200, 400):
	assert result[i] == (itoh(i), i)

ret = client.bop_count('test:btree_int', (100, 199))
print(ret.get_result())
assert ret.get_result() == 100





# hex key
ret = client.bop_create('test:btree_hex', ArcusTranscoder.FLAG_STRING, timeout)
print (ret.get_result())
assert ret.get_result() == True

for i in range(0x10000, 0x10200):
	ret = client.bop_insert('test:btree_hex', itoh(i), 'bop item %d' % i, itoh(i))
	print(ret.get_result())
	assert ret.get_result() == True

ret = client.bop_get('test:btree_hex', ('0x010050', '0x010150'))
print(ret.get_result())

result = ret.get_result()
for i in range(0x10050, 0x10150):
	assert result[itoh(i)] == (itoh(i), 'bop item %d' % i)




# eflag test

ret = client.bop_create('test:btree_eflag', ArcusTranscoder.FLAG_INTEGER, timeout)
print (ret.get_result())
assert ret.get_result() == True

for i in range(0, 1000):
	ret = client.bop_insert('test:btree_eflag', i, i, itoh(i))
	print(ret.get_result())
	assert ret.get_result() == True

ret = client.bop_get('test:btree_eflag', (200, 400), EflagFilter('EFLAG & 0x00ff == 0x0001'))
print(ret.get_result())
result = ret.get_result()
assert result[257] == ('0x0101', 257)

ret = client.bop_get('test:btree_eflag', (200, 400), EflagFilter('EFLAG & 0x00ff > 0x0010'))
print(ret.get_result())
result = ret.get_result()

for i in range(200, 401):
	if (len(itoh(i)) < 6): 
		if i in result:
			assert False
		continue

	if (i & 0x00ff) <= 0x0010:
		if i in result:
			assert False
		continue

	assert result[i] == (itoh(i), i)




#####################################################################################################
#
# TEST 5: btree mget, smget
#
#####################################################################################################
# int key
ret = client.bop_create('test:btree_1', ArcusTranscoder.FLAG_INTEGER, timeout)
print (ret.get_result())
assert ret.get_result() == True

for i in range(0, 1000):
	ret = client.bop_insert('test:btree_1', i, i, itoh(i))
	print(ret.get_result())
	assert ret.get_result() == True


ret = client.bop_create('test:btree_2', ArcusTranscoder.FLAG_INTEGER, timeout)
print (ret.get_result())
assert ret.get_result() == True

for i in range(1000, 2000):
	ret = client.bop_insert('test:btree_2', i, i, itoh(i))
	print(ret.get_result())
	assert ret.get_result() == True

ret = client.bop_create('test:btree_3', ArcusTranscoder.FLAG_INTEGER, timeout)
print (ret.get_result())
assert ret.get_result() == True

for i in range(2000, 3000):
	ret = client.bop_insert('test:btree_3', i, i, itoh(i))
	print(ret.get_result())
	assert ret.get_result() == True



ret = client.bop_mget(['test:btree_1', 'test:btree_2', 'test:btree_3', 'test:btree_4', 'test:btree_5'], (500, 2500))
print(ret.get_result())


ret = client.bop_smget(['test:btree_1', 'test:btree_2', 'test:btree_3', 'test:btree_4', 'test:btree_5'], (500, 2500))

print(ret.get_result())
result = ret.get_result()
missed_key = ret.get_missed_key()

idx = 500
for item in result:
	if item[0] != idx: # bkey
		print(item[0])
		print(idx)

	assert item[0] == idx # bkey
	assert item[1][:11] == 'test:btree_' # key
	assert item[2] == itoh(idx) # eflag
	assert item[3] == idx # value
	idx += 1
	
assert missed_key == ['test:btree_4', 'test:btree_5']




#####################################################################################################
#
# TEST 6: dynamic list
#
#####################################################################################################

arcus_list = client.list_alloc('test:arcus_list', ArcusTranscoder.FLAG_STRING, 5)
print (arcus_list)
assert arcus_list == []

items = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5', 'item 6']

for item in items:
	arcus_list.append(item)

print (arcus_list)
assert arcus_list == items
print (arcus_list[2:4])
assert arcus_list[2:4] == items[2:4]
print (arcus_list[:2])
assert arcus_list[:2] == items[:2]
print (arcus_list[3:])
assert arcus_list[3:] == items[3:]


print('## for loop test')
idx = 0
for a in arcus_list:
	print(a)
	assert a == items[idx]
	idx += 1


# cached ArcusList Test
arcus_list = client.list_alloc('test:arcus_list_cache', ArcusTranscoder.FLAG_STRING, 5, cache_time=10)
assert arcus_list == []

items = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5', 'item 6']

for item in items:
	arcus_list.append(item)

print (arcus_list)
assert arcus_list == items
print (arcus_list[2:4])
assert arcus_list[2:4] == items[2:4]
print (arcus_list[:2])
assert arcus_list[:2] == items[:2]
print (arcus_list[3:])
assert arcus_list[3:] == items[3:]


print('## for loop test')
idx = 0
for a in arcus_list:
	print(a)
	assert a == items[idx]
	idx += 1

#####################################################################################################
#
# TEST 7: dynamic set
#
#####################################################################################################


arcus_set = client.set_alloc('test:arcus_set', ArcusTranscoder.FLAG_STRING, 5)
print (arcus_set)

items = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5', 'item 6']

for item in items:
	arcus_set.add(item)

print (arcus_set)

print('## for loop test')
for a in arcus_set:
	print(a)

for a in items:
	assert a in arcus_set

print ('### test done ###')
client.disconnect()




