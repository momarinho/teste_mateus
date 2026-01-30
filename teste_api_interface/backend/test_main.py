from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Testa se a API está online"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API is online", "mode": "Database"}

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
    # Usando o CNPJ que confirmamos que existe: 27452545000195
    cnpj = "27452545000195"
    response = client.get(f"/api/operadoras/{cnpj}")
    assert response.status_code == 200
    data = response.json()
    assert data["cnpj"] == cnpj

def test_search_operadora_invalid():
    """Testa a busca de uma operadora inexistente"""
    response = client.get("/api/operadoras/00000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Operadora not found"

def test_estatisticas_gerais():
    """Testa se o endpoint de estatísticas retorna a estrutura correta"""
    response = client.get("/api/despesas/estatisticas")
    assert response.status_code == 200
    data = response.json()
    assert "total_geral" in data
    assert "media_trimestral" in data
    assert "top_5_operadoras" in data
