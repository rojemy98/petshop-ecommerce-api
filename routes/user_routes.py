from flask import Blueprint, jsonify, request, g

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
    @jwt_required(jwt_manager, db_manager)
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

    @user_bp.route("/me", methods=["GET"])
    @jwt_required(jwt_manager, db_manager)
    def get_current_user():

        session = db_manager.create_session()

        try:
            service = UserService(session)

            user_id = g.user.get("id")

            if user_id is None:
                return jsonify({
                    "message": "Invalid user information in token."
                }), 401

            user = service.get_user_by_id(user_id)

            return jsonify({
                "user": user.to_dict()
            }), 200

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        finally:
            session.close()

    @user_bp.route("/me", methods=["PUT"])
    @jwt_required(jwt_manager, db_manager)
    def update_current_user():

        data = request.get_json(silent=True)

        if not isinstance(data, dict) or not data:
            return jsonify({
                "message": "Request body is required."
            }), 400

        allowed_fields = {
            "name",
            "last_name",
            "email"
        }

        invalid_fields = set(data) - allowed_fields

        if invalid_fields:
            return jsonify({
                "message": (
                    "Invalid fields: "
                    + ", ".join(sorted(invalid_fields))
                )
            }), 400

        for field, value in data.items():

            if not isinstance(value, str) or not value.strip():
                return jsonify({
                    "message": f"{field} must be a non-empty string."
                }), 400

            max_length = 150 if field == "email" else 100

            if len(value.strip()) > max_length:
                return jsonify({
                    "message": f"{field} exceeds the maximum length."
                }), 400

        session = db_manager.create_session()

        try:
            service = UserService(session)

            user_id = g.user.get("id")

            if user_id is None:
                return jsonify({
                    "message": "Invalid user information in token."
                }), 401

            user = service.update_user(
                user_id,
                data
            )

            return jsonify({
                "message": "Profile updated successfully.",
                "user": user.to_dict()
            }), 200

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

    
    @user_bp.route("/me/password", methods=["PUT"])
    @jwt_required(jwt_manager, db_manager)
    def change_current_user_password():

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "message": "Invalid request body."
            }), 400

        required_fields = {
            "current_password",
            "new_password",
            "confirm_password"
        }

        if set(data.keys()) != required_fields:
            return jsonify({
                "message": (
                    "Required fields: current_password, "
                    "new_password, confirm_password."
                )
            }), 400

        current_password = data["current_password"]
        new_password = data["new_password"]
        confirm_password = data["confirm_password"]

        if not all(
            isinstance(value, str) and value
            for value in (
                current_password,
                new_password,
                confirm_password
            )
        ):
            return jsonify({
                "message": "All password fields are required."
            }), 400

        if new_password != confirm_password:
            return jsonify({
                "message": "New passwords do not match."
            }), 400

        session = db_manager.create_session()

        try:
            service = UserService(session)

            user_id = g.user.get("id")

            if user_id is None:
                return jsonify({
                    "message": "Invalid user information in token."
                }), 401

            service.change_password(
                user_id,
                current_password,
                new_password
            )

            return jsonify({
                "message": "Password updated successfully."
            }), 200

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


    @user_bp.route("/<int:user_id>",methods=["GET"])
    @jwt_required(jwt_manager, db_manager)
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
    @jwt_required(jwt_manager, db_manager)
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

    @user_bp.route("/<int:user_id>", methods=["PUT"])
    @jwt_required(jwt_manager, db_manager)
    @role_required("ADMIN")
    def update_user(user_id):

        data = request.get_json(silent=True)

        if not isinstance(data, dict) or not data:
            return jsonify({
                "message": "Request body is required."
            }), 400

        session = db_manager.create_session()

        try:
            service = UserService(session)

            user = service.update_user(
                user_id,
                data
            )

            return jsonify({
                "message": "User updated successfully.",
                "user": user.to_dict()
            }), 200

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
    @jwt_required(jwt_manager, db_manager)
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

    @user_bp.route(
        "/<int:user_id>/revoke-sessions",
        methods=["POST"]
    )
    @jwt_required(jwt_manager, db_manager)
    @role_required("ADMIN")
    def revoke_user_sessions(user_id):

        session = db_manager.create_session()

        try:
            service = UserService(session)

            service.revoke_user_sessions(user_id)

            return jsonify({
                "message": "User sessions revoked successfully."
            }), 200

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        finally:
            session.close()

    return user_bp