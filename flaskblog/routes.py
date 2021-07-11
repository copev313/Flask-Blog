import secrets
import os
from PIL import Image
from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
    abort
)
from flaskblog import app, bcrypt, db, mail
from flaskblog.forms import (
    LoginForm,
    RegistrationForm,
    UpdateAccountForm,
    PostForm,
    RequestResetForm,
    ResetPasswordForm,
)
from flaskblog.models import Post, User
from flask_login import (
    login_user,
    current_user,
    login_required,
    logout_user,
)
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query\
                .order_by(Post.date_posted.desc())\
                .paginate(page=page, per_page=5)
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
        return redirect(url_for('login'))

    # [CASE] GET request:
    return render_template('register.html',
                            title='Register',
                            form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # User is already logged in:
    if current_user.is_authenticated:
        return redirect(url_for('home'))

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
                    return redirect(url_for('home'))

            # [CASE] Invalid email or password:
            else:
                flash("Login unsuccessful. Please check email and password.",
                      'danger')

    # [CASE] GET request:
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


# Create a new post:
@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    # [CASE] POST request:
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    content=form.content.data,
                    author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Post has been created.", 'success')
        return redirect(url_for('home'))

    # [CASE] GET request:
    return render_template('create_post.html',
                           title='New Post',
                           form=form)


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html',
                           title=post.title,
                           post=post)


# Update an existing post:
@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    # [VALIDATION] Only the post's author can update the post:
    if (post.author != current_user):       
        abort(403)

    form = PostForm()
    # [CASE] POST request:
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated.", 'info')
        return redirect(url_for('post', post_id=post.id))

    # [CASE] GET request:
    elif (request.method == 'GET'):
        form.title.data = post.title
        form.content.data = post.content
        return render_template('create_post.html',
                               title='Update Post',
                               form=form)


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    # [VALIDATION] Only the post's author can delete the post:
    if (post.author != current_user):       
        abort(403)
    
    # Delete the post:
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted.", 'secondary')
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
                .order_by(Post.date_posted.desc())\
                .paginate(page=page, per_page=5)

    return render_template('user_posts.html',
                           posts=posts,
                           user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''Hello {user.username},

To reset your password, visit the following link: 
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.

Thank you,

    The Flask-Blog App
'''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    # User is already logged in:
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RequestResetForm()
    # [CASE] POST request:
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.',
              'warning')
        return redirect(url_for('login'))
    
    # [CASE] GET request:
    return render_template('reset_request.html',
                           title='Reset Password',
                           form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    # User is already logged in:
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    user = User.verify_reset_token(token)
    if user is None:       
        flash('That is an invalid or expired token.', 'warning')       
        return redirect(url_for('reset_request'))

    form = ResetPasswordForm()
    # [CASE] POST request:
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)\
                                .decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Your password has be updated. You are now able to login.",
              'success')
        return redirect(url_for('login'))

    # [CASE] GET request:
    return render_template('reset_token.html',
                           title='Reset Password',
                           form=form)