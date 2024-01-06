from sqlalchemy import MetaData
from sqlalchemy import ForeignKey
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    Firstname = db.Column(db.String)
    Lastname = db.Column(db.String)
    Accountno = db.Column(db.String, unique=True)  # Assuming it's unique
    password = db.Column(db.String)
    accountbalance = db.Column(db.String , default = '0.0')

#     # Relationship definition for transactions associated with a user
#     transactions = relationship('Transaction', backref='user', lazy=True)

# class Transaction(db.Model):
#     __tablename__ = 'transaction'

#     id = db.Column(db.Integer, primary_key=True)
#     Accountbalance = db.Column(db.String)
#     Chequeno = db.Column(db.String)
#     Accountno = db.Column(db.String, db.ForeignKey('users.Accountno'))  # Foreign key reference

#     # You can add more fields as needed for transactions

#     # This establishes the relationship to the User model
#     user_id = db.Column(db.Integer, ForeignKey('users.id'))


