import jinja2
import logging
import os
import webapp2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), '')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		toRender = self.render_str(template, **kw)
		self.write(toRender)

class File(db.Model):
	uname = db.StringProperty(required = True)
	address = db.StringProperty(required = True)
	email = db.StringProperty(required = True)
	description = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	
	fileName = db.TextProperty(required = True)

class Admin(Handler):
	def get(self):
		files = File.all().order("-created")
		files = list(files)
		self.render("admin.html", files=files)

class Upload(Handler):
	def get(self):
		self.render("upload.html")

	def post(self):
		uname = self.request.get("uname")
		address = self.request.get("address")
		email = self.request.get("email")
		description = self.request.get("description")
		fileName = self.request.get("fileName")
		
		logging.error("file: %s" % dir(fileName))

		if not uname or not address or not email or not description or not fileName or not fileContents:
			self.render("upload.html",
						error="Please fill in all values and keep the description less than 50 characters")
		elif len(description)>50:
			self.render("upload.html", error="Description is too long.")
		# elif not fileName.strip().endswith(".txt"):
			# self.render("upload.html", error="File isn't a txt")
		elif len(fileContents) > 5000000:
			self.render("upload.html", error="File is too big!")
		else:
			f = File(uname=uname, address=address, email=email, description=description, fileName=fileName)
			f.put()
			self.write("Good job! File was uploaded!")

app = webapp2.WSGIApplication([ ("/upload", Upload),
								("/admin", Admin),
								],
								debug=True)