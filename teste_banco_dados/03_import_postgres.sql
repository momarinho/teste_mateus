-- Teste 3.3 - Importacao com validacao (PostgreSQL > 10)
-- Usa tabelas de staging e registra rejeicoes.
-- Ajuste os caminhos dos CSVs antes de executar.

SET search_path TO teste_ans;

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
);

CREATE TABLE IF NOT EXISTS consolidado_despesas_rejeitadas (
  cnpj TEXT,
  razao_social TEXT,
  trimestre TEXT,
  ano TEXT,
  valor_despesas TEXT,
  motivo TEXT
);

CREATE TABLE IF NOT EXISTS despesas_agregadas_rejeitadas (
  razao_social TEXT,
  uf TEXT,
  total_despesas TEXT,
  media_despesas_trimestre TEXT,
  desvio_padrao_despesas TEXT,
  motivo TEXT
);

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
);

CREATE TABLE stg_consolidado_despesas (
  cnpj TEXT,
  razao_social TEXT,
  trimestre TEXT,
  ano TEXT,
  valor_despesas TEXT
);

CREATE TABLE stg_despesas_agregadas (
  razao_social TEXT,
  uf TEXT,
  total_despesas TEXT,
  media_despesas_trimestre TEXT,
  desvio_padrao_despesas TEXT
);

\copy stg_operadoras FROM 'C:/Users/Transporte-02/Desktop/teste_mateus/teste_transformacao_validacao/operadoras_ativas.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ';', QUOTE '"', NULL '', ENCODING 'UTF8');

\copy stg_consolidado_despesas FROM 'C:/Users/Transporte-02/Desktop/teste_mateus/data/processed/consolidado_despesas.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', QUOTE '"', NULL '', ENCODING 'UTF8');

\copy stg_despesas_agregadas FROM 'C:/Users/Transporte-02/Desktop/teste_mateus/teste_transformacao_validacao/despesas_agregadas.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ';', QUOTE '"', NULL '', ENCODING 'UTF8');

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
  concat_ws(',',
    CASE WHEN cnpj_clean IS NULL OR cnpj_clean = '' OR length(cnpj_clean) <> 14 THEN 'cnpj_invalido' END,
    CASE WHEN razao_social_trim IS NULL OR razao_social_trim = '' THEN 'razao_social_ausente' END,
    CASE WHEN registro_operadora_num IS NULL THEN 'registro_operadora_invalido' END
  )
FROM (
  SELECT
    *,
    regexp_replace(cnpj, '[^0-9]', '', 'g') AS cnpj_clean,
    btrim(razao_social) AS razao_social_trim,
    CASE
      WHEN registro_operadora ~ '^[0-9]+$' THEN registro_operadora::integer
      ELSE NULL
    END AS registro_operadora_num
  FROM stg_operadoras
) s
WHERE
  (cnpj_clean IS NULL OR cnpj_clean = '' OR length(cnpj_clean) <> 14)
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
    WHEN data_registro_ans ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' THEN to_date(data_registro_ans, 'YYYY-MM-DD')
    WHEN data_registro_ans ~ '^[0-9]{2}/[0-9]{2}/[0-9]{4}$' THEN to_date(data_registro_ans, 'DD/MM/YYYY')
    ELSE NULL
  END
FROM (
  SELECT
    *,
    regexp_replace(cnpj, '[^0-9]', '', 'g') AS cnpj_clean,
    btrim(razao_social) AS razao_social_trim,
    CASE
      WHEN registro_operadora ~ '^[0-9]+$' THEN registro_operadora::integer
      ELSE NULL
    END AS registro_operadora_num
  FROM stg_operadoras
) s
WHERE
  (cnpj_clean IS NOT NULL AND cnpj_clean <> '' AND length(cnpj_clean) = 14)
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
  concat_ws(',',
    CASE WHEN cnpj_clean IS NULL OR cnpj_clean = '' OR length(cnpj_clean) <> 14 THEN 'cnpj_invalido' END,
    CASE WHEN razao_social_trim IS NULL OR razao_social_trim = '' THEN 'razao_social_ausente' END,
    CASE WHEN trimestre_num IS NULL THEN 'trimestre_invalido' END,
    CASE WHEN ano_num IS NULL THEN 'ano_invalido' END,
    CASE WHEN valor_num IS NULL THEN 'valor_invalido' END
  )
