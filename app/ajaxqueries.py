import pickle
from app import app
from urllib.request import urlopen
import certifi
import json
import datetime
from datetime import date
import math

from flask import render_template, redirect, request, session, url_for, jsonify
from flask_login import current_user, user_logged_out, login_user, logout_user, login_required

from app.models import ( db, 
                        Symbol, User, UserSymbol, IndicatorsParams,
                        SymbolData, Operation,
                        get_user_indicators_params )
from app.indicators import ChartsData

@app.route("/clear_symbols_historical_data", methods = ['POST', 'GET'])
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

@app.route("/get_charts_data", methods = ['POST', 'GET'])
@login_required
def get_gharts_data():
   if request.method == "POST":
      request_data = request.get_json()
      symbol = request_data[0]["symbol"]
      period = int(request_data[0]["period"])
   try:
          indicators_params = get_user_indicators_params(symbol, current_user.id)
          chartsdata = ChartsData(symbol,indicators_params)
          chartsdata.load()
          chartsdata.calculate_indicators()
          symbol_data = db.session.query(Symbol).filter(Symbol.symbol == symbol).first()  
          offset = max(indicators_params.get_offset(), len(chartsdata.Labels()) - period)      
          results = {"processed": "true",
                    "error_descr":"",
                    "charts_ma_data": config_MA(chartsdata, indicators_params, offset),
                    "charts_rsi_data": config_RSI(chartsdata, indicators_params, offset),
                    "charts_macd_data": config_MACD(chartsdata, indicators_params, offset),
                    "symbol_header":symbol_data.title,
                    "last_price":chartsdata.lastPrice
                    }
   except Exception as ex:
         results = {"processed": 'false', "error_descr": ex.args}
      
   return jsonify(results)
#__________________________________________________________________________________
#
#  Convert one sline date label (MM-DD-YY) to double line date label [DD,MM]
#__________________________________________________________________________________
def format_labels(sourcelabels)->list[str]:
     labels = []
     month = ""
     day = ""
     year = ""

     for label in sourcelabels:
          labelparts = label.split()
          if labelparts[2] == year:
               if labelparts[0][:3] == month:
                    labels.append([labelparts[1][:2],labelparts[0][:3],""])
               else:
                    labels.append([labelparts[1][:2],labelparts[0][:3],""])
                    month = labelparts[0][:3]
          else:
               labels.append([labelparts[1][:2],labelparts[0][:3],labelparts[2]])
               year = labelparts[2]       
               month = labelparts[0][:3]
     return labels


