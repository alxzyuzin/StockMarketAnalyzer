from app import app
from app.models import db, User, Simbol, UserSimbol
import argparse
import uuid


 
    
def reset_user_name(email:str, name:str):
    with app.app_context():
        user = db.session.query(User).filter(User.email == email).first()
        user.name = name
        db.session.commit()
        user = db.session.query(User).filter(User.email == email).first()
        print(user)
    return


def reset_user_password(email:str, password:str):
    with app.app_context():
        user = db.session.query(User).filter(User.email == email).first()
        user.set_password(password)
        db.session.commit()
        user = db.session.query(User).filter(User.email == email).first()
        print(user)
    return

def dbinit():
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()

    print("Database reinitialized.")
    return            
        #for aw in ArtworksData:
        #    db.session.add(ArtworkModel(aw['filename'], aw['title'], aw['description'], aw['width'], aw['height'], aw['price'], aw['status']))
        
        # Check if data loaded
        #users = db.session.query(UserModel).all()
        #artworks = db.session.query(ArtworkModel).all()
    return

def add_admin(admin_email = 'alx.zyuzin@gmail.com'):
    with app.app_context():
        user = db.session.query(User).filter(User.email == admin_email).first()
        if user == None:
            admin =  User(id = str(uuid.uuid4()), email = admin_email,
                            username = 'Alexander', password = 'password', admin = True)
            db.session.add(admin)
            db.session.commit()
            user = db.session.query(User).filter(User.email == admin_email).first()
        print(user)
    return

def loadsimboldatafromscv(filename:str):
    
    with app.app_context():
               # CSV file structure        
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
        try:
            with open(filename, 'r') as file:
                file.readline()
                file.readline()
                for line in file:
                    line = line.replace('ï¿½',' ')
                    line = line.replace("%","")
                    line = line.replace("--","0.0")
                    linedata = line.split(',')
                    
                    smb = Simbol(simbol = linedata[0],
                                title = linedata[1],
                                category = linedata[2],
                                ytd = float(linedata[3]),
                                oneyearreturn =  float(linedata[4]),
                                threeyearreturn =  float(linedata[5]),
                                fiveyearreturn =  float(linedata[6]),
                                tenyearreturn =  float(linedata[7]),
                                lifeoffundreturn =  float(linedata[8]),
                                netto = float(linedata[9]),
                                gross = float(linedata[10]),
                                overall = float(linedata[11])
                    )
                    db.session.add(smb)
        
        except FileNotFoundError:
            print(f"The file {filename} does not exist.")   
        except PermissionError:
            print("You do not have permission to access this file.")  
        except IsADirectoryError:
            print("The specified path is a directory, not a file.")
        except IOError:
            print("An I/O error occurred.")
        
        db.session.commit()
        simbols = db.session.query(Simbol).all()
        for simbol in simbols:
            print(simbol)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--init", type=str)
    parser.add_argument("-f", "--file", type=str)
    parser.add_argument("-n", "--name", type=str)
    parser.add_argument("-u", "--adduser", type=str)
    
    args = parser.parse_args()
    db.init_app(app)
    
    if args.init == 'y':
        dbinit()

    if args.file != None:
        loadsimboldatafromscv(args.file)

    if args.adduser != None:
        add_admin() 
    


if __name__ == "__main__":
    main()
