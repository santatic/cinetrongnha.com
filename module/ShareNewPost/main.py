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
	def image_upload(self, file_obj, pic_path, thumb_path):
		with open(pic_path, "wb+") as f:
			f.write(file_obj.body)
		self.image_thumbnail(pic_path, thumb_path)
		return os.remove(pic_path)
	
	@gen.coroutine
	def image_download(self, url, pic_path, thumb_path):
		try:
			client 		= httpclient.AsyncHTTPClient()
			response 	= yield client.fetch(url)
			if response.error:
				return None
			else:
				with open(pic_path, "wb+") as f:
					f.write(response.body)
				return self.image_thumbnail(pic_path, thumb_path)
		except Exception as e:
			print(e)

	def image_thumbnail(self, pic_path, thumb_path):
		image 		= Image.open(pic_path)
		# ImageOps compatible mode
		if image.mode not in ("L", "RGB"):
			image 	= image.convert("RGB")
		imagefit 	= ImageOps.fit(image, (120, 120), Image.ANTIALIAS)
		return imagefit.save(thumb_path, 'JPEG', quality=90)

	@gen.coroutine
	def form(self, argv):
		return self.site.render_string(self.module['path'] + "form.html", module=self.module, form={"template": ""})

	@gen.coroutine
	def json(self, argv):
		session 	= yield self.site.session.get(['user_id'])						
		if 'user_id' in session:
			title 		= self.site.get_argument("title", None)
			
			if title:
				source 		= self.site.get_argument("source", "")
				note 		= self.site.get_argument("note", "")
				link 		= self.site.get_argument("link", None)
				image 		= self.site.get_argument("image", None)
				safekid 	= self.site.get_argument("safekid", False)

				content 	= {}
				if safekid == "on":
					safekid 	= True
				###
				if 'file' in self.site.request.files or image:
					site_dir 	= "site/%s/static/upload/" % self.site.db_site['_id']
					site_link 	= "/%s/static/upload/" % self.site.db_site['_id']
					if not os.path.exists(site_dir):
						os.makedirs(site_dir)
					###
					if image:
						try:
							exten 	= '.' + urlparse(image).path.rsplit('.', 1)[1]
						except Exception as e:
							exten 	= '.jpg'
					else:
						file 	= self.site.request.files['file'][0]
						exten 	= os.path.splitext(file['filename'])[1]
					### generic name
					while True:
						post_pic 	= str(hashlib.md5((str(time.time())).encode('ascii', 'replace')).hexdigest())
						if not os.path.exists(pic_path):
							break

					thumb_name 		= "%s_t.jpg" % (post_pic)
					thumb_path 		= site_dir + thumb_name
					### get image
					if image:
						self.image_download(image, pic_path, thumb_path)
					else:
						self.image_upload(file, pic_path, thumb_path)
					content['thumbnail']	= site_link + thumb_name

				seo_title 		= function.seo_encode(title)
				if len(content) > 0:
					###### insert database
					format 		= "sl"
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
								"link": link,
								"note": note,
								"source": source,
								"format": format,
								"title" : title,
								"seo_title": seo_title,
								"picture" : content,
								"safekid": safekid
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

					# if insert:
					# 	return self.site.redirect('/%s/%s/%s/%s.html' % (self.site.db_site['name'],self.module['setting']['server']['view_page'], insert, seo_title))
					return {"post": "OK"}