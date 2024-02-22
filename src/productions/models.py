from sqlalchemy import inspect,Enum
from datetime import datetime
import enum
# from sqlalchemy import Enum
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
        features = db.relationship('ProductionFeatures', backref='product', lazy=True,cascade="all, delete-orphan")
        
        
        
        def toDict(self):
                return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

        def setValuesFromDict(self, data: dict) -> None:
                for key, value in data.items():
                        if hasattr(self, key):
                                setattr(self, key, value)
        def __repr__(self):
                return "<%r>" % self.name
        
        def getFeaturesWithTotoalPrice(self):
                featuresResult = []
                for feature in self.features:
                        totalPrice = self.price or 0
                        if feature.enable== True and feature.is_price_effect:
                                totalPrice += feature.price_effect_value
                                # featuresResult.append({"id":feature.id,"title":feature.name,"value":feature.value,"priceEffectValue":feature.price_effect_value,"isEffectPrice":feature.is_price_effect,"totalPrice":totalPrice})
                        featuresResult.append({"id":feature.id,"title":feature.name,"value":feature.value,"priceEffectValue":feature.price_effect_value,"isEffectPrice":feature.is_price_effect,"totalPrice":totalPrice})
                return featuresResult


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






class ProductionFeatures(db.Model):
        id = db.Column(db.String(50), primary_key=True, nullable=False, unique=True) 
        product_id = db.Column(db.String(50), db.ForeignKey('production.id'), nullable=False)
        name = db.Column(db.String(50),nullable=False)
        description = db.Column(db.String(50),nullable=True)
        feature_type = db.Column(Enum('color', 'quality', 'others', name='ProductFeatureType'))#db.Column(featureType, nullable=True)
        value = db.Column(db.String(20), nullable=False)
        is_price_effect = db.Column(db.Boolean, nullable=False,default=False)
        price_effect_value =db.Column(db.Float, nullable=True)
        enable = db.Column(db.Boolean, nullable=False,default=False)
        
        createdTime =db.Column(db.DateTime(timezone=False), server_default=func.now())
        updatedTime =db.Column(db.DateTime(timezone=False), onupdate=func.now())
        
       
        def toDict(self):
                return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }
        
        def __repr__(self):
                return "<%r>" % self.name
        

        def setValuesFromDict(self, data: dict) -> None:
                for key, value in data.items():
                        if hasattr(self, key):
                                setattr(self, key, value)

        def setValues(self,**kwargs):
                for key, value in kwargs.items():
                        if hasattr(self, key):
                                setattr(self, key, value)