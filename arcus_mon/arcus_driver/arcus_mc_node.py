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
 

import sys
import socket
import time
import os
import re
import threading
from threading import Lock
import select

from arcus import *


# Some parts of Connection and ArcusMCNode is came from python memcache module
class Connection(object):
	def __init__(self, host):
		ip, port = host.split(':')
		self.ip = ip
		self.port = int(port)
		self.address = ( self.ip, self.port )

		self.socket = None
		self.buffer = b''

		self.connect()

	def connect(self):
		if self.socket:
			disconnect()

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.socket.connect(self.address)
		except socket.timeout as msg:
			self.disconnect()
		except socket.error as msg:
			self.disconnect()

		self.buffer = b''
		return self.socket

	def disconnect(self):
		if self.socket:
			self.socket.close()
			self.socket = None

	def disconnected(self):
		return self.socket == None

	def send_request(self, request):
		arcuslog(self, 'send_request: ', request + b'\r\n')
		self.socket.sendall(request + b'\r\n')

	def hasline(self):
		index = self.buffer.find(b'\r\n')
		return index >= 0

	def readline(self):
		buf = self.buffer

		while True:
			index = buf.find(b'\r\n')
			if index >= 0:
				break

			data = self.socket.recv(4096)
			arcuslog(self, 'sock recv: (%d): "' % len(data), data)

			if data == None:
				self.disconnect()
				raise ArcusNodeConnectionException('connection lost')

			buf += data

		self.buffer = buf[index+2:]

		arcuslog(self, 'readline: ', buf[:index])
		return buf[:index]

	def recv(self, rlen):
		buf = self.buffer
		while len(buf) < rlen:
			foo = self.socket.recv(max(rlen - len(buf), 4096))
			arcuslog(self, 'sock recv: (%d): ' % len(foo), foo)

			buf += foo
			if foo == None:
				raise ArcusNodeSocketException('Read %d bytes, expecting %d, read returned 0 length bytes' % ( len(buf), rlen ))

		self.buffer = buf[rlen:]
		arcuslog(self, 'recv: ', buf[:rlen])
		return buf[:rlen]


