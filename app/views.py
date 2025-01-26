from logging import exception
from app import app
from flask import render_template, redirect, request, session, url_for, jsonify
from flask_login import current_user, user_logged_out, login_user, logout_user, login_required

#import secrets
#import smtplib

from smtplib import SMTPException, SMTPConnectError, SMTPSenderRefused
import datetime
from datetime import date
from io import BytesIO
import base64
import pickle

from app.models import ( db, 
                        Simbol, User, UserSimbol, 
                        IndicatorsParams, SimbolData,Operation,
                        Account,
                        get_user_indicators_params )
from app.userlogin  import currentusername
from app.indicators import ChartsData

#____________________________________________________________________________
#   Display homepage
#____________________________________________________________________________
@app.route("/")
def home():
   return render_template("home.html", pageName = "Home", user = current_user)


#____________________________________________________________________________
#   Display list of simbols and calculated indiators for selected simbol
#____________________________________________________________________________

@app.route("/simbols")
@login_required
def simbols():
   #if not current_user.is_authenticated:
   #    return render_template("home.html", pageName = "Home", user = current_user)
   plots_img = "/static/images/empty_plots.png"
   if request.args:
      req = request.args
      listtype = req["listtype"]
      simbol   = req["simbol"]
      rwl      = req["rwl"]
      simbols=[]
      # If page requested for specific simbol get simbol description from database
      selected_simbol_data = db.session.query(Simbol).filter(Simbol.simbol == simbol).first()  
      try:
         # Listtypes
         #   0 - unselected
         #   1 - portfolio
         #   2 - watchlist
         #   3 - shortlist
         
         # Get list of simbols in portfolio
         if listtype == "portfolio": 
            subquery = db.session.query(UserSimbol.simbol)\
                     .filter(UserSimbol.userid == current_user.id, UserSimbol.listtype == 1).subquery()
            simbols = db.session.query(Simbol, SimbolData)\
                                 .outerjoin(SimbolData, SimbolData.simbol ==Simbol.simbol)\
                                 .filter(Simbol.simbol.in_(subquery))\
                                 .order_by(Simbol.simbol).all()            
         # Get list of simbols in watchlist
         if listtype == "watchlist":
            subquery = db.session.query(UserSimbol.simbol)\
                                 .filter(UserSimbol.userid == current_user.id, UserSimbol.listtype == 2).subquery()
            simbols = db.session.query(Simbol, SimbolData)\
                                 .outerjoin(SimbolData, SimbolData.simbol ==Simbol.simbol)\
                                 .filter(Simbol.simbol.in_(subquery))\
                                 .order_by(Simbol.simbol).all()
            # Get list of simbols in watchlist
         if listtype == "shortlist":
            subquery = db.session.query(UserSimbol.simbol)\
                                 .filter(UserSimbol.userid == current_user.id, UserSimbol.listtype == 3).subquery()
            simbols = db.session.query(Simbol, SimbolData)\
                                 .outerjoin(SimbolData, SimbolData.simbol ==Simbol.simbol)\
                                 .filter(Simbol.simbol.in_(subquery))\
                                 .order_by(Simbol.simbol).all()
            
         # Get list of all simbols that are in application databace 
         if listtype == "unselected":
            subquery = db.session.query(UserSimbol.simbol).filter(UserSimbol.userid == current_user.id).subquery()
            simbols = db.session.query(Simbol, SimbolData)\
                                 .outerjoin(SimbolData, SimbolData.simbol ==Simbol.simbol)\
                                 .filter(Simbol.simbol.notin_(subquery))\
                                 .order_by(Simbol.simbol).all()
         # Create mosck history data object to provide all nessesery values for html template
         # if no one simbol selected
         historydata = ChartsData("-----", get_user_indicators_params("-----", current_user.id))
         if simbol != '':
            # Get history price data for simbol and calculate indicators
            historydata = load_historical_data(simbol = simbol)
            # Build plots 
            if historydata != None and historydata.dataLoaded:
               plt = historydata.build_plots()
               # Save plots to a temporary buffer.
               buf = BytesIO()
               plt.savefig(buf, format="png")
               # Embed the result in the html output.
               fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
               plots_img = f'data:image/png;base64,{fig_data}'
            else:
                return render_template("error.html", pageName = "Simbols", user = current_user, error_descr = historydata.errorMessage)     
               
         # Refresh historical data for current list of simbols and calculate warning levels
         if rwl == 'true':    
            # We already read list of simbols for carrent page into variable "simbols" 
            for smb in simbols:
               load_historical_data(simbol = smb[0].simbol)
 
         return render_template("simbols.html" , pageName = "Simbols", simbols = simbols,
                                 selected_simbol = req["simbol"],
                                 selected_simbol_data = selected_simbol_data,  
                                 user = current_user,
                                 listtype = req["listtype"], plots_image = plots_img,
                                 last_price = historydata.lastPrice,
                                 warning_level = historydata.warningLevel)             
      except Exception as ex:
          return render_template("error.html", pageName = "Simbols", user = current_user, error_descr = ex.args)     

