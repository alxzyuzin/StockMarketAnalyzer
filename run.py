# App starts from this file

# import variable app from pakage app
from app import app

# package app contains module models.py
# import variables db,login from module models.py
# defined in a package app

from app.models import db
from app.userlogin import login


# Link 'db' instance to our application
db.init_app(app)
# Link 'login' instance to our application
login.init_app(app)
# Tell Flask_login page name (route) 
# the unauthenticated users will be redirected
# This is login page only
login.login_view = 'login'


if __name__ == "__main__":
    app.run()