class ArcusMCNode:
	worker = None
	shutdown = False

	def __init__(self, addr, name, transcoder, node_allocator):
		#mandatory files
		self.addr = addr
		self.name = name
		self.in_use = False
		self.transcoder = transcoder

		self.handle = Connection(addr)
		self.ops = []
		self.lock = Lock() # for ordering worker.q and ops

		self.node_allocator = node_allocator

	def __repr__(self):
		return '%s-%s' % (self.addr, self.name)

	def get_fileno(self):
		return self.handle.socket.fileno()

	def disconnect(self):
		# disconnect socket
		self.handle.disconnect()

		# clear existing operation
		for op in self.ops:
			op.set_invalid()

		self.ops = []
		
	def disconnect_all(self): # shutdown
		self.node_allocator.shutdown = True
		self.disconnect()

		self.node_allocator.worker.q.put(None)
		
	def process_request(self, request):
		if self.handle.disconnected():
			ret = self.handle.connect()
			if ret != None:
				# re-register if node connection is available
				self.node_allocator.worker.register_node(self)

		self.handle.send_request(request)



	##########################################################################################
	### commands
	##########################################################################################
	def get(self, key):
		return self._get('get', key)

	def gets(self, key):
		return self._get('gets', key)

	def set(self, key, val, exptime=0):
		return self._set("set", key, val, exptime)

	def cas(self, key, val, cas_id, exptime=0):
		return self._cas(key, 'cas', val, cas_id, exptime)

	def incr(self, key, value=1):
		return self._incr_decr("incr", key, value)

	def decr(self, key, value=1):
		return self._incr_decr("decr", key, value)

	def add(self, key, val, exptime=0):
		return self._set("add", key, val, exptime)

	def append(self, key, val, exptime=0):
		return self._set("append", key, val, exptime)

	def prepend(self, key, val, exptime=0):
		return self._set("prepend", key, val, exptime)

	def replace(self, key, val, exptime=0):
		return self._set("replace", key, val, exptime)

	def delete(self, key):
		full_cmd = "delete %s" % key
		return self.add_op('delete', bytes(full_cmd, 'utf-8'), self._recv_delete)

	def flush_all(self):
		full_cmd = b'flush_all'
		return self.add_op('flush_all', full_cmd, self._recv_ok)

	def get_stats(self, stat_args = None):
		if stat_args == None:
			full_cmd = b'stats'
		else:
			full_cmd = bytes('stats ' + stat_args, 'utf-8')

		op = self.add_op('stats', full_cmd, self._recv_stat)

	def lop_create(self, key, flags, exptime=0, noreply=False, attr=None):
		return self._coll_create('lop create', key, flags, exptime, noreply, attr)

	def lop_insert(self, key, index, value, noreply=False, pipe=False, attr=None):
		return self._coll_set('lop insert', key, index, value, noreply, pipe, attr)

	def lop_delete(self, key, range, drop=False, noreply=False, pipe=False):
		option = ''
		if drop == True:
			option += 'drop'

		if noreply == True:
			option += ' noreply'

		if pipe == True:
			assert noreply == False
			option += ' pipe'

		if isinstance(range, tuple):
			full_cmd = bytes('lop delete %s %d..%d %s' % (key, range[0], range[1], option), 'utf-8');
			return self.add_op('lop delete', full_cmd, self._recv_delete, noreply or pipe)
		else:
			full_cmd = bytes('lop delete %s %d %s' % (key, range, option), 'utf-8');
			return self.add_op('lop delete', full_cmd, self._recv_delete, noreply or pipe)


	def lop_get(self, key, range, delete=False, drop=False):
		return self._coll_get('lop get', key, range, self._recv_lop_get, delete, drop)

	def sop_create(self, key, flags, exptime=0, noreply=False, attr=None):
		return self._coll_create('sop create', key, flags, exptime, noreply, attr)

	def sop_insert(self, key, value, noreply=False, pipe=False, attr=None):
		return self._coll_set('sop insert', key, None, value, noreply, pipe, attr)

	def sop_get(self, key, count=0, delete=False, drop=False):
		return self._coll_get('sop get', key, count, self._recv_sop_get, delete, drop)

	def sop_delete(self, key, val, drop=False, noreply=False, pipe=False):
		flags, len, value = self.transcoder.encode(val)

		option = '%d' % len
		if drop == True:
			option += 'drop'

		if noreply == True:
			option += ' noreply'

		if pipe == True:
			assert noreply == False
			option += ' pipe'

		option += '\r\n'

		full_cmd = bytes('sop delete %s %s' % (key, option), 'utf-8') + value;
		return self.add_op('sop delete', full_cmd, self._recv_delete, noreply or pipe)

	def sop_exist(self, key, val, pipe=False):
		flags, len, value = self.transcoder.encode(val)

		option = '%d' % len
		if pipe == True:
			assert noreply == False
			option += ' pipe'

		option += '\r\n'

		full_cmd = bytes('sop exist %s %s' % (key, option), 'utf-8') + value
		return self.add_op('sop exist', full_cmd, self._recv_exist, pipe)


	def bop_create(self, key, flags, exptime=0, noreply=False, attr=None):
		return self._coll_create('bop create', key, flags, exptime, noreply, attr)

	def bop_insert(self, key, bkey, value, eflag=None, noreply=False, pipe=False, attr=None):
		return self._coll_set('bop insert', key, None, value, noreply, pipe, attr, bkey, eflag)

	def bop_upsert(self, key, bkey, value, eflag=None, noreply=False, pipe=False, attr=None):
		return self._coll_set('bop upsert', key, None, value, noreply, pipe, attr, bkey, eflag)

	def bop_update(self, key, bkey, value, eflag=None, noreply=False, pipe=False, attr=None):
		return self._coll_set('bop update', key, None, value, noreply, pipe, attr, bkey, eflag)

	def bop_delete(self, key, range, filter=None, count=None, drop=False, noreply=False, pipe=False):
		option = ''

		if filter != None:
			option += filter.get_expr() + ' '

		if count != None:
			option += '%d ' % count

		if drop == True:
			option += 'drop'

		if noreply == True:
			option += ' noreply'

		if pipe == True:
			assert noreply == False
			option += ' pipe'

		if isinstance(range, tuple):
			if isinstance(range[0], str):
				if range[0][:2] != '0x' or range[1][:2] != '0x':
					raise CollectionHexFormat()

				full_cmd = bytes('bop delete %s %s..%s %s' % (key, range[0], range[1], option), 'utf-8')
				return self.add_op('bop delete', full_cmd, self._recv_delete, noreply or pipe)
			else:
				full_cmd = bytes('bop delete %s %d..%d %s' % (key, range[0], range[1], option), 'utf-8')
				return self.add_op('bop delete', full_cmd, self._recv_delete, noreply or pipe)
		else:
			if isinstance(range, str):
				if range[:2] != '0x':
					raise CollectionHexFormat()

				full_cmd = bytes('bop delete %s %s %s' % (key, range, option), 'utf-8')
				return self.add_op('bop delete', full_cmd, self._recv_delete, noreply or pipe)
			else:
				full_cmd = bytes('bop delete %s %d %s' % (key, range, option), 'utf-8')
				return self.add_op('bop delete', full_cmd, self._recv_delete, noreply or pipe)

	def bop_get(self, key, range, filter=None, delete=False, drop=False):
		return self._coll_get('bop get', key, range, self._recv_bop_get, delete, drop, filter=filter)

	def bop_mget(self, key_list, range, filter=None, offset=None, count=50):
		return self._coll_mget('bop mget', key_list, range, filter, offset, count)

	def bop_smget(self, key_list, range, filter=None, offset=None, count=2000):
		return self._coll_mget('bop smget', key_list, range, filter, offset, count)

	def bop_count(self, key, range, filter):
		return self._coll_get('bop count', key, range, self._recv_bop_get, filter=filter)

	def bop_incr(self, key, bkey, value, noreply=False, pipe=False):
		return self._bop_incrdecr('bop incr', key, bkey, value, noreply, pipe)
		
	def bop_decr(self, key, bkey, value, noreply=False, pipe=False):
		return self._bop_incrdecr('bop decr', key, bkey, value, noreply, pipe)


	##########################################################################################
	### Queue senders
	##########################################################################################
	def add_op(self, cmd, full_cmd, callback, noreply = False):
		op = ArcusOperation(self, full_cmd, callback)
		arcuslog(self, 'add operation %s(%s:%s) to %s' % (full_cmd, callback, hex(id(op)), self))

			
		if noreply: # or pipe
			# don't need to receive response, set_result now
			self.node_allocator.worker.q.put(op)
			op.set_result(True)
		else:
			self.lock.acquire()
			self.node_allocator.worker.q.put(op)
			self.ops.append(op)
			self.lock.release()

		return op

	def _get(self, cmd, key):
		full_cmd = bytes("%s %s" % (cmd, key), 'utf-8')
		if cmd == 'gets':
			callback = self._recv_cas_value
		else:
			callback = self._recv_value

		op = self.add_op(cmd, full_cmd, callback)
		return op

	def _set(self, cmd, key, val, exptime=0):
		flags, len, value = self.transcoder.encode(val)
		if flags == None:
			return(0)

		full_cmd = bytes("%s %s %d %d %d\r\n" % (cmd, key, flags, exptime, len), 'utf-8')
		full_cmd += value

		op = self.add_op(cmd, full_cmd, self._recv_set)
		return op 

	def _cas(self, cmd, key, val, cas_id, exptime=0):
		flags, len, value = self.transcoder.encode(val)
		if flags == None:
			return(0)

		full_cmd = bytes("%s %s %d %d %d %d\r\n" % (cmd, key, flags, exptime, len, cas_id), 'utf-8')
		full_cmd += value

		op = self.add_op(cmd, full_cmd, self._recv_set)
		return op 

	def _incr_decr(self, cmd, key, value):
		full_cmd = "%s %s %d" % (cmd, key, value)

		op = self.add_op(cmd, bytes(full_cmd, 'utf-8'), self._recv_set)
		return op

	def _coll_create(self, cmd, key, flags, exptime=0, noreply=False, attr=None):
		if attr == None:
			attr = {}

		# default value
		if 'maxcount' not in attr:
			attr['maxcount'] = 4000
		if 'ovflaction' not in attr:
			attr['ovflaction'] = 'tail_trim'
		if 'readable' not in attr:
			attr['readable'] = True

		option = '%d %d %d' % (flags, exptime, attr['maxcount'])
		if attr['ovflaction'] != 'tail_trim':
			option += ' ' + attr['ovflaction']
		if attr['readable'] == False:
			option += ' unreadable'

		if noreply == True:
			option += ' noreply'

		full_cmd = bytes('%s %s %s' % (cmd, key, option), 'utf-8')
		return self.add_op(cmd, full_cmd, self._recv_coll_create, noreply)

	def _bop_incrdecr(self, cmd, key, bkey, val, noreply=False, pipe=False):
		if isinstance(val, int):
			value = '%d' % val
		else:
			value = val

		if isinstance(bkey, int):
			bkey_str = '%d' % bkey
		else:
			if bkey[:2] != '0x':
				raise CollectionHexFormat()
			bkey_str = '%s' % bkey

		option = '%s %s' % (bkey_str, value)
	
		if noreply == True:
			option += ' noreply'

		if pipe == True:
			assert noreply == False
			option += ' pipe'

		full_cmd = bytes('%s %s %s' % (cmd, key, option), 'utf-8')
		return self.add_op(cmd, full_cmd, self._recv_set, noreply or pipe)

	def _coll_set(self, cmd, key, index, val, noreply=False, pipe=False, attr=None, bkey=None, eflag=None):
		flags, len, value = self.transcoder.encode(val)

		if bkey != None:	# bop
			assert index == None

			if isinstance(bkey, int):
				bkey_str = '%d' % bkey
			else:
				if bkey[:2] != '0x':
					raise CollectionHexFormat()
				bkey_str = '%s' % bkey

			if eflag != None:
				if eflag[:2] != '0x':
					raise CollectionHexFormat()
				option = '%s %s %d' % (bkey_str, eflag, len)
			else:
				option = '%s %d' % (bkey_str, len)
		elif index != None:	# lop
			option = '%d %d' % (index, len)
		else:			# sop
			option = '%d' % (len)
	
		if attr != None:
			# default mandatory value
			if 'flags' not in attr:
				attr['flags'] = 0
			if 'exptime' not in attr:
				attr['exptime'] = 0
			if 'maxcount' not in attr:
				attr['maxcount'] = 4000

			option += ' create %d %d %d' % (attr['flags'], attr['exptime'], attr['maxcount'])
			if 'ovflaction' in attr:
				option += ' ' + attr['ovflaction']
			if 'readable' in attr and attr['readable'] == False:
				option += ' unreadable'

		if noreply == True:
			option += ' noreply'

		if pipe == True:
			assert noreply == False
			option += ' pipe'

		option += '\r\n'

		full_cmd = bytes('%s %s %s' % (cmd, key, option), 'utf-8') + value
		return self.add_op(cmd, full_cmd, self._recv_coll_set, noreply or pipe)

	def _coll_get(self, cmd, key, range, callback, delete=None, drop=None, filter=None):
		option = ''
		type = cmd[:3]

		if filter != None:
			option += filter.get_expr() + ' '

		if delete == True:
			option += 'delete'

		if drop == True:
			assert delete == False
			option += 'drop'

		if isinstance(range, tuple):
			if type == 'bop' and isinstance(range[0], str):
				if range[0][:2] != '0x' or range[1][:2] != '0x':
					raise CollectionHexFormat()

				full_cmd = bytes("%s %s %s..%s %s" % (cmd, key, range[0], range[1], option), 'utf-8')
				return self.add_op(cmd, full_cmd, callback);
			else:
				full_cmd = bytes("%s %s %d..%d %s" % (cmd, key, range[0], range[1], option), 'utf-8')
				return self.add_op(cmd, full_cmd, callback);
		else:
			if type == 'bop' and isinstance(range, str):
				if range[:2] != '0x':
					raise CollectionHexFormat()

				full_cmd = bytes("%s %s %s %s" % (cmd, key, range, option), 'utf-8')
				return self.add_op(cmd, full_cmd, callback);
			else:
				full_cmd = bytes("%s %s %d %s" % (cmd, key, range, option), 'utf-8')
				return self.add_op(cmd, full_cmd, callback);


	def _coll_mget(self, org_cmd, key_list, range, filter, offset, count):

		comma_sep_keys = ''
		for key in key_list:
			if comma_sep_keys != '':
				comma_sep_keys += ','
			comma_sep_keys += key

		cmd = '%s %d %d ' % (org_cmd, len(comma_sep_keys), len(key_list))

		if isinstance(range, tuple):
			if isinstance(range[0], str):
				if range[0][:2] != '0x' or range[1][:2] != '0x':
					raise CollectionHexFormat()

				cmd += '%s..%s' % range
			else:
				cmd += '%d..%d' % range
		else:
			if isinstance(range, str):
				if range[:2] != '0x':
					raise CollectionHexFormat()

				cmd += '%s' % range
			else:
				cmd += '%d' % range

		if filter != None:
			cmd += ' ' + filter.get_expr()

		if offset != None:
			cmd += ' %d' % offset
		cmd += ' %d' % count

		cmd += '\r\n%s' % comma_sep_keys
		cmd = bytes(cmd, 'utf-8')

		if org_cmd == 'bop mget':
			reply = self._recv_mget
		else:
			reply = self._recv_smget
		
		op = self.add_op(org_cmd, cmd, reply)

		return op 

	

	##########################################################################################
	### recievers
	##########################################################################################
	def do_op(self):
		self.lock.acquire()
		if len(self.ops) <= 0:
			assert False
			self.lock.release()

		op = self.ops.pop(0)
		self.lock.release()

		ret = op.callback()
		op.set_result(ret)

		while self.handle.hasline(): # remaining jobs
			self.lock.acquire()
			op = self.ops.pop(0)
			self.lock.release()

			ret = op.callback()
			op.set_result(ret)

	def _recv_ok(self):
		line = self.handle.readline()
		if line == b'OK':
			return True

		return False

	def _recv_stat(self):
		data = {}
		while True:
			line = handle.readline()
			if line[:3] == b'END' or line is None:
				break

			dummy, k, v = line.split(' ', 2)
			data[k] = v

			return data

	def _recv_set(self):
		line = self.handle.readline()
		if line[0:8] == b'RESPONSE':
			dummy, count = line.split()

			ret = []
			for i in range(0, int(count)):
				line = self.handle.readline()
				ret.append(line.decode('utf-8'))

			line = self.handle.readline() # b'END'
		
			return ret
				
			
		if line == b'STORED':
			return True

		if line == b'NOT_FOUND':
			return False

		if line == b'TYPE_MISMATCH':
			raise CollectionType()

		if line == b'OVERFLOWED':
			raise CollectionOverflow() 

		if line == b'OUT_OF_RANGE':
			raise CollectionIndex()

		if line.isdigit():	# incr, decr, bop incr, bop decr
			return int(line)

		return False

	def _recv_delete(self):
		line = self.handle.readline()
		if line[0:8] == b'RESPONSE':
			dummy, count = line.split()

			ret = []
			for i in range(0, int(count)):
				line = self.handle.readline()
				ret.append(line.decode('utf-8'))

			line = self.handle.readline() # b'END'
		
			return ret
				
		if line == b'DELETED':
			return True

		if line == b'NOT_FOUND':
			return True # True ?? (or exception)

		if line == b'TYPE_MISMATCH':
			raise CollectionType()

		if line == b'OVERFLOWED':
			raise CollectionOverflow() 

		if line == b'OUT_OF_RANGE' or line == b'NOT_FOUND_ELEMENT':
			raise CollectionIndex()

		return False

	def _recv_cas_value(self): 
		line = self.handle.readline()
		if line and line[:5] != b'VALUE':
			return None

		resp, rkey, flags, len, cas_id = line.split()
		flags = int(flags)
		rlen = int(len)
		val = self._decode_value(flags, rlen)
		return (val, cas_id)

	def _recv_value(self):
		line = self.handle.readline()
		if line and line[:5] != b'VALUE':
			return None

		resp, rkey, flags, len = line.split()
		flags = int(flags)
		rlen = int(len)
		return self._decode_value(flags, rlen)

	def _recv_coll_create(self):
		line = self.handle.readline()
		if line == b'CREATED':
			return True

		if line == b'EXISTS':
			raise CollectionExist()

		return False

	def _recv_coll_set(self):
		line = self.handle.readline()
		if line[0:8] == b'RESPONSE':
			dummy, count = line.split()

			ret = []
			for i in range(0, int(count)):
				line = self.handle.readline()
				ret.append(line.decode('utf-8'))

			line = self.handle.readline() # b'END'
		
			return ret
				
		if line == b'STORED':
			return True

		if line == b'NOT_FOUND':
			return False

		if line == b'TYPE_MISMATCH':
			raise CollectionType()

		if line == b'OVERFLOWED':
			raise CollectionOverflow() 

		if line == b'OUT_OF_RANGE':
			raise CollectionIndex()

		return False

	def _recv_lop_get(self):
		ret, value = self._decode_collection('lop')
		if ret == b'NOT_FOUND':
			return None

		if ret == b'TYPE_MISMATCH':
			raise CollectionType()


		if ret == b'UNREADABLE':
			raise CollectionUnreadable() 

		if ret == b'OUT_OF_RANGE' or ret == b'NOT_FOUND_ELEMENT':
			value = []

		return value

	def _recv_sop_get(self):
		ret, value = self._decode_collection('sop')
		if ret == b'NOT_FOUND':
			return None

		if ret == b'TYPE_MISMATCH':
			raise CollectionType()

		if ret == b'UNREADABLE':
			raise CollectionUnreadable() 

		if ret == b'OUT_OF_RANGE' or ret == b'NOT_FOUND_ELEMENT':
			value = set()

		return value

	def _recv_exist(self):
		line = self.handle.readline()
		return line == b'EXIST'

	def _recv_bop_get(self):
		ret, value = self._decode_collection('bop')
		if ret == b'NOT_FOUND':
			return None

		if ret == b'TYPE_MISMATCH':
			raise CollectionType()

		if ret == b'UNREADABLE':
			raise CollectionUnreadable() 

		if ret == b'OUT_OF_RANGE' or ret == b'NOT_FOUND_ELEMENT':
			value = {}

		return value

	def _recv_mget(self):
		ret, value, miss = self._decode_bop_mget()
		if ret == b'NOT_FOUND':
			return None

		if ret == b'TYPE_MISMATCH':
			raise CollectionType()

		if ret == b'UNREADABLE':
			raise CollectionUnreadable() 

		if ret == b'OUT_OF_RANGE' or ret == b'NOT_FOUND_ELEMENT':
			raise CollectionIndex()

		return (value, miss)

	def _recv_smget(self):
		ret, value, miss = self._decode_bop_smget()
		if ret == b'NOT_FOUND':
			return None

		if ret == b'TYPE_MISMATCH':
			raise CollectionType()

		if ret == b'UNREADABLE':
			raise CollectionUnreadable() 

		if ret == b'OUT_OF_RANGE' or ret == b'NOT_FOUND_ELEMENT':
			raise CollectionIndex()

		return (value, miss)




	##########################################################################################
	### decoders
	##########################################################################################
	def _decode_value(self, flags, rlen):
		rlen += 2 # include \r\n
		buf = self.handle.recv(rlen)
		if len(buf) != rlen:
			raise ArcusNodeSocketException("received %d bytes when expecting %d" % (len(buf), rlen))

		if len(buf) == rlen:
			buf = buf[:-2]  # strip \r\n

		val = self.transcoder.decode(flags, buf)

		line = self.handle.readline()
		if line != b'END':
			raise ArcusProtocolException('invalid response expect END but recv: %s' % line)

		return val

	def _decode_collection(self, type):
		if type == 'bop':
			values = {}
		elif type == 'sop':
			values = set()
		else: # lop
			values = []

		while True:
			line = self.handle.readline()
			if line[:5] != b'VALUE' and line[:5] != b'COUNT':
				return (line, values)

			if line[:5] == b'VALUE':
				resp, flags, count = line.split()
				flags = int(flags)
				count = int(count)
			elif line[:5] == b'COUNT':
				cmd, count = line.split(b'=')
				return (cmd, int(count))
			
			for i in range(0, count):
				line = self.handle.readline()
				if type == 'bop': # bop get
					bkey, eflag, length_buf = line.split(b' ', 2)

					if eflag.isdigit(): # eflag not exist
						length = eflag
						eflag = None
						buf = length_buf
					else:
						eflag = eflag.decode('utf-8')
						length, buf = length_buf.split(b' ', 1)

					if bkey.isdigit():
						bkey = int(bkey)
					else:
						bkey = bkey.decode('utf-8')
		
					val = self.transcoder.decode(flags, buf)
					values[bkey] = (eflag, val)
				elif type == 'lop':
					length, buf = line.split(b' ', 1)
					val = self.transcoder.decode(flags, buf)
					values.append(val)
				else: # sop
					length, buf = line.split(b' ', 1)
					val = self.transcoder.decode(flags, buf)
					values.add(val)

		return None

			
	def _decode_bop_mget(self):
		values = {}
		missed_keys = []

		while True:
			line = self.handle.readline()
			if line[:11] == b'MISSED_KEYS':
				dummy, count = line.split(b' ')
				count = int(count)
				for i in range(0, count): 
					line = self.handle.readline()
					missed_keys.append(line.decode('utf-8'))

				continue

			if line[:5] != b'VALUE' and line[:5] != b'COUNT':
				return (line, values, missed_keys)

			ret = line.split()
			key = ret[1].decode('utf-8')
			status = ret[2]

			if status == b'NOT_FOUND':
				missed_keys.append(key)
				continue

			count = 0
			if len(ret) == 5:
				flags = int(ret[3])
				count = int(ret[4])

			val = {}
			for i in range(0, count):
				line = self.handle.readline()
				element, bkey, eflag, length_buf = line.split(b' ', 3)

				if eflag.isdigit(): # eflag not exist
					length = eflag
					eflag = None
					buf = length_buf
				else:
					eflag = eflag.decode('utf-8')
					length, buf = length_buf.split(b' ', 1)

				if bkey.isdigit():
					bkey = int(bkey)
				else:
					bkey = bkey.decode('utf-8')
	
				ret = self.transcoder.decode(flags, buf)
				val[bkey] = (eflag, ret)

			values[key] = val

		return None



	def _decode_bop_smget(self):
		values = []
		missed_keys = []

		while True:
			line = self.handle.readline()
			if line[:11] == b'MISSED_KEYS':
				dummy, count = line.split(b' ')
				count = int(count)
				for i in range(0, count): 
					line = self.handle.readline()
					missed_keys.append(line.decode('utf-8'))

				continue

			if line[:5] != b'VALUE' and line[:5] != b'COUNT':
				return (line, values, missed_keys)

			ret = line.split()
			count = int(ret[1])
			
			for i in range(0, count):
				line = self.handle.readline()
				key, flags, bkey, eflag, length_buf = line.split(b' ', 4)

				if eflag.isdigit(): # eflag not exist
					length = eflag
					eflag = None
					buf = length_buf
				else:
					eflag = eflag.decode('utf-8')
					length, buf = length_buf.split(b' ', 1)

				key = key.decode('utf-8')

				if bkey.isdigit():
					bkey = int(bkey)
				else:
					bkey = bkey.decode('utf-8')
	
				val = self.transcoder.decode(int(flags), buf)
				values.append((bkey, key, eflag, val))

		return None





