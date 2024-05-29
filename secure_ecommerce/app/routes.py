# app/routes.py
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from app import db
from app.models import User, Product
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class Register(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.query.filter_by(email=email).first():
            return {'message': 'User already exists'}, 400

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return {'message': 'User registered successfully'}, 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity={'username': user.username, 'is_admin': user.is_admin})
            return {'access_token': access_token}, 200
        return {'message': 'Invalid credentials'}, 401

class ProductList(Resource):
    def get(self):
        products = Product.query.all()
        return jsonify([product.to_dict() for product in products])

class ProductResource(Resource):
    def get(self, product_id):
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict())

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(ProductList, '/products')
api.add_resource(ProductResource, '/products/<int:product_id>')