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
		if post and 'link' in post['post']:
			if 'thumbnail' in post['post']['picture'] and post['post']['picture']['thumbnail']:
				picture 	=  template.Template('<img src="{{ picture }}">').generate(picture=post['post']['picture']['thumbnail']).decode("utf-8")
			elif 'picture' in post['post']['picture'] and post['post']['picture']['full']:
				picture 	=  template.Template('<img src="{{ picture }}">').generate(picture=post['post']['picture']['full']).decode("utf-8")
			else:
				picture 	= ""
			### seo title generic ###
			if 'seo_title' in post['post']:
				seo_title 	= post['post']['seo_title']
			else:
				seo_title 	= function.seo_encode(post['post']['title'])
			### is public post ###
			if 'type' in post:
				action 	= post['type']
			else:
				action 	= 'private'

			if action in ["private", "trash"]:
				time 	= post['time']
			else:
				time 	= post['public']['time']
			#####
			argv 	= {
				"id" 		: str(post['_id']),
				"picture" 	: picture,
				"link" 		: post['post']['link'],
				"view" 		: "%s://%s/%s/%s/%s/%s.html" % (self.site.request.protocol, self.site.request.host, self.site.db_site['name'], self.module['setting']['server']['page_view'], post['_id'], seo_title),
				"site" 		: urlparse(post['post']['link']).netloc,
				"title"		: post['post']['title'],
				"by" 		: post['user']['first_name'] + ' ' + post['user']['last_name'],
				"view"		: post['view']['count'] if 'view' in post else 0,
				"time"		: time,
			}
		else:
			argv 	= {
				"id" 		: '{{ id }}',
				"picture" 	: '{{ picture }}',
				"link" 		: '{{ link }}',
				"view" 		: '{{ view }}',
				"site" 		: '{{ site }}',
				"title"		: '{{ title }}',
				"by" 		: '{{ by }}',
				"view"		: '{{ view }}',
				"time"		: '{{ time }}',
			}
		return argv

	@gen.coroutine
	def post_json(self, post_id=None, post_time=None, post_tab= None, post_view=0, post_count =30):
		try:
			if post_count > self.module['setting']['server']['max_count']:
				post_count = self.module['setting']['server']['max_count']
		except Exception as e:
			pass
		
		users_id 	= {}
		posts 		= []
		if post_count > 0:
			###
			query	= { 'site_id': self.module['site_id']}
			###
			if 'filter' in self.module['setting']['server']:
				query['post.format'] 	= { "$in": self.module['setting']['server']['filter']}
			# else:
			# 	query['post.format'] 	= { "$in": ["bi", "bv", "bl"]}
			if post_id:
				if type(post_id) == str:
					post_id 	= [ObjectId(p) for p in post_id.split(',')]
				elif type(post_id) == ObjectId:
					post_id 	= [post_id]

				if type(post_id) == list:
					query['_id'] = {'$nin': post_id}

			
			###### tab generic
			if post_tab in ["private", "trash"]:
				self.module['permission'] 	= yield self.permission(self.site.db_site, self.module)
				if self.module['permission']:
					query['type'] 	= post_tab
					sort 			= [('time', -1)]
				else:
					return posts
			else:
				### limit up time
				if not post_time:
					post_time 			= time()*1000
				post_time 	= int(post_time)
				query['public.time'] 	= {"$lte": int(post_time)}
				### public post only
				query['type'] 	= "public"
				### sap xem theo thoi gian moi nhat
				sort 			= [('public.time', -1)]
				# hot = like/view
				if post_tab == "hot":
					sort.insert(0, ('hot', -1))
				# top = sort xem nhieu nhat
				elif post_tab == "top":
					sort.insert(0, ('view.count', -1))
					if post_view:
						query['view.count'] = {"$lte": int(post_view)}
					if not post_time:
						post_time 			= time()*1000
					query['public.time']["$gte"] 	= int(post_time - 604800000)
					# query['time'] = {"$gte": int(time() - 864000)*1000}
			##################
			cursor 		= self.site.db.post.find(query, {'user_id': -1, 'post': 1, 'view.count': -1, 'time': -1, 'public.time': -1}).sort(sort).limit(post_count) # -1: pymongo.DESCENDING
			while (yield cursor.fetch_next):
				post 	= cursor.next_object()
				posts.append(post)
				# id cua user post
				users_id[post['user_id']] 	= 1

			##################
			# lay info cua user comment trong list
			query 		= { "_id": { "$in": list(users_id.keys())}}
			users 		= {}
			cursor 		= self.site.db.user.find(query, {'first_name': 1, 'last_name': 1, 'picture': 1})
			while (yield cursor.fetch_next):
				user 	= cursor.next_object()
				users[user['_id']] = user

			##################
			for post in posts:
				if post['user_id'] in users:
					post['user'] = users[post['user_id']]
		return posts

	@gen.coroutine
	def permission(self, db_site, db_module):
		'''
		module kiem tra user co nam trong groups/users co quyen truy cap website hay ko
		@db_site : data lay tu db cua site
		@db_module : data lay dc tu module
		'''
		if "permission" in db_module:
			session 	= yield self.site.session.get(['user_id'])
			if 'user_id' in session:
				if session['user_id'] in db_module['permission']['users']:
					return True
				for group_id in db_module['permission']['groups']:
					group 		= yield self.db.groups.find_one(
									{'_id': group_id, 'site_id': db_site['_id'], 'type': "usergroup",'users': session['user_id']},
									{"_id": 1}
								)
					if group:
						return True
		else:
			return True
		print("authentication failure!", db_module)
		return False