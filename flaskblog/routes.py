from flask import flash, redirect, render_template, request, url_for
from flaskblog import app, bcrypt, db
from flaskblog.forms import LoginForm, RegistrationForm
from flaskblog.models import Post, User
from flask_login import (
    login_user,
    current_user,
    login_required,
    logout_user,
)


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

        flash(f"Your account has been created. You are now able to login", 'success')
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
            flash("Login unsuccessful. Please check email and password.", 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')
