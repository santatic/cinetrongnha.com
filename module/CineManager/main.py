# import os
from tornado import gen, escape
from base64 import b64encode
from bson.objectid import ObjectId
from time import time
from module import ModuleBase
from core import function
from core.app.movie import MovieManager

class Module(ModuleBase):
	"""docstring for Module"""
	def __init__(self):
		super(Module, self).__init__()
		self.script.extend([
			"/static/js/beautify.js",
		])

	@gen.coroutine
	def form(self, argv):
		json_argv 	= self.post_argv()
		template 	= {
			"post": self.site.render_string(self.module['path'] + "post.html", argv=[json_argv]).decode("utf-8"),
		}
		return self.site.render_string(
			self.module['path'] + "form.html",
			module 	= self.module,
			argv 	= {
				"template": b64encode(escape.json_encode(template).encode("utf-8")),
				"post": '{%% raw module["%s"]["post"] %%}' % self.module['_id'],
				"tab": '{%% raw module["%s"]["tab"] %%}' % self.module['_id'],
			},
		), True

	@gen.coroutine
	def form_post(self, argv):
		json_argv 	= yield self.json(argv)
		post_form 	= self.site.render_string(self.module['path'] + "post.html", argv=json_argv['post'])
		return {"post": post_form, "tab": json_argv['tab']}

	@gen.coroutine
	def json(self, argv):
		self.manager 	= MovieManager(self.site, self.module)
		post_id 		= self.site.get_argument('post', None)
		
		if not post_id and argv and len(argv) > 0:
			post_id = argv[0]
		
		if type(post_id) == str and len(post_id) == 24:
			post_id 	= ObjectId(post_id)

		action 		= self.site.get_argument('action', None)
		
		if action == "findgroup":
			g_name = self.site.get_argument('g_name', None)
			groups = yield self.manager.search_post_group(g_name)
			if groups:
				result = []
				for g in groups:
					result.append({
							"id": str(g['_id']),
							"name": g['name'],
							"post": [str(p) for p in g['post']]
						})
				return {"post": result}
		elif action == "groupofpost":
			if post_id:
				groups = yield self.manager.get_post_group(post_id=post_id, output={"_id": 1, "name": 1, "post": 1})
				# print(groups)
				result = []
				for g in groups:
					result.append({
							"id": str(g['_id']),
							"name": g['name'],
							"post": [str(p) for p in g['post']]
						})
				return {"post": result}
		elif action == "postofgroup":
			g_id = self.site.get_argument('g_id', None)
			if g_id:
				groups = yield self.manager.get_post_group(group_id=g_id, output={"_id": 1, "name": 1, "post": 1})
				if groups and 'post' in groups[0]:
					posts 		= yield self.post_json(post_id= groups[0]['post'])
					posts_argv 	= []
					for post in posts:
						posts_argv.append(self.post_argv(post))
					return {"post": posts_argv}
		
		elif action == "channelofpost":
			if post_id:
				post = yield self.site.db.post.find_one({"_id": post_id}, {"channel": 1})
				result = []
				if post and 'channel' in post:
					channel = yield self.site.db.channel.find({'_id': {"$in": post['channel']}},{"name": 1}).to_list(length=30)
					for c in channel:
						result.append({
								"id": str(c['_id']),
								"name": c['name'],
							})
				return {"post": result}
		elif action == "findchannel":
			c_name = self.site.get_argument('c_name', None)
			
			query = {'site_id': self.site.site_db['_id']}
			if c_name:
				query['name'] = c_name

			channel = yield self.site.db.channel.find(query,{"name": 1}).to_list(length=30)
			result = []
			for c in channel:
				result.append({
						"id": str(c['_id']),
						"name": c['name'],
					})
			return {"post": result}

		elif type(post_id) == ObjectId:
			### public/private/trash/restore post
			if action == "manager":
				post_is 	= self.site.get_argument('is', 'private')
				# public post
				if post_is in ["public","private","trash","restore"]:
					timestep 	= int(self.site.get_argument('timestep', 0))
					update 		= yield self.manager.set_post_access(post_id, access=post_is, timestep=timestep)
					if update:
						return '{"error": 0, "success": "%s successful!"}' % post_is
				#  finished post
				elif post_is == "finished":
					update 		= yield self.manager.set_movie_finished(post_id)
					if update:
						return '{"error": 0, "success": "%s successful!"}' % post_is
				# unfinished post
				elif post_is == "unfinished":
					update 		= yield self.manager.set_movie_unfinished(post_id)
					if update:
						return '{"error": 0, "success": "%s successful!"}' % post_is
				# edit post
				elif post_is == "edit":
					json 	= self.site.get_argument('movie', None)
					if json:
						json 	= escape.json_decode(json)
						if 'chap' in json:
							update 	= yield self.manager.set_movie_chaps(json['chap'], post_id)
						else:
							update 	= yield self.manager.set_movie_info(json, post_id)
						
						if update:
							return '{"error": 0, "success": "edit successful!"}'

				# delete post
				elif post_is == "delete":
					post 	= yield self.manager.db.remove({"_id": post_id, 'site_id': self.site.site_db['_id'], 'post.format': "mv","type": "trash"})	
					if post:
						post 	= yield self.manager.db.remove({"parent_id": post_id, 'site_id': self.site.site_db['_id'], 'post.format': "mvc"})
						if post:
							return '{"error": 0, "success": "delete successful!"}'
				
				# join group
				elif post_is == "joingroup":
					group_id  	= self.site.get_argument('g_id', None)
					group_name  = self.site.get_argument('g_name', None)
					yield self.manager.set_post_group(post_id, group_id, group_name)

				# join group
				elif post_is == "leavegroup":
					group_id  	= self.site.get_argument('g_id', None)
					yield self.manager.leave_post_group(post_id, group_id)
				
				elif post_is == "joinchannel":
					channel_id = self.site.get_argument('c_id', None)
					if type(channel_id) == str and len(channel_id) == 24:
						channel_id 	= ObjectId(channel_id)
						
					result = yield self.site.db.post.update({
							"_id": post_id
						},{
							"$push": {"channel": channel_id}
						}, upsert=True)
					if result and 'n' in result and result['n'] > 0:
						return '{"error": 0, "success": "edit successful!"}'
				elif post_is == "removechannel":
					channel_id = self.site.get_argument('c_id', None)
					if type(channel_id) == str and len(channel_id) == 24:
						channel_id 	= ObjectId(channel_id)
						
					post = yield self.site.db.post.find_one({'_id': post_id}, {"channel": 1})
					if post and 'channel' in post and channel_id in post['channel']:
						channels = [x for x in post['channel'] if x != channel_id]
						result = yield self.site.db.post.update({
							"_id": post_id
						},{
							"$set": {"channel": channels}
						}, upsert=True)
						if result and 'n' in result and result['n'] > 0:
							return '{"error": 0, "success": "edit successful!"}'
			# get post information for editor
			elif action == "edit":
				post 	= yield self.manager.db.find_one({'_id': post_id}, {'post': 1})
				if post:
					return {"post": post['post']}
			# join search list post
			elif action == "search":
				search 	= self.site.get_argument('search', None)
				if search:
					try:
						post_count 	= int(self.site.get_argument('count', 10))
					except Exception as e:
						post_count 	= 10
					# tim danh sach post
					posts_id 		= yield self.manager.search_title_seo(search)
					# ko trung voi post hien co
					posts_id 		= [x for x in posts_id if x != post_id]
					posts 			= yield self.post_json(post_id= posts_id, post_tab= "search", post_count= post_count)
					posts_argv 		= {p['_id']:self.post_argv(p) for p in posts}
					post_result 	= [posts_argv[p] for p in posts_id if p in list(posts_argv.keys())]
					return {"post": post_result}
		### get post content
		if not action:
			post_skip 	= self.site.get_argument('skip', None)
			# post_view 	= self.site.get_argument('view', None)
			post_tab 	= self.site.get_argument('tab', "new")
			post_count 	= int(self.site.get_argument('count', 10))

			posts 		= yield self.post_json(post_id= post_id, post_skip= post_skip, post_tab= post_tab, post_count= post_count)
			# print(posts)
			posts_argv 	= []
			for post in posts:
				posts_argv.append(self.post_argv(post))
			# print(post_argv)
			return {"post": posts_argv, "tab": post_tab}

		return '{"error":1,"success":0}'

	def post_argv(self, post= None):
		if post:
			if 'poster' in post['post']:
				poster 	= post['post']['poster']
			else:
				poster 	= ''
			### seo title generic ###
			if 'title_seo' in post['post']:
				title_seo 	= post['post']['title_seo']
			else:
				title_seo 	= ''
			### link generic ###
			if 'link' in post['post']:
				link 	= post['post']['link']
			else:
				link 	= "%s/%s/%s/%s.html" % (self.site.domain_root, self.site.site_db['page']['name'], post['_id'], title_seo)
			### is public post ###
			if 'access' in post:
				action 			= post['access']['type']
			else:
				action 			= 'private'
			#####
			argv 	= {
				"id" 		: str(post['_id']),
				"poster" 	: poster,
				"link" 		: link,
				"title"		: escape.xhtml_escape("%s - %s (%s)" % (post['post']['title'], post['post']['subtitle'], post['post']['year'])),
				"by" 		: post['user']['first_name'] + ' ' + post['user']['last_name'],
				"view"		: post['view']['count'] if 'view' in post else 0,
				"time"		: post['owner']['time'],
				"action"	: action,
				"finished"	: 'finished' if 'finished' in post['post'] and post['post']['finished'] == True else 'unfinished'
			}
		else:
			argv 	= {
				"id" 		: '{{ id }}',
				"poster" 	: '{{ poster }}',
				"link" 		: '{{ link }}',
				"title"		: '{{ title }}',
				"by" 		: '{{ by }}',
				"view"		: '{{ view }}',
				"time"		: '{{ time }}',
				"action"	: '{{ action }}',
				"finished"	: '{{ finished }}',
			}
		return argv

	@gen.coroutine
	def post_json(self, post_id=None, post_skip=None, post_tab= None, post_count=25):
		if post_count > self.module['setting']['server']['max_count']:
			post_count = self.module['setting']['server']['max_count']
		###
		if type(post_id) == str:
			post_id 	= [ObjectId(p) for p in post_id.split(',')]
		elif type(post_id) == ObjectId:
			post_id 	= [post_id]

		###
		posts 		= []
		if post_count > 0:
			### sap xem theo thoi gian moi nhat
			sort 		= [('access.time', -1)]
			
			# find query
			query	= { 'site_id': self.module['site_id'], "format": "mv"}

			if type(post_id) == list:
				query['_id'] = {'$in': post_id}

			# search movie
			if post_tab != "search":
				# finished post
				if post_tab == "finished":
					query['post.finished'] = True
				
				elif post_tab == "unfinished":
					query['$or'] = [
						{'post.finished' : False},
						{'post.finished': {"$exists": False}}
					]
				
				# public post
				if post_tab == "public":
					query['access.type'] = "public"
				# private post
				elif post_tab == "private":
					query['$or'] =[ {"access.type":"private"}, {"access.type": {"$exists": False}}]
				# trash post
				elif post_tab == "trash":
					query['access.type'] = "trash"
				# new post : mac dinh ko co trong trash
				else:
					query['access.type'] = {"$nin": ["trash"]}

			# run search
			cursor 		= self.manager.db.find(query, {'owner': 1, 'post': 1, 'view.count': 1, 'access.type': 1}).sort(sort)
			if post_skip:
				try:
					cursor = cursor.skip(int(post_skip))
				except:
					pass
			cursor 		= cursor.limit(post_count)

			# insert user info
			users_id 	= {}
			while (yield cursor.fetch_next):
				post 	= cursor.next_object()
				posts.append(post)
				# id cua user post
				users_id[post['owner']['id']] 	= 1
			###
			# lay info cua user comment trong list
			query 		= { "_id": { "$in": list(users_id.keys())} }
			users 		= {}
			cursor 		= self.site.db.user.find(query, {'first_name': 1, 'last_name': 1, 'email': 1, 'picture': 1})
			while (yield cursor.fetch_next):
				user 	= cursor.next_object()
				users[user['_id']] = user
			###
			for post in posts:
				if post['owner']['id'] in users:
					post['user'] = users[post['owner']['id']]
		return posts