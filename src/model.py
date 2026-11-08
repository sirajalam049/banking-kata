from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

from enum import Enum


class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


@dataclass(frozen=True)
class Transaction:
    amount: Decimal
    transaction_type: TransactionType
    running_balance: Decimal
    transaction_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))