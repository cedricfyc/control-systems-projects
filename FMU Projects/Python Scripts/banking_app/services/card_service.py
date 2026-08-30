from uuid import UUID
from typing import List

from banking_app.models.card import Card


class CardService:
    def __init__(self, card_repository):
        self.card_repository = card_repository

    # -----------------------------------------------------------
    #                          CREATE
    # -----------------------------------------------------------


    def issue_card(self) -> Card:
        pass

    # -----------------------------------------------------------
    #                          READ
    # -----------------------------------------------------------

    def get_card_by_card_id(self, card_id: UUID) -> Card:
        pass

    def get_card_by_account_id(self, customer_id: UUID) -> Card:
        pass

    def get_card_by_account_number(self, customer_id: UUID) -> Card:
        pass

    def get_all_cards(self) -> List[Card]:
        pass

    def get_card_status_by_id(self, card_id) -> List[Card]:
        pass

    def search_card(self) -> List[Card]:
        pass

    # -----------------------------------------------------------
    #                          UPDATE
    # -----------------------------------------------------------

    def activate_card(self, card_id: UUID):
        pass

    def deactivate_card(self, card_id: UUID):
        pass

    def freeze_card(self, card_id: UUID) -> Card:
        pass

    def unfreeze_card(self, card_id: UUID):
        pass

    def cancel_card(self, card_id: UUID):
        pass


    # -----------------------------------------------------------
    #                          DELETE
    # -----------------------------------------------------------


    def delete_card(self, card_id: UUID):
        pass