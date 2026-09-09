from flask import (
    Blueprint,
    request,
    jsonify,
    g
)

from auth import (
    jwt_required,
    role_required
)

from services import ReturnService


def create_returns_blueprint(
    db_manager,
    jwt_manager,
    cache_manager
):

    returns_bp = Blueprint(
        "returns",
        __name__,
        url_prefix="/returns"
    )


    @returns_bp.route("", methods=["GET"])
    @jwt_required(jwt_manager)
    def get_returns():

        session = db_manager.create_session()

        try:
            service = ReturnService(
                session,
                cache_manager
            )

            returns = service.get_returns(
                user_id=g.user["id"],
                role=g.user["role"],
            )

            return jsonify([
                return_request.to_dict()
                for return_request in returns
            ]), 200

        finally:
            session.close()

    @returns_bp.route("/<int:return_id>", methods=["GET"])
    @jwt_required(jwt_manager)
    def get_return(return_id):

        session = db_manager.create_session()

        try:
            service = ReturnService(
                session,
                cache_manager
            )

            return_request = service.get_return_by_id(
                return_id=return_id,
                user_id=g.user["id"],
                role=g.user["role"],
            )

            return jsonify(
                return_request.to_dict()
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

    @returns_bp.route("/invoice/<string:invoice_number>",methods=["POST"])
    @jwt_required(jwt_manager)
    def create_return(invoice_number):

        data = request.get_json()

        if not data:
            return jsonify({
                "message": "Request body is required."
            }), 400

        if data.get("reason") is None:
            return jsonify({
                "message": "Reason is required."
            }), 400

        if data.get("products") is None:
            return jsonify({
                "message": "Products are required."
            }), 400

        session = db_manager.create_session()

        try:
            service = ReturnService(session, cache_manager)

            return_request = (
                service.create_return(
                    invoice_number=invoice_number,
                    user_id=g.user["id"],
                    reason=data["reason"],
                    products=data["products"]
                )
            )

            return jsonify(
                return_request.to_dict()
            ), 201

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

    @returns_bp.route("/<int:return_id>/status",methods=["PUT"])
    @jwt_required(jwt_manager)
    @role_required("ADMIN")
    def update_return_status(return_id):

        data = request.get_json()

        if not data:
            return jsonify({
                "message": "Request body is required."
            }), 400

        if data.get("status") is None:
            return jsonify({
                "message": "Status is required."
            }), 400

        session = db_manager.create_session()

        try:
            service = ReturnService(session, cache_manager)

            return_request = (
                service.update_return_status(
                    return_id=return_id,
                    new_status=data["status"]
                )
            )

            return jsonify(
                return_request.to_dict()
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

    return returns_bp