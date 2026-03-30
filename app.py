from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage for users
users = []

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/users', methods=['POST'])
def create_user():
    user = request.get_json()
    users.append(user)
    return jsonify(user), 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    if user_id < len(users):
        return jsonify(users[user_id])
    return jsonify({'error': 'User not found'}), 404

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if user_id < len(users):
        users[user_id] = request.get_json()
        return jsonify(users[user_id])
    return jsonify({'error': 'User not found'}), 404

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_id < len(users):
        deleted = users.pop(user_id)
        return jsonify(deleted)
    return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)