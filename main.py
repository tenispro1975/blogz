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
    allowed_routes = ['index', 'signup', 'blog', 'login']
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
        
        if username == username and password == password:
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
        
        if title == "": 
            title_err = "Please enter a valid title"
        elif new_blog == "": 
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
    
    user_id = request.args.get('user_id')
    blog_id = request.args.get('id')
    blog = Blog.query.all()

    if blog_id:
        
        blog = Blog.query.get(blog_id)
        return render_template('blog_post.html', blog=blog)
    elif user_id:
        user = User.query.get(user_id)
        blogs = Blog.query.filter_by(owner=user).all()
        return render_template('user.html', blogs=blogs)
    
    else:
        blogs = Blog.query.all()
        return render_template('blog-listings.html', blogs=blogs)

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_err = ''   
        password_err = ''
        verify_err = ''
        
        existing_user = User.query.filter_by(username=username).first()

        if len(username) < 3 or ' ' in username:
            username_err = 'Username not valid'
            #username = ''
        
        if len(password) < 3 or " " in password:
            password_err = 'Password not valid'
            #password = ''

        if not verify == password:
            verify_err = 'Password does not match'
            verify = ''   

        if username_err or password_err or verify_err:
            return render_template('signup.html', username_err=username_err, password_err=password_err, verify_err=verify_err)   
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            username_err = 'Username already exists'
            return render_template('signup.html', username_err=username_err, password_err=password_err, verify_err=verify_err)
            
        else:  
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
        return redirect('/newpost')
        
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/', methods=['GET'])
def index():   
   
    users = User.query.all()
    
    return render_template('index.html', title="Blogz", users=users)
      
if __name__ == '__main__':
    app.run()

 