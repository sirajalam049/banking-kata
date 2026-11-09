import concurrent.futures
from datetime import datetime, timezone
import pytest
from decimal import Decimal
from src.exceptions import FailedToApplyOperationAfterRetriesError
from src.service import Account


def test_incorrect_deposit():
    acc = Account()
    transaction_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError) as e:
        acc.apply_deposit(Decimal(-100), transaction_date)
    assert str(e.value) == "Deposit amount must be positive"
    assert acc.current_balance == Decimal(0)
    assert len(acc.transactions) == 0


def test_incorrect_withdraw():
    acc = Account()
    transaction_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError) as e:
        acc.apply_withdraw(Decimal(-100), transaction_date)
    assert str(e.value) == "Withdrawal amount must be positive"
    assert acc.current_balance == Decimal(0)
    assert len(acc.transactions) == 0

def test_incorrect_withdraw_insufficient_funds():
    acc = Account()
    transaction_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError) as e:
        acc.apply_withdraw(Decimal(100), transaction_date)
    assert str(e.value) == "Insufficient funds"
    assert acc.current_balance == Decimal(0)
    assert len(acc.transactions) == 0


def test_concurrent_optimistic_deposit_operations_without_self_retry():
    acc = Account(processing_delay=0.02)
    transaction_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    with pytest.raises(FailedToApplyOperationAfterRetriesError) as e: # Only one transaction should be successful
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(lambda amount: acc.deposit_optimistic_without_self_retry(amount, transaction_date), [Decimal(100), Decimal(50)]))
    assert acc.current_balance in [Decimal(50), Decimal(100)] # Only one transaction should be successful
    assert len(acc.transactions) == 1 # Only one transaction should be successful

def test_concurrent_optimistic_withdraw_operations_without_self_retry():
    acc = Account(processing_delay=0.01)
    transaction_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    acc.apply_deposit(Decimal(500), transaction_date)
    with pytest.raises(FailedToApplyOperationAfterRetriesError) as e: # Only one transaction should be successful
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(lambda amount: acc.withdraw_optimistic_without_self_retry(amount, transaction_date), [Decimal(100), Decimal(50)]))
    assert acc.current_balance in [Decimal(400), Decimal(450)] # Only one transaction should be successful
    assert len(acc.transactions) == 2 # Only one transaction should (+1 the initial deposit) be successful