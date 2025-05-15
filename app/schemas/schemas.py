from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(gt=0, default=None)

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Inventory Schemas
class InventoryBase(BaseModel):
    quantity: int = Field(ge=0)
    low_stock_threshold: int = Field(ge=0)

class InventoryCreate(InventoryBase):
    product_id: int

class InventoryUpdate(InventoryBase):
    quantity: Optional[int] = Field(ge=0, default=None)
    low_stock_threshold: Optional[int] = Field(ge=0, default=None)

class InventoryResponse(InventoryBase):
    id: int
    product_id: int
    last_updated: datetime
    created_at: datetime
    updated_at: datetime
    product: ProductResponse

    class Config:
        from_attributes = True

class InventoryStatus(BaseModel):
    id: int
    product_name: str
    quantity: int
    low_stock_threshold: int
    status: str

class InventoryHistory(BaseModel):
    id: int
    product_name: str
    quantity: int
    low_stock_threshold: int
    change_date: datetime
    status: str

# Sale Schemas
class SaleBase(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    total_amount: float = Field(gt=0)
    sale_date: datetime

class SaleCreate(SaleBase):
    pass

class SaleUpdate(SaleBase):
    quantity: Optional[int] = Field(gt=0, default=None)
    total_amount: Optional[float] = Field(gt=0, default=None)
    sale_date: Optional[datetime] = None

class SaleResponse(SaleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    product: ProductResponse

    class Config:
        from_attributes = True

# Analytics Schemas
class SalesAnalytics(BaseModel):
    period: str
    total_sales: float
    total_quantity: int
    average_order_value: float

class SalesComparison(BaseModel):
    period1: SalesAnalytics
    period2: SalesAnalytics
    percentage_change: float

class RevenueAnalytics(BaseModel):
    period: str
    revenue: float
    order_count: int
    average_order_value: float

class RevenueResponse(BaseModel):
    period: str
    total_revenue: float

    class Config:
        from_attributes = True

class PeriodRevenue(BaseModel):
    start: datetime
    end: datetime
    total_revenue: float

    class Config:
        from_attributes = True

class RevenueComparisonResponse(BaseModel):
    period1: PeriodRevenue
    period2: PeriodRevenue
    percentage_change: float

    class Config:
        from_attributes = True 