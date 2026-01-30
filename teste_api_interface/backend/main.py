from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from database import engine, Base
from check_setup import check_db_and_csv
from config import settings
from routers import operadoras, despesas

# Create database tables (if database connection is available)
# In production, use Alembic for migrations.
if engine:
    Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Starting up application...")
    # Verify setup again
    check_db_and_csv()
    yield
    # Shutdown logic
    print("Shutting down application...")

app = FastAPI(
    title="Teste Intuitive Care - API",
    description="API for managing Operadoras and Expenses data.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. In prod, specify.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(operadoras.router)
app.include_router(despesas.router)

@app.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "ok", "message": "API is online", "mode": "CSV" if settings.USE_CSV else "Database"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
