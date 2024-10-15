from logging import exception
from app import app
from flask import render_template, request, sessions, url_for
from flask_login import current_user, user_logged_out

import smtplib
from smtplib import SMTPException, SMTPConnectError, SMTPSenderRefused
import datetime

#from app.dbutils import select_imagedata
#from app.models import db, ArtworkModel, GalleryModel
from app.username  import currentusername




#======================================
#   Display homepage
#======================================
@app.route("/")
def home():
   #galleries = db.session.query(GalleryModel).all()
   return render_template("home.html")