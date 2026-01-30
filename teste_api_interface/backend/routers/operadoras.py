from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import math

from database import get_db
from schemas.operadora import Operadora, PaginatedOperadoras
from services import operadora_service

router = APIRouter(
    prefix="/api/operadoras",
    tags=["Operadoras"]
)

@router.get("/", response_model=PaginatedOperadoras)
def read_operadoras(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by Razao Social"),
    db: Session = Depends(get_db)
):
    """
    Lista operadoras com paginacao e filtro opcional.
    """
    operadoras_list, total_count = operadora_service.get_operadoras(db, page, limit, search)
    
    total_pages = math.ceil(total_count / limit)
    
    return {
        "data": operadoras_list,
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }

@router.get("/{cnpj}", response_model=Operadora)
def read_operadora(cnpj: str, db: Session = Depends(get_db)):
    """
    Retorna detalhes de uma operadora pelo CNPJ.
    """
    operadora = operadora_service.get_operadora_by_cnpj(db, cnpj)
    if not operadora:
        raise HTTPException(status_code=404, detail="Operadora not found")
    return operadora
