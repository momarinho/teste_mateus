from typing import Optional, List
from pydantic import BaseModel
from datetime import date

class OperadoraBase(BaseModel):
    registro_operadora: Optional[int]
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    modalidade: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    cep: Optional[str] = None
    ddd: Optional[str] = None
    telefone: Optional[str] = None
    fax: Optional[str] = None
    endereco_eletronico: Optional[str] = None
    representante: Optional[str] = None
    cargo_representante: Optional[str] = None
    regiao_de_comercializacao: Optional[str] = None
    data_registro_ans: Optional[date] = None

class Operadora(OperadoraBase):
    class Config:
        from_attributes = True

class PaginatedOperadoras(BaseModel):
    data: List[Operadora]
    total: int
    page: int
    limit: int
    total_pages: int
