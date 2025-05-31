from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Cấu hình cơ sở dữ liệu SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///microdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Định nghĩa mô hình MicroData
class MicroData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False, unique=True)
    freq = db.Column(db.String(100))
    image = db.Column(db.String(200))

    def __repr__(self):
        return f"<MicroData {self.model}>"

# API lấy danh sách thiết bị
@app.route('/api/microdata', methods=['GET'])
def get_microdata():
    data = MicroData.query.all()
    return jsonify([{'id': item.id, 'brand': item.brand, 'model': item.model, 'freq': item.freq, 'image': item.image} for item in data])

# API thêm thiết bị mới
@app.route('/api/microdata', methods=['POST'])
def add_microdata():
    data = request.get_json()
    new_device = MicroData(
        brand=data['brand'],
        model=data['model'],
        freq=data['freq'],
        image=data['image']
    )
    db.session.add(new_device)
    db.session.commit()
    return jsonify({'message': 'Dữ liệu đã được thêm'}), 201

if __name__ == '__main__':
  #  app.run(debug=True)
    app.run(host='127.0.0.1', port=8000, debug=True)
