A modular, scalable FastAPI backend for an e-commerce application supporting:

- **User Service**
- **Product Service**
- **Cart Service**
- **Order / Checkout Service**
- **Admin Service**

This project follows a clean architecture with routers, services, repositories, and schemas.

##Features

**User Service**
- User registration & login (JWT authentication)
- Profile management
- Token verification
- Secure password hashing

**Product Service**
- Create/update/delete products (Admin only)
- Get single product / all products
- Category & search filters, sort
- Product image management

**Cart Service**
- Add to cart
- Update quantity
- Remove item
- Auto-validate stock before updating

**Order / Checkout Service**
- Create order
- Validate stock
- Place order and reduce inventory
- Get order history for users

**Admin Service**
- Dashboard overview
- Manage products
- View all orders, sales analytics
