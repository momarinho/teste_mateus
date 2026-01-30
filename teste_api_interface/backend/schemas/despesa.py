from pydantic import BaseModel
from typing import List, Optional

class DespesaBase(BaseModel):
    cnpj: str
    razao_social: Optional[str] = None
    ano: int
    trimestre: int
    valor_despesas: float

class Despesa(DespesaBase):
    class Config:
        from_attributes = True

class DespesaUF(BaseModel):
    uf: str
    total_despesas: float

class OperadoraTop(BaseModel):
    razao_social: str
    total_despesas: float

class Estatisticas(BaseModel):
    total_geral: float
    media_trimestral: float
    top_5_operadoras: List[OperadoraTop]
