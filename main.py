from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'category': p.category
    } for p in products])

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([{
        'id': o.id,
        'customer_name': o.customer_name,
        'product_name': o.product_name,
        'quantity': o.quantity,
        'price': o.price
    } for o in orders])

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()

    category = Category.query.filter_by(name=data['category']).first()

    if not category:
        category = Category(name=data['category'])
        db.session.add(category)
        db.session.commit()

    existing_product = Product.query.filter_by(name=data['name']).first()
    if existing_product:
        return jsonify({'message': 'Product already exists'}), 400

    product = Product(name=data['name'], price=data['price'], category=category.name)
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully'}), 201

@app.route('/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    product = Product.query.filter_by(name=data['product_name']).first()
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    order = Order(
        customer_name=data['customer_name'],
        product_name=data['product_name'],
        quantity=data['quantity'],
        price=product.price
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order added successfully'}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Recreate tables based on the current models
    app.run(debug=True)
