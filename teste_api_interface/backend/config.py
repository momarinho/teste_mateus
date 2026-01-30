import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "teste_ans")
    
    # Allow fallback to CSV if DB is not available
    USE_CSV = os.getenv("USE_CSV", "False").lower() == "true"
    # Adjust paths to assume running from backend directory
    CSV_PATH_OPERADORAS = os.getenv("CSV_PATH_OPERADORAS", "../../teste_transformacao_validacao/operadoras_ativas.csv")
    CSV_PATH_DESPESAS = os.getenv("CSV_PATH_DESPESAS", "../../data/processed/consolidado_despesas.csv")

    @property
    def DATABASE_URL(self):
        # Handle empty password
        pwd = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return f"mysql+mysqlconnector://{self.DB_USER}{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
