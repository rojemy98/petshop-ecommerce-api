from sqlalchemy.orm import Session

from models import BillingAddress
from repositories import BillingAddressesRepository


class BillingAddressService:

    def __init__(self, session: Session):
        self.session = session
        self.repository = BillingAddressesRepository(
            session
        )

    def get_user_addresses(
        self,
        user_id: int
    ) -> list[BillingAddress]:

        return self.repository.get_by_user_id(
            user_id
        )

    def get_address(
        self,
        address_id: int,
        user_id: int
    ) -> BillingAddress:

        address = self.repository.get_by_id(
            address_id
        )

        if address is None:
            raise LookupError(
                "Billing address not found."
            )

        if address.user_id != user_id:
            raise PermissionError(
                "You do not have access to this "
                "billing address."
            )

        return address

    def create_address(
        self,
        data: dict,
        user_id: int
    ) -> BillingAddress:

        address = BillingAddress(
            user_id=user_id,
            address=data["address"].strip(),
            city=data["city"].strip(),
            province=data["province"].strip(),
            postal_code=data["postal_code"],
            country=data["country"].strip()
        )

        try:
            self.repository.create(address)
            self.session.commit()

            return address

        except Exception:
            self.session.rollback()
            raise

    def update_address(
        self,
        address_id: int,
        data: dict,
        user_id: int
    ) -> BillingAddress:

        address = self.get_address(
            address_id,
            user_id
        )

        allowed_fields = {
            "address",
            "city",
            "province",
            "postal_code",
            "country"
        }

        invalid_fields = set(data) - allowed_fields

        if invalid_fields:
            raise ValueError(
                f"Fields cannot be updated: "
                f"{', '.join(invalid_fields)}."
            )

        for field, value in data.items():

            if isinstance(value, str):
                value = value.strip()

                if not value:
                    raise ValueError(
                        f"{field} cannot be empty."
                    )

            setattr(address, field, value)

        try:
            self.repository.update(address)
            self.session.commit()

            return address

        except Exception:
            self.session.rollback()
            raise

    def delete_address(
        self,
        address_id: int,
        user_id: int
    ) -> None:

        address = self.get_address(
            address_id,
            user_id
        )

        try:
            self.repository.delete(address)
            self.session.commit()

        except Exception:
            self.session.rollback()
            raise
        