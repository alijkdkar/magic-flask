from flask import request

from ..app import app
from .controllers import * #create_product_controller,get_one_production_by_id_controller,list_all_production_controller,upload_file,search_by_file,update_product_controller,delete_product_controller

#un auth 
@app.route("/product", methods=['GET', 'POST'])
def list_productions():
    if request.method == 'GET': return list_all_production_controller()
    # if request.method == 'POST': return create_product_controller()
    else: return 'Method is Not Allowed'

@app.route("/product/<product_id>", methods=['GET'])
def retrieve_productions(product_id):
    if request.method == 'GET': return get_one_production_by_id_controller(product_id)

@app.route("/product/search",methods=['GET', 'POST'])
def SearchByImage():
    print(request.method)
    if request.method in ['GET','POST']:return search_by_file()
    else: return 'Method is Not Allowed'

# admin Auth API


@app.route("/admin/product", methods=['GET', 'POST'])
def list_create_productions():
    if request.method == 'GET': return list_all_production_controller()
    if request.method == 'POST': return create_product_controller()
    else: return 'Method is Not Allowed'

@app.route("/admin/product/<product_id>", methods=['GET', 'PUT', 'DELETE'])
def retrieve_update_destroy_productions(product_id):
    if request.method == 'GET': return get_one_production_by_id_controller(product_id)
    if request.method == 'PUT': return update_product_controller(product_id)
    if request.method == 'DELETE': return delete_product_controller(product_id)
    else: return 'Method is Not Allowed'

@app.route("/admin/product/<product_id>/feature", methods=['POST','GET', 'PUT', 'DELETE'])
def add_feature(product_id):
    if request.method == "POST": return AddProductFeatures(product_id)
    else: return 'Method is Not Allowed'

    
@app.route("/admin/storage", methods=['GET', 'POST'])
def UploadFile():
    if request.method in ['GET','POST']:return upload_file()


@app.route("/admin/category",methods=['GET','POST'])
def list_create_category():
    if request.method == 'GET': return getAllCategories()
    if request.method == 'POST':  return create_category()
    else:return 'Method is Not Allowed'


@app.route("/admin/category/<cat_id>", methods=['GET', 'PUT', 'DELETE'])
def retrieve_update_destroy_category(cat_id):
    if request.method == 'GET':return GetCategoryById(cat_id)
    if request.method == 'PUT': return UpdateCategory(cat_id)
    if request.method == 'DELETE': return DeleteCategory(cat_id)
    else: return 'Method is Not Allowed'