
#Set-ExecutionPolicy Unrestricted -Scope Process

# App starts from this file

# import variable app from pakage app
from app import app

if __name__ == "__main__":
    app.run()