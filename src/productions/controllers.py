from flask import request, jsonify
import uuid,os
from werkzeug.utils import secure_filename
from .. import minio
from .. import db
from .models import Production,ProductionImage
from sqlalchemy import inspect

allowed_extention = ['jpg','jpeg','png',]

def list_all_production_controller():
        allProduction =  Production.query.all()
        response = []
        for pro in allProduction:
                data =pro.toDict()
                data["image"]=minio.GetFileUrl(pro.image)
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
    print(type(imagesId))
    for x in imagesId:
        newImageId = str(uuid.uuid4())
        newProductImage= ProductionImage(
              id = newImageId,
              file_id = x,
              product_id=new_production.id,
              image_path= '',
              type = 'Image'
        )
        print('image id',newProductImage.product_id)
        db.session.add(newProductImage)

    db.session.add(new_production)
    db.session.commit()

    response = Production.query.get(id).toDict()
    return jsonify(response)

        

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

def allowed_file(fileName:str):
     """Checks if the file is one of the allowed types/extensions."""
     if fileName.split('.')[1] in allowed_extention:
        return True
     return False
