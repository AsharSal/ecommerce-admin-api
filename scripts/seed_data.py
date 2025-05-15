import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.models import Category, Product, Inventory, Sale
from datetime import datetime, timedelta
import random

def seed_data():
    db = SessionLocal()
    try:
        # Create categories
        categories = [
            Category(name="Electronics", description="Electronic devices and accessories"),
            Category(name="Clothing", description="Apparel and fashion items"),
            Category(name="Home & Kitchen", description="Home goods and kitchen appliances"),
            Category(name="Books", description="Books and publications"),
            Category(name="Sports", description="Sports equipment and accessories")
        ]
        db.add_all(categories)
        db.commit()

        # Create products
        products = []
        for category in categories:
            for i in range(5):  # 5 products per category
                product = Product(
                    name=f"{category.name} Product {i+1}",
                    description=f"Description for {category.name} Product {i+1}",
                    price=random.uniform(10.0, 1000.0),
                    category_id=category.id
                )
                products.append(product)
        
        db.add_all(products)
        db.commit()

        # Create inventory
        for product in products:
            inventory = Inventory(
                product_id=product.id,
                quantity=random.randint(0, 100),
                low_stock_threshold=10
            )
            db.add(inventory)
        db.commit()

        # Create sales
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        for product in products:
            # Create 10-20 sales per product
            for _ in range(random.randint(10, 20)):
                quantity = random.randint(1, 5)
                sale = Sale(
                    product_id=product.id,
                    quantity=quantity,
                    total_amount=product.price * quantity,
                    sale_date=start_date + timedelta(
                        seconds=random.randint(0, int((end_date - start_date).total_seconds()))
                    )
                )
                db.add(sale)
        db.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data() 