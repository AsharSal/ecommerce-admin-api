from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import sales, inventory, products

app = FastAPI(
    title="E-commerce Admin API",
    description="API for managing e-commerce inventory, products, and sales",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sales.router, prefix="/api/sales", tags=["sales"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
app.include_router(products.router, prefix="/api/products", tags=["products"])

@app.get("/")
def read_root():
    return {"message": "Welcome to E-commerce Admin API"} 