# Roadmap - Teste Intuitive Care

Legenda: [x] feito | [ ] pendente

## 1. Teste de Integracao com API Publica
- [x] 1.1 Acesso a API ANS: download ultimos 3 trimestres
- [x] 1.2 Processamento: extracao, normalizacao e filtro de sinistros
- [x] 1.3 Consolidacao + inconsistencias + ZIP consolidado
- [x] Documentacao (README Teste 1)

## 2. Teste de Transformacao e Validacao
- [x] 2.1 Validacao (CNPJ, valor, razao social) + trade-off documentado
- [x] 2.2 Enriquecimento (join CADOP) + tratamento de falhas documentado
- [x] 2.3 Agregacao (total, media, desvio) + ordenacao + ZIP
- [x] Documentacao (README Teste 2)

## 3. Teste de Banco de Dados e Analise
- [x] 3.1 Preparacao: CSVs gerados e listados
- [x] 3.2 DDLs com PKs/indices + trade-offs documentados
- [x] 3.3 Importacao validada + tratamento de inconsistencias documentado
- [x] 3.4 Queries analiticas + justificativas documentadas
- [x] Executar scripts em MySQL (concluido em 30/01/2026)

## 4. Teste de API e Interface Web
- [x] 4.1 Definir fonte de dados (BD ou CSV)
- [x] 4.2 Backend (Flask/FastAPI) + trade-offs
- [ ] 4.2.1 Framework escolhido e justificado
- [ ] 4.2.2 Paginacao escolhida e justificada
- [ ] 4.2.3 Cache/consulta direta escolhido e justificado
- [ ] 4.2.4 Estrutura de resposta escolhida e justificada
- [ ] 4.3 Frontend Vue + trade-offs
- [ ] 4.3.1 Busca/filtro escolhido e justificado
- [ ] 4.3.2 Gerenciamento de estado escolhido e justificado
- [ ] 4.3.3 Performance da tabela documentada
- [ ] 4.3.4 Erros/loading/dados vazios documentados
- [ ] 4.4 Postman collection + exemplos
- [ ] Documentacao geral no README

## Entrega
- [ ] Gerar ZIP final: Teste_{seu_nome}.zip
- [ ] Push final