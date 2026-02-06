# uvicorn main:app --reload

from wsgiref import types
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re
from dotenv import load_dotenv
from fastapi.responses import PlainTextResponse
from db import DatabaseNotConfiguredError, fetch_table_metadata
from google import genai

app = FastAPI()
load_dotenv()

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# 1. Dummy Metadata (fallback if DB not configured)
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


def _build_index(table_metadata: list[dict]) -> faiss.IndexFlatL2:
    if not table_metadata:
        dimension = model.get_sentence_embedding_dimension()
        return faiss.IndexFlatL2(dimension)
    documents = [
        f"Table: {table['table']}. Description: {table['description']}. Columns: {', '.join(table['columns'])}"
        for table in table_metadata
    ]
    embeddings = model.encode(documents)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    return index


@app.on_event("startup")
def _load_metadata() -> None:
    try:
        metadata = fetch_table_metadata()
    except DatabaseNotConfiguredError:
        metadata = TABLE_METADATA
    app.state.table_metadata = metadata
    app.state.index = _build_index(metadata)


# -----------------------------
# 2. API Models
# -----------------------------
class SearchRequest(BaseModel):
    query: str
    top_k: int = 2

class SearchResponse(BaseModel):
    table: str
    description: str
    columns: list
    score: float


class MetadataResponse(BaseModel):
    table: str
    description: str
    columns: list

# -----------------------------
# 3. Search Endpoint
# -----------------------------


def generatePrompt(metadata: [],userInput: str):
    schema_context = "Database Schema:\n"
    for table in metadata:
        schema_context += f"- Table: {table['table']}\n"
        schema_context += f"  Description: {table['description']}\n"
        schema_context += f"  Columns: {', '.join(table['columns'])}\n\n"

    system_instruction = f"""
    You are a SQL expert. Given the following database schema, generate a valid SQL query 
    that answers the user's question. Only return the SQL code, nothing else.
    
    {schema_context},
    this is what the user wants: {userInput}
    """

    return system_instruction

def callgemini(prompt: str) -> str:
    client=genai.Client(api_key="AIzaSyBd3b4CwGvnf4wLkYZ3W5wX6gKeqVDB9kY")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def getSql(metadata: [],userInput: str):

    prompt=generatePrompt(metadata,userInput)
    
    response=callgemini(prompt)
    # response="```sql\nSELECT\n  c.customer_name\nFROM customers AS c\nJOIN orders AS o\n  ON c.customer_id = o.customer_id\nWHERE\n  o.total_amount > 250;\n```"
    clean_sql = re.sub(r"^```sql\s*|\s*```$", "", response.strip(), flags=re.MULTILINE)
    print("Generated SQL Query:")
    print(clean_sql)
    return PlainTextResponse(clean_sql)

@app.post("/getSql", response_model=str)
def search_metadata(request: SearchRequest):
    table_metadata = app.state.table_metadata
    if not table_metadata:
        raise HTTPException(status_code=503, detail="No table metadata available.")
    top_k = max(1, min(request.top_k, len(table_metadata)))
    query_embedding = model.encode([request.query])
    distances, indices = app.state.index.search(np.array(query_embedding), top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        table_data = table_metadata[idx]
        results.append({
            "table": table_data["table"],
            "description": table_data["description"],
            "columns": table_data["columns"],
            "score": float(distances[0][i])
        })

    return getSql(results,request.query)


@app.get("/debug/metadata", response_model=list[MetadataResponse])
def debug_metadata():
    return app.state.table_metadata
