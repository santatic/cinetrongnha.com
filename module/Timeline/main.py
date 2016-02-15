from tornado import gen, escape
from base64 import b64encode
from bson.objectid import ObjectId
from time import time
from module import ModuleBase
from core import function
from core.app.movie import MovieManager
import re

class Module(ModuleBase):
	# """docstring for Module"""
	def __init__(self):
		super(Module, self).__init__()
		self.tab_current = None

	@gen.coroutine
	def form(self, argv):
		tab_argv 		= yield self.tab_argv()
		template 		= {
			"tab": self.site.render_string(self.module['path'] + "tab.html", argv=tab_argv).decode("utf-8"),
		}
		return self.site.render_string(
			self.module['path'] + "form.html",
			module 	= self.module,
			argv 	= {
				"template": b64encode(escape.json_encode(template).encode("utf-8")),
				"tab": '{%% raw module["%s"]["tab"] %%}' % self.module['_id']
			}
		), True

	# @gen.coroutine
	def find_tab(self, tab_name):
		for t in self.module['tab']:
			if tab_name == t['name']:
				self.tab_current = t
				return True
		return False

	@gen.coroutine
	def form_post(self, argv):
		if not argv or not argv[0]:
			self.tab_current = self.module['tab'][0]
			tab_argv 		= yield self.tab_argv(self.tab_current['name'])
		else:
			tab_argv 		= yield self.tab_argv(argv[0])
		tab_form 	= self.site.render_string(self.module['path'] + "tab.html", argv=tab_argv)
		return {"tab": tab_form}

	@gen.coroutine
	def json(self, argv):
		pass

	@gen.coroutine
	def tab_argv(self, tab=None):
		if tab:
			if self.tab_current or self.find_tab(tab):
				module_db 	= yield self.site.db.module.find_one({"_id": self.tab_current['module']})
				module_obj 	= self.site.loadModule(module_db)
				if module_obj:
					module_form, load 	= yield module_obj.load_form(module_db, self.site, [], {
							"post": '{{ module_post }}',
							"list": '{{ module_list }}'
						})
					# module_form 	= module_form
					template 		= b64encode(escape.json_encode(module_form.decode("utf-8")).encode("utf-8"))
					module_post 	= yield module_obj.load_post(module_db, self.site, [])
					for k in module_post:
						module_form 	= module_post[k].join(module_form.split(('{{ module_%s }}' % k).encode('utf-8')))
					argv 	= {
						"name": self.tab_current['name'],
						"template": template,
						"post": module_form
					}
			else:
				return None
		else:
			argv 	= {
				"name" 		: '{{ name }}',
				"template" 	: '{{ template }}',
				"post" 		: '{{ post }}'
			}
		return argv

	def post_argv(self, post= None):
		pass

	@gen.coroutine
	def post_json(
		self,
		post_id 	= None,
		post_skip 	= None,
		post_tab 	= None,
		post_count 	= 12,
		post_sort 	= False,
		sort 		= [('access.time', -1)],
	):
		#  limit count of post
		try:
			if post_count > self.module['setting']['server']['max_count']:
				post_count = self.module['setting']['server']['max_count']
		except:
			pass
		
		# set tab static
		if not post_tab and 'tab' in self.module['setting']['server']:
			post_tab = self.module['setting']['server']['tab']

		if post_count > 0:
			###
			query	= {
				'site_id'		: self.module['site_id'],
				# 'format'		: "pg",
				# 'access.type' 	: "public"
			}
			###
			if 'channel' in self.site.page_db:
				query['_id'] = self.site.page_db['channel']

			# if post_id:
			# 	if type(post_id) == str:
			# 		post_id 	= [ObjectId(p) for p in post_id.strip().split(',')]
			# 	elif type(post_id) == ObjectId:
			# 		post_id 	= [post_id]

			# 	if type(post_id) == list:
			# 		query['_id'] = {'$in': post_id}
			###
			chan 	= yield self.site.db.channel.find_one(query, {"post":1})
			if chan and 'post' in chan:
				groups_id 	= chan['post'][::-1]
				groups 		= yield self.site.db.post_group.find({"_id": {"$in": groups_id}}, {"post":1}).to_list(length=len(groups_id))
				# sort with post id
				if groups and 'post' in groups:
					return groups['post'][::-1]