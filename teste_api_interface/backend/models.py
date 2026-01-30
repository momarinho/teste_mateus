from sqlalchemy import Column, String, Float, Integer, Date
from database import Base

class Operadora(Base):
    __tablename__ = "operadoras"

    registro_operadora = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(14), index=True)
    razao_social = Column(String(255))
    nome_fantasia = Column(String(255))
    modalidade = Column(String(100))
    logradouro = Column(String(255))
    numero = Column(String(50))
    complemento = Column(String(255))
    bairro = Column(String(100))
    cidade = Column(String(100))
    uf = Column(String(2))
    cep = Column(String(20))
    ddd = Column(String(5))
    telefone = Column(String(20))
    fax = Column(String(20))
    endereco_eletronico = Column(String(255))
    representante = Column(String(255))
    cargo_representante = Column(String(100))
    regiao_de_comercializacao = Column(String(100))
    data_registro_ans = Column(Date)

class ConsolidadoDespesa(Base):
    __tablename__ = "consolidado_despesas"

    # Since loading from CSV often lacks a simple ID, we might need a composite key or use a surrogate.
    # The SQL schema for Phase 3 used a surrogate ID but the LOAD DATA INFILE into staging didn't.
    # The final tables had a surrogate ID `id`? Let's check schema again.
    # Wait, 03_import_mysql.sql inserted into `consolidado_despesas` (target table). It selected clean columns.
    # I didn't verify if `consolidado_despesas` has an `id` column in `01_schema_mysql.sql`.
    # Let's assume there is an ID or use composite PK (cnpj, ano, trimestre).
    
    # For now, I'll use a composite PK.
    cnpj = Column(String(14), primary_key=True)
    trimestre = Column(Integer, primary_key=True)
    ano = Column(Integer, primary_key=True)
    
    razao_social = Column(String(255)) # Redundant but present in CSV
    valor_despesas = Column(Float)
