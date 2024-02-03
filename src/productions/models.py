from sqlalchemy import inspect,Enum
from datetime import datetime
# from flask_validator import ValidateEmail, ValidateString, ValidateCountry
from sqlalchemy.orm import validates

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from typing import List
from .. import db # from __init__.py


class Production(db.Model):
        id = db.Column(db.String(50), primary_key=True, nullable=False, unique=True)
        name = db.Column(db.String(100))
        description = db.Column(db.String(200))
        image = db.Column(db.String(200))
        price = db.Column(db.BigInteger,nullable=True)
        unit = db.Column(Enum('MetreMoraba', 'MetreMokaab', 'KiloGaram','Tona', name='product_unit'), nullable=True)
        material = db.Column(db.String(100))
        stock = db.Column(Enum('AVAILABLE', 'UNAVAILABLE', name='StockStatus'), nullable=True)
        code = db.Column(db.String(100))
        color = db.Column(Enum('NONE', 'BLUE','YELLOW','GRAY', name='Color'), nullable=True)
        images = db.relationship('ProductionImage', backref='product', lazy=True)

        def toDict(self):
                return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }


        def __repr__(self):
                return "<%r>" % self.name


class ProductionImage(db.Model):
        id = db.Column(db.String(50), primary_key=True, nullable=False, unique=True) 
        file_id = db.Column(db.String(50))#minio file Id
        image_path = db.Column(db.String(255), nullable=False)
        product_id = db.Column(db.String(50), db.ForeignKey('production.id'), nullable=False)
        type = db.Column(Enum('Image', 'Video', name='MediaType'), nullable=True)
        
        def toDict(self):
                return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }
        
        def __repr__(self):
                return "<%r>" % self.file_id
