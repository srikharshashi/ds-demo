from flask import Flask, request, jsonify,send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from utils import generate_keys,embed_signature,generate_signature,embed_signature
import binascii


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONV_FOLDER'] = 'conv'

db = SQLAlchemy(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['CONV_FOLDER']):
    os.makedirs(app.config['CONV_FOLDER'])



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    public_key = db.Column(db.Text, nullable=False)
    private_key = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

with app.app_context():
    db.create_all()



@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return {'message': 'Invalid input'}, 400

    public_key, private_key = generate_keys()
    print(public_key,"\n",private_key)
    user = User(username=data['username'], password=data['password'], public_key=public_key, private_key=private_key)
    db.session.add(user)
    db.session.commit()

    return {'message': 'User registered successfully'}, 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return {'message': 'Invalid input'}, 400

    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        return {
            'message': 'Login successful',
            'username': user.username,
            'public_key': user.public_key
        }, 200
    else:
        return {'message': 'Invalid username or password'}, 401

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return {'message': 'No image provided'}, 400

    file = request.files['image']
    if file.filename == '':
        return {'message': 'No image provided'}, 400
    
    username = request.headers.get('username')
    if not username:
        return {'message': 'Missing username in header'}, 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return {'message': 'User not found'}, 404

    

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    filepath2 = os.path.join(app.config['CONV_FOLDER'], filename)

    file.save(filepath)

    signature = generate_signature(user.private_key,filepath2)
    embed_signature(signature,filepath,filepath2)

    return {'message': 'Image uploaded successfully', 'filename': filename}, 201

@app.route('/uploads/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



if __name__ == '__main__':
    app.run(debug=False,port=2000)
