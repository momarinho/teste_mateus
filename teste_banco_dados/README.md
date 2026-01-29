# Teste 3: Banco de Dados e Analise

Este diretorio contem os scripts SQL para a etapa **3** do teste (carga de CSVs e preparacao do banco) com suporte a **MySQL 8.0** e **PostgreSQL > 10**.

## Arquivos

- `01_schema_mysql.sql`: cria database, tabelas e indices (MySQL).
- `02_load_mysql.sql`: carrega os CSVs via `LOAD DATA LOCAL INFILE` (MySQL).
- `01_schema_postgres.sql`: cria schema, tabelas e indices (PostgreSQL).
- `02_load_postgres.sql`: carrega os CSVs via `\copy` (psql).

## Estrutura (3.2)

- Cada tabela possui chave primaria surrogate (`*_id`) para permitir carga mesmo com
  inconsistencias (ex.: CNPJ ausente).
- Indices principais: `cnpj` e `(ano, trimestre)` no consolidado, `uf` nas agregadas,
  e `cnpj`/`registro_operadora` no cadastro.

## Pre-requisitos

- Ter os CSVs gerados nos testes anteriores:
  - `data/processed/consolidado_despesas.csv` (Teste 1.3)
  - `teste_transformacao_validacao/despesas_agregadas.csv` (Teste 2.3)
  - `teste_transformacao_validacao/operadoras_ativas.csv` (Teste 2.2)

## Como executar (MySQL 8.0)

1) Abra o cliente MySQL com `LOCAL INFILE` habilitado.
2) Ajuste os caminhos dos CSVs no arquivo `02_load_mysql.sql`.
3) Execute:

```sql
SOURCE teste_banco_dados/01_schema_mysql.sql;
SOURCE teste_banco_dados/02_load_mysql.sql;
```

## Como executar (PostgreSQL > 10)

1) Abra o `psql` apontando para o banco desejado.
2) Ajuste os caminhos dos CSVs no arquivo `02_load_postgres.sql`.
3) Execute:

```sql
\i teste_banco_dados/01_schema_postgres.sql
\i teste_banco_dados/02_load_postgres.sql
```

## Observacoes e trade-offs

- Normalizacao (opcao B - tabelas separadas): evita duplicacao do cadastro em grandes volumes,
  facilita atualizacoes pontuais e mantem queries analiticas com joins simples por CNPJ.
  O trade-off e a necessidade de join, mas o ganho de consistencia e manutencao compensa.
- Tipos de dados: valores monetarios em DECIMAL/NUMERIC para precisao exata; DATE para datas
  por ser suficiente e mais simples que TIMESTAMP quando o horario nao e relevante.
- `despesas_agregadas.csv` usa **virgula como separador decimal**. Os scripts fazem a conversao (virgula -> ponto) antes de inserir.
- Para PostgreSQL foi usada uma tabela temporaria para converter os valores numericos.
- As tabelas foram modeladas de forma simples, mantendo colunas em texto quando o CSV nao garante padrao estrito.
