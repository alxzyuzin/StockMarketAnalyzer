from app import app
from flask_login import current_user, user_logged_out, login_user, logout_user, login_required
from flask import render_template, redirect, request, session, url_for, jsonify

from app.models import ( db,
                         Simbol, User, UserSimbol, IndicatorsParams, SimbolData,
                         get_user_indicators_params)


@app.route('/settings')
@login_required
def settings():
   if request.args:
      req = request.args
      simbol   = req["simbol"]
      # Select simbols that are in user's portfolio
      simbols = db.session.query(UserSimbol.simbol).filter(UserSimbol.userid == current_user.id, UserSimbol.listtype == 1).all()
   
      if simbol == '':
         indicators_params = None
      else:
         indicators_params = get_user_indicators_params(simbol, current_user.id)
   
   return render_template("settings.html", pageName = "Settings", 
                          simbols = simbols,
                          user = current_user,
                          par_values = indicators_params,
                          message = "") 

@app.route('/savesettings')
@login_required
def savesettings():
   settingsSavingResult = "Settings saved successfully."
   return render_template("settings.html", pageName = "Settings", user = current_user, message = settingsSavingResult) 

