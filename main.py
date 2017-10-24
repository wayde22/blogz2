from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True      
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'beproductive'
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
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


@app.before_request   #Runs everytime a request is made before it goes on.
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']  #Is a whitelist of pages that someone can see without being logged in.
    if request.endpoint not in allowed_routes and 'username' not in session: # The endpoint is the paths in the allowed route variables.
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()  #Returns a username if the user exist, if not it return none.
        if user and user.password == password:  #Compared the password if the user exist.
            session['username'] = username  #This session object is how the site remembers that someone is logged in. 
            flash("Logged in")
            return redirect('/')
        else:
            flash("User password incorrect, or user does not exist", "error")
            return render_template('login.html')

    else:
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #TODO - validate user's data
        if verify == "" or verify != password:
            flash("The passwords do not match!")
            return render_template('signup.html')

        existing_user = User.query.filter_by(username=username).first()  #Returns a username if the user exist, if not it return NONE.
        if not existing_user:  #If the user does not exist in the database the run the following code.
            new_user = User(username, password)  #Adds the object for the user.
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username  #This session object is how the site remembers that someone is logged in.
            return redirect('/')
        else:
            #TODO = user better response messaging
            return "<h1 class='error'>Duplicate user</h1>"

    return render_template('signup.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/blog', methods=['GET', 'POST'])
def blog():
    
    if request.args:
        blog_id = request.args.get('id')
        user_id = request.args.get('user')
        users = ''
        blogs = ''
                
        if blog_id:
            blogs = Blog.query.get(blog_id)
            return render_template('post.html', blogs=blogs)
        if user_id:
            user = User.query.get(user_id)
            blogs = Blog.query.filter_by(owner=user).all()
            return render_template('user.html', blogs=blogs)
        
    else:
        blogs = Blog.query.all()
       
        return render_template('blog.html', blogs=blogs)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():       
    
    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ""
        body_error = ""

        if len(blog_title) == 0:
            title_error = "No title entered"

        if len(blog_body) == 0:
            body_error = "No information entered"

        if not title_error and not body_error:
            updated_blog = Blog(blog_title, blog_body, owner) #Packages the blog title and body up.
            db.session.add(updated_blog) #Adds the data from the form.
            db.session.commit() #Commits the data from the form.
            query_string = "/blog?id=" + str(updated_blog.id) #Adds the path with a appropriated form data to the appropriated id.
            return redirect(query_string) #Redirects to blog with the added path.
            
        else:
            return render_template('newpost.html', title_error=title_error,body_error=body_error)
    
    else:
         return render_template('newpost.html')




@app.route('/logout')
def logout():
    del session['username']  #Remove the user from the session.
    return redirect('/')


if __name__ == '__main__':
    app.run()