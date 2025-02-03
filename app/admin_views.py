from app import app
from flask import render_template, redirect, request, session, url_for, jsonify
from flask_login import current_user, user_logged_out, login_user, logout_user, login_required

#____________________________________________________________________________
#   Display page for managing symbols list
#____________________________________________________________________________
#@app.route("/managesymbols")
#@login_required
#def managesymbols():
#   return render_template("managesymbols.html", pageName = "Admin", user = current_user)

#____________________________________________________________________________
#   Display page for managing users
#____________________________________________________________________________
@app.route("/manageusers")
@login_required
def manageusers():
   return render_template("manageusers.html", pageName = "Admin", user = current_user)