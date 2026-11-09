from datetime import datetime, timezone
from decimal import Decimal
from time import sleep
from typing import List
from threading import Lock
from src.model import Transaction, TransactionType
from logging import getLogger

logger = getLogger(__name__)

class Account:

    _transactions: List[Transaction]
    _current_balance: Decimal
    _last_transaction_date: datetime
    _lock: Lock

    MAX_RETRIES = 3

    def __init__(self):
        self._transactions = []
        self._current_balance = Decimal(0)
        self._last_transaction_date = datetime.now(timezone.utc)
        self._lock = Lock()

    def deposit_pessimistic(self, amount: Decimal, transaction_date: datetime = datetime.now(timezone.utc)) -> Transaction:
        with self._lock:
            return self.deposit(amount, self._current_balance, transaction_date)

    def withdraw_pessimistic(self, amount: Decimal, transaction_date: datetime = datetime.now(timezone.utc)) -> Transaction:
        with self._lock:
            return self.withdraw(amount, self._current_balance, transaction_date)

    def deposit_optimistic_with_self_retry(self, amount: Decimal, transaction_date: datetime = datetime.now(timezone.utc)) -> Transaction:
        for _ in range(1, self.MAX_RETRIES + 1):
            try:
                return self.deposit(amount, self._current_balance, transaction_date)
            except ValueError:
                logger.warning(f"Retrying {_} of {self.MAX_RETRIES}")
                continue
        raise ValueError(f"Failed to deposit after {self.MAX_RETRIES} retries") # pragma: no cover

    def withdraw_optimistic_with_self_retry(self, amount: Decimal, transaction_date: datetime = datetime.now(timezone.utc)) -> Transaction:
        for _ in range(1, self.MAX_RETRIES + 1):
            try:
                return self.withdraw(amount, self._current_balance, transaction_date)
            except ValueError:
                logger.info(f"Retrying {_} of {self.MAX_RETRIES}")
                continue
        raise ValueError(f"Failed to withdraw after {self.MAX_RETRIES} retries") # pragma: no cover

    def deposit(self, amount: Decimal, prev_balance: Decimal, transaction_date: datetime = datetime.now(timezone.utc)) -> Transaction:
        if amount <= Decimal(0):
            raise ValueError("Deposit amount must be positive")
        sleep(0.01) # Simulating processing time
        if prev_balance != self._current_balance:
            raise ValueError(f"Concurrent transactions detected. Please retry")
        self._current_balance = round(self._current_balance + amount, 2)
        txn = Transaction(amount, TransactionType.DEPOSIT, self._current_balance, transaction_date)
        self._transactions.append(txn)
        return txn

    def withdraw(self, amount: Decimal, prev_balance: Decimal, transaction_date: datetime = datetime.now(timezone.utc)) -> Transaction:
        if amount <= Decimal(0):
            raise ValueError("Withdrawal amount must be positive")
        sleep(0.01) # Simulating processing time
        if prev_balance != self._current_balance:
            raise ValueError(f"Concurrent transactions detected. Please retry.")
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
