from flask import Blueprint, request, jsonify
from backend.app.models.User import User
from flask_jwt_extended import create_access_token
from datetime import timedelta

auth_bp = Blueprint('auth_routes', __name__, url_prefix='/api')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'name': user.name
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
