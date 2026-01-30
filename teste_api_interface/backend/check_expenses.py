from sqlalchemy import create_engine, text
from config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    print("Checking specific CNPJ expenses:")
    result = conn.execute(text("SELECT * FROM consolidado_despesas WHERE cnpj = '19541931000125'")).fetchall()
    print(result)

    print("\n--- Top 5 CNPJs with expenses ---")
    top_ops = conn.execute(text("SELECT cnpj, SUM(valor_despesas) as total FROM consolidado_despesas GROUP BY cnpj ORDER BY total DESC LIMIT 5")).fetchall()
    for row in top_ops:
        print(f"CNPJ: {row[0]}, Total: {row[1]}")
