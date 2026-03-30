import jwt
import datetime
from functools import wraps
from flask import Flask, jsonify, request

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your-secret-key'  # In production, use environment variable

# In-memory storage for users
users = []

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split(" ")[1]
            if not token:
                return jsonify({'message': 'Token is missing!'}), 401
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                if data.get('role') != role:
                    return jsonify({'message': 'Role required!'}), 403
            except:
                return jsonify({'message': 'Token is invalid!'}), 401
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route('/users', methods=['GET'])
@token_required
def get_users():
    return jsonify(users)

@app.route('/users', methods=['POST'])
@token_required
def create_user():
    user = request.get_json()
    users.append(user)
    return jsonify(user), 201

@app.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    if user_id < len(users):
        return jsonify(users[user_id])
    return jsonify({'error': 'User not found'}), 404

@app.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    if user_id < len(users):
        users[user_id] = request.get_json()
        return jsonify(users[user_id])
    return jsonify({'error': 'User not found'}), 404

@app.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    if user_id < len(users):
        deleted = users.pop(user_id)
        return jsonify(deleted)
    return jsonify({'error': 'User not found'}), 404

@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Username and password required!'}), 400
    # Hardcoded credentials for demonstration
    if auth['username'] == 'admin' and auth['password'] == 'password':
        token = jwt.encode({
            'user': auth['username'],
            'role': 'admin',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    elif auth['username'] == 'user' and auth['password'] == 'password':
        token = jwt.encode({
            'user': auth['username'],
            'role': 'user',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials!'}), 401

@app.route('/admin', methods=['GET'])
@token_required
@role_required('admin')
def admin_route():
    return jsonify({'message': 'Welcome admin!'})

@app.route('/user', methods=['GET'])
@token_required
@role_required('user')
def user_route():
    return jsonify({'message': 'Welcome user!'})

if __name__ == '__main__':
    app.run(debug=True)