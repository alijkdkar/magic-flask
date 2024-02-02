from flask import request, jsonify
import uuid,os
from werkzeug.utils import secure_filename
from .. import minio
from .. import db
from .models import Production,ProductionImage

allowed_extention = ['jpg','jpeg','png',]

def list_all_production_controller():
        allProduction =  Production.query.all()
        response = []
        for pro in allProduction:
                response.append(pro.toDict())
        return  jsonify(response)

def get_one_production_by_id_controller(prodId):
        product = Production.query.get(prodId).toDict()
        return jsonify(product)

def create_product_controller():
    request_form = request.form.to_dict()
    id = str(uuid.uuid4())
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
                          stock  = request_form['stock']
                          )
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
            file.filename=str(uuid.uuid4())+"."+extention
            minio.Upload_File(file=file)
            return jsonify({"id":uuid.uuid4()})
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
