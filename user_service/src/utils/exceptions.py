# class UserServiceException(Exception):
#     """Base exception for user service"""
#     pass

# class UserNotFoundError(UserServiceException):
#     """User not found"""
#     pass

# class UserAlreadyExistsError(UserServiceException):
#     """User already exists"""
#     pass

# class InvalidCredentialsError(UserServiceException):
#     """Invalid credentials"""
#     pass

class UserServiceException(Exception):
    status_code = 400
    message = "User service error"

class UserNotFoundError(Exception):
    status_code = 404
    message = "User not found"

class InvalidCredentialsError(UserServiceException):
    status_code = 401
    message = "Invalid email or password"

class UserAlreadyExistsError(UserServiceException):
    status_code = 400
    message = "User already exists"
