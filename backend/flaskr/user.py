import json
from flask import Blueprint, request, Response
from flaskr.db_project import db, User
from http import HTTPStatus
from flask_jwt_extended import create_access_token,  create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from flaskr import jwt
from datetime import timedelta, datetime
import random
from .mail_service import mail_service



auth_bp = Blueprint('auth', __name__, url_prefix='/dev.dudorov.com/api/auth/users')

token_blacklist = set()

@auth_bp.post('/tokens')
def login():
    try:
        data = request.get_json()

        if not data or 'email' not in data or 'password' not in data:
            return Response(
                json.dumps({"success": False,
                    "status": -1,
                    "data": None,
                    "error": "Missing email or password"}),
                HTTPStatus.UNPROCESSABLE_ENTITY,
                mimetype="application/json")
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            return Response(
                json.dumps({"success": False,
                    "status": -1,
                    "data": None,
                    "error": "Invalid email or password"}),
                HTTPStatus.NOT_FOUND,
                mimetype="application/json")

        code = str(random.randint(100000, 999999))
        user.twofa_code = code
        user.twofa_code_expires = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        mail_service.send_2fa_code(user.email, code)
        print(code)


        temp_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(minutes=10)
        )

        return Response(
            json.dumps({
                "success": True,
                "status": 0,
                "data": {
                    "temp_token": temp_token,
                    "message": "2FA код отправлен"
                },
                "error": None
            }),
            HTTPStatus.OK,
            mimetype="application/json"
        )
    except Exception as e:
        return Response(
            json.dumps({
                "success": False,
                "status": -1,
                "data": None,
                "error": str(e),
            }),
            HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json"
        )


@auth_bp.route('/verify-2fa', methods=['POST'])
@jwt_required()
def verify_2fa():
    try:

        user = User.query.get(int(get_jwt_identity()))
        if not user:
            return Response(
                json.dumps({
                    "success": False,
                    "status": -1,
                    "data": None,
                    "error": "User not found"
                }),
                HTTPStatus.NOT_FOUND,
                mimetype="application/json"
            )

        code = str(request.json.get('code', ''))

        if not code.isdigit() or len(code) != 6:
            return Response(
                json.dumps({"success": False,
                    "status": -1,
                    "data": None,
                    "error": "Code must be 6 digits"}),
                HTTPStatus.BAD_REQUEST,
                mimetype="application/json")

        if (not user.twofa_code or
        user.twofa_code != code or
        datetime.utcnow() > user.twofa_code_expires
        ):
            return Response(
                json.dumps({"success": False,
                            "status": -1,
                            "data": None,
                            "error": "Invalid code"}),
                HTTPStatus.NOT_FOUND,
                mimetype="application/json")
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        user.twofa_code = None
        db.session.commit()

        return Response(
            json.dumps(
                {
                    "success": True,
                    "status": 0,
                    "data": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "id": user.id,
                    }}
            ),
            HTTPStatus.OK,
            mimetype="application/json",
        )
    except Exception as e:
        return Response(
            json.dumps({
                "success": False,
                "status": -1,
                "data": None,
                "error": str(e),
            }),
            HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json"
        )




@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in token_blacklist


@auth_bp.route('/tokens', methods=['DELETE'])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]  # Уникальный идентификатор токена
        token_blacklist.add(jti)

        return Response(
            json.dumps({
                "success": True,
                "status": 0,
                "data": None,
                "error": ""
            }),
            HTTPStatus.OK,
            mimetype="application/json",
            )
    except Exception as e:
        return Response(
            json.dumps({
                "success": False,
                "status": -1,
                "data": None,
                "error": str(e)
            }),
            HTTPStatus.INTERNAL_SERVER_ERROR,
            mimetype="application/json"
        )

@auth_bp.get('/me')
@jwt_required()
def get_current_user():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return Response(
                json.dumps({
                    "success": False,
                    "error": "User not found"
                }),
                HTTPStatus.NOT_FOUND,
                mimetype="application/json",
            )
    except Exception as e:
        return Response(
                json.dumps({
                    "success": False,
                    "error": str(e)
                }),
                HTTPStatus.INTERNAL_SERVER_ERROR,
                mimetype="application/json",
            )
    return Response(
            json.dumps({
                "email": user.email,
                "artist": user.username,

            }),
            HTTPStatus.OK,
            mimetype="application/json",
        )


@auth_bp.route('/validate-access-token', methods=['GET'])
@jwt_required(refresh=True)
def validate_access_token():
    try:
        jti = get_jwt()['jti']

        if jti in token_blacklist:
            return Response(
                json.dumps({
                    "success": False,
                    "status": -1,
                    "data": None,
                    "error": "Refresh token revoked"
                }),
                HTTPStatus.UNAUTHORIZED,
                mimetype="application/json"
            )
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return Response(
                json.dumps({
                    "success": False,
                    "error": "User not found"
                }),
                HTTPStatus.NOT_FOUND,
                mimetype="application/json",
            )
        return Response(
            json.dumps({
                "success": True,
                "status": 0,
                "data": {
                    "access_token_valid": True,
                },
                "error": ""
            }),
            HTTPStatus.OK,
            mimetype="application/json"
        )

    except Exception as e:

        return Response(
                json.dumps({
                    "success": False,
                    "status": -1,
                    "data": False,
                    "error": str(e)
                }),
                HTTPStatus.INTERNAL_SERVER_ERROR,
                mimetype="application/json",
            )



@auth_bp.route('/tokens', methods=['PUT'])
@jwt_required(refresh=True)
def refresh_access_token():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return Response(
                json.dumps({
                    "success": False,
                    "error": "User not found"
                }),
                HTTPStatus.NOT_FOUND,
                mimetype="application/json",
            )

        new_access_token = create_access_token(
            identity=str(user_id))
        new_refresh_token = create_refresh_token(identity=str(user_id))

        return Response(
            json.dumps({
                "success": True,
                "status": 0,
                "data": {
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token
                },
                "error": ""
            }),
            HTTPStatus.OK,
            mimetype="application/json"
        )

    except Exception as e:
        return Response(
                json.dumps({
                    "success": False,
                    "status": -1,
                    "data": None,
                    "error": str(e)
                }),
                HTTPStatus.INTERNAL_SERVER_ERROR,
                mimetype="application/json",
            )