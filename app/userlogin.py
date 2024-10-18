from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, current_user

login = LoginManager()

def currentusername():
    if current_user.is_authenticated:
        return current_user.username
    else:
        return None
    
@login.user_loader
def load_user(id):
    #return UserModel.query.get(int(id))
    return "username"