@app.route("/simbols_ind")
@login_required
def simbols_ind():
   #if not current_user.is_authenticated:
   #    return render_template("home.html", pageName = "Home", user = current_user)
   plots_img = "/static/images/empty_plots.png"
   if request.args:
      req = request.args
      listtype = req["listtype"]
      simbol   = req["simbol"]
      rwl      = req["rwl"]
      simbols=[]
      # If page requested for specific simbol get simbol description from database
      selected_simbol_data = db.session.query(Simbol).filter(Simbol.simbol == simbol).first()  
      try:
         # Listtypes
         #   0 - unselected
         #   1 - portfolio
         #   2 - watchlist
         #   3 - shortlist
         
         # Get list of simbols in portfolio
         if listtype == "portfolio": 
            subquery = db.session.query(UserSimbol.simbol)\
                     .filter(UserSimbol.userid == current_user.id, UserSimbol.listtype == 1).subquery()
            simbols = db.session.query(Simbol, SimbolData)\
                                 .outerjoin(SimbolData, SimbolData.simbol ==Simbol.simbol)\
                                 .filter(Simbol.simbol.in_(subquery))\
                                 .order_by(Simbol.simbol).all()            
         # Get list of simbols in watchlist
         if listtype == "watchlist":
            subquery = db.session.query(UserSimbol.simbol)\
                                 .filter(UserSimbol.userid == current_user.id, UserSimbol.listtype == 2).subquery()
            simbols = db.session.query(Simbol, SimbolData)\
                                 .outerjoin(SimbolData, SimbolData.simbol ==Simbol.simbol)\
                                 .filter(Simbol.simbol.in_(subquery))\
                                 .order_by(Simbol.simbol).all()
            # Get list of simbols in watchlist
         if listtype == "shortlist":
            subquery = db.session.query(UserSimbol.simbol)\
                                 .filter(UserSimbol.userid == current_user.id, UserSimbol.listtype == 3).subquery()
            simbols = db.session.query(Simbol, SimbolData)\
                                 .outerjoin(SimbolData, SimbolData.simbol ==Simbol.simbol)\
                                 .filter(Simbol.simbol.in_(subquery))\
                                 .order_by(Simbol.simbol).all()
            
         # Get list of all simbols that are in application databace 
         if listtype == "unselected":
            subquery = db.session.query(UserSimbol.simbol).filter(UserSimbol.userid == current_user.id).subquery()
            simbols = db.session.query(Simbol, SimbolData)\
                                 .outerjoin(SimbolData, SimbolData.simbol ==Simbol.simbol)\
                                 .filter(Simbol.simbol.notin_(subquery))\
                                 .order_by(Simbol.simbol).all()
         # Create mosck history data object to provide all nessesery values for html template
         # if no one simbol selected
         historydata = ChartsData("-----", get_user_indicators_params("-----", current_user.id))
         if simbol != '':
            # Get history price data for simbol and calculate indicators
            historydata = load_historical_data(simbol = simbol)
            # Build plots 
            if historydata != None and historydata.dataLoaded:
               plt = historydata.build_plots()
               # Save plots to a temporary buffer.
               buf = BytesIO()
               plt.savefig(buf, format="png")
               # Embed the result in the html output.
               fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
               plots_img = f'data:image/png;base64,{fig_data}'
            else:
                return render_template("error.html", pageName = "Simbols", user = current_user, error_descr = historydata.errorMessage)     
               
         # Refresh historical data for current list of simbols and calculate warning levels
         if rwl == 'true':    
            # We already read list of simbols for carrent page into variable "simbols" 
            for smb in simbols:
               load_historical_data(simbol = smb[0].simbol)
 
         return render_template("simbols_ind.html" , pageName = "Simbols", simbols = simbols,
                                 selected_simbol = req["simbol"],
                                 selected_simbol_data = selected_simbol_data,  
                                 user = current_user,
                                 listtype = req["listtype"], plots_image = plots_img,
                                 last_price = historydata.lastPrice,
                                 warning_level = historydata.warningLevel)             
      except Exception as ex:
          return render_template("error.html", pageName = "Simbols", user = current_user, error_descr = ex.args)     

@app.route('/portfolio')
@login_required
def portfolio():
   return render_template("portfolio.html", pageName = "Portfolio", user = current_user) 

@app.route('/contacts')
def contacts():
   return render_template("contacts.html", pageName = "Contacts", user = current_user) 
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

