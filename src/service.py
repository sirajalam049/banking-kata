from datetime import datetime, timezone
from decimal import Decimal
from time import sleep
from typing import List
from threading import RLock
from src.model import Transaction, TransactionType
from logging import getLogger

logger = getLogger(__name__)

class Account:

    _transactions: List[Transaction]
    _current_balance: Decimal
    _lock: RLock
    _processing_delay: float
    _acc_version:int

    MAX_RETRIES = 3

    def __init__(self, processing_delay: float = 0):
        self._transactions = []
        self._current_balance = Decimal(0)
        self._lock = RLock()
        self._acc_version = 0
        self._processing_delay = processing_delay

    def deposit_pessimistic(self, amount: Decimal, transaction_date: datetime) -> Transaction:
        with self._lock:
            return self.deposit(amount, self._acc_version, transaction_date)

    def withdraw_pessimistic(self, amount: Decimal, transaction_date: datetime) -> Transaction:
        with self._lock:
            return self.withdraw(amount, self._acc_version, transaction_date)

    def deposit_optimistic_with_self_retry(self, amount: Decimal, transaction_date: datetime) -> Transaction:
        for _ in range(1, self.MAX_RETRIES + 1):
            try:
                return self.deposit(amount, self._acc_version, transaction_date)
            except ValueError:
                logger.warning(f"Retrying {_} of {self.MAX_RETRIES}")
                continue
        raise ValueError(f"Failed to deposit after {self.MAX_RETRIES} retries") # pragma: no cover

    def withdraw_optimistic_with_self_retry(self, amount: Decimal, transaction_date: datetime) -> Transaction:
        for _ in range(1, self.MAX_RETRIES + 1):
            try:
                return self.withdraw(amount, self._acc_version, transaction_date)
            except ValueError:
                logger.info(f"Retrying {_} of {self.MAX_RETRIES}")
                continue
        raise ValueError(f"Failed to withdraw after {self.MAX_RETRIES} retries") # pragma: no cover

    def deposit(self, amount: Decimal, version: int, transaction_date: datetime) -> Transaction:
        if amount <= Decimal(0):
            raise ValueError("Deposit amount must be positive")
        if self._processing_delay:
            sleep(self._processing_delay)
        with self._lock: #Making read and write atomic
            if version != self._acc_version:
                raise ValueError(f"Concurrent transactions detected. Please retry")
            self._current_balance = round(self._current_balance + amount, 2)
            self._acc_version += 1
            txn = Transaction(amount, TransactionType.DEPOSIT, self._current_balance, transaction_date)
            self._transactions.append(txn)
            return txn

    def withdraw(self, amount: Decimal, version: int, transaction_date: datetime) -> Transaction:
        if amount <= Decimal(0):
            raise ValueError("Withdrawal amount must be positive")
        if self._processing_delay:
            sleep(self._processing_delay)
        with self._lock: #Making read and write atomic
            if amount > self._current_balance:
                raise ValueError("Insufficient funds")
            if version != self._acc_version:
                raise ValueError(f"Concurrent transactions detected. Please retry.")
            self._current_balance = round(self._current_balance - amount, 2)
            self._acc_version += 1
            txn = Transaction(amount, TransactionType.WITHDRAWAL, self._current_balance, transaction_date)
            self._transactions.append(txn)
            return txn

    def print_statement(self) -> str:
        header = "\nDate\t\t\tAmount\t\t\tBalance"
        transactions = []
        def _format_transaction(txn: Transaction) -> str:
            sign = "+" if txn.transaction_type == TransactionType.DEPOSIT else "-"
            txn_date = txn.transaction_date.strftime('%d.%m.%Y')
            txn_amount = f"{sign} {txn.amount:.2f}"
            txn_balance = f"{txn.running_balance:.2f}"
            return f"{txn_date}\t\t{txn_amount}\t\t{txn_balance}"

        for txn in self._transactions:
            transactions.append(_format_transaction(txn))
        return f"{header}\n{'\n'.join(transactions)}"
    
    @property
    def current_balance(self) -> Decimal:
        return self._current_balance
    
    @property
    def transactions(self) -> List[Transaction]:
        return self._transactions

    @property
    def acc_version(self) -> int:
        return self._acc_version
