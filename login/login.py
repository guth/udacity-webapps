import webapp2
import cgi

def escape_html(s):
	return cgi.escape(s, quote=True)

def validUsername(s):
	for c in s:
		if c == ' ':
			return False
	return True

def validPassword(p):
	return p != '' and p != 'aa'

def areSame(p, pv):
	return p == pv

def validEmail(e):
	if e == '':
		return True
	for c in e:
		if c == '@':
			return True
	return False

form="""
<h2>Signup</h2>

<form method="post">
	<label>
		Username
		<input type="text" name="username" value="%(username)s"/>
		<span style="color: red;">%(uError)s</span>
	</label>
	<br/>
	<label>
		Password
		<input type="password" name="password" value="%(password)s"/>
		<span style="color: red;">%(pError)s</span>
	</label>
	<br/>
	<label>
		Verify Password
		<input type="password" name="verifyPassword" value="%(verifyPassword)s"/>
		<span style="color: red;">%(pvError)s</span>
	</label>
	<br/>
	<label>
		Email (optional)
		<input type="text" name="email" value="%(email)s"/>
		<span style="color: red;">%(eError)s</span>
	</label>
	<br/>
	<input type="submit" />
</form>
"""


class MainPage(webapp2.RequestHandler):

	def write_form(self, args):
		self.response.write(form % args)

	def getArgs(self):
		args = {}
		args["username"] = self.request.get("username")
		args["password"] = self.request.get("password")
		args["verifyPassword"] = self.request.get("verifyPassword")
		args["email"] = self.request.get("email")
		args["uError"] = ""
		args["pError"] = ""
		args["pvError"] = ""
		args["eError"] = ""
		return args

	def getErrors(self):
		errors = {}
		errors["uError"] = "Not a valid username."
		errors["pError"] = "Not a valid password."
		errors["pvError"] = "Your passwords didn't match."
		errors["eError"] = "Not a valid email."
		return errors

	def get(self):
		args = self.getArgs()
		self.write_form(args)

	def post(self):
		args = self.getArgs()
		errors = self.getErrors()
		success = True

		if not validUsername(args["username"]):
			success = False
			args["uError"] = errors["uError"]
		if not validPassword(args["password"]):
			success = False
			args["pError"] = errors["pError"]
		if not areSame(args["password"], args["verifyPassword"]):
			success = False
			args["pvError"] = errors["pvError"]
		if not validEmail(args["email"]):
			success = False
			args["eError"] = errors["eError"]

		if success:
			url = "/welcome?username=%s" % args["username"]
			self.redirect(url)
		else:
			self.write_form(args)

class WelcomeHandler(webapp2.RequestHandler):
	def get(self):
		username = self.request.get("username")
		form = "<h2>Welcome, %s!</h2>" % username
		self.response.write(form)

app = webapp2.WSGIApplication([ ('/', MainPage),
								('/welcome', WelcomeHandler) ],
								debug=True)