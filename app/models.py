from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
from datetime import date
from config import InitialIndicatorsParams



#Set-ExecutionPolicy Unrestricted -Scope Process
 

db = SQLAlchemy()
# User's data
class User(UserMixin, db.Model):
    __tablename__ = 'user'
 
    id = db.Column(db.String(40), primary_key=True)
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

# List of simbols registered in the system
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
    sector = db.Column(db.String(30))
    industry = db.Column(db.String(30))
    country = db.Column(db.String(4))
    isfund = db.Column(db.Boolean)
    onemonthreturn = db.Column(db.Float)
    twomonthreturn = db.Column(db.Float)
    threemonthreturn = db.Column(db.Float)
    sixmonthreturn = db.Column(db.Float)
    ytd = db.Column(db.Float)
    oneyearreturn = db.Column(db.Float)
    threeyearreturn = db.Column(db.Float)
    fiveyearreturn = db.Column(db.Float)
    tenyearreturn = db.Column(db.Float)
    lifeoffundreturn = db.Column(db.Float)
    netto = db.Column(db.Float)
    gross = db.Column(db.Float)
    overall = db.Column(db.Float)
    
    def __init__(self, simbol:str = "", title:str = "", category:str = "",
                 sector:str = "", industry:str = "", country:str = "", isfund:bool = False,
                 onemonthreturn = 0.0, twomonthreturn = 0.0, threemonthreturn = 0.0, sixmonthreturn = 0.0,
                 ytd:float = 0.0,  oneyearreturn:float = 0.0, threeyearreturn:float = 0.0,
                 fiveyearreturn:float = 0.0, tenyearreturn:float = 0.0, lifeoffundreturn:float = 0.0,
                 netto:float = 0.0, gross:float = 0.0, overall:float = 0.0):
        self.simbol = simbol
        self.title = title
        self.category = category
        self.sector = sector
        self.industry = industry
        self.country = country
        self.isfund = isfund
        self.onemonthreturn = onemonthreturn
        self.twomonthreturn = twomonthreturn
        self.threemonthreturn = threemonthreturn
        self.sixmonthreturn = sixmonthreturn
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
                 {self.sector}:{self.industry}:{self.country}:{self.isfund}\
                 {self.onemonthreturn}:{self.twomonthreturn}:\
                 {self.threemonthreturn}:{self.sixmonthreturn}:{self.ytd}:\
                 {self.oneyearreturn}:{self.threeyearreturn}:{self.fiveyearreturn}:\
                 {self.tenyearreturn}:{self.lifeoffundreturn}:\
                 {self.netto}:{self.gross}:{self.overall}"
     
   # def to_dic(self):
   #     return {
   #             "simbol":self.simbol,
   #             "title":self.title,
   #             "category":self.category,
   #             "oneyearreturn":self.oneyearreturn,
   #             "threeyearreturn":self.threeyearreturn,
   #             "fiveyearreturn":self.fiveyearreturn,
   #             "tenyearreturn":self.tenyearreturn,
   #             "lifeoffundreturn":self.lifeoffundreturn,
   #             "netto":self.netto,
   #             "gross":self.gross,
   #             "overall":self.overall
   #             }

# Simbol's history data cache
class SimbolData(db.Model):
    __tablename__ = "simboldata"

    simbol = db.Column(db.String(10), primary_key=True)
    warning_level = db.Column(db.Integer)
    date_of_loading = db.Column(db.Date)             
    historical_data = db.Column(db.LargeBinary)
    last_price = db.Column(db.Float)

    
    def __init__(self, simbol:str, warning_level:int, date_of_loading:date, historical_data, last_price:float):
        self.simbol = simbol
        self.warning_level = warning_level
        self.date_of_loading = date_of_loading
        self.historical_data = historical_data
        self.last_price = last_price

    def __repr__(self):
        return f"simbol: {self.simbol}; warning_level: {self.warning_level}; date_of_loading: {self.date_of_loading}; historical_data: BLOB"

