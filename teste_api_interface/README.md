# Teste 4 - API e Interface Web

Este diretório contém a implementação do backend (FastAPI) e frontend (Vue.js) para visualização e busca de dados de operadoras da ANS.

## Estrutura
*   `backend/`: Código da API em Python/FastAPI.
*   `frontend/`: Código da Interface em Vue.js 3 + Pinia + Vite.
*   `postman_collection.json`: Coleção do Postman para testes da API.
*   `ARCHITECTURE.md`: Documentação das decisões de arquitetura e trade-offs (item 4.3 do roadmap).

## Pré-requisitos
*   Python 3.9+
*   Node.js 16+
*   MySQL (Opcional, se usar modo Database. O padrão é usar CSVs gerados nas etapas anteriores).

## Instruções de Execução

### 1. Backend
1.  Navegue até a pasta `backend`:
    ```bash
    cd backend
    ```
2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure o `.env` se necessário. Por padrão, ele busca os CSVs nas pastas irmãs (`teste_transformacao_validacao` e `data/processed`).
4.  Inicie o servidor:
    ```bash
    uvicorn main:app --reload
    ```
    A API estará disponível em `http://127.0.0.1:8000`.
    Documentação automática (Swagger): `http://127.0.0.1:8000/docs`.

### 2. Frontend
1.  Navegue até a pasta `frontend`:
    ```bash
    cd frontend
    ```
2.  Instale as dependências:
    ```bash
    npm install
    ```
3.  Inicie o servidor de desenvolvimento:
    ```bash
    npm run dev
    ```
    Acesse a interface no navegador (Geralmente `http://localhost:5173`).

## Funcionalidades
*   **Listagem de Operadoras:** Paginação server-side, busca por Razão Social ou CNPJ.
*   **Detalhes:** Visualização completa dos dados da operadora e histórico de despesas.
*   **Gráfico:** Distribuição de despesas por UF (Doughnut Chart).
*   **Modo Híbrido:** O backend suporta leitura direta dos CSVs (padrão para avaliação rápida) ou conexão com Banco de Dados MySQL (configurável via `.env`).
