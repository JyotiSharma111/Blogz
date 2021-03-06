from flask import Flask, request, redirect, render_template, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Shrestha@123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'W3YnjNA&kuMJK'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(400))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')

        if user and user.password != password:
            flash("Password Incorrect", "error")
            return redirect('/login')
        
        if not user:
            flash('Username does not exist', 'error')
            return redirect('/login')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_error = False
        password_error = False
        verify_error = False
        
        if username == "":
            flash("Username cannot be blank", 'error')
            username_error = True
        if len(username) < 3:
            flash("Username must be greater than 3 characters", 'error')
            username_error = True
        
        if password == "":
            flash("Password cannot be blank", 'error')
            password_error = True
        if len(username) < 3:
            flash("Password must be greater than 3 characters", 'error')
            password_error = True

        if password != verify:
            flash("Passwords don't match", 'error')
            verify_error = True

        if not username_error and not password_error and not verify_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect("/newpost")
            else:
                flash("Username already taken", "error")
        else:
            return redirect("/signup")

    return render_template("signup.html")

@app.route('/logout')
def logout():
    del session['username']
    flash("Logged Out")
    return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users, title="Blog Users")

@app.route("/blog", methods=["GET","POST"])
def blogs():

    id_check = request.args.get("id")
    user_check = request.args.get("user")
    posts = Blog.query.all()

    if id_check is not None:
        post_id = int(request.args.get("id"))
        post = Blog.query.filter_by(id=post_id).first()
        return render_template("single-blog.html", post=post)
    if user_check is not None:
        user_id = request.args.get("user")
        posts = Blog.query.filter_by(owner_id=user_id).all()
        return render_template("SingleUser.html",posts=posts)
    else:
        posts = Blog.query.all()
        

    return render_template("singleUser.html", posts=posts, title="Blog Posts")


@app.route("/newpost", methods=['GET','POST'])
def add_blog():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == "POST":

        blog_title = request.form['blog-title']
        blog_post = request.form['blog-post']
        title_error = False
        post_error = False

        if blog_title == "":
            flash("Please enter a Blog title for your post")
            title_error = True
        if len(blog_title) > 50:
            flash("Please limit your Blog title to 50 characters")
            title_error = True
        if blog_post == "":
            flash("Please enter a Blog post before submitting")
            post_error = True
        if len(blog_post) > 500:
            flash("Please limit your Blog post to 300 characters")
            post_error = True

        if not title_error and not post_error and owner:
            new_post = Blog(blog_title,blog_post,owner)
            db.session.add(new_post)
            db.session.commit()
            post_id = (new_post.id)          
            return redirect(url_for("blogs",id=post_id))
        else:
            return redirect("/newpost")

    return render_template("add-blog.html")

if __name__ == '__main__':
    app.run()
