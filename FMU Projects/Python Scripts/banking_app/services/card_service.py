from uuid import UUID

class CardService:
    def __init__(self, card_repository):
        self.card_repository = card_repository

    def issue_card(self):
        pass

    def get_card_by_card_id(self, card_id: UUID):
        pass

    def get_card_by_account_id(self, customer_id: UUID):
        pass

    def get_card_by_account_number(self, customer_id: UUID):
        pass

    def get_all_cards(self):
        pass

    def activate_card(self, card_id: UUID):
        pass

    def deactivate_card(self, card_id):
        pass

    def freeze_card(self, card_id):
        pass

    def unfreeze_card(self, card_id):
        pass

    def cancel_card(self, card_id):
        pass

    def get_card_status_by_id(self, card_id):
        pass

    def search_card(self):
        pass