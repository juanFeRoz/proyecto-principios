import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from faker import Faker
import random

app = Flask(__name__)

db_user = os.environ.get('DB_USER', 'postgres')
db_password = os.environ.get('DB_PASSWORD', 'password')
db_host = os.environ.get('DB_HOST', 'localhost') 
db_name = os.environ.get('DB_NAME', 'tienda_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
fake = Faker()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()

@app.route('/')
def health_check():
    return jsonify({"status": "ok", "message": "API Inventario V1.0"})

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.limit(100).all() 
    return jsonify([{
        'id': p.id, 
        'name': p.name, 
        'price': p.price,
        'stock': p.stock
    } for p in products])

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(
        name=data.get('name', 'Producto Genérico'),
        description=data.get('description', 'Sin descripción'),
        price=data.get('price', 10.0),
        stock=data.get('stock', 10)
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Producto creado", "id": new_product.id}), 201

@app.route('/seed/<int:count>', methods=['POST'])
def seed_data(count):
    print(f"Generando {count} registros...")
    for _ in range(count):
        p = Product(
            name=fake.bs(),
            description=fake.catch_phrase(),
            price=round(random.uniform(10, 500), 2),
            stock=random.randint(0, 1000)
        )
        db.session.add(p)
    db.session.commit()
    return jsonify({"message": f"Se han insertado {count} productos falsos exitosamente."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)