from sqlalchemy import create_engine, text
from config import settings

engine = create_engine(settings.DATABASE_URL)

target_cnpj = '19541931000125'

with engine.connect() as conn:
    print(f"Checking expenses for CNPJ {target_cnpj}...")
    # Check exact match
    rows = conn.execute(text(f"SELECT * FROM consolidado_despesas WHERE cnpj = '{target_cnpj}'")).fetchall()
    print(f"Rows found: {len(rows)}")
    
    # Check if there are ANY expenses in the table
    total = conn.execute(text("SELECT COUNT(*) FROM consolidado_despesas")).scalar()
    print(f"Total rows in consolidado_despesas: {total}")

    if len(rows) == 0:
        print("Trying to find a CNPJ that HAS expenses...")
        sample = conn.execute(text("SELECT cnpj, SUM(valor_despesas) as total FROM consolidado_despesas GROUP BY cnpj HAVING total > 0 LIMIT 1")).fetchone()
        if sample:
            print(f"Suggested CNPJ for testing: {sample[0]} (Total: {sample[1]})")
