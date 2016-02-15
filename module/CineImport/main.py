from tornado import gen, escape
from module import ModuleBase
from core.app import movie

class Module(ModuleBase):
	"""docstring for Module"""
	def __init__(self):
		super(Module, self).__init__()
		self.script.extend([
			"/static/js/beautify.js",
		])

	@gen.coroutine
	def form(self, argv):
		return self.site.render_string(self.module['path'] + "form.html", module=self.module, form={"template": ""}), False

	@gen.coroutine
	def json(self, argv):
		self.manager 	= movie.MovieManager(self.site, self.module)
		if self.manager:
			action 	= self.site.get_argument('action', None)
			if action == "import":
				data 	= self.site.get_argument('movie', None)
				if data:
					data 		= escape.json_decode(data)
					# insert information
					insert		= yield self.manager.set_movie_info(data)
					# update movie
					if insert:
						print(insert)
						update 	= yield self.manager.set_movie_chaps(mv_id=insert, chaps=data['chap'])
						if update:
							return '{"error":0,"success":1}'
		return '{"error":1,"success":0}'