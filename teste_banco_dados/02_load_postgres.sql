-- Teste 3.1 - Carga de CSVs (PostgreSQL > 10)
-- Execute via psql. Ajuste os caminhos dos CSVs antes de rodar.

SET search_path TO teste_ans;

-- Operadoras (teste 2.2)
\copy operadoras (
  registro_operadora,
  cnpj,
  razao_social,
  nome_fantasia,
  modalidade,
  logradouro,
  numero,
  complemento,
  bairro,
  cidade,
  uf,
  cep,
  ddd,
  telefone,
  fax,
  endereco_eletronico,
  representante,
  cargo_representante,
  regiao_de_comercializacao,
  data_registro_ans
) FROM 'C:/Users/Transporte-02/Desktop/teste_mateus/teste_transformacao_validacao/operadoras_ativas.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ';', QUOTE '"', NULL '');

-- Consolidado de despesas (teste 1.3)
\copy consolidado_despesas (
  cnpj,
  razao_social,
  trimestre,
  ano,
  valor_despesas
) FROM 'C:/Users/Transporte-02/Desktop/teste_mateus/data/processed/consolidado_despesas.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', QUOTE '"', NULL '');

-- Despesas agregadas (teste 2.3) - valores com virgula decimal
CREATE TEMP TABLE stg_despesas_agregadas (
  razao_social TEXT,
  uf CHAR(2),
  total_despesas_text TEXT,
  media_despesas_trimestre_text TEXT,
  desvio_padrao_despesas_text TEXT
);

\copy stg_despesas_agregadas FROM 'C:/Users/Transporte-02/Desktop/teste_mateus/teste_transformacao_validacao/despesas_agregadas.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ';', QUOTE '"', NULL '');

INSERT INTO despesas_agregadas (
  razao_social,
  uf,
  total_despesas,
  media_despesas_trimestre,
  desvio_padrao_despesas
)
SELECT
  razao_social,
  uf,
  NULLIF(REPLACE(total_despesas_text, ',', '.'), '')::NUMERIC(20,6),
  NULLIF(REPLACE(media_despesas_trimestre_text, ',', '.'), '')::NUMERIC(20,6),
  NULLIF(REPLACE(desvio_padrao_despesas_text, ',', '.'), '')::NUMERIC(20,6)
FROM stg_despesas_agregadas;

DROP TABLE stg_despesas_agregadas;