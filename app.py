from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_heroku import Heroku
from environs import Env
import os

app = Flask(__name__)
CORS(app)
heroku = Heroku(app)

env = Env()
env.read_env()
DATABASE_URL = env("DATABASE_URL")

basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


# Create Table Products
class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)    
    description = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(500))
    category = db.Column(db.String(60), nullable=False)
    inventory = db.Column(db.Integer)
    
    def __init__(self, name, description, image, category, inventory):       
        self.name = name
        self.description = description
        self.image = image
        self.category = category
        self.inventory = inventory


class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'image', 'category', 'inventory')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


# Create Table Comments
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(500), nullable=False)
    id_product = db.Column(db.Integer, nullable=False)
    id_user =db.Column(db.Integer)

    def __init__(self, comment, id_product, id_user):       
        self.comment = comment
        self.id_product = id_product
        self.id_user = id_user

class CommentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'comment', 'id_product', 'id_user')

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)


# Create Table Users
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __init__(self, name, email, password, role):       
        self.name = name
        self.email = email
        self.password = password
        self.role = role

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'password', 'role')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route('/', methods=["GET"])
def home():    
    return "<h1>CRUD donuts && Booze Home Page</h1>"
    

# Endpoints for Products -------------------------------------------------------
@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    description = request.json['description']
    image = request.json['image']
    category = request.json['category']
    inventory = request.json['inventory']

    new_product = Product(name, description, image,
                          category, inventory)

    db.session.add(new_product)
    db.session.commit()

    product = Product.query.get(new_product.id)
    return product_schema.jsonify(product)

@app.route('/products', methods=["GET"])
def get_products():    
    all_products = Product.query.all()
    result = products_schema.dump(all_products)

    return jsonify(result)

@app.route('/product/<id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)

    result = product_schema.dump(product)
    return jsonify(result)

@app.route('/product/<id>', methods=['PATCH'])
def update_category(id):
    product = Product.query.get(id)

    new_inventory = request.json['inventory']

    product.inventory = new_inventory

    db.session.commit()
    return product_schema.jsonify(product)

@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    record = Product.query.get(id)
    db.session.delete(record)
    db.session.commit()

    return jsonify('Item deleted')

# Endpoints for Comments -------------------------------------------------------    
@app.route('/comment', methods=['POST'])
def add_comment():
    comment = request.json['comment']
    id_product = request.json['id_product']
    id_user = request.json['id_user']

    new_comment = Comment(comment, id_product, id_user)

    db.session.add(new_comment)
    db.session.commit()

    current_comment = Comment.query.get(new_comment.id)
    return comment_schema.jsonify(current_comment)

@app.route('/comments', methods=["GET"])
def get_comments():    
    all_comments = Comment.query.all()
    result = comments_schema.dump(all_comments)

    return jsonify(result)

@app.route('/comment/<id>', methods=['GET'])
def get_comment(id):
    # comments_by_id_product = Comment.query.get(id_product)
    comments_by_id_product = Comment.query.filter_by(id_product = id)
    if len(comments_by_id_product) > 1:
        result = comments_schema.dump(comments_by_id_product)
    else:        
        result = comment_schema.dump(comments_by_id_product)

    return jsonify(result)

@app.route('/comment/<id>', methods=['DELETE'])
def delete_comment(id):
    record = Comment.query.get(id)
    db.session.delete(record)
    db.session.commit()

    return jsonify('Comment deleted')

# Endpoints for Users -------------------------------------------------------
@app.route('/user', methods=['POST'])
def add_user():
    name = request.json["name"]
    email = request.json["email"]
    password = request.json["password"]
    role = request.json["role"]

    new_user = User(name, email, password, role)

    db.session.add(new_user)
    db.session.commit()

    user = User.query.get(new_user.id)
    return user_schema.jsonify(user)

@app.route('/users', methods=["GET"])
def get_users():    
    all_users = User.query.all()
    result = users_schema.dump(all_users)

    return jsonify(result)

@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)

    result = user_schema.dump(user)
    return jsonify(result)

@app.route('/user/<id>', methods=['PATCH'])
def update_password(id):
    user = User.query.get(id)

    new_password = request.json['password']

    user.password = new_password

    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    record = User.query.get(id)
    db.session.delete(record)
    db.session.commit()

    return jsonify('User deleted')



if __name__ == '__main__':
    app.run(debug=True)
