from datetime import datetime, timezone
from decimal import Decimal
from src.service import Account
from src.model import TransactionType

def test_first_deposit():
    acc = Account()
    transaction_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    acc.apply_deposit(Decimal(100), transaction_date)
    assert acc.current_balance == Decimal(100)
    assert len(acc.transactions) == 1
    assert acc.transactions[0].amount == Decimal(100)
    assert acc.transactions[0].transaction_type == TransactionType.DEPOSIT
    assert acc.transactions[0].running_balance == Decimal(100)
    assert acc.transactions[0].transaction_date == transaction_date


def test_first_withdraw():
    acc = Account()
    transaction_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    acc.apply_deposit(Decimal(100), transaction_date)
    acc.apply_withdraw(Decimal(50), transaction_date)
    assert acc.current_balance == Decimal(50)
    assert len(acc.transactions) == 2
    assert acc.transactions[1].amount == Decimal(50)
    assert acc.transactions[1].transaction_type == TransactionType.WITHDRAWAL
    assert acc.transactions[1].running_balance == Decimal(50)
    assert acc.transactions[1].transaction_date == transaction_date


def test_multiple_operations():
    acc = Account()
    transaction_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    acc.apply_deposit(Decimal(100), transaction_date)
    acc.apply_withdraw(Decimal(50), transaction_date)
    acc.apply_deposit(Decimal(25), transaction_date)
    assert acc.current_balance == Decimal(75)
    assert len(acc.transactions) == 3
    assert acc.transactions[2].amount == Decimal(25)
    assert acc.transactions[2].transaction_type == TransactionType.DEPOSIT
    assert acc.transactions[2].running_balance == Decimal(75)
    assert acc.transactions[2].transaction_date == transaction_date


def test_print_statement():
    acc = Account()
    transaction_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    acc.apply_deposit(Decimal(100), transaction_date)
    acc.apply_withdraw(Decimal(50), transaction_date)
    header = f"{'Date':<15} {'Amount':<10} {'Balance':<10}"
    transactions = [
        f"{transaction_date.strftime('%d.%m.%Y'):<15} {'+ 100.00':<10} {'100.00':<10}",
        f"{transaction_date.strftime('%d.%m.%Y'):<15} {'- 50.00':<10} {'50.00':<10}",
    ]
    assert acc.print_statement() == f"{header}\n{transactions[0]}\n{transactions[1]}"