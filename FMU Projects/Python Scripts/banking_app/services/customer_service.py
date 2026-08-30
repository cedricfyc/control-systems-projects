from banking_app.models.account import Account
from banking_app.models.customer import Customer, Address
from banking_app.models.user import User, PermissionChecker
from banking_app.repositories.customer_repo import CustomerRepository

from banking_app.utils.enums import CustomerStatus
from banking_app.utils.enums import Permission

from uuid import UUID
from typing import List, Optional
from datetime import date
import re


class CustomerService:

    def __init__(self,
                 current_user: User,
                 customer_repository: CustomerRepository):
        self.current_user = current_user
        self.customer_repository = customer_repository
        self.permission_checker = PermissionChecker()

    #-----------------------------------------------------------
    #                          CREATE
    #-----------------------------------------------------------

    def register_customer(self,
                          first_name: str,
                          middle_name: Optional[str],
                          last_name: str,
                          date_of_birth: date,
                          national_id: str,
                          email: Optional[str],
                          phone_number: Optional[str],
                          address_city: str,
                          address_country: str,
                          address_state: Optional[str],
                          address_street: Optional[str],
                          address_zip: Optional[str],
                          kyc_verified: Optional[bool]
                          ) -> Optional[Customer]:

        # Validate all inputs
        self.validate_all_inputs(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            national_id=national_id,
            email=email,
            phone_number=phone_number,
            address_city=address_city,
            address_country=address_country,
            address_zip=address_zip
        )


        # Create address object
        customer_address = Address(
            street=address_street,
            city=address_city,
            country=address_country,
            state=address_state,
            zip=address_zip)

        # Check for permission first
        if self.require_view_customer_permission():
            # create customer using constructor
            created_customer = Customer(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                national_id=national_id,
                email=email,
                phone_number=phone_number,
                address=customer_address,
                kyc_verified=kyc_verified
            )
            created_customer = self.customer_repository.create(created_customer)
            return created_customer

        else:
            return None

    # -----------------------------------------------------------
    #                          READ
    # -----------------------------------------------------------

    def get_customer(self, customer_id: UUID) -> Customer:
        pass

    def search_customer(self,
            customer_id: Optional[UUID] = None,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            address_country: Optional[str] = None,
            customer_status: Optional[CustomerStatus] = None,
            limit: int = 100,
            offset: int = 0,
    ) -> List[Customer]:

        self.validate_search_inputs(first_name=first_name, address_country=address_country, last_name=last_name)

        query_results = self.customer_repository.search(
            customer_id=customer_id,
            first_name=first_name,
            last_name=last_name,
            address_country=address_country,
            customer_status=customer_status,
            limit=limit, offset=offset
        )

        return query_results

    def get_customer_accounts(self) -> List[Account]:
        self.require_view_account_permission()
        pass

    def get_customers_by_status(self, customer_status: CustomerStatus) -> List[Customer]:
        self.require_view_customer_permission()
        pass

    # -----------------------------------------------------------
    #                          UPDATE
    # -----------------------------------------------------------

    def update_customer_details(self,
                          first_name: str,
                          middle_name: Optional[str],
                          last_name: str,
                          date_of_birth: date,
                          national_id: str,
                          email: Optional[str],
                          phone_number: Optional[str],
                          address_city: str,
                          address_country: str,
                          address_state: Optional[str],
                          address_street: Optional[str],
                          address_zip: Optional[str],
                          kyc_verified: Optional[bool]
                          ) -> Optional[Customer]:

        # Validate all inputs
        self.validate_all_inputs(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            national_id=national_id,
            email=email,
            phone_number=phone_number,
            address_city=address_city,
            address_country=address_country,
            address_zip=address_zip
        )
        self.require_update_customer_permission()
        pass

    def deactivate_customer(self,
                            customer_id: UUID,
                            customer_first_name: str,
                            customer_middle_name: str,
                            customer_last_name: str) -> Customer:
        self.require_update_customer_permission()
        pass


    # -----------------------------------------------------------
    #                          DELETE
    # -----------------------------------------------------------


    def delete_customer(self, first_name: str, last_name: str, customer_id: Optional[UUID] = None) -> None:
        self.require_delete_customer_permission()
        pass

    # -----------------------------------------------------------
    #                          HELPER
    # -----------------------------------------------------------

    # Permission handlers
    def require_view_account_permission(self) -> bool:
        return PermissionChecker.require_permission(
                self.current_user,
                Permission.VIEW_ANY_ACCOUNT)


    def require_create_customer_permission(self) -> bool:
        return PermissionChecker.require_permission(
                self.current_user,
                Permission.CREATE_CUSTOMER)

    def require_view_customer_permission(self) -> bool:
        return PermissionChecker.require_permission(
                self.current_user,
                Permission.VIEW_ANY_CUSTOMER)

    def require_update_customer_permission(self) -> bool:
        return PermissionChecker.require_permission(
                self.current_user,
                Permission.UPDATE_CUSTOMER)

    def require_delete_customer_permission(self) -> bool:
        return PermissionChecker.require_permission(
                self.current_user,
                Permission.DELETE_CUSTOMER)


    # Validation handlers
    def validate_all_inputs(self,
                            first_name: str,
                            middle_name: Optional[str],
                            last_name: str,
                            date_of_birth: date,
                            national_id: str,
                            email: Optional[str],
                            phone_number: Optional[str],
                            address_city: str,
                            address_country: str,
                            address_zip: Optional[str],
                            ):
        # Name validation
        if not first_name or not first_name.strip():
            raise ValueError("First name is required")
        if not last_name or not last_name.strip():
            raise ValueError("Last name is required")

        name_pattern = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'\-\s]+$")
        for field_name, value in (("first_name", first_name),
                                  ("middle_name", middle_name),
                                  ("last_name", last_name)):
            if value and not name_pattern.match(value.strip()):
                raise ValueError(f"{field_name} contains invalid characters.")

        # Date of birth validation
        if not isinstance(date_of_birth, date):
            raise ValueError("Date of birth must be a valid date.")

        today = date.today()
        if date_of_birth > today:
            raise ValueError("Date of birth cannot be in the future.")

        age = today.year - date_of_birth.year - (
                (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
        )

        if age < 18:
            raise ValueError("Customer must be at least 18 years old to register.")

        # National ID validation
        if not national_id or not national_id.strip():
            raise ValueError("national_id is required.")
        if not re.match(r"^[A-Za-z0-9\-]{4,20}$", national_id.strip()):
            raise ValueError("national_id format is invalid.")

        # Email validation
        if email is not None:
            email = email.strip()
            email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
            if not email_pattern.match(email):
                raise ValueError("email is not a valid email address.")

        # Phone number
        if phone_number is not None:
            phone_number = phone_number.strip()
            # Accepts optional leading +, digits, spaces, dashes, parentheses
            phone_pattern = re.compile(r"^\+?[0-9][0-9\s\-()]{6,19}$")

            if not phone_pattern.fullmatch(phone_number):
                raise ValueError("phone_number is not a valid phone number.")

        # At least one contact method needs to be available.
        if not email and not phone_number:
            raise ValueError("Either email or phone number must be provided.")

        # Address validation
        if not address_city or not address_city.strip():
            raise ValueError("address_city is required.")
        if not address_country or not address_country.strip():
            raise ValueError("address_country is required.")
        # Zip validation
        if address_zip is not None and not re.match(r"^[A-Za-z0-9\s\-]{2,12}$", address_zip.strip()):
            raise ValueError("address_zip format is invalid.")

        # Check if customer exists on the persistence layer
        if self.customer_repository.exists_by_details(first_name=first_name,
                                                      middle_name=middle_name,
                                                      last_name=last_name,
                                                      date_of_birth=date_of_birth,
                                                      national_id=national_id):
            raise ValueError("A customer with the described identity already exists.")


    def validate_search_inputs(self,first_name: Optional[str],
                                      last_name: Optional[str],
                                      address_country: Optional[str]):

        if not first_name or not first_name.strip():
            raise ValueError("First name is required")
        if not last_name or not last_name.strip():
            raise ValueError("Last name is required")

        name_pattern = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'\-\s]+$")
        for field_name, value in (("first_name", first_name),
                                  ("last_name", last_name)):
            if value and not name_pattern.match(value.strip()):
                raise ValueError(f"{field_name} contains invalid characters.")

        if address_country is not None and not re.match(r"^[A-Za-z0-9\-]{4,20}$", address_country.strip()):
            raise ValueError("Country address is invalid.")