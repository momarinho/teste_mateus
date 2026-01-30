import pandas as pd
import os
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from config import settings
from models import ConsolidadoDespesa, Operadora
from schemas.despesa import DespesaUF, Despesa
from services import operadora_service

_despesas_df = None

def load_despesas_csv():
    global _despesas_df
    if _despesas_df is None:
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), settings.CSV_PATH_DESPESAS))
        try:
            # Load despesas. Assuming format matches.
            # Using ; or , separator? Phase 3 usually produces CSV. Let's assume ; based on operadoras.
            # Usually standard pandas read_csv handles standard CSV.
            # Let's try default, if fail try ;
            try:
                _despesas_df = pd.read_csv(csv_path, encoding='utf-8', sep=',')
                if 'cnpj' not in _despesas_df.columns:
                     # If ',' didn't work properly or it's separated by ';', check columns
                     _despesas_df = pd.read_csv(csv_path, encoding='utf-8', sep=';')
            except:
                 _despesas_df = pd.read_csv(csv_path, encoding='utf-8', sep=';')

            # Ensure we have required columns
            # Clean values
            _despesas_df['valor_despesas'] = pd.to_numeric(_despesas_df['valor_despesas'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            _despesas_df['cnpj'] = _despesas_df['cnpj'].astype(str)
            
        except Exception as e:
            print(f"Error loading Despesas CSV: {e}")
            _despesas_df = pd.DataFrame()
    return _despesas_df

def get_expenses_by_uf(db: Session) -> List[DespesaUF]:
    if settings.USE_CSV:
        despesas = load_despesas_csv()
        operadoras = operadora_service.load_operadoras_csv()
        
        if despesas.empty or operadoras.empty:
            return []
            
        # Merge to get UF
        # operadoras has 'cnpj', 'uf'
        merged = pd.merge(despesas, operadoras[['cnpj', 'uf']], on='cnpj', how='inner')
        
        # Group by UF
        grouped = merged.groupby('uf')['valor_despesas'].sum().reset_index()
        grouped.rename(columns={'valor_despesas': 'total_despesas'}, inplace=True)
        
        return grouped.to_dict(orient='records')
    else:
        # DB Logic
        # Join ConsolidadoDespesa with Operadora (assuming foreign key or implicit join on CNPJ)
        # SQLAlchemy join
        results = db.query(
            Operadora.uf,
            func.sum(ConsolidadoDespesa.valor_despesas).label('total_despesas')
        ).join(
            Operadora, ConsolidadoDespesa.cnpj == Operadora.cnpj
        ).group_by(Operadora.uf).all()
        
        return [{"uf": r.uf, "total_despesas": r.total_despesas} for r in results if r.uf]

def get_expenses_by_operator(db: Session, cnpj: str) -> List[Despesa]:
    if settings.USE_CSV:
        df = load_despesas_csv()
        # Filter
        clean_cnpj = ''.join(filter(str.isdigit, cnpj))
        # Try both clean and raw ? df should be normalized.
        # Let's assume df 'cnpj' is somewhat raw.
        # But for reliability, better to strip.
        # In load_despesas_csv we didn't strip non-digits.
        
        filtered = df[df['cnpj'].apply(lambda x: ''.join(filter(str.isdigit, str(x)))) == clean_cnpj]
        
        return filtered.to_dict(orient='records')
    else:
        return db.query(ConsolidadoDespesa).filter(ConsolidadoDespesa.cnpj == cnpj).order_by(ConsolidadoDespesa.ano, ConsolidadoDespesa.trimestre).all()

def get_estatisticas(db: Session):
    if settings.USE_CSV:
        df = load_despesas_csv()
        op_df = operadora_service.load_operadoras_csv() # Needed for razao_social if not in despesas
        
        # Despesas might have razao_social, but let's check
        if 'razao_social' not in df.columns:
            # Merge
             df = pd.merge(df, op_df[['cnpj', 'razao_social']], on='cnpj', how='left')

        total_geral = df['valor_despesas'].sum()
        
        # Média trimestral considerar (soma das despesas) / (num operadoras * num trimestres) ???
        # Or just mean of the rows? The rows are (operadora, trimestre). 
        # Requirement: "média de despesas". usually mean of value.
        media_trimestral = df['valor_despesas'].mean()
        
        # Top 5
        # Group by razao_social sum
        top_5 = df.groupby('razao_social')['valor_despesas'].sum().nlargest(5).reset_index()
        top_5_list = top_5.to_dict(orient='records') # [{'razao_social':..., 'valor_despesas':...}]
        top_5_formatted = [{"razao_social": i['razao_social'], "total_despesas": i['valor_despesas']} for i in top_5_list]

        return {
            "total_geral": total_geral,
            "media_trimestral": media_trimestral,
            "top_5_operadoras": top_5_formatted
        }

    else:
        # DB Logic
        total_geral = db.query(func.sum(ConsolidadoDespesa.valor_despesas)).scalar() or 0
        media_trimestral = db.query(func.avg(ConsolidadoDespesa.valor_despesas)).scalar() or 0
        
        # Top 5
        top_5 = db.query(
            ConsolidadoDespesa.razao_social,
            func.sum(ConsolidadoDespesa.valor_despesas).label('total_despesas')
        ).group_by(ConsolidadoDespesa.razao_social).order_by(func.sum(ConsolidadoDespesa.valor_despesas).desc()).limit(5).all()
        
        top_5_formatted = [{"razao_social": r.razao_social, "total_despesas": r.total_despesas} for r in top_5]
        
        return {
            "total_geral": total_geral,
            "media_trimestral": media_trimestral,
            "top_5_operadoras": top_5_formatted
        }
