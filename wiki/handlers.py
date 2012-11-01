import jinja2
import logging
import os
import utils
import webapp2
from DB.user import User

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
		def write(self, *a, **kw):
			self.response.out.write(*a, **kw)

		def render_str(self, template, **params):
			t = jinja_env.get_template(template)
			return t.render(params)

		def render(self, template, **kw):
			kw['user'] = self.current_user()
			toRender = self.render_str(template, **kw)
			self.write(toRender)

		def set_cookie(self, key, val):
			secure = utils.make_secure_val(val)
			self.response.headers.add_header("Set-Cookie", "%s=%s; Path=/" % (key, secure))

		def delete_cookie(self, key):
			self.response.delete_cookie(key)
			#self.response.headers.add_header("Set-Cookie", "user_id=; Path=/")

		def get_cookie(self, key):
			return self.request.cookies.get(key)

		def logged_in(self):
			user_cookie = self.get_cookie("user_id")
			if user_cookie and utils.check_secure_val(user_cookie):
				return True

		def current_user(self):
			user_cookie = self.get_cookie("user_id")
			if user_cookie:
				user_id = utils.check_secure_val(user_cookie)
				if user_id:
					return User.by_id(user_id)