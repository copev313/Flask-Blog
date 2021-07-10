import secrets
import os
from PIL import Image
from flask import flash, redirect, render_template, request, url_for
from flaskblog import app, bcrypt, db
from flaskblog.forms import (
    LoginForm,
    RegistrationForm,
    UpdateAccountForm,
)
from flaskblog.models import Post, User
from flask_login import (
    login_user,
    current_user,
    login_required,
    logout_user,
)

# Sample post data:
posts = [
    {
        'author': 'Evan Cope',
        'title': 'Post One Title',
        'content': "First post's content . . .",
        'date_posted': 'April 1, 2020',
    }, 
    {
        'author': 'Evan Cope',
        'title': 'Post Two Title',
        'content': "Second post's content . . .",
        'date_posted': 'April 2, 2020',
    },
]


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # User is already logged in:
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash(f"Your account has been created. You are now able to login",
              'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # User is already logged in:
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login unsuccessful. Please check email and password.",
                  'danger')

    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# Helper function for resizing & saving a profile image:
def save_picture(form_picture):
    # Generate random hex to prevent duplicate images:
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,
                                'static/profile_pics',
                                picture_fn)
    # Resize the image to 125x125 pixels:
    output_size = (125, 125)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    # Save the image:
    img.save(picture_path)

    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    # [CASE] POST request:
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f"Your account has been updated.", 'success')
        return redirect(url_for('account'))

    # [CASE] GET request:
    elif (request.method == 'GET'):
        form.username.data = current_user.username       
        form.email.data = current_user.email

    # Get users profile image:
    image_file = url_for('static',
                         filename= f"profile_pics/{current_user.image_file}")

    return render_template('account.html',
                           title='Account',
                           image_file=image_file,
                           form =form)
