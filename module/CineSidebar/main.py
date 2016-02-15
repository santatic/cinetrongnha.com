import re
from tornado import gen, escape
from base64 import b64encode
from bson.objectid import ObjectId
from module import ModuleBase
from core.app.movie import MovieManager

class Module(ModuleBase):
	"""docstring for Module"""
	def __init__(self):
		super(Module, self).__init__()
		self.script.extend([
			"/static/js/jquery.lazyload.min.js",
		])

	@gen.coroutine
	def form(self, argv):
		# generic template for json data
		argv 			= self.post_argv()
		template 		= {
			"post": self.site.render_string(self.module['path'] + "post.html", argv=[argv]).decode("utf-8"),
		}
		return self.site.render_string(
			self.module['path'] + "form.html",
			module 	= self.module,
			argv 	= {
				"template": b64encode(escape.json_encode(template).encode("utf-8")),
				"post": '{%% raw module["%s"]["post"] %%}' % self.module['_id']
			}
		), True
	@gen.coroutine
	def form_post(self, argv):
		json_argv 		= yield self.json(argv)
		post_form 		= self.site.render_string(self.module['path'] + "post.html", argv=json_argv['post'])
		return {"post": post_form}

	@gen.coroutine
	def json(self, argv):
		self.manager 	= MovieManager(self.site, self.module)
		action 			= self.site.get_argument('action', None)
		if action == 'setting':
			post_id 	= self.site.get_argument('post', None)
			if post_id:
				if type(post_id) == str and re.match(r'[a-z0-9]{24}', post_id):
					post_id 		= ObjectId(post_id)

				mv_setting = self.site.get_argument('setting', None)

				if mv_setting == "complete":
					mv_setting = "mvc"
				elif mv_setting == "remove":
					mv_setting = "mvd"
				result = yield self.manager.set_user_view_post(post_id, mv_setting)
				if result:
					return '{"error":0,"success":1}'
		else:
			post_id 	= self.site.get_argument('post', None)
			if not post_id:
				posts_view 	= yield self.manager.get_user_view_post()
				if posts_view:
					post_id = []
					for p in posts_view:
						if 'post_id' in p:
							post_id.append(p['post_id'])
			###
			posts = yield self.post_json(post_id)
			posts_argv 	= []
			for post in posts:
				posts_argv.append(self.post_argv(post))
					
			return {"post": posts_argv}
		return '{"error":1,"success":0}'

	def post_argv(self, post= None):
		if post:			# title
			if 'title_seo' in post['post']:
				title_seo 		= escape.xhtml_escape(post['post']['title_seo'])
			else:
				title_seo 	= ''

			if 'title' in post['post']:
				title 		= escape.xhtml_escape("%s (%s)" % (post['post']['title'], post['post']['year']))
			else:
				title 		= ""

			# poster
			if 'poster' in post['post']:
				poster 		= escape.xhtml_escape(post['post']['poster'])
			else:
				poster 		= ""

			###
			argv 	= {
				"id" 				: str(post['_id']),
				"title"				: title,
				"subtitle"			: escape.xhtml_escape(post['post']['subtitle']),
				"poster" 			: poster,
				"link" 				: "%s/%s/%s/%s.html" % (self.site.domain_root, self.module['setting']['server']['page_view'], post['_id'], title_seo),
			}
		else:
			argv 	= {
				"id" 				: '{{ id }}',
				"title"				: '{{ title }}',
				"subtitle"			: '{{ subtitle }}',
				"poster" 			: '{{ poster }}',
				"link"				: '{{ link }}'
			}
		return argv

	@gen.coroutine
	def post_json(self, post_id, sort=[('access.time', 1)], count=10):
		### post id
		if type(post_id) == str:
			post_id =[ObjectId(p) for p in post_id.split(',') if re.match(r'[a-z0-9]{24}', p)]

		if type(post_id) == list:
			post_id = {'$in': post_id}
		###
		cursor 	= self.site.db.post.find({
			'_id': post_id,
			'site_id': self.module['site_id'],
			'format': 'mv',
			'access.type': 'public'
		}, {'post': 1}).sort(sort)
		posts 	= yield cursor.to_list(length=count)
		if type(post_id) == dict and '$in' in post_id:
			result = []
			for p in post_id['$in']:
				for rp in posts:
					if p == rp['_id']:
						result.append(rp)
						break
			return result
		return posts