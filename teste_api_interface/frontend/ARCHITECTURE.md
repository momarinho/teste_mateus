# Arquitetura e Decisões Técnicas (Frontend & API)

Este documento detalha as decisões técnicas tomadas para o desenvolvimento da interface Vue.js e da API de suporte, respondendo aos pontos levantados no roadmap (item 4.3).

## 4.3.1 Estratégia de Busca/Filtro
**Escolha:** Opção A (Busca no Servidor)  
**Justificativa:**
Embora a busca no cliente (Client-side) seja extremamente rápida para pequenos volumes de dados, o dataset de operadoras e despesas pode escalar. Carregar todos os dados (milhares de registros) para o navegador do usuário consumiria muita memória e causaria um "load time" inicial alto.
A busca no servidor (Server-side) foi implementada na API (`GET /api/operadoras/?search=...`), permitindo que o backend (SQL ou Pandas/CSV) filtre os dados e retorne apenas a página relevante. Isso garante escalabilidade e menor uso de dados móveis/banda para o cliente.

## 4.3.2 Gerenciamento de Estado
**Escolha:** Opção B (Pinia)  
**Justificativa:**
Utilizamos o **Pinia** (padrão oficial para Vue 3) em vez de simples Props/Events ou Vuex.
*   **Complexidade:** A aplicação possui estados que precisam ser compartilhados entre visualizações distintas (ex: lista de operadoras na Home e detalhes na View de Detalhes, embora recarreguemos para garantir frescor, o estado de paginação e filtros poderia ser persistido).
*   **Manutenibilidade:** Centralizar a lógica de API (Actions) e o estado (State) no Store (`operadoraStore.js`) limpa os componentes Vue, deixando-os focados apenas em apresentação (`UI`).
*   **Modernidade:** Pinia oferece melhor suporte a TypeScript (se adotado futuramente) e uma API mais simples que o Vuex.

## 4.3.3 Performance da Tabela
**Estratégia:** Paginação Server-Side  
**Justificativa:**
Para exibir "muitas operadoras", renderizar milhares de linhas no DOM travamos o navegador (mesmo com Virtual DOM).
*   Implementamos paginação (padrão 10 itens por página) na API e no Frontend.
*   Isso mantém a performance da UI constante (O(1) em relação ao total de dados) e reduz o payload da rede.
*   Alternativas como "Virtual Scrolling" adicionam complexidade (altura dinâmica de linhas) que não foi julgada necessária dado o requisito de uma tabela paginada explícita.

## 4.3.4 Tratamento de Erros e Loading
**Implementação:**
*   **Loading:** Estados booleanos (`loading`, `loadingChart`) no Store e Componentes controlam a exibição de "spinners" (loaders CSS). Isso fornece feedback visual imediato ao usuário durante requisições assíncronas.
*   **Erros:**
    *   **API:** O backend retorna códigos HTTP apropriados (404 para não encontrado, 500 para erro interno).
    *   **Frontend:** O Store captura exceções (`try/catch`) e preenche uma variável de estado `error`. A UI exibe mensagens amigáveis ("Erro ao buscar operadoras") em vez de stack traces.
    *   **Dados Vazios:** Componentes de tabela e gráfico possuem verificações (`v-if="operadoras.length === 0"`) para exibir "Nenhum dado encontrado", evitando tabelas vazias confusas.

## Detalhes Adicionais
*   **Tech Stack:** Vue 3 (Composition API), Vite, Pinia, Vue Router, Axel (HTTP Client), Chart.js (Visualização).
*   **Design:** CSS customizado com variáveis (Dark/Light theme ready) focando em estética "Clean/Premium" (Inter font, sombras suaves, cores consistentes).
