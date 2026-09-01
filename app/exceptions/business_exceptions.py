class BusinessException(Exception):
    """Base exception for business logic errors."""

    pass


class ClaimNotFoundException(BusinessException):
    """Raised when a claim cannot be found."""

    pass


class ClaimNotSubmittedException(BusinessException):
    """Raised when a claim is not in submitted status."""

    pass


class PolicyNotFoundException(BusinessException):
    """Raised when a policy cannot be found."""

    pass


class PolicyNotActiveException(BusinessException):
    """Raised when a policy is not active."""

    pass