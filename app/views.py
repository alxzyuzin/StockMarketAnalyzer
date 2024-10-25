from logging import exception
from app import app
from flask import render_template, redirect, request, sessions, url_for
from flask_login import current_user, user_logged_out, login_user, logout_user, login_required

#import secrets
#import smtplib

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
   return render_template("home.html", user = current_user)


#____________________________________________________________________________
#   Display list of simbols and calculated indiators for selected simbol
#____________________________________________________________________________

@app.route("/simbols")
def simbols():
   if request.args:
      req = request.args
      simbols=[]
      if req["listtype"] == "portfolio":
          subquery = db.session.query(UserSimbol.simbol).filter(UserSimbol.userid == current_user.id and UserSimbol.listtype == "portfolio").subquery()
          simbols = db.session.query(Simbol).filter(Simbol.simbol.in_(subquery)).order_by(Simbol.simbol).all()
   
      if req["listtype"] == "watchlist":
          subquery = db.session.query(UserSimbol.simbol).filter(UserSimbol.userid == current_user.id and UserSimbol.listtype == "watchlist").subquery()
          simbols = db.session.query(Simbol).filter(Simbol.simbol.in_(subquery)).order_by(Simbol.simbol).all()
          
      if req["listtype"] == "unselected":
          subquery = db.session.query(UserSimbol.simbol).filter(UserSimbol.userid == current_user.id).subquery()
          simbols = db.session.query(Simbol).filter(Simbol.simbol.notin_(subquery)).order_by(Simbol.simbol).all()
       
   return render_template("simbols.html", simbols = simbols, user = current_user, listtype = req["listtype"])


#____________________________________________________________________________
#   Display login page 
#____________________________________________________________________________

@app.route("/login", methods=["GET","POST"])
def login():
    loginResult = ""
    if request.method == "POST":
        inUserName = request.form["inputUserName"]
        inPassword = request.form["inputPassword"]
        try:
            user = db.session.query(User).filter(User.username == inUserName).first()
            if user is not None and user.check_password(inPassword):
                login_user(user)
                return redirect('/')
            else:
                loginResult = "Invalid user name or password."   
        except Exception as ex:  
            loginResult = "Login error."        
    return render_template("login.html", pageName = "Login", user = current_user, loginRes = loginResult)


#____________________________________________________________________________
#   Log user off and redirect to home page 
#____________________________________________________________________________

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')