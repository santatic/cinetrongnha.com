import os, re, logging, json
import tornado.web
import tornado.gen
import tornado.websocket
from bson.objectid import ObjectId
from bson import json_util
from tornado import escape
from base64 import b64encode
from core import base, function

class Site(base.BaseHandler):
	"""docstring for Site"""
	def initialize(self, **kwargs):
		# facebook graph
		self.graph 			= {}
		#
		self.platform 		= self.get_secure_cookie("platform", None)
		if not self.platform:
			user_agent 		= self.request.headers.get('User-Agent')
			self.platform 	= function.mobile_detect(user_agent)
			self.set_secure_cookie("platform", self.platform)
		else:
			self.platform 	= self.platform.decode('utf-8')

	@tornado.gen.coroutine
	def geter(self, site_page=None, site_post=None, site_seo=None):
		### BUILDER ###
		build 			= self.get_argument('build', None)
		if build:
			self.site_db = yield self.db.site.find_one({"domain": self.request.host})
			
			if build == "page" and site_page:
				page = yield self.db.page.find_one({'site_id': self.site_db['_id'], "name": site_page})
				yield self.build_page(page)
			
			if build in ["site", "all"]:
				yield self.build_site(self.site_db)
				if build == "all":
					pages = yield self.db.page.find({'site_id': self.site_db['_id']}).to_list(None)
					for page in pages:
						yield self.build_page(page)
			

		### detect site
		domain 	= self.request.host
		query 	= {"domain": domain}
		output 	= {
			'user_id': 1,
			'name': 1,
			'title': 1,
			'setting': 1,
			'header': 1,
			'template': 1,
			'module': 1,
			'domain': 1,
		}
		if site_page:
			query['page.name'] 	= site_page
			output['page.$'] 	= 1
		else:
			output['page'] 	= {"$slice": [0, 1]}

		self.site_db = yield self.db.site.find_one(query, output)
		# site ko thay hoac page ko ton tai
		if not self.site_db:
			return {"action": "result", "data": 'error: page not found !'}
		
		# redirect home page
		if not site_page:
			return {"action": "redirect", "data": "%s://%s/%s" % (self.request.protocol, domain, self.site_db['page'][0]['name'])}
		
		# rebuild template
		if not 'template' in self.site_db:
			return {"action": "result", "data": 'warning: rebuild template !'}

		self.domain_root 		= "%s://%s" % (self.request.protocol, domain)

		self.site_db['page'] = self.site_db['page'][0]

		### check permission of page
		if 'permission' in self.site_db['page'] and not (yield self.permission(self.site_db['page']['permission'])):
			return {"action": "redirect", "data": self.get_login_url()}

		# patch page name
		if type(self.site_db['page']['name']) == list:
			self.site_db['page']['name'] 	= site_page

		# channel / user
		if 'format' in self.site_db['page']:
			if self.site_db['page']['format'] == "channel":
				self.site_db['page']['channel'] = yield self.db.channel.find_one({"name": self.site_db['page']['name'], 'site_id': self.site_db['_id']})
				if self.site_db['page']['channel']:
					# graph info
					setting = self.site_db['page']['channel']['setting']
					if 'description' in setting:
						self.graph['og:description'] 	= setting['description']
					
					if 'title' in setting:
						self.graph['og:title'] 			= escape.xhtml_escape(setting['title'])
					
					if 'image' in setting :
						if self.site_db['setting']['image'][0] == '/':
							self.site_db['setting']['image'] 	= "%s%s" % (self.domain_root, setting['image'])
						self.graph['og:image'] 			= [
							["og:image", setting['image']],
							["og:image:width", "1500"],
							["og:image:height", "1500"]
						]
				else:
					return {"action": "result", "data": 'warning: channel not found !'}

		### facebook graph
		if not 'og:type' in self.graph:
			self.graph['og:type'] 			= "website"
		if not 'og:locale' in self.graph:
			self.graph['og:locale']			= "en_US"
		if not 'og:site_name' in self.graph:
			self.graph['og:site_name'] 		= escape.xhtml_escape(self.site_db['name'])
		if not 'og:title' in self.graph:
			self.graph['og:title'] 			= escape.xhtml_escape(self.site_db['setting']['title'])
		if not 'og:description' in self.graph and 'description' in self.site_db['setting'] :
			self.graph['og:description'] 	= self.site_db['setting']['description']
		if not 'og:image' in self.graph and 'image' in self.site_db['setting'] :
			if self.site_db['setting']['image'][0] == '/':
				self.site_db['setting']['image'] 	= "%s%s" % (self.domain_root, self.site_db['setting']['image'])
			self.graph['og:image'] 			= [
				["og:image", self.site_db['setting']['image']],
				["og:image:width", "1500"],
				["og:image:height", "1500"]
			]
		if not 'keywords' in self.graph and 'keywords' in self.site_db['setting'] :
			self.graph['keywords'] 	= self.site_db['setting']['keywords']

		### get login encode
		login 			= dict((yield self.session.get(['user_id', 'first_name', 'last_name', 'picture', 'access_token'])))
		if not "user_id" in login:
			login 		= {}
		else:
			self.site_db['user'] = login
			# self.site_db['user']['name'] = "%s %s" % (login['first_name'], login['last_name'])

		self.site_db['login'] 	= b64encode(json.dumps(login, default=json_util.default).encode("utf-8"))

		### module argv of site + page
		modules_argv 	= yield self.get_module_argv(self.site_db['module'] + self.site_db['page']['module'], argv=[site_post])

		### site argv
		self.site_db['graph'] = self.graph
		return {"action": "result", "data": self.render_string("%s/site.html" % (str(self.site_db['_id'])), argv=self.site_db, module=modules_argv).decode('utf-8')}
				

	@tornado.gen.coroutine
	def poster(self, site_page=None, site_post=None, site_seo=None):
		domain 	= self.request.host
		query 	= {"domain": domain}
		output 	= {
			'user_id': 1,
			'name': 1,
			'setting': 1,
			'domain': {"$slice": [0,1]},
		}
		if site_page:
			query['page.name'] 	= site_page
			output['page.$'] 	= 1
		else:
			output['page'] 	= {"$slice": [0, 1]}

		self.site_db = yield self.db.site.find_one(query, output)
		# site ko thay hoac page ko ton tai
		if not self.site_db:
			return {"action": "result", "data": 'error: page not found !'}
		
		self.domain_root 		= "%s://%s" % (self.request.protocol, domain)
		self.site_db['page'] 	= self.site_db['page'][0]

		# check permission of page
		if 'permission' in self.site_db['page'] and not (yield self.permission(self.site_db['page']['permission'])):
			return {"action": "redirect", "data": self.get_login_url()}
		
		# patch page name
		if type(self.site_db['page']['name']) == list:
			self.site_db['page']['name'] 	= site_page
		# channel / user
		if 'format' in self.site_db['page']:
			if self.site_db['page']['format'] == "channel":
				self.site_db['page']['channel'] = yield self.db.channel.find_one({"name": self.site_db['page']['name']})
		
		module 	= self.get_argument('module', None)
		if module:
			modules_post 	= yield self.get_module_argv([ObjectId(module)], output="json", argv=[site_post])
			if modules_post:
				if 'permission' in modules_post and not (yield self.permission(modules_post['permission'])):
					return {"action": "result", "data": '{}'}
				return {"action": "result", "data": modules_post[module]}
		else:
			modules_post 	= yield self.get_module_argv(self.site_db['page']['module'], argv=[site_post])
			result 			= {
				"content": self.render_string(
					"%s/%s" % (str(self.site_db['_id']), self.site_db['page']['template']),
					argv= self.site_db['page'],
					module= modules_post
				).decode('utf-8')
			}
			return {
				"action": "result",
				"data": result
			}
		return {"action": "result", "data": '{}'}

	@tornado.gen.coroutine
	def get_module_argv(self, modules_id, output="html", argv=[]):
		modules_obj 	= yield self.db.module.find({'_id': {'$in': modules_id}, 'site_id': self.site_db['_id']}).to_list(None)
		modules_post 	= {}
		for i, obj in enumerate(modules_obj):
			md_obj 	= self.loadModule(obj)
			if md_obj:
				if output == "json":
					modules_post[str(obj['_id'])] 	= yield md_obj.load_json(obj, self, argv)
				else:
					modules_post[str(obj['_id'])] 	= yield md_obj.load_post(obj, self, argv)
			else:
				modules_post[str(obj['_id'])] 	= "error module %s %s" % (str(obj['name']), str(obj['_id']))
		return modules_post

	@tornado.gen.coroutine
	def permission(self, permission):
		'''
		module kiem tra user co nam trong groups/users co quyen truy cap website hay ko
		. neu @page_db chua site thi lay @page_id de get data tu db
		'''
		if permission:
			session 	= yield self.session.get(['user_id'])
			if 'user_id' in session:
				if session['user_id'] in permission['users']:
					return True
				if 'group' in permission:
					group 	= yield self.db.groups.find_one(
								{'_id': {"$in" : permission['group']}, 'site_id': self.site_db['_id'], 'type': "usergroup", 'users': session['user_id']},
								{'_id': 1}
							)
					if group:
						return True
		return False

	def loadModule(self, module):
		if module['name'] in self.settings['modules']:
			return self.settings['modules'][module['name']]['object']()
		return None

	######################
	@tornado.gen.coroutine
	def build_site(self, site_db, site_post=None, site_seo=None):
		script 		= {}
		module 		= {}
		### sidebar module
		if 'sidebar' in site_db['header']:
			obj = yield self.db.module.find_one({'_id': site_db['header']['sidebar'], 'site_id': site_db['_id']})
			if obj:
				try:
					md_obj 				= self.loadModule(obj)
					if md_obj:
						obj['form'], load 	= yield md_obj.load_form(obj, self, [site_post])
						if load:
							module[obj['_id']] = 1
						require 		= md_obj.script_require()
						for req in require:
							script[req] = 1
					else:
						obj['form'] 	= obj['name']
				except Exception as e:
					obj['form'] 		= obj['name']
					# traceback.print_exc(file=sys.stdout)
					logging.exception('Got exception on', self)
				site_db['header']['sidebar'] = obj
			else:
				print('module not found', site_db['header']['sidebar'])

		### menu module
		if 'menu' in site_db['header']:
			obj = yield self.db.module.find_one({'_id': site_db['header']['menu'], 'site_id': site_db['_id']})
			if obj:
				try:
					md_obj 				= self.loadModule(obj)
					if md_obj:
						obj['form'], load 	= yield md_obj.load_form(obj, self, [site_post])
						if load:
							module[obj['_id']] = 1
						require 		= md_obj.script_require()
						for req in require:
							script[req] = 1
					else:
						obj['form'] 	= obj['name']
				except Exception as e:
					obj['form'] 		= obj['name']
					# traceback.print_exc(file=sys.stdout)
					logging.exception('Got exception on', self)
				site_db['header']['menu'] = obj
			else:
				print('module not found', site_db['header']['menu'])
		###
		if not 'setting' in site_db['header']:
			site_db['header']['setting'] 	= {}
		site_db['header']['setting'] 	= self.setting_generic(site_db['header']['setting'])

		### script core
		if 'script' in site_db['setting']:
			for s in site_db['setting']['script']:
				script[s] = 1
		
		# core default script
		core_script = {}
		path = 'static/core'
		dirs = os.listdir(path)
		for f in dirs:
			if f.endswith('.js') or f.endswith('.css'):
				core_script['/%s/%s' % (path, f)] = 1
		script = list(core_script.keys()) + list(script.keys())
		####
		argv = {
			"html": self.site_db['setting']['html'] if 'html' in self.site_db['setting'] else '',
			"header_info": '<title>{% raw argv["graph"]["og:title"] %}</title><meta name="title" content="{% raw argv["graph"]["og:title"] %}" /><meta property="og:title" content="{% raw argv["graph"]["og:title"] %}" />{% if "keywords" in argv["graph"] %}<meta name="keywords" content="{{ argv["graph"]["keywords"] }}">{% end %}{% if "og:type" in argv["graph"] %}<meta property="og:type" content="{% raw argv["graph"]["og:type"] %}" />{% end %}{% if "og:url" in argv["graph"] %}<meta property="og:url" content="{% raw argv["graph"]["og:url"] %}" />{% end %}{% if "og:image" in argv["graph"] %}{% for g in argv["graph"]["og:image"] %}<meta property="{{ g[0] }}" content="{% raw g[1] %}" />{% end %}<link rel="image_src" href="{{ argv["graph"]["og:image"][0][1] }}" />{% end %}{% if "og:site_name" in argv["graph"] %}<meta property="og:site_name" content="{% raw argv["graph"]["og:site_name"] %}" />{% end %}{% if "og:description" in argv["graph"] %}<meta property="og:description" name="description" content="{% raw argv["graph"]["og:description"] %}" />{% end %}{% if "og:locale" in argv["graph"] %}<meta property="og:locale" content="{% raw argv["graph"]["og:locale"] %}" />{% end %}{% if "fb:app_id" in argv["graph"] %}<meta property="fb:app_id" content="{% raw argv["graph"]["fb:app_id"] %}" />{% end %}',
			"script": script,
			"facebook_id": self.settings['facebook_oauth']['key'],
			"login": "{{ argv['login'] }}",
			"user_login": '{% if "user" in argv %}<div class="icon"><img class="avatar" src="{{ argv["user"]["picture"] }}"></div><div class="first-name">{{ argv["user"]["first_name"] }} <b class="caret"></b></div>{% else %}<div class="button login login-require">Login</div>{% end %}',
			"page": "{%% module Template('%s/%%s' %% argv['page']['template'], argv=argv['page'], module=module) %%}" % str(site_db['_id'])
		}
		# ---note--- update site modules list
		yield self.db.site.update({
				"_id": self.site_db['_id']
			}, {
				"$set":{
					"module": list(module.keys())
				}
			}, upsert=True)
		# write template
		site_form = self.render_string("site.html", site=site_db, script=script, argv= argv).decode('utf-8')
		site_form = re.sub(r"\n([\t]+)?", r"", site_form.strip()).encode('utf-8')
		f = open('template/%s/%s' % (self.site_db['_id'], self.site_db['template']), 'wb')
		f.write(site_form)
		f.close()

	@tornado.gen.coroutine
	def build_page(self, page_db, site_post=None, site_seo=None):
		# form 	= yield self.db.page.find_one({'name': page_db})
		form = page_db
		if not form:
			return
		# generic form
		script = {}
		module = {}
		new_rows 	= []
		for row in form['form']['rows']:
			# encode setting to client view
			if not 'setting' in row:
				row['setting'] = {}
			row['setting']	= self.setting_generic(row['setting'])
			if row['setting']:
				new_rows.append(row)
		form['form']['rows'] 	= new_rows

		for row in form['form']['rows']:
			new_cols 	= []
			for col in row['cols']:
				# encode setting to client view
				if not 'setting' in col:
					col['setting'] = {}

				col['setting']	= self.setting_generic(col['setting'])
				if col['setting']:
					new_cols.append(col)
			row['cols'] 	= new_cols
			for col in row['cols']:
				new_rows2 	= []
				for row2 in col['rows']:
					# encode setting to client view
					if not 'setting' in row2:
						row2['setting'] = {}
					row2['setting']	= self.setting_generic(row2['setting'])
					if row2['setting']:
						new_rows2.append(row2)
				col['rows'] 	= new_rows2
				for row2 in col['rows']:
					for i in range(0, len(row2['module'])):
						obj 	= yield self.db.module.find_one({'_id': row2['module'][i], "site_id": self.site_db['_id']})
						if obj:
							try:
								md_obj 				= self.loadModule(obj)
								if md_obj:
									obj['form'], load 	= yield md_obj.load_form(obj, self, [site_post])

									if load:
										module[obj['_id']] = 1

									require 		= md_obj.script_require()
									for req in require:
										script[req] 	= 1
								else:
									obj['form'] 	= obj['name']
							except Exception as e:
								obj['form'] 		= obj['name']
								# traceback.print_exc(file=sys.stdout)
								logging.exception('Got exception on', self)
							row2['module'][i] 			= obj
						else:
							print('module not found', row2['module'][i])
		

		# ---note--- update page modules list
		result = yield self.db.site.find_one({"_id": self.site_db['_id']}, {"page.id": page_db['_id']})

		page_argv = {
				"id": form['_id'],
				"name": form['name'],
				"module": list(module.keys()),
			}
		if 'permission' in form:
			page_argv['permission'] = form['permission']

		if type(form['name']) == list:
			form['name'] = form['name'][0]
		page_argv["template"] = "%s.html" % form['name']

		if 'format' in form:
			page_argv['format'] = form['format']

		if result and 'page' in result and result['page']:
			yield self.db.site.update({
				"_id": self.site_db['_id'],
				"page.name": form['name']
			}, {
				"$set": {"page.$": page_argv}
			}, upsert=True)
		else:
			yield self.db.site.update({
				"_id": self.site_db['_id']
			}, {
				"$push": {
					"page": page_argv
				}
			}, upsert=True)

		###
		page_form = self.render_string("page.html", page=form, script=script).decode('utf-8')
		page_form = re.sub(r"\n([\t]+)?", r"", page_form.strip()).encode('utf-8')
		f = open('template/%s/%s' % (self.site_db['_id'], page_argv['template']), 'wb')
		f.write(page_form)
		f.close()

	def setting_generic(self, setting):
		if type(setting) in [dict, list]:
			return b64encode(escape.json_encode(setting).encode("utf-8"))
		return None

