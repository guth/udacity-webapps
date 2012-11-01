import os
import webapp2
import jinja2
import urllib2
import logging
import time

from xml.dom import minidom
from google.appengine.api import memcache
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), '')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

class Handler(webapp2.RequestHandler):
		def write(self, *a, **kw):
			self.response.out.write(*a, **kw)

		def render_str(self, template, **params):
			t = jinja_env.get_template(template)
			return t.render(params)

		def render(self, template, **kw):
			toRender = self.render_str(template, **kw)
			self.write(toRender)

IP_URL = "http://api.hostip.info/?ip="
def get_coords(ip):
	#ip = "4.2.2.2"
	ip = "23.24.209.141"
	url = IP_URL + ip
	content = None
	try:
		content = urllib2.urlopen(url).read()
	except urllib2.URLError:
		return

	if content:
		lat, lon = get_coords_xml(content)
		return db.GeoPt(lat, lon)

def get_coords_xml(xml):
	d = minidom.parseString(xml)
	coords = d.getElementsByTagName("gml:coordinates")
	if coords and coords[0].childNodes[0].nodeValue:
		lon, lat = coords[0].childNodes[0].nodeValue.split(",")
		return lat, lon

GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false"
def gmaps_img(points):
	# markets = '&'.join('markers=%s,%s' % (p.lat, p.lon) for p in points)
	# return GMAPS_URL + markers
	url = GMAPS_URL
	for point in points:
		url += "&markers=%s,%s" % (point.lat, point.lon)
	return url

class Art(db.Model):
	title = db.StringProperty(required = True)
	art = db.TextProperty(required = True)
	# When a new instance of Art is created, 'auto_now_add = True'
	# automatically sets the time to the current time,
	created = db.DateTimeProperty(auto_now_add = True)
	coords = db.GeoPtProperty()

LAST_QUERY_TIME_KEY = 'last_query'
def top_arts(update=False):
	key = "top"
	arts = memcache.get(key)
	if arts is None or update:

		logging.error("DB QUERY")
		arts = db.GqlQuery("SELECT * FROM Art "
							"ORDER BY created DESC "
							"LIMIT 10")

		# Each time we iterate over arts (above), we run the query
		# Below we make it into a list, so we detatch the list from the query
		# Results of the query are cached in our new list. Efficiency!
		# Prevent the running of multiple queries
		arts = list(arts)
		memcache.set(key, arts)
		memcache.set(LAST_QUERY_TIME_KEY, int(time.time()))
	return arts

class MainPage(Handler):
	def get(self):
		# self.write(repr(get_coords(self.request.remote_addr)))
		self.render_front()

	def post(self):
		title = self.request.get("title")
		art = self.request.get("art")

		if title and art:
			a = Art(title = title, art = art)
			# coords = get_coords(self.request.remote_addr)
			# if coords:
				# a.coords = coords
			
			# Stores our new Art object in the database
			a.put()
			
			# Re-run the query and update the cache
			top_arts(True)

			self.redirect("/")
		else:
			error = "We need both a title and some artwork!"
			self.render_front(title, art, error)

	def render_front(self, title="", art="", error=""):
		arts = top_arts()
		
		# find which arts have coords
		points = [a.coords for a in arts if a.coords]
		# points = filter(None, (a.coords for a in arts))

		# if we have any arts with coords, make an image url
		img_url = None
		if points:
			img_url = gmaps_img(points)

		query_time = memcache.get(LAST_QUERY_TIME_KEY)
		if not query_time:
			query_time = 0
		else:
			query_time = int(time.time()) - query_time
		# display the image url
		self.render("front.html", title = title, art = art, error = error, arts = arts, img_url=img_url, query_time=query_time)

app = webapp2.WSGIApplication([ ('/', MainPage)], debug=True)