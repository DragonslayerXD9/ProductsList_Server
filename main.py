from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json

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
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(80), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    products = db.Column(db.Text, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(80), nullable=False, default="Pending")

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
        'quantity': p.quantity,
        'category': p.category
    } for p in products])

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([{
        'id': o.id,
        'customer_name': o.customer_name,
        'products': json.loads(o.products),
        'total_price': o.total_price,
        'status': o.status
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

    product = Product(name=data['name'], price=data['price'], quantity=data['quantity'], category=category.name)
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully'}), 201

@app.route('/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    
    products_info = []
    total_price = 0.0
    
    for product_data in data['products']:
        product = Product.query.filter_by(name=product_data['name']).first()
        
        if not product:
            return jsonify({'message': f"Product {product_data['name']} not found"}), 404
        product_info = {
            "name": product.name,
            "quantity": product_data['quantity'],
            "price": product.price,
            "total_price": product.price * product_data['quantity']
        }
        
        products_info.append(product_info)
        
        total_price += product_info['total_price']
        
        db.session.commit()

    order = Order(
        customer_name=data['customer_name'],
        products=json.dumps(products_info),
        total_price=total_price,
        status='Complete'
    )

    db.session.add(order)
    db.session.commit()

    return jsonify({'message': 'Order added successfully', 'order_id': order.id, 'total_price': total_price}), 201


if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