class SiteWS(tornado.websocket.WebSocketHandler, Site):
	"""docstring for SiteWS"""
	def __init__(self, application, request, **kwargs):
		Site.__init__(self, application, request, **kwargs)
		tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)
	# pass webhandler
	def finish(self):
		pass

	def open(self):
		self._ws_inited 	= False

	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def on_message(self, message):
		print(message)
		if not self._ws_inited:
			yield self.initer()
			Site.initialize(self)
			# self.initialize()
			domain 				= self.request.host
			self.site_db 		= yield self.db.site.find_one({"domain": domain}, {'name': 1, 'domain': 1})
			if not self.site_db:
				self.write_message('{"ok":0,"error":"site not found"}')
				return self.close()
			### inited
			msg 	= escape.json_decode(message)
			if 'action' in msg:
				if 'module' in msg:
					self.module_id 	= ObjectId(msg['module'])
					if msg['action'] == "module":
						self.module_db	= yield self.db.module.find_one({"_id": self.module_id})
						if self.module_db:
							self.module_obj 	= self.loadModule(self.module_db)
							if self.module_obj:
								self.module_obj.ws_init(self.module_db, self)
								self._ws_inited 	= True
								result 				= '{"ok":1}'
							else:
								result 				= '{"ok":0}'
							return self.write_message(result)
			self.write_message('{"ok":0,"error":"unknown error"}')
			self.close()
		else: # inited
			yield self.module_obj.ws_read(message)

	def on_close(self):
		self.module_obj.close()
		del self.module_obj
		print("WebSocket closed")
		

class SiteStatic(tornado.web.StaticFileHandler):
	"""docstring for SiteStatic"""
	def initialize(self, **kwargs):
		pass

	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self, file):
		domain 		= self.request.host
		site 		= yield self.settings["db"].site.find_one({"domain": domain}, {'_id': 1})
		if site:
			if file.startswith('sitemap') and file.endswith('.xml'):
				path 	= 'site/%s/sitemap/' % site['_id']
			elif file.startswith('google') and file.endswith('.html'):
				path 	= 'site/%s/google/' % site['_id']
			else:
				path 	= 'site/%s/static/' % site['_id']

			if os.path.exists(path):
				super(SiteStatic, self).initialize(path)
				yield super(SiteStatic, self).get(file)
				return
		raise tornado.web.HTTPError(404)

class ModuleStatic(tornado.web.StaticFileHandler):
	"""docstring for ModuleStatic"""
	def initialize(self, **kwargs):
		pass

	def get(self, module, file):
		if module in self.settings['modules']:
			path 	= self.settings['modules'][module]['static']
			if os.path.exists(path):
				super(ModuleStatic, self).initialize(path)
				return super(ModuleStatic, self).get(file)
		raise tornado.web.HTTPError(404)
