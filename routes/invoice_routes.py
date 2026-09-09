from flask import (
    Blueprint,
    jsonify,
    g,
)

from auth import jwt_required
from services import InvoiceService


def create_invoices_blueprint(
    db_manager,
    jwt_manager
):

    invoices_bp = Blueprint(
        "invoices",
        __name__,
        url_prefix="/invoices"
    )

    @invoices_bp.route("",methods=["GET"])
    @jwt_required(jwt_manager)
    def get_invoices():

        session = db_manager.create_session()

        try:
            service = InvoiceService(session)

            invoices = service.get_invoices(
                user_id=g.user["id"],
                role=g.user["role"]
            )

            return jsonify([
                invoice.to_dict()
                for invoice in invoices
            ]), 200

        finally:
            session.close()

    @invoices_bp.route("/<string:invoice_number>",methods=["GET"])
    @jwt_required(jwt_manager)
    def get_invoice(invoice_number):

        session = db_manager.create_session()

        try:
            service = InvoiceService(session)

            invoice = (
                service.get_invoice_by_number(
                    invoice_number=invoice_number,
                    user_id=g.user["id"],
                    role=g.user["role"]
                )
            )

            return jsonify(
                invoice.to_dict()
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

    return invoices_bp