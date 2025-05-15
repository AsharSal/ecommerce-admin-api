from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.models import Inventory, Product
from app.schemas.schemas import (
    InventoryResponse, InventoryCreate, InventoryUpdate,
    InventoryStatus, InventoryHistory
)

router = APIRouter()

@router.get("/", response_model=List[InventoryResponse])
def get_inventory(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None
):
    """Get all inventory items with optional product filter"""
    query = db.query(Inventory)
    if product_id:
        query = query.filter(Inventory.product_id == product_id)
    return query.offset(skip).limit(limit).all()

@router.get("/status", response_model=List[InventoryStatus])
def get_inventory_status(
    db: Session = Depends(get_db),
    low_stock_only: bool = False
):
    """Get current inventory status with optional low stock filter"""
    query = db.query(
        Inventory.id,
        Product.name.label('product_name'),
        Inventory.quantity,
        Inventory.low_stock_threshold,
        func.case(
            (Inventory.quantity <= Inventory.low_stock_threshold, 'Low Stock'),
            (Inventory.quantity == 0, 'Out of Stock'),
            else_='In Stock'
        ).label('status')
    ).join(Product)

    if low_stock_only:
        query = query.filter(Inventory.quantity <= Inventory.low_stock_threshold)

    return query.all()

@router.get("/alerts", response_model=List[InventoryStatus])
def get_low_stock_alerts(
    db: Session = Depends(get_db),
    threshold: Optional[int] = None
):
    """Get low stock alerts with optional custom threshold"""
    query = db.query(
        Inventory.id,
        Product.name.label('product_name'),
        Inventory.quantity,
        Inventory.low_stock_threshold,
        func.case(
            (Inventory.quantity <= Inventory.low_stock_threshold, 'Low Stock'),
            (Inventory.quantity == 0, 'Out of Stock'),
            else_='In Stock'
        ).label('status')
    ).join(Product)

    if threshold is not None:
        query = query.filter(Inventory.quantity <= threshold)
    else:
        query = query.filter(Inventory.quantity <= Inventory.low_stock_threshold)

    return query.all()

@router.post("/", response_model=InventoryResponse)
def create_inventory(inventory: InventoryCreate, db: Session = Depends(get_db)):
    """Create a new inventory item"""
    # Check if product exists
    product = db.query(Product).filter(Product.id == inventory.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if inventory already exists for this product
    existing_inventory = db.query(Inventory).filter(Inventory.product_id == inventory.product_id).first()
    if existing_inventory:
        raise HTTPException(status_code=400, detail="Inventory already exists for this product")
    
    db_inventory = Inventory(**inventory.model_dump())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

@router.get("/{inventory_id}", response_model=InventoryResponse)
def get_inventory_item(inventory_id: int, db: Session = Depends(get_db)):
    """Get a specific inventory item"""
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory(
    inventory_id: int,
    inventory: InventoryUpdate,
    db: Session = Depends(get_db)
):
    """Update an inventory item"""
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if db_inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    # Store old quantity for history
    old_quantity = db_inventory.quantity
    
    for key, value in inventory.model_dump(exclude_unset=True).items():
        setattr(db_inventory, key, value)
    
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

@router.get("/history/{inventory_id}", response_model=List[InventoryHistory])
def get_inventory_history(
    inventory_id: int,
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get inventory change history"""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")

    # Get all updates within the date range
    history = db.query(
        Inventory.id,
        Product.name.label('product_name'),
        Inventory.quantity,
        Inventory.low_stock_threshold,
        Inventory.updated_at.label('change_date'),
        func.case(
            (Inventory.quantity <= Inventory.low_stock_threshold, 'Low Stock'),
            (Inventory.quantity == 0, 'Out of Stock'),
            else_='In Stock'
        ).label('status')
    ).join(Product).filter(
        Inventory.id == inventory_id,
        Inventory.updated_at >= start_date,
        Inventory.updated_at <= end_date
    ).order_by(Inventory.updated_at.desc()).all()

    return history

@router.get("/history", response_model=List[InventoryHistory])
def get_all_inventory_history(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    product_id: Optional[int] = None
):
    """Get inventory change history for all items or specific product"""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    query = db.query(
        Inventory.id,
        Product.name.label('product_name'),
        Inventory.quantity,
        Inventory.low_stock_threshold,
        Inventory.updated_at.label('change_date'),
        func.case(
            (Inventory.quantity <= Inventory.low_stock_threshold, 'Low Stock'),
            (Inventory.quantity == 0, 'Out of Stock'),
            else_='In Stock'
        ).label('status')
    ).join(Product).filter(
        Inventory.updated_at >= start_date,
        Inventory.updated_at <= end_date
    )

    if product_id:
        query = query.filter(Inventory.product_id == product_id)

    return query.order_by(Inventory.updated_at.desc()).all()

@router.delete("/{inventory_id}")
def delete_inventory(inventory_id: int, db: Session = Depends(get_db)):
    """Delete an inventory item"""
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if db_inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    db.delete(db_inventory)
    db.commit()
    return {"message": "Inventory deleted successfully"} 