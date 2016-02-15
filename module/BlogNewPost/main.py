import time, os, hashlib
from core import base, function
from tornado import gen, escape, template ,httpclient
from module import ModuleBase

from base64 import b64encode
from bson.objectid import ObjectId
from PIL import Image, ImageOps
from urllib.parse import urlparse

class Module(ModuleBase):
	"""docstring for Module"""
	@gen.coroutine
	def image_upload(self, file_obj, pic_path, image_path):
		with open(pic_path, "wb+") as f:
			f.write(file_obj.body)
		self.image_generic(pic_path, image_path)
	@gen.coroutine
	def image_download(self, url, pic_path, image_path):
		client 		= httpclient.AsyncHTTPClient()
		response 	= yield client.fetch(url)
		if response.error:
			return None
		else:
			with open(pic_path, "wb+") as f:
				f.write(response.body)
			self.image_generic(pic_path, image_path)

	def image_generic(self, pic_path, image_path):
		self.image_thumbnail(pic_path, image_path['thumb'][0], image_path['thumb'][1])
		self.image_medium(pic_path, image_path['medium'][0], image_path['medium'][1])
		if 'large' in image_path:
			self.image_medium(pic_path, image_path['large'][0], image_path['large'][1])
			os.remove(pic_path)

	def image_thumbnail(self, pic_path, thumb_path, size):
		image 		= Image.open(pic_path)
		# ImageOps compatible mode
		if image.mode not in ("L", "RGB"):
			image 	= image.convert("RGB")
		imagefit 	= ImageOps.fit(image, size, Image.ANTIALIAS)
		return imagefit.save(thumb_path, 'JPEG', quality=90)

	def image_medium(self, pic_path, medium_path, width = 350):
		image 		= Image.open(pic_path)
		# ImageOps compatible mode
		if image.mode not in ("L", "RGB"):
			image 	= image.convert("RGB")
		height 		= int(width/image.size[0]*image.size[1])
		image.thumbnail((width, height), Image.ANTIALIAS)
		if 'pic-banner' in self.module['setting']['server']:
			banner 	= "site/%s/%s" %(self.site.db_site['_id'], self.module['setting']['server']['pic-banner'])
			if os.path.exists(banner):
				width 		= image.size[0]
				height 		= image.size[1]
				banner 		= Image.open(banner)
				if banner.mode not in ("L", "RGB"):
					banner 		= banner.convert("RGB")
				banner.thumbnail((width, int(width/banner.size[0]*banner.size[1])), Image.ANTIALIAS)
				img 		= Image.new("RGB", (width, height + banner.size[1]), (71, 71, 71))
				img.paste(image, (0, 0, width, height))
				img.paste(banner, (0, height, banner.size[0], height + banner.size[1]))
				image 	= img

		return image.save(medium_path, "JPEG", quality=100)

	@gen.coroutine
	def form(self, argv):
		return self.site.render_string(self.module['path'] + "form.html", module=self.module, form={"template": ""})

	@gen.coroutine
	def json(self, argv):
		session 	= yield self.site.session.get(['user_id'])						
		if 'user_id' in session:
			title 		= self.site.get_argument("title", None)
			
			if title:
				source 			= self.site.get_argument("source", "")
				note 			= self.site.get_argument("note", "")
				link 			= self.site.get_argument("link", None)
				safekid 		= self.site.get_argument("safekid", False)

				content 		= {}
				hide_banner 	= False

				if safekid == "on":
					safekid 	= True
				###
				if link and len(link.split('youtube.com/watch?v=')) > 1:
					content['video'] 	= link
					format 				= "bv"
				elif 'file' in self.site.request.files or link:
					site_dir 	= "site/%s/static/upload/" % self.site.db_site['_id']
					site_link 	= "/%s/static/upload/" % self.site.db_site['_id']
					if not os.path.exists(site_dir):
						os.makedirs(site_dir)
					###
					if link:
						format 	= "bl"
						try:
							exten 	= '.' + urlparse(link).path.rsplit('.', 1)[1]
						except Exception as e:
							exten 	= '.jpg'
					else:
						format 	= "bi"
						file 	= self.site.request.files['file'][0]
						exten 	= os.path.splitext(file['filename'])[1]
					### generic name
					while True:
						post_pic 	= str(hashlib.md5((str(time.time())).encode('ascii', 'replace')).hexdigest())
						pic_name 	= post_pic + exten
						pic_path 	= site_dir + pic_name
						if not os.path.exists(pic_path):
							break

					thumb_name 		= "%s_t.jpg" % (post_pic)
					thumb_path 		= site_dir + thumb_name
					medium_name 	= "%s_m.jpg" % (post_pic)
					medium_path 	= site_dir + medium_name
					picture_name 	= "%s_l.jpg" % (post_pic)
					picture_path 	= site_dir + picture_name

					### get image
					image_path 		= {
						"thumb"		: [thumb_path, (120, 120)],
						"medium"	: [medium_path, 400],
					}
					if exten != '.gif':
						hide_banner 		= True
						image_path["large"]	= [picture_path, 800]
					else:
						picture_name 		= pic_name
					if link:
						self.image_download(link, pic_path, image_path)
					else:
						self.image_upload(file, pic_path, image_path)
					content['picture'] 		= site_link + picture_name
					content['thumbnail']	= site_link + thumb_name
					content['medium']		= site_link + medium_name

				seo_title 		= function.seo_encode(title)
				if len(content) > 0 and format:
					###### insert database
					site_id 	= self.site.db_site['_id']
					user_id 	= session['user_id']
					insert 		= yield self.site.db.post.insert(
						{
							"site_id" : site_id,
							"user_id" : user_id,
							"tags" : [
							],
							"type": "private",
							"post" : {
								"note": note,
								"source": source,
								"format": format,
								"title" : title,
								"seo_title": seo_title,
								"content" : content,
								"safekid": safekid,
								"banner": hide_banner
							},
							"like" : {
								"count" : 0,
								"data" : [
								]
							},
							"view": {"count": 0, "user": []},
							"time" : int(time.time()*1000),
							"ip" : self.site.request.remote_ip
						}
					)

					if insert:
						return self.site.redirect('/%s/%s/%s/%s.html' % (self.site.db_site['name'],self.module['setting']['server']['view_page'], insert, seo_title))