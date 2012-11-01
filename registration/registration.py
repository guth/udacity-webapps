import os
import webapp2
import jinja2
import hmac
import hashlib
import random
import string

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), '')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def hasSpace(s):
	for c in s:
		if c == ' ':
			return True
	return False

def validEmail(e):
	if e == '':
		return True
	for c in e:
		if c == '@':
			return True
	return False

def user_already_exists(username):
	user = User.by_name(username)
	if user:
		return True

SECRET = "hunter2"
def hash_str(val):
	return hmac.new(SECRET, str(val)).hexdigest()

# makes a cookie in the form "val|HASH"
def make_secure_val(s):
	return str("%s|%s" % (str(s), hash_str(s)))

# h is in the form "val|HASH"
def check_secure_val(h):
	if not h:
		return None
	val = h.split("|")[0]
	if h == make_secure_val(val):
		return val

SALT_LENGTH = 25
def make_salt():
	return ''.join([random.choice(string.letters) for x in xrange(SALT_LENGTH)])

def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt = make_salt()
	password_hash = hashlib.sha256(name+pw+salt).hexdigest()
	return password_hash

def valid_pw(name, pw, salt, h):
	return h == make_pw_hash(name, pw, salt)

class Handler(webapp2.RequestHandler):
		def write(self, *a, **kw):
			self.response.out.write(*a, **kw)

		def render_str(self, template, **params):
			t = jinja_env.get_template(template)
			return t.render(params)

		def render(self, template, **kw):
			toRender = self.render_str(template, **kw)
			self.write(toRender)

		def logged_in(self):
			user_id_cookie_str = self.request.cookies.get("user_id")
			user_id = check_secure_val(user_id_cookie_str)
			if user_id:
				return True

		def username_from_cookie(self):
			user_id_cookie_str = self.request.cookies.get("user_id")
			user_id = check_secure_val(user_id_cookie_str)
			if not user_id:
				return None
			user = User.by_id(int(user_id))
			return user.username

class User(db.Model):
	username = db.StringProperty(required = True)
	password_hash = db.StringProperty(required = True)
	salt = db.StringProperty(required = True)
	email = db.StringProperty()
	created = db.DateTimeProperty(auto_now_add = True)

	@staticmethod
	def by_id(user_id):
		return User.get_by_id(user_id)

	@staticmethod
	def by_name(username):
		u = User.all().filter("username =", username).get()
		return u

class Welcome(Handler):
	def get(self):
		if not self.logged_in():
			self.response.headers.add_header("Set-Cookie", "user_id=; Path=/")
			self.redirect('/signup')

		username = self.username_from_cookie()
		self.render("welcome.html", username=username)

class Login(Handler):
	def get(self):
		if self.logged_in():
			self.redirect("/welcome")
		self.render("login.html")
	
	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")

		if not username or not password or hasSpace(username) or hasSpace(password):
			self.render("login.html", username=username, password=password, loginError="Invalid login 1.")
		else:
			user = User.by_name(username)
			if not user: # user doesn't exist
				self.render("login.html", username=username, password=password, loginError="Invalid login 2. (User doesn't exist)")
			elif not valid_pw(username, password, user.salt, user.password_hash):
				self.render("login.html", username=username, password=password, loginError="Invalid login 3. (Invalid password)")
			else:
				# Login successful
				user_id_cookie = make_secure_val(user.key().id())
				self.response.headers.add_header("Set-Cookie", "user_id=%s; Path=/" % user_id_cookie)
				self.redirect("/welcome")

class Signup(Handler):
	def get(self):
		if self.logged_in():
			self.redirect("/welcome")
		self.render("signup.html")

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		verifyPassword = self.request.get("verifyPassword")
		email = self.request.get("email")

		errors = {}
		errorKeys = ["uError", "pError", "pvError", "eError"]
		for errorKey in errorKeys:
			errors[errorKey] = ""

		success = True
		if not username or hasSpace(username):
			errors["uError"] = "Enter a valid username."
			success = False
		if not password or hasSpace(password):
			errors["pError"] = "Enter a valid password."
			success = False
		if not verifyPassword or password != verifyPassword:
			errors["pvError"] = "Passwords must match."
			success = False
		if email and not validEmail(email):
			errors["eError"] = "Invalid email."
			success = False
		if user_already_exists(username):
			errors["uError"] = "User already exists."
			success = False

		if success:
			salt = make_salt()
			password_hash = make_pw_hash(username, password, salt)
			user = User(username=username, password_hash=password_hash,salt=salt,email=email)
			user.put()

			user_id_cookie = make_secure_val(user.key().id())
			self.response.headers.add_header("Set-Cookie", "user_id=%s; Path=/" % user_id_cookie)
			self.redirect("/welcome")
		else:
			self.render("signup.html", username=username, password=password, verifyPassword=verifyPassword, email=email,
										**errors)

class Logout(Handler):
	def get(self):
		self.response.delete_cookie("user_id")
		#self.response.headers.add_header("Set-Cookie", "user_id=; Path=/")
		self.redirect("/signup")

app = webapp2.WSGIApplication([ ('/signup', Signup),
								('/welcome', Welcome),
								('/login', Login),
								('/logout', Logout),
								], debug=True)