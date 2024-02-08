from flask import request, jsonify
import uuid,os
from werkzeug.utils import secure_filename
from .. import minio
from .. import db
from ..utils.ImageProccessor import CoreImageAnalyzer
from .models import Production,ProductionImage,Category,Tag
from sqlalchemy import inspect

allowed_extention = ['jpg','jpeg','png',]

# production

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
                response.append(data)
        return  jsonify(response)

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
        return jsonify(data)

def create_product_controller():
    request_form = request.form.to_dict()
    id = str(uuid.uuid4())
    print(id)
    new_production = Production(
                          id = id,
                          name = request_form['name'],
                          description = request_form['description'],
                          image = request_form['image'],
                          price = request_form['price'],
                          unit = request_form['unit'],
                          material = request_form['material'],
                          code = request_form['code'],
                          color = request_form['color'],
                          stock  = request_form['stock'],
                          )
    imagesId = request_form['images'].split(',')
    
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

    db.session.add(new_production)
    db.session.commit()
    
    categorisIds = request_form['categories'].split(',')
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


# production


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




#region Category
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


