from tornado import gen, ioloop
from bson.binary import Binary
import pickle, hashlib, time

class CacheManager(object):
	"""docstring for CacheManager"""
	def __init__(self, db):
		self.db 		= db
		self.locker 	= {}

	@gen.coroutine
	def set(self, source, data, expire, query=None):
		# build key md5
		m 		= hashlib.md5()
		m.update(source.encode("utf-8"))
		key 	= m.hexdigest()
		if not query:
			query = {}
		query.update({
			"key": key,
			"expire": int(time.time()) + expire,
			"source": source,
			"data": Binary(pickle.dumps(data)),
		})
		# insert cache
		result 	= yield self.db.insert(query)
		# unlock locker if exist
		if key in self.locker:
			del self.locker[key]
		return key, result

	@gen.coroutine
	def get(self, key=None, source=None, query=None, output=None, lock=False, lock_time=1, lock_count=5):
		if not key and source:
			m 		= hashlib.md5()
			m.update(source.encode("utf-8"))
			key 	= m.hexdigest()

		if key:
			if not query:
				query = {}
			if not output:
				output = {}

			query.update({
					'key': key,
					'expire': {"$gte": int(time.time())}
				})
			output.update({
					'data': 1,
					'lock': 1
				})
			# wait for other process caching...
			if lock:
				while key in self.locker and lock_count > 0:
					print("\nwaiting for cache....", lock_count)
					# sleep lock_time 1s
					yield gen.Task(ioloop.IOLoop.instance().add_timeout, time.time() + lock_time)
					# retry sleep count
					lock_count -= 1

			# timeout or unlocked
			result 	= yield self.db.find_one(query, output)
			
			if result and "data" in result:
				result['data'] = pickle.loads(result['data'])
				return result
			else:
				# neu ko co result ma lock thi insert vao truoc va lock lai
				# sau do return None
				if lock:
					self.locker[key] = True
		return None

	@gen.coroutine
	def clear(self, query=None, source=None, everything=False):
		# clear locker
		self.locker = {}
		# clear db
		if not query:
			query = {}

		if source:
			m 		= hashlib.md5()
			m.update(source.encode("utf-8"))
			query['key'] 	= m.hexdigest()

		if not everything:
			query.update({
				"expire": {
					"$lt":int(time.time())
				}
			})
		result = yield self.db.remove(query, multi=True)
		return result