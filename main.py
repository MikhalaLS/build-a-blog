import os
import webapp2
import jinja2

from google.appengine.ext import db

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = False)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        self.redirect("/blog")


class PostPage(Handler):
    def render_front(self,title="", post="", error=""):
        self.render("post.html", title = title, post = post, error = error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            a = Post(title = title, post = post)
            a.put()
            idnum = a.key().id()

            self.redirect("/blog/"+str(idnum))
        else:
            error = "we need both a title and some text!"
            self.render_front(title, post, error)


class ReadPage(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        commode = posts.get()
        self.render("read.html", posts = posts)

class ViewPostHandler(Handler):
    def get(self, id):
        ip = Post.get_by_id(int(id))
        self.render("permalink.html", ip = ip)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', ReadPage),
    ('/newpost', PostPage),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
