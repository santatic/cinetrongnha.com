from tornado import gen
from module import ModuleBase

class Module(ModuleBase):
	"""docstring for Module"""
	def __init__(self):
		self.script 	= [
			"script.js",
		]

	@gen.coroutine
	def form(self, argv):
		return self.site.render_string(self.module['path'] + "form.html", module=self.module, form={"template": ""}), False