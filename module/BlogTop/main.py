import tornado.gen
from tornado import template
from base64 import b64encode
from bson.objectid import ObjectId
from module import ModuleBase
from time import time
from core import function

class Module(ModuleBase):
	"""docstring for Module"""
	@tornado.gen.coroutine
	def form(self, argv):
		json_argv 		= yield self.json(argv)
		###
		posts_form 		= b""
		for argv in json_argv['post']:
			posts_form 	+= self.site.render_string(self.module['path'] + "post.html", argv=argv)
		# generic template for json data
		argv 			= self.post_argv()
		template_form 	= b64encode(self.site.render_string(self.module['path'] + "post.html", argv=argv))
		return self.site.render_string(self.module['path'] + "form.html", module=self.module, form={"posts": posts_form, "template": template_form})
		
	@tornado.gen.coroutine
	def json(self, argv):
		post_id 	= self.site.get_argument('post', None)
		if not post_id:
			post_id 	= argv[0]
		post_time 	= self.site.get_argument('time', None)
		post_view 	= self.site.get_argument('view', None)
		post_count 	= int(self.site.get_argument('count', 30))
		posts 		= yield self.post_json(post_id= post_id, post_time= post_time, post_view= post_view, post_count= post_count)
		posts_argv 	= []
		for post in posts:
			posts_argv.append(self.post_argv(post))
		return {"post": posts_argv}

	def post_argv(self, post= None):
		if post:
			banner 	= ''
			if 'safekid' in post['post'] and post['post']['safekid']:
				content 	= '<img src="/static/image/safekid.png">'
			elif 'picture' in post['post']['content']:
				if 'thumbnail' in post['post']['content'] and 'thumbnail' in self.module['setting']['server'] and self.module['setting']['server']['thumbnail']:
					picture 	= post['post']['content']['thumbnail']
				elif 'medium' in post['post']['content']:
					picture 	= post['post']['content']['medium']
				else:
					picture 	= post['post']['content']['picture']
				content 	= template.Template('<img src="{{ picture }}">').generate(picture=picture).decode("utf-8")
				# banner class
				if 'banner' in post['post'] and post['post']['banner']:
					banner 		= "banner"
			elif 'video' in post['post']['content']:
				content 	= template.Template('<div class="video" link="{{ video }}"></div>').generate(video=post['post']['content']['video']).decode("utf-8")
			else:
				content 	= ""
			###
			if 'seo_title' in post['post']:
				seo_title 	= post['post']['seo_title']
			else:
				seo_title 	= function.seo_encode(post['post']['title'])
			###
			argv 	= {
				"id" 		: str(post['_id']),
				"content" 	: content,
				"link" 		: "%s/%s/%s/%s.html" % (self.site.domain_root, self.module['setting']['server']['page_view'], post['_id'], seo_title),
				"title"		: post['post']['title'],
				"by" 		: post['user']['first_name'] + ' ' + post['user']['last_name'],
				"view"		: post['view']['count'] if 'view' in post else 0,
				"time"		: post['public']['time'],
				"banner" 	: banner,
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
				"banner" 	: '{{ banner }}',
			}
		return argv

	@tornado.gen.coroutine
	def post_json(self, post_id=None, post_time=None, post_view=0, post_count =30):
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

			### limit up time
			if not post_time:
				post_time 			= time()*1000
			post_time 	= int(post_time)
			query['public.time'] 	= {"$lte": int(post_time)}

			### public post only
			query['type'] 	= "public"
			### sap xem theo thoi gian moi nhat
			sort 			= [('public.time', -1)]

			### top type
			top_type 	= None
			if 'top_type' in self.module['setting']['server']:
				top_type 	= self.module['setting']['server']['top_type']
			# sort xem nhieu nhat
			if top_type == "view":
				sort.insert(0, ('view.count', -1))
				# if post_view:
				# 	query['view.count'] = {"$lte": int(post_view)}
				if not post_time:
					post_time 			= time()*1000
				query['public.time']["$gte"] 	= int(post_time - 604800000)

			##################
			cursor 		= self.site.db.post.find(query, {'user_id': -1, 'post': 1, 'view.count': -1, 'public.time': -1}).sort(sort).limit(post_count) # -1: pymongo.DESCENDING
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
