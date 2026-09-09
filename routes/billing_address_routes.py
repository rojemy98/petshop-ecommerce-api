from flask import Blueprint, request, jsonify, g

from auth import jwt_required
from services import BillingAddressService


def create_billing_addresses_blueprint(
    db_manager,
    jwt_manager
):

    addresses_bp = Blueprint(
        "billing_addresses",
        __name__,
        url_prefix="/billing-addresses"
    )

    @addresses_bp.route("", methods=["GET"])
    @jwt_required(jwt_manager)
    def get_addresses():

        session = db_manager.create_session()

        try:
            service = BillingAddressService(
                session
            )

            addresses = service.get_user_addresses(
                g.user["id"]
            )

            return jsonify([
                address.to_dict()
                for address in addresses
            ]), 200

        finally:
            session.close()

    @addresses_bp.route("/<int:address_id>",methods=["GET"])
    @jwt_required(jwt_manager)
    def get_address(address_id):

        session = db_manager.create_session()

        try:
            service = BillingAddressService(
                session
            )

            address = service.get_address(
                address_id=address_id,
                user_id=g.user["id"]
            )

            return jsonify(
                address.to_dict()
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

    @addresses_bp.route("", methods=["POST"])
    @jwt_required(jwt_manager)
    def create_address():

        data = request.get_json()

        if not data:
            return jsonify({
                "message": "Request body is required."
            }), 400

        required_fields = {
            "address",
            "city",
            "province",
            "postal_code",
            "country"
        }

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
            service = BillingAddressService(
                session
            )

            address = service.create_address(
                data=data,
                user_id=g.user["id"]
            )

            return jsonify(
                address.to_dict()
            ), 201

        except ValueError as error:
            return jsonify({
                "message": str(error)
            }), 400

        finally:
            session.close()

    @addresses_bp.route("/<int:address_id>",methods=["PUT"])
    @jwt_required(jwt_manager)
    def update_address(address_id):

        data = request.get_json()

        if not data:
            return jsonify({
                "message": "Request body is required."
            }), 400

        session = db_manager.create_session()

        try:
            service = BillingAddressService(
                session
            )

            address = service.update_address(
                address_id=address_id,
                data=data,
                user_id=g.user["id"]
            )

            return jsonify(
                address.to_dict()
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

    @addresses_bp.route("/<int:address_id>",methods=["DELETE"])
    @jwt_required(jwt_manager)
    def delete_address(address_id):

        session = db_manager.create_session()

        try:
            service = BillingAddressService(
                session
            )

            service.delete_address(
                address_id=address_id,
                user_id=g.user["id"]
            )

            return "", 204

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

    return addresses_bp