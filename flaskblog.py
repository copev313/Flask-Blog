from flask import Flask, flash, redirect, render_template, url_for
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!42476'

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
    form = RegistrationForm()
    
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}!", 'success')
        return redirect(url_for('home'))
    
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash("You've been logged in!", 'success')
            return redirect(url_for('home'))
        else:
            flash("Login unsuccessful. Please check username and password.", 'danger')

    return render_template('login.html', title='Login', form=form)

