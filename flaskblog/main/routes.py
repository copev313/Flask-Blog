from flask import Blueprint, current_app, render_template, request
from flaskblog.models import Post


main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query\
                .order_by(Post.date_posted.desc())\
                .paginate(page=page,
                          per_page=current_app.config['POSTS_PER_PAGE'])
    return render_template('main/home.html', posts=posts, footer=True)


@main.route('/about')
def about():
    return render_template('main/about.html', title='About')


@main.route('/announcements')
def announcements():
    return render_template('main/announcements.html', title='Announcements')