#__________________________________________________________________________________
#
#  Configuration for Moving Average chart
#__________________________________________________________________________________
def config_MA(chartsData:ChartsData, indicatorsParams:IndicatorsParams, offset:int):
     
     labels = format_labels(chartsData.Labels())
     
     closePrices = chartsData.ClosePrices()
     firstMA = chartsData.FirstMA()
     secondMA = chartsData.SecondMA()
     thirdMA = chartsData.ThirdMA()
     upperBoligerBand  = chartsData.UpperBBRange()
     lowerBoligerBand  = chartsData.LoverBBRange()
     
     # Calculate trend lines
     #chartsData.calcUpperTrendLine(period)
     #upperTrendLine = chartsData.UpperTrendLine()
     #trendlineoffset = len(upperTrendLine) - period

     #chartsData.calcLowerTrendLine(period)
     #lowerTrendLine = chartsData.LowerTrendLine()

     opacity = str(hex(int(255 * indicatorsParams.bollingerband_opacity)))[2:]
     bollingerBandColor = indicatorsParams.bollingerband_color + opacity
     data = {
               'labels':labels[offset:],
          
               'datasets': [
                         { # Daily prices
                         'label':'Daily prices',
                         'data':closePrices[offset:],
                         'borderWidth':1,
                         'pointRadius':0,
                         'borderColor':indicatorsParams.default_color,
                         #'yAxisID':'y',
                         },
                         { # First MA
                         'label':f'{indicatorsParams.ma_first_period} days {indicatorsParams.ma_first_type.upper()}',
                         'data':firstMA[offset:],
                         'borderWidth':1,
                         'pointRadius':0,
                         'borderColor':indicatorsParams.ma_first_color,
                         #'yAxisID': 'y',
                         },
                         { # Second MA
                         'label':f'{indicatorsParams.ma_second_period} days {indicatorsParams.ma_second_type.upper()}',
                         'data':secondMA[offset:],
                         'borderWidth':1,
                         'pointRadius':0,
                         'borderColor':indicatorsParams.ma_second_color,
                         #'yAxisID': 'y',
                         },
                         { # Third MA
                         'label':f'{indicatorsParams.ma_third_period} days {indicatorsParams.ma_third_type.upper()}',
                         'data':thirdMA[offset:],
                         'borderWidth':1,
                         'pointRadius':0,
                         'borderColor':indicatorsParams.ma_third_color,
                         #'yAxisID': 'y',
                         },
                         { # Upper Bolinger band
                         'label':'none',
                         'data':upperBoligerBand[offset:],
                         'borderWidth':1,
                         'pointRadius':0,
                         'borderColor':bollingerBandColor,               
                         },
                         { # Lover Bolinger band
                         'label':f'Bollinger band {indicatorsParams.bollingerband_period} days.',
                         'data':lowerBoligerBand[offset:],
                         'borderWidth':1,
                         'pointRadius':0,
                         'borderColor':bollingerBandColor,
                         'backgroundColor':  bollingerBandColor,
                         'fill':'-1'
                         }
   
                         ]
        }

     y_min = math.floor(min(min(closePrices[offset:]), min(lowerBoligerBand[offset:]))) 
     y_max = math.ceil(max(max(closePrices[offset:]), max(upperBoligerBand[offset:])))

     chartConfig = {
            'type': 'line',
            'data': data,
            'options': {
                         'responsive': True,
                         'maintainAspectRatio': False, #// Disable the aspect ratio to control height
                         'scales': {
                              'x':{               
                                   'ticks':{
                                             'type': 'time',
                                             'time': {
                                                       'unit': 'day', # Unit for the ticks (e.g., 'day', 'month', 'year')
                                                       'stepSize': 5  # Interval for the ticks (e.g., every 2 days)
                                              },
                                             'color': indicatorsParams.default_color,
                                             'maxRotation': 0, #Prevents rotation
                                             'minRotation': 0  # Prevents rotation
                                             },
                                   'grid':{
                                             'color':indicatorsParams.default_color,
                                             'lineWidth': 0.3,
                                             'tickColor':indicatorsParams.default_color,
                                             'borderColor':indicatorsParams.default_color,
                                             }
                                   }, 
                              'y': {
                              
                                   'min': y_min,
                                   'max': y_max,
                                   'ticks': { 
                                             'color': indicatorsParams.default_color
                                             },
                                   'grid': {
                                             'color':indicatorsParams.default_color,
                                             'lineWidth': 0.3,
                                             'tickColor':indicatorsParams.default_color,
                                             'borderColor':indicatorsParams.default_color,
                                             }
                              },
                              'y1': {
                              'position':'right',
                              'min': y_min,
                              'max': y_max,
                              'ticks': { 'color': indicatorsParams.default_color },
                              'grid': { 'display':False  }
                              }

                         },
                         'plugins': {
                                   'legend': {
                                             'labels': {
                                                        'color': indicatorsParams.default_color, # Set the color for legend labels
                                                        'filter': ''
                                                       }
                                             }
                                   }
            }
        }
     return chartConfig

