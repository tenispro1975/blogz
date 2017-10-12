from flask import Flask, request, redirect, render_template
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
    body = db.Column(db.String(250))

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.completed = True

@app.route('/')
def index():
    title= ""
    title_err= ""
    body= ""
    body_err= ""
    
   #template = jinja_env.get_template('add-post.html')
    return render_template('add-post.html', title=title, body=body, title_err=title_err, body_err=body_err)

@app.route('/newpost', methods=['POST'])
def add_post():
    title = request.form['title']
    body = request.form['body']

    title_err = ''
    body_err = ''

    if title == " ":
        title_err = 'title of blog required'

    if body == " ":
        body_err = 'body of blog required'
        
    if not title_err or body_err:
        return redirect('/blog')
        
    else:  
        #template = jinja_env.get_template('add-post.html')
        return render_template('add-post.html', title=title, body=body, title_err=title_err, body_err=body_err)
    

@app.route('/blog', methods=['POST', 'GET'])
def blog_listings():

    if request.method == 'POST':
        title_name = request.form['title']
        body_name = request.form['body']
        new_title = title(title_name)
        new_blog = body(body_name)
        db.session.add(new_blog)
        db.session.commit()
    
    title = title.query.filter_by(completed=False).all()
    new_title = title.query.filter_by(completed=True).all()
    new_blog = blog.query.filter_by(completed=True).all()
    return render_template('blog-listings.html', title=title, new_title=new_title, new_blog=new_blog)

if __name__ == '__main__':
    app.run()