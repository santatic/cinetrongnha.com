from tornado import gen
from bson.objectid import ObjectId
from time import time
from core import function
import re

class AppManager(object):
	"""docstring for AppManager"""
	def __init__(self, site, module):
		self.site 		= site
		self.module 	= module
		self.site_id 	= None
		self.user_id 	= None

	@gen.coroutine
	def user_init(self):
		if not self.site_id:
			self.site_id 	= self.site.site_db['_id']
		
		if not self.user_id:
			session 	= yield self.site.session.get(['user_id'])
			if 'user_id' in session:
				self.user_id 		= session['user_id']

		if self.site_id and self.user_id:
			return True
		return False
	
	# post permission
	# post public: all can view
	# post private: post hidden
	# post trash: post removed
	@gen.coroutine
	def set_post_access(self, post_id, access="private", timestep=0):
		if (yield self.user_init()):
			if type(post_id) == str and re.match(r'[a-z0-9]{24}', post_id):
				post_id = ObjectId(post_id)
			
			if access == "restore":
				access 	= "private"
			now 			= int(time());
			update_time 	= now + timestep
			update 			= yield self.site.db.post.update(
						{"_id": post_id, 'site_id': self.site_id},
						{	
							"$set"	: { "access.type": access, "access.time": update_time},
							"$push"	: {
								"access.info"	: {
									"type"	: access,
									"id"	: self.user_id,
									"time"	: now,
									"ip" 	: self.site.request.remote_ip
								}
							}
						},
						upsert=True
					)
			if 'n' in update and update['n'] > 0:
				return post_id
		return None

	# post in group / in tag / in mind
	@gen.coroutine
	def post_recommend(self, post_id=None, query=None, output=None, count=10):
		if type(post_id) == str and re.match(r'[a-z0-9]{24}', post_id):
			post_id = ObjectId(post_id)

		if type(post_id) == ObjectId:
			if not query:
				query = {}
			query['format'] = "pg"
			result = yield self.get_post_group(post_id=post_id, query=query, output=output)
			if result:
				posts = []
				for g in result:
					if 'post' in g:
						posts += g['post']
				return posts
				
	@gen.coroutine
	def set_post_view(self, post_id):
		now = int(time());
		# if (yield self.user_init()):
		# 	post = yield self.site.db.post_view.find_one({
		# 		'_id': post_id,
		# 		'site_id': self.site_id,
		# 		'view.info': {
		# 			'$elemMatch': {
		# 				'id': self.user_id,
		# 				'time': {"$gte": now - 3600} # 1h truoc
		# 			}
		# 		}
		# 	}, {
		# 		'_id': 1
		# 	})
		# 	print('view --- ',post)
		# else:
		# 	post = None

		# if not post:
		query = {
			'_id': post_id,
			'site_id': self.site.site_db['_id'],
		}
		update = {
			"$inc": {
				"view.count": 1
			}
		}
		# if self.user_id:
		# 	update['$push'] = {
		# 		"view.info": {
		# 			"id": self.user_id,
		# 			"time": now
		# 		} 
		# 	}
		result = yield self.site.db.post.update(query, update)
		if result and 'n' in result and result['n'] > 0:
			return True

	# post view is check user viewing/viewed or don't want to view one post
	@gen.coroutine
	def set_user_view_post(self, post_id, format, access='public', post=None):
		if (yield self.user_init()):
			if not post:
				query = {
					'site_id': self.site_id,
					'user_id': self.user_id,
					'post_id': post_id
				}
				post = yield self.site.db.post_view.find_one(query, {'_id':1})

			now = int(time()*1000)
			# update view
			if post:
				result = yield self.site.db.post_view.update(
					{'_id': post['_id']},
					{'$set': {
						'format': format,
						'time': now,
						'access': access
					}},
					upsert=True
				)
			# insert view
			else:
				query.update({
					'format': format,
					'time': now,
					'access': access
				})
				result = yield self.site.db.post_view.insert(query)
			return result
		return None


	@gen.coroutine
	def get_user_view_post(self, format, post_id=None,  time=None, sort=[('time',1)], count=10, access='public'):
		if (yield self.user_init()):
			query = {
				'site_id': self.site_id,
				'user_id': self.user_id,
				'format': format,
				'access': access
			}
			if post_id:
				query['post_id'] = post_id
				
			if time:
				query['time'] = {'$gte': time}
				
			cursor 		= self.site.db.post_view.find(query).sort(sort)
			result		= yield cursor.to_list(length=count)
			return result
		return None

	# post group is group of all post have group
	# ex: some session of move
	# post group is not tag
	@gen.coroutine
	def set_post_group(self, post_id, group_id=None, group_name=None):
		# BSON ObjectId
		if type(post_id) == str and re.match(r'[a-z0-9]{24}', post_id):
			post_id = ObjectId(post_id)

		if type(post_id) == ObjectId:
			post_id = [post_id]

		if type(post_id) == list and (yield self.user_init()):
			# BSON ObjectId
			if type(group_id) == str and re.match(r'[a-z0-9]{24}', group_id):
				group_id = ObjectId(group_id)

			# create new group
			if not group_id and group_name:
				result = yield self.site.db.post_group.insert({
						"site_id": self.site_id,
						"user_id": self.user_id,
						"name": group_name,
						"name_seo": function.seo_encode(group_name),
						"post": post_id,
						"format": "pg", #post group
					})
			# inset to group
			else:
				result 	= yield self.site.db.post_group.update({
						"_id": group_id,
						"site_id": self.site_id,
						"format": "pg",
					},{
						"$addToSet": {
							"post": {"$each": post_id}
						}
					})
			return result

	# remove group of post
	@gen.coroutine
	def leave_post_group(self, post_id, group_id=None):
		# BSON ObjectId
		if type(post_id) == str and re.match(r'[a-z0-9]{24}', post_id):
			post_id = ObjectId(post_id)

		if type(post_id) == ObjectId:
			post_id = [post_id]

		if type(post_id) == list and (yield self.user_init()):
			# BSON ObjectId
			if type(group_id) == str and re.match(r'[a-z0-9]{24}', group_id):
				group_id = ObjectId(group_id)

			# remove group
			result 	= yield self.site.db.post_group.update({
					"_id": group_id,
					"site_id": self.site_id,
					"format": "pg",
				},{
					"$pull": {
						"post": {"$in": post_id}
					}
				})
			return result

	@gen.coroutine
	def get_post_group(self, group_id=None, post_id=None, query=None, output=None, count=50):
		# BSON ObjectId
		if type(group_id) == str and re.match(r'[a-z0-9]{24}', group_id):
			group_id = ObjectId(group_id)

		if not query:
			query 	= {}

		if type(group_id) == ObjectId:
			query.update({
				"_id": group_id,
				"site_id": self.site.site_db['_id'],
			})
		elif post_id:
			# BSON ObjectId
			if type(post_id) == str and re.match(r'[a-z0-9]{24}', post_id):
				post_id = ObjectId(post_id)

			if type(post_id) == ObjectId:
				query.update({
					"post": post_id,
					"site_id": self.site.site_db['_id']
				})
		else:
			return None
		# print('group query', query)
		if query:
			if not output:
				output = {"post": 1}
			return (yield self.site.db.post_group.find(query, output).to_list(length=count))

	@gen.coroutine
	def _searcher(self, string, find_at, query=None, database=None, count=50, cache=1800):
		if not self.site_id:
			self.site_id 	= self.site.site_db['_id']

		if self.site_id:
			seo_string 	= function.seo_encode(string[:100])
			#  default database
			if not database:
				database = self.site.db.post

			# in cache
			if cache > 0:
				result 	= yield self.site.cache.get(source="%s%s" % (seo_string, find_at))
				if result and 'data' in result:
					return result['data']

			words = []
			word = seo_string
			
			# generic keywork
			while True:
				if word:
					words.append(word)
					if '-' in word:
						# split right
						tmp = word.rsplit('-',1)[0]
						if not tmp in words:
							words.append(tmp)
						
						# split left
						tmp = word.split('-',1)[1]
						if not tmp in words:
							words.append(tmp)

						word = tmp.rsplit('-',1)[0]
						continue
				break
			# start search
			if not query:
				query = {}
			
			query['site_id'] 	= self.site_id
			search_dict 		= {}
			for i, word in enumerate(words, start=1):
				if len(search_dict) > count:
					break
				word 	= word.strip()
				if word:
					# change search query
					query[find_at] = {'$regex': re.compile(".*" + word + ".*", re.IGNORECASE)}
					result = yield database.find(query, {"_id": 1}).to_list(length=count)
					if result:
						for mv in result:
							if mv['_id'] not in search_dict:
								search_dict[mv['_id']] = int(99/i)
							else:
								search_dict[mv['_id']] += int(99/i)

			# sort result
			sort_dict 	= {}
			for k, v in search_dict.items():
				if v not in sort_dict:
					sort_dict[v] 	= [k]
				else:
					sort_dict[v].append(k)
			result 	= [x for k in sorted(sort_dict) for x in sort_dict[k]][::-1][:count]
			
			# cache store
			if cache > 0:
				yield self.site.cache.set(seo_string, result, cache)
			return result
		return []