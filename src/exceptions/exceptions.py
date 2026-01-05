class AppError(Exception):
    """Base class for all application-specific exceptions."""
    pass

class InvalidDTOError(AppError):
    """Raised when a Data Transfer Object (DTO) is invalid or malformed."""
    pass