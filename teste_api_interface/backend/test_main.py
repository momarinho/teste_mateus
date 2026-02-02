import pytest
from fastapi.testclient import TestClient

from config import settings
from main import app
from services import operadora_service

client = TestClient(app)

def test_health_check():
    """Testa se a API está online"""
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["message"] == "API is online"
    if settings.USE_CSV:
        assert payload["mode"] == "CSV"
    else:
        assert payload["mode"] == "Database"

def test_read_operadoras():
    """Testa a listagem de operadoras (primeira página)"""
    response = client.get("/api/operadoras/?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
    assert len(data["data"]) <= 5

def test_search_operadora_valid():
    """Testa a busca de uma operadora específica existente"""
    if settings.USE_CSV:
        df = operadora_service.load_operadoras_csv()
        if df.empty or "cnpj" not in df.columns:
            pytest.skip("CSV de operadoras nao disponivel para teste.")
        cnpj = "".join(filter(str.isdigit, str(df.iloc[0]["cnpj"])))
        if not cnpj:
            pytest.skip("CSV de operadoras sem CNPJ valido para teste.")
    else:
        # Usando o CNPJ que confirmamos que existe: 27452545000195
        cnpj = "27452545000195"
    response = client.get(f"/api/operadoras/{cnpj}")
    assert response.status_code == 200
    data = response.json()
    assert "".join(filter(str.isdigit, data["cnpj"])) == cnpj

def test_search_operadora_invalid():
    """Testa a busca de uma operadora inexistente"""
    response = client.get("/api/operadoras/00000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Operadora not found"

def test_estatisticas_gerais():
    """Testa se o endpoint de estatísticas retorna a estrutura correta"""
    response = client.get("/api/estatisticas")
    assert response.status_code == 200
    data = response.json()
    assert "total_geral" in data
    assert "media_trimestral" in data
    assert "top_5_operadoras" in data
