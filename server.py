#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, logging
# pass library load
sys.path.append(os.path.abspath('library'))
import motor

from tornado import web, options, ioloop, httpserver
from tornado.options import define, options
from core import login, register, site, cache
from motorsession import Session
from module import ModuleLoader

###################
define("port", default=8888, help="run on the given port", type=int)
define("dbhost", default="localhost", help="database port", type=str)
define("dbport", default=27017, help="database port", type=int)
###################
logging.basicConfig(filename="error.log",level=logging.WARNING,)
logging.getLogger("tornado.access").propagate = False
###################
class Application(web.Application):
	def __init__(self):
		handlers = [
			# (r"/register", register.Register),
			(r"/login", login.LoginOAuth),
			(r"/login/facebook", login.LoginOAuthFacebook),
			(r"/?", site.Site),
			(r"/ws/?$", site.SiteWS),
			(r"/sitestatic/(.*?)$", site.SiteStatic, {"path": "./"}),
			(r"/(sitemap[a-zA-Z0-9\.\-\_]*\.xml)$", site.SiteStatic, {"path": "./"}), # google sitemap
			(r"/(google[a-z0-9]+\.html)$", site.SiteStatic, {"path": "./"}), # google webmaster verify
			(r"/module/([a-zA-Z0-9]+)/static/(.*?)$", site.ModuleStatic),
			(r"/([a-z0-9]{24}/(.*?))$", web.StaticFileHandler, {"path": "site"}), 	# fix bug for old version
			(r"/([a-zA-Z0-9\.\-\_]+)/?$", site.Site),
			(r"/([a-zA-Z0-9\.\-\_]+)/([a-zA-Z0-9\.\-\_]{24})(.*?)$", site.Site),
		]
		### load module
		modules 	= ModuleLoader().modules
		
		settings = {
			# 'debug'					: True,
			'xheaders' 				: True,
			# 'xsrf_cookies'			: True,
			# 'xsrf_cookie_version'	: 1,
			'cookie_secret'			: "iTfgAulVRmq2KO9CFYdPwla+45Mzs0s9g5Vtt5wNtQA1V5qnvO5L+qmWGmpyGsGw1",
			'template_path'			: os.path.join(os.path.dirname(__file__), "template"),
			'static_path'			: os.path.join(os.path.dirname(__file__), "static"),
			'login_url'				: "/login",
			# 'google_oauth':			{
			# 	"key":	"559871339827.apps.googleusercontent.com",
			# 	"secret": "zhAUqeJvUglRBrM-fb89S2Ee"
			# },
			'facebook_oauth'		: {
				"key":	"680287678695523",
				"secret":	"e1f3f74757aa265117a0130a5473f19f"
			},
			"db"					: motor.MotorClient(options.dbhost, options.dbport).database,
			"db_session"			: motor.MotorClient(options.dbhost, options.dbport).sessions.session,
			"modules"				: modules
		}
		
		settings['cache']  = cache.CacheManager(settings['db'].cache)
		# clear cache
		settings['cache'].clear()

		Session(settings['db_session']).clear_old()

		web.Application.__init__(self, handlers, **settings)
		# self.db = torndb.Connection(
		# host=options.mysql_host, database=options.mysql_database,
		# user=options.mysql_user, password=options.mysql_password)
if __name__ == "__main__":
	options.parse_command_line()
	server = httpserver.HTTPServer(Application())
	server.listen(options.port)
	ioloop.IOLoop.instance().start()