from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import ENUM
import enum
from datetime import datetime
# from flask_validator import ValidateEmail, ValidateString, ValidateCountry
from sqlalchemy.orm import validates

from .. import db # from __init__.py

# ----------------------------------------------- #

class RoleEnum(enum.Enum):
    Admin = 'admin'
    SemiAmin = 'semiAdmin'
    Manager = 'manager',
    Blogger='blogger',
    Simple = 'simple',
    Guest = 'guest'
    
class Culture(enum.Enum):
    FA='fa',
    EN='en',
    FR='fr'

# culture_enum = ENUM('fa', 'en', 'fr', name='culture')

# role_enum = ENUM( 'admin', 'semiAdmin', 'manager','blogger','simple', 'guest',name='role')




# SQL Datatype Objects => https://docs.sqlalchemy.org/en/14/core/types.html
class Account(db.Model):
# Auto Generated Fields:
    id           = db.Column(db.String(50), primary_key=True, nullable=False, unique=True)
    created      = db.Column(db.DateTime(timezone=True), default=datetime.now)                           # The Date of the Instance Creation => Created one Time when Instantiation
    updated      = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)    # The Date of the Instance Update => Changed with Every Update

# Input by User Fields:
    email        = db.Column(db.String(100), nullable=False, unique=True)
    username     = db.Column(db.String(100), nullable=False)
    dob          = db.Column(db.Date)
    country      = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    password  = db.Column(db.String(500), nullable=False,default="")
    culture = db.Column(ENUM('fa', 'en','fe', name='Culture'), nullable=True)
    role = db.Column(ENUM('admin', 'semiAdmin','manager','blogger','simple','guest', name='Role'), nullable=True)

    




# Set an empty string to null for username field => https://stackoverflow.com/a/57294872
    @validates('username')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '': return None
        else: return value


# How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522
    def toDict(self):
        return { c.key:  getattr(self, c.key) for c in inspect(self).mapper.column_attrs if c.key != "password" }

    def __repr__(self):
        return "<%r>" % self.email
    


    def to_json(self):        
        return {"name": self.username,
                "email": self.email}

    def is_authenticated(self):
        return True

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False          

    def get_id(self):         
        return str(self.id)
    
    def is_admin(self):
        #todo: check with Role
        return True
    
    def get_culture(self):
        if self.culture is None:
            return 'fa'
        return self.culture
    
    def get_role(self):
        if self.role is None:
            return 'guest'
        return self.role