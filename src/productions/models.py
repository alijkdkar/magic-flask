from sqlalchemy import inspect,Enum
from datetime import datetime
# from flask_validator import ValidateEmail, ValidateString, ValidateCountry
from sqlalchemy.orm import validates

from sqlalchemy import ForeignKey
from sqlalchemy import Integer,func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from typing import List
from .. import db # from __init__.py



class Category(db.Model):
        id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
        title = db.Column(db.String(100))
        description = db.Column(db.String(200))
        parent_id = db.Column(Integer, ForeignKey('category.id'),nullable=True, unique=False)

        def toDict(self):
                return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }
        
        def setValuesFromDict(self, data: dict) -> None:
                for key, value in data.items():
                        if hasattr(self, key):
                                setattr(self, key, value)

post_tag = db.Table('product_tag',
                    db.Column('production_id', db.String(50), db.ForeignKey('production.id')),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                    )

products_Category = db.Table('production_category',
                    db.Column('production_id', db.String(50), db.ForeignKey('production.id')),
                    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
                    )


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def toDict(self):
        return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    def __repr__(self):
        return f'<Tag "{self.name}">' 


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
        viewOnly = db.Column(db.Boolean())
        enable = db.Column(db.Boolean())
        createdTime =db.Column(db.DateTime(timezone=False), server_default=func.now())
        updatedTime =db.Column(db.DateTime(timezone=False), onupdate=func.now())
        
        tags = db.relationship('Tag', secondary=post_tag, backref='products')
        categorys = db.relationship("Category",secondary=products_Category, backref='product', lazy=True)
        images = db.relationship('ProductionImage', backref='product', lazy=True,cascade="all, delete-orphan")
        
        def toDict(self):
                return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

        def setValuesFromDict(self, data: dict) -> None:
                for key, value in data.items():
                        if hasattr(self, key):
                                setattr(self, key, value)
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
