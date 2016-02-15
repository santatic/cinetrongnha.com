from tornado import gen
from module import ModuleBase

class Module(ModuleBase):
	"""docstring for Module"""
	# def __init__(self):
	# 	super(Module, self).__init__()
	# 	self.script.extend([
	# 		"/static/jwplayer/jwplayer.js",
	# 		# "/static/jwplayer/jwpsrv.js"
	# 	])

	@gen.coroutine
	def form(self, argv):
		return self.site.render_string(self.module['path'] + "form.html", module=self.module), False
