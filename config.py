class Config(object):
    DATABASE_FILE   = "app/database/appdata.db"
    USER_NAME       = "ALX.ZYUZIN@GMAIL.COM"
    USER_PASSWORD   = "PASSWORD"
    #Secret key used for session encryption and other security features.
    SECRET_KEY      = "IkqQWV907tMmatKFsPccU6kk5L_mDfWzPUaji_3vWRk"
    #Secret key used for fetching data from https://financialmodelingprep.com/api.
    API_KEY         = "VmvqJNpPV26D4SP554R2BkjnrCuJsJ2m"
    #The URI for the database to be used with SQLAlchemy.
    SQLALCHEMY_DATABASE_URI = "sqlite:///appdata.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
	#The type of session storage to be used (e.g. ‘filesystem’, ‘redis’, ‘memcached’, etc.).    
    SESSION_TYPE = "filesystem"
    #The lifetime of a permanent session in seconds. Default 31 days	
    PERMANENT_SESSION_LIFETIME = 36000

    #DEBUG	False	Enables or disables debug mode.
    #TESTING	False	Enables or disables testing mode.
    #SERVER_NAME	None	The hostname and port number of the server.
    #SESSION_COOKIE_NAME	‘session’	The name of the session cookie.
    #SESSION_COOKIE_SECURE	False	Enables or disables secure session cookies (HTTPS).
    #SESSION_COOKIE_HTTPONLY	True	Enables or disables httponly session cookies (cannot be accessed by JavaScript).	
    #SQLALCHEMY_TRACK_MODIFICATIONS	True	Enables or disables modification tracking for SQLAlchemy.
    #UPLOAD_FOLDER	None	The folder where uploaded files are stored.
    #MAX_CONTENT_LENGTH	None	The maximum allowed size for uploaded files.
    #JSONIFY_PRETTYPRINT_REGULAR	False	Enables or disables pretty-printing of JSON responses.
    #JSON_SORT_KEYS	True	Enables or disables sorting of keys in JSON responses.
    #JSONIFY_MIMETYPE	‘application/json’	The mimetype used for JSON responses.
    #CORS_*	None	Various configuration options for Cross-Origin Resource Sharing (CORS).





class InitialIndicatorsParams(object):
    USERID = ""
    SIMBOL = "-----"

    WIDTH = 800
    HEIGH = 600

    BACKGROUND_COLOR = "#F0F0F0"
    DEFAULT_COLOR = "#1F1F1F"

    HISTORY_LENGTH = 250
    DAILY_PRICES_COLOR = "#AAAAAA"

    MA_FIRST_PERIOD = 4
    MA_FIRST_TYPE = "sma"
    MA_FIRST_COLOR = '#FFFF00'
    SHOW_MA_FIRST = True

    MA_SECOND_PERIOD = 9
    MA_SECOND_TYPE = "ema"
    MA_SECOND_COLOR = '#00FF00'
    SHOW_MA_SECOND = True

    MA_THIRD_PERIOD = 18
    MA_THIRD_TYPE = "ema"
    MA_THIRD_COLOR = '#0000FF'
    SHOW_MA_THIRD = True

    VOLUME_COLOR = "#0000FF"
    SHOW_VOLUME = True

    RSI_PERIOD = 20
    RSI_COLOR = "#00FF00"    
    SHOW_RSI = True    
    
    MACD_SHORT_PERIOD = 12
    MACD_LONG_PERIOD = 26
    MACD_SIGNAL_PERIOD = 9 
    MACD_MAIN_COLOR = "#0000FF"
    MACD_SIGNAL_COLOR = "#FF0000"    
    SHOW_MACD = True
    
    BOLLINGERBAND_PERIOD = 20
    BOLLINGERBAND_PROBABILITY = 90
    BOLLINGERBAND_COLOR = "#00FF00"
    BOLLINGERBAND_OPACITY = 0.2
    SHOW_BOLINGERBAND = True
    