class EflagFilter:
	def __init__(self, expr = None):
		self.lhs_offset = 0
		self.bit_op = None
		self.bit_rhs = None
		self.comp_op = None
		self.comp_rhs = None

		if expr != None:
			self._parse(expr)

	def get_expr(self):
		expr = ''
		if self.lhs_offset != None:
			expr += '%d' % self.lhs_offset

			if self.bit_op and self.bit_rhs:
				expr += ' %s %s' % (self.bit_op, self.bit_rhs)

			if self.comp_op and self.comp_rhs:
				expr += ' %s %s' % (self.comp_op, self.comp_rhs)

		return expr			

	def _parse(self, expr):
		re_expr = re.compile("EFLAG[ ]*(\[[ ]*([0-9]*)[ ]*\:[ ]*\])?[ ]*(([\&\|\^])[ ]*(0x[0-9a-fA-F]+))?[ ]*(==|\!=|<|>|<=|>=)[ ]*(0x[0-9a-fA-F]+)")

		match = re_expr.match(expr)
		if match == None:
			raise FilterInvalid()
			
		# ( dummy, lhs_offset, dummy, bit_op, bit_rhs, comp_op, comp_rhs )
		g = match.groups()
		dummy_1, self.lhs_offset, dummy_2, self.bit_op, self.bit_rhs, self.comp_op, self.comp_rhs = g
		
		if self.lhs_offset == None:
			self.lhs_offset = 0
		else:
			self.lhs_offset = int(self.lhs_offset)

		if self.comp_op == '==':
			self.comp_op = 'EQ'
		elif self.comp_op == '!=':
			self.comp_op = 'NE'
		elif self.comp_op == '<':
			self.comp_op = 'LT'
		elif self.comp_op == '<=':
			self.comp_op = 'LE'
		elif self.comp_op == '>':
			self.comp_op = 'GT'
		elif self.comp_op == '>=':
			self.comp_op = 'GE'



