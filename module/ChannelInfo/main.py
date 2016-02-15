from tornado import gen, escape
from bson.objectid import ObjectId
from module import ModuleBase

class Module(ModuleBase):
	"""docstring for Module"""
	# def __init__(self):
	# 	super(Module, self).__init__()

	@gen.coroutine
	def form(self, argv):
		argv = self.post_argv()
		return self.site.render_string(
			self.module['path'] + "form.html",
			module 	= self.module,
			argv 	= {
				"name": '{%% raw module["%s"]["name"] %%}' % self.module['_id'],
				"title": '{%% raw module["%s"]["title"] %%}' % self.module['_id'],
				"description": '{%% raw module["%s"]["description"] %%}' % self.module['_id'],
				"image": '{%% raw module["%s"]["image"] %%}' % self.module['_id'],
				"banner": '{%% raw module["%s"]["banner"] %%}' % self.module['_id']
			}
		), True

	@gen.coroutine
	def form_post(self, argv):
		json_argv 	= yield self.json(argv)
		post 		= self.post_argv(json_argv)
		return post

	@gen.coroutine
	def json(self, argv):
		channel = self.site.site_db['page']['name']
		post = yield self.post_json(channel)
		return post
	
	def post_argv(self, post=None):
		if post:
			argv = {
				"name": post['name'],
				"title": post['setting']['title'],
				"description": post['setting']['description'],
				"image": post['setting']['image'] if 'image' in post['setting'] else '',
				"banner": post['setting']['banner'] if 'banner' in post['setting'] else ''
			}
		else:
			argv = {
				"name": '{{ name }}',
				"title": '{{ title }}',
				"description": '{{ description }}',
				"image": '{{ image }}',
				"banner": '{{ banner }}',
			}
		return argv

	@gen.coroutine
	def post_json(self, c_name):
		if c_name:
			channel = yield self.site.db.channel.find_one({
					'name': c_name, 'site_id': self.site.site_db['_id']
				},{
					'setting': 1, 'name': 1
				})
			return channel