from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase

config = {
    "apiKey": "AIzaSyCCnt5xrueFHh-XyLPWyP6XUZRkpi8tGco",
    "authDomain": "personalproj-ba3c3.firebaseapp.com",
    "projectId": "personalproj-ba3c3",
    "storageBucket": "personalproj-ba3c3.appspot.com",
    "messagingSenderId": "442365273351",
    "appId": "1:442365273351:web:ade388b566ce5b2ebb91a2",
    "databaseURL": "https://personalproj-ba3c3-default-rtdb.europe-west1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'

#Code goes below here

@app.route('/', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        fullname = request.form['full_name']
        username = request.form['username']
        bio = request.form['bio']
        pfp = request.form['profile_pic']
    try:
        login_session['user'] = auth.create_user_with_email_and_password(email, password)
        UID = login_session['user']['localId']
        user = {"name": fullname, "email": email, "username" : username, "bio" : bio, "pfp" : pfp}
        db.child("Users").child(UID).set(user)
        return redirect(url_for('home'))
    except:
        error = "Authentication failed"
        return render_template("signup.html")

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
    try:
        login_session['user'] = auth.sign_in_with_email_and_password(email, password)
        return redirect(url_for('home'))
    except:
        error = "Authentication failed"
        return render_template("signin.html")

@app.route('/home', methods=['GET', 'POST'])
def home():
    pdict = db.child("Posts").get().val()
    pos = []
    post_list = []
    for i in pdict:
        pos.append(pdict[i])
    for x in range(len(pos)):
        post_list.append(pos[x])
    return render_template("home.html", post_list = post_list)

@app.route('/profile', methods=['GET', 'POST'])
def myprofile():
    UID = login_session['user']['localId']
    profile = db.child("Users").child(UID).get().val()
    posts = db.child("Posts").get().val()
    user_posts = []
    for i in posts:
        post_dict = db.child("Posts").child(i).get().val()
        if post_dict['uid'] == login_session['user']['localId']:
            user_posts.append(posts[i])
    return render_template("profile.html", user_profile = profile, user_posts = user_posts)

@app.route('/delete', methods=['GET', 'POST'])
def delete_account():
    try:
        UID = login_session['user']['localId']
        db.child("Users").child(UID).remove()
        return redirect(url_for('signup'))
    except:
        error = "Couldn’t remove object"

@app.route('/signout', methods=['GET', 'POST'])
def signout():
    login_session['user'] = None
    auth.current_user = None
    return redirect(url_for('signup'))

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        pic = request.form['picture']
        desc = request.form['picture_desc']
        try:
            UID = login_session['user']['localId']
            post = {"postpic": pic, "postdesc": desc, "uid" : UID}
            db.child("Posts").push(post)
            return redirect(url_for('profile'))
        except:
            error = "Authentication failed"
            return render_template("add_post.html")
    return render_template("add_post.html")



#Code goes above here

if __name__ == '__main__':
    app.run(debug=True)