#============================================================================
#     AJAX requests handlers
#============================================================================
#____________________________________________________________________________
#   Handle request on moving simbols between lists of simbols
#____________________________________________________________________________
@app.route("//move_simbols_between_lists", methods = ['POST', 'GET'])
@login_required
def move_simbols_between_lists():
   if request.method == "POST":
      request_data = request.get_json()
      simbol = request_data[0]["simbol"]
      sourcelist = request_data[0]["sourcelist"]
      targetlist = int(request_data[0]["targetlist"])
      try:
         # Listtypes
         #   0 - unselected
         #   1 - portfolio
         #   2 - watchlist

         # Moving simbol from unselected to watchlist or portfolio or shortlist
         if (sourcelist == 0) and (targetlist == 1 or targetlist == 2 or targetlist == 3):
            db.session.add(UserSimbol(userid = current_user.id,
                                      simbol = simbol,
                                      listtype = targetlist))
         # Moving simbol between watchlist an portfolio in any direction   
         if (sourcelist == 1 and targetlist == 2)\
            or (sourcelist == 2 and targetlist == 1)\
            or (sourcelist == 1 and targetlist == 3)\
            or (sourcelist == 3 and targetlist == 1)\
            or (sourcelist == 2 and targetlist == 3)\
            or (sourcelist == 3 and targetlist == 2):
         
            record = db.session.query(UserSimbol)\
                               .filter(UserSimbol.userid == current_user.id, 
                                       UserSimbol.simbol == simbol,
                                       UserSimbol.listtype == sourcelist)\
                               .first()
            record.listtype = targetlist
         
          # Moving simbol from watchlist or portfolio or shortlist to unselected   
         if (sourcelist == 1 or sourcelist == 2 or sourcelist == 3) and (targetlist == 0):
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
@login_required
def calculate_indicators():
   if request.method == "POST":
      request_data = request.get_json()
      simbol = request_data[0]["simbol"]
   try:
         indicators_params = get_user_indicators_params(simbol, current_user.id)
         chartsdata = ChartsData(simbol,indicators_params)
         chartsdata.calculate_indicators()
         plt = chartsdata.build_plots()

         # Save plots to a temporary buffer.
         buf = BytesIO()
         plt.savefig(buf, format="png")
         # Embed the result in the html output.
         fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
         plotsimg = f'data:image/png;base64,{fig_data}'
         results = {"processed": "true",
                    "error_descr":"",
                    "plotsimg":plotsimg
                    }
   except Exception as ex:
         results = {"processed": 'false', "error_descr": ex.args}
      
   return render_template("simbols.html", simbols = simbols, user = current_user, listtype = request["listtype"])        
   
   #   try:
   #      indicators_params = get_user_indicators_params(simbol, current_user.id)
   #      chartsdata = ChartsData(simbol,indicators_params)
   #      chartsdata.calculate_indicators()
   #      plt = chartsdata.build_plots()

         # Save plots to a temporary buffer.
   #      buf = BytesIO()
   #      plt.savefig(buf, format="png")
   #      # Embed the result in the html output.
   #      fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
   #      plotsimg = f'data:image/png;base64,{fig_data}'
   #      results = {"processed": "true",
   #                 "error_descr":"",
   #                 "plotsimg":plotsimg
   #                 }
   #   except Exception as ex:
   #      results = {"processed": 'false', "error_descr": ex.args}
      
   #return jsonify(results)

#____________________________________________________________________________
# If fresh history price data exist in the cache 
#  Restore data from the cache and return object with data
# else
#  Download history price data for simbol, calculate indicators,
#  save data to the cache and return object with data
#____________________________________________________________________________
def load_historical_data( simbol:str):

   def get_history_data(simbol:str, indicators_params:IndicatorsParams):
      historydata = ChartsData(simbol, indicators_params)
      historydata.load()
      if historydata.dataLoaded != False:
         historydata.calculate_indicators()
      return historydata
   
   try:
      historydata = None
      indicators_params = get_user_indicators_params(simbol, current_user.id)
      # Try to find simbol's history data in cache
      simboldata = db.session.query(SimbolData).filter(SimbolData.simbol == simbol).first()
      # If no data for simbol in the cache load history data and save it to the cache
      if simboldata == None:
            # No simbol data in the cache so load history data and
            # save history data in the cache
            historydata = get_history_data(simbol, indicators_params)
            if historydata.dataLoaded:            
               serialized_history_data = pickle.dumps(historydata)
               simboldata = SimbolData(simbol = simbol,
                                       warning_level=historydata.warningLevel,
                                       date_of_loading=date.today(),
                                       historical_data = serialized_history_data,
                                       last_price = historydata.lastPrice)
               db.session.add(simboldata)
               db.session.commit()
            else:
               return historydata
         
      historydata = pickle.loads(simboldata.historical_data)

      # Simbol data exist in the cache
      # If data in the cache outdated or data loaded with outdated params
      # load new history data   
      if simboldata.date_of_loading < date.today()\
         or (not (historydata.get_indicators_params() == indicators_params)):
        
         historydata = get_history_data(simbol, indicators_params)
         if historydata.dataLoaded:
            # Save new history data in the cache
            serialized_historycaldata = pickle.dumps(historydata) 
            simboldata.warning_level = historydata.warningLevel
            simboldata.date_of_loading = date.today()
            simboldata.historical_data = serialized_historycaldata
            simboldata.last_price = historydata.lastPrice
            db.session.commit()
      else:
         # There is valid simbol data in the cache 
         # Restore simbol's history data from cache
         historydata = pickle.loads(simboldata.historical_data)

   except Exception as ex:
     raise Exception(f"Error loading historical data for simbol {simbol} {ex.args}")
  
   return historydata

