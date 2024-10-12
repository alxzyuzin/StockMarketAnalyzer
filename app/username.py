from flask_login import current_user

def currentusername():
    if current_user.is_authenticated:
        return current_user.username
    else:
        return None