#__________________________________________________________________________________
#
#  Configuration for RSI chart
#__________________________________________________________________________________  
def config_RSI(chartsData:ChartsData, indicatorsParams:IndicatorsParams,offset:int):
     
     labels = format_labels(chartsData.Labels())    
     rsiData = chartsData.RSI()
     data = {
               'labels':labels[offset:],
          
               'datasets': [
                         { # RSI
                         'label':'RSI',
                         'data':chartsData.RSI()[offset:],
                         'borderWidth':1,
                         'pointRadius':0,
                         'borderColor':indicatorsParams.rsi_color,
                         },
                        
                         ]
        }

     threshold_x_min = min(labels[offset:])
     threshold_x_max = max(labels[offset:])
     threshold_y_min = -30
     threshold_y_max = 30

     chart_y_max = 50
     chart_y_min = -50

     chartConfig = {
                    'type': 'line',
                    'data': data,
                    'options': {
                                   'responsive': True,
                                   'maintainAspectRatio': False,
                         'scales': {
                              'x':{               
                                   'ticks':{
                                        'type': 'time',
                                             'time': {
                                                       'unit': 'day', # Unit for the ticks (e.g., 'day', 'month', 'year')
                                                       'stepSize': 5  # Interval for the ticks (e.g., every 2 days)
                                              },
                                             'display': True, # Show x-axis labels
                                             'stepSize': 20,  # Set ticks interval 
                                             'color': indicatorsParams.default_color,
                                             'maxRotation': 0, #Prevents rotation
                                             'minRotation': 0  # Prevents rotation
                                             },
                                   'grid':{
                                             'color':indicatorsParams.default_color,
                                             'lineWidth': 0.3,
                                             'tickColor':indicatorsParams.default_color,
                                             'borderColor':indicatorsParams.default_color,
                                             }
                                   }, 
                              'y': {                        
                                   'min': chart_y_min,
                                   'max': chart_y_max,
                                   'ticks': { 
                                             'color': indicatorsParams.default_color
                                             },
                                   'grid': {
                                             'color':indicatorsParams.default_color,
                                             'lineWidth': 0.3,
                                             'tickColor':indicatorsParams.default_color,
                                             'borderColor':indicatorsParams.default_color,
                                             }
                              },
                              'y1': {
                              'position':'right',
                              'min': chart_y_min,
                              'max': chart_y_max,
                              'ticks': { 'color': indicatorsParams.default_color },
                              'grid': { 'display':False  }
                              }

                         },
                         'plugins': {
                                   'legend': {
                                             'display': False, # Hide the legend
                                             'labels': {
                                                        'color': indicatorsParams.default_color, # Set the color for legend labels
                                                        'filter': ''
                                                       }
                                             },
                                   
                                   'annotation': {
                                                  'annotations': {
                                                                 'box': {
                                                                           'type': 'box',
                                                                           'xMin': threshold_x_min,
                                                                           'xMax': threshold_x_max,
                                                                           'yMin': threshold_y_min, # y-axis value where the line starts
                                                                           'yMax': threshold_y_max,  # y-axis value where the line ends
                                                                           'backgroundColor': '#80808020',
                                                                           'borderWidth': 1,
                                                                           'z': -1,
                                                                           },
                                                                 'zero_line': {
                                                                           'type': 'line',
                                                                           'xMin': threshold_x_min,
                                                                           'xMax': threshold_x_max,
                                                                           'yMin': 0, # y-axis value where the line starts
                                                                           'yMax': 0,  # y-axis value where the line ends
                                                                           'borderColor': '#B0B0B0',
                                                                           'borderWidth': 1,
                                                                           'z': 1,
                                                                           },
                                                                 'upper_threhold': {
                                                                           'type': 'line',
                                                                           'xMin': threshold_x_min,
                                                                           'xMax': threshold_x_max,
                                                                           'yMin': threshold_y_max, # y-axis value where the line starts
                                                                           'yMax': threshold_y_max,  # y-axis value where the line ends
                                                                           'borderColor': '#B0B0B0',
                                                                           'borderWidth': 1,
                                                                           'z': 1,
                                                                           'label': {
                                                                                     'content': 'Overbought threhold',
                                                                                     'enabled': True,
                                                                                     'position': 'center'
                                                                                     }
                                                                           },
                                                                 'lover_threhold': {
                                                                           'type': 'line',
                                                                           'xMin': threshold_x_min,
                                                                           'xMax': threshold_x_max,
                                                                           'yMin': threshold_y_min,  # y-axis value where the line starts
                                                                           'yMax': threshold_y_min,  # y-axis value where the line ends
                                                                           'borderColor': '#B0B0B0',
                                                                           'borderWidth': 1,
                                                                           'z': 1,
                                                                           'label': {
                                                                                     'content': 'Oversold threshold',
                                                                                     'enabled': True,
                                                                                     'position': 'center',
                                                                                     'font': {
                                                                                               'size': 14,
                                                                                               'weight': 'bold',
                                                                                               'family': 'Arial',
                                                                                               'style': 'italic'
                                                                                          },
                                                                                          'color': 'rgb(0, 0, 0)',
                                                                                          'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                                                                                          'borderRadius': 5,
                                                                                          'padding': 5,
                                                                                          'rotation': 90
                                                                                     }
                                                                           }
                                                                 }
                                             }
            }
        }
     }


     return chartConfig


