import os
import sys
from sqlalchemy import text
from database import engine, SessionLocal
from config import settings

def check_db_and_csv():
    print("Checking Setup for Phase 4...")
    
    # 1. Check CSV Files
    print("\n[1] Checking Local CSV Files (Fallback Data Source):")
    # CSV paths are relative to where the script is run. Assuming run from backend/ dir.
    # config.settings has "../../..."
    # If run from backend dir, we can verify absolute path.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Adjusting since config settings are relative to backend dir or relative to project root?
    # Usually ".." means up one level. From backend -> teste_api_interface -> teste_mateus -> ...
    # Wait, backend/../teste_transformacao... -> "teste_api_interface/teste_transformacao" which is WRONG.
    # We are in `teste_api_interface/backend`.
    # `..` -> `teste_api_interface`.
    # `../..` -> `teste_mateus`.
    # So `../../teste_transformacao_validacao/operadoras_ativas.csv` is correct from `backend`.
    
    csv_ops = os.path.abspath(os.path.join(base_dir, settings.CSV_PATH_OPERADORAS))
    csv_desp = os.path.abspath(os.path.join(base_dir, settings.CSV_PATH_DESPESAS))
    
    if os.path.exists(csv_ops):
        print(f"  [OK] Operadoras CSV found: {csv_ops}")
    else:
        print(f"  [MISSING] Operadoras CSV: {csv_ops}")
        
    if os.path.exists(csv_desp):
        print(f"  [OK] Despesas CSV found: {csv_desp}")
    else:
        print(f"  [MISSING] Despesas CSV: {csv_desp}")
        
    # 2. Check Database Connection
    print("\n[2] Checking Database Connection (Primary Data Source):")
    if not engine:
        print("  [FAIL] Database engine could not be initialized. Check credentials in .env")
        return False
        
    try:
        connection = engine.connect()
        print("  [OK] Connected to Database.")
        
        # 3. Check Tables
        try:
            result = connection.execute(text("SHOW TABLES LIKE 'operadoras';"))
            if result.fetchone():
                print("  [OK] Table 'operadoras' exists.")
            else:
                print("  [FAIL] Table 'operadoras' does NOT exist.")
                
            result = connection.execute(text("SHOW TABLES LIKE 'consolidado_despesas';"))
            if result.fetchone():
                print("  [OK] Table 'consolidado_despesas' exists.")
            else:
                print("  [FAIL] Table 'consolidado_despesas' does NOT exist.")
                
            # Count rows
            count_ops = connection.execute(text("SELECT COUNT(*) FROM operadoras")).scalar()
            print(f"  [INFO] Rows in 'operadoras': {count_ops}")
            
        except Exception as e:
            print(f"  [ERROR] Error checking tables: {e}")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"  [FAIL] Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = check_db_and_csv()
    if not success:
        sys.exit(1)
