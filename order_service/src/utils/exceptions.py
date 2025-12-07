class OrderServiceException(Exception):
    status_code: int = 400
    message: str = "Order service error"

    def __init__(self, message: str = None):
        if message:
            self.message = message
        super().__init__(self.message)


class OrderNotFoundError(OrderServiceException):
    status_code = 404
    message = "Order not found"


class UnauthorizedError(OrderServiceException):
    status_code = 401
    message = "Unauthorized"


class ForbiddenError(OrderServiceException):
    status_code = 403
    message = "Forbidden"


class InvalidOrderError(OrderServiceException):
    status_code = 400
    message = "Invalid order request"

class InvalidRequestError(OrderServiceException):
    status_code = 400
    message = "Invalid request"