#__________________________________________________________________________________
#
#  Configuration for MACD chart
#__________________________________________________________________________________  
def config_MACD(chartsData:ChartsData, indicatorsParams:IndicatorsParams,offset:int):
     
     labels = format_labels(chartsData.Labels())    
     data = {
               'labels':labels[offset:],
          
               'datasets': [
                         { # MACD line
                         'label':f'MACD short period {indicatorsParams.macd_short_period} days, long period {indicatorsParams.macd_long_period} days',
                         'data':chartsData.MACD()[offset:],
                         'borderWidth':1,
                         'pointRadius':0,
                         'borderColor':indicatorsParams.macd_main_color,
                         },
                         { # MACD signal line
                         'label':f'MASD signal line {indicatorsParams.macd_signal_period} days',
                         'data':chartsData.MACDSignal()[offset:],
                         'borderWidth':1,
                         'pointRadius':0,
                         'borderColor':indicatorsParams.macd_signal_color,
                         }
                        
                         ]
        }
     
     chart_y_max = max(max(chartsData.MACD()[offset:]), max(chartsData.MACDSignal()[offset:]))
     chart_y_min = min(min(chartsData.MACD()[offset:]), min(chartsData.MACDSignal()[offset:]))
     grid_config = {
                    'color':indicatorsParams.default_color,
                    'lineWidth': 0.3,
                    'tickColor':indicatorsParams.default_color,
                    'borderColor':indicatorsParams.default_color,
                    }
     
     chartConfig = {
                    'type': 'line',
                    'data': data,
                    'options': {
                                   'responsive': True,
                                   'maintainAspectRatio': False,
                         'scales': {
                              'x':{               
                                   'ticks':{
                                        'type': 'time',
                                             'time': {
                                                       'unit': 'day', # Unit for the ticks (e.g., 'day', 'month', 'year')
                                                       'stepSize': 5  # Interval for the ticks (e.g., every 2 days)
                                              },
                                             'display': True, # Show x-axis labels
                                             'stepSize': 20,  # Set ticks interval 
                                             'color': indicatorsParams.default_color,
                                             'maxRotation': 0, #Prevents rotation
                                             'minRotation': 0  # Prevents rotation
                                             },
                                   'grid':grid_config
                                   }, 
                              'y': {                        
                                   'min': chart_y_min,
                                   'max': chart_y_max,
                                   'ticks': {'color': indicatorsParams.default_color},
                                   'grid': grid_config
                              },
                              'y1': {
                                   'position':'right',
                                   'min': chart_y_min,
                                   'max': chart_y_max,
                                   'ticks': { 'color': indicatorsParams.default_color },
                                   'grid': { 'display':False  }
                              }

                         },
                         'plugins': {
                                   'legend': {
                                             'display': True, # Show the legend
                                             'labels': {
                                                        'color': indicatorsParams.default_color, # Set the color for legend labels
                                                        'filter': ''
                                                       }
                                             },                                  
            }
        }
     }


     return chartConfig


