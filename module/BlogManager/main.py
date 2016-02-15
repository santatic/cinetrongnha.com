import os
from tornado import gen, template
from base64 import b64encode
from bson.objectid import ObjectId
from time import time
from urllib.parse import urlparse
from module import ModuleBase
from core import function


class Module(ModuleBase):
	"""docstring for Module"""
	@gen.coroutine
	def form(self, argv):
		json_argv 		= yield self.json(argv)
		###
		posts_form 		= b""
		for argv in json_argv['post']:
			posts_form 	+= self.site.render_string(self.module['path'] + "post.html", argv=argv)
		# generic template for json data
		argv 			= self.post_argv()
		template_form 	= b64encode(self.site.render_string(self.module['path'] + "post.html", argv=argv))
		return self.site.render_string(self.module['path'] + "form.html", module=self.module, form={"posts": posts_form, "template": template_form}, argv=json_argv['form'])
	
	@gen.coroutine
	def json(self, argv):
		post_id 	= self.site.get_argument('post', None)
		# if not post_id and argv[0]:
		# 	post_id 	= argv[0]
		if type(post_id) == str and len(post_id) == 24:
			post_id 	= ObjectId(post_id)
		action 		= self.site.get_argument('action', None)
		### public/private post ###
		if action == "manager":
			session 		= yield self.site.session.get(['user_id'])
			update_time 	= int(time()*1000);
			if 'user_id' in session:
				post_is 	= self.site.get_argument('is', 'private')
				# public post
				if post_is == "public":
					public_time 	= update_time + int(self.site.get_argument('timestep', 0))
					update 	= yield self.site.db.post.update(
								{"_id": post_id, 'site_id': self.site.db_site['_id']},
								{	
									"$set": { "type": "public", "public.time": public_time},
									"$push": {
										"public.user": {
											"user_id": session['user_id'],
											"time": public_time
										}
									}
								},
								upsert=True
							)
					if update:
						return '{"error": 0, "success": "public sucessful!"}'
				# private post
				elif post_is == "private":
					update 	= yield self.site.db.post.update(
								{"_id": post_id, 'site_id': self.site.db_site['_id']},
								{	
									"$set": { "type": "private", "private.time": update_time},
									"$push": {
										"private.user": {
											"user_id": session['user_id'],
											"time": update_time
										}
									}
								},
								upsert=True
							)
					if update:
						return '{"error": 0, "success": "private sucessful!"}'
				# trash post
				elif post_is == "trash":
					update 	= yield self.site.db.post.update(
								{"_id": post_id, 'site_id': self.site.db_site['_id']},
								{	
									"$set": { "type": "trash", "trash.time": update_time},
									"$push": {
										"trash.user": {
											"user_id": session['user_id'],
											"time": update_time
										}
									}
								},
								upsert=True
							)
					if update:
						return '{"error": 0, "success": "trafunction.seo_encodesh sucessful!"}'
				# restore post
				elif post_is == "restore":
					update 	= yield self.site.db.post.update(
								{"_id": post_id, 'site_id': self.site.db_site['_id']},
								{
									"$set": {"type": "private"}
								}
							)
					if update:
						return '{"error": 0, "success": "restore sucessful!"}'
				# edit post
				elif post_is == "edit":
					post_title 		= self.site.get_argument('p_title', None)
					post_note 		= self.site.get_argument('p_note', "")
					post_source		= self.site.get_argument('p_source', "")
					post_safekid 	= self.site.get_argument('p_safekid', False)
					if post_safekid == "true":
						post_safekid 	= True
					else:
						post_safekid 	= False

					if post_title:
						update 	= yield self.site.db.post.update(
									{"_id": post_id, 'site_id': self.site.db_site['_id']},
									{"$set": {
										"post.title" : post_title,
										"post.seo_title" : function.seo_encode(post_title),
										"post.note" : post_note,
										"post.source" : post_source,
										"post.safekid" : post_safekid
										}
									}	
								)
						if update:
							return '{"error": 0, "success": "edit sucessful!"}'
				# delete post
				elif post_is == "delete":
					post 	= yield self.site.db.post.find_one(
								{"_id": post_id, 'site_id': self.site.db_site['_id'], "type": "trash"},
								{"post": 1}
							)
					if post:
						list_file 	= []
						### old version
						if 'content' in post['post']:
							if 'picture' in post['post']['content']:
								if post['post']['content']['picture'][0] == '/':
									list_file.append('site' + post['post']['content']['picture'])
							if 'thumbnail' in post['post']['content']:
								if post['post']['content']['thumbnail'][0] == '/':
									list_file.append('site' + post['post']['content']['thumbnail'])
							if 'medium' in post['post']['content']:
								if post['post']['content']['medium'][0] == '/':
									list_file.append('site' + post['post']['content']['medium'])
						for pic in list_file:
							if os.path.isfile(pic):
								try:
									os.remove(pic)
								except Exception as e:
									raise e
						post 	= yield self.site.db.post.remove({"_id": post_id, 'site_id': self.site.db_site['_id'], "type": "trash"})	
						if post:
							return '{"error": 0, "success": "delete sucessful!"}'

		elif action == "edit":
			post 	= yield self.site.db.post.find_one({'_id': post_id}, {'post': 1})
			
			if not 'safekid' in post['post']:
				post['post']['safekid'] 	= False
			return {"post": {
						'title'		: post['post']['title'],
						'note'		: post['post']['note'],
						'source'	: post['post']['source'],
						'safekid'	: post['post']['safekid']
					}
				}
		else:
			### get post content ###
			post_time 	= self.site.get_argument('time', None)
			post_view 	= self.site.get_argument('view', None)
			post_tab 	= self.site.get_argument('tab', "new")
			post_count 	= int(self.site.get_argument('count', 10))

			posts 		= yield self.post_json(post_id= post_id, post_time= post_time, post_tab= post_tab, post_view= post_view, post_count= post_count)
			posts_argv 	= []
			for post in posts:
				posts_argv.append(self.post_argv(post))
			return {"post": posts_argv, "form": {"tab": post_tab}}

		return '{"error": 1, "success": 0}'

	def post_argv(self, post= None):
		if post:
			if 'thumbnail' in post['post']['content'] and post['post']['content']['thumbnail']:
				content 	=  template.Template('<img src="{{ picture }}">').generate(picture=post['post']['content']['thumbnail']).decode("utf-8")
			elif 'picture' in post['post']['content'] and post['post']['content']['picture']:
				content 	=  template.Template('<img src="{{ picture }}">').generate(picture=post['post']['content']['picture']).decode("utf-8")
			else:
				content 	= ""
			### seo title generic ###
			if 'seo_title' in post['post']:
				seo_title 	= post['post']['seo_title']
			else:
				seo_title 	= function.seo_encode(post['post']['title'])
			### link generic ###
			if 'link' in post['post']:
				link 	= post['post']['link']
			else:
				link 	= "/%s/%s/%s/%s.html" % (self.site.db_site['name'], self.site.db_page['name'], post['_id'], seo_title)
			### is public post ###
			if 'type' in post:
				action 	= post['type']
			else:
				action 	= 'private'
			#####
			argv 	= {
				"id" 		: str(post['_id']),
				"content" 	: content,
				"link" 		: link,
				"title"		: post['post']['title'],
				"by" 		: post['user']['first_name'] + ' ' + post['user']['last_name'],
				"view"		: post['view']['count'] if 'view' in post else 0,
				"time"		: post['time'],
				"action"	: action,
			}
		else:
			argv 	= {
				"id" 		: '{{ id }}',
				"content" 	: '{{ content }}',
				"link" 		: '{{ link }}',
				"title"		: '{{ title }}',
				"by" 		: '{{ by }}',
				"view"		: '{{ view }}',
				"time"		: '{{ time }}',
				"action"	: '{{ action }}',
			}
		return argv

	@gen.coroutine
	def post_json(self, post_id=None, post_time=None, post_tab= None, post_view=0, post_count =10):
		if post_count > self.module['setting']['server']['max_count']:
			post_count = self.module['setting']['server']['max_count']
		###
		query	= { 'site_id': self.module['site_id']}
		###
		# if 'filter' in self.module['setting']['server']:
		# 	query['post.format'] 	= { "$in": self.module['setting']['server']['filter']}
		# else:
		# 	query['post.format'] 	= { "$in": ["sl", "sv", "si"]}
		###
		if type(post_id) == str:
			post_id 	= [ObjectId(p) for p in post_id.split(',')]
		elif type(post_id) == ObjectId:
			post_id 	= [post_id]

		if type(post_id) == list:
			query['_id'] = {'$nin': post_id}
		###
		posts 		= []
		if post_count > 0:
			users_id 	= {}
			### limit up time
			if post_time:
				query['time'] = {"$lte": int(post_time)}

			### sap xem theo thoi gian moi nhat
			sort 		= [('time', -1)]

			
			# # sort xem nhieu nhat
			# if post_tab == "top":
			# 	sort.insert(0, ('hot', -1))
			# 	# query['time'] = {"$gte": update_time - 864000}
			# # hot = like/time
			# elif post_tab == "hot":
			# 	sort.insert(0, ('view.count', -1))
			# 	if post_view:
			# 		query['view.count'] = {"$lte": int(post_view)}
			# 	# query['time'] = {"$gte": int(time() - 864000)*1000}
			### mac dinh ko co trong trash
			
			# public post
			if post_tab == "public":
				query['type'] = "public"
			# private post
			elif post_tab == "private":
				query['$or'] =[ {"type":"private"}, {"type": {"$exists": False}}]
			# trash post
			elif post_tab == "trash":
				query['type'] = "trash"
			# new
			else:
				query['type'] = {"$nin": ["trash"]}

			cursor 		= self.site.db.post.find(query, {'user_id': 1, 'site_id': 1, 'time': 1, 'like': 1, 'post': 1, 'view.count': 1, 'type': 1}).sort(sort).limit(post_count) # -1: pymongo.DESCENDING
			while (yield cursor.fetch_next):
				post 	= cursor.next_object()
				posts.append(post)
				# id cua user post
				users_id[post['user_id']] 	= 1
			##################
			# lay info cua user comment trong list
			query 		= { "_id": { "$in": list(users_id.keys())} }
			users 		= {}
			cursor 		= self.site.db.user.find(query, {'first_name': 1, 'last_name': 1, 'email': 1, 'picture': 1})
			while (yield cursor.fetch_next):
				user 	= cursor.next_object()
				users[user['_id']] = user
			##################
			for post in posts:
				if post['user_id'] in users:
					post['user'] = users[post['user_id']]
		return posts