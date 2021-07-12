import secrets
import os
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail


# Helper function for resizing & saving a profile image:
def save_picture(form_picture):
    # Generate random hex to prevent duplicate images:
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path,
                                'static/profile_pics',
                                picture_fn)
    # Resize the image to 125x125 pixels:
    output_size = (125, 125)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    # Save the image:
    img.save(picture_path)
    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''Hello {user.username},

To reset your password, visit the following link: 
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.

Thank you,

    The Flask-Blog App
'''
    mail.send(msg)
