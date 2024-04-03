from flask import request, jsonify,abort
import uuid,os,json
from werkzeug.utils import secure_filename
from .. import minio
from .. import db
from ..utils.ImageProccessor import CoreImageAnalyzer
from ..utils.milvus import MilvuesClient

from .models import Production,ProductionImage,Category,Tag,ProductionFeatures
from sqlalchemy import inspect


allowed_extention = ['jpg','jpeg','png',]
milvus=MilvuesClient().connect()

#### production #####

def list_all_production_controller():
        pageSize = request.args.get('pageSize')
        pageNumber = request.args.get('pageNumber')
        if pageSize is None:
            pageSize=10
        
        if pageNumber is None:
            pageNumber = 1

        allProduction =  Production.query.paginate(max_per_page=int(pageSize),page=int(pageNumber))
        response = []
        for pro in allProduction:
                data =pro.toDict()
                data["image"]=minio.GetFileUrl(pro.image)

                categoris=[]
                for cat in pro.categorys:
                    categoris.append(cat.toDict())
                data['categories'] = categoris
                data['features']=pro.getFeaturesWithTotoalPrice()
                response.append(data)
        return   jsonify({"count":len(response),"list":response})

def get_one_production_by_id_controller(prodId):
        product = Production.query.get(prodId)
        product.imagesUrl =[]
        for idx,x in enumerate(product.images):
            print(idx,minio.GetFileUrl(x.file_id))
            product.imagesUrl.append(minio.GetFileUrl(x.file_id))


        data=product.toDict()
        data["imagesUrls"]=product.imagesUrl
        data['image']=minio.GetFileUrl(product.image)
        categoris=[]
        for cat in product.categorys:
            categoris.append(cat.toDict())
        data['categories'] = categoris
        data['features']=product.getFeaturesWithTotoalPrice()

        return jsonify(data)

def create_product_controller():
    # request_form = request.form.to_dict()
    request_form1 = request.data.decode('utf-8')
    id = str(uuid.uuid4())
    print(id)
    json_data = json.loads(request_form1)
    new_production = Production(
                          id = id,
                          name = json_data.get('name'),
                          description = json_data.get('description'),
                          image = json_data.get('image'),
                          price = json_data.get('price'),
                          unit = json_data.get('unit'),
                          material = json_data.get('materil'),
                          code = json_data.get('code'),
                          color = json_data.get('color'),
                          stock  = json_data.get('stock'),
                          )
    imagesId = json_data.get('images')
    print("images :",imagesId,new_production.id)
    for x in imagesId:
        newImageId = str(uuid.uuid4())
        newProductImage= ProductionImage(
              id = newImageId,
              file_id = x,
              product_id=new_production.id,
              image_path= '',
              type = 'Image'
        )
        db.session.add(newProductImage)
    
    AddProductFeatures(id)

    db.session.add(new_production)
    db.session.commit()
    
    categorisIds = json_data.get('categories')
    print(categorisIds)
    for catId in categorisIds:
        cat =Category.query.get(catId)
        new_production.categorys.append(cat)
    db.session.commit()


    response = Production.query.get(id).toDict()
    return jsonify(response)

def update_product_controller(product_id):
    productDb = Production.query.get(product_id)
    productDb.setValuesFromDict(request.form)
    db.session.commit()
    return jsonify({"Message":"Success"}),201

def delete_product_controller(product_id):
    product = Production.query.get(product_id)
    if product is None:
        jsonify({"error": "Not Found Production"}),404
    
    print(product.images)
    for img in product.images:
        # imgId = uuid.UUID(img.id)
        # pimage =ProductionImage.query.filter_by(id=imgId).first()
        db.session.delete(img)
    
    db.session.delete(product)
    db.session.commit()
    return  jsonify("Product Deleted")

def AddProductFeatures(product_id):
    request_form = request.data.decode('utf-8')
    # product = Production.query.get(product_id)
    # if product is None:
    #     abort(404)
    try:
        print(request_form)
        json_data = json.loads(request_form)
        print("after")
        # Access the 'Features' array
        features = json_data.get('Features')
        print("its feature:",features)
        # Process each feature
        for feature in features:
            feature_name = feature.get('name')
            feature_description = feature.get('description')
            feature_type = feature.get('feature_type')
            feature_value = feature.get('value')
            is_price_effect = feature.get('is_price_effect')
            price_effect_value = feature.get('price_effect_value')
            enable = feature.get('enable')
            new_feature=ProductionFeatures(id=str(uuid.uuid4()),
                           product_id = product_id,
                           name = feature_name,
                           description = feature_description,
                           feature_type = str(feature_type), #ProductFeatureType(feature_type),
                           value = feature_value,
                           is_price_effect = bool(is_price_effect),
                           enable = bool(enable),
                           price_effect_value = price_effect_value
                           )
            db.session.add(new_feature)
        # db.session.commit()

                
    except json.JSONDecodeError as ex :
    # except Exception as  ex :
        print("Data is not in JSON format",ex.msg)
        abort(500)
    return jsonify("Feature added successfully"),201

