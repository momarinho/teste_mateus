# Teste Intuitive Care - Projeto

Este repositorio cobre as fases **1** e **2** do teste.

Para detalhes completos, consulte:
- `teste_api_ans/README.md` (Teste 1: download, processamento e consolidacao)
- `teste_transformacao_validacao/README.md` (Teste 2: validacao, enriquecimento e agregacao)

## Execucao rapida (resumo)

### Teste 1
```bash
python teste_api_ans/download_ans_demos.py
python teste_api_ans/process_ans_files.py
python teste_api_ans/consolidate_ans_expenses.py
```

### Teste 2
```bash
python teste_transformacao_validacao/run_transformation.py
```

## Observacoes
- Os ZIPs gerados nas etapas intermediarias nao precisam ser versionados.
- O ZIP final do projeto (entrega) sera gerado ao final do teste.
