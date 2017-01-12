from flask import Blueprint, abort, session

from user.models import User
from relationship.models import Relationship
from user.decorators import login_required

relationship_app = Blueprint('relationship_app', __name__)

@relationship_app.route('/add_friend/<to_username>', methods=('GET', 'POST'))
@login_required
def add_friend(to_username):
    logged_user = User.objects.filter(username=session.get('username')).first()
    