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

## Trade-offs Técnicos - Backend

### 4.2.1 Escolha do Framework: **FastAPI** (Opção B)

**Justificativa:**
Optei pelo **FastAPI** em detrimento do Flask, considerando os seguintes pontos:

1.  **Performance e Assincronismo:**
    - O FastAPI é construído sobre Starlette (ASGI) e Pydantic, oferecendo performance significativamente superior ao Flask (WSGI) para operações de I/O, como consultas a banco de dados.
    - O suporte nativo a `async/await` permite lidar com múltiplas requisições concorrentes de forma eficiente, crucial para APIs que consomem dados de BD ou arquivos.

2.  **Validação de Dados e Tipagem:**
    - O uso do **Pydantic** garante validação automática de dados de entrada e saída baseada em *type hints* do Python. Isso reduz drasticamente a necessidade de código manual de validação e tratamento de erros (boilerplate).
    - Torna o código mais robusto e "self-documenting".

3.  **Documentação Automática:**
    - Gera automaticamente documentação interativa (Swagger UI e ReDoc) sem configuração extra. Isso facilita o teste das rotas e a comunicação com o Frontend (Vue.js), agilizando o desenvolvimento da Fase 4.3.

4.  **Facilidade de Manutenção:**
    - A estrutura modular (Routers, Schemas, Services) incentivada pelo FastAPI, aliada à injeção de dependências, facilita a manutenção e escalabilidade do projeto em comparação a um setup Flask básico que exigiria mais decisões de arquitetura e bibliotecas de terceiros (como Flask-RESTful ou Marshmallow).

---

## Próximos Passos (Roadmap)

- [x] 4.1 Preparação de dados (Conexão validada)
- [x] 4.2 Setup do Servidor (FastAPI)
- [x] 4.2.1 Framework escolhido e justificado
- [ ] 4.2.2 Paginação escolhida e justificada
- [ ] 4.2.3 Cache/consulta direta escolhido e justificado
- [ ] 4.2.4 Estrutura de resposta escolhida e justificada
- [ ] 4.3 Setup do Frontend (Vue.js)
