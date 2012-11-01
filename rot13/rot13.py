import webapp2
import cgi

def escape_html(s):
	return cgi.escape(s, quote=True)

def rot13(s):
	out = []
	for c in s:
		if c >= 'a' and c <= 'z':
			i = ord(c)+13
			if i > ord('z'):
				i = i - 26
			out.append(chr(i))
		elif c >= "A" and c <= "Z":
			i = ord(c)+13
			if i > ord('Z'):
				i = i - 26
			out.append(chr(i))
		else:
			out.append(c)
	return "".join(out)

form="""
<h2>Enter some text to ROT13:</h2>

<form method="post">
	<textarea name="text" style="height: 100px; width: 300px;">%(text)s</textarea>
	<br />
	<input type="submit" />
</form>
"""

class MainPage(webapp2.RequestHandler):

	def write_form(self,text=""):
		self.response.write(form % {"text": escape_html(text)})

	def get(self):
		self.write_form()

	def post(self):
		text = self.request.get("text")
		text = rot13(text)
		self.write_form(text)
		
app = webapp2.WSGIApplication([ ('/', MainPage)], debug=True)