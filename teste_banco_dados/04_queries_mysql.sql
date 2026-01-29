-- Teste 3.4 - Queries analiticas (MySQL 8.0)

-- Query 1: 5 operadoras com maior crescimento percentual entre o primeiro e o ultimo trimestre
WITH q_bounds AS (
  SELECT
    MIN(ano * 10 + trimestre) AS q_min,
    MAX(ano * 10 + trimestre) AS q_max
  FROM consolidado_despesas
),
quartis AS (
  SELECT
    cnpj,
    MAX(razao_social) AS razao_social,
    (ano * 10 + trimestre) AS qkey,
    SUM(valor_despesas) AS total
  FROM consolidado_despesas
  GROUP BY cnpj, qkey
),
base AS (
  SELECT
    q.cnpj,
    q.razao_social,
    SUM(CASE WHEN q.qkey = qb.q_min THEN q.total END) AS total_inicio,
    SUM(CASE WHEN q.qkey = qb.q_max THEN q.total END) AS total_fim
  FROM quartis q
  CROSS JOIN q_bounds qb
  GROUP BY q.cnpj, q.razao_social
)
SELECT
  cnpj,
  razao_social,
  total_inicio,
  total_fim,
  ((total_fim - total_inicio) / total_inicio) * 100 AS crescimento_pct
FROM base
WHERE total_inicio IS NOT NULL
  AND total_fim IS NOT NULL
  AND total_inicio > 0
ORDER BY crescimento_pct DESC
LIMIT 5;

-- Query 2: distribuicao de despesas por UF (top 5)
SELECT
  uf,
  SUM(total_despesas) AS total_despesas_uf,
  AVG(total_despesas) AS media_por_operadora
FROM despesas_agregadas
WHERE uf IS NOT NULL AND uf <> ''
GROUP BY uf
ORDER BY total_despesas_uf DESC
LIMIT 5;

-- Query 3: operadoras acima da media em pelo menos 2 dos 3 trimestres mais recentes
WITH quarters AS (
  SELECT DISTINCT
    ano * 10 + trimestre AS qkey
  FROM consolidado_despesas
  ORDER BY qkey DESC
  LIMIT 3
),
operadora_trimestre AS (
  SELECT
    cnpj,
    (ano * 10 + trimestre) AS qkey,
    SUM(valor_despesas) AS total
  FROM consolidado_despesas
  GROUP BY cnpj, qkey
),
media_trimestre AS (
  SELECT
    o.qkey,
    AVG(o.total) AS media_total
  FROM operadora_trimestre o
  WHERE o.qkey IN (SELECT qkey FROM quarters)
  GROUP BY o.qkey
),
flags AS (
  SELECT
    o.cnpj,
    o.qkey,
    CASE WHEN o.total > m.media_total THEN 1 ELSE 0 END AS acima_media
  FROM operadora_trimestre o
  JOIN media_trimestre m ON m.qkey = o.qkey
),
contagem AS (
  SELECT
    cnpj,
    SUM(acima_media) AS qtd_acima
  FROM flags
  GROUP BY cnpj
)
SELECT
  COUNT(*) AS operadoras_acima_media_em_2_trimestres
FROM contagem
WHERE qtd_acima >= 2;