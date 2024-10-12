# Зтот файл превращает каталог в котором он лежит
# в package

from flask import Flask
app = Flask(__name__)

from app import views
#rom app import admin_views

#from utils import currentusername

app.config.from_object("config.Config")