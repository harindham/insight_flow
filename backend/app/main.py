from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

app = FastAPI()

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# 1. Dummy Metadata (like DB schema)
# -----------------------------
TABLE_METADATA = [
    {
        "table": "customers",
        "description": "Stores customers information",
        "columns": ["customer_id", "customer_name", "email", "phone", "city", "state", "country", "zip_code"]
    },
    {
        "table": "orders",
        "description": "Stores orders by the customers",
        "columns": ["order_id", "customer_id", "order_date", "total_amount", "status", "shipping_address"]
    },
    {
        "table": "products",
        "description": "Stores product catalog information",
        "columns": ["product_id", "product_name", "category_id", "price", "stock_quantity", "supplier_id"]
    },
    {
        "table": "suppliers",
        "description": "Stores supplier information",
        "columns": ["supplier_id", "contact_name", "email", "phone", "address", "city", "country"]
    },
    {
        "table": "categories",
        "description": "Stores product categories",
        "columns": ["category_id", "category_name", "description"]
    },
    {
        "table": "payments",
        "description": "Stores payment information for orders",
        "columns": ["payment_id", "order_id", "payment_date", "amount", "payment_method", "payment_status"]
    },
    {
        "table": "reviews",
        "description": "Stores customer reviews for products",
        "columns": ["review_id", "product_id", "customer_id", "rating", "review_text", "review_date"]
    },
    {
        "table": "employees",
        "description": "Stores company employee information",
        "columns": ["employee_id", "first_name", "last_name", "email", "phone", "position", "department", "hire_date"]
    }
]


# Convert metadata to searchable text
documents = [
    f"Table: {table['table']}. Description: {table['description']}. Columns: {', '.join(table['columns'])}"
    for table in TABLE_METADATA
]

# -----------------------------
# 2. Create Vector Store (FAISS)
# -----------------------------
embeddings = model.encode(documents)
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# -----------------------------
# 3. API Models
# -----------------------------
class SearchRequest(BaseModel):
    query: str
    top_k: int = 2

class SearchResponse(BaseModel):
    table: str
    description: str
    columns: list
    score: float

# -----------------------------
# 4. Search Endpoint
# -----------------------------
@app.post("/search", response_model=list[SearchResponse])
def search_metadata(request: SearchRequest):
    query_embedding = model.encode([request.query])
    distances, indices = index.search(np.array(query_embedding), request.top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        table_data = TABLE_METADATA[idx]
        results.append({
            "table": table_data["table"],
            "description": table_data["description"],
            "columns": table_data["columns"],
            "score": float(distances[0][i])
        })

    return results
