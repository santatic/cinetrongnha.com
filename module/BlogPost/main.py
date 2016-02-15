from tornado import gen, template, escape
from base64 import b64encode
from bson.objectid import ObjectId
from module import ModuleBase
from core import function

class Module(ModuleBase):
	"""docstring for Module"""
	@gen.coroutine
	def form(self, argv):
		json_argv 			= yield self.json(argv)
		if 'post' in json_argv and json_argv['post']:
			post_form 		= self.site.render_string(self.module['path'] + "post.html", argv=json_argv['post'], module= self.module)
		else:
			post_form 		= "Ảnh đang chờ kiểm duyệt hoặc không tồn tại!"
		# generic template for json data
		argv 				= self.post_argv()
		template_form 		= b64encode(self.site.render_string(self.module['path'] + "post.html", argv=argv, module= self.module))
		
		return self.site.render_string(self.module['path'] + "form.html", module=self.module, form={"post": post_form, "template": template_form})

	@gen.coroutine
	def json(self, argv):
		action 	= self.site.get_argument('action', None)
		post 	= yield self.post_json(argv[0], action)
		if post:
			argv 	= self.post_argv(post)

			self.site.graph['og:url'] 		= argv['link']
			self.site.graph['og:title'] 	= argv['title']

			if len(argv['note']) > 10:
				self.site.graph['og:description'] 	= argv['note']

			if 'picture' in post['post']['content']:
				image 		= "%s://%s%s" % (self.site.request.protocol, self.site.request.host, post['post']['content']['picture'])
			elif 'video' in post['post']['content']:
				image 		= "http://i1.ytimg.com/vi/%s/hqdefault.jpg" % post['post']['content']['video'].split('youtube.com/watch?v=',2)[1].split(r'/[#|\?]/', 1)[0]
			else:
				image 		= None
			if image:
				self.site.graph['og:image'] 	= [
					["og:image", image],
					["og:image:width", "1500"],
					["og:image:height", "1500"]
				]
		else:
			argv 	= None
		return {"post": argv}

	def post_argv(self, post= None):
		if post:
			#####
			if 'picture' in post['post']['content']:
				content 	=  template.Template('<img src="{{ picture }}">').generate(picture=post['post']['content']['picture']).decode("utf-8")
			elif 'video' in post['post']['content']:
				content 	=  template.Template('<div class="video" link="{{ video }}"></div>').generate(video=post['post']['content']['video']).decode("utf-8")
			else:
				content 	= ""
			#####
			if 'type' in post and post['type'] == 'private':
				warning 	= "Bài viết đang được chờ kiểm duyệt, bạn thông cảm nhé :)"
			else:
				warning 	= ""
			#####
			if 'note' in post['post']['content']:
				# old version
				argv 	= {
					"id" 			: str(post['_id']),
					"content" 		: content,
					"note"			: escape.xhtml_escape(post['post']['content']['note']),
					"link" 			: "%s://%s/%s/%s/%s/%s.html" % (self.site.request.protocol, self.site.request.host, self.site.db_site['name'], self.site.db_page['name'], post['_id'], function.seo_encode(post['post']['title'])),
					"title"			: escape.xhtml_escape(post['post']['title']),
					"source"		: escape.xhtml_escape(post['post']['content']['source']),
					"time"			: post['time'],
					"user.name" 	: post['user']['first_name'] + ' ' + post['user']['last_name'],
					"user.picture"	: post['user']['picture'],
					"warning"		: warning,
					"banner" 		: ''
				}
			else:
				# newversion
				argv 	= {
					"id" 			: str(post['_id']),
					"content" 		: content,
					"note"			: escape.xhtml_escape(post['post']['note']),
					"link" 			: "%s://%s/%s/%s/%s/%s.html" % (self.site.request.protocol, self.site.request.host, self.site.db_site['name'], self.site.db_page['name'], post['_id'], function.seo_encode(post['post']['title'])),
					"title"			: escape.xhtml_escape(post['post']['title']),
					"source"		: escape.xhtml_escape(post['post']['source']),
					"time"			: post['time'],
					"user.name" 	: post['user']['first_name'] + ' ' + post['user']['last_name'],
					"user.picture"	: post['user']['picture'],
					"warning"		: warning,
					"banner" 		: "banner" if 'banner' in post['post'] and post['post']['banner'] else '',
				}
		else:
			argv 	= {
				"id" 			: '{{ id }}',
				"content" 		: '{{ content }}',
				"note" 			: '{{ note }}',
				"link" 			: '{{ link }}',
				"title"			: '{{ title }}',
				"source"		: '{{ source }}',
				"time"			: '{{ time }}',
				"user.name" 	: '{{ user.name }}',
				"user.picture"	: '{{ user.picture }}',
				"warning"		: '{{ warning }}',
				"banner" 		: '{{ banner }}',
			}
		return argv

	@gen.coroutine
	def post_json(self, post, action = None):
		###
		query = {'site_id': self.module['site_id']}
		### type filter
		if 'type' in self.module['setting']['server']:
			query['type'] 	= self.module['setting']['server']['type']
		### format filter
		if 'format' in self.module['setting']['server']:
			query['post.format'] 	= { "$in": self.module['setting']['server']['format']}
		else:
			query['post.format'] 	= { "$in": ["bi", "bv", "bl"]}

		if type(post) == str and len(post) == 24:
			post 		= ObjectId(post)

		### action
		sort 	= [('public.time', -1)]
		if action == "after":
			query['_id'] 	= { "$lt": post }
		elif action == "before":
			sort 	= [('public.time', 1)]
			query['_id'] 	= { "$gt": post }
		else:
			query['_id'] 	= post
			###### owner $or query
			session 	= yield self.site.session.get(['user_id'])
			if 'user_id' in session:
				query 	= {"$or": [query, {'_id': post , "user_id": session['user_id'], 'type': 'private'}]}
		#####
		post 		= yield self.site.db.post.find(query, {'_id': 1, 'user_id': 1, 'site_id': 1, 'time': 1, 'like': 1, 'post': 1, 'type': 1}).sort(sort).to_list(length=1);
		#####
		if len(post) > 0:
			post 			= post[0]
			# lay info cua user comment trong list
			user 			= yield self.site.db.user.find_one({ "_id": post['user_id'] }, {'first_name': 1, 'last_name': 1, 'email': 1, 'picture': 1})
			post['user'] 	= user
			
			# no yield for run after response , is faster
			self.view_update(post)
		return post
		
	@gen.coroutine
	def view_update(self, post):
		try:
			user 		= yield self.site.session.get(['user_id'])
			update 		= {"$inc": {"view.count": 1}}
			if 'user_id' in user:
				update["$pushAll"] 	= { "view.user": [user['user_id']]}

			yield self.site.db.post.update({
						"_id": post['_id']
					},
					update,
					upsert= True
				)
		except Exception as e:
			raise e