class ArcusMCPoll(threading.Thread):
	def __init__(self, node_allocator):
		threading.Thread.__init__(self)
		self.epoll = select.epoll()
		self.sock_node_map = {}
		self.node_allocator = node_allocator

	def run(self):
		arcuslog(self, 'epoll start')

		while True:
			events = self.epoll.poll(2)

			if self.node_allocator.shutdown == True:
				arcuslog(self, 'epoll out')
				return

			for fileno, event in events:
				if event & select.EPOLLIN:
					node = self.sock_node_map[fileno]
					node.do_op()

				if event & select.EPOLLHUP:
					print('EPOLL HUP')
					epoll.unregister(fileno)
					node = self.sock_node_map[fileno]
					node.disconnect()
					del self.sock_node_map[fileno]


	def register_node(self, node):
		self.epoll.register(node.get_fileno(), select.EPOLLIN | select.EPOLLHUP)

		arcuslog(self, 'regist node: ', node.get_fileno(), node)
		self.sock_node_map[node.get_fileno()] = node
		
		
		
class ArcusMCWorker(threading.Thread):
	def __init__(self, node_allocator):
		threading.Thread.__init__(self)
		self.q = queue.Queue()
		self.poll = ArcusMCPoll(node_allocator)
		self.poll.start()
		self.node_allocator = node_allocator

	def run(self):
		arcuslog(self, 'worker start')

		while True:
			op = self.q.get()
			if self.node_allocator.shutdown == True:
				arcuslog(self, 'worker done')
				self.poll.join()
				return

			if op == None: # maybe shutdown
				continue
		
			arcuslog(self, 'get operation %s(%s:%s) from %s' % (op.request, op.callback, hex(id(op)), op.node))
			node = op.node
			node.process_request(op.request)


	def register_node(self, node):
		self.poll.register_node(node)
		
		


class ArcusMCNodeAllocator:
	def __init__(self, transcoder):
		self.transcoder = transcoder
		self.worker = ArcusMCWorker(self)
		self.worker.start()
		self.shutdown = False
		

	def alloc(self, addr, name):
		ret = ArcusMCNode(addr, name, self.transcoder, self)
		self.worker.register_node(ret)
		return ret


	def join(self):
		self.worker.join()



