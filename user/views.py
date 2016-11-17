from flask import Blueprint, render_template
import bcrypt

from user.models import User
from user.forms import RegisterForm

user_app = Blueprint('user_app', __name__)

@user_app.route('/login')
def login():
    return "User login"