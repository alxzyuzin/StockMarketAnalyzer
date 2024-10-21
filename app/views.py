from logging import exception
from app import app
from flask import render_template, request, sessions, url_for
from flask_login import current_user, user_logged_out

import smtplib
from smtplib import SMTPException, SMTPConnectError, SMTPSenderRefused
import datetime

#from app.dbutils import select_imagedata
from app.models import db, Simbol, User, UserSimbol
from app.userlogin  import currentusername




#____________________________________________________________________________
#   Display homepage
#____________________________________________________________________________
@app.route("/")
def home():
   return render_template("home.html")


#____________________________________________________________________________
#   Display list of simbols and calculated indiators for selected simbol
#____________________________________________________________________________
@app.route("/simbols")
def simbols():
   if request.args:
      req = request.args
      if req["listtype"] == "portfolio":
          simbols = db.session.query(Simbol).order_by(Simbol.simbol).all()
      if req["listtype"] == "wachlist":
          simbols = db.session.query(Simbol).order_by(Simbol.simbol).all()
      if req["listtype"] == "unselected":
          simbols = db.session.query(Simbol).order_by(Simbol.simbol).all()
        
      print(req["listtype"])
   return render_template("simbols.html", simbols = simbols)