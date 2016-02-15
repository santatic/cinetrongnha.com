from tornado import web, auth, escape

class LoginOAuthFacebook(auth.FacebookGraphMixin):
	_OAUTH_ACCESS_TOKEN_URL = "https://graph.facebook.com/v2.1/oauth/access_token?"
	_OAUTH_AUTHORIZE_URL = "https://www.facebook.com/v2.1/dialog/oauth?"
	_FACEBOOK_BASE_URL = "https://graph.facebook.com/v2.1"


	# https://graph.facebook.com/v2.1/783161408416348/posts 	--- read_stream
	# https://graph.facebook.com/v2.1/783161408416348/feed
	# https://developers.facebook.com/docs/graph-api/reference/v2.1/user/apprequests
	# http://api-portal.anypoint.mulesoft.com/facebook/api/facebook-graph-api/docs/reference/realtime-updates
	# https://graph.facebook.com/v2.1/100001734918068?fields=context.fields(mutual_friends.limit(500).after(NTYzODc0OTIwMzkyMDQ0))
	def __init__(self, user=None):
		self.user 	= user

	@gen.coroutine
	def init(self):
		if not self.user:
			self.user = yield self.session.get(['email'])

		if self.user and 'facebook' in self.user:
			self.facebook = self.user['facebook']
			if 'access_token' in self.facebook:
				return True
		
		return False

	# user nottify
	@gen.coroutine
	def set_notify(self, msg, link):
		result = yield self.facebook_request(
			"/me/notifications",
			post_args = '',
			access_token = self.user["access_token"],
			template = msg,
			href = link
		)
		print('notify', result)

	# user feed
	@gen.coroutine
	def get_feed(self, locale='vi_VN'):
		# https://developers.facebook.com/docs/graph-api/reference/v2.1/user/feed
		# /{user-id}/links shows only the links that were published by this person.
		# /{user-id}/posts shows only the posts that were published by this person.
		# /{user-id}/statuses shows only the status update posts that were published by this person.
		# /{user-id}/tagged shows only the posts that this person was tagged in.

		# if 'locale' in self.facebook:
		# 	locale = self.facebook['locale']
		result = yield self.facebook_request(
			"me/feed",
			access_token = self.user["access_token"],
			post_args = 'message'
		)
		print('feed', result)
	
	@gen.coroutine
	def set_feed(self, msg):
		# permission : publish_actions
		result = yield self.facebook_request(
			"me/feed",
			post_args= {"message": msg}
			access_token = self.user["access_token"],
		)
		print('feed', result)

	# get friend
	@gen.coroutine
	def get_friends(self):
		result = yield self.facebook_request(
			"/me",
			access_token = self.user["access_token"],
			fields = 'context.fields(mutual_friends.limit(5000))'
		)
		print('friends', result)

		if 'context' in result and 'mutual_friends' in result['context']:
			result = result['context']['mutual_friends']

		while 'paging' in result and 'cursors' in result['paging'] and 'after' in result['paging']['cursors']:
			result = yield self.facebook_request(
				"/me",
				access_token = self.user["access_token"],
				fields = 'context.fields(mutual_friends.limit(5000).after(%s))' % result['paging']['cursors']['after']
			)
			# param = result['paging']['next'].split('?',1)[1].split('&')
			# data = {}
			# for p in param:
			# 	p = p.split('=')
			# 	data[p[0]] = p[1]
			# result = yield self.facebook_request(
			# 	"/me/friends",
			# 	**data
			# )
			# print('friends', result)
			if 'context' in result and 'mutual_friends' in result['context']:
				result = result['context']['mutual_friends']