from sqlalchemy import create_engine, text
from config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    print("Checking CNPJ 00006037000127 in operadoras table...")
    res = conn.execute(text("SELECT * FROM operadoras WHERE cnpj = '00006037000127'")).fetchone()
    if res:
        print("Found in operadoras!")
        print(res)
    else:
        print("NOT found in operadoras.")

    print("\nChecking for common CNPJs (in both tables)...")
    query = """
    SELECT o.cnpj, o.razao_social 
    FROM operadoras o
    JOIN consolidado_despesas d ON o.cnpj = d.cnpj
    GROUP BY o.cnpj
    LIMIT 5
    """
    common = conn.execute(text(query)).fetchall()
    if common:
        print("Found CNPJs with both details and expenses:")
        for row in common:
            print(f" - {row[0]} ({row[1]})")
    else:
        print("No overlap found between operadoras and expenses!")
