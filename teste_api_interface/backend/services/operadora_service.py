import pandas as pd
import os
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Tuple, List, Optional

from config import settings
from models import Operadora as OperadoraModel
from schemas.operadora import Operadora as OperadoraSchema

# Cache global para CSV (simples)
_operadoras_df = None

def load_operadoras_csv():
    global _operadoras_df
    if _operadoras_df is None:
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), settings.CSV_PATH_OPERADORAS))
        # Assuming CSV structure matches expected. 
        # The CSV from Phase 2 uses ';' as separator
        try:
            _operadoras_df = pd.read_csv(csv_path, sep=';', encoding='utf-8', dtype={'cnpj': str, 'registro_operadora': str})
            # Simple cleanup for nan values to avoid Pydantic errors
            _operadoras_df = _operadoras_df.where(pd.notnull(_operadoras_df), None)
            
            # Map columns if necessary or ensure they match schema
            # 'data_registro_ans' might need parsing to date object if Pydantic expects date
            # But let's keep it simple for now, Pydantic might valid strings as dates provided they are ISO8601
        except Exception as e:
            print(f"Error loading CSV: {e}")
            _operadoras_df = pd.DataFrame()
    return _operadoras_df

def get_operadoras(
    db: Session, 
    page: int = 1, 
    limit: int = 10, 
    search: Optional[str] = None
) -> Tuple[List[OperadoraSchema], int]:
    
    offset = (page - 1) * limit

    if settings.USE_CSV:
        df = load_operadoras_csv()
        
        # Filtering
        if search:
            # Case insensitive search in razao_social OR cnpj
            search_clean = search.lower().strip()
            # For dataframes we can do boolean indexing
            # We check if razao_social contains search OR cnpj contains search
            df = df[
                df['razao_social'].str.lower().str.contains(search_clean, na=False) | 
                df['cnpj'].str.contains(search_clean, na=False)
            ]
        
        total = len(df)
        
        # Pagination
        # Ensure we don't go out of bounds
        start = offset
        end = offset + limit
        
        paginated_df = df.iloc[start:end]
        
        # Convert to list of dicts
        data = paginated_df.to_dict(orient='records')
        
        # Convert Dicts to Pydantic Models (handling data conversion if strictly needed)
        # Note: If date string format issue arises, we might need pre-processing.
        return data, total

    else:
        # Database logic
        query = db.query(OperadoraModel)
        
        if search:
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    OperadoraModel.razao_social.ilike(f"%{search}%"),
                    OperadoraModel.cnpj.ilike(f"%{search}%")
                )
            )
            
        total = query.count()
        operadoras = query.offset(offset).limit(limit).all()
        
        return operadoras, total

def get_operadora_by_cnpj(db: Session, cnpj: str):
    if settings.USE_CSV:
        df = load_operadoras_csv()
        # Clean CNPJ input just in case
        clean_cnpj = ''.join(filter(str.isdigit, cnpj))
        
        # Assuming CSV has numbers only or formatted? 
        # Phase 2 CSV usually has formatted text or raw. Let's try raw match or fuzzy.
        # Ideally the CSV should be normalized.
        # Let's try direct match first.
        result = df[df['cnpj'] == cnpj]
        if result.empty:
            return None
        return result.iloc[0].to_dict()
    else:
        return db.query(OperadoraModel).filter(OperadoraModel.cnpj == cnpj).first()
