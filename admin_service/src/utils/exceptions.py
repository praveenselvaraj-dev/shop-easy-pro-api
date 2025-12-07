class AdminServiceException(Exception):
    status_code: int = 400
    message: str = "Admin service error"

    def __init__(self, message: str = None):
        if message:
            self.message = message
        super().__init__(self.message)


class NotFoundError(AdminServiceException):
    status_code = 404
    message = "Resource not found"


class ForbiddenError(AdminServiceException):
    status_code = 403
    message = "Forbidden"


class UnauthorizedError(AdminServiceException):
    status_code = 401
    message = "Unauthorized"


class InvalidRequestError(AdminServiceException):
    status_code = 400
    message = "Invalid request"
