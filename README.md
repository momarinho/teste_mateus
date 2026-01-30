# Teste Técnico Intuitive Care - Mateus Marinho

Este repositório contém a solução completa para o Teste Técnico da Intuitive Care (v2.0), abrangendo todas as 4 fases do desafio: Integração com API, Transformação de Dados, Banco de Dados e Interface Web.

## 📁 Estrutura do Projeto

*   `teste_api_ans/`: Scripts da Fase 1 (Download e processamento API ANS).
*   `teste_transformacao_validacao/`: Scripts da Fase 2 (Limpeza e enriquecimento de dados).
*   `teste_banco_dados/`: Scripts SQL da Fase 3 (Schemas e Queries).
*   `teste_api_interface/`: Aplicação Web da Fase 4 (Backend FastAPI + Frontend Vue.js).
*   `data/`: Diretório de armazenamento de dados brutos e processados (alguns arquivos grandes podem não estar no Git).
*   `README.md`: Este arquivo de documentação.

---

## 🚀 Como Executar

O projeto foi desenvolvido em ambiente Windows, utilizando Python 3, Node.js (v18+) e MySQL 8.0.

### Pré-requisitos
*   Python 3.10+
*   Node.js & NPM
*   MySQL Server 8.0
*   Git

### Passo 1: Integração API e Dados (Fases 1 e 2)

Execute os scripts Python sequencialmente para baixar e preparar os dados:

```bash
# 1. Download e Processamento Inicial
python teste_api_ans/download_ans_demos.py
python teste_api_ans/process_ans_files.py
python teste_api_ans/consolidate_ans_expenses.py

# 2. Transformação e Validação
python teste_transformacao_validacao/run_transformation.py
```

Isso gerará os arquivos CSV finais em `teste_transformacao_validacao/` e `data/processed/`.

### Passo 2: Banco de Dados (Fase 3)

1.  Acesse seu MySQL Client (Workbench, DBeaver ou CLI).
2.  Execute os scripts na ordem:
    *   `teste_banco_dados/01_schema_mysql.sql`: Cria o banco e tabelas.
    *   `teste_banco_dados/03_import_mysql.sql`: Importa os dados dos CSVs gerados (ajuste os caminhos nos comandos `LOAD DATA` se necessário).
    *   `teste_banco_dados/04_queries_mysql.sql`: Executa as queries analíticas solicitadas.

> **Nota caso use CLI:** Certifique-se de habilitar `local-infile=1` no cliente e servidor MySQL para permitir a importação de CSVs locais.

### Passo 3: Interface Web (Fase 4)

A aplicação é composta por um Backend (FastAPI) e Frontend (Vue.js).

**Backend:**
```bash
cd teste_api_interface/backend
pip install -r requirements.txt
# Configure o .env se necessário (DB_PASSWORD, etc)
python main.py
# Servidor rodará em http://localhost:8000
```

**Frontend:**
```bash
cd teste_api_interface/frontend
npm install
npm run dev
# Acesse em http://localhost:5173
```

---

## ⚖️ Trade-offs Técnicos e Decisões de Arquitetura

Conforme solicitado, abaixo estão documentadas as decisões técnicas tomadas para cada desafio do teste.

### Fase 1: Processamento de Arquivos
*   **Memória vs Incremental:** Optei pelo **processamento incremental**. Dado que os arquivos da ANS podem ser grandes e históricos (vários anos/trimestres), carregar tudo em memória Pandas poderia estourar a RAM em ambientes menores. Processar arquivo por arquivo e fazer *append* no resultado final é mais seguro e escalável.

### Fase 2: Validação e Enriquecimento
*   **Tratamento de CNPJs Inválidos:** Optei por **segregar os dados**. Linhas com CNPJs inválidos ou nulos não são descartadas silenciosamente, mas também não poluem a base principal. Elas podem ser logadas ou salvas em um arquivo de "rejeitados" (como implementado no script de importação do banco), permitindo auditoria posterior sem comprometer a integridade das análises.
*   **Estratégia de Join:** Utilizei a biblioteca **Pandas (`merge`)**. Para o volume de dados atual (milhares de operadoras), o Pandas é extremamente eficiente e prático, permitindo joins em memória rápidos. Se o volume fosse na casa dos Terabytes, mudaria para PySpark ou Dask.
*   **Ordenação:** A ordenação foi feita via Pandas `sort_values`. É rápido e suficiente para datasets que cabem na memória.

