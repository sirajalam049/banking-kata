from datetime import datetime
from decimal import Decimal
from src.service import Account

if __name__ == "__main__":
    acc=Account()
    acc.apply_deposit(Decimal(100), datetime(2026, 1, 1, 12, 0, 0))
    acc.apply_withdraw(Decimal(50), datetime(2026, 1, 1, 12, 0, 0))
    acc.apply_deposit(Decimal(120), datetime(2026, 1, 1, 12, 0, 0))
    acc.apply_deposit(Decimal(60), datetime(2026, 1, 1, 12, 0, 0))
    acc.apply_deposit(Decimal(30), datetime(2026, 1, 1, 12, 0, 0))
    acc.apply_withdraw(Decimal(70), datetime(2026, 1, 1, 12, 0, 0))
    print(acc.print_statement())