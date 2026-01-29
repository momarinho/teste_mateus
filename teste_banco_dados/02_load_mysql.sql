-- Teste 3.1 - Carga de CSVs (MySQL 8.0)
-- Ajuste os caminhos abaixo para o seu ambiente.

USE teste_ans;

-- Operadoras (teste 2.2)
LOAD DATA LOCAL INFILE 'C:/Users/Transporte-02/Desktop/teste_mateus/teste_transformacao_validacao/operadoras_ativas.csv'
INTO TABLE operadoras
FIELDS TERMINATED BY ';'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
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
  @data_registro_ans
)
SET data_registro_ans = NULLIF(@data_registro_ans, '');

-- Consolidado de despesas (teste 1.3)
LOAD DATA LOCAL INFILE 'C:/Users/Transporte-02/Desktop/teste_mateus/data/processed/consolidado_despesas.csv'
INTO TABLE consolidado_despesas
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
  cnpj,
  razao_social,
  trimestre,
  ano,
  valor_despesas
);

-- Despesas agregadas (teste 2.3) - valores com virgula decimal
LOAD DATA LOCAL INFILE 'C:/Users/Transporte-02/Desktop/teste_mateus/teste_transformacao_validacao/despesas_agregadas.csv'
INTO TABLE despesas_agregadas
FIELDS TERMINATED BY ';'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
  razao_social,
  uf,
  @total_despesas,
  @media_despesas_trimestre,
  @desvio_padrao_despesas
)
SET
  total_despesas = NULLIF(REPLACE(@total_despesas, ',', '.'), ''),
  media_despesas_trimestre = NULLIF(REPLACE(@media_despesas_trimestre, ',', '.'), ''),
  desvio_padrao_despesas = NULLIF(REPLACE(@desvio_padrao_despesas, ',', '.'), '');