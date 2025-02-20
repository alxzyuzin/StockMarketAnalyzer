from app import app
from flask_login import current_user, user_logged_out, login_user, logout_user, login_required
from flask import render_template, redirect, request, session, url_for, jsonify

from app.models import ( db,
                         Symbol, User, UserSymbol, IndicatorsParams, SymbolData,
                         get_default_indicators_params)


@app.route('/setindicatorsparams', methods=["GET","POST"])
@login_required
def settings():
   user_indicators_params = None
   new_params_set = False
   message = ""
   if request.args:
      req = request.args
      symbol   = req["symbol"]
      # Select symbols that are in user's portfolio
      #smbols = db.session.query(UserSymbol.symbol).filter(UserSymbol.userid == current_user.id, UserSymbol.listtype == 1).all()
   else:
     error_description = "Page '/setindicatorsparams' didn't get any requested args"
     return render_template("error.html", pageName = "Settings",
                             user = current_user, error_descr = error_description)     


   if symbol == '':
      error_description = "Page '/setindicatorsparams' simbol=''"
      return render_template("error.html", pageName = "Settings",
                             user = current_user, error_descr = error_description)
   try:
      user_indicators_params  = db.session.query(IndicatorsParams
                                                 ).filter(IndicatorsParams.userid == current_user.id,
                                                         IndicatorsParams.symbol == symbol
                                                ).first()   

      if user_indicators_params == None:
         new_params_set = True
         user_indicators_params = get_default_indicators_params()
         user_indicators_params.userid = current_user.id
      
      if request.method == "POST":
         form = request.form
         user_indicators_params.history_length = form["historyLength"]
         user_indicators_params.width = form["plotsWidth"]   
         user_indicators_params.heigh = form["plotsHeight"]
         user_indicators_params.background_color = form["plotsBgColor"]
         user_indicators_params.default_color = form["plotsDefaultColor"]

         user_indicators_params.ma_first_period = form["firstMaPriodLength"]
         user_indicators_params.ma_first_type = form["firstMaType"]
         user_indicators_params.ma_first_color = form["firstMaColor"]
         user_indicators_params.show_ma_first = get_checkbox_value(form, "firstMaShow")

         user_indicators_params.ma_second_period = form["secondMaPriodLength"]
         user_indicators_params.ma_second_type = form["secondMaType"]
         user_indicators_params.ma_second_color = form["secondMaColor"]
         user_indicators_params.show_ma_second = get_checkbox_value(form, "secondMaShow")
         
         user_indicators_params.ma_third_period = form["thirdMaPriodLength"]
         user_indicators_params.ma_third_type = form["thirdMaType"]
         user_indicators_params.ma_third_color = form["thirdMaColor"]
         user_indicators_params.show_ma_third = get_checkbox_value(form, "thirdMaShow")
         
         user_indicators_params.ma_volume_color = form["volumeColor"]
         user_indicators_params.show_volume = get_checkbox_value(form, "volumeShow")
         
         user_indicators_params.rsi_period = form["RSIPeriodLength"]
         user_indicators_params.rsi_color = form["RSIColor"]
         user_indicators_params.show_rsi = get_checkbox_value(form, "RSIShow")

         user_indicators_params.macd_short_period = form["MACDShortPeriodLength"]
         user_indicators_params.macd_long_period = form["MACDLongPeriodLength"]
         user_indicators_params.macd_signal_period  = form["MACDSignalPeriodLength"]
         user_indicators_params.macd_main_color = form["MACDMainColor"]
         user_indicators_params.macd_signal_color = form["MACDSignalColor"]
         user_indicators_params.show_macd = get_checkbox_value(form, "showMACD")

         user_indicators_params.bollingerband_period = form["bollingerBandPeriodLength"]
         user_indicators_params.bollingerband_probability = form["bollingerBandProbability"]
         user_indicators_params.bollingerband_color = form["bollingerBandColor"]
         user_indicators_params.bollingerband_opacity= form["bollingerBandOpacity"]
         user_indicators_params.show_bollingerband = get_checkbox_value(form, "showBollingerBand")

         if new_params_set:
            db.session.add(user_indicators_params)
         
         db.session.commit()
         message =  "Parameters saved."

      return render_template("indicatorsparams.html", pageName = "Settings", 
                           symbols = None,
                           user = current_user,
                           par_values = user_indicators_params,
                           message = message) 
   except Exception as ex:
      return render_template("error.html", pageName = "Settings", user = current_user, error_descr = ex.args)     

def get_checkbox_value(form:object, name:str)->bool:
   if form.get(name, "off") == "off":
      return False
   else:
      return True



@app.route('/userprofile', methods=["GET","POST"])
@login_required
def userprfile():
    _operationResult = ""
    if request.method == "POST":
        _UserName = request.form["inputUserName"]
        _EMail = request.form["inputUserEMail"]
        _Password_1 = request.form["inputPassword_1"]
        _Password_2 = request.form["inputPassword_2"]
        if _Password_1 != _Password_2:
            _operationResult = "Entered passwords do not match."
            return render_template("userprofile.html", pageName = "UserProfile", user = current_user, operationResult = _operationResult)

        try:
            user = db.session.query(User).filter(User.id == current_user.id).first()
            user.username = _UserName
            user.email = _EMail
            user.set_password(_Password_1)
            db.session.commit() 
            _operationResult = "User's data updated succesfully."
        except Exception as ex:  
             return render_template("error.html", pageName = "UserProfile", user = current_user, error_descr = ex.args)            
    return render_template("userprofile.html", pageName = "UserProfile", user = current_user, operationResult = _operationResult)