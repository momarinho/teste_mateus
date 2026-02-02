from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
import math

from database import get_db
from schemas.operadora import Operadora, PaginatedOperadoras
from schemas.despesa import Despesa
from services import operadora_service, despesa_service

router = APIRouter(
    prefix="/api/operadoras",
    tags=["Operadoras"]
)

@router.get("/", response_model=PaginatedOperadoras)
def read_operadoras(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by Razao Social or CNPJ"),
    db: Session = Depends(get_db)
):
    """
    Lista operadoras com paginacao e filtro opcional (Razao Social ou CNPJ).
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


@router.get("/{cnpj}/despesas", response_model=List[Despesa])
def read_operadora_despesas(cnpj: str, db: Session = Depends(get_db)):
    """
    Retorna o historico de despesas da operadora pelo CNPJ.
    """
    return despesa_service.get_expenses_by_operator(db, cnpj)
