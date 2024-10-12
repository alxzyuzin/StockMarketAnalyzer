from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
 
login = LoginManager()
db = SQLAlchemy()

@login.user_loader
def load_user(id):
    #return UserModel.query.get(int(id))
    return "username"