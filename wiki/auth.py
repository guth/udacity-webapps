from handlers import Handler
from DB.user import User
from utils import hasSpace, make_salt, make_pw_hash, valid_pw, validEmail

class Login(Handler):
	def get(self):
		if self.logged_in():
			self.redirect("/main")
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
				self.set_cookie("user_id", user.key().id())
				self.redirect("/")

class Logout(Handler):
	def get(self):
		self.delete_cookie("user_id")
		self.redirect("/login")

class Signup(Handler):
	def get(self):
		if self.logged_in():
			self.redirect("/")
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
		if User.user_already_exists(username):
			errors["uError"] = "User already exists."
			success = False

		if success:
			salt = make_salt()
			password_hash = make_pw_hash(username, password, salt)
			user = User(username=username, password_hash=password_hash, salt=salt, email=email)
			user.put()

			self.set_cookie("user_id", user.key().id())
			self.redirect("/")
		else:
			self.render("signup.html", username=username, password=password, verifyPassword=verifyPassword, email=email,
										**errors)