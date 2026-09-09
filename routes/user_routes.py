from flask import Blueprint, jsonify, request

from auth.decorators import jwt_required, role_required
from services.user_service import UserService


def create_user_blueprint(
    db_manager,
    jwt_manager
):

    user_bp = Blueprint(
        "users",
        __name__,
        url_prefix="/users"
    )

    @user_bp.route("", methods=["GET"])
    @jwt_required(jwt_manager)
    @role_required("ADMIN")
    def get_users():

        session = db_manager.create_session()

        try:
            service = UserService(session)

            users = service.get_users()

            return jsonify([
                user.to_dict()
                for user in users
            ]), 200

        finally:
            session.close()

    @user_bp.route("/<int:user_id>",methods=["GET"])
    @jwt_required(jwt_manager)
    @role_required("ADMIN")
    def get_user(user_id):

        session = db_manager.create_session()

        try:
            service = UserService(session)

            user = service.get_user_by_id(
                user_id
            )

            return jsonify(
                user.to_dict()
            ), 200

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        finally:
            session.close()

    @user_bp.route("", methods=["POST"])
    @jwt_required(jwt_manager)
    @role_required("ADMIN")
    def create_user():

        data = request.get_json() or {}

        required_fields = {
            "name",
            "last_name",
            "email",
            "password",
        }

        missing_fields = (
            required_fields
            - data.keys()
        )

        if missing_fields:
            return jsonify({
                "message": (
                    "Missing required fields: "
                    + ", ".join(
                        sorted(missing_fields)
                    )
                )
            }), 400

        session = db_manager.create_session()

        try:
            service = UserService(session)

            user = service.create_user(
                name=data["name"],
                last_name=data["last_name"],
                email=data["email"],
                password=data["password"],
                role=data.get(
                    "role",
                    "CLIENT"
                ),
            )

            return jsonify(
                user.to_dict()
            ), 201

        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 400

        finally:
            session.close()

    @user_bp.route("/<int:user_id>",methods=["PUT"])
    @jwt_required(jwt_manager)
    @role_required("ADMIN")
    def update_user(user_id):

        data = request.get_json() or {}

        if not data:
            return jsonify({
                "message": (
                    "Request body is required."
                )
            }), 400

        session = db_manager.create_session()

        try:
            service = UserService(session)

            user = service.update_user(
                user_id,
                data,
            )

            return jsonify(
                user.to_dict()
            ), 200

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 400

        finally:
            session.close()

    @user_bp.route("/<int:user_id>",methods=["DELETE"])
    @jwt_required(jwt_manager)
    @role_required("ADMIN")
    def delete_user(user_id):

        session = db_manager.create_session()

        try:
            service = UserService(session)

            service.delete_user(
                user_id
            )

            return "", 204

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 400

        finally:
            session.close()

    return user_bp