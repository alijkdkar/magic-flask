from flask import request, jsonify,abort
import uuid,os,json
from werkzeug.utils import secure_filename
from .. import minio
from .. import db
from ..utils.ImageProccessor import CoreImageAnalyzer
from ..utils.milvus import MyMilvuesClient
from ..utils.milvus import MyMilvuesClient

from .models import Production,ProductionImage,Category,Tag,ProductionFeatures
from sqlalchemy.sql import text



allowed_extention = ['jpg','jpeg','png',]
milvus=MyMilvuesClient().connect()

#### production #####

def list_all_production_controller():
        pageSize = request.args.get('pageSize')
        pageNumber = request.args.get('pageNumber')
        categoriesFilter = request.args.get('categories')
        if pageSize is None:
            pageSize=10
        
        if pageNumber is None:
            pageNumber = 1
        sort=''
        if 'sort' in request.args:
            sor =  request.args.get("sort")
            sor = json.loads(str(sor))
            sort = '"production"."'+sor[0]+'"'+" "+sor[1]
        
        if categoriesFilter is not None and categoriesFilter.strip() != '':
            categoriesFilter = categoriesFilter.split(',')
            allProduction =  (Production.query
                                            .join(Production.categories)
                                            .filter(Production.categories.any(Category.id.in_(categoriesFilter)))
                                            .order_by(text(sort)).paginate(max_per_page=int(pageSize),page=int(pageNumber)))

        else:
            allProduction =  Production.query.order_by(text(sort)).paginate(max_per_page=int(pageSize),page=int(pageNumber))
        
        
        
        response = []
        for pro in allProduction:
                data =pro.toDict()
                if pro.image is not None:    
                    data["image"]=minio.GetFileUrl(pro.image)

                categoris=[]
                for cat in pro.categories:
                    categoris.append(cat.toDict())
                data['categories'] = categoris
                data['features']=pro.getFeaturesWithTotoalPrice()
                response.append(data)
        return   jsonify({"count":len(response),"list":response})


def get_one_production_by_code_controller(product_code):
        product = Production.query.filter_by(code=product_code).first()
        imagesUrl =[]
        
        for _,img in enumerate(product.images):
            imagesUrl.append(minio.GetFileUrl(img.file_id))

        data=product.toDict()
        data["images"]=imagesUrl
        data['image']= minio.GetFileUrl(product.image)
        categoris=[]
        for cat in product.categories:
            categoris.append(cat.toDict())
        data['categories'] = categoris
        data['features']=product.getFeaturesWithTotoalPrice()

        return jsonify(data)

def get_one_production_by_id_controller(prodId):
        product = Production.query.get(prodId)
        imagesUrl =[]
        if product.images is not None:
            for idx,x in enumerate(product.images):
                j = ({"file_id":x.file_id,"url": minio.GetFileUrl(x.file_id)})
                imagesUrl.append(j)

        data=product.toDict()
        data["images"]=imagesUrl
        if product.image is not None:    
            data['image']=({"file_id":product.image,"url": minio.GetFileUrl(product.image)})
        categoris=[]
        for cat in product.categories:
            categoris.append(cat.id)
        data['categories'] = categoris
        data['features']=product.getFeaturesWithTotoalPrice()

        return jsonify(data)

def create_product_controller():
    request_form1 = request.data.decode('utf-8')
    id = str(uuid.uuid4())
    
    json_data = json.loads(request_form1)
    if json_data.get('code') is not None and CheckCodeUsed(json_data.get('code'))==True:
        return  jsonify({"status":"bad request","msg":"duplicat code"}),400


    new_production = Production(
                          id = id,
                          name = json_data.get('name'),
                          description = json_data.get('description'),
                          image = json_data.get('image'),
                          price = json_data.get('price'),
                          unit = json_data.get('unit'),
                          material = json_data.get('material'),
                          code = json_data.get('code'),
                          color = json_data.get('color'),
                          stock  = json_data.get('stock'),
                          enable = json_data.get('enable'),
                          viewOnly = json_data.get('viewOnly'),
                          )
    imagesId = json_data.get('images')
    print("images :",imagesId,new_production.id)
    if imagesId is not None:
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
        new_production.categories.append(cat)
    db.session.commit()


    response = Production.query.get(id).toDict()
    return jsonify(response)

def update_product_controller(product_id):
    productDb = Production.query.get(product_id)
    requestPayload= json.loads(request.data.decode("utf-8"))
    productDb.setValuesFromJson(requestPayload)

   
    features = ProductionFeatures.query.filter_by(product_id=str(product_id)).all()
    for x in features:
        db.session.delete(x)

    AddProductFeatures(product_id)

    for img in productDb.images:
        db.session.delete(img)
    imagesId = requestPayload.get('images')
    if imagesId is not None:
        for x in imagesId:
            newImageId = str(uuid.uuid4())
            newProductImage= ProductionImage(
              id = newImageId,
              file_id = x,
              product_id=productDb.id,
              image_path= '',
              type = 'Image'
            )
            db.session.add(newProductImage)
    
    db.session.commit()
    return jsonify({"Message":"Success"}),201

