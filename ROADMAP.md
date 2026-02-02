# Roadmap - Teste Intuitive Care

Legenda: [x] feito | [ ] pendente

## 1. Teste de Integracao com API Publica
- [x] 1.1 Acesso a API ANS: download ultimos 3 trimestres
- [x] 1.2 Processamento: extracao, normalizacao e filtro de sinistros
- [x] 1.3 Consolidacao + inconsistencias + ZIP consolidado
- [x] Documentacao (README Teste 1)
- [x] Gerar artefatos locais (data/processed/consolidado_despesas.csv e consolidado_despesas.zip)

## 2. Teste de Transformacao e Validacao
- [x] 2.1 Validacao (CNPJ, valor, razao social) + trade-off documentado
- [x] 2.2 Enriquecimento (join CADOP) + tratamento de falhas documentado
- [x] 2.3 Agregacao (total, media, desvio) + ordenacao + ZIP
- [x] Documentacao (README Teste 2)
- [x] Gerar artefatos locais (despesas_agregadas.csv e Teste_{seu_nome}.zip)

## 3. Teste de Banco de Dados e Analise
- [x] 3.1 Preparacao: CSVs gerados e listados
- [x] 3.2 DDLs com PKs/indices + trade-offs documentados
- [x] 3.3 Importacao validada + tratamento de inconsistencias documentado
- [x] 3.4 Queries analiticas + justificativas documentadas
- [x] Executar scripts em MySQL (concluido em 30/01/2026)

## 4. Teste de API e Interface Web
- [x] 4.1 Definir fonte de dados (BD ou CSV)
- [x] 4.2 Backend (Flask/FastAPI) + trade-offs
- [x] 4.2.1 Framework escolhido e justificado
- [x] 4.2.2 Paginacao escolhida e justificada (Paginação Limit/Offset)
- [x] 4.2.3 Cache/consulta direta escolhido e justificado (Cache simples em memória para CSV)
- [x] 4.2.4 Estrutura de resposta escolhida e justificada (JSON Padronizado: data, meta)
- [x] 4.3 Frontend Vue + trade-offs (Ver `frontend/ARCHITECTURE.md`)
- [x] 4.3.1 Busca/filtro escolhido e justificado (Server-side)
- [x] 4.3.2 Gerenciamento de estado escolhido e justificado (Pinia)
- [x] 4.3.3 Performance da tabela documentada (Paginação)
- [x] 4.3.4 Erros/loading/dados vazios documentados
- [x] 4.4 Postman collection + exemplos (`teste_api_interface/postman_collection.json`)
- [x] Documentacao geral no README
- [ ] Ajustar rotas conforme enunciado: GET /api/estatisticas e GET /api/operadoras/{cnpj}/despesas
- [ ] Atualizar Postman para refletir as rotas exigidas
- [ ] Garantir compatibilidade do modo CSV (mapear colunas CNPJ/RazaoSocial/UF)

## Entrega
- [ ] Gerar ZIP final: Teste_{seu_nome}.zip
- [ ] Push final

## 5. Diferenciais (Não Obrigatórios)
- [x] **Preocupação com performance**: Índices no BD, paginação no front/back, processamento incremental.
- [x] **Arquitetura bem planejada**: Separação de responsabilidades (Service layer, Routers, Store, Components).
- [x] **Uso adequado de versionamento (Git)**: Repositório estruturado.
- [x] **Implementação de testes adicionais**: (Sugestão: Testes unitários com Pytest para o Backend).
- [ ] **Aplicação de recursos de nuvem**: (Opcional: Dockerfile ou Deploy em Vercel/Render).
