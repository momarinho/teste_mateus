from contextlib import asynccontextmanager

import uvicorn
from check_setup import check_db_and_csv
from config import settings
from database import Base, engine, get_db
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import despesas, operadoras
from schemas.despesa import Estatisticas
from services import despesa_service

# Create database tables (if database connection is available)
# In production, use Alembic for migrations.
if engine and not settings.USE_CSV:
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
    lifespan=lifespan,
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


@app.get("/api/estatisticas", response_model=Estatisticas, tags=["Despesas"])
def get_estatisticas_gerais(db=Depends(get_db)):
    """
    Retorna estatisticas agregadas (Total, Media, Top 5).
    """
    return despesa_service.get_estatisticas(db)


@app.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {
        "status": "ok",
        "message": "API is online",
        "mode": "CSV" if settings.USE_CSV else "Database",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
