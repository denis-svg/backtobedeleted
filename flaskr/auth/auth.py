from flask import (
    Blueprint, request, jsonify
)

from flaskr.auth.LocalAuth import LocalAuth

bp = Blueprint('auth', __name__, url_prefix='/auth')
local_auth = LocalAuth()

@bp.route('/register', methods=('GET', 'POST'))
def register():
    result = local_auth.registerUser(request)
    status = result.pop("status")
    return jsonify(result), status

@bp.route('/login', methods=('GET', 'POST'))
def login():
    result = local_auth.loginUser(request)
    status = result.pop("status")
    # if the status is 200 then I will include the token in the header
    if status == 200:
        token = result.pop("token")
        response = jsonify(result)
        response.headers['Authorization'] = f'Bearer {token}'
        return response
    
    return jsonify(result), status

@bp.route("/protected", methods=('GET', 'POST'))
@local_auth.tokenRequired(request, role="admin")
def protected():
    return jsonify({"protected":True})

@bp.route("/unprotected", methods=('GET', 'POST'))
def unprotected():
    return jsonify({"unprotected":True})