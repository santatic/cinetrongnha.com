from tornado import gen, escape
from base64 import b64encode
from bson.objectid import ObjectId
from time import time
from module import ModuleBase
from core import function
from core.app.movie import MovieManager
import re

class Module(ModuleBase):
	# """docstring for Module"""
	def __init__(self):
		super(Module, self).__init__()
		self.script.extend([
			"/static/js/jquery.lazyload.min.js",
		])

	@gen.coroutine
	def form(self, argv, default = None):
		# generic template for json data
		post_argv 		= self.post_argv()
		info_argv 		= self.info_argv()
		template 		= {
			"post": self.site.render_string(self.module['path'] + "post.html", argv=[post_argv]).decode("utf-8"),
			"info": self.site.render_string(self.module['path'] + "info.html", argv=info_argv).decode("utf-8")
		}
		form_argv = {
				"template": b64encode(escape.json_encode(template).encode("utf-8")),
				"post": '{%% raw module["%s"]["post"] %%}' % self.module['_id']
			}
		if default:
			form_argv.update(default)

		return self.site.render_string(
			self.module['path'] + "form.html",
			module 	= self.module,
			argv 	= form_argv
		), True

	@gen.coroutine
	def form_post(self, argv):
		if 'init_post' in self.module['setting']['server'] and not self.module['setting']['server']['init_post']:
			post_form 		= ''
		else:
			json_argv 		= yield self.json(argv)
			post_form 		= self.site.render_string(self.module['path'] + "post.html", argv=json_argv['post'])
		return {"post": post_form}

	@gen.coroutine
	def json(self, argv):
		self.manager 	= MovieManager(self.site, self.module)
		
		action 		= self.site.get_argument('action', None)
		search 		= self.site.get_argument('search', None)
		post_skip 	= self.site.get_argument('skip', None)
		post_tab 	= self.site.get_argument('tab', None)
		post_count 	= int(self.site.get_argument('count', 0))
		post_sort 	= False
		
		if search:
			post_id 	= yield self.manager.search_title_seo(search, post_count)
			post_sort 	= True
		else:
			post_id 	= self.site.get_argument('post', None)
			if post_id == None:
				try:
					post_id = argv[0]
				except:
					pass
			if type(post_id) == str and len(post_id) == 24:
				post_id 	= ObjectId(post_id)

		if action == "info":
			output = {
				'post.title':1,
				'post.subtitle':1,
				'post.poster':1,
				'post.director':1,
				'post.stars':1,
				'post.description':1,
				'post.country':1,
				'post.year':1,
				'post.length':1,
				'post.category':1,
				'post.title_seo':1,
				'post.trailer':1,
				'post.imdb':1,
				# 'view.count':1,
			}
		else:
			output = {
				'post.title':1,
				'post.subtitle':1,
				'post.title_seo':1,
				'post.poster':1,
				'post.year':1,
				'post.imdb':1,
				'post.length':1,
				# 'rating.count': 1,
				# 'rating.average': 1,
				'view.count':1,
			}

		posts 	= yield self.post_json(
			post_id		= post_id,
			post_skip	= post_skip,
			post_tab 	= post_tab,
			post_count 	= post_count,
			post_sort 	= post_sort,
			output 		= output,
		)
		posts_argv 	= []
		if action == "info":
			for post in posts:
				posts_argv.append(self.info_argv(post))
		else:
			for post in posts:
				posts_argv.append(self.post_argv(post))
		return {"post": posts_argv, "form": {'search': search}}

	def post_argv(self, post= None):
		if post and 'post' in post:
			argv 	= {
				"id" 			: str(post['_id']),
				"title"			: escape.xhtml_escape("%s (%s)" % (post['post']['title'], post['post']['year'])),
				"subtitle" 		: escape.xhtml_escape(post['post']['subtitle']),
			}

			if 'poster' in post['post']:
				argv['poster'] 	= post['post']['poster']
			else:
				argv['poster'] 	= ''

			# seo title generic
			if 'title_seo' in post['post']:
				title_seo 	= post['post']['title_seo']
			else:
				title_seo 	= function.seo_encode('%s-%s-%s' % (post['post']['title'], post['post']['subtitle'], post['post']['year']))
			argv["link"] 	= "%s/%s/%s/%s.html" % (self.site.domain_root, self.module['setting']['server']['page_view'], post['_id'], escape.url_escape(title_seo))
			
			# imdb
			if 'imdb' in post['post']:
				argv['imdb'] 	= post['post']['imdb']
			else:
				argv['imdb'] 	= 0

			# # rating
			# if 'rating' in post:
			# 	# rating 	= post['rating']
			# 	argv['rating_count'] 	= int(post['rating']['count'])
			# 	argv['rating_average'] 	= int(post['rating']['average'])
			# else:
			# 	argv['rating_count'] 	= 0
			# 	argv['rating_average'] 	= 0

			# view count
			if 'view' in post and 'count' in post['view']:
				argv['view_count'] = post['view']['count']
			else:
				argv['view_count'] = 0

			# length
			try:
				argv['length'] 		= "%s/%s" % (post['post']['length']['current'], post['post']['length']['count'])
				argv['length_type'] = post['post']['length']['type']
			except:
				argv['length'] 		= ''
				argv['length_type'] = 'short'
		else:
			argv 	= {
				"id" 				: '{{ id }}',
				"title"				: '{{ title }}',
				"subtitle"			: '{{ subtitle }}',
				"poster" 			: '{{ poster }}',
				"link" 				: '{{ link }}',
				# "rating_count"		: '{{ rating_count }}',
				# "rating_average"	: '{{ rating_average }}',
				"view_count"		: '{{ view_count }}',
				"length"			: '{{ length }}',
				"length_type"		: '{{ length_type }}',
				"imdb"				: '{{ imdb }}'
			}
		return argv

	def info_argv(self, post= None):
		if post:
			# search page
			searcher 	= "/%s/" % ("search")
			
			# # title
			# if 'title' in post['post']:
			# 	title 		= escape.xhtml_escape("%s - %s (%s)" % (post['post']['title'], post['post']['subtitle'], post['post']['year']))
			# else:
			# 	title 		= ""

			# poster
			if 'poster' in post['post']:
				poster 		= escape.xhtml_escape(post['post']['poster'])
			else:
				poster 		= ""

			# director
			if 'director' in post['post']:
				director 	= []
				for dir in post['post']['director']:
					director.append('<a href="%s?director=%s" site-goto="">%s</a>' % (searcher, escape.url_escape(dir), dir))
				director 	= ', '.join(director)
			else:
				director 	= ""

			# stars
			if 'stars' in post['post']:
				stars 	= []
				for star in post['post']['stars']:
					stars.append('<a href="%s?stars=%s" site-goto="">%s</a>' % (searcher, escape.url_escape(star), star))
				stars 	= ', '.join(stars)
			else:
				stars 	= ""

			# description
			if 'description' in post['post']:
				description 	= post['post']['description']
			else:
				description 	= ""

			# country
			if 'country' in post['post']:
				country 	= '<a href="%s?country=%s" site-goto="">%s</a>' % (searcher, escape.url_escape(post['post']['country']), post['post']['country'])
			else:
				country 	= ""

			# year
			if 'year' in post['post']:
				year 	= '<a href="%s?year=%s" site-goto="">%s</a>' % (searcher, escape.url_escape(post['post']['year']), post['post']['year'])
			else:
				year 	= ""

			# length
			if 'length' in post['post']:
				length 	= post['post']['length']
				if type(length) == dict:
					length 	= "%s %s" % (length['count'], "tập" if length['type'] == "long" else "phút")
			else:
				length 	= ""

			# category
			if 'category' in post['post']:
				category 	= []
				for cate in post['post']['category']:
					category.append('<a href="%s?category=%s" site-goto="">%s</a>' % (searcher, escape.url_escape(cate), cate))
				category 	= ', '.join(category)
			else:
				category 	= ""

			# seo title
			if 'title_seo' in post['post']:
				title_seo 		= escape.xhtml_escape(post['post']['title_seo'])
			else:
				title_seo 	= ''

			# trailer
			if 'trailer' in post['post']:
				trailer 	= []
				regex 		= re.compile("(\?v\=|\/v\/|\.be\/)(.*?)(\?|&|#|$)")
				for t in post['post']['trailer']:
					if not '/embed/' in t:
						r = regex.search(t)
						if r:
							t = 'https://www.youtube.com/embed/%s' % r.groups()[1]
					trailer.append('<div class="embed-responsive embed-responsive-16by9"><iframe class="embed-responsive-item" src="%s"></iframe></div>' % escape.xhtml_escape(t))
				trailer 	= ''.join(trailer)
			else:
				trailer 	= ''

			# imdb
			if 'imdb' in post['post']:
				imdb 	= post['post']['imdb']
			else:
				imdb 	= 0

			###
			argv 	= {
				"id" 				: str(post['_id']),
				"title"				: escape.xhtml_escape("%s (%s)" % (post['post']['title'], post['post']['year'])),
				"subtitle" 			: escape.xhtml_escape(post['post']['subtitle']),
				"poster" 			: poster,
				"director" 			: director,
				"stars" 			: stars,
				"description" 		: description,
				"country" 			: country,
				"year" 				: year,
				"length" 			: length,
				"category" 			: category,
				"trailer"			: trailer,
				"imdb"				: imdb,
				"link" 				: "%s/%s/%s/%s.html" % (self.site.domain_root, self.module['setting']['server']['page_view'], post['_id'], title_seo),
			}
		else:
			argv 	= {
				"id" 				: '{{ id }}',
				"title"				: '{{ title }}',
				"subtitle"			: '{{ subtitle }}',
				"poster" 			: '{{ poster }}',
				"director" 			: '{{ director }}',
				"stars" 			: '{{ stars }}',
				"description" 		: '{{ description }}',
				"country" 			: '{{ country }}',
				"year" 				: '{{ year }}',
				"length" 			: '{{ length }}',
				"category" 			: '{{ category }}',
				"trailer"			: '{{ trailer }}',
				"imdb"				: '{{ imdb }}',
				"link"				: '{{ link }}'
			}
		return argv

	@gen.coroutine
	def post_json(
		self,
		post_id 	= None,
		post_skip 	= None,
		post_tab 	= None,
		post_count 	= 0,
		post_sort 	= False,
		sort 		= [('access.time', -1)],
		output 		= None,
	):
		#  limit count of post
		if not post_count and 'count' in self.module['setting']['server']:
			post_count = self.module['setting']['server']['count']
		try:
			if post_count > self.module['setting']['server']['max_count']:
				post_count = self.module['setting']['server']['max_count']
		except:
			pass
		# set tab static
		if not post_tab and 'tab' in self.module['setting']['server']:
			post_tab = self.module['setting']['server']['tab']

		posts 		= []
		if post_count > 0:
			###
			query	= {
				'site_id'		: self.module['site_id'],
				'format'		: "mv",
				'access.type' 	: "public"
			}
			###
			if 'channel' in self.site.site_db['page']:
				query['channel'] = self.site.site_db['page']['channel']['_id']

			if 'post_length' in self.module['setting']['server'] and self.module['setting']['server']['post_length'] in ['short', 'long']:
				query['post.length.type'] = self.module['setting']['server']['post_length']
			###
			if post_tab == "recommend":
				result 	= yield self.manager.post_recommend(post_id, count=post_count)
				if result and post_id in result:
					result.remove(post_id)
				post_id = result
				# sort output = tab rate
				post_tab = "rate"

			if post_tab == "rate":
				sort = [('rating.average', -1), ('rating.count', -1)] + sort
			
			if post_id:
				if type(post_id) == str:
					post_id 	= [ObjectId(p) for p in post_id.split(',')]
				elif type(post_id) == ObjectId:
					post_id 	= [post_id]

				if type(post_id) == list:
					query['_id'] = {'$in': post_id}
			###
			if not output:
				output = {}
			cursor 		= self.site.db.post.find(query, output).sort(sort)
			if post_skip:
				try:
					cursor = cursor.skip(int(post_skip))
				except:
					pass
			posts	= yield cursor.to_list(length=post_count)

			# sort with post id
			if post_sort and len(post_id) > 1:
				result = query['_id']['$in']
				for i in range(0,len(result)):
					if type(result[i]) == ObjectId:
						for p in posts:
							if result[i] == p['_id']:
								result[i] = p
								break
					if type(result[i]) == ObjectId:
						result[i] = None

				posts = [x for x in result if x]
		return posts