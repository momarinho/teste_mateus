-- Teste 3.3 - Importacao com validacao (MySQL 8.0)
-- Usa tabelas de staging e registra rejeicoes.
-- Ajuste os caminhos dos CSVs antes de executar.

USE teste_ans;

DROP TABLE IF EXISTS stg_operadoras;
DROP TABLE IF EXISTS stg_consolidado_despesas;
DROP TABLE IF EXISTS stg_despesas_agregadas;

CREATE TABLE IF NOT EXISTS operadoras_rejeitadas (
  registro_operadora TEXT,
  cnpj TEXT,
  razao_social TEXT,
  nome_fantasia TEXT,
  modalidade TEXT,
  logradouro TEXT,
  numero TEXT,
  complemento TEXT,
  bairro TEXT,
  cidade TEXT,
  uf TEXT,
  cep TEXT,
  ddd TEXT,
  telefone TEXT,
  fax TEXT,
  endereco_eletronico TEXT,
  representante TEXT,
  cargo_representante TEXT,
  regiao_de_comercializacao TEXT,
  data_registro_ans TEXT,
  motivo TEXT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS consolidado_despesas_rejeitadas (
  cnpj TEXT,
  razao_social TEXT,
  trimestre TEXT,
  ano TEXT,
  valor_despesas TEXT,
  motivo TEXT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS despesas_agregadas_rejeitadas (
  razao_social TEXT,
  uf TEXT,
  total_despesas TEXT,
  media_despesas_trimestre TEXT,
  desvio_padrao_despesas TEXT,
  motivo TEXT
) ENGINE=InnoDB;

CREATE TABLE stg_operadoras (
  registro_operadora TEXT,
  cnpj TEXT,
  razao_social TEXT,
  nome_fantasia TEXT,
  modalidade TEXT,
  logradouro TEXT,
  numero TEXT,
  complemento TEXT,
  bairro TEXT,
  cidade TEXT,
  uf TEXT,
  cep TEXT,
  ddd TEXT,
  telefone TEXT,
  fax TEXT,
  endereco_eletronico TEXT,
  representante TEXT,
  cargo_representante TEXT,
  regiao_de_comercializacao TEXT,
  data_registro_ans TEXT
) ENGINE=InnoDB;

CREATE TABLE stg_consolidado_despesas (
  cnpj TEXT,
  razao_social TEXT,
  trimestre TEXT,
  ano TEXT,
  valor_despesas TEXT
) ENGINE=InnoDB;

CREATE TABLE stg_despesas_agregadas (
  razao_social TEXT,
  uf TEXT,
  total_despesas TEXT,
  media_despesas_trimestre TEXT,
  desvio_padrao_despesas TEXT
) ENGINE=InnoDB;

LOAD DATA LOCAL INFILE 'C:/Users/Transporte-02/Desktop/teste_mateus/teste_transformacao_validacao/operadoras_ativas.csv'
INTO TABLE stg_operadoras
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ';'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

LOAD DATA LOCAL INFILE 'C:/Users/Transporte-02/Desktop/teste_mateus/data/processed/consolidado_despesas.csv'
INTO TABLE stg_consolidado_despesas
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

LOAD DATA LOCAL INFILE 'C:/Users/Transporte-02/Desktop/teste_mateus/teste_transformacao_validacao/despesas_agregadas.csv'
INTO TABLE stg_despesas_agregadas
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ';'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

-- Rejeicoes: operadoras
INSERT INTO operadoras_rejeitadas (
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
  data_registro_ans,
  motivo
)
SELECT
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
  data_registro_ans,
  CONCAT_WS(',',
    IF(cnpj_clean IS NULL OR cnpj_clean = '' OR CHAR_LENGTH(cnpj_clean) <> 14, 'cnpj_invalido', NULL),
    IF(razao_social_trim IS NULL OR razao_social_trim = '', 'razao_social_ausente', NULL),
    IF(registro_operadora_num IS NULL, 'registro_operadora_invalido', NULL)
  )
FROM (
  SELECT
    *,
    REGEXP_REPLACE(cnpj, '[^0-9]', '') AS cnpj_clean,
    TRIM(razao_social) AS razao_social_trim,
    CASE
      WHEN registro_operadora REGEXP '^[0-9]+$' THEN CAST(registro_operadora AS UNSIGNED)
      ELSE NULL
    END AS registro_operadora_num
  FROM stg_operadoras
) s
WHERE
  (cnpj_clean IS NULL OR cnpj_clean = '' OR CHAR_LENGTH(cnpj_clean) <> 14)
  OR (razao_social_trim IS NULL OR razao_social_trim = '')
  OR (registro_operadora_num IS NULL);

-- Carga: operadoras validas
INSERT INTO operadoras (
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
)
SELECT
  registro_operadora_num,
  cnpj_clean,
  razao_social_trim,
  NULLIF(nome_fantasia, ''),
  NULLIF(modalidade, ''),
  NULLIF(logradouro, ''),
  NULLIF(numero, ''),
  NULLIF(complemento, ''),
  NULLIF(bairro, ''),
  NULLIF(cidade, ''),
  NULLIF(uf, ''),
  NULLIF(cep, ''),
  NULLIF(ddd, ''),
  NULLIF(telefone, ''),
  NULLIF(fax, ''),
  NULLIF(endereco_eletronico, ''),
  NULLIF(representante, ''),
  NULLIF(cargo_representante, ''),
  NULLIF(regiao_de_comercializacao, ''),
  CASE
    WHEN data_registro_ans REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' THEN STR_TO_DATE(data_registro_ans, '%Y-%m-%d')
    WHEN data_registro_ans REGEXP '^[0-9]{2}/[0-9]{2}/[0-9]{4}$' THEN STR_TO_DATE(data_registro_ans, '%d/%m/%Y')
    ELSE NULL
  END
FROM (
  SELECT
    *,
    REGEXP_REPLACE(cnpj, '[^0-9]', '') AS cnpj_clean,
    TRIM(razao_social) AS razao_social_trim,
    CASE
      WHEN registro_operadora REGEXP '^[0-9]+$' THEN CAST(registro_operadora AS UNSIGNED)
      ELSE NULL
    END AS registro_operadora_num
  FROM stg_operadoras
) s
WHERE
  (cnpj_clean IS NOT NULL AND cnpj_clean <> '' AND CHAR_LENGTH(cnpj_clean) = 14)
  AND (razao_social_trim IS NOT NULL AND razao_social_trim <> '')
  AND (registro_operadora_num IS NOT NULL);

-- Rejeicoes: consolidado_despesas
INSERT INTO consolidado_despesas_rejeitadas (
  cnpj,
  razao_social,
  trimestre,
  ano,
  valor_despesas,
  motivo
)
SELECT
  cnpj,
  razao_social,
  trimestre,
  ano,
  valor_despesas,
  CONCAT_WS(',',
    IF(cnpj_clean IS NULL OR cnpj_clean = '' OR CHAR_LENGTH(cnpj_clean) <> 14, 'cnpj_invalido', NULL),
    IF(razao_social_trim IS NULL OR razao_social_trim = '', 'razao_social_ausente', NULL),
    IF(trimestre_num IS NULL, 'trimestre_invalido', NULL),
    IF(ano_num IS NULL, 'ano_invalido', NULL),
    IF(valor_num IS NULL, 'valor_invalido', NULL)
  )
FROM (
  SELECT
    *,
    REGEXP_REPLACE(cnpj, '[^0-9]', '') AS cnpj_clean,
    TRIM(razao_social) AS razao_social_trim,
    CASE
      WHEN trimestre REGEXP '^[0-9]+$' AND CAST(trimestre AS UNSIGNED) BETWEEN 1 AND 4 THEN CAST(trimestre AS UNSIGNED)
      ELSE NULL
    END AS trimestre_num,
    CASE
      WHEN ano REGEXP '^[0-9]+$' THEN CAST(ano AS UNSIGNED)
      ELSE NULL
    END AS ano_num,
    CASE
      WHEN REPLACE(valor_despesas, ',', '.') REGEXP '^-?[0-9]+(\\.[0-9]+)?$'
        THEN CAST(REPLACE(valor_despesas, ',', '.') AS DECIMAL(18,2))
      ELSE NULL
    END AS valor_num
  FROM stg_consolidado_despesas
) s
WHERE
  (cnpj_clean IS NULL OR cnpj_clean = '' OR CHAR_LENGTH(cnpj_clean) <> 14)
  OR (razao_social_trim IS NULL OR razao_social_trim = '')
  OR (trimestre_num IS NULL)
  OR (ano_num IS NULL)
  OR (valor_num IS NULL);

-- Carga: consolidado_despesas validas
INSERT INTO consolidado_despesas (
  cnpj,
  razao_social,
  trimestre,
  ano,
  valor_despesas
)
SELECT
  cnpj_clean,
  razao_social_trim,
  trimestre_num,
  ano_num,
  valor_num
FROM (
  SELECT
    *,
    REGEXP_REPLACE(cnpj, '[^0-9]', '') AS cnpj_clean,
    TRIM(razao_social) AS razao_social_trim,
    CASE
      WHEN trimestre REGEXP '^[0-9]+$' AND CAST(trimestre AS UNSIGNED) BETWEEN 1 AND 4 THEN CAST(trimestre AS UNSIGNED)
      ELSE NULL
    END AS trimestre_num,
    CASE
      WHEN ano REGEXP '^[0-9]+$' THEN CAST(ano AS UNSIGNED)
      ELSE NULL
    END AS ano_num,
    CASE
      WHEN REPLACE(valor_despesas, ',', '.') REGEXP '^-?[0-9]+(\\.[0-9]+)?$'
        THEN CAST(REPLACE(valor_despesas, ',', '.') AS DECIMAL(18,2))
      ELSE NULL
    END AS valor_num
  FROM stg_consolidado_despesas
) s
WHERE
  (cnpj_clean IS NOT NULL AND cnpj_clean <> '' AND CHAR_LENGTH(cnpj_clean) = 14)
  AND (razao_social_trim IS NOT NULL AND razao_social_trim <> '')
  AND (trimestre_num IS NOT NULL)
  AND (ano_num IS NOT NULL)
  AND (valor_num IS NOT NULL);

-- Rejeicoes: despesas_agregadas
INSERT INTO despesas_agregadas_rejeitadas (
  razao_social,
  uf,
  total_despesas,
  media_despesas_trimestre,
  desvio_padrao_despesas,
  motivo
)
SELECT
  razao_social,
  uf,
  total_despesas,
  media_despesas_trimestre,
  desvio_padrao_despesas,
  CONCAT_WS(',',
    IF(razao_social_trim IS NULL OR razao_social_trim = '', 'razao_social_ausente', NULL),
    IF(uf_trim IS NULL OR uf_trim = '' OR CHAR_LENGTH(uf_trim) <> 2, 'uf_invalida', NULL),
    IF(total_num IS NULL, 'total_invalido', NULL)
  )
FROM (
  SELECT
    *,
    TRIM(razao_social) AS razao_social_trim,
    TRIM(uf) AS uf_trim,
    CASE
      WHEN REPLACE(total_despesas, ',', '.') REGEXP '^-?[0-9]+(\\.[0-9]+)?$'
        THEN CAST(REPLACE(total_despesas, ',', '.') AS DECIMAL(20,6))
      ELSE NULL
    END AS total_num,
    CASE
      WHEN REPLACE(media_despesas_trimestre, ',', '.') REGEXP '^-?[0-9]+(\\.[0-9]+)?$'
        THEN CAST(REPLACE(media_despesas_trimestre, ',', '.') AS DECIMAL(20,6))
      ELSE NULL
    END AS media_num,
    CASE
      WHEN REPLACE(desvio_padrao_despesas, ',', '.') REGEXP '^-?[0-9]+(\\.[0-9]+)?$'
        THEN CAST(REPLACE(desvio_padrao_despesas, ',', '.') AS DECIMAL(20,6))
      ELSE NULL
    END AS desvio_num
  FROM stg_despesas_agregadas
) s
WHERE
  (razao_social_trim IS NULL OR razao_social_trim = '')
  OR (uf_trim IS NULL OR uf_trim = '' OR CHAR_LENGTH(uf_trim) <> 2)
  OR (total_num IS NULL);

-- Carga: despesas_agregadas validas
INSERT INTO despesas_agregadas (
  razao_social,
  uf,
  total_despesas,
  media_despesas_trimestre,
  desvio_padrao_despesas
)
SELECT
  razao_social_trim,
  uf_trim,
  total_num,
  media_num,
  desvio_num
FROM (
  SELECT
    *,
    TRIM(razao_social) AS razao_social_trim,
    TRIM(uf) AS uf_trim,
    CASE
      WHEN REPLACE(total_despesas, ',', '.') REGEXP '^-?[0-9]+(\\.[0-9]+)?$'
        THEN CAST(REPLACE(total_despesas, ',', '.') AS DECIMAL(20,6))
      ELSE NULL
    END AS total_num,
    CASE
      WHEN REPLACE(media_despesas_trimestre, ',', '.') REGEXP '^-?[0-9]+(\\.[0-9]+)?$'
        THEN CAST(REPLACE(media_despesas_trimestre, ',', '.') AS DECIMAL(20,6))
      ELSE NULL
    END AS media_num,
    CASE
      WHEN REPLACE(desvio_padrao_despesas, ',', '.') REGEXP '^-?[0-9]+(\\.[0-9]+)?$'
        THEN CAST(REPLACE(desvio_padrao_despesas, ',', '.') AS DECIMAL(20,6))
      ELSE NULL
    END AS desvio_num
  FROM stg_despesas_agregadas
) s
WHERE
  (razao_social_trim IS NOT NULL AND razao_social_trim <> '')
  AND (uf_trim IS NOT NULL AND uf_trim <> '' AND CHAR_LENGTH(uf_trim) = 2)
  AND (total_num IS NOT NULL);