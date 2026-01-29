# Teste 2: Transformação e Validação de Dados

Este diretório contém a solução em Python para o **Teste 2**, que foca na validação, enriquecimento e agregação dos dados de despesas das operadoras da ANS.

## Dependências

- Python 3.9+
- Pandas

Para instalar a dependência, execute:
```bash
pip install pandas
```

## Como Executar

O script principal `run_transformation.py` é projetado para executar todas as etapas do Teste 2 em sequência.

**Pré-requisito:** Antes de executar este script, certifique-se de que os scripts do **Teste 1** foram executados e o arquivo `data/processed/consolidado_despesas.csv` existe.

Para iniciar o processo, execute:
```bash
python teste_transformacao_validacao/run_transformation.py
```

## O que o script faz

### Etapa 2.1: Validação de Dados

1.  **Carregamento:** O script carrega o arquivo `consolidado_despesas.csv` gerado pelo Teste 1.
2.  **Validação:** Cada linha é submetida a um conjunto de validações:
    - **CNPJ:** Verifica o formato (14 dígitos) e os dígitos verificadores.
    - **Valor de Despesa:** Garante que o valor é numérico e positivo (> 0).
    - **Razão Social:** Verifica se o campo não está vazio.
3.  **Registro de Problemas:** Em vez de descartar linhas com falhas, o script adiciona a coluna `problemas_validacao`, que lista todas as inconsistências encontradas em cada registro.
4.  **Saída:** O resultado é salvo no arquivo `teste_transformacao_validacao/2.1_dados_validados.csv`.

---

## Decisões Técnicas e Trade-offs

### 2.1. Validação de Dados - Estratégia para Tratamento de CNPJs Inválidos

*   **Abordagem Escolhida:** **Marcar e Consolidar (Flag and Consolidate Issues)**. Em vez de remover as linhas com CNPJs inválidos (ou outros problemas de validação), foi criada uma nova coluna chamada `problemas_validacao`. Esta coluna armazena uma lista separada por vírgulas de todos os problemas encontrados em uma determinada linha (ex: `cnpj_invalido`, `valor_nao_positivo`). Linhas sem problemas têm este campo vazio.

*   **Prós:**
    *   **Não há perda de dados:** Todos os registros originais são mantidos, permitindo uma análise completa da qualidade dos dados brutos e a possibilidade de correção manual futura.
    *   **Centralização de Problemas:** Todos os tipos de erros de validação (CNPJ, valor, Razão Social) são consolidados em um único local, simplificando a filtragem e a análise de inconsistências.
    *   **Rastreabilidade:** Facilita a identificação da origem e da frequência de cada tipo de erro.

*   **Contras:**
    *   **Necessidade de Tratamento Posterior:** As etapas subsequentes do processo (como enriquecimento e agregação) precisam estar cientes da coluna `problemas_validacao` e devem filtrar ativamente as linhas problemáticas para garantir a precisão das análises.
    *   **Aumento do Tamanho do Arquivo:** A adição da nova coluna aumenta ligeiramente o tamanho do arquivo de dados.

---

### 2.2. Enriquecimento de Dados - Estratégia de Join e Processamento

**(Decisão a ser documentada aqui)**

*   **Abordagem Escolhida:**
*   **Justificativa:**

### 2.2. Enriquecimento de Dados - Tratamento de Registros sem Match e Duplicados

**(Decisão a ser documentada aqui)**

*   **Registros sem match:**
*   **CNPJs duplicados:**

---

### 2.3. Agregação - Estratégia de Ordenação

**(Decisão a ser documentada aqui)**

*   **Abordagem Escolhida:**
*   **Justificativa:**

---