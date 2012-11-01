from google.appengine.ext import db

class User(db.Model):
	username = db.StringProperty(required = True)
	password_hash = db.StringProperty(required = True)
	salt = db.StringProperty(required = True)
	email = db.StringProperty()
	created = db.DateTimeProperty(auto_now_add = True)

	@staticmethod
	def by_id(user_id):
		return User.get_by_id(int(user_id))

	@staticmethod
	def by_name(username):
		u = User.all().filter("username =", username).get()
		return u

	@staticmethod
	def user_already_exists(username):
		u = User.by_name(username)
		return u is not None

	def get_username(self):
		return username