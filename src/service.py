from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from src.model import Transaction, TransactionType

class Account:

    transactions: List[Transaction] = []
    current_balance: Decimal = Decimal(0)
    
    def deposit(self, amount: Decimal, transaction_date: datetime = datetime.now(timezone.utc)) -> Transaction:
        self.current_balance = round(self.current_balance + amount, 2)
        txn = Transaction(amount, TransactionType.DEPOSIT, self.current_balance, transaction_date)
        self.transactions.append(txn)
        return txn

    def withdraw(self, amount: Decimal, transaction_date: datetime = datetime.now(timezone.utc)) -> Transaction:
        self.current_balance = round(self.current_balance - amount, 2)
        txn = Transaction(amount, TransactionType.WITHDRAWAL, self.current_balance, transaction_date)
        self.transactions.append(txn)
        return txn

    def print_statement(self) -> str:
        return "\n".join([f"{transaction.transaction_date.strftime('%d/%m/%Y')} {transaction.transaction_type.value} {transaction.amount:.2f} {transaction.running_balance:.2f}" for transaction in self.transactions])
    
