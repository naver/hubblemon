
import time
import socket
import select
import threading
import queue


class tsException(Exception):
	def __init__(self, msg):
		self.msg = msg


class tsConnection:
	def __init__(self):
		self.socket = None
		self.buffer = ''

	def connect(self, addr):
		if self.socket:
			self.disconnect()

		self.addr = addr
		ip, port = addr.split(':')
		address = ( ip, int(port) )

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.socket.connect(address)
		except socket.timeout as msg:
			self.disconnect()
			self.socket = None
			return None
		except socket.error as msg:
			self.disconnect()
			self.socket = None
			return None

		#print(address)
		self.buffer = b''
		self.socket.setblocking(0)

		return self.socket

	def disconnect(self):
		if self.socket:
			self.socket.close()
			self.socket = None

	def disconnected(self):
		return self.socket == None

	def send_request(self, request):
		#print('send_request: ', request + '\r\n')
		self.socket.sendall(bytes(request + '\r\n', 'utf-8'))

	def hasline(self):
		index = self.buffer.find(b'\r\n')
		return index >= 0

	def readline(self, timeout = 0):
		buf = self.buffer

		while True:
			index = buf.find(b'\r\n')
			if index >= 0:
				break

			if timeout > 0:
				ret = select.select([self.socket], [], [], timeout)
			else:
				ret = select.select([self.socket], [], [])

			if ret[0]:
				data = self.socket.recv(4096)
				#print('sock recv: (%d): "%s"' % (len(data), data))
			else:
				return None

			if len(data) <= 0:
				self.disconnect()
				raise tsException('connection lost')

			buf += data

		self.buffer = buf[index+2:]

		#print 'readline: ', buf[:index]
		return buf[:index]

	def recv(self, rlen):
		buf = self.buffer
		while len(buf) < rlen:
			foo = self.socket.recv(max(rlen - len(buf), 4096))
			#print('sock recv: (%d): "%s"' % (len(foo), foo))
			if len(foo) <= 0:
				self.disconnect()
				raise tsException('connection lost')

			buf += foo
			if foo == None:
				raise tsException('Read %d bytes, expecting %d, read returned 0 length bytes' % ( len(buf), rlen ))

		self.buffer = buf[rlen:]
		#print 'recv: ', buf[:rlen]
		return buf[:rlen]


class tsValue:
	def __init__(self, ts, value):
		self.ts = ts

		if isinstance(value, bytes):
			value = value.decode('utf-8')

		self.value = value

	def __str__(self):
		return "%d:%s" % (self.ts, str(self.value))

	def __repr__(self):
		return self.__str__()

	def __eq__(self, rhs):
		if hasattr(rhs, 'ts'):
			return self.ts == rhs.ts and self.value == rhs.value

		return False



class tsCursor:
	def __init__(self):
		self.id = -1
		self.query = ""

		self.names = []
		self.items = []
		self.iter = None

		self.stream = False
		self.closed = False

		self.q = queue.Queue()
		self.callback = None

	def next(self, wait = False):
		while True:
			if self.iter == None:
				self.items = self.q.get() # wait until set
				self.iter = iter(self.items)

			try:
				ret = next(self.iter)
				return ret

			except StopIteration:
				self.iter = None
				if wait == True:
					continue # wait next queue

				return None
			
	def queue_put(self, items):
		self.q.put_nowait(items)

		if self.callback != None:
			self.callback(self)
		

	def set_error(self, msg):
		self.queue_put([tsValue(0, msg)])


