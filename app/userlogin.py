from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, current_user

from app.models import db, User

login = LoginManager()

def currentuser():
    if current_user.is_authenticated:
        return current_user
    else:
        return None

def currentusername():
    if current_user.is_authenticated:
        return current_user.username
    else:
        return None
    
@login.user_loader
def load_user(id):
    return User.query.get(str(id))
   