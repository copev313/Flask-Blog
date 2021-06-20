from flask import Flask, render_template


app = Flask(__name__)

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


@app.route('/login')
def login():
    return "<h1>[LOGIN PAGE]</h1>"


@app.route('/register')
def register():
    return "<h1>[REGISTER PAGE]</h1>"
