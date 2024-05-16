
from flask import Flask ,request
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Namespace, Resource, fields
from models import User, db 
from flask_migrate import Migrate
from flask_cors import CORS
import secrets
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from jwt.exceptions import ExpiredSignatureError, DecodeError
import jwt
import os

# Initialize Flask app
app = Flask(__name__)



secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)

CORS(app)
# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask-RESTx
api = Api()
api.init_app(app)

# Define API namespace
ns = Namespace('banking')
api.add_namespace(ns)

# ---------------------------schemas------------------------------
user_signup_schema = api.model( 'accountregistration' ,{
    "Firstname" : fields.String ,
    "Lastname" : fields.String ,
    "Accountnumber" : fields.String ,
    "password" : fields.String
})
user_login_schema = api.model('user_input',{
    "Accountnumber": fields.String,
    "password" : fields.String,
})

depositschema = api.model('schema',{
    "Accountbalance" : fields.String ,
    "Accountno" : fields.String
})
ChangePasswordschema = api.model( 'changepassword' ,{
   "Accountno" : fields.String ,
   "old_password" : fields.String ,
   'new_password' : fields.String
}
 )
@ns.route('/signup')
class Signup(Resource):
    @ns.expect(user_signup_schema)
    def post(self):
        data = request.get_json() 

        firstname = data.get('Firstname')
        lastname = data.get('Lastname')
        accountnumber = data.get('Accountnumber')
        pin = data.get('password')

        if not (firstname and lastname and accountnumber):
            return {'message': 'Missing username, password, or email'}, 400

        existing_user = User.query.filter_by(Accountno=accountnumber).first()

        if existing_user:
            return {'message': 'Email already exists'}, 400

        new_user = User(Firstname=firstname,
                         Lastname=lastname, 
                         Accountno=accountnumber,
                         password = pin
                         )

        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User created successfully'}, 201



@ns.route('/login')
class Login(Resource):
    @ns.expect(user_login_schema)
    def post(self):
        data = request.get_json()
        # check whether data is missing or if the username or 'password' are missing
        accountnumber = data.get('Accountnumber')
        pin = data.get('password')
        if not(accountnumber and pin):
            return{
                'message': 'Missing Accountnumber , pin'
            } , 400
        
        # query to database to find the user with the provided username
        user = User.query.filter_by(Accountno = accountnumber).first()
        if not user:
            return {
                'message' : 'could Not Verify'
            } , 401
        
    


        return {
            'id' : user.id ,
            'Accountnumber': user.Accountno,
            'Pin' : user.password ,
            'Firstname': user.Firstname,
            'Lastname': user.Lastname,
            'Accountbalance': user.accountbalance  # Return the account balance
        }, 201
    
@ns.route('/deposit')
class PostDeposit(Resource):
    @ns.expect(depositschema)
    def post(self):
        try:
            data = request.json

            # Retrieve the user based on the provided account number
            user = User.query.filter_by(Accountno=data.get('Accountno')).first()

            if user:
                # Add the new deposit amount to the existing Accountbalance
                user.accountbalance = str(float(user.accountbalance) + float(data.get('Accountbalance')))
                db.session.commit()

                return {
                    "message": "Deposit created successfully",
                    "deposit": {
                        "Accountbalance": user.accountbalance
                    }
                }, 201

            return {
                "message": "User not found",
            }, 404

        except Exception as e:
            db.session.rollback()
            return {
                "message": "Failed to create a transaction",
                "error": str(e)
            }, 500

@ns.route('/changepassword')
class ChangePassword(Resource):
    @ns.expect(ChangePasswordschema)
    def post(self):
        try:
            data = request.get_json()
            
            currentuser = data.get('Accountno')
            old_password = data.get('old_password')
            new_password = data.get('new_password')


            user = User.query.filter_by(Accountno=currentuser).first()

            if not user:
                return {"message": "User not found"}, 404

            # Check if the entered old password matches the user's actual password
            if user.password != old_password:
             return {"message": "Old password is incorrect"}, 400

            # Update the user's password to the new one
            user.password = new_password
            db.session.commit()

            return {"message": "Password updated successfully"}, 200

        except Exception as e:
            db.session.rollback()
            return {"message": "Failed to update password", "error": str(e)}, 500