@app.route("/editsimboldata", methods=["GET","POST"])
@login_required
def editsimboldata():
   
   def get_checkbox_value(form:object, name:str)->bool:
      if form.get(name, "off") == "off":
         return False
      else:
         return True
      
   EditResult = ""
   simbol = Simbol()
   if request.args:
      req = request.args
      if req["simbol"] != "":
         simbol = db.session.query(Simbol).filter(Simbol.simbol == request[simbol]).first()
  
   if request.method == "POST":
      try:
         simbol = request.form["inputSimbol"]
         simbol = db.session.query(Simbol).filter(Simbol.simbol == simbol).first()
         if simbol == None:
            simbol = Simbol()
            db.session.add(simbol)

         simbol.simbol = request.form["inputSimbol"]
         simbol.simbol = request.form["inputSimbol"]
         simbol.title = request.form["inputTitle"]
         simbol.sector = request.form["inputSector"]
         simbol.industry = request.form["inputIndustry"]
         simbol.country = request.form["inputCountry"]
         simbol.isfund = get_checkbox_value(request.form, "isFund")
         simbol.onemonthreturn = float(request.form["inputOneMonthReturn"])
         simbol.twomonthreturn = float(request.form["inputTwoMonthReturn"])
         simbol.threemonthreturn = float(request.form["inputThreeMonthReturn"])
         simbol.sixmonthreturn = float(request.form["inputSixMonthReturn"])

         #simbol.ytd = float(request.form["inputYTD"])
         #simbol.oneyearreturn = float(request.form["inputOneYearReturn"])
         #simbol.threeyearreturn = float(request.form["inputThreeYearReturn"])
         #simbol.fiveyearreturn = float(request.form["inputFiveYearReturn"])
         #simbol.tenyearreturn = float(request.form["inputTenYearReturn"])
         #simbol.lifeoffundreturn = float(request.form["inputLifeOfFundReturn"])
         #simbol.netto = float(request.form["inputNetto"])
         #simbol.gross = float(request.form["inputGross"])
         #simbol.overall = float(request.form["inputOverall"])
      
         #db.session.add(simbol)
         db.session.commit()
         EditResult = "Simbol data saved."
      except Exception as ex:
         EditResult = f"Error saving simbol data {ex.args}"
           
   return render_template("editsimbol.html", pageName = "Simbol", simbol = simbol, user = current_user, operationResult = EditResult)


#____________________________________________________________________________
# Register operation against portolio 
#  0 - buy shares
#  1 - sell shares
#  2 - deposit cash to investment account
#  3 - withdraw cash from investment account
#____________________________________________________________________________
@app.route("/activity")
@login_required
def activity():
   operationResult = ""
   accounts = []
   operations = []
   portfolioSymbols = []

   try:
      accounts = db.session.query(Account).filter(Account.userid == current_user.id).all()
      accounts.append(Account( "9140b38c-8d65-4e54-bf8f-205337e0634d", "Z32117095", 0.0, "USD") )  
      operations = db.session.query(Operation).filter(Operation.userid == current_user.id).all()
      portfolioSymbols = db.session.query(UserSimbol)\
                                 .filter(UserSimbol.userid == current_user.id and 
                                         UserSimbol.listtype == 1)\
                                 .all()
   except Exception as ex:
      operationResult = f"Error loading data {ex.args}"
   return render_template("activity.html", pageName = "Portfolio",
                          today = date.today(),
                          accounts = accounts, 
                          portfolioSymbols = portfolioSymbols,
                          operations = operations,
                          user = current_user, 
                          operationResult = operationResult)


#____________________________________________________________________________
#  Calculate and display portfolio perfomance
#____________________________________________________________________________     
@app.route("/perfomance", methods=["GET","POST"])
@login_required
def perfomance():
   operationResult = ""
   return render_template("perfomance.html", pageName = "Portfolio", 
                          user = current_user,
                          operationResult = operationResult)

     



