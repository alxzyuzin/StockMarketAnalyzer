from logging import exception
from app import app
from flask import render_template, redirect, request, sessions, url_for, jsonify
from flask_login import current_user, user_logged_out, login_user, logout_user, login_required

#import secrets
#import smtplib

from smtplib import SMTPException, SMTPConnectError, SMTPSenderRefused
import datetime

#from app.dbutils import select_imagedata
from app.models import db, Simbol, User, UserSimbol, IndicatorsParams
from app.userlogin  import currentusername
from app.indicators import ChartsData

from config import InitialIndicatorsParams


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

#____________________________________________________________________________
#   Handle request on moving simbols between lists of simbols
#____________________________________________________________________________
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

#____________________________________________________________________________
#   Calculate simbol indicators, build plots and return plots to client
#____________________________________________________________________________
@app.route("/calculate_indicators", methods = ['POST', 'GET'])
def calculate_indicators():
   if request.method == "POST":
      request_data = request.get_json()
      simbol = request_data[0]["simbol"]
           
      try:
         indicators_params = get_user_indicators_params(simbol, current_user.id)
         chartsdata = ChartsData(simbol,250)
         chartsdata.calculate_indicators(indicators_params)
         results = {"processed": "true", "error_descr":"", "message":"Everything is OK so far."}
      except Exception as ex:
         results = {"processed": 'false', "error_descr": ex.args}
      
   return jsonify(results)


def get_user_indicators_params(simbol:str, userid:str):
   params = IndicatorsParams(
               userid = InitialIndicatorsParams.USERID,
               simbol =  InitialIndicatorsParams.SIMBOL,

               width = InitialIndicatorsParams.WIDTH,
               heigh = InitialIndicatorsParams.HEIGH,
               daily_prices_color = InitialIndicatorsParams.DAILY_PRICES_COLOR,
    
                ma_first_period = InitialIndicatorsParams.MA_FIRST_PERIOD,
                ma_first_type = InitialIndicatorsParams.MA_FIRST_TYPE,
                ma_first_color = InitialIndicatorsParams.MA_FIRST_COLOR,
                show_ma_first = InitialIndicatorsParams.SHOW_MA_FIRST,

                ma_second_period = InitialIndicatorsParams.MA_SECOND_PERIOD,
                ma_second_type = InitialIndicatorsParams.MA_SECOND_TYPE,
                ma_second_color = InitialIndicatorsParams.MA_SECOND_COLOR,
                show_ma_second = InitialIndicatorsParams.SHOW_MA_SECOND,

                ma_third_period = InitialIndicatorsParams.MA_THIRD_PERIOD,
                ma_third_type = InitialIndicatorsParams.MA_THIRD_TYPE,
                ma_third_color = InitialIndicatorsParams.MA_THIRD_COLOR,
                show_ma_third = InitialIndicatorsParams.SHOW_MA_THIRD,
                
                ma_volume_color = InitialIndicatorsParams.VOLUME_COLOR,
                show_volume = InitialIndicatorsParams.SHOW_VOLUME,
    
                rsi_period = InitialIndicatorsParams.RSI_PERIOD,
                rsi_color = InitialIndicatorsParams.RSI_COLOR,
                show_rsi = InitialIndicatorsParams.SHOW_RSI,

                macd_short_period = InitialIndicatorsParams.MACD_SHORT_PERIOD,
                macd_long_period = InitialIndicatorsParams.MACD_LONG_PERIOD,
                macd_signal_period = InitialIndicatorsParams.MACD_SIGNAL_PERIOD,
                macd_main_color = InitialIndicatorsParams.MACD_MAIN_COLOR,
                macd_signal_color = InitialIndicatorsParams.MACD_SIGNAL_COLOR,
                show_macd = InitialIndicatorsParams.SHOW_MACD,

                bollingerband_period = InitialIndicatorsParams.BOLLINGERBAND_PERIOD,
                bollingerband_probability = InitialIndicatorsParams.BOLLINGERBAND_PROBABILITY,
                bollingerband_color = InitialIndicatorsParams.BOLLINGERBAND_COLOR,
                bollingerband_opacity = InitialIndicatorsParams.BOLLINGERBAND_OPACITY,
                show_bollingerband = InitialIndicatorsParams.SHOW_BOLINGERBAND
   )
   
   return params