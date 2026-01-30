# Teste Intuitive Care - Projeto

Este repositorio cobre as fases **1**, **2** e **3** do teste.

Para detalhes completos, consulte:
- `teste_api_ans/README.md` (Teste 1: download, processamento e consolidacao)
- `teste_transformacao_validacao/README.md` (Teste 2: validacao, enriquecimento e agregacao)
- `teste_banco_dados/README.md` (Teste 3: banco de dados e analise)
- `teste_api_interface/README.md` (Teste 4: API FastAPI e Interface Vue.js)

## Execucao rapida (resumo)

### Teste 1
```bash
python teste_api_ans/download_ans_demos.py
python teste_api_ans/process_ans_files.py
python teste_api_ans/consolidate_ans_expenses.py
```

### Teste 2
```bash
python teste_transformacao_validacao/run_transformation.py
```

### Teste 3
- MySQL: executar `teste_banco_dados/01_schema_mysql.sql` e `teste_banco_dados/02_load_mysql.sql`
- MySQL (validacao + analises): `teste_banco_dados/03_import_mysql.sql` e `teste_banco_dados/04_queries_mysql.sql`
- PostgreSQL: executar `teste_banco_dados/01_schema_postgres.sql` e `teste_banco_dados/02_load_postgres.sql`
- PostgreSQL (validacao + analises): `teste_banco_dados/03_import_postgres.sql` e `teste_banco_dados/04_queries_postgres.sql`

### Teste 4 (Web Interface)
- Backend:
  ```bash
  cd teste_api_interface/backend && pip install -r requirements.txt && uvicorn main:app --reload
  ```
- Frontend:
  ```bash
  cd teste_api_interface/frontend && npm install && npm run dev
  ```

## Observacoes
- Os ZIPs gerados nas etapas intermediarias nao precisam ser versionados.
- O ZIP final do projeto (entrega) sera gerado ao final do teste.
- Status: scripts de banco estao prontos, mas a execucao em MySQL ficou para momento posterior.
