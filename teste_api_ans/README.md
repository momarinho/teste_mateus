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

- As etapas 1.2 e 1.3 ainda não foram implementadas.
- Quando chegarmos nelas, este README será atualizado com instruções completas
  de execução e documentação das decisões técnicas.
