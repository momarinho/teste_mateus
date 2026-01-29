-- Teste 3.1 - Preparacao de banco (PostgreSQL > 10)

CREATE SCHEMA IF NOT EXISTS teste_ans;
SET search_path TO teste_ans;

DROP TABLE IF EXISTS operadoras;
DROP TABLE IF EXISTS consolidado_despesas;
DROP TABLE IF EXISTS despesas_agregadas;

CREATE TABLE operadoras (
  registro_operadora INTEGER,
  cnpj CHAR(14),
  razao_social TEXT,
  nome_fantasia TEXT,
  modalidade VARCHAR(120),
  logradouro TEXT,
  numero VARCHAR(30),
  complemento TEXT,
  bairro TEXT,
  cidade VARCHAR(120),
  uf CHAR(2),
  cep VARCHAR(12),
  ddd VARCHAR(6),
  telefone VARCHAR(20),
  fax VARCHAR(20),
  endereco_eletronico VARCHAR(200),
  representante TEXT,
  cargo_representante TEXT,
  regiao_de_comercializacao VARCHAR(10),
  data_registro_ans DATE
);

CREATE INDEX idx_operadoras_cnpj ON operadoras (cnpj);
CREATE INDEX idx_operadoras_registro ON operadoras (registro_operadora);

CREATE TABLE consolidado_despesas (
  cnpj CHAR(14),
  razao_social TEXT,
  trimestre SMALLINT,
  ano SMALLINT,
  valor_despesas NUMERIC(18,2)
);

CREATE INDEX idx_consolidado_cnpj ON consolidado_despesas (cnpj);
CREATE INDEX idx_consolidado_ano_tri ON consolidado_despesas (ano, trimestre);

CREATE TABLE despesas_agregadas (
  razao_social TEXT,
  uf CHAR(2),
  total_despesas NUMERIC(20,6),
  media_despesas_trimestre NUMERIC(20,6),
  desvio_padrao_despesas NUMERIC(20,6)
);

CREATE INDEX idx_agregadas_uf ON despesas_agregadas (uf);