# E-commerce Admin API

A FastAPI-based backend for managing products, inventory, and sales for an e-commerce admin dashboard.

## Features
- Product management (CRUD)
- Inventory management (CRUD, status, low stock alerts, history)
- Sales management (CRUD, analytics, revenue analysis)
- Modern, auto-generated OpenAPI docs

## Tech Stack
- Python 3.8+
- FastAPI
- SQLAlchemy
- Alembic (migrations)
- MySQL
- Pydantic

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd ecommerce-admin
```


2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/ecommerce_admin
SECRET_KEY=your-secret-key
```

4. Initialize the database:
```bash
alembic upgrade head
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## Database Schema

### Product
| Field         | Type    | Description         |
|--------------|---------|---------------------|
| id           | int     | Primary key         |
| name         | string  | Product name        |
| description  | string  | Product description |
| price        | float   | Product price       |
| created_at   | datetime| Created timestamp   |
| updated_at   | datetime| Updated timestamp   |

### Inventory
| Field              | Type    | Description                |
|--------------------|---------|----------------------------|
| id                 | int     | Primary key                |
| product_id         | int     | Foreign key to Product     |
| quantity           | int     | Current stock quantity     |
| low_stock_threshold| int     | Low stock alert threshold  |
| created_at         | datetime| Created timestamp          |
| updated_at         | datetime| Updated timestamp          |

### Sale
| Field        | Type    | Description                |
|--------------|---------|----------------------------|
| id           | int     | Primary key                |
| product_id   | int     | Foreign key to Product     |
| quantity     | int     | Quantity sold              |
| total_amount | float   | Total sale amount          |
| sale_date    | datetime| Date/time of sale          |
| created_at   | datetime| Created timestamp          |
| updated_at   | datetime| Updated timestamp          |

## API Endpoints

### Products
- `GET /api/products` - List all products
- `POST /api/products` - Create a product
- `GET /api/products/{product_id}` - Get a product
- `PUT /api/products/{product_id}` - Update a product
- `DELETE /api/products/{product_id}` - Delete a product

### Inventory
- `GET /api/inventory` - List all inventory items
- `POST /api/inventory` - Create inventory for a product
- `GET /api/inventory/{inventory_id}` - Get inventory item
- `PUT /api/inventory/{inventory_id}` - Update inventory item
- `DELETE /api/inventory/{inventory_id}` - Delete inventory item
- `GET /api/inventory/status` - Get inventory status (with low stock filter)
- `GET /api/inventory/alerts` - Get low stock alerts
- `GET /api/inventory/history` - Get inventory change history (all)
- `GET /api/inventory/history/{inventory_id}` - Get inventory change history for a specific item

### Sales
- `GET /api/sales` - List all sales
- `POST /api/sales` - Create a sale
- `GET /api/sales/{sale_id}` - Get a sale
- `PUT /api/sales/{sale_id}` - Update a sale
- `DELETE /api/sales/{sale_id}` - Delete a sale
- `GET /api/sales/revenue/product/{product_id}` - Revenue analytics for a product
- `GET /api/sales/revenue/daily` - Get daily revenue (with optional start_date and end_date)
- `GET /api/sales/revenue/weekly` - Get weekly revenue (with optional start_date and end_date)
- `GET /api/sales/revenue/monthly` - Get monthly revenue (with optional start_date and end_date)
- `GET /api/sales/revenue/annual` - Get annual revenue (with optional start_date and end_date)
- `GET /api/sales/revenue/compare` - Compare revenue between two periods (requires period1_start, period1_end, period2_start, period2_end)

## Example Requests

### Create Product
```json
POST /api/products
{
  "name": "Sample Product",
  "description": "A test product",
  "price": 19.99
}
```

### Create Inventory
```json
POST /api/inventory
{
  "product_id": 1,
  "quantity": 100,
  "low_stock_threshold": 10
}
```

### Create Sale
```json
POST /api/sales
{
  "product_id": 1,
  "quantity": 2,
  "total_amount": 39.98,
  "sale_date": "2024-03-19T12:00:00Z"
}
```

### Get Inventory Status
```
GET /api/inventory/status
```

### Get Low Stock Alerts
```
GET /api/inventory/alerts
```

### Get Inventory History
```
GET /api/inventory/history
GET /api/inventory/history/{inventory_id}
```

### Get Product Revenue Analytics
```
GET /api/sales/revenue/product/{product_id}
```

### Get Revenue Analytics
```
# Get daily revenue
GET /api/sales/revenue/daily?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z

# Get weekly revenue
GET /api/sales/revenue/weekly?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z

# Get monthly revenue
GET /api/sales/revenue/monthly?start_date=2024-01-01T00:00:00Z&end_date=2024-12-31T23:59:59Z

# Get annual revenue
GET /api/sales/revenue/annual?start_date=2024-01-01T00:00:00Z&end_date=2024-12-31T23:59:59Z

# Compare revenue between periods
GET /api/sales/revenue/compare?period1_start=2024-01-01T00:00:00Z&period1_end=2024-01-31T23:59:59Z&period2_start=2024-02-01T00:00:00Z&period2_end=2024-02-29T23:59:59Z
```

## Postman Collection
Import the provided `postman_collection.json` into Postman to test all endpoints.

## License

MIT License 