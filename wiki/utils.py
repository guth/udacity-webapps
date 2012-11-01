import cgi
import hmac
import hashlib
import random
import string

SECRET = "hunter2"
def hash_str(val):
	return hmac.new(SECRET, str(val)).hexdigest()

# makes a cookie in the form "val|HASH"
def make_secure_val(val):
	return str("%s|%s" % (str(val), hash_str(val)))

# h is in the form "val|HASH"
# Returns the cookie value if it's valid, otherwise returns None
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

def escape_html(s):
	return cgi.escape(s, quote=True)

def validUsername(s):
	for c in s:
		if c == ' ':
			return False
	return True

def validPassword(p):
	return p is not None and len(p) > 0

def validEmail(e):
	for c in e:
		if c == '@':
			return True
	return False

def hasSpace(s):
	for c in s:
		if c == ' ':
			return True