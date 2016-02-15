import os
from tornado import gen, escape
from base64 import b64encode
from bson.objectid import ObjectId

class ModuleBase(object):
	def __init__(self):
		self.script 	= [
			"script.js",
			"style.css"
		]

	def script_require(self):
		result 	= []
		for s in self.script:
			if not s.startswith('/'):
				s = "/module/%s/static/%s" % (self.module['name'], s)
			result.append(s)
		return result

	@gen.coroutine
	def load_form(self, module, site, argv, *args, **kwargs):
		self.site 	= site
		self.module_define(module, True)
		result 		= yield self.form(argv, *args, **kwargs)
		return result#.decode('utf-8')
	
	@gen.coroutine
	def load_post(self, module, site, argv):
		self.site 	= site
		self.module_define(module)
		
		return (yield self.form_post(argv))

	@gen.coroutine
	def load_json(self, module, site, argv):
		self.site 	= site
		self.module_define(module)
		argv 		= yield self.json(argv)
		
		if not self.site._finished and argv:
			if type(argv) == str:
				return argv

			if type(argv) != dict:
				argv 			= {}
				
			if not 'post' in argv:
				argv['post'] 	= []

			result 	= {"post": argv['post']}
			if len(self.site.graph) > 0:
				result['graph'] 	= self.site.graph
			return escape.json_encode(result).encode("utf-8")
		return "{}"

	@gen.coroutine
	def form(self, argv):
		return ""

	@gen.coroutine
	def form_post(self, argv):
		return ""

	@gen.coroutine
	def json(self, argv):
		return {}
	
	def module_define(self, module, overwrite=False):
		self.module 			= module
		self.module['path'] 	= "../module/"+ self.module['name']+"/"
		# encode base64 de send cho client
		p 						= self.site.platform
		if p in self.module['setting']:
			if overwrite and 'client' in self.module['setting'][p]:
				self.setting_overwrite(self.module['setting'][p]['client'], self.module['setting']['client'])
			if 'server' in self.module['setting'][p]:
				self.setting_overwrite(self.module['setting'][p]['server'], self.module['setting']['server'])
		
		if overwrite:
			self.module['setting']['client'] 			= b64encode(escape.json_encode(self.module['setting']['client']).encode("utf-8"))
		return True

	def setting_overwrite(self, sfrom, sto):
		for key in sfrom:
			if key in sto:
				if type(sfrom[key]) in [str, int, float]:
					sto[key] 	= sfrom[key]
				elif type(sfrom[key]) == type(sto[key]):
					if type(sfrom[key]) == list:
						for s in sfrom[key]:
							if not s in sto[key]:
								sto[key][s] 	= sfrom[key][s]
					elif type(sfrom[key]) == dict:
						sto[key] = self.setting_overwrite(sfrom[key], sto[key])
			else:
				sto[key] 	= sfrom[key]
	
	### webscoket init
	def ws_init(self, module, site):
		self._module_inited 	= False
		self.site 				= site
		self.module_define(module)
	
	# websocket message recv
	@gen.coroutine
	def ws_read(self, msg):
		pass

	# websocket message write
	def ws_write(self, msg):
		self.site.write_message(msg)

	# websocket close
	def ws_close(self):
		self.site.close()

	def close(self):
		pass

### load module object ###
class ModuleLoader(object):
	"""docstring for ModuleLoader"""
	def __init__(self):
		self.modules 		= dict()
		self.module_path 	= "module" + os.path.sep
		self.module_static 	= "static" + os.path.sep
		############### load module #####################
		all_modules = os.listdir(self.module_path)
		loadable_modules = list()
		for module in all_modules:
			md 	= self.module_path + module + os.path.sep + "main.py"
			if os.path.isfile(md):# and md[-3:] == '.py':
				loadable_modules.append(md[:-3])

		del all_modules
		############# import module ####################
		for md in loadable_modules:
			module_name		= md[len(self.module_path):].split(os.path.sep, 1)[0]
			module 			= self.importModule(md)
			self.setModule(module_name, module)

	def setModule(self, module_name, module):
		module_instance  			= module.Module
		self.modules[module_name] 	= {
				"object" :module_instance,
				"static": self.module_path + module_name + os.path.sep + self.module_static
			}

	def importModule(self, module_name):
		return __import__((module_name).replace('/', '.'), None, None, ['Module'])