from flask import (
    Blueprint,
    request,
    jsonify,
    g,
)

from auth import jwt_required
from services import CartService, CheckoutService


def create_carts_blueprint(
    db_manager,
    jwt_manager,
    cache_manager
):
    carts_bp = Blueprint(
        "carts",
        __name__,
        url_prefix="/carts"
    )

    @carts_bp.route("/active", methods=["GET"])
    @jwt_required(jwt_manager)
    def get_active_cart():

        session = db_manager.create_session()

        try:
            service = CartService(session)

            cart = service.get_active_cart(
                user_id=g.user["id"]
            )

            return jsonify(
                cart.to_dict()
            ), 200

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        finally:
            session.close()

    @carts_bp.route("",methods=["GET"])
    @jwt_required(jwt_manager)
    def get_carts():

        session = db_manager.create_session()

        try:
            service = CartService(session)

            carts = service.get_user_carts(
                user_id=g.user["id"]
            )

            return jsonify([
                cart.to_dict()
                for cart in carts
            ]), 200

        finally:
            session.close()

    @carts_bp.route("/<int:cart_id>",methods=["GET"])
    @jwt_required(jwt_manager)
    def get_cart(cart_id):

        session = db_manager.create_session()

        try:
            service = CartService(session)

            cart = service.get_cart(
                cart_id=cart_id,
                user_id=g.user["id"]
            )

            return jsonify(
                cart.to_dict()
            ), 200

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        except PermissionError as error:
            return jsonify({
                "message": str(error)
            }), 403

        finally:
            session.close()

    @carts_bp.route("", methods=["POST"])
    @jwt_required(jwt_manager)
    def create_cart():

        session = db_manager.create_session()

        try:
            service = CartService(session)

            cart = service.create_cart(
                user_id=g.user["id"]
            )

            return jsonify(
                cart.to_dict()
            ), 201

        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 409

        finally:
            session.close()

    @carts_bp.route("/<int:cart_id>/items",methods=["POST"])
    @jwt_required(jwt_manager)
    def add_product(cart_id):

        data = request.get_json()

        if not data:
            return jsonify({
                "message": "Request body is required."
            }), 400

        if (
            data.get("product_id") is None
            or data.get("quantity") is None
        ):
            return jsonify({
                "message":
                    "product_id and quantity are required."
            }), 400

        session = db_manager.create_session()

        try:
            service = CartService(session)

            cart = service.add_product(
                cart_id=cart_id,
                product_id=data["product_id"],
                quantity=data["quantity"],
                user_id=g.user["id"]
            )

            return jsonify(
                cart.to_dict()
            ), 200

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        except PermissionError as error:
            return jsonify({
                "message": str(error)
            }), 403

        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 400

        finally:
            session.close()

    @carts_bp.route("/<int:cart_id>/items/<int:product_id>",methods=["PUT"])
    @jwt_required(jwt_manager)
    def update_product_quantity(cart_id, product_id):

        data = request.get_json()

        if not data:
            return jsonify({
                "message": "Request body is required."
            }), 400

        if data.get("quantity") is None:
            return jsonify({
                "message": "Quantity is required."
            }), 400

        session = db_manager.create_session()

        try:
            service = CartService(session)

            cart = service.update_product_quantity(
                cart_id=cart_id,
                product_id=product_id,
                quantity=data["quantity"],
                user_id=g.user["id"]
            )

            return jsonify(
                cart.to_dict()
            ), 200

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        except PermissionError as error:
            return jsonify({
                "message": str(error)
            }), 403

        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 400

        finally:
            session.close()

    @carts_bp.route("/<int:cart_id>/items/<int:product_id>",methods=["DELETE"])
    @jwt_required(jwt_manager)
    def remove_product(
        cart_id,
        product_id
    ):

        session = db_manager.create_session()

        try:
            service = CartService(session)

            cart = service.remove_product(
                cart_id=cart_id,
                product_id=product_id,
                user_id=g.user["id"]
            )

            return jsonify(
                cart.to_dict()
            ), 200

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        except PermissionError as error:
            return jsonify({
                "message": str(error)
            }), 403

        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 400

        finally:
            session.close()

    @carts_bp.route("/<int:cart_id>",methods=["DELETE"])
    @jwt_required(jwt_manager)
    def abandon_cart(cart_id):

        session = db_manager.create_session()

        try:
            service = CartService(session)

            cart = service.abandon_cart(
                cart_id=cart_id,
                user_id=g.user["id"]
            )

            return jsonify(
                cart.to_dict()
            ), 200

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        except PermissionError as error:
            return jsonify({
                "message": str(error)
            }), 403

        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 400

        finally:
            session.close()

    @carts_bp.route("/<int:cart_id>/checkout",methods=["POST"])
    @jwt_required(jwt_manager)
    def checkout(cart_id):

        data = request.get_json()

        if not data:
            return jsonify({
                "message": "Request body is required."
            }), 400

        required_fields = [
            "billing_address_id",
            "payment_method",
            "payment_reference"
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
            service = CheckoutService(session, cache_manager)

            invoice = service.checkout(
                cart_id=cart_id,
                user_id=g.user["id"],
                billing_address_id=data[
                    "billing_address_id"
                ],
                payment_method=data[
                    "payment_method"
                ],
                payment_reference=data[
                    "payment_reference"
                ]
            )

            return jsonify({
                "message": "Checkout completed successfully.",
                "invoice_number": invoice.invoice_number,
                "total": float(invoice.total)
            }), 201

        except LookupError as error:
            return jsonify({
                "message": str(error)
            }), 404

        except PermissionError as error:
            return jsonify({
                "message": str(error)
            }), 403

        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 400

        finally:
            session.close()

    return carts_bp