# List of simbols selected by user to include 
# in portfolio, watchlist or shortlist 
class UserSimbol(db.Model):  
    __tablename__ = 'usersimbol'

    simbol = db.Column(db.String(10), primary_key=True)
    userid = db.Column(db.String(40), primary_key=True)
    listtype  = db.Column(db.Integer)
    warning_level = db.Column(db.Integer)
    calculation_date = db.Column(db.Date)

    # Listtypes
    #   0 - unselected
    #   1 - portfolio
    #   2 - watchlist
    #   3 - shortlist
    
    def __init__(self, simbol:str, userid:str, listtype:int,
                 warning_level:int = 0, calculation_date:date = date.today()):
             
        self.simbol = simbol
        self.userid = userid
        self.listtype = listtype
        self.warning_level = warning_level
        self.calculation_date = calculation_date
    
    def __repr__(self):
        return f"simbol: {self.simbol}; userid: {self.userid}; list type: {self.listtype};\
              warning_level: {self.warning_level}; calculation date: {self.calculation_date}"

# Values of indicators parameters that user
# defined for each simbol in order to calculate indicators    
class IndicatorsParams(db.Model):
    __tablename__ = 'indicatorsparams'

    userid = db.Column(db.String(40), primary_key=True)
    simbol = db.Column(db.String(10), primary_key=True)
    
    width  = db.Column(db.Integer)
    heigh  = db.Column(db.Integer)
    
    history_length = db.Column(db.Integer)

    default_color = db.Column(db.String(9))
    background_color   = db.Column(db.String(9))
    
    ma_first_period = db.Column(db.Integer)
    ma_first_type  = db.Column(db.String(4)) # SMA EMA e.s.on
    ma_first_color = db.Column(db.String(9))
    show_ma_first  = db.Column(db.Boolean)

    ma_second_period = db.Column(db.Integer)
    ma_second_type  = db.Column(db.String(4)) # SMA EMA e.s.on
    ma_second_color = db.Column(db.String(9))
    show_ma_second  = db.Column(db.Boolean)

    ma_third_period = db.Column(db.Integer)
    ma_third_type  = db.Column(db.String(4)) # SMA EMA e.s.on
    ma_third_color = db.Column(db.String(9))
    show_ma_third  = db.Column(db.Boolean)

    ma_volume_color = db.Column(db.String(9))
    show_volume  = db.Column(db.Boolean)
    
    rsi_period = db.Column(db.Integer)
    rsi_color = db.Column(db.String(9))
    show_rsi  = db.Column(db.Boolean)

    macd_short_period = db.Column(db.Integer)
    macd_long_period = db.Column(db.Integer)
    macd_signal_period = db.Column(db.Integer)
    macd_main_color = db.Column(db.String(9))
    macd_signal_color = db.Column(db.String(9))
    show_macd  = db.Column(db.Boolean)

    bollingerband_period = db.Column(db.Integer)
    bollingerband_probability = db.Column(db.Integer) # in percents
    bollingerband_color = db.Column(db.String(9))
    bollingerband_opacity = db.Column(db.Float)
    show_bollingerband  = db.Column(db.Boolean)

    def __init__(self, userid:str, simbol:str, 
                 
                width:int,
                heigh:int,
                history_length:int,
                default_color:str,
                background_color:str,
    
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

        self.default_color = default_color
        self.background_color = background_color
    
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
        default_color: {self.default_color};\
        background_color: {self.background_color};\
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

    def __eq__(self, other):  
        if isinstance(other, IndicatorsParams):
            if self.userid == other.userid and\
                self.simbol == other.simbol and\
                self.width  == other.width and\
                self.heigh  == other.heigh and\
                self.history_length == other.history_length and\
                self.default_color == other.default_color and\
                self.background_color == other.background_color and\
                self.ma_first_period == other.ma_first_period and\
                self.ma_first_type  == other.ma_first_type and\
                self.ma_first_color == other.ma_first_color and\
                self.show_ma_first == other.show_ma_first and\
                self.ma_second_period == other.ma_second_period and\
                self.ma_second_type  == other.ma_second_type and\
                self.ma_second_color == other.ma_second_color and\
                self.show_ma_second == other.show_ma_second and\
                self.ma_third_period == other.ma_third_period and\
                self.ma_third_type  == other.ma_third_type and\
                self.ma_third_color == other.ma_third_color and\
                self.show_ma_third == other.show_ma_third and\
                self.ma_volume_color == other.ma_volume_color and\
                self.show_volume == other.show_volume and\
                self.rsi_period == other.rsi_period and\
                self.rsi_color == other.rsi_color and\
                self.show_rsi == other.show_rsi and\
                self.macd_short_period == other.macd_short_period and\
                self.macd_long_period == other.macd_long_period and\
                self.macd_signal_period == other.macd_signal_period and\
                self.macd_main_color == other.macd_main_color and\
                self.macd_signal_color == other.macd_signal_color and\
                self.show_macd == other.show_macd and\
                self.bollingerband_period == other.bollingerband_period and\
                self.bollingerband_probability == other.bollingerband_probability and\
                self.bollingerband_color == other.bollingerband_color and\
                self.bollingerband_opacity == other.bollingerband_opacity and\
                self.show_bollingerband == other.show_bollingerband:
                return True 
            else:
                return False
        else:
            return False

    def is_equal(self, other)->bool:
        if  self.userid == other.userid and\
            self.simbol == other.simbol and\
            self.width  == other.width and\
            self.heigh  == other.heigh and\
            self.history_length == other.history_length and\
            self.default_color == other.default_color and\
            self.background_color == other.background_color and\
            self.ma_first_period == other.ma_first_period and\
            self.ma_first_type  == other.ma_first_type and\
            self.ma_first_color == other.ma_first_color and\
            self.show_ma_first == other.show_ma_first and\
            self.ma_second_period == other.ma_second_period and\
            self.ma_second_type  == other.ma_second_type and\
            self.ma_second_color == other.ma_second_color and\
            self.show_ma_second == other.show_ma_second and\
            self.ma_third_period == other.ma_third_period and\
            self.ma_third_type  == other.ma_third_type and\
            self.ma_third_color == other.ma_third_color and\
            self.show_ma_third == other.show_ma_third and\
            self.ma_volume_color == other.ma_volume_color and\
            self.show_volume == other.show_volume and\
            self.rsi_period == other.rsi_period and\
            self.rsi_color == other.rsi_color and\
            self.show_rsi == other.show_rsi and\
            self.macd_short_period == other.macd_short_period and\
            self.macd_long_period == other.macd_long_period and\
            self.macd_signal_period == other.macd_signal_period and\
            self.macd_main_color == other.macd_main_color and\
            self.macd_signal_color == other.macd_signal_color and\
            self.show_macd == other.show_macd and\
            self.bollingerband_period == other.bollingerband_period and\
            self.bollingerband_probability == other.bollingerband_probability and\
            self.bollingerband_color == other.bollingerband_color and\
            self.bollingerband_opacity == other.bollingerband_opacity and\
            self.show_bollingerband == other.show_bollingerband:
            return True 
        else:
            return False

# List of users activities
# 0 - Buy stock
# 1 - Sell stock
# 3 - Deposit money to account
# 4 - Withdraw money from account   
class Operation(db.Model):  
    __tablename__ = 'operation'
    id = db.Column(db.Integer, primary_key=True, nullable = False, autoincrement=True)
    userid = db.Column(db.String(40), nullable = False)
    account = db.Column(db.String(15), nullable = False)
    simbol = db.Column(db.String(10), nullable = False)
    date = db.Column(db.Date, nullable = False)
    type = db.Column(db.Integer, nullable = False)
    price  = db.Column(db.Float, nullable = False)
    quantity = db.Column(db.Float, nullable = False)
    todayprice  = db.Column(db.Float, nullable = False)
    
    def __init__(self,  userid:str, account:str, simbol:str, 
                 date,  type:int = 0,
                 price:float = 0.0, quantity:float = 0.0, todayprice:float = 0.0):
        
        self.userid = userid
        self.account = account
        self.simbol = simbol
        self.date = date
        self.type = type # buy or sell
        self.price = price
        self.quantity = quantity
        self.todayprice = todayprice
        
    def __repr__(self):
        return f"id: {self.id}; simbol: {self.simbol}; userid: {self.userid}; account: {self.account};\
                date: {self.date}; type: {self.type};\
                price: {self.price}; quantity: {self.quantity};\
                todayprice: {self.todayprice};"
    
class Account(db.Model):
    __tablename__ = 'account'
    userid = db.Column(db.String(40), primary_key=True)
    name = db.Column(db.String(15), primary_key=True)
    balance = db.Column(db.Float)
    currency = db.Column(db.String(3))
    
    def __init__(self, userid:str, name:str, balance:float, currency:str):
        self.userid = userid
        self.name = name
        self.balance = balance
        self.currency = currency
        
    def __repr__(self):
        return f"userid: {self.userid}; account: {self.name}; balance: {self.balance}; currency: {self.currency}"
    
def get_default_indicators_params()->IndicatorsParams:

   params = IndicatorsParams(
                userid = InitialIndicatorsParams.USERID,
                simbol =  InitialIndicatorsParams.SIMBOL,

                width = InitialIndicatorsParams.WIDTH,
                heigh = InitialIndicatorsParams.HEIGH,

                history_length = InitialIndicatorsParams.HISTORY_LENGTH,

                default_color = InitialIndicatorsParams.DEFAULT_COLOR,
                background_color = InitialIndicatorsParams.BACKGROUND_COLOR,
    
                ma_first_period = InitialIndicatorsParams.MA_FIRST_PERIOD,
                ma_first_type = InitialIndicatorsParams.MA_FIRST_TYPE,
                ma_first_color = InitialIndicatorsParams.MA_FIRST_COLOR,
                show_ma_first = InitialIndicatorsParams.SHOW_MA_FIRST,

                ma_second_period = InitialIndicatorsParams.MA_SECOND_PERIOD,
                ma_second_type = InitialIndicatorsParams.MA_SECOND_TYPE,
                ma_second_color = InitialIndicatorsParams.MA_SECOND_COLOR,
                show_ma_second = InitialIndicatorsParams.SHOW_MA_SECOND,

                ma_third_period = InitialIndicatorsParams.MA_THIRD_PERIOD,
                ma_third_type = InitialIndicatorsParams.MA_THIRD_TYPE,
                ma_third_color = InitialIndicatorsParams.MA_THIRD_COLOR,
                show_ma_third = InitialIndicatorsParams.SHOW_MA_THIRD,
                
                ma_volume_color = InitialIndicatorsParams.VOLUME_COLOR,
                show_volume = InitialIndicatorsParams.SHOW_VOLUME,
    
                rsi_period = InitialIndicatorsParams.RSI_PERIOD,
                rsi_color = InitialIndicatorsParams.RSI_COLOR,
                show_rsi = InitialIndicatorsParams.SHOW_RSI,

                macd_short_period = InitialIndicatorsParams.MACD_SHORT_PERIOD,
                macd_long_period = InitialIndicatorsParams.MACD_LONG_PERIOD,
                macd_signal_period = InitialIndicatorsParams.MACD_SIGNAL_PERIOD,
                macd_main_color = InitialIndicatorsParams.MACD_MAIN_COLOR,
                macd_signal_color = InitialIndicatorsParams.MACD_SIGNAL_COLOR,
                show_macd = InitialIndicatorsParams.SHOW_MACD,

                bollingerband_period = InitialIndicatorsParams.BOLLINGERBAND_PERIOD,
                bollingerband_probability = InitialIndicatorsParams.BOLLINGERBAND_PROBABILITY,
                bollingerband_color = InitialIndicatorsParams.BOLLINGERBAND_COLOR,
                bollingerband_opacity = InitialIndicatorsParams.BOLLINGERBAND_OPACITY,
                show_bollingerband = InitialIndicatorsParams.SHOW_BOLINGERBAND
   )
   
   return params

def get_user_indicators_params(simbol:str, userid:str)->IndicatorsParams:
    # Try to get params for defined user and simbol
    user_indicators_params  = db.session\
                                .query(IndicatorsParams)\
                                .filter(IndicatorsParams.userid == userid,
                                        IndicatorsParams.simbol == simbol)\
                                .first()   
    if user_indicators_params == None:
        # if set of parameters not found try to get default parameters for that user 
        user_indicators_params  = db.session\
                                .query(IndicatorsParams)\
                                .filter(IndicatorsParams.userid == userid,
                                        IndicatorsParams.simbol == "-----")\
                                .first()
        if user_indicators_params == None:   
            # if default set of parameters for that user not found
            # use system default set of parameters 
            user_indicators_params = get_default_indicators_params()
    
    return user_indicators_params