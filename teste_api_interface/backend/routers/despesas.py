from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.despesa import Despesa, DespesaUF, Estatisticas
from services import despesa_service

router = APIRouter(
    prefix="/api/despesas",
    tags=["Despesas"]
)

@router.get("/por-uf", response_model=List[DespesaUF])
def get_expenses_by_uf(db: Session = Depends(get_db)):
    """
    Retorna a distribuicao de despesas por UF.
    """
    return despesa_service.get_expenses_by_uf(db)

@router.get("/operadora/{cnpj}", response_model=List[Despesa])
def get_expenses_by_operator(cnpj: str, db: Session = Depends(get_db)):
    """
    Retorna o historico de despesas de uma operadora.
    """
    return despesa_service.get_expenses_by_operator(db, cnpj)

@router.get("/estatisticas", response_model=Estatisticas)
def get_general_statistics(db: Session = Depends(get_db)):
    """
    Retorna estatisticas agregadas (Total, Media, Top 5).
    """
    return despesa_service.get_estatisticas(db)
