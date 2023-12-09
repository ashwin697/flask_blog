from curses import flash
from flask import Flask, redirect , render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from flask_ckeditor import CKEditor
import math

passwd = "123"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:{passwd}@db/flask_app'
db = SQLAlchemy(app)
app.secret_key = 'fdgddfg^&^SDdgdhe3#tB455gdfgdf%^$#$#@#CVTRsSader'
ckeditor = CKEditor(app)

## defining the table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(15), nullable=False)

class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    user = db.Column(db.String(30), nullable=False)
    slug = db.Column(db.String(150), nullable=False)
    tagline = db.Column(db.String(350), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(15), nullable=True)
    imagefile = db.Column(db.String(35), nullable=True)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), nullable=False)
    msg = db.Column(db.String(900), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(15), nullable=True)

# creating table
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    
    posts = Post.query.filter_by().all()
    post_on_page = 4
    # print(len(posts))
    totalpage = math.ceil(len(posts) / post_on_page)
    # print("totalpage ", totalpage)
    page = int(request.args.get('page', 1))
    # print("page -", page)
    start_index = (page - 1) * post_on_page
    end_index = start_index + post_on_page
    posts_on_page = posts[start_index:end_index]
    
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page+1)  # cast page to a string
    elif page == totalpage:
        # print("last page ", totalpage)
        prev = "/?page=" + str(page-1)  # cast page to a string
        next = "#"
    else:
        prev = "/?page=" + str(page-1)  # cast page to a string
        next = "/?page=" + str(page+1)  # cast page to a string

    return render_template("home.html", post=posts_on_page, next=next, prev=prev)




