from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager


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
     
class UserSimbol(db.Model):  
    __tablename__ = 'usersimbol'

    simbol = db.Column(db.String(10), primary_key = True)
    userid = db.Column(db.String(100), primary_key=True)
    listtype  = db.Column(db.Integer)
    
    def __init__(self, simbol:str, userid:str, listtype:str):
        self.simbol = simbol
        self.iserid = userid
        self.listtype = listtype

    def __repr__(self):
        return f"simbol: {self.simbol}; userid: {self.userid}; list type: {self.listtype} "




