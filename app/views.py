from logging import exception
from app import app
from flask import render_template, redirect, request, sessions, url_for, jsonify
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
        # Listtypes
         #   0 - unselected
         #   1 - portfolio
         #   2 - watchlist
      if req["listtype"] == "portfolio":
         subquery = db.session.query(UserSimbol.simbol).filter(UserSimbol.userid == current_user.id, UserSimbol.listtype == 1).subquery()
         simbols = db.session.query(Simbol).filter(Simbol.simbol.in_(subquery)).order_by(Simbol.simbol).all()
   
      if req["listtype"] == "watchlist":
         subquery = db.session.query(UserSimbol.simbol).filter(UserSimbol.userid == current_user.id, UserSimbol.listtype == 2).subquery()
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

@app.route("//move_simbols_between_lists", methods = ['POST', 'GET'])
def add_simbol_to_watchlist():
   if request.method == "POST":
      request_data = request.get_json()
      simbol = request_data[0]["simbol"]
      sourcelist = request_data[0]["sourcelist"]
      targetlist = request_data[0]["targetlist"]
      try:
         # Listtypes
         #   0 - unselected
         #   1 - portfolio
         #   2 - watchlist

         # Moving simbol from unselected to watchlist or portfolio
         if (sourcelist == 0) and (targetlist == 1 or targetlist == 2):
            db.session.add(UserSimbol(userid = current_user.id,
                                   simbol = simbol,
                                   listtype = targetlist))
         # Moving simbol between watchlist an portfolio in any direction   
         if (sourcelist == 1 and targetlist == 2) or (sourcelist == 2 and targetlist == 1):   
             record = db.session.query(UserSimbol).filter(UserSimbol.userid == current_user.id, 
                                                          UserSimbol.simbol == simbol,
                                                          UserSimbol.listtype == sourcelist
                                                          ).first()
             record.listtype = targetlist
         
          # Moving simbol from watchlist or portfolio to unselected   
         if (sourcelist == 1 or sourcelist == 2) and (targetlist == 0):
            db.session.query(UserSimbol).filter(UserSimbol.userid == current_user.id,
                                                          UserSimbol.simbol == simbol,
                                                          UserSimbol.listtype == sourcelist
                                                          ).delete()
         db.session.commit()
         results = {"processed": "true", "error_descr":""}
      except Exception as ex:
         results = {"processed": 'false', "error_descr": ex.args}
      
   return jsonify(results)