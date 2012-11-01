import logging
import webapp2
from handlers import Handler
from auth import Login, Logout, Signup
from DB.article import Article

class Main(Handler):
	def get(self):
		self.write("Main!")
		self.write("<br/>")
		self.write(PAGE_RE)

class EditPage(Handler):
	def get(self, name):
		if not self.logged_in():
			self.redirect("/login")

		article_id = self.request.get("v")
		article = None
		if article_id:
			article = Article.by_id(article_id)
		else:
			article = Article.most_recent_by_name(name)
		
		self.render("edit.html", article=article)

	def post(self, name):
		user = self.current_user()
		content = self.request.get("content")
		article = Article(name=name, content=content, createdById = user.key().id())
		article.put()
		self.redirect(name)

class HistoryPage(Handler):
	def get(self, name):
		article = Article.most_recent_by_name(name)
		articles = Article.all_by_name(name)
		if not articles:
			self.redirect("/edit" + name)
		self.render("history.html", article=article, articles=articles)

class WikiPage(Handler):
	def get(self, name):
		if not Article.article_exists(name):
			if not self.logged_in():
				self.redirect("/login")
			else:
				self.redirect("/edit" + name)

		article_id = self.request.get("v")
		article = None
		if article_id:
			article = Article.by_id(article_id)
		else:
			article = Article.most_recent_by_name(name)
		
		self.render("wiki.html", article=article)


PAGE_RE = r"(/(?:[a-zA-Z0-9_-]+/?)*)"
app = webapp2.WSGIApplication([ ("/signup", Signup),
								("/login", Login),
								("/logout", Logout),
								("/main", Main),
								("/edit" + PAGE_RE, EditPage),
								("/history" + PAGE_RE, HistoryPage),
								(PAGE_RE, WikiPage),
								],
								debug=True)