from functools import wraps

import jwt
from flask import request, jsonify, g

from services.jwt_manager import JWTManager


def jwt_required(jwt_manager: JWTManager):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            authorization = request.headers.get(
                "Authorization"
            )

            if not authorization:
                return jsonify({
                    "message":
                        "Authorization header is required."
                }), 401

            parts = authorization.split()

            if (
                len(parts) != 2
                or parts[0].lower() != "bearer"
            ):
                return jsonify({
                    "message":
                        "Invalid authorization header."
                }), 401

            token = parts[1]

            try:
                payload = jwt_manager.decode(token)

            except jwt.ExpiredSignatureError:
                return jsonify({
                    "message": "Token has expired."
                }), 401

            except jwt.InvalidTokenError:
                return jsonify({
                    "message": "Invalid token."
                }), 401

            g.user = payload

            return function(*args, **kwargs)

        return wrapper

    return decorator


def role_required(required_role: str):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            user = getattr(g, "user", None)

            if user is None:
                return jsonify({
                    "message":
                        "Authentication is required."
                }), 401

            if user.get("role") != required_role:
                return jsonify({
                    "message":
                        "You do not have permission "
                        "to access this resource."
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator