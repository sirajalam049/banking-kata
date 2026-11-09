class InsufficientFundsError(ValueError):
    pass

class DepositAmountMustBePositiveError(ValueError):
    pass

class WithdrawalAmountMustBePositiveError(ValueError):
    pass

class FailedToApplyOperationAfterRetriesError(Exception):
    pass
