import sys, traceback
import urllib.parse
import functools
import motorsession

from tornado import web, gen, escape

class BaseHandler(web.RequestHandler):
	def __init__(self, application, request, **kwargs):
		super(BaseHandler, self).__init__(application, request, **kwargs)
		self.application 	= application
		self.request 		= request
		self.kwargs 		= kwargs
		self.db 			= self.settings["db"]
		self.cache 			= self.settings['cache']
		# tao session object
		# kiem tra xem session do co ton tai hay ko, neu ko thi tao moi session
		sid 	= self.get_secure_cookie("sessionid", None)
		if sid:
			sid 	= sid.decode("utf8")
		self.session 		= motorsession.Session(
								self.settings["db_session"],		# db session
								sid 								# neu ko co sessionid thi None
							)

	@gen.coroutine
	def initer(self):
		old_session 	= self.get_secure_cookie("sessionid", None)
		if old_session:
			old_session 	= old_session.decode("utf8")
		self.session_id 	= yield self.session.isalive()
		if self.session_id and self.session_id != old_session:
			self.set_secure_cookie("sessionid", self.session_id)
		return self.session_id

	@gen.coroutine
	def geter(self):
		return None

	@gen.coroutine
	def poster(self):
		return None

	@web.asynchronous
	@gen.coroutine
	def get(self, *args, **kwargs):
		try:
			yield self.initer()
			result 	= yield self.geter(*args, **kwargs)
			if result and 'action' in result:
				if result['action'] == "result":
					if type(result['data']) in [dict, list]:
						return self.write(escape.json_encode(result['data']))
					return self.write(result['data'])
				elif result['action'] == "redirect":
					return self.redirect(result['data'])
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
		if not self._finished:
			return self.write('')
			self.finish()

	@web.asynchronous
	@gen.coroutine
	def post(self, *args, **kwargs):
		try:
			yield self.initer()
			result 	= yield self.poster(*args, **kwargs)
			if result and 'action' in result:
				if result['action'] == "result":
					if type(result['data']) in [dict, list]:
						return self.write(escape.json_encode(result['data']))
					return self.write(result['data'])
				elif result['action'] == "redirect":
					return self.redirect(result['data'])
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
		if not self._finished:
			return self.write('')
			self.finish()