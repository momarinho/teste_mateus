# Teste 4: API e Interface Web

Este diretório contém a Fase 4 do projeto: **Desenvolvimento da API e Frontend**.

## Estrutura

- `backend/`: Código Python (FastAPI/Flask) para servir os dados e realizar cálculos.
- `frontend/`: Código Vue.js para visualizar os dados.

## Configuração do Backend (4.1)

1. Crie um ambiente virtual e instale as dependências:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

2. Configure o banco de dados:
   - Copie o arquivo `.env.example` para `.env` (se existir) ou crie um novo `.env`.
   - Edite as variáveis `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`.

3. Verifique a conexão com o banco de dados:
   ```bash
   python check_setup.py
   ```
   
   Se a conexão falhar, verifique `DB_PASSWORD`.
   Caso prefira usar CSVs em vez do Banco de Dados, defina `USE_CSV=True` no `.env`.

## Próximos Passos (Roadmap)

- [x] 4.1 Preparação de dados (Conexão validada)
- [ ] 4.2 Setup do Servidor (FastAPI)
- [ ] 4.2.1 Framework e rotas básicas
- [ ] 4.2.2 Paginação
- [ ] 4.2.3 Cache e Estatísticas
- [ ] 4.3 Setup do Frontend (Vue.js)
- [ ] ...
