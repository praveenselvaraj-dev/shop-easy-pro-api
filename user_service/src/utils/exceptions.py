class UserServiceException(Exception):
    """Base exception for user service"""
    pass

class UserNotFoundError(UserServiceException):
    """User not found"""
    pass

class UserAlreadyExistsError(UserServiceException):
    """User already exists"""
    pass

class InvalidCredentialsError(UserServiceException):
    """Invalid credentials"""
    pass