from flask import request
from flask_login import login_required
from ..app import app
from .controllers import * #list_all_accounts_controller, create_account_controller, retrieve_account_controller, update_account_controller, delete_account_controller


allowed_list = ['/product','/product/<product_code>','/login','/admin/storage','/product/search/all','/product/search']

@app.route("/admin/account", methods=['GET', 'POST'])
@login_required
def list_create_accounts():
    if request.method == 'GET': return list_all_accounts_controller()
    if request.method == 'POST': return create_account_controller_admin()
    else: return 'Method is Not Allowed'

@app.route("/admin/account/<account_id>", methods=['GET', 'PUT', 'DELETE'])
def retrieve_update_destroy_accounts(account_id):
    if request.method == 'GET': return retrieve_account_controller(account_id)
    if request.method == 'PUT': return update_account_controller(account_id)
    if request.method == 'DELETE': return delete_account_controller(account_id)
    else: return 'Method is Not Allowed'



@app.route('/login', methods=['POST'])
def AuthApi():
    print("login")
    if request.method in ["POST"]:return login()
    else: return 'Method is Not Allowed'

@app.route('/register', methods=['POST'])
def Register():
    if request.method == "POST":return create_account_controller()
    else: return 'Method is Not Allowed'

@app.route('/logout')
def logoutUser():
    if request.method in ["GET","POST"]:return logout()
    else: return 'Method is Not Allowed'


@app.route('/current_user', methods=['GET'])
@login_required
def currentUser():
    if request.method == "GET":return OnlineUser()
    else: return 'Method is Not Allowed'

# @app.before_request
# def check_Permission():
    # print('in check permission',request.url,request.method,request.cookies)
    # print(request.url_root,request.url_rule)
    # print(allowed_list,str(request.url_rule) in allowed_list)

    # if   request.method !='OPTIONS' and str(request.url_rule) not in allowed_list:
    #     CheckPermissionsFunc()
    # print("Request allowed")
