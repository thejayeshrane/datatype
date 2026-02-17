import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Enable CORS so your frontend can talk to this backend later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory where THIS main.py file is located
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "data.csv")

# 1. Load the CSV into memory
# We use a try-except block so the server doesn't just crash if the file is missing

try:
    df = pd.read_csv(csv_path)
    print(f"✅ Success: Loaded {len(df)} rows from {csv_path}")
except Exception as e:
    print(f"❌ Error: {e}")



@app.get("/")
def health_check():
    return {
        "status": "Online", 
        "agent": "Data-Discovery-001",
        "rows_loaded": len(df) if 'df' in locals() else 0
    }

# Add this below your existing @app.get("/") route

@app.get("/stats")
def get_stats():
    # 1. Calculate Total Revenue: (Price * Units_Sold) summed up
    total_revenue = (df['Price'] * df['Units_Sold']).sum()
    
    # 2. Find the product with the highest Units_Sold
    # .idxmax() finds the index of the highest number
    best_seller_index = df['Units_Sold'].idxmax()
    best_seller_name = df.loc[best_seller_index]['Product']
    
    return {
        "total_revenue": float(total_revenue),
        "best_seller": best_seller_name,
        "total_items_sold": int(df['Units_Sold'].sum())
    }

@app.get("/product/{product_name}")
def get_product_stats(product_name: str):
    # Search for the product (case-insensitive)
    # .str.lower() ensures "laptop" matches "Laptop"
    result = df[df['Product'].str.lower() == product_name.lower()]
    
    if result.empty:
        return {"error": "Product not found"}
    
    # Grab the first match found
    row = result.iloc[0]
    return {
        "product": row['Product'],
        "revenue": float(row['Price'] * row['Units_Sold']),
        "units": int(row['Units_Sold'])
    }