@app.route("/contact", methods = ['GET','POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        desc = request.form.get('description')

        contactentry = Contact(name=name,email=email,phone=phone,subject=subject,msg=desc,date=datetime.now().strftime("%H:%M:%S"))

        db.session.add(contactentry)
        db.session.commit()


    return render_template("contact.html")





@app.route("/about")
def about():
    return render_template("about.html")





@app.route("/register", methods = ['GET','POST'])
def register():
    if(request.method=='POST'):
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        userentery = User(username=username , password=password , email=email)
        db.session.add(userentery)
        db.session.commit()

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user'] = f"{user.id}{user.username}^&%$df"
            print("session created")
            # flash('You were successfully logged in')
            return redirect(url_for('home'))
        
        return redirect(url_for("login"))
    return render_template("register.html")





@app.route("/login", methods = ['POST', 'GET'])
def login():
    if 'user' not in session:
        if(request.method=='POST'):
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session['user'] = f"{user.id}{user.username}^&%$df"
                print(session['user'])
            return redirect(url_for('home'))
        return render_template("login.html")
    else:
        return "request not valid"




@app.route("/logout")
def logout():
    session.pop('user')
    # flash('You were successfully logged out')
    return redirect(url_for('home'))



#dashboard start here
@app.route("/dashboard", methods = ['GET','POST'])
def dashboard():
    if 'user' in session:
        
        posts = Post.query.filter_by(user=session.get('user')).all()
        totalpost = len(posts)
        return render_template("dashboard.html", posts=posts, total=totalpost)
    else:
        return redirect(url_for('login'))


#addpost start here
@app.route("/addpost",methods = ['GET','POST'])
def addpost():
    if 'user' in session:
        root_path = "/home/ashwin/Documents/pythonpract/flasktest_app/static/uploads"
        if(request.method == 'POST'):
            title = request.form.get('title')
            slug = request.form.get('slug')
            tagline = request.form.get('tagline')
            content = request.form.get('ckeditor')
            imagefile = ''

            # check if a file was uploaded
            if 'image' in request.files:
                # get the uploaded file
                file = request.files['image']
                # make sure it has a valid filename
                if file.filename != '':
                    # save the file to the upload folder
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(root_path , filename))
                    imagefile = filename

            postentry = Post(title=title,tagline=tagline,imagefile=imagefile,slug=slug,content=content,date=datetime.now().strftime("%H:%M:%S"),user=session.get('user'))

            db.session.add(postentry)
            db.session.commit()
            return redirect(url_for('dashboard'))

        return render_template("addpost.html")
    else:
        return "user not valid"

#show post start here
@app.route("/post/<string:slug>", methods = ['GET'])
def postsview(slug):
    posts = Post.query.filter_by(slug=slug).first()
    return render_template("post.html",post=posts)



@app.route("/listpost", methods = ['GET'])
def listpost():
    if 'user' in session:
        posts = Post.query.filter_by(user=session.get('user')).all()
        post_on_page = 4
        # print(len(posts))
        totalpage = math.ceil(len(posts) / post_on_page)
        # print("totalpage ", totalpage)
        page = int(request.args.get('page', 1))
        # print("page -", page)
        start_index = (page - 1) * post_on_page
        end_index = start_index + post_on_page
        posts_on_page = posts[start_index:end_index]
        
        if page == 1:
            prev = "#"
            next = "/listpost?page=" + str(page+1)  # cast page to a string
        elif page == totalpage:
            # print("last page ", totalpage)
            prev = "/listpost?page=" + str(page-1)  # cast page to a string
            next = "#"
        else:
            prev = "/listpost?page=" + str(page-1)  # cast page to a string
            next = "/listpost?page=" + str(page+1)  # cast page to a string

        return render_template("viewpost.html", post=posts_on_page, next=next, prev=prev)
    else:
        return redirect(url_for('login'))
    

#show post start here
@app.route("/edit/<string:slugi>", methods = ['GET','POST'])
def edit(slugi):
    if 'user' in session :
        if request.method == "POST":
            root_path = "/home/ashwin/Documents/pythonpract/flasktest_app/static/uploads"
        if(request.method == 'POST'):
            title = request.form.get('title')
            slug = request.form.get('slug')
            tagline = request.form.get('tagline')
            content = request.form.get('ckeditor')
            imagefile = ''

            # check if a file was uploaded
            if 'image' in request.files:
                # get the uploaded file
                file = request.files['image']
                # make sure it has a valid filename
                if file.filename != '':
                    # save the file to the upload folder
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(root_path , filename))
                    imagefile = filename

            
            post = Post.query.filter_by(slug=slugi,user=session.get('user')).first()

            post.title = title
            post.slug = slug
            post.content = content
            post.tagline = tagline
            post.imagefile = imagefile
            db.session.add(post)
            db.session.commit()
            redirect(url_for('edit', slugi=post.slug))
        post = Post.query.filter_by(slug=slugi,user=session.get('user')).first()
        return render_template("editpost.html",post=post)
    else:
        return redirect(url_for('login'))
    
@app.route("/editpage", methods = ['GET','POST'])
def editpage():
    if 'user' in session :
        post = Post.query.filter_by(user=session.get('user')).all()
        post_on_page = 4
        # print(len(posts))
        totalpage = math.ceil(len(post) / post_on_page)
        # print("totalpage ", totalpage)
        page = int(request.args.get('page', 1))
        # print("page -", page)
        start_index = (page - 1) * post_on_page
        end_index = start_index + post_on_page
        posts_on_page = post[start_index:end_index]
        
        if page == 1:
            prev = "#"
            next = "/editpage?page=" + str(page+1)  # cast page to a string
        elif page == totalpage:
            # print("last page ", totalpage)
            prev = "/editpage?page=" + str(page-1)  # cast page to a string
            next = "#"
        else:
            prev = "/editpage?page=" + str(page-1)  # cast page to a string
            next = "/editpage?page=" + str(page+1)  # cast page to a string

        return render_template('editpage.html', post=posts_on_page, next=next, prev=prev)
        
    else:
        return redirect(url_for('login'))
    






@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if ('user' in session):
        post = Post.query.filter_by(sno=sno,user=session.get('user')).first()
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('editpage'))
    else:
        return redirect(url_for('login'))



app.run(debug=True)