FROM (
  SELECT
    *,
    regexp_replace(cnpj, '[^0-9]', '', 'g') AS cnpj_clean,
    btrim(razao_social) AS razao_social_trim,
    CASE
      WHEN trimestre ~ '^[0-9]+$' AND trimestre::integer BETWEEN 1 AND 4 THEN trimestre::integer
      ELSE NULL
    END AS trimestre_num,
    CASE
      WHEN ano ~ '^[0-9]+$' THEN ano::integer
      ELSE NULL
    END AS ano_num,
    CASE
      WHEN replace(valor_despesas, ',', '.') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN replace(valor_despesas, ',', '.')::numeric(18,2)
      ELSE NULL
    END AS valor_num
  FROM stg_consolidado_despesas
) s
WHERE
  (cnpj_clean IS NULL OR cnpj_clean = '' OR length(cnpj_clean) <> 14)
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
    regexp_replace(cnpj, '[^0-9]', '', 'g') AS cnpj_clean,
    btrim(razao_social) AS razao_social_trim,
    CASE
      WHEN trimestre ~ '^[0-9]+$' AND trimestre::integer BETWEEN 1 AND 4 THEN trimestre::integer
      ELSE NULL
    END AS trimestre_num,
    CASE
      WHEN ano ~ '^[0-9]+$' THEN ano::integer
      ELSE NULL
    END AS ano_num,
    CASE
      WHEN replace(valor_despesas, ',', '.') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN replace(valor_despesas, ',', '.')::numeric(18,2)
      ELSE NULL
    END AS valor_num
  FROM stg_consolidado_despesas
) s
WHERE
  (cnpj_clean IS NOT NULL AND cnpj_clean <> '' AND length(cnpj_clean) = 14)
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
  concat_ws(',',
    CASE WHEN razao_social_trim IS NULL OR razao_social_trim = '' THEN 'razao_social_ausente' END,
    CASE WHEN uf_trim IS NULL OR uf_trim = '' OR length(uf_trim) <> 2 THEN 'uf_invalida' END,
    CASE WHEN total_num IS NULL THEN 'total_invalido' END
  )
FROM (
  SELECT
    *,
    btrim(razao_social) AS razao_social_trim,
    btrim(uf) AS uf_trim,
    CASE
      WHEN replace(total_despesas, ',', '.') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN replace(total_despesas, ',', '.')::numeric(20,6)
      ELSE NULL
    END AS total_num,
    CASE
      WHEN replace(media_despesas_trimestre, ',', '.') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN replace(media_despesas_trimestre, ',', '.')::numeric(20,6)
      ELSE NULL
    END AS media_num,
    CASE
      WHEN replace(desvio_padrao_despesas, ',', '.') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN replace(desvio_padrao_despesas, ',', '.')::numeric(20,6)
      ELSE NULL
    END AS desvio_num
  FROM stg_despesas_agregadas
) s
WHERE
  (razao_social_trim IS NULL OR razao_social_trim = '')
  OR (uf_trim IS NULL OR uf_trim = '' OR length(uf_trim) <> 2)
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
    btrim(razao_social) AS razao_social_trim,
    btrim(uf) AS uf_trim,
    CASE
      WHEN replace(total_despesas, ',', '.') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN replace(total_despesas, ',', '.')::numeric(20,6)
      ELSE NULL
    END AS total_num,
    CASE
      WHEN replace(media_despesas_trimestre, ',', '.') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN replace(media_despesas_trimestre, ',', '.')::numeric(20,6)
      ELSE NULL
    END AS media_num,
    CASE
      WHEN replace(desvio_padrao_despesas, ',', '.') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN replace(desvio_padrao_despesas, ',', '.')::numeric(20,6)
      ELSE NULL
    END AS desvio_num
  FROM stg_despesas_agregadas
) s
WHERE
  (razao_social_trim IS NOT NULL AND razao_social_trim <> '')
  AND (uf_trim IS NOT NULL AND uf_trim <> '' AND length(uf_trim) = 2)
  AND (total_num IS NOT NULL);