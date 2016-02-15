from .. import AppManager
from core import function

from tornado import gen, escape
from bson.objectid import ObjectId
from time import time

import re
import sys, traceback

############# MOVIE MANAGER ##############
class MovieManager(AppManager):
	"""docstring for MovieManager"""
	def __init__(self, site, module):
		super(MovieManager, self).__init__(site, module)
		self.db 		= self.site.db.post


	@gen.coroutine
	def set_user_view_post(self, post_id, format='mvi', access='public', overwrite=False):
		# mvi: movie viewing
		# mvc: movie complete
		# mvd: movie delete

		if format and format not in ['mvi', 'mvc', 'mvd']:
			print('movie format failure !')
			return False

		if (yield self.user_init()):
			post = yield self.site.db.post_view.find_one({
				'site_id': self.site_id,
				'user_id': self.user_id,
				'post_id': post_id
			},{
				'format': 1
			})

			# neu movie da vi xoa, thi movie do se ko dc danh dau xem lai
			# tru khi co keywork overwrire thi se ko kiem tra truong hop nay
			if not overwrite and post and 'format' in post and post['format'] == 'mvd':
				return None

			if post_id and type(post_id) == ObjectId:
				result = yield super(MovieManager, self).set_user_view_post(post_id, format=format, access=access, post=post)
				return result

	@gen.coroutine
	def get_user_view_post(self, format='mvi', post_id=None, time=None, sort=[('time', -1)], count=10, access='public'):
		if (yield self.user_init()):
			if post_id and type(post_id) == list:
				post_id = {'$nin': post_id}

			if type(format) == list:
				format = {'$in': format}

			result = yield super(MovieManager, self).get_user_view_post(format, post_id=post_id, time=time, sort=sort, count=count, access=access)
			return result

	# set movie dang xem do
	@gen.coroutine
	def set_user_view_post_lasted(self, mv_id, chap_index=-1, server_index=-1, part_index=-1, seek_index= 0):
		if (yield self.user_init()):
			if type(mv_id) == str and re.match(r'[a-z0-9]{24}', mv_id):
				mv_id 		= ObjectId(mv_id)

			query = {
				"post_id": mv_id,
				"site_id": self.site_id,
				"user_id": self.user_id,
			}
			view = yield self.site.db.post_view.find_one(query, {"_id":1, "format":1})
			if view and 'format' in view and view['format'] in ['mvi', 'mvc']:
				result = yield self.site.db.post_view.update({
						"_id": view['_id']
					},{
						"$set": {
							"data": {
								"chap": chap_index,
								"server": server_index,
								"part": part_index,
								"seek": seek_index,
							}
						}
					}, upsert=True)
				if result and 'n' in result and result['n'] > 0:
					return True
		return None

	# get movie dang xem do
	@gen.coroutine
	def get_user_view_post_lasted(self, mv_id):
		if (yield self.user_init()):
			if type(mv_id) == str and re.match(r'[a-z0-9]{24}', mv_id):
				mv_id 		= ObjectId(mv_id)

			result =  yield self.site.db.post_view.find_one({
					"post_id": mv_id,
					"site_id": self.site_id,
					"user_id": self.user_id,
					"format": "mvi"
				}, {'data':1})
			return result
		return None

	# set movie rating
	@gen.coroutine
	def set_post_rating(self, mv_id, rate):
		if rate >= 0 and rate <= 5 and (yield self.user_init()):
			if type(mv_id) == str and re.match(r'[a-z0-9]{24}', mv_id):
				mv_id 		= ObjectId(mv_id)

			# find user id
			result =  yield self.db.find_one({
					"_id": mv_id,
					"site_id": self.site_id,
					"format": "mv",
					"rating.user.id": self.user_id
				}, {'rating.sum':1,'rating.average':1, 'rating.count':1, 'rating.user.$':1})
			
			if not result:
				result =  yield self.db.find_one({
					"_id": mv_id,
					"site_id": self.site_id,
					"format": "mv",
				}, {'rating.sum':1,'rating.average':1, 'rating.count':1})

			# print(result)

			if result and 'rating' in result:
				if 'user' in result['rating']:
					# print('[+] rating update')
					rating_sum = result['rating']['sum'] - result['rating']['user'][0]['rate'] + rate
					yield self.db.update({
							'_id': mv_id,
							'rating.user.id': self.user_id
						},{
							"$set": {
								'rating.sum': rating_sum,
								'rating.average': rating_sum//result['rating']['count'],
								'rating.user.$.rate': rate
							}
						}, upsert= True)
				else:
					# print('[+] rating push')
					rating_sum = result['rating']['sum'] + rate
					rating_count = result['rating']['count'] + 1
					rating_average = rating_sum//rating_count

					yield self.db.update({
							"_id": mv_id
						},{
							"$set": {
								'rating.sum': rating_sum,
								'rating.count': rating_count,
								'rating.average': rating_average
							},
							'$push': {
								'rating.user': {
									"id": self.user_id,
									"rate": rate
								}
							}
						}, upsert= True)
			# return result
		return None

	# dung de goi y nhung post trong group cua movie
	# hoac nhung post gan tuong tu voi movie nay
	# overwrite post recommend
	@gen.coroutine
	def post_recommend(self, post_id=None, query=None, output=None, count=10):
		return (yield super(MovieManager, self).post_recommend(post_id=post_id, query=query, output=output, count=count))

	# neu movie da hoan thanh va ko con cap nhat moi
	# set movie finished
	@gen.coroutine
	def set_movie_finished(self, mv_id):
		if (yield self.user_init()):
			return (yield self.site.db.post.update({
						'_id': mv_id,
						'site_id': self.site_id
					},{
						"$set": {
							'post.finished': True
						}
					}, upsert=True))
	
	# neu movie chua hoan thanh
	# set movie finished
	@gen.coroutine
	def set_movie_unfinished(self, mv_id):
		if (yield self.user_init()):
			return (yield self.site.db.post.update({
						'_id': mv_id,
						'site_id': self.site_id
					},{
						"$set": {
							'post.finished': False
						}
					}, upsert=True))

	# ham dung de update/insert movie info
	# dung de update/edit cac movie information
	# neu movie ko co thi insert vao
	@gen.coroutine
	def set_movie_info(self, data, mv_id=None):
		try:
			if (yield self.user_init()):
				# update movie
				if mv_id:
					if type(mv_id) == str and re.match(r'[a-z0-9]{24}', mv_id):
						mv_id 		= ObjectId(mv_id)
					
					query 		= {}
					if 'title' in data:
						query['post.title'] 	= data['title']
					
					if 'subtitle' in data:
						query['post.subtitle'] 	= data['subtitle']
					
					if 'source' in data:
						if type(data['source']) == list:
							query['post.source'] 	= data['source']
						else:
							query['post.source'] 	= [x.strip() for x in data['source'].strip().split('\n')]
					
					if 'poster' in data:
						query['post.poster'] 	= data['poster']
					
					if 'director' in data:
						if type(data['director']) == list:
							query['post.director'] 	= data['director']
						else:
							query['post.director'] 	= [x.strip() for x in data['director'].strip().split('\n')]
						
					if 'stars' in data:
						if type(data['stars']) == list:
							query['post.stars'] 	= data['stars']
						else:
							query['post.stars'] 	= [x.strip() for x in data['stars'].strip().split('\n')]
					
					if 'country' in data:
						query['post.country'] 	= data['country']
					
					if 'year' in data:
						query['post.year'] 	= data['year']
					
					if 'category' in data:
						if type(data['category']) == list:
							query['post.category'] 	= data['category']
						else:
							query['post.category'] 	= [x.strip() for x in data['category'].strip().split('\n')]
					
					query['post.trailer'] = []
					if 'trailer' in data:
						if type(data['trailer']) == str:
							data['trailer'] = [x.strip() for x in data['trailer'].strip().split('\n')]

						if type(data['trailer']) == list:
							regex 		= re.compile("(\?v\=|\/v\/|\.be\/)(.*?)(\?|&|#|$)")
							for t in data['trailer']:
								if not '/embed/' in t:
									r = regex.search(t)
									if r:
										t = 'https://www.youtube.com/embed/%s' % r.groups()[1]
								query['post.trailer'].append(t)

					if 'image' in data:
						if type(data['image']) == list:
							query['post.image'] 	= data['image']
						else:
							query['post.image'] 	= [x.strip() for x in data['image'].strip().split('\n')]

					if 'description' in data:
						query['post.description'] 	= data['description']

					if 'length' in data:
						try:
							query['post.length'] 	= escape.json_decode(data['length'])
						except Exception as e:
							query['post.length'] 	= data['length']
					
					if 'imdb' in data:
						try:
							query['post.imdb'] = float(data['imdb'])
						except:
							pass
					
					### update seo title
					if 'title_seo' in data:
						query['post.title_seo']	= data['title_seo']
					elif all(x in query for x in ['title', 'subtitle', 'year']):
						query['post.title_seo']	= function.seo_encode('%s-%s-%s' % (data['title'], data['subtitle'], data['year']))
					
					# updater information
					# print(query)
					current_time 	= int(time()*1000)
					### update database
					update 	= yield self.db.update(
						{"_id": mv_id, 'site_id': self.site_id, 'format': 'mv'},
						{
							"$set": query,
							"$push":{
								"update": {
									"id"	: self.user_id,
									"time"	: current_time,
									"ip" 	: self.site.request.remote_ip
								}
							}
						}, 
						upsert=True
					)
					if 'n' in update and update['n'] == 1:
						return mv_id
				# insert movie
				else:
					if 'title' in data:
						query 		= {
							'safekid' 			: False,
							'title'				: data['title'],
							'subtitle' 			: data['subtitle'] if 'subtitle' in data else '',
							'source'			: data['source'] if 'source' in data else [],
							'poster' 			: data['poster'] if 'subtitle' in data else '',
							'director'			: data['director'] if 'director' in data else [],
							'stars' 			: data['stars'] if 'stars' in data else [],
							'country'			: data['country'] if 'country' in data else '',
							'year' 				: data['year'] if 'year' in data else '',
							'trailer' 			: data['trailer'] if 'trailer' in data else [],
							'image' 			: data['image'] if 'image' in data else [],
							'category' 			: data['category']  if 'category' in data else [],
							'description'		: data['description']  if 'description' in data else '',
							'length'			: data['length'] if 'length' in data else {},
							'imdb'				: data['imdb'] if 'imdb' in data else '',
							'chap' 				: []
						}
						query['title_seo']		= function.seo_encode('%s-%s-%s' % (data['title'], data['subtitle'], data['year']))
						
						if type(query['source']) == str:
							query['source'] 	= [x.strip() for x in query['source'].strip().split('\n')]
						
						if type(query['director']) == str:
							query['director'] 	= [x.strip() for x in query['director'].strip().split('\n')]
						
						if type(query['stars']) == str:
							query['stars'] 	= [x.strip() for x in query['stars'].strip().split('\n')]
						
						if type(query['category']) == str:
							query['category'] 	= [x.strip() for x in query['category'].strip().split('\n')]

						if type(query['imdb']) == str:
							try:
								query['imdb'] = float(query['imdb'])
							except:
								pass
						### insert database
						current_time 	= int(time()*1000)
						insert 			= yield self.db.insert(
							{
								"site_id" 	: self.site_id,
								'format' 	: "mv",
								"post" 		: query,
								"like" 		: {"count": 0,"info": []},
								"view"		: {"count": 0,"info": []},
								"access"	: {
									"type"	: "private",
									"time"	: current_time,
									"info"	: []
								},
								"owner"		: {
									"id" 	: self.user_id,
									"time"	: current_time,
									"ip" 	: self.site.request.remote_ip
								},
								"tag" 		: [],
								"rating"	: {
									"sum"		: 0,
									"count"		: 0,
									"average"	: 0,
									"user"		: []
								}
							}
						)
						return insert
		except Exception as e:
			traceback.print_exc(file=sys.stdout)
		return None
		
	# vi movie phai duoc insert info bang ham set_movie_info
	# nen movie da co id
	# ham dung de update/insert chap/server/part cua movie
	@gen.coroutine
	def set_movie_chaps(self, chaps, mv_id, update_log=True):
		if (yield self.user_init()):
			if type(mv_id) == str and re.match(r'[a-z0-9]{24}', mv_id):
				mv_id 		= ObjectId(mv_id)
			
			# update server data
			if chaps and type(mv_id) == ObjectId:
				try:
					# check rule
					for chap in chaps:
						if not 'name' in chap or not 'server' in chap:
							return None

						for server in chap['server']:
							if not 'name' in server or not 'part' in server:
								return None

							for part in server['part']:
								# if not 'name' in server or not 'link' in server:
								if not 'name' in part:
									return None

								if not 'link' in part:
									print("server don't have link", chap, server)
								
								# update cache if link exist and cache exists
								elif 'cache' in part and type(part['cache']) == dict and 'expire' in part['cache'] and 'video' in part['cache']:
									if type(part['cache']['expire']) != int:
										try:
											part['cache']['expire'] = int(part['cache']['expire'])
										except:
											pass
									if type(part['cache']['expire']) == int:
										expire = part['cache']['expire'] - int(time())
										if expire > 0:
											self.set_movie_link_cache(part['link'], part['cache']['video'], expire)
								if 'cache' in part:
									del part['cache']
					# pass rule
					# print('chaps', chaps)
					# update movie list
					query 	= {
						"$set": {
							"post.chap": chaps
						}
					}
					if len(chaps) > 1:
						query['$set']["post.length.current"] = len(chaps)

					if update_log:
						query["$push"] 	= {
							"update": {
								"_id"	: self.user_id,
								"time"	: int(time()*1000),
								"ip" 	: self.site.request.remote_ip
							}
						}
					update 	= yield self.db.update(
						{"_id": mv_id, 'site_id': self.site_id, "format": "mv"},
						query,
						upsert=True
					)
					if 'n' in update and update['n'] == 1:
						# movie updated => fork clear cache all chap of this movie
						self.clear_movie_part_cache(movie_id=mv_id)
						return mv_id
				except Exception as e:
					traceback.print_exc(file=sys.stdout)
		return None

	# search title cua movie
	# co the dung de tim title, subtitle, year
	@gen.coroutine
	def search_title_seo(self, string, count=50, cache=1800):
		return (yield self._searcher(
			string,
			find_at 	= "post.title_seo",
			query 		= {"format": "mv"},
			database 	= self.db,
			count 		= count,
			cache 		= cache
		))

	# tim post_group
	# sort theo thu tu lon den be
	# import data vao list da sort
	@gen.coroutine
	def search_post_group(self, string, count=50, cache=1800):
		query 	= {}
		if string and len(string) > 0:
			groups 	= yield self._searcher(
				string,
				find_at 	= "name_seo",
				query 		= {"format": "pg"},
				database 	= self.site.db.post_group,
				count 		= count,
				cache 		= cache
			)
			query["_id"] 	= {"$in": groups}
			searcher 		= True
		else:
			searcher 		= False
			
		groups_info		= yield self.site.db.post_group.find(query, {
				"_id": 1,
				"name": 1,
				"post": 1
			}
		).to_list(length=count)

		if searcher:
			# sort with post id
			result = groups
			for i in range(0, len(groups)):
				if type(result[i]) == ObjectId:
					for p in groups_info:
						if result[i] == p['_id']:
							result[i] = p
							break

				if type(result[i]) == ObjectId:
					result[i] = None

			result = [x for x in result if x]
			return result
		else:
			return groups_info

	# ham dung de lay danh sach link video cua 1 part trong movie
	# generic movie part
	@gen.coroutine
	def get_movie_part(self, movie_id, chap_index, server_index, cache_time=3600):
		try:
			# find cache
			cache_string 	= "%s-c%s-s%s" % (str(movie_id), chap_index, server_index)
			cache_result 	= yield self.site.cache.get(source=cache_string, lock=True, lock_time=3, lock_count=30)
			if cache_result and 'data' in cache_result:
				return cache_result['data']

			if type(movie_id) == str and re.match(r'[a-z0-9]{24}', movie_id):
				movie_id 	= ObjectId(movie_id)

			if type(movie_id) == ObjectId:
				chap_index 		= int(chap_index)
				server_index 	= int(server_index)

				post = yield self.db.find_one({
						"_id" 		: movie_id,
						"site_id" 	: self.site.site_db['_id'],
						"format" 	: "mv"
					}, {
						'post.xyzhack': 1, # hack find
						'post.chap': {"$slice": [chap_index, 1]},
						'post.chap.server': {"$slice": [server_index, 1]}
					})

				if post and 'post' in post and 'chap' in post['post'] and len(post['post']['chap']) > 0:
					chap 	= post['post']['chap'][0]
					if 'server' in chap and len(chap['server']) > 0 and 'part' in chap['server'][0]:
						part 	= chap['server'][0]['part']
						result 	= []
						for p in part:
							json = {"name": p['name']}
							if 'link' in p and p['link']:
								json['video'] = yield self.get_movie_link_cache(p['link'], cache_time=cache_time)
							result.append(json)
						# fork cache store
						self.site.cache.set( cache_string, result, cache_time,
							query={
								"of" : {
									"format": "mvpart",
									"movie": movie_id,
									"module": {
										"name": self.module['name'],
										"id": self.module['_id']
									}
								}
							}
						)
						return result
		except:
			traceback.print_exc(file=sys.stdout)
	
	# clear movie part cache when update part
	@gen.coroutine
	def clear_movie_part_cache(self, movie_id):
		self.site.cache.clear(
			query = {
				"of.format": "mvpart",
				"of.movie": movie_id
			},
			everything = True
		)

	# vi video co the tu remote server nhu picasaweb
	# nen ham nay dung de lay cac link video va cache lai
	# movie get part cache
	@gen.coroutine
	def get_movie_link_cache(self, link, cache_time=3600):
		try:
			# youtube
			if 'youtube.com' in link[:28] or 'youtu.be' in link[:16]:
				if 'youtu.be/' in link[:17]:
					vd_id 	= link.split('youtu.be/',2)
					if len(vd_id) > 1:
						return "https://www.youtube.com/watch?v=%s" % vd_id[1]
				return link

			# picasaweb
			elif 'picasaweb' in link[:18]:
				# find cache
				cache_result 	= yield self.site.cache.get(source=link, lock=True, lock_count=30)
				if cache_result and 'data' in cache_result:
					return cache_result['data']

				source 	= yield function.http_client(link, c_delay=0)
				source 	= escape.json_decode(source)
				# print('source', source)
				json 	= source['feed']['media']['content']
				expire 	= 0
				video 	= []
				for v in json:
					if not expire and 'expire' in v['url']:
						expire 	= int(v['url'].split('expire=',1)[1].split('&',1)[0])

					if 'type' in v and (v['type'].startswith('video/') or v['type'].startswith('application/')):
						video.append(v)
				# store cache
				cache_time = cache_time + int(time())
				if expire > cache_time:
					self.set_movie_link_cache(link, video, expire - cache_time)
				return video
			elif 'docs.google.com' in link[:25]:
				source 		= yield function.http_client(link, c_delay=0)
				s_format 	= source.split('["fmt_list","',1)[1].split('"]',1)[0].split(',')

				v_format 	= {}
				for f in s_format:
					f = f.split('/', 2)
					size = f[1].split('x')
					v_format[f[0]] = size

				video 		= []
				s_video 	= source.split('["url_encoded_fmt_stream_map","',1)[1].split('"]',1)[0]
				s_video 	= escape.json_decode('["%s"]'% s_video)[0].split(',itag=')
				for v in s_video:
					itag = v.split('&url=',1)[0]
					if '=' in itag:
						itag = itag.rsplit('=',1)[1]
					if itag in v_format:
						iurl = v.split('&url=',1)[1].split('&',1)[0]
						itype = escape.url_unescape(v.split('&type=',1)[1]).split('&',1)[0].split(';',1)[0]
						video.append({
								"url": escape.url_unescape(iurl),
								"width": int(v_format[itag][0]),
								"height": int(v_format[itag][1]),
								"type": itype
							})
				# print(video)
				# ko cache vi part cache da du 3600s
				return video

			# https://plus.google.com/_/photos/lightbox/photo/117469308172362315957/6068501600309862578?soc-app=2&cid=0&soc-platform=1&ozv=es_oz_20141009.12_p1&avw=phst%3A31&f.sid=-7178491292173930655&_reqid=235130&rt=j
			
			# https://plus.google.com/photos/103168733314236184036/albums/6063013498393185633/6063426189374545202?pid=6063426189374545202&amp;oid=103168733314236184036

			# https://plus.google.com/_/photos/lightbox/photo/117224281821248286118/6072825042706372306

			elif 'plus.google.com' in link[:25]:
				# find cache
				cache_result 	= yield self.site.cache.get(source=link, lock=True, lock_count=30)
				if cache_result and 'data' in cache_result:
					return cache_result['data']

				source 		= yield function.http_client(link, c_delay=0)
				# get photoid
				source 		= source.split(',"6063426189374545202",',1)[1].split('video.googleusercontent.com',1)[0].split('redirector.googlevideo.com')
				# print(source)
				expire 		= 0
				video 		= []
				for i, v in enumerate(source):
					if i > 0:
						size = source[i-1].rsplit('[',1)[1].split(',')
						url = "https://redirector.googlevideo.com" + v.split('"]',1)[0]
						url = escape.url_unescape(escape.json_decode('["%s"]'% url)[0])
						if not expire and 'expire' in url:
							expire	= int(url.split('expire=',1)[1].split('&',1)[0])
						video.append({
								"url": url,
								"width": int(size[1]),
								"height": int(size[2]),
								"type": "video/mpeg4"
							})
						

				# store cache
				cache_time = cache_time + int(time())
				if expire > cache_time:
					self.set_movie_link_cache(link, video, expire - cache_time)
				return video
		except:
			traceback.print_exc(file=sys.stdout)
	
	# ham dung de set cache cho 1 link part nao do trong movie
	# movie set part cache
	@gen.coroutine
	def set_movie_link_cache(self, link, data, cache_time=None):
		# fork cache store
		self.site.cache.set(link, data, cache_time,
			query={
				"of" : {
					"format": "mvlink",
					"module": {
						"name": self.module['name'],
						"id": self.module['_id']
					}
				}
			}
		)