### Fase 3: Banco de Dados
*   **Normalização:** Escolhi uma abordagem **híbrida (levemente desnormalizada)** para as despesas.
    *   `operadoras`: Tabela cadastral normalizada (chave: registro_operadora/cnpj).
    *   `consolidado_despesas`: Mantida separada para evitar duplicação de dados cadastrais a cada linha de despesa. Contudo, mantive `razao_social` nela temporariamente para facilitar queries rápidas de leitura humana, embora a boa prática estrita de 3NF sugerisse usar apenas o ID da operadora.
*   **Tipos de Dados:**
    *   **Monetários (`DECIMAL(18,2)`):** Imprescindível para valores financeiros para evitar erros de arredondamento de ponto flutuante (comuns em `FLOAT`).
    *   **Datas:** Utilizei `DATE` para campos de data completa e `INT`/`SMALLINT` para Ano/Trimestre, facilitando indexação e buscas por período.

### Fase 4: API e Interface
*   **Backend Framework (FastAPI vs Flask):** Escolhi **FastAPI**.
    *   *Justificativa:* Performance superior (ASGI), validação de dados nativa com Pydantic (reduz código de boilerplate) e geração automática de documentação (Swagger UI), o que acelera muito o desenvolvimento e teste.
*   **Paginação (Offset vs Cursor):** Escolhi **Offset-based (`page` e `limit`)**.
    *   *Justificativa:* É mais intuitivo para o usuário final em interfaces de tabelas ("Ir para página 5"). Cursor-based é melhor para performance em *scroll infinito* ou volumes massivos, mas para uma lista administrativa de ~1000 - ~2000 registros, Offset é perfeitamente adequado e mais simples de implementar no frontend.
*   **Cache:** Implementação planejada via **Cache Simples em Memória (opcional)** ou banco.
    *   Para `/api/estatisticas`: Como são queries pesadas de agregação, o ideal em produção é cachear por X minutos (ex: Redis) ou usar uma Materialized View no banco. No escopo deste teste, as queries são rápidas o suficiente para serem executadas em tempo real.
*   **Resposta da API:** Optei por **Dados + Metadados**.
    *   Ex: `{ "data": [...], "total": 100, "page": 1, "limit": 10 }`. Isso permite que o Frontend monte os componentes de paginação (número total de páginas) sem precisar fazer uma request separada.
*   **Busca no Frontend:** Optei por **Busca no Servidor**.
    *   *Justificativa:* Embora 1000 operadoras caibam na memória do navegador, realizar a filtragem no backend (SQL `LIKE` ou Full Text Search) é mais robusto, economiza banda (não precisa baixar tudo de uma vez) e já prepara a aplicação para escalar quando houver milhões de registros.
*   **Gerenciamento de Estado (Pinia):** Usei **Pinia** (padrão atual do Vue 3).
    *   Centraliza o estado das operadoras e paginação, facilitando a comunicação entre a lista, a barra de busca e a paginação sem "prop drilling" excessivo.

## 📚 Documentação da API

A documentação interativa (Swagger UI) está disponível em `/docs` quando o backend está rodando.
Além disso, uma **Postman Collection** (`postman_collection.json`) está incluída na raiz do projeto para testes externos.

---
## 🧪 Testes Automatizados (Diferencial)

Foi implementada uma suíte de testes unitários para o Backend, garantindo a integridade dos principais endpoints e regras de negócio.

Para executar:
```bash
cd teste_api_interface/backend
# Instale as dependências de teste
pip install pytest httpx
# Execute os testes
python -m pytest test_main.py
```
O resultado deve exibir `5 passed`, cobrindo:
1. Health Check
2. Listagem Paginada
3. Busca Válida
4. Tratamento de Erro (404)
5. Estatísticas Consolidadas

---
**Desenvolvido por Mateus Marinho**
