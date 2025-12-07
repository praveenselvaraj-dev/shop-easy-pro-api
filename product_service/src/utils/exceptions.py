class ProductServiceException(Exception):
    status_code = 400
    message = "Product service error"

class ProductNotFoundError(ProductServiceException):
    status_code = 404
    message = "Product not found"

class InsufficientStockError(ProductServiceException):
    status_code = 400
    message = "Insufficient stock"

class UnauthorizedError(ProductServiceException):
    status_code = 403
    message = "Not authorized"
