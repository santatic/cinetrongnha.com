import time, re
from tornado import gen, escape
from base64 import b64encode
from bson.objectid import ObjectId
from core.app.movie import MovieManager
from core import report
from module import ModuleBase

class Module(ModuleBase):
	"""docstring for Module"""
	def __init__(self):
		super(Module, self).__init__()
		self.script.extend([
			"/static/jwplayer/jwplayer.js",
			# "/static/jwplayer/jwpsrv.js"
		])

	@gen.coroutine
	def form(self, argv):
		post_argv 		= self.post_argv()
		template 		= {
			"post": self.site.render_string(self.module['path'] + "post.html", argv=post_argv, module= self.module).decode("utf-8")
		}
		return self.site.render_string(
			self.module['path'] + "form.html",
			module 	= self.module,
			form 	= {
				"template": b64encode(escape.json_encode(template).encode("utf-8")),
				"post": '{%% raw module["%s"]["post"] %%}' % self.module['_id']
			}
		), True
	@gen.coroutine
	def form_post(self, argv):
		json_argv 		= yield self.json(argv)
		if 'post' in json_argv and json_argv['post']:
			post_form 	= self.site.render_string(self.module['path'] + "post.html", argv=json_argv['post'], module= self.module)
		else:
			post_form 	= "Nội dung đang chờ kiểm duyệt hoặc không tồn tại!"
		return {"post": post_form}

	@gen.coroutine
	def json(self, argv):
		self.manager 	= MovieManager(self.site, self.module)

		action 		= self.site.get_argument('action', None)
		post_id 	= self.site.get_argument('post', None)
		
		if post_id == None:
			try:
				post_id = argv[0]
			except:
				pass

		if type(post_id) == str and re.match(r'[a-z0-9]{24}', post_id):
			post_id 		= ObjectId(post_id)

		if post_id:
			# update movie track
			post_track 	= self.site.get_argument('track', None)
			if post_track:
				if len(post_track) == 24:
					track_id = ObjectId(post_track)
				self.manager.set_user_view_post(track_id)

				# set movie view count
				self.manager.set_post_view(post_id)
		
			# part view
			if action == "part":
				# lock some request failure
				if self.site.request.headers.get('X-Requested-With') == 'XMLHttpRequest' and self.site.site_db['domain'][0] in self.site.request.headers.get('Referer')[:50]:
					mv_chap_index 		= self.site.get_argument('c-i', 0)
					mv_server_index 	= self.site.get_argument('s-i', 0)
					result = yield self.manager.get_movie_part(post_id, mv_chap_index, mv_server_index)
					if result:
						return {"post": result}
			
			# save last viewing movie chap/server/part
			elif action == "viewing":
				mv_chap 	= self.site.get_argument('mv-chap', -1)
				mv_server 	= self.site.get_argument('mv-server', -1)
				mv_part 	= self.site.get_argument('mv-part', -1)
				mv_seek 	= self.site.get_argument('mv-seek', 0)
				###
				try:
					mv_chap = int(mv_chap)
				except:
					mv_chap = -1
				###
				try:
					mv_server = int(mv_server)
				except:
					mv_server = -1
				###
				try:
					mv_part = int(mv_part)
				except:
					mv_part = -1
				###
				try:
					mv_seek = float(mv_seek)
				except:
					mv_seek = -1
				###
				# print(post_id, mv_chap, mv_server, mv_part, mv_seek)
				self.manager.get_user_view_post_lasted(post_id, mv_chap, mv_server, mv_part, mv_seek)
				return '{"error":0,"success":1}'
			elif action == "rating":
				mv_rate 	= self.site.get_argument('rate', None)
				if mv_rate:
					# print('rate', mv_rate)
					mv_rate = int(mv_rate)
					self.manager.set_post_rating(post_id, mv_rate)
					return '{"error":0,"success":1}'
			elif action == "report":
				mv_report 	= self.site.get_argument('report', None)
				mv_content	= self.site.get_argument('content', None)
				obj 		= report.SiteReport(self.site)
				# fork
				obj.set(mv_report, mv_content)
				return '{"error":0,"success":1}'
			else:
				post 	= yield self.post_json(argv[0])
				if post:
					argv 	= self.post_argv(post)
					
					# facebook graph
					self.site.graph['og:url'] 		= argv['link']
					self.site.graph['og:title'] 	= "%s - %s - %s"% (argv['title'], self.site.site_db['setting']['title'], self.site.site_db['domain'])
					if len(argv['description']) > 10:
						self.site.graph['og:description'] 	= escape.xhtml_escape("Xem Phim %s, %s" % (argv['title'], argv['description'][:300]))

					if 'poster' in argv:
						image 		= argv['poster']
					# elif 'trailer' in post['post']['trailer']:
					# 	image 		= "http://i1.ytimg.com/vi/%s/hqdefault.jpg" % post['post']['content']['video'].split('youtube.com/watch?v=',2)[1].split(r'/[#|\?]/', 1)[0]
					else:
						image 		= None
					if image:
						self.site.graph['og:image'] 	= [
							["og:image", image],
							["og:image:width", "1500"],
							["og:image:height", "1500"]
						]

				else:
					argv 	= None				
				return {"post": argv}
		return '{"error":1,"success":0}'

	def post_argv(self, post=None):
		if post:
			# search page
			searcher 	= "/%s/" % ("search")
			
			###
			argv 	= {
				"id" 				: str(post['_id']),
			}

			# title
			if 'title' in post['post']:
				argv['title'] 		= escape.xhtml_escape("%s - %s (%s)" % (post['post']['title'], post['post']['subtitle'], post['post']['year']))
			else:
				argv['title'] 		= ""

			# poster
			if 'poster' in post['post']:
				argv['poster'] 		= escape.xhtml_escape(post['post']['poster'])
			else:
				argv['poster'] 		= ""

			# director
			if 'director' in post['post']:
				director 	= []
				for dir in post['post']['director']:
					director.append('<a href="%s?director=%s" site-goto="">%s</a>' % (searcher, escape.url_escape(dir), dir))
				argv['director'] 	= ', '.join(director)
			else:
				argv['director'] 	= ""

			# stars
			if 'stars' in post['post']:
				stars 	= []
				for star in post['post']['stars']:
					stars.append('<a href="%s?stars=%s" site-goto="">%s</a>' % (searcher, escape.url_escape(star), star))
				argv['stars'] 	= ', '.join(stars)
			else:
				argv['stars'] 	= ""

			# description
			if 'description' in post['post']:
				argv['description'] 	= post['post']['description']
			else:
				argv['description'] 	= ""

			# country
			if 'country' in post['post']:
				argv['country'] 	= '<a href="%s?country=%s" site-goto="">%s</a>' % (searcher, escape.url_escape(post['post']['country']), post['post']['country'])
			else:
				argv['country'] 	= ""

			# year
			if 'year' in post['post']:
				argv['year'] 	= '<a href="%s?year=%s" site-goto="">%s</a>' % (searcher, escape.url_escape(post['post']['year']), post['post']['year'])
			else:
				argv['year'] 	= ""

			# length
			if 'length' in post['post'] and type(post['post']['length']) == dict:
				obj 	= post['post']['length']
				if obj['type'] == "long":
					# length = "%s/%s tập" % (obj['current'], obj['count'])
					argv['length'] = "%s tập" % obj['count']
					if 'current' in obj:
						argv['length'] = "%s/%s" % (obj['current'], argv['length'])
				else:
					argv['length'] 	= "%s phút" % obj['count']
			else:
				argv['length'] 	= ""

			# category
			if 'category' in post['post']:
				category 	= []
				for cate in post['post']['category']:
					category.append('<a href="%s?category=%s" site-goto="">%s</a>' % (searcher, escape.url_escape(cate), cate))
				argv['category'] 	= ', '.join(category)
			else:
				argv['category'] 	= ""

			# lastview
			if 'lastview' in post:
				argv['lastview'] = "%s|%s|%s|%s" % (post['lastview']['chap'], post['lastview']['server'], post['lastview']['part'], post['lastview']['seek'])
			else:
				argv['lastview'] = ""

			# seo title
			if 'title_seo' in post['post']:
				title_seo 		= escape.xhtml_escape(post['post']['title_seo'])
			else:
				title_seo 	= ''
			argv["link"] 	= "%s/%s/%s/%s.html" % (self.site.domain_root, self.site.site_db['page']['name'], post['_id'], title_seo)

			# image background
			if 'image' in post['post'] and post['post']['image']:
				argv['background'] = post['post']['image'][0]
			else:
				argv['background'] = 'https://lh6.googleusercontent.com/-UCQ1vCljDNk/VD5yhNY3cBI/AAAAAAAAAFM/ubsvrbtVq3Q/s1200/286652.jpg'

			# rating
			if 'rating' in post:
				# rating 	= post['rating']
				argv['rating_count'] 	= int(post['rating']['count'])
				argv['rating_average'] 	= int(post['rating']['average'])
			else:
				argv['rating_count'] 	= 0
				argv['rating_average'] 	= 0

			# movie chaps
			chaps 	= []
			if 'chap' in post['post']:
				for chap in post['post']['chap']:
					o_chap = {"name": chap['name'], "server": []}
					for server in chap['server']:
						o_chap['server'].append({"name": server['name']})
					chaps.append(o_chap)
			argv['chap'] 	= b64encode(escape.json_encode(chaps).encode("utf-8")).decode("utf-8")			
		else:
			argv 	= {
				"id" 				: '{{ id }}',
				"title"				: '{{ title }}',
				"poster" 			: '{{ poster }}',
				"director" 			: '{{ director }}',
				"stars" 			: '{{ stars }}',
				"description" 		: '{{ description }}',
				"country" 			: '{{ country }}',
				"year" 				: '{{ year }}',
				"length" 			: '{{ length }}',
				"category" 			: '{{ category }}',
				"background"		: '{{ background }}',
				"chap" 				: '{{ chap }}',
				"lastview"			: '{{ lastview }}',
				"rating_count"		: '{{ rating_count }}',
				"rating_average"	: '{{ rating_average }}',
				"link"				: '{{ link }}',
			}
		return argv

	@gen.coroutine
	def post_json(self, post_id):
		if type(post_id) == str and re.match(r'[a-z0-9]{24}', post_id):
			post_id 		= ObjectId(post_id)
		
		if type(post_id) == ObjectId:
			query = {
				'_id' 		: post_id,
				'site_id' 	: self.module['site_id'],
				'format' 	: 'mv'
			}

			if 'access' in self.module['setting']['server']:
				query['access.type'] = self.module['setting']['server']['access']
			# print(query)
			post 	= yield self.manager.db.find_one( query, {
				'rating.count': 1,
				'rating.average': 1,
				'post.title': 1,
				'post.subtitle': 1,
				'post.title_seo': 1,
				'post.poster': 1,
				'post.director': 1,
				'post.stars': 1,
				'post.description': 1,
				'post.country': 1,
				'post.year': 1,
				'post.length': 1,
				'post.category': 1,
				# 'post.image': {"$slice": [0,1]}, 
				'post.image': 1,
				'post.chap.name': 1,
				'post.chap.server.name': 1,
			})
			# print(post)
			if post:
				lastview 	= yield self.manager.get_user_view_post_lasted(post['_id'])
				if lastview and 'data' in lastview:
					post['lastview'] = lastview['data']
			return post