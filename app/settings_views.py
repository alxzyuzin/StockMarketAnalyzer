from app import app
from flask_login import current_user, user_logged_out, login_user, logout_user, login_required
from flask import render_template, redirect, request, session, url_for, jsonify

from app.models import ( db,
                         Simbol, User, UserSimbol, IndicatorsParams, SimbolData,
                         get_user_indicators_params)


@app.route('/settings', methods=["GET","POST"])
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