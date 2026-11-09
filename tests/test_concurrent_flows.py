import concurrent.futures
from datetime import datetime, timezone
from decimal import Decimal
from src.service import Account



def test_concurrent_optimistic_deposit_operations_with_self_retry():
    acc = Account(processing_delay=0.01)
    transaction_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(lambda amount: acc.deposit_optimistic_with_self_retry(amount, transaction_date), [Decimal(100), Decimal(50)]))
    assert acc.current_balance == Decimal(150) # Both transactions should be successful
    assert len(acc.transactions) == 2 # Both transactions should be successful

def test_concurrent_optimistic_withdraw_operations_with_self_retry():
    acc = Account(processing_delay=0.01)
    transaction_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    acc.apply_deposit(Decimal(500), transaction_date)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(lambda amount: acc.withdraw_optimistic_with_self_retry(amount, transaction_date), [Decimal(100), Decimal(50)]))
    assert acc.current_balance == Decimal(350) # Both transactions should be successful
    assert len(acc.transactions) == 3 # Both transactions should be successful


def test_concurrent_pessimistic_deposit_operations():
    acc = Account(processing_delay=0.01)
    transaction_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(lambda amount: acc.deposit_pessimistic(amount, transaction_date), [Decimal(100), Decimal(50)]))
    assert acc.current_balance == Decimal(150) # Both transactions should be successful
    assert len(acc.transactions) == 2 # Both transactions should be successful

def test_concurrent_pessimistic_withdraw_operations():
    acc = Account(processing_delay=0.01)
    transaction_date = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    acc.apply_deposit(Decimal(500), transaction_date)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(lambda amount: acc.withdraw_pessimistic(amount, transaction_date), [Decimal(100), Decimal(50)]))
    assert acc.current_balance == Decimal(350) # Both transactions should be successful
    assert len(acc.transactions) == 3 # Both transactions should be successful