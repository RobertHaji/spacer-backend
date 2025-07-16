from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///categories.db'
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/categories', methods=['POST'])
def create_category():
    data = request.json
    new_category = Category(name=data['name'])
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'id': new_category.id, 'name': new_category.name}), 201

@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])

@app.route('/categories/<int:id>', methods=['GET'])
def get_category(id):
    category = Category.query.get_or_404(id)
    return jsonify({'id': category.id, 'name': category.name})

@app.route('/categories/<int:id>', methods=['PUT'])
def update_category(id):
    category = Category.query.get_or_404(id)
    data = request.json
    category.name = data['name']
    db.session.commit()
    return jsonify({'id': category.id, 'name': category.name})



if __name__ == '__main__':
    app.run(debug=True)
