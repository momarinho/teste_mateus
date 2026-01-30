import pandas as pd
from sqlalchemy import create_engine, text
from config import settings
import os

def reload_operadoras():
    # 1. Read CSV
    csv_path = r"c:\Users\Transporte-02\Desktop\teste_mateus\teste_transformacao_validacao\operadoras_ativas.csv"
    print(f"Reading {csv_path}...")
    
    # Ensure we read it as string to avoid pandas inferring types wrongly usually, but here everything goes to staging (TEXT)
    # The staging table has specific columns.
    # CSV headers: REGISTRO_OPERADORA;CNPJ;Razao_Social;...
    # Staging columns: lower case.
    
    try:
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8', dtype=str)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Normalize column names to match table (optional, but good for to_sql)
    # stg_operadoras columns: registro_operadora, cnpj, ...
    # CSV has REGISTRO_OPERADORA. 
    df.columns = [c.lower() for c in df.columns]
    
    # 2. Connect to DB
    print("Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.begin() as conn:
        # 3. Truncate tables
        print("Truncating tables...")
        conn.execute(text("TRUNCATE TABLE stg_operadoras"))
        conn.execute(text("TRUNCATE TABLE operadoras")) # We are reloading everything
        
        # 4. Insert into Staging
        # pandas to_sql is convenient.
        print(f"Inserting {len(df)} rows into stg_operadoras...")
        df.to_sql('stg_operadoras', con=conn, if_exists='append', index=False)
        
        # 5. Execute Transformation SQL
        print("Executing transformation and insertion into 'operadoras'...")
        # Dictionary of logic from 03_import_mysql.sql / fix_import.py
        # We reuse the logic from fix_import.py which was updated for the schema fix.
        
        insert_query = """
        INSERT INTO operadoras (
          registro_operadora,
          cnpj,
          razao_social,
          nome_fantasia,
          modalidade,
          logradouro,
          numero,
          complemento,
          bairro,
          cidade,
          uf,
          cep,
          ddd,
          telefone,
          fax,
          endereco_eletronico,
          representante,
          cargo_representante,
          regiao_de_comercializacao,
          data_registro_ans
        )
        SELECT
          CAST(registro_operadora AS UNSIGNED),
          REGEXP_REPLACE(cnpj, '[^0-9]', ''),
          TRIM(razao_social),
          NULLIF(nome_fantasia, ''),
          NULLIF(modalidade, ''),
          NULLIF(logradouro, ''),
          NULLIF(numero, ''),
          NULLIF(complemento, ''),
          NULLIF(bairro, ''),
          NULLIF(cidade, ''),
          NULLIF(uf, ''),
          NULLIF(cep, ''),
          NULLIF(ddd, ''),
          NULLIF(telefone, ''),
          NULLIF(fax, ''),
          NULLIF(endereco_eletronico, ''),
          NULLIF(representante, ''),
          NULLIF(cargo_representante, ''),
          NULLIF(regiao_de_comercializacao, ''),
          CASE
            WHEN data_registro_ans REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' THEN STR_TO_DATE(data_registro_ans, '%Y-%m-%d')
            WHEN data_registro_ans REGEXP '^[0-9]{2}/[0-9]{2}/[0-9]{4}$' THEN STR_TO_DATE(data_registro_ans, '%d/%m/%Y')
            ELSE NULL
          END
        FROM stg_operadoras
        WHERE
          (REGEXP_REPLACE(cnpj, '[^0-9]', '') IS NOT NULL AND CHAR_LENGTH(REGEXP_REPLACE(cnpj, '[^0-9]', '')) = 14)
          AND (TRIM(razao_social) IS NOT NULL AND TRIM(razao_social) <> '')
          AND (registro_operadora REGEXP '^[0-9]+$');
        """
        
        conn.execute(text(insert_query))
        
        # 6. Check Result
        count = conn.execute(text("SELECT COUNT(*) FROM operadoras")).scalar()
        print(f"Success! {count} rows inserted into 'operadoras'.")

if __name__ == "__main__":
    reload_operadoras()
