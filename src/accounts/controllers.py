from flask import request, jsonify
import uuid
from .. import db
from .. import login_manager
from .models import Account
from flask_login import login_user, logout_user
from .. import bcrypt
from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import current_user


# ----------------------------------------------- #

# Query Object Methods => https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query
# Session Object Methods => https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session
# How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522

def list_all_accounts_controller():
    accounts = Account.query.all()
    response = []
    for account in accounts: response.append(account.toDict())
    return jsonify({"count":len(response),"list": response})

def create_account_controller():
    request_form = request.form.to_dict()
    id = str(uuid.uuid4())
    
    username = request_form['username']
    email = request_form['email']
    password = request_form['password']
    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    existing_user = Account.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    
    existing_user = Account.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400


    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_account = Account(
                          id             = id,
                          email          = request_form['email'],
                          username       = request_form['username'],
                        #   dob            = request_form['dob'],
                          country        = request_form['country'],
                          phone_number   = request_form['phone_number'],
                          password       = hashed_password,
                          role = request_form['role'] or None, 
                          culture = request_form['culture'] or None
                          )
    db.session.add(new_account)
    db.session.commit()

    response = Account.query.get(id).toDict()
    return jsonify(response),201

def retrieve_account_controller(account_id):
    response = Account.query.get(account_id).toDict()
    return jsonify(response)

def update_account_controller(account_id):
    request_form = request.form.to_dict()
    account = Account.query.get(account_id)

    account.email        = request_form['email']
    account.username     = request_form['username']
    account.dob          = request_form['dob']
    account.country      = request_form['country']
    account.phone_number = request_form['phone_number']
    account.role = request_form['role'] or None, 
    account.culture = request_form['culture'] or None
    db.session.commit()

    response = Account.query.get(account_id).toDict()
    return jsonify(response)

def delete_account_controller(account_id):
    Account.query.filter_by(id=account_id).delete()
    db.session.commit()

    return ('Account with Id "{}" deleted successfully!').format(account_id)







def login():
    info = request.form.to_dict()
    username = info.get('username', 'guest')
    password = info.get('password', '')
    user = Account.query.filter_by(username=username).first()
    
    print(user, username, password)
    print(bcrypt.generate_password_hash(password).decode('utf-8'))

    if user and bcrypt.check_password_hash(user.password, password):
    # Password is correct
        login_user(user)
        return jsonify(user.to_json())
    else:
        # Password is incorrect
        return jsonify({"status": 401,
                        "reason": "Username or Password Error"})

        

@login_manager.user_loader
def load_user(user_id):
    return Account.query.filter_by(id=user_id).first()



def logout():
    logout_user()
    return redirect(url_for('index'))




def CheckPermissionsFunc():
    if  not current_user.is_authenticated:
        abort(403)
    
    if  current_user.role == 'admin':
        pass
        #todo must check every reqest role access managment


def OnlineUser():
    user_data = {
        'id': current_user.id,
        'username': current_user.username,
        'isAdmin': current_user.is_admin(),
        'loggedIn': current_user.is_authenticated(),
        'culture':current_user.get_culture()
    }
    return jsonify(user_data), 200



