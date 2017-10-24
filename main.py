from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:ctown1975@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "secret key"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    new_blog = db.Column(db.String(750))
    owner_id =db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, new_blog, owner):
        self.title = title
        self.new_blog = new_blog
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
   
@app.route('/login', methods=['POST', 'GET'])
def login():
    
    username = ''
    password = ''
    verify = ''
    username_err = ''
    password_err = ''
    verify_err = ''
     
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        owner = User.query.filter_by(username=username).first()
        
        if username and owner.password == password:
            session['username'] = username
            session['password'] = password
            flash("Logged in")
            return redirect('/blog')
        else:
            flash('User password incorrect, or user does not exist', 'error')
    
    return render_template('login.html')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title_err = ""
    new_blog_err = "" 

    if request.method == 'POST':
        title = request.form['title']
        new_blog = request.form['new_blog']    
        username = session['username']
        owner = User.query.filter_by(username=username).first()
        
        if title == "" or new_blog == "":
            title_err = "Please enter a valid title"
            new_blog_err = "Please enter a valid blog entry"
            return render_template('new_post.html', title_err=title_err, new_blog_err=new_blog_err) 
        else:
            blog = Blog(title, new_blog, owner)
            db.session.add(blog)
            db.session.commit()
            return redirect('/blog?id=' + str(blog.id))     

    return render_template('new_post.html')       

@app.route('/blog', methods=['GET'])
def blog():

    user_id = request.arg.get('userid')
    blog_id = request.arg.get('id')
    blogs = Blog.query.all()
    
    if blog_id:
        blog = blog.query.filter_by(id=blog_id).first()
        return render_template('user.html')
    if user_id:
        owner_id = user_id
        post = blog.query.filter_by(owner_id=user_id).all()
        return render_template('blog_post.html', post=posts)
    

    return render_template('blog-listings.html', blogs=blogs)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        if len(username) < 3 or ' ' in username:
            username_err = 'Username not valid'
            username = ''
        
        if len(password) < 3 or " " in password:
            password_err = 'Password not valid'
            password = ''

        if not verify == password:
            verify_err = 'Password does not match'
            verify = ''   

        if not username_err and not password_err and not verify_err:
            return render_template('newpost.html', username=username)   
        
        existing_user = User.query.filter_by(username=username).first()
        
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return "<h1>Duplicate user</h1>"
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/', methods=['GET'])
def index():   
   
    users = User.query.all()
    
    return render_template('index.html', title="Blogz", users=users)
      
if __name__ == '__main__':
    app.run()

 