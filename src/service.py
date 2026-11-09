from datetime import datetime, timezone
from decimal import Decimal
from typing import List
from threading import Lock
from src.model import Transaction, TransactionType

class Account:

    _transactions: List[Transaction]
    _current_balance: Decimal
    _last_transaction_date: datetime
    _lock: Lock

    def __init__(self):
        self._transactions = []
        self._current_balance = Decimal(0)
        self._last_transaction_date = datetime.now(timezone.utc)
        self._lock = Lock()
    
    def deposit(self, amount: Decimal, current_transactions: int, transaction_date: datetime = datetime.now(timezone.utc)) -> Transaction:
        if amount <= Decimal(0):
            raise ValueError("Deposit amount must be positive")

        with self._lock:
            if current_transactions != len(self._transactions):
                raise ValueError("Concurrent transactions detected. Please retry.")

        self._current_balance = round(self._current_balance + amount, 2)
        txn = Transaction(amount, TransactionType.DEPOSIT, self._current_balance, transaction_date)
        self._transactions.append(txn)
        return txn

    def withdraw(self, amount: Decimal, current_transactions: int, transaction_date: datetime = datetime.now(timezone.utc)) -> Transaction:
        if amount <= Decimal(0):
            raise ValueError("Withdrawal amount must be positive")

        with self._lock:
            if current_transactions != len(self._transactions):
                raise ValueError("Concurrent transactions detected. Please retry.")

        self._current_balance = round(self._current_balance - amount, 2)
        txn = Transaction(amount, TransactionType.WITHDRAWAL, self._current_balance, transaction_date)
        self._transactions.append(txn)
        return txn

    def print_statement(self) -> str:
        return "\n".join([f"{transaction.transaction_date.strftime('%d/%m/%Y')} {transaction.transaction_type.value} {transaction.amount:.2f} {transaction.running_balance:.2f}" for transaction in self._transactions])
    
    @property
    def current_balance(self) -> Decimal:
        return self._current_balance
    
    @property
    def transactions(self) -> List[Transaction]:
        return self._transactions