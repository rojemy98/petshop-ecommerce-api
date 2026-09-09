from flask import Blueprint, request, jsonify, g

from auth import jwt_required, role_required
from services import ProductService

import json

from config import CACHE_TTL


def create_products_blueprint(
    db_manager,
    jwt_manager,
    cache_manager
):
    products_bp = Blueprint(
        "products",
        __name__,
        url_prefix="/products"
    )

    @products_bp.route("", methods=["GET"])
    @jwt_required(jwt_manager)
    def get_products():

        cache_key = "products:all"

        cached_data = cache_manager.get_data(
            cache_key
        )

        if cached_data is not None:

            print("CACHE HIT:", cache_key)

            return jsonify(
                json.loads(cached_data)
            ), 200

        print("CACHE MISS:", cache_key)

        session = db_manager.create_session()

        try:
            service = ProductService(session)

            products = service.get_available_products()

            products_data = [
                product.to_dict()
                for product in products
            ]

            cache_manager.store_data(
                cache_key,
                json.dumps(products_data),
                CACHE_TTL
            )

            return jsonify(
                products_data
            ), 200

        finally:
            session.close()

    @products_bp.route("/<int:product_id>",methods=["GET"])
    @jwt_required(jwt_manager)
    def get_product(product_id):

        cache_key = f"product:{product_id}"

        cached_data = cache_manager.get_data(
            cache_key
        )

        if cached_data is not None:

            print("CACHE HIT:", cache_key)

            return jsonify(
                json.loads(cached_data)
            ), 200

        print("CACHE MISS:", cache_key)

        session = db_manager.create_session()

        try:
            service = ProductService(session)

            product = service.get_product_by_id(
                product_id
            )

            product_data = product.to_dict()

            cache_manager.store_data(
                cache_key,
                json.dumps(product_data),
                CACHE_TTL
            )

            return jsonify(
                product_data
            ), 200

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        finally:
            session.close()

    @products_bp.route("", methods=["POST"])
    @jwt_required(jwt_manager)
    @role_required("ADMIN")
    def create_product():

        data = request.get_json()

        if not data:
            return jsonify({
                "message": "Request body is required."
            }), 400

        required_fields = [
            "name",
            "price",
            "stock"
        ]

        missing_fields = [
            field
            for field in required_fields
            if data.get(field) is None
        ]

        if missing_fields:
            return jsonify({
                "message": "Missing required fields.",
                "fields": missing_fields
            }), 400

        session = db_manager.create_session()

        try:
            service = ProductService(session)

            product = service.create_product(
                data=data,
                user_id=g.user["id"]
            )

            cache_manager.delete_data(
                "products:all"
            )

            return jsonify(
                product.to_dict()
            ), 201

        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 400

        finally:
            session.close()

    @products_bp.route("/<int:product_id>",methods=["PUT"])
    @jwt_required(jwt_manager)
    @role_required("ADMIN")
    def update_product(product_id):

        data = request.get_json()

        if not data:
            return jsonify({
                "message": "Request body is required."
            }), 400

        session = db_manager.create_session()

        try:
            service = ProductService(session)

            product = service.update_product(
                product_id=product_id,
                data=data,
                user_id=g.user["id"]
            )

            cache_manager.delete_data(
                f"product:{product_id}"
            )

            cache_manager.delete_data(
                "products:all"
            )

            return jsonify(
                product.to_dict()
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

    @products_bp.route("/<int:product_id>",methods=["DELETE"])
    @jwt_required(jwt_manager)
    @role_required("ADMIN")
    def delete_product(product_id):

        session = db_manager.create_session()

        try:
            service = ProductService(session)

            service.delete_product(
                product_id=product_id,
                user_id=g.user["id"]
            )

            cache_manager.delete_data(
                f"product:{product_id}"
            )

            cache_manager.delete_data(
                "products:all"
            )

            return "", 204

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        finally:
            session.close()

    return products_bp