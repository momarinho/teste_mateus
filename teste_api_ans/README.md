# Teste Intuitive Care - Parte 1.1 (ANS)

Este diretório contém a solução em Python para a etapa **1.1 Acesso à API de Dados Abertos da ANS**. O objetivo é identificar e baixar os arquivos de **Demonstrações Contábeis** dos **últimos 3 trimestres disponíveis**.

## Requisitos

- Python 3.9+
- Acesso à internet

## Como executar (apenas 1.1)

1) A partir deste diretório, rode:

```bash
python download_ans_demos.py
```

Por padrão, o script:
- Usa a base `https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/`
- Seleciona os **3 trimestres mais recentes** disponíveis
- Faz download para `data/demonstracoes_contabeis/`
- Gera um arquivo `manifest.json` no mesmo diretório

2) Se quiser ajustar parâmetros:

```bash
python download_ans_demos.py ^
  --quarters 3 ^
  --output-dir data/demonstracoes_contabeis ^
  --max-depth 2 ^
  --timeout 30
```

Opções úteis:
- `--dry-run` apenas lista o que seria baixado (sem salvar arquivos)
- `--overwrite` força o download mesmo se o arquivo já existir
- `--extensions` controla as extensões aceitas (ex: `.zip,.csv,.xlsx`)

## O que o script faz

1) Navega pela pasta `demonstracoes_contabeis/`.
2) Identifica pastas/arquivos por **ano** e **trimestre** com regex `1T2025`, `2T2024`, etc.
3) Seleciona os **3 trimestres mais recentes**, mesmo se houver variações:
   - arquivos diretamente no ano
   - pastas por trimestre
   - múltiplos arquivos por trimestre
4) Baixa todos os arquivos encontrados para cada trimestre selecionado.

## Manifest

O arquivo `manifest.json` registra:
- URL de origem
- Caminho local do arquivo
- Trimestre associado
- Status do download (downloaded/skipped/error)

## Trade-offs técnicos (resumo)

- **Parser HTML (stdlib)**: usei `html.parser` para evitar dependências externas; é suficiente para o índice simples do FTP.
- **Detecção flexível de trimestre**: regex sobre o caminho do link, permitindo variações como arquivos diretamente no ano ou subpastas.
- **Recursão com profundidade limitada**: evita varrer estruturas muito profundas, mas cobre subpastas típicas dos trimestres.
- **Extensões configuráveis**: reduz risco de baixar páginas HTML indevidas; pode ser ajustado via `--extensions`.

## Próximas partes (1.2 e 1.3)

## Parte 1.2 - Processamento de Arquivos

### Requisitos adicionais

- Python 3.9+
- `openpyxl` para leitura de XLSX:

```bash
pip install openpyxl
```

### Como executar (1.2)

```bash
python process_ans_files.py
```

O script:
- Lê os ZIPs baixados na etapa 1.1 (ou usa `manifest.json` se existir)
- Extrai automaticamente os ZIPs
- Processa somente arquivos que contenham **Despesas com Eventos/Sinistros**
- Normaliza a estrutura em CSVs padronizados em `data/processed/normalized/`
- Gera `data/processed/process_manifest.json`
- Mantém `reg_ans` quando disponível para rastreabilidade entre etapas
- Registra erros e um resumo de processamento no `process_manifest.json`

### Trade-off técnico (processamento incremental)

Optei por **processamento incremental** (streaming), lendo linha a linha nos CSV/TXT
e iterando linhas no XLSX com `openpyxl` em modo `read_only`. Essa abordagem:
- Reduz uso de memória para arquivos grandes
- Evita carregar datasets inteiros em RAM
- Permite continuar mesmo com arquivos extensos

O trade-off é um código um pouco mais complexo que a abordagem
`pandas.read_csv()`/`read_excel()` completa em memória, mas é mais seguro para
volumes variáveis.

## Próximas partes (1.3)

## Parte 1.3 - Consolidação e Análise

### Como executar (1.3)

```bash
python consolidate_ans_expenses.py
```

Saídas:
- CSV consolidado: `data/processed/consolidado_despesas.csv`
- ZIP: `data/processed/consolidado_despesas.zip`
- CSV de inconsistências: `data/processed/consolidado_inconsistencias.csv`
- Resumo de inconsistências: `data/processed/inconsistencias_resumo.json`

### Tratamento de inconsistências

Durante a consolidação, o script gera um CSV separado com inconsistências:
- `cnpj_com_razoes_diferentes`: mesmo CNPJ com mais de uma razão social
- `valor_nao_positivo`: valores zerados ou negativos
- `trimestre_corrigido_competencia`: trimestre/ano corrigidos via `competencia_raw`
- `ano_invalido` / `trimestre_invalido`: campos inválidos no input
- `cnpj_ausente` / `razao_social_ausente`: campos ausentes
- `valor_invalido`: valor não numérico

Decisão: **não descarto registros automaticamente**; sinalizo no CSV de
inconsistências para auditoria, mantendo transparência e permitindo decisões
futuras (ex.: excluir ou ajustar somente na etapa de análise).

## Self-annealing / Aprendizado com falhas

Princípio adotado: o projeto fica mais resiliente a cada falha detectada.
O ciclo é explícito e repetível:
1) **Detectar** erro/caso limite
2) **Registrar** (manifest, CSV de inconsistências, logs)
3) **Corrigir/ajustar** a configuração ou a heurística
4) **Repetir** com validação

Onde foi aplicado:
- **1.1**: manifest do download registra arquivos, status e erros, facilitando reexecução.
- **1.2**: `process_manifest.json` registra colunas detectadas e erros por arquivo.
- **1.3**: CSV de inconsistências separa casos suspeitos sem descartar dados.

Isso não é simulated annealing clássico, mas segue a mesma ideia de iterar
com base em falhas para endurecer o pipeline.
