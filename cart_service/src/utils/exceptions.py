class CartServiceException(Exception):
    status_code: int = 400
    message: str = "Cart service error"

    def __init__(self, message: str = None):
        if message:
            self.message = message
        super().__init__(self.message)


class ProductNotFoundError(CartServiceException):
    status_code = 404
    message = "Product not found"


class NotEnoughStockError(CartServiceException):
    status_code = 400
    message = "Not enough stock"


class CartItemNotFoundError(CartServiceException):
    status_code = 404
    message = "Cart item not found"


class UnauthorizedError(CartServiceException):
    status_code = 401
    message = "Unauthorized"

class ForbiddenError(CartServiceException):
    status_code = 403
    message = "Forbidden"