def GetAllFeatureOfThisProduct(product_id):
    product =Production.query.get(product_id)
    if product==None:
        abort(404)
    features = ProductionFeatures.query.filter_by(product_id=str(product_id)).all()
    response = []
    for x in features:
        response.append(x.toDict())
    return jsonify({"count":len(response),"list":response})

def UpdateProductFeatureById(product_id):
    product =Production.query.get(product_id)
    if product==None:
        abort(404)
    try:
        request_form = request.data.decode('utf-8')
        print(request_form)
        json_data = json.loads(request_form)
        # Access the 'Features' array
        features = json_data.get('Features')

        # Process each feature
        for feature in features:
            feature_id = feature.get('id')
            feature_name = feature.get('name')
            feature_description = feature.get('description')
            feature_type = feature.get('feature_type')
            feature_value = feature.get('value')
            is_price_effect = bool(feature.get('is_price_effect'))
            price_effect_value = feature.get('price_effect_value')
            enable = bool(feature.get('enable'))
            featureDb =ProductionFeatures.query.get(feature_id)
            if featureDb is not None:
                featureDb.setValues(name=feature_name,description=feature_description,type=feature_type,value=feature_value,is_price_effect=is_price_effect,price_effect_value=price_effect_value,enable=enable)



        db.session.commit()

                
    except json.JSONDecodeError as ex :
    # except Exception as  ex :
        print("Data is not in JSON format",ex.msg)
        abort(500)
    return jsonify("Feature updated successfully"),200

def DeleteOneFeatureFromTheList(product_id,feature_id):
    pass

###### production-END ######


def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({"No File Uploaded"})
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return jsonify({"Bad Request"})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # upload to minio and return id 
            filename,extention = os.path.splitext(file.filename)
            file.filename=str(uuid.uuid4())+extention
            minio.Upload_File(file=file)
            feature = CoreImageAnalyzer().FeattureExtraction(file=file)
            print(feature)
            ids = milvus.insert_vectors(file.filename,feature)
            print('milvus:',ids)
            return jsonify({"id":file.filename})
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

def search_by_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({"No File Uploaded"})
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return jsonify({"Bad Request"})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # upload to minio and return id 
            return list_all_production_controller()
            
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

def allowed_file(fileName:str):
     """Checks if the file is one of the allowed types/extensions."""
     if fileName.split('.')[1] in allowed_extention:
        return True
     return False




#######region Category#######
def create_category():
    request_form = request.form.to_dict()
    if 'parentId' in request_form:
        cat = Category(title=request_form['title'],description=request_form['description'],parent_id=request_form['parentId'])
    else:
        cat = Category(title=request_form['title'],description=request_form['description'])
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.toDict())

def  getAllCategories():
    categories = Category.query.all()
    result = []
    for cat in categories:
         result.append(cat.toDict())
    return  jsonify(result)

def GetCategoryById(id):
     cat = Category.query.get(id)
     if cat is None:
        return jsonify({"error": "Not Found Exception"}),404
     else :
        return jsonify(cat.toDict())  

def UpdateCategory(id):
    cat = Category.query.get(id)
    # if  cat.parent_id != None:
    #       return jsonify({"error": "This category has subcategories and cannot be deleted"}),404
    cat.setValuesFromDict(request.form)
    try:
        db.session.commit()
    except Exception as ex:
        print(ex)
    return jsonify({"Message":"The category was updated successfully"}),201

def DeleteCategory(id):
    cat = Category.query.get(id)
    print("parent",cat.parent_id)
    
    if Category.query.filter(Category.parent_id==id).count()>0:#todo: check ant production with this cat id #or Category.query.filter(Production.category_id == id).count() > 0:
          return jsonify({"error": "This category has subcategories and cannot be deleted"}),403
    else :
          db.session.delete(cat)
          db.session.commit()
          return  jsonify("Category Deleted")

#Todo Crud
######### end Category #########

