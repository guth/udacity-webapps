from google.appengine.ext import db

class Article(db.Model):
	name = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	createdById = db.IntegerProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

	@staticmethod
	def by_id(article_id):
		return Article.get_by_id(int(article_id))

	@staticmethod
	def all_by_name(name):
		a = Article.all().filter("name =", name).order("-created")
		a = list(a)
		return a

	@staticmethod
	def most_recent_by_name(name):
		a = Article.all().filter("name =", name).order("-created").get()
		return a

	@staticmethod
	def article_exists(name):
		a = Article.most_recent_by_name(name)
		return a is not None

	# def get_edit_link(self):
	# 	return ('<a href="/edit%s">edit</a>' % self.name)

	# def get_edit_version_link(self):
	# 	return ('<a href="/edit%s?v=%s">edit</a>' % (self.name, str(self.key().id())))

	# def get_view_link(self):
	# 	return ('<a href="%s">view</a>' % self.name)

	# def get_view_version_link(self):
	# 	return ('<a href="%s?v=%s">view</a>' % (self.name, str(self.key().id())))

	# def get_history_link(self):
	# 	return ('<a href="/history%s">history</a>' % self.name)
	
	# def get_history_version_link(self):
	# 	return ('<a href="/history%s?v=%s">history</a>' % (self.name, str(self.key().id())))