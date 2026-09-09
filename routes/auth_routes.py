from flask import Blueprint, request, jsonify, g

from auth import jwt_required
from services import AuthService


def create_auth_blueprint(
    db_manager,
    jwt_manager
):
    auth_bp = Blueprint(
        "auth",
        __name__,
        url_prefix="/auth"
    )

    @auth_bp.route("/register", methods=["POST"])
    def register():
        data = request.get_json()

        if not data:
            return jsonify({
                "message": "Request body is required."
            }), 400

        required_fields = [
            "name",
            "last_name",
            "email",
            "password"
        ]

        missing_fields = [
            field
            for field in required_fields
            if not data.get(field)
        ]

        if missing_fields:
            return jsonify({
                "message": "Missing required fields.",
                "fields": missing_fields
            }), 400

        session = db_manager.create_session()

        try:
            auth_service = AuthService(
                session,
                jwt_manager
            )

            token = auth_service.register(
                name=data["name"],
                last_name=data["last_name"],
                email=data["email"],
                password=data["password"]
            )

            return jsonify({
                "message": "User registered successfully.",
                "access_token": token
            }), 201

        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 400

        finally:
            session.close()

    @auth_bp.route("/login", methods=["POST"])
    def login():
        data = request.get_json()

        if not data:
            return jsonify({
                "message": "Request body is required."
            }), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({
                "message": "Email and password are required."
            }), 400

        session = db_manager.create_session()

        try:
            auth_service = AuthService(
                session,
                jwt_manager
            )

            token = auth_service.login(
                email=email,
                password=password,
                ip_address=request.remote_addr or "unknown"
            )

            return jsonify({
                "message": "Login successful.",
                "access_token": token
            }), 200

        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 401

        finally:
            session.close()

    @auth_bp.route("/me", methods=["GET"])
    @jwt_required(jwt_manager)
    def me():
        return jsonify({
            "user": g.user
        }), 200

    return auth_bp