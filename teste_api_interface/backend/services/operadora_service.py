import os
import re
from typing import List, Optional, Tuple

import pandas as pd
from config import settings
from models import Operadora as OperadoraModel
from schemas.operadora import Operadora as OperadoraSchema
from sqlalchemy import func
from sqlalchemy.orm import Session

# Cache global para CSV (simples)
_operadoras_df = None


def _to_operadora_schema(item: object) -> OperadoraSchema:
    if hasattr(OperadoraSchema, "model_validate"):
        return OperadoraSchema.model_validate(item)
    if hasattr(OperadoraSchema, "from_orm"):
        return OperadoraSchema.from_orm(item)
    return OperadoraSchema.parse_obj(item)


def _normalize_col(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def _rename_operadoras_columns(df: pd.DataFrame) -> pd.DataFrame:
    canonical = {
        "registrooperadora": "registro_operadora",
        "regans": "registro_operadora",
        "registroans": "registro_operadora",
        "cnpj": "cnpj",
        "razaosocial": "razao_social",
        "razaosocialnome": "razao_social",
        "nomefantasia": "nome_fantasia",
        "modalidade": "modalidade",
        "logradouro": "logradouro",
        "numero": "numero",
        "complemento": "complemento",
        "bairro": "bairro",
        "cidade": "cidade",
        "uf": "uf",
        "cep": "cep",
        "ddd": "ddd",
        "telefone": "telefone",
        "fax": "fax",
        "enderecoeletronico": "endereco_eletronico",
        "representante": "representante",
        "cargorepresentante": "cargo_representante",
        "regiaodecomercializacao": "regiao_de_comercializacao",
        "dataregistroans": "data_registro_ans",
    }
    rename_map = {}
    for col in df.columns:
        normalized = _normalize_col(col)
        if normalized in canonical:
            rename_map[col] = canonical[normalized]
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


def _coerce_optional_str(value):
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if text.lower() == "nan" or text == "":
        return None
    if text.endswith(".0"):
        text = text[:-2]
    return text


def _coerce_optional_int(value):
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith(".0"):
        text = text[:-2]
    if text.isdigit():
        return int(text)
    return None


def load_operadoras_csv():
    global _operadoras_df
    if _operadoras_df is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        csv_path = os.path.abspath(os.path.join(base_dir, settings.CSV_PATH_OPERADORAS))
        # Assuming CSV structure matches expected.
        # The CSV from Phase 2 uses ';' as separator
        try:
            _operadoras_df = pd.read_csv(
                csv_path,
                sep=";",
                encoding="utf-8",
                dtype={"cnpj": str, "registro_operadora": str},
            )
            _operadoras_df = _rename_operadoras_columns(_operadoras_df)
            if "cnpj" in _operadoras_df.columns:
                _operadoras_df["cnpj"] = _operadoras_df["cnpj"].apply(
                    lambda x: _coerce_optional_str(re.sub(r"\D", "", str(x)))
                )
            if "registro_operadora" in _operadoras_df.columns:
                _operadoras_df["registro_operadora"] = _operadoras_df[
                    "registro_operadora"
                ].apply(_coerce_optional_int)
            string_cols = [
                "razao_social",
                "nome_fantasia",
                "modalidade",
                "logradouro",
                "numero",
                "complemento",
                "bairro",
                "cidade",
                "uf",
                "cep",
                "ddd",
                "telefone",
                "fax",
                "endereco_eletronico",
                "representante",
                "cargo_representante",
                "regiao_de_comercializacao",
                "data_registro_ans",
            ]
            for col in string_cols:
                if col in _operadoras_df.columns:
                    _operadoras_df[col] = _operadoras_df[col].apply(
                        _coerce_optional_str
                    )
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
    db: Session, page: int = 1, limit: int = 10, search: Optional[str] = None
) -> Tuple[List[OperadoraSchema], int]:
    offset = (page - 1) * limit

    if settings.USE_CSV:
        df = load_operadoras_csv()
        if "razao_social" not in df.columns:
            df["razao_social"] = ""
        if "cnpj" not in df.columns:
            df["cnpj"] = ""

        # Filtering
        if search:
            # Case insensitive search in razao_social OR cnpj
            search_clean = search.lower().strip()
            # For dataframes we can do boolean indexing
            # We check if razao_social contains search OR cnpj contains search
            df = df[
                df["razao_social"].str.lower().str.contains(search_clean, na=False)
                | df["cnpj"].str.contains(search_clean, na=False)
            ]

        total = len(df)

        # Pagination
        # Ensure we don't go out of bounds
        start = offset
        end = offset + limit

        paginated_df = df.iloc[start:end]

        # Convert to list of dicts
        data = paginated_df.to_dict(orient="records")

        # Convert Dicts to Pydantic Models (handling data conversion if strictly needed)
        # Note: If date string format issue arises, we might need pre-processing.
        operadoras = [_to_operadora_schema(item) for item in data]
        return operadoras, total

    else:
        # Database logic
        query = db.query(OperadoraModel)

        if search:
            from sqlalchemy import or_

            query = query.filter(
                or_(
                    OperadoraModel.razao_social.ilike(f"%{search}%"),
                    OperadoraModel.cnpj.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        operadoras = query.offset(offset).limit(limit).all()
        operadoras_schema = [_to_operadora_schema(item) for item in operadoras]

        return operadoras_schema, total


def get_operadora_by_cnpj(db: Session, cnpj: str):
    if settings.USE_CSV:
        df = load_operadoras_csv()
        # Clean CNPJ input just in case
        clean_cnpj = "".join(filter(str.isdigit, cnpj))
        # Assuming CSV has numbers only or formatted?
        # Phase 2 CSV usually has formatted text or raw. Let's try raw match or fuzzy.
        # Ideally the CSV should be normalized.
        # Let's try direct match first.
        if "cnpj" not in df.columns:
            return None
        result = df[
            df["cnpj"].apply(lambda x: "".join(filter(str.isdigit, str(x))))
            == clean_cnpj
        ]
        if result.empty:
            return None
        return result.iloc[0].to_dict()
    else:
        return db.query(OperadoraModel).filter(OperadoraModel.cnpj == cnpj).first()
