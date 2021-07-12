from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.posts.forms import PostForm
from flaskblog.models import Post


posts = Blueprint('posts', __name__)


# Create a new post:
@posts.route('/post/new', methods=['GET', 'POST'])
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
        return redirect(url_for('main.home'))

    # [CASE] GET request:
    return render_template('create_post.html',
                           title='New Post',
                           form=form)


@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html',
                           title=post.title,
                           post=post)


# Update an existing post:
@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
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
        return redirect(url_for('posts.post', post_id=post.id))

    # [CASE] GET request:
    elif (request.method == 'GET'):
        form.title.data = post.title
        form.content.data = post.content
        return render_template('create_post.html',
                               title='Update Post',
                               form=form)


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
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
    return redirect(url_for('main.home'))
