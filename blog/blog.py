import jinja2
import json
import logging
import os
import time
import webapp2

from datetime import datetime, timedelta
from google.appengine.api import memcache
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), '')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

# BEGIN STEVE'S SOLUTION METHODS
def age_set(key, val):
	save_time = datetime.utcnow()
	memcache.set(key, (val, save_time))

def age_get(key):
	r = memcache.get(key)
	if r:
		val, save_time = r
		age = (datetime.utcnow() - save_time).total_seconds()
	else:
		val, age = None, 0

	return val, age

def add_post(post):
	post.put()
	get_posts(update = True)
	return str(post.key().id())

def get_posts(update = False):
	q = Post.all().order("-created").fetch(limit = 10)
	mc_key = "BLOGS"

	posts, age = age_get(mc_key)
	if update or posts is None:
		posts = list(q) # Runs the query
		age_set(mc_key, posts)

	return posts, age

# END STEVE'S SOLUTION METHODS

class Handler(webapp2.RequestHandler):
		def write(self, *a, **kw):
			self.response.out.write(*a, **kw)

		def render_str(self, template, **params):
			t = jinja_env.get_template(template)
			return t.render(params)

		def render(self, template, **kw):
			toRender = self.render_str(template, **kw)
			self.write(toRender)

class Post(db.Model):
	title = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	# When a new instance of Art is created, 'auto_now_add = True'
	# automatically sets the time to the current time,
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)

	# Used to preserve new lines when the posts is returned as HTML
	#def render(self):
		#self.render_text = self.content.replace("\n", "<br/>")
		#return render_str("blog.html", posts=self)

	def render_content(self):
		return self.content.replace("\n", "<br/>")

POSTS_KEY = "top_posts"
LAST_QUERY_KEY = "last_query"
def get_key(base_key, post_id=None):
	key = str(base_key)
	if post_id:
		key += str(post_id)
	return str(key)

def get_posts(post_id=None, update=False):
	post_key = get_key(POSTS_KEY, post_id)
	query_key = get_key(LAST_QUERY_KEY, post_id)

	posts = memcache.get(post_key)
	# The two lines below are equivalent:
	# posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
	# posts = Post.all().order("-created")
	if update or not posts:
		if not post_id:
			logging.error("DB QUERY")
			posts = Post.all().order("-created")
		else:
			logging.error("DB QUERY ID %s" % post_id)
			# Or: posts = Post.get_by_id(post_id)			
			key = db.Key.from_path("Post", int(post_id))
			post = db.get(key)
			posts = [post]	# Needs to be iterable

		memcache.set(post_key, posts)
		memcache.set(query_key, int(time.time()))

	return posts

class Blog(Handler):
	def get(self, post_id=None):
		posts = get_posts(post_id)
		query_key = get_key(LAST_QUERY_KEY, post_id)
		query_time = memcache.get(query_key)

		if not query_time:
			query_time = 0
		else:
			query_time = int(time.time()) - query_time

		if not posts:
			self.error(404)
			return

		self.render("blog.html", posts=posts, query_time=query_time)

class JsonBlog(Handler):
	def get(self, post_id=None):
		posts = get_posts(post_id)
			
		if not posts:
			self.error(404)
			return

		# Render the json!
		jsonList = []
		for p in posts:
			d = {}
			d['title'] = p.title
			d['content'] = p.content
			# time_fmt = "%c"
			# time_fmt = "%a %b %d %H:%M:%S %Y"
			d['created'] = p.created.strftime("%a %b %d %H:%M:%S %Y")
			d['last_modified'] = p.last_modified.strftime("%a %b %d %H:%M:%S %Y")
			jsonList.append(d)

		# A single post shouldn't be contained in a list
		if len(jsonList) == 1:
			jsonList = jsonList[0]
		
		# jsonToRender = json.loads(str(jsonList).replace("'", '\"'))
		jsonToRender = json.dumps(jsonList)
		self.response.headers["Content-Type"] = "application/json; charset=UTF-8"
		self.write(jsonToRender)

class NewPost(Handler):
	def get(self):
		self.render("newpost.html")

	def post(self):
		title = self.request.get("title")
		content = self.request.get("content")

		if title and content:
			newPost = Post(title=title, content=content)
			newPost.put()

			get_posts(update=True)
			get_posts(post_id=newPost.key().id(), update=True)

			self.redirect("/blog/%s" % newPost.key().id())
		else:
			error = "Title and content must not be blank"
			self.render("newpost.html", title=title, content=content, error=error)

class Flush(Handler):
	def get(self):
		success = memcache.flush_all()

		if not success:
			self.error(404)
		else:
			self.redirect("/blog")

app = webapp2.WSGIApplication([ ('/newpost', NewPost),
								# Here, the paranthesis says to pass what's inside
								# of it as a string parameter to the handler
								('/blog/([0-9]+)', Blog),
								('/blog/?', Blog),
								('/blog/([0-9]+)/?[.]json', JsonBlog),
								('/blog/?[.]json', JsonBlog),
								('/flush/?', Flush),
								], debug=True)