class tsClient(threading.Thread):
	def __init__(self, async = True):
		self.handle = tsConnection()
		self.cursor_map = {}
		self.requests = queue.Queue()
		self.quit = False
		self.async = async
		self.lock = threading.Lock()

		if self.async == True:
			threading.Thread.__init__(self)

	def run(self):
		while True:
			ret = self.process_response(0.1)
			if ret == False:
				if self.quit == True:
					return
				else:
					continue

	def connect(self, addr):
		self.handle.connect(addr)
		self.requests.queue.clear()

		if self.async == True:
			self.start()

	def disconnect(self):
		self.handle.disconnect()
		self.quit = True

	def process_list(self, cur):
		i = 0
		items = []

		while True:
			line = self.handle.readline().strip().decode('utf-8')
			if line.startswith("end"):
				break
			else:
				v = tsValue(i, line)
				items.append(v)

			i += 1

		cur.queue_put(items)


	def process_get(self, cur):
		columns = 0
		rows = 0
		items = []

		while True:
			line = self.handle.readline().strip().decode('utf-8')

			if line.startswith("cursor"):
				toks = line.split(" ")
				cursor_id = toks[1]
				if cursor_id != "none":
					cur.id = int(cursor_id)

			elif line.startswith("columns"):
				toks = line.split(" ")
				columns = int(toks[1])

			elif line.startswith("column"):
				if cur.id == -1:
					if columns <= 0 or len(cur.names) >= columns:
						cur.set_error("ERROR COLUMN COUNT (%d/%d)" % (columns, len(cur.names)))

					toks = line.split(" ")
					name = toks[1]
					types = toks[2]
					protocol = toks[3]

					cur.names.append(name)
				else:
					continue

			elif line.startswith("rows"):
				toks = line.split(" ")
				rows = int(toks[1])

			elif line.startswith("end"):
				if cur.id >= 0: # end of stream cursor
					self.cursor_map.delete(cur.id)

				cur.queue_put(items)
				break

			elif line.startswith("continue"):
				if cur.id < 0:
					cur.set_error("ERROR CURSOR ID")

				self.cursor_map[cur.id] = cur
				cur.queue_put(items)
				break

			else: # rows
				toks = line.split(" ")

				ts = int(toks[0])
				values = []

				for item in toks[1:]:
					f = float(item)
					values.append(f)
					
				v = tsValue(ts, values)
				items.append(v)


	def process_execute(self, cur):
		v = tsValue(0, "OK")
		cur.queue_put([v])


	def process_response(self, timeout = 0):
		line = self.handle.readline(timeout).decode('utf-8')
		if line == None:
			return False

		if line.startswith("ERROR"):
			cur = self.requests.get()
			cur.set_error(line)
		elif line.startswith("OK"):
			cur = self.requests.get()

			if cur.query.startswith("list"):
				self.process_list(cur)
			elif cur.query.startswith("get") or cur.query.startswith("sget"):
				self.process_get(cur)
			else:
				self.process_execute(cur)
		elif line.startswith("cursor"): # stream response of another request
			toks = line.split(" ")
			stream_id = int(toks[1])
			if stream_id not in self.cursor_map:
				print("ERROR CURSOR ID %d" % stream_id)
				return False 

			cur = self.cursor_map[stream_id]
			self.process_get(cur)
		else:
			cur = self.requests.get()
			cur.set_error("ERROR PROTOCOL:" + line)

		return True

	def process_sync_response(self, cur):
		line = self.handle.readline(0).decode('utf-8')

		if line == None:
			return False

		if line.startswith("ERROR"):
			cur.set_error(line)
		elif line.startswith("OK"):
			if cur.query.startswith("list"):
				self.process_list(cur)
			elif cur.query.startswith("get") or cur.query.startswith("sget"):
				self.process_get(cur)
			else:
				self.process_execute(cur)
		elif line.startswith("cursor"): # stream response of another request
			toks = line.split(" ")
			stream_id = int(toks[1])
			if stream_id not in self.cursor_map:
				print("ERROR CURSOR ID %d" % stream_id)
				return False 

			self.process_get(cur)
		else:
			cur.set_error("ERROR PROTOCOL:" + line)

		return True


	def request(self, query, callback = None):
		cur = tsCursor()
		cur.query = query

		if query[0] < 'a' or query[0] >'z':
			cur = tsCursor()
			cur.set_error("query error:" + query)
			return cur

		cur.callback = callback


		if self.async == True:
			self.lock.acquire()
			self.requests.put(cur)
			self.handle.send_request(query)
			self.lock.release()
		else:
			self.handle.send_request(query)
			self.process_sync_response(cur)

		return cur



