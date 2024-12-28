# Зтот файл превращает каталог в котором он лежит
# в package

from flask import Flask
app = Flask(__name__)

from app import views, settings_views, ajaxqueries, admin_views
#rom app import admin_views

#from utils import currentusername

app.config.from_object("config.Config")


#_______________________________________________________
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
