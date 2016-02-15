# import os
from tornado import gen
from base64 import b64encode
from time import time
from module import ModuleBase
from bson.objectid import ObjectId
from bson import json_util
import json

class Module(ModuleBase):
	"""docstring for Module"""
	def __init__(self):
		super(Module, self).__init__()
		self.script.extend([
			"/static/js/beautify.js",
		])

	@gen.coroutine
	def form(self, argv):
		json_argv 		= yield self.json(argv)
		return self.site.render_string(
			self.module['path'] + "form.html",
			module 	= self.module,
			argv 	= json_argv
		), False

	@gen.coroutine
	def json(self, argv):
		session 	= yield self.site.session.get(['user_id'])
		if 'user_id' in session and session['user_id'] == self.site.site_db['user_id']:
			post_id 		= self.site.get_argument('post', None)
			if type(post_id) == str and len(post_id) == 24:
				post_id 	= ObjectId(post_id)
			
			action 			= self.site.get_argument('action', None)

			if action == "update":
				o_type 	= self.site.get_argument('type', None)
				o_json 	= self.site.get_argument('json', None)
				if o_type and o_json:
					o_json 	= json.loads(o_json, object_hook=json_util.object_hook)
					if '_id' in o_json and 'name' in o_json:
						query = {"_id": o_json['_id'], "name": o_json['name']}
						del o_json['_id']
						if o_type == "page":
							self.site.db.page.update(query, {"$set": o_json}, upsert=True)
						elif o_type == "module":
							self.site.db.module.update(query, {"$set": o_json}, upsert=True)
						return '{"error":0,"success":1}'
			else:
				config = {
					"page": (yield self.site.db.page.find({"site_id": self.site.site_db['_id']}, {"name": 1, "setting": 1, "form": 1, "permission": 1}).to_list(length=100)),
					"module": (yield self.site.db.module.find({"site_id": self.site.site_db['_id']}, {"name": 1, "setting": 1}).to_list(length=100)),
				}
				return b64encode(json.dumps(config, default=json_util.default).encode("utf-8"))
		return '{"error":1,"success":0}'