@app.route("/get_symbol_data", methods = ['POST', 'GET'])
@login_required
def get_symbol_data():
     symbol_data = {}
     description = ""
     processed = "false"
     try:
          if request.method == "POST":
               request_data = request.get_json()
               symbol = request_data[0]["symbol"]
               smb = db.session.query(Symbol).filter(Symbol.symbol == symbol).first()  
               
               symbol_data['symbol'] = smb.symbol
               symbol_data['title'] = smb.title
               symbol_data['sector'] = smb.sector
               symbol_data['industry'] = smb.industry
               symbol_data['country'] = smb.country
               symbol_data['isfund'] = smb.isfund
               symbol_data['onemonthreturn'] = smb.onemonthreturn
               symbol_data['twomonthreturn'] = smb.twomonthreturn
               symbol_data['threemonthreturn'] = smb.threemonthreturn
               symbol_data['sixmonthreturn'] = smb.sixmonthreturn
               
               processed = "true"
               description = f"Data obtained for symbol {symbol}"
          else:
               description = "No 'POST' request obtained."
               
     except Exception as ex:
          description = ex.msg     
          symbol_data = {}
          processed = "false"

     results = {
                "processed": processed,
                "description":description,
                "symbol_data":symbol_data,
               } 
     return jsonify(results)

@app.route("/save_symbol_data", methods = ['POST', 'GET'])
@login_required
def save_symbol_data():
     description = ""
     try:
          if request.method == "POST":
               request_data = request.get_json()[0]
               symbol = request_data["symbol"]
               smb = db.session.query(Symbol).filter(Symbol.symbol == symbol).first()  
               isnewsymbol = False
               if smb is None:
                    isnewsymbol = True
                    smb = Symbol()
                    smb.symbol = symbol
                    db.session.add(smb)
               smb.title = request_data["title"]
               smb.sector = request_data["sector"]
               smb.industry = request_data["industry"]
               smb.country = request_data["country"]
               smb.isfund = request_data["isfund"]
               smb.onemonthreturn = str_to_float(request_data["onemonthreturn"])
               smb.twomonthreturn = str_to_float(request_data["twomonthreturn"])
               smb.threemonthreturn = str_to_float(request_data["threemonthreturn"])
               smb.sixmonthreturn = str_to_float(request_data["sixmonthreturn"])

               #symbol.ytd = float(request.form["inputYTD"])
               #symbol.oneyearreturn = float(request.form["inputOneYearReturn"])
               #symbol.threeyearreturn = float(request.form["inputThreeYearReturn"])
               #symbol.fiveyearreturn = float(request.form["inputFiveYearReturn"])
               #symbol.tenyearreturn = float(request.form["inputTenYearReturn"])
               #symbol.lifeoffundreturn = float(request.form["inputLifeOfFundReturn"])
               #symbol.netto = float(request.form["inputNetto"])
               #symbol.gross = float(request.form["inputGross"])
               #symbol.overall = float(request.form["inputOverall"])
 

               db.session.commit()
               processed = True
               description = f"Symbol data saved."
               
     except Exception as ex:
          db.session.rollback()
          
          if hasattr(ex, 'msg'):
               description = f"Symbol data not saved - {ex.msg}"
          if hasattr(ex, 'args'):
               description = f"Symbol data not saved - {ex.args}"
          processed = False
     
     results = {
               "processed": processed,
               "description": description,
               "isnewsymbol":isnewsymbol
               }
     return jsonify(results)

def str_to_float(value:str)->float:
     if value == "":
          return 0
     else:
          return float(value)
     
@app.route("/delete_symbol_data", methods = ['POST', 'GET'])
@login_required
def delete_symbol_data():
     description = ""
     try:
          if request.method == "POST":
               request_data = request.get_json()
               Symbol.query.filter_by(symbol = request_data["symbol"]).delete()
               db.session.commit()
               processed = True
               description = f"Symbol data deleted."
     except Exception as ex:
          db.session.rollback()
          msghdr = "Symbol data not deleted -"
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