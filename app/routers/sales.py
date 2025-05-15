from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.models import Sale, Product
from app.schemas.schemas import (
    SaleResponse, SaleCreate, SaleUpdate, 
    SalesAnalytics, SalesComparison,
    RevenueAnalytics, RevenueResponse, RevenueComparisonResponse
)

router = APIRouter()

@router.get("/", response_model=List[SaleResponse])
def get_sales(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    product_id: Optional[int] = None
):
    query = db.query(Sale)
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    if product_id:
        query = query.filter(Sale.product_id == product_id)
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=SaleResponse)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    """Create a new sale"""
    db_sale = Sale(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    """Get a specific sale by ID"""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale(sale_id: int, sale: SaleUpdate, db: Session = Depends(get_db)):
    """Update a sale"""
    db_sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if db_sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    for key, value in sale.model_dump(exclude_unset=True).items():
        setattr(db_sale, key, value)
    
    db.commit()
    db.refresh(db_sale)
    return db_sale

@router.delete("/{sale_id}")
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    """Delete a sale"""
    db_sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if db_sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    db.delete(db_sale)
    db.commit()
    return {"message": "Sale deleted successfully"}

@router.get("/revenue/product/{product_id}", response_model=RevenueAnalytics)
def get_product_revenue(
    product_id: int,
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get revenue analysis for a specific product"""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    result = db.query(
        func.sum(Sale.total_amount).label('revenue'),
        func.count(Sale.id).label('order_count'),
        func.avg(Sale.total_amount).label('average_order_value')
    ).filter(
        Sale.product_id == product_id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="No sales data found for this product")

    return RevenueAnalytics(
        period=f"{start_date.date()} to {end_date.date()}",
        revenue=float(result.revenue or 0),
        order_count=int(result.order_count or 0),
        average_order_value=float(result.average_order_value or 0)
    )

@router.get("/revenue/daily", response_model=List[RevenueResponse])
def get_daily_revenue(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get daily revenue for a specified period"""
    query = db.query(
        func.date(Sale.sale_date).label("period"),
        func.sum(Sale.total_amount).label("total_revenue")
    ).group_by(func.date(Sale.sale_date))
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    results = query.all()
    return [{"period": str(r.period), "total_revenue": r.total_revenue} for r in results]

@router.get("/revenue/weekly", response_model=List[RevenueResponse])
def get_weekly_revenue(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get weekly revenue for a specified period (MySQL compatible)"""
    query = db.query(
        func.year(Sale.sale_date).label("year"),
        func.week(Sale.sale_date, 1).label("week"),
        func.sum(Sale.total_amount).label("total_revenue")
    )
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    query = query.group_by(func.year(Sale.sale_date), func.week(Sale.sale_date, 1)).order_by(func.year(Sale.sale_date), func.week(Sale.sale_date, 1))
    results = query.all()
    return [{"period": f"{r.year}-W{str(r.week).zfill(2)}", "total_revenue": r.total_revenue} for r in results]

@router.get("/revenue/monthly", response_model=List[RevenueResponse])
def get_monthly_revenue(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get monthly revenue for a specified period (MySQL compatible)"""
    query = db.query(
        func.year(Sale.sale_date).label("year"),
        func.month(Sale.sale_date).label("month"),
        func.sum(Sale.total_amount).label("total_revenue")
    )
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    query = query.group_by(func.year(Sale.sale_date), func.month(Sale.sale_date)).order_by(func.year(Sale.sale_date), func.month(Sale.sale_date))
    results = query.all()
    return [{"period": f"{r.year}-{str(r.month).zfill(2)}", "total_revenue": r.total_revenue} for r in results]

@router.get("/revenue/annual", response_model=List[RevenueResponse])
def get_annual_revenue(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get annual revenue for a specified period (MySQL compatible)"""
    query = db.query(
        func.year(Sale.sale_date).label("year"),
        func.sum(Sale.total_amount).label("total_revenue")
    )
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    query = query.group_by(func.year(Sale.sale_date)).order_by(func.year(Sale.sale_date))
    results = query.all()
    return [{"period": str(r.year), "total_revenue": r.total_revenue} for r in results]

@router.get("/revenue/compare", response_model=RevenueComparisonResponse)
def compare_revenue(
    period1_start: datetime = Query(...),
    period1_end: datetime = Query(...),
    period2_start: datetime = Query(...),
    period2_end: datetime = Query(...),
    db: Session = Depends(get_db)
):
    """Compare revenue between two different periods"""
    # Get revenue for period 1
    period1_revenue = db.query(func.sum(Sale.total_amount)).filter(
        Sale.sale_date >= period1_start,
        Sale.sale_date <= period1_end
    ).scalar() or 0

    # Get revenue for period 2
    period2_revenue = db.query(func.sum(Sale.total_amount)).filter(
        Sale.sale_date >= period2_start,
        Sale.sale_date <= period2_end
    ).scalar() or 0

    # Calculate percentage change
    if period1_revenue == 0:
        percentage_change = 100 if period2_revenue > 0 else 0
    else:
        percentage_change = ((period2_revenue - period1_revenue) / period1_revenue) * 100

    return {
        "period1": {
            "start": period1_start,
            "end": period1_end,
            "total_revenue": period1_revenue
        },
        "period2": {
            "start": period2_start,
            "end": period2_end,
            "total_revenue": period2_revenue
        },
        "percentage_change": percentage_change
    } 