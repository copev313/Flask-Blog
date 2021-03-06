from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_required, login_user, logout_user
from flaskblog import bcrypt, db
from flaskblog.users.forms import (LoginForm, RegistrationForm, RequestResetForm,
                             ResetPasswordForm, UpdateAccountForm)
from flaskblog.models import Post, User
from flaskblog.users.utils import save_picture, send_reset_email


users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    # User is already logged in:
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    # [CASE] POST request:
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)\
                                .decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created. You are now able to login",
              'success')
        return redirect(url_for('users.login'))

    # [CASE] GET request:
    return render_template('users/register.html',
                            title='Register',
                            form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    # User is already logged in:
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    # [CASE] POST request:
    if (request.method == 'POST'):
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()

            # [CASE] Valid user exists & password is correct:
            if user and bcrypt.check_password_hash(
                user.password, form.password.data
            ):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('main.home'))

            # [CASE] Invalid email or password:
            else:
                flash("Login unsuccessful. Please check email and password.",
                      'danger')

    # [CASE] GET request:
    return render_template('users/login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
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
        return redirect(url_for('users.account'))

    # [CASE] GET request:
    elif (request.method == 'GET'):
        form.username.data = current_user.username       
        form.email.data = current_user.email

    # Get users profile image:
    image_file = url_for('static',
                         filename= f"profile_pics/{current_user.image_file}")

    return render_template('users/account.html',
                           title='Account',
                           image_file=image_file,
                           form =form)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
                .order_by(Post.date_posted.desc())\
                .paginate(page=page,
                          per_page=current_app.config['POSTS_PER_PAGE'])

    return render_template('users/user_posts.html',
                           posts=posts,
                           user=user)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    # User is already logged in:
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RequestResetForm()
    # [CASE] POST request:
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.',
              'warning')
        return redirect(url_for('users.login'))
    
    # [CASE] GET request:
    return render_template('users/reset_request.html',
                           title='Reset Password',
                           form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    # User is already logged in:
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    user = User.verify_reset_token(token)
    if user is None:       
        flash('That is an invalid or expired token.', 'danger')       
        return redirect(url_for('users.reset_request'))

    form = ResetPasswordForm()
    # [CASE] POST request:
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)\
                                .decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Your password has be updated. You are now able to login.",
              'success')
        return redirect(url_for('users.login'))

    # [CASE] GET request:
    return render_template('users/reset_token.html',
                           title='Reset Password',
                           form=form)
