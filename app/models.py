from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
from datetime import date



#Set-ExecutionPolicy Unrestricted -Scope Process
 

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
 
    id = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String())
    admin = db.Column(db.Boolean)
 
    def __init__(self, id:str, email:str, username:str, password:str, admin = False):
        self.id = id
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.admin = admin
        
    def __repr__(self):
        return f"{self.id}:{self.email}:{self.username}:{self.password_hash}"
 
    def set_password(self,password:str):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self,password:str):
        return check_password_hash(self.password_hash,password)

class Simbol(db.Model):
    __tablename__ = 'simbol'
          
        #  0 - Simbol                  string
        #  1 - Name                    string
        #  2 - Morningstar Category    string
        #  3 - YTD # (Daily)           float
        #  4 - 1 Yr                    float
        #  5 - 3 Yr                    float
        #  6 - 5 Yr                    float
        #  7 - 10 Yr                   float
        #  8 - Life of Fund            float
        #  9 - Net †                   float
        # 10 - Gross ‡                 float
        # 11 - Overall                 float
    
    simbol = db.Column(db.String(10), primary_key = True)                         
    title = db.Column(db.String(100))
    category = db.Column(db.String(20))
    ytd = db.Column(db.Float)
    oneyearreturn = db.Column(db.Float)
    threeyearreturn = db.Column(db.Float)
    fiveyearreturn = db.Column(db.Float)
    tenyearreturn = db.Column(db.Float)
    lifeoffundreturn = db.Column(db.Float)
    netto = db.Column(db.Float)
    gross = db.Column(db.Float)
    overall = db.Column(db.Float)
    
    #gallery = db.relationship('GalleryModel', backref="artwork")
    
    def __init__(self, simbol:str, title:str, category:str, ytd:float,
                 oneyearreturn:float, threeyearreturn:float, fiveyearreturn:float, tenyearreturn:float,
                 lifeoffundreturn:float, netto:float, gross:float, overall:float):
        self.simbol = simbol
        self.title = title
        self.category = category
        self.ytd = ytd
        self.oneyearreturn = oneyearreturn
        self.threeyearreturn = threeyearreturn
        self.fiveyearreturn = fiveyearreturn
        self.tenyearreturn = tenyearreturn
        self.lifeoffundreturn = lifeoffundreturn
        self.netto = netto
        self.gross = gross
        self.overall = overall
 
    def __repr__(self):
        return f"{self.simbol}:{self.title}:{self.category}:\
                 {self.oneyearreturn}:{self.threeyearreturn}:{self.fiveyearreturn}\
                 {self.tenyearreturn}:{self.lifeoffundreturn}:\
                 {self.netto}:{self.gross}:{self.overall}"
     
    def to_dic(self):
        return {
                "simbol":self.simbol,
                "title":self.title,
                "category":self.category,
                "oneyearreturn":self.oneyearreturn,
                "threeyearreturn":self.threeyearreturn,
                "fiveyearreturn":self.fiveyearreturn,
                "tenyearreturn":self.tenyearreturn,
                "lifeoffundreturn":self.lifeoffundreturn,
                "netto":self.netto,
                "gross":self.gross,
                "overall":self.overall
                }

class SimbolData(db.Model):
    __tablename__ = "simboldata"

    simbol = db.Column(db.String(10), primary_key=True)
    date_of_loading = db.Column(db.Date)             
    historical_data = db.Column(db.LargeBinary)

    def __init(self, simbol:str):
        self.simbol = simbol
        
    def __init__(self, simbol:str, warning_level:int, date_of_loading:date, historical_data):
        self.simbol = simbol
        self.warning_level = warning_level
        self.date_of_loading = date_of_loading
        self.historical_data = historical_data

    def __repr__(self):
        return f"simbol: {self.simbol}; warning_level: {self.warning_level}; date_of_loading: {self.date_of_loading}; historical_data: BLOB"

class UserSimbol(db.Model):  
    __tablename__ = 'usersimbol'

    simbol = db.Column(db.String(10), primary_key=True)
    userid = db.Column(db.String(100), primary_key=True)
    listtype  = db.Column(db.Integer)
    warning_level = db.Column(db.Integer)
    calculation_date = db.Column(db.Date)
    plots_image = db.Column(db.Text)

    # Listtypes
    #   0 - unselected
    #   1 - portfolio
    #   2 - watchlist
    
    def __init__(self, simbol:str, userid:str, listtype:int,
                 warning_level:int = 0, calculation_date:date = date.today(), 
                 plots_image:str = ""):
        self.simbol = simbol
        self.userid = userid
        self.listtype = listtype
        self.warning_level = warning_level
        self.calculation_date = calculation_date
        self.plots_image = plots_image

    def __repr__(self):
        return f"simbol: {self.simbol}; userid: {self.userid}; list type: {self.listtype};\
              warning_level: {self.warning_level}; calculation date: {self.calculation_date}"
    
class IndicatorsParams(db.Model):
    __tablename__ = 'indicatorsparams'

    userid = db.Column(db.String(100), primary_key=True)
    simbol = db.Column(db.String(10), primary_key=True)
    
    width  = db.Column(db.Integer)
    heigh  = db.Column(db.Integer)
    
    history_length = db.Column(db.Integer)

    daily_prices_color = db.Column(db.String(6))
    
    ma_first_period = db.Column(db.Integer)
    ma_first_type  = db.Column(db.String(4)) # SMA EMA e.s.on
    ma_first_color = db.Column(db.String(6))
    show_ma_first  = db.Column(db.Boolean)

    ma_second_period = db.Column(db.Integer)
    ma_second_type  = db.Column(db.String(4)) # SMA EMA e.s.on
    ma_second_color = db.Column(db.String(6))
    show_ma_second  = db.Column(db.Boolean)

    ma_third_period = db.Column(db.Integer)
    ma_third_type  = db.Column(db.String(4)) # SMA EMA e.s.on
    ma_third_color = db.Column(db.String(6))
    show_ma_third  = db.Column(db.Boolean)

    ma_volume_color = db.Column(db.String(6))
    show_volume  = db.Column(db.Boolean)
    
    rsi_period = db.Column(db.Integer)
    rsi_color = db.Column(db.String(6))
    show_rsi  = db.Column(db.Boolean)

    macd_short_period = db.Column(db.Integer)
    macd_long_period = db.Column(db.Integer)
    macd_signal_period = db.Column(db.Integer)
    macd_main_color = db.Column(db.String(6))
    macd_signal_color = db.Column(db.String(6))
    show_macd  = db.Column(db.Boolean)

    bollingerband_period = db.Column(db.Integer)
    bollingerband_probability = db.Column(db.Integer) # in percents
    bollingerband_color = db.Column(db.String(6))
    bollingerband_opacity = db.Column(db.Float)
    show_bollingerband  = db.Column(db.Boolean)

    def __init__(self, userid:str, simbol:str, 
                 
                width:int,
                heigh:int,
                history_length:int,
                daily_prices_color:str,
    
                ma_first_period:int,
                ma_first_type:str,
                ma_first_color:str,
                show_ma_first:bool,

                ma_second_period:int,
                ma_second_type:str,
                ma_second_color:str,
                show_ma_second:bool,

                ma_third_period:int,
                ma_third_type:str,
                ma_third_color:str,
                show_ma_third:bool,
                
                ma_volume_color:str,
                show_volume:bool,
    
                rsi_period:int,
                rsi_color:str,
                show_rsi:bool,

                macd_short_period:int,
                macd_long_period:int,
                macd_signal_period:int,
                macd_main_color:str,
                macd_signal_color:str,
                show_macd:bool,

                bollingerband_period:int,
                bollingerband_probability:int,
                bollingerband_color:str,
                bollingerband_opacity:float,
                show_bollingerband:bool
            ):
        
        self.userid = userid
        self.simbol = simbol
        self.width  = width
        self.heigh  = heigh

        self.history_length = history_length

        self.daily_prices_color = daily_prices_color
    
        self.ma_first_period = ma_first_period
        self.ma_first_type  = ma_first_type
        self.ma_first_color = ma_first_color
        self.show_ma_first = show_ma_first

        self.ma_second_period = ma_second_period
        self.ma_second_type  = ma_second_type
        self.ma_second_color = ma_second_color
        self.show_ma_second = show_ma_second

        self.ma_third_period = ma_third_period
        self.ma_third_type  = ma_third_type
        self.ma_third_color = ma_third_color
        self.show_ma_third = show_ma_third

        self.ma_volume_color = ma_volume_color
        self.show_volume = show_volume
    
        self.rsi_period = rsi_period
        self.rsi_color = rsi_color
        self.show_rsi = show_rsi

        self.macd_short_period = macd_short_period
        self.macd_long_period = macd_long_period
        self.macd_signal_period = macd_signal_period
        self.macd_main_color = macd_main_color
        self.macd_signal_color = macd_signal_color
        self.show_macd = show_macd

        self.bollingerband_period = bollingerband_period
        self.bollingerband_probability = bollingerband_probability
        self.bollingerband_color = bollingerband_color
        self.bollingerband_opacity = bollingerband_opacity
        self.show_bollingerband = show_bollingerband

    def __repr__(self):
        return f"userid: {self.userid};\
        simbol: {self.simbol};\
        width: {self.width};\
        heigh: {self.heigh};\
        history_length: {self.history_length};\
        daily_prices_color: {self.daily_prices_color};\
        ma_first_period: {self.ma_first_period};\
        ma_first_type: {self.ma_first_type};\
        ma_first_color: {self.ma_first_color};\
        show_ma_first: {self.show_ma_first};\
        ma_second_period: {self.ma_second_period};\
        ma_second_type: {self.ma_second_type};\
        ma_second_color: {self.ma_second_color};\
        show_ma_second: {self.show_ma_second};\
        ma_third_period: {self.ma_third_period};\
        ma_third_type: {self.ma_third_type};\
        ma_third_color: {self.ma_third_color};\
        show_ma_third: {self.show_ma_third}\
        ma_volume_color: {self.ma_volume_color};\
        show_volume: {self.show_volume};\
        rsi_period: {self.rsi_period};\
        rsi_color: {self.rsi_color};\
        show_rsi: {self.show_rsi};\
        macd_short_period: {self.macd_short_period};\
        macd_long_period: {self.macd_long_period};\
        macd_signal_period: {self.macd_signal_period};\
        macd_main_color: {self.macd_main_color};\
        macd_signal_color: {self.macd_signal_color};\
        show_macd: {self.show_macd};\
        bollingerband_period: {self.bollingerband_period};\
        bollingerband_probability: {self.bollingerband_probability};\
        bollingerband_color: {self.bollingerband_color};\
        bollingerband_opacity: {self.bollingerband_opacity};\
        show_bollingerband: {self.show_bollingerband};"

    def get_offset(self):
        return max(
            self.ma_first_period,
            self.ma_second_period,
            self.ma_third_period,
            self.rsi_period,
            self.macd_short_period,
            self.macd_long_period,
            self.macd_signal_period,
            self.bollingerband_period
        )

class Operation(db.Model):  
    __tablename__ = 'operation'
    rowid = db.Column(db.Integer, primary_key=True, nullable = False)
    userid = db.Column(db.String(100), nullable = False)
    simbol = db.Column(db.String(10), nullable = False)
    operation_date = db.Column(db.Date, nullable = False)
    operation_type = db.Column(db.String(4), nullable = False)
    price  = db.Column(db.Float, nullable = False)
    amount = db.Column(db.Float, nullable = False)
    
    def __init__(self,  userid:str, simbol:str, 
                 operation_date:date,  operation_type:str,
                 price:float, amount:float):
        self.userid = userid
        self.simbol = simbol
        self.operation_date = operation_date
        self.operation_type = operation_type # buy or sell
        self.price = price
        self.amount = amount
        

    def __repr__(self):
        return f"simbol: {self.simbol}; userid: {self.userid};\
                operation date: {self.operation_date}\
                operationtype: {self.operation_type}\
                price: {self.price}; amount: {self.amount} "