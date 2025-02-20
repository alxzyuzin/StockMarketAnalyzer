from logging import exception
from app import app
from flask import render_template, redirect, request, session, url_for, jsonify
from flask_login import (current_user, user_logged_out, 
                         login_user, logout_user, login_required)

#import secrets
#import smtplib

from smtplib import SMTPException, SMTPConnectError, SMTPSenderRefused
import datetime
from datetime import date
from io import BytesIO
import base64
import pickle

from app.models import ( db, 
                        Symbol, User, UserSymbol, 
                        IndicatorsParams, SymbolData,Operation,
                        Account,
                        get_user_indicators_params )
from app.userlogin  import currentusername
from app.indicators import ChartsData
from sqlalchemy import and_

#____________________________________________________________________________
#   Display homepage
#____________________________________________________________________________
@app.route("/")
def home():
   return render_template("home.html", pageName = "Home", user = current_user)


#____________________________________________________________________________
#   Display list of simbols and calculated indiators for selected simbol
#____________________________________________________________________________

@app.route("/symbols")
@login_required
def symbols():
  
   plots_img = "/static/images/empty_plots.png"
   if request.args:
      req = request.args
      listtype = int(req["listtype"])
      rwl      = req["rwl"]
      symbols=[]  
      try:
         # Listtypes
         #   0 - unselected
         #   1 - portfolio
         #   2 - watchlist
         #   3 - shortlist
         if listtype > 0 :
            subquery = db.session.query(UserSymbol.symbol
                                       ).filter(UserSymbol.userid == current_user.id, UserSymbol.listtype == listtype
                                       ).subquery()
            symbols = db.session.query(Symbol, SymbolData
                                       ).outerjoin(SymbolData, SymbolData.symbol ==Symbol.symbol
                                       ).filter(Symbol.symbol.in_(subquery)
                                       ).order_by(Symbol.symbol).all()   


         ## Get list of symbols in portfolio
         #if listtype == "portfolio": 
         #   subquery = db.session.query(UserSymbol.symbol
         #                              ).filter(UserSymbol.userid == current_user.id, UserSymbol.listtype == 1
         #                              ).subquery()
         #   symbols = db.session.query(Symbol, SymbolData
         #                              ).outerjoin(SymbolData, SymbolData.symbol ==Symbol.symbol
         #                              ).filter(Symbol.symbol.in_(subquery)
         #                              ).order_by(Symbol.symbol).all()            
         # Get list of simbols in watchlist
         #if listtype == "watchlist":
         #   subquery = db.session.query(UserSymbol.symbol
         #                              ).filter(UserSymbol.userid == current_user.id, UserSymbol.listtype == 2
         #                              ).subquery()
         #   symbols = db.session.query(Symbol, SymbolData
         #                              ).outerjoin(SymbolData, SymbolData.symbol == Symbol.symbol
         #                              ).filter(Symbol.symbol.in_(subquery)
         #                              ).order_by(Symbol.symbol).all()
            # Get list of symbols in watchlist
         #if listtype == "shortlist":
         #   subquery = db.session.query(UserSymbol.symbol
         #                              ).filter(UserSymbol.userid == current_user.id, UserSymbol.listtype == 3
         #                              ).subquery()
         #   symbols = db.session.query(Symbol, SymbolData
         #                              ).outerjoin(SymbolData, SymbolData.symbol ==Symbol.symbol
         #                              ).filter(Symbol.symbol.in_(subquery)
         #                              ).order_by(Symbol.symbol).all()
            
         # Get list of all symbols that are in application database 
         #if listtype == "unselected":
         else:
            subquery = db.session.query(UserSymbol.symbol
                                       ).filter(UserSymbol.userid == current_user.id
                                       ).subquery()
            symbols = db.session.query(Symbol, SymbolData
                                       ).outerjoin(SymbolData, SymbolData.symbol ==Symbol.symbol
                                       ).filter(Symbol.symbol.notin_(subquery)
                                       ).order_by(Symbol.symbol).all()
         # Create mosck history data object to provide all nessesery values for html template
         # if no one symbol selected
         historydata = ChartsData("-----", get_user_indicators_params("-----", current_user.id))
         #if symbol != '':
         #   # Get history price data for symbol and calculate indicators
         #   historydata = load_historical_data(symbol = symbol)
         #   # Build plots 
         #   if historydata != None and historydata.dataLoaded:
         #      plt = historydata.build_plots()
         #      # Save plots to a temporary buffer.
         #      buf = BytesIO()
         #      plt.savefig(buf, format="png")
         #      # Embed the result in the html output.
         #      fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
         #      plots_img = f'data:image/png;base64,{fig_data}'
         #   else:
         #       return render_template("error.html", pageName = "Symbols", user = current_user, error_descr = historydata.errorMessage)     
               
         # Refresh historical data for current list of symbols and calculate warning levels
         if rwl == 'true':    
            # We already read list of symbols for carrent page into variable "symbols" 
            for smb in symbols:
               load_historical_data(symbol = smb[0].symbol)
 
         return render_template("symbols.html" , pageName = "Symbols", symbols = symbols,
                                 user = current_user,
                                 listtype = listtype, plots_image = plots_img,
                                 last_price = historydata.lastPrice,
                                 warning_level = historydata.warningLevel)             
      except Exception as ex:
          return render_template("error.html", pageName = "Symbols", user = current_user, error_descr = ex.args)     

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
#   Handle request on moving symbols between lists of symbols
#____________________________________________________________________________
@app.route("/move_symbols_between_lists", methods = ['POST', 'GET'])
@login_required
def move_symbols_between_lists():
   if request.method == "POST":
      request_data = request.get_json()
      symbol = request_data[0]["symbol"]
      sourcelist = int(request_data[0]["sourcelist"])
      targetlist = int(request_data[0]["targetlist"])
      try:
         # Listtypes
         #   0 - unselected
         #   1 - portfolio
         #   2 - watchlist

         # Moving symbol from unselected to watchlist or portfolio or shortlist
         if sourcelist == 0:
            db.session.add(UserSymbol(userid = current_user.id,
                                      symbol = symbol,
                                      listtype = targetlist))
         # Moving symbol between watchlist an portfolio in any direction   
         if not(sourcelist == 0 or targetlist == 0):
            record = db.session.query(UserSymbol
                              ).filter(UserSymbol.userid == current_user.id, 
                                       UserSymbol.symbol == symbol,
                                       UserSymbol.listtype == sourcelist
                              ).first()
            record.listtype = targetlist
         
          # Moving symbol from watchlist or portfolio or shortlist to unselected   
         if targetlist == 0:
            db.session.query(UserSymbol).filter(UserSymbol.userid == current_user.id,
                                                UserSymbol.symbol == symbol,
                                                UserSymbol.listtype == sourcelist
                                                ).delete()
         db.session.commit()
         results = {"processed": "true", "error_descr":""}
      except Exception as ex:
         results = {"processed": 'false', "error_descr": ex.args}
      
   return jsonify(results)

#____________________________________________________________________________
#   Calculate symbol indicators, build plots and return plots to client
#____________________________________________________________________________
@app.route("/calculate_indicators", methods = ['POST', 'GET'])
@login_required
def calculate_indicators():
   if request.method == "POST":
      request_data = request.get_json()
      symbol = request_data[0]["symbol"]
   try:
         indicators_params = get_user_indicators_params(symbol, current_user.id)
         chartsdata = ChartsData(symbol,indicators_params)
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
      
   return render_template("symbols.html", symbols = symbols, user = current_user, listtype = request["listtype"])        
   
   #   try:
   #      indicators_params = get_user_indicators_params(symbol, current_user.id)
   #      chartsdata = ChartsData(symbol,indicators_params)
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
#  Download history price data for symbol, calculate indicators,
#  save data to the cache and return object with data
#____________________________________________________________________________
def load_historical_data( symbol:str):

   def get_history_data(symbol:str, indicators_params:IndicatorsParams):
      historydata = ChartsData(symbol, indicators_params)
      historydata.load()
      if historydata.dataLoaded != False:
         historydata.calculate_indicators()
      return historydata
   
   try:
      historydata = None
      indicators_params = get_user_indicators_params(symbol, current_user.id)
      # Try to find symbol's history data in cache
      symboldata = db.session.query(SymbolData).filter(SymbolData.symbol == symbol).first()
      # If no data for symbol in the cache load history data and save it to the cache
      if symboldata == None:
            # No symbol data in the cache so load history data and
            # save history data in the cache
            historydata = get_history_data(symbol, indicators_params)
            if historydata.dataLoaded:            
               serialized_history_data = pickle.dumps(historydata)
               symboldata = SymbolData(symbol = symbol,
                                       warning_level=historydata.warningLevel,
                                       date_of_loading=date.today(),
                                       historical_data = serialized_history_data,
                                       last_price = historydata.lastPrice)
               db.session.add(symboldata)
               db.session.commit()
            else:
               return historydata
         
      historydata = pickle.loads(symboldata.historical_data)

      # Symbol data exist in the cache
      # If data in the cache outdated or data loaded with outdated params
      # load new history data   
      if symboldata.date_of_loading < date.today()\
         or (not (historydata.get_indicators_params() == indicators_params)):
        
         historydata = get_history_data(symbol, indicators_params)
         if historydata.dataLoaded:
            # Save new history data in the cache
            serialized_historycaldata = pickle.dumps(historydata) 
            symboldata.warning_level = historydata.warningLevel
            symboldata.date_of_loading = date.today()
            symboldata.historical_data = serialized_historycaldata
            symboldata.last_price = historydata.lastPrice
            db.session.commit()
      else:
         # There is valid symbol data in the cache 
         # Restore symbol's history data from cache
         historydata = pickle.loads(symboldata.historical_data)

   except Exception as ex:
     raise Exception(f"Error loading historical data for symbol {symbol} {ex.args}")
  
   return historydata

@app.route("/editsymboldata", methods=["GET","POST"])
@login_required
def editsymboldata():
   
   def get_checkbox_value(form:object, name:str)->bool:
      if form.get(name, "off") == "off":
         return False
      else:
         return True
      
   EditResult = ""
   symbol = Symbol()
   if request.args:
      req = request.args
      if req["symbol"] != "":
         symbol = db.session.query(Symbol).filter(Symbol.symbol == request[symbol]).first()
  
   if request.method == "POST":
      try:
         symbol = request.form["inputSymbol"]
         symbol = db.session.query(Symbol).filter(Symbol.symbol == symbol).first()
         if symbol == None:
            symbol = Symbol()
            db.session.add(symbol)

         symbol.symbol = request.form["inputSymbol"]
         symbol.title = request.form["inputTitle"]
         symbol.sector = request.form["inputSector"]
         symbol.industry = request.form["inputIndustry"]
         symbol.country = request.form["inputCountry"]
         symbol.isfund = get_checkbox_value(request.form, "isFund")
         symbol.onemonthreturn = float(request.form["inputOneMonthReturn"])
         symbol.twomonthreturn = float(request.form["inputTwoMonthReturn"])
         symbol.threemonthreturn = float(request.form["inputThreeMonthReturn"])
         symbol.sixmonthreturn = float(request.form["inputSixMonthReturn"])

         #symbol.ytd = float(request.form["inputYTD"])
         #symbol.oneyearreturn = float(request.form["inputOneYearReturn"])
         #symbol.threeyearreturn = float(request.form["inputThreeYearReturn"])
         #symbol.fiveyearreturn = float(request.form["inputFiveYearReturn"])
         #symbol.tenyearreturn = float(request.form["inputTenYearReturn"])
         #symbol.lifeoffundreturn = float(request.form["inputLifeOfFundReturn"])
         #symbol.netto = float(request.form["inputNetto"])
         #symbol.gross = float(request.form["inputGross"])
         #symbol.overall = float(request.form["inputOverall"])
      
         #db.session.add(symbol)
         db.session.commit()
         EditResult = "Symbol data saved."
      except Exception as ex:
         EditResult = f"Error saving symbol data {ex.args}"
           
   return render_template("editsymbol.html", pageName = "Symbol", symbol = symbol, user = current_user, operationResult = EditResult)


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
      portfolioSymbols = db.session.query(UserSymbol
                                          ).filter(UserSymbol.userid == current_user.id and 
                                                   UserSymbol.listtype == 1
                                          ).all()
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

     
#____________________________________________________________________________
# Delete symbols from database and edit symbol info
#____________________________________________________________________________
@app.route("/managesymbols")
@login_required
def managesymbols():
   # symbol
   # title
   # sector
   # industry
   # country
   # isfund
   operationResult = ""
   try:
     
      symbols = db.session.query(
                                 Symbol.symbol, 
                                 Symbol.title,
                                 Symbol.sector,
                                 Symbol.industry,
                                 Symbol.country,
                                 Symbol.isfund,
                                 UserSymbol.listtype,
                                 UserSymbol.userid
                              ).outerjoin(
                                 UserSymbol, and_(Symbol.symbol == UserSymbol.symbol, UserSymbol.userid == current_user.id)
                              #).filter(
                                 
                              ).order_by(
                                 Symbol.symbol
                              ).all()

      i = 0
      #symbols = db.session.query(Symbol).order_by(Symbol.symbol).all()
   except Exception as ex:
      operationResult = f"Error loading data {ex.args}"
   return render_template("managesymbols.html", pageName = "Symbols",
                          today = date.today(),
                          symbols = symbols,
                          user = current_user, 
                          operationResult = operationResult)



#@app.route("/copilotexample")
#def copilotexample():
#   return render_template("copilotexample.html", pageName = "Copilot Example", user = current_user)