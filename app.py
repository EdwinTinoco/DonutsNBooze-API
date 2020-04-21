from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
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


@app.route('/')
def home():    
    return "<h1>*CRUD donuts && Booze Home Page*</h1>"

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


# Endpoints for Users -------------------------------------------------------



# Endpoints for Comments -------------------------------------------------------



if __name__ == '__main__':
    app.run(debug=True)