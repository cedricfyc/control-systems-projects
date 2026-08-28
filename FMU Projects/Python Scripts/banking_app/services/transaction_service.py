from uuid import UUID

class TransactionService:
    def __init__(self, transaction_repository):
        self.transaction_repository = transaction_repository

    def deposit(self, account_id: UUID):
        pass

    def withdraw(self, account_id: UUID):
        pass

    def transfer(self, from_account_id: UUID, to_account_id: UUID):
        pass

    def get_transaction_history(self):
        pass