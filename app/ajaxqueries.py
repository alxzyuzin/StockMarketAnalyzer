from app import app
from flask import render_template, redirect, request, session, url_for, jsonify
from flask_login import current_user, user_logged_out, login_user, logout_user, login_required

from app.models import ( db, 
                        Simbol, User, UserSimbol, IndicatorsParams, SimbolData,
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