def delete_product_controller(product_id):
    product = Production.query.get(product_id)
    if product is None:
        jsonify({"error": "Not Found Production"}),404
    
    print(product.images)
    for img in product.images:
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
        json_data = json.loads(request_form)
        # Access the 'Features' array
        features = json_data.get('features')
        print("its feature:",features)
        # Process each feature
        if features is not None:
        
            for feature in features:
                feature_name = feature.get('title')
                feature_description = feature.get('description')
                feature_type = feature.get('featureType')
                feature_value = feature.get('value')
                is_price_effect = bool(feature.get('isEffectPrice'))
                price_effect_value = feature.get('priceEffectValue')
                enable = feature.get('active')
                new_feature=ProductionFeatures(id=str(uuid.uuid4()),
                            product_id = product_id,
                            name = feature_name,
                            description = feature_description,
                            feature_type = str(feature_type), #ProductFeatureType(feature_type),
                            value = feature_value or 'someValue',
                            is_price_effect = bool(is_price_effect),
                            enable = bool(enable),
                            price_effect_value = price_effect_value
                            )
                db.session.add(new_feature)

                
    except json.JSONDecodeError as ex :
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
    return features

def UpdateProductFeatureById(product_id):
    product =Production.query.get(product_id)
    if product==None:
        abort(404)
    try:
        request_form = request.data.decode('utf-8')
        print(request_form)
        json_data = json.loads(request_form)
        # Access the 'Features' array
        features = json_data.get('features')

        # Process each feature
        for feature in features:
            feature_id = feature.get('id')
            feature_name = feature.get('title')
            feature_description = feature.get('description')
            feature_type = feature.get('featureType')
            feature_value = feature.get('value')
            is_price_effect = bool(feature.get('isEffectPrice'))
            price_effect_value = feature.get('priceEffectValue')
            enable = bool(feature.get('active'))
            featureDb =ProductionFeatures.query.get(feature_id)
            if featureDb is not None:
                featureDb.setValues(name=feature_name,description=feature_description,type=feature_type,value=feature_value,is_price_effect=is_price_effect,price_effect_value=price_effect_value,enable=enable)



        db.session.commit()

                
    except json.JSONDecodeError as ex :
        print("Data is not in JSON format",ex.msg)
        abort(500)
    return jsonify("Feature updated successfully"),200

def DeleteOneFeatureFromTheList(product_id,feature_id):
    pass



###### production ######


def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        print('files:',request.files)

        if 'file' not in request.files:
            return jsonify({"No File Uploaded"})
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        print(file.filename)
        if file.filename == '':
            return jsonify({"Bad Request"}),400
        if  file is not None and  allowed_file(file.filename.lower()):
            print('in allowd fiile')
            filename = secure_filename(file.filename)
            # upload to minio and return id 
            filename,extention = os.path.splitext(file.filename)
            file.filename=str(uuid.uuid4())+extention
            minio.Upload_File(file=file)
            feature = CoreImageAnalyzer().FeattureExtraction(file=file)
            ids = milvus.insert_vectors(file.filename,feature)
            print('milvus:',ids)
            fileUrl = minio.GetFileUrl(fileName=file.filename)
            return jsonify({"id":file.filename,"url":fileUrl})
        else:
            return jsonify({"file extention is not allowed"}),400
    else:
        print('in else ')
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
            feature = CoreImageAnalyzer().FeattureExtraction(file=file)
            milvus.search_similar_vectors(feature)
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

def GetAllIndex():
    ss=milvus.GetAllIndexed()
    print("asdasdasd")
    if ss is None:
        print("nothing found")
    else:
        print(ss)
    
    return jsonify({"message": "done"}),200

def allowed_file(fileName:str):
     """Checks if the file is one of the allowed types/extensions."""
     if fileName.split('.')[1] in allowed_extention:
        return True
     return False

def CheckCodeUsed(code):
        p=Production.query.filter_by(code=code).first()
        return jsonify( p is not None)


#######region Category#######
def create_category():
    request_form1 = request.data.decode('utf-8')
    json_data = json.loads(request_form1)
    # print(json_data.get('parentId'))
    
    if  json_data.get('parentId') is not None:
        cat = Category(title=json_data.get('title'),description=json_data.get('description'),parent_id=json_data.get('parentId'),enName=json_data.get('enName'))
    else:
        cat = Category(title=json_data.get('title'),description=json_data.get('description'),enName=json_data.get('enName'))
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.toDict())



def  getAllCategories():
    list_of_ids = request.args.get('filter')
    pageSize = request.args.get('pageSize')
    pageNumber = request.args.get('pageNumber')

    if pageSize is None:
        pageSize=10
    if pageNumber is None:
        pageNumber = 1
    categories = list
    list_of_ids = json.loads(list_of_ids)
    if  list_of_ids is not None:
        list_of_ids =list_of_ids.get('ids')
    if type(list_of_ids)==list and len(list_of_ids)>0:
        categories = Category.query.filter(Category.id.in_(list_of_ids)).paginate(max_per_page=int(pageSize),page=int(pageNumber))
    else:
        categories = Category.query.paginate(max_per_page=int(pageSize),page=int(pageNumber))

    result = []
    for cat in categories:
         result.append(cat.toDict())
    return jsonify({"count":len(result),"list":result})
    

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
    # cat.setValuesFromDict(request.form)
    cat.setValuesFromJson(json.loads(request.data.decode('utf-8')))
    try:
        db.session.commit()
    except Exception as ex:
        print(ex)
    return jsonify(cat.toDict()),201

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