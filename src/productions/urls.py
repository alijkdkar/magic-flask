from flask import request

from ..app import app
from .controllers import create_product_controller,get_one_production_by_id_controller,list_all_production_controller,upload_file,search_by_file

@app.route("/productions", methods=['GET', 'POST'])
def list_create_productions():
    if request.method == 'GET': return list_all_production_controller()
    if request.method == 'POST': return create_product_controller()
    else: return 'Method is Not Allowed'

@app.route("/productions/<product_id>", methods=['GET', 'PUT', 'DELETE'])
def retrieve_update_destroy_productions(product_id):
    if request.method == 'GET': return get_one_production_by_id_controller(product_id)
#     if request.method == 'PUT': return update_account_controller(account_id)
#     if request.method == 'DELETE': return delete_account_controller(account_id)
#     else: return 'Method is Not Allowed'
    
@app.route("/productions/search",methods=['GET', 'POST'])
def SearchByImage():
    print(request.method)
    if request.method in ['GET','POST']:return search_by_file()
    else: return 'Method is Not Allowed'
    
@app.route("/storage", methods=['GET', 'POST'])
def UploadFile():
    if request.method in ['GET','POST']:return upload_file()