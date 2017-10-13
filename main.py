from flask import Flask, request, redirect, render_template, sessions, flash
from flask_sqlalchemy import SQLAlchemy
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build_a_blog:tenispro@localhost:8889/build_a_blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    new_blog = db.Column(db.String(750))
    completed = db.Column(db.Boolean)
    
    def __init__(self, title, new_post):
        self.title = title
        self.new_blog = new_blog
        self.completed = False

@app.route('/')
def index():
    blogs = Blog.query.all()
    #template = jinja_env.get_template('add-post.html')
    return render_template('blog-listings.html', blogs=blogs) #title=title, new_blog=new_blog, title_err=title_err, new_blog_err=new_blog-Err)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title_err = ""
    new_blog_err = "" 

    if request.method == 'POST':
        title = request.form['title']
        new_blog = request.form['new_blog']    
        
        if title == "" or new_blog == "":
            title_err = "Please eneter a valid title"
            new_blog_err = "Please enter a valid blog entry"
            return render_template('/newpost', title_err=title_err, new_blog_err=new_blog_err) 
        else:
            blog = Blog(title, new_blog)
            db.session.add(blog)
            db.session.commit()
            return redirect('/blog?id=' + str(blog.id))     

    return render_template('add-post.html')       

@app.route('/blog', methods=['GET'])
def blog_listings():

    if request.args:
        id = request.args.get("id")
        blog = Blog.query.get(id)
        return render_template('blog-post.html', blog=blog)
    else:
        blogs = Blog.query.all()
        
        return render_template('blog-listings.html', blogs=blogs)

if __name__ == '__main__':
    app.run()