import pickle
from app import app
from urllib.request import urlopen
import certifi
import json
import datetime
from datetime import date

from flask import render_template, redirect, request, session, url_for, jsonify
from flask_login import current_user, user_logged_out, login_user, logout_user, login_required

from app.models import ( db, 
                        Simbol, User, UserSimbol, IndicatorsParams,
                        SimbolData, Operation,
                        get_user_indicators_params )

@app.route("/clear_simbols_historical_data", methods = ['POST', 'GET'])
@login_required
def clear_simbols_historical_data():
    try:
         pass
    #     indicators_params = get_user_indicators_params(simbol, current_user.id)
    #     chartsdata = ChartsData(simbol,indicators_params)
    #     chartsdata.calculate_indicators()
    #     plt = chartsdata.build_plots()

         # Save plots to a temporary buffer.
    #     buf = BytesIO()
    #      plt.savefig(buf, format="png")
    #      # Embed the result in the html output.
    #      fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    #      plotsimg = f'data:image/png;base64,{fig_data}'
    #     results = {"processed": "true",
    #                "error_descr":"",
    #                "plotsimg":plotsimg
    #                }
    except Exception as ex:
         results = {"processed": 'false', "error_descr": ex.args}
      
    return jsonify(results)


@app.route("/get_company_info", methods = ['POST', 'GET'])
@login_required
def get_company_info():
     company_info = {}
     description = ""
     processed = "false"
     try:
          if request.method == "POST":
               request_data = request.get_json()
               simbol = request_data[0]["simbol"]
          
               url = f"https://financialmodelingprep.com/api/v3/profile/{simbol}?apikey={app.config['API_KEY']}"
               
               response = urlopen(url, cafile=certifi.where())
               data = response.read().decode("utf-8")
               sourceData = json.loads(data)
               if len(sourceData) == 0:
                    description = f"No data obtained for simbol '{simbol}'"
                    processed = "true"
               else:
                    company_info["symbol"] = sourceData[0]["symbol"]  
                    company_info["companyName"] = sourceData[0]["companyName"]  
                    company_info["industry"] = sourceData[0]["industry"] 
                    company_info["sector"] = sourceData[0]["sector"]   
                    company_info["country"] = sourceData[0]["country"] 
                    company_info["isFund"] = sourceData[0]["isFund"]
                    description = f"Data obtained for simbol {simbol}"
                    processed = "true"      
          else:
               description = "No 'POST' request obtained."
               
     except Exception as ex:
          description = ex.msg     
          company_info = {}
          processed = "false"

     results = {
                "processed": processed,
                "description":description,
                "company_info":company_info,
                    } 
     return jsonify(results)



@app.route("/save_operation", methods = ['POST', 'GET'])
@login_required
def add_operation():
     description = ""
     try:
          if request.method == "POST":
               request_data = request.get_json()
               # Define the format of the date string 
               date_format = "%Y-%m-%d"
               # Convert string date to datetime object 
               operation_date = datetime.datetime.strptime(request_data["date"], date_format)
               rowid = int(request_data["rowid"])      
               if int(request_data["rowid"]) == -1:
                    newOperation = Operation(current_user.id, request_data["account"],
                                        request_data["symbol"], operation_date,
                                        int(request_data["operationType"]),
                                        float(request_data["price"]),
                                        float(request_data["quantity"]) )
                    db.session.add(newOperation)
               else:
                    operation = Operation.query.filter_by(id = request_data["rowid"]).first()
                    operation.account = request_data["account"]
                    operation.simbol = request_data["symbol"]
                    operation.date = operation_date
                    operation.price = float(request_data["price"])
                    operation.quantity = float(request_data["quantity"])
               db.session.commit()
               processed = True
               description = f"Operation saved."
     except Exception as ex:
          db.session.rollback()
          
          if hasattr(ex, 'msg'):
               description = f"Operation not saved - {ex.msg}"
          if hasattr(ex, 'args'):
               description = f"Operation not saved - {ex.args}"
          processed = False
     
     results = {
               "processed": processed,
               "description": description,
               }
     return jsonify(results)

@app.route("/delete_operation", methods = ['POST', 'GET'])
@login_required
def delete_operation():
     description = ""
     try:
          if request.method == "POST":
               request_data = request.get_json()
               Operation.query.filter_by(id = request_data["rowid"]).delete()
               db.session.commit()
               processed = True
               description = f"Operation deleted."
     except Exception as ex:
          db.session.rollback()
          msghdr = "Operation not deleted -"
          if hasattr(ex, 'msg'):
               description = f"{msghdr} {ex.msg}"
          if hasattr(ex, 'args'):
               description = f"{msghdr} {ex.args}"
          processed = False
     
     results = {
               "processed": processed,
               "description": description,
               }
     return jsonify(results)


@app.route("/get_operation_data", methods = ['POST', 'GET'])
@login_required
def get_operation_data():
     description = ""
     try:
          if request.method == "POST":
               request_data = request.get_json()
               operation = Operation.query.filter_by(id = request_data["rowid"]).first()
               operationdata = {
                              "id":operation.id, 
                              "type":operation.type,
                              "userid":operation.userid,
                              "account":operation.account,
                              "simbol":operation.simbol,
                              "date":operation.date.strftime("%Y-%m-%d"),
                              "price":operation.price,
                              "quantity":operation.quantity, 
                              "todayprice":operation.todayprice
                              }
               processed = True
               description = f"Data obtained."
     except Exception as ex:
          msghdr = "Request for data failed - "
          if hasattr(ex, 'msg'):
               description = f"{msghdr} {ex.msg}"
          if hasattr(ex, 'args'):
               description = f"{msghdr} {ex.args}"
          processed = False
     
     results = {
               "processed":processed,
               "operationdata": operationdata,
               "description": description
               }
     return jsonify(results)
