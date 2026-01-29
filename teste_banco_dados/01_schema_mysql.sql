-- Teste 3.1 - Preparacao de banco (MySQL 8.0)
-- Ajuste os caminhos dos CSVs antes de executar o LOAD.

CREATE DATABASE IF NOT EXISTS teste_ans
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE teste_ans;

DROP TABLE IF EXISTS operadoras;
DROP TABLE IF EXISTS consolidado_despesas;
DROP TABLE IF EXISTS despesas_agregadas;

CREATE TABLE operadoras (
  operadora_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  registro_operadora INT,
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
  data_registro_ans DATE,
  KEY idx_operadoras_cnpj (cnpj),
  KEY idx_operadoras_registro (registro_operadora),
  KEY idx_operadoras_uf (uf)
) ENGINE=InnoDB;

CREATE TABLE consolidado_despesas (
  despesa_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  cnpj CHAR(14),
  razao_social TEXT,
  trimestre TINYINT,
  ano SMALLINT,
  valor_despesas DECIMAL(18,2),
  KEY idx_consolidado_cnpj (cnpj),
  KEY idx_consolidado_ano_tri (ano, trimestre),
  KEY idx_consolidado_razao (razao_social(120))
) ENGINE=InnoDB;

CREATE TABLE despesas_agregadas (
  agregada_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  razao_social TEXT,
  uf CHAR(2),
  total_despesas DECIMAL(20,6),
  media_despesas_trimestre DECIMAL(20,6),
  desvio_padrao_despesas DECIMAL(20,6),
  KEY idx_agregadas_uf (uf),
  KEY idx_agregadas_razao (razao_social(120))
) ENGINE=InnoDB;
