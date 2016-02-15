from tornado import gen, escape
from base64 import b64encode
from bson.objectid import ObjectId
# from time import time
from module import ModuleBase
from core import function
from core.app.movie import MovieManager
import re
class Module(ModuleBase):
	"""docstring for Module"""
	def __init__(self):
		super(Module, self).__init__()
		self.cache_time 	= 86400 #24h

	@gen.coroutine
	def form(self, argv):
		post_argv 		= self.post_argv()
		template 		= {
			"post": self.site.render_string(self.module['path'] + "post.html", argv=post_argv).decode("utf-8")
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
		post_argv		= self.post_argv(json_argv['post'])
		post_form 		= self.site.render_string(self.module['path'] + "post.html", argv=post_argv)
		return {"post": post_form}

	@gen.coroutine
	def json(self, argv):
		self.manager 	= MovieManager(self.site, self.module)
		# action 			= self.site.get_argument('action', None)
		# get cache store
		cache_string 	= "%s" % str(self.module['_id'])
		result 			= yield self.site.cache.get(cache_string)
		if result and 'data' in result:
			return result['data']
		else:
			posts 	= yield self.post_json()
			result 	= {"post": posts}

			# set cache store
			self.site.cache.set(cache_string, result, self.cache_time)
			return result

	@gen.coroutine
	def post_json(self, post_list=None, post_count=10):
		if not post_list:
			try:
				post_list = self.module['setting']['server']['post']
			except:
				post_list = []
		if type(post_list) == str:
			post_list = [ObjectId(p) for p in post_list.split(',') if re.match(r'[a-z0-9]{24}', p)]

		query = {
			"site_id": self.module['site_id'],
			"format": "mv"
		}

		if post_list:
			query['_id'] = {"$in": post_list}

		posts = yield self.manager.db.find(query, {"post.image": 1, "post.title":1 , "post.title_seo":1 , "post.description": 1}).sort([('access.time', -1)]).to_list(length=post_count)
		return posts


	def post_argv(self, post= None):
		if post:
			post_item 	= ""
			post_goto 	= ""
			goto 		= 0
			module_id 	= str(self.module['_id'])
			for p in post:
				if 'post' in p and 'image' in p['post']:

					# seo title
					if 'title_seo' in p['post']:
						title_seo 	= escape.xhtml_escape(p['post']['title_seo'])
					else:
						title_seo 	= ''
					
					link 	= "%s/%s/%s/%s.html" % (self.site.domain_root, self.module['setting']['server']['view'], p['_id'], title_seo)

					if goto == 0:
						item_class 	= "active"
					else:
						item_class	= ""
					post_item 	+= """<div class="item {item_class}"><div class="img"><img src="{image}"></div><a href="{link}" site-goto><div class="carousel-caption"><h3>{title}</h3><div class="descript"><p>{descript}</p></div></div></a></div>""".format(
												title		= p['post']['title'],
												descript	= p['post']['description'],
												image		= p['post']['image'][0],
												item_class 	= item_class,
												link 		= link,
											)
					post_goto 	+= '<li data-target="#carousel-%s" data-slide-to="%s" class="%s"></li>' % (module_id, goto, item_class)
					goto 		+= 1
			
			argv = {
				"id"		: module_id,
				"item"		: post_item,
				"goto"		: post_goto,
			}
		else:
			argv 	= {
				"id"		: '{{ id }}',
				"item"		: '{{ item }}',
				"goto" 		: '{{ goto }}',
			}
		return argv

