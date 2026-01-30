# Teste 4: API e Interface Web

Este diretório contém a Fase 4 do projeto: **Desenvolvimento da API e Frontend**.

## Estrutura

- `backend/`: Código Python (FastAPI/Flask) para servir os dados e realizar cálculos.
- `frontend/`: Código Vue.js para visualizar os dados.

## Configuração do Backend (4.1)

1. Crie um ambiente virtual e instale as dependências:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

2. Configure o banco de dados:
   - Copie o arquivo `.env.example` para `.env` (se existir) ou crie um novo `.env`.
   - Edite as variáveis `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`.

3. Verifique a conexão com o banco de dados:
   ```bash
   python check_setup.py
   ```
   
   Se a conexão falhar, verifique `DB_PASSWORD`.
   Caso prefira usar CSVs em vez do Banco de Dados, defina `USE_CSV=True` no `.env`.

## Trade-offs Técnicos - Backend

### 4.2.1 Escolha do Framework: **FastAPI** (Opção B)

**Justificativa:**
Optei pelo **FastAPI** em detrimento do Flask, considerando os seguintes pontos:

1.  **Performance e Assincronismo:**
    - O FastAPI é construído sobre Starlette (ASGI) e Pydantic, oferecendo performance significativamente superior ao Flask (WSGI) para operações de I/O, como consultas a banco de dados.
    - O suporte nativo a `async/await` permite lidar com múltiplas requisições concorrentes de forma eficiente, crucial para APIs que consomem dados de BD ou arquivos.

2.  **Validação de Dados e Tipagem:**
    - O uso do **Pydantic** garante validação automática de dados de entrada e saída baseada em *type hints* do Python. Isso reduz drasticamente a necessidade de código manual de validação e tratamento de erros (boilerplate).
    - Torna o código mais robusto e "self-documenting".

3.  **Documentação Automática:**
    - Gera automaticamente documentação interativa (Swagger UI e ReDoc) sem configuração extra. Isso facilita o teste das rotas e a comunicação com o Frontend (Vue.js), agilizando o desenvolvimento da Fase 4.3.

4.  **Facilidade de Manutenção:**
    - A estrutura modular (Routers, Schemas, Services) incentivada pelo FastAPI, aliada à injeção de dependências, facilita a manutenção e escalabilidade do projeto em comparação a um setup Flask básico que exigiria mais decisões de arquitetura e bibliotecas de terceiros (como Flask-RESTful ou Marshmallow).

### 4.2.2 Estratégia de Paginação: **Offset-based** (Opção A)

**Justificativa:**
Para a rota `/api/operadoras`, adotei a paginação baseada em **offset** (`page` e `limit`).

1.  **Simplicidade de Implementação e Uso:**
    - É a abordagem mais intuitiva e fácil de implementar tanto no backend (usando `OFFSET` e `LIMIT` em SQL) quanto no frontend (calculando o número da página).
    - Permite que o usuário navegue diretamente para uma página específica (ex: "ir para a página 5"), o que é um requisito comum em interfaces de usuário.

2.  **Adequado ao Volume de Dados:**
    - O volume de dados de operadoras da ANS (milhares) é perfeitamente gerenciável por esta abordagem. Problemas de performance com `OFFSET` geralmente ocorrem apenas com milhões de registros e páginas muito distantes, o que não é o cenário aqui.
    - O custo de uma consulta a mais para obter a contagem total (`COUNT(*)`) é aceitável e permite exibir o número total de páginas no frontend.

3.  **Trade-offs vs. Cursor/Keyset:**
    - **Cursor/Keyset** é mais performático para datasets gigantes e que mudam com frequência, pois evita o `OFFSET`. No entanto, ele não permite pular para páginas arbitrárias e é mais complexo de implementar.
    - Dado que a lista de operadoras não muda em tempo real, o pequeno risco de inconsistência (um item novo mover resultados entre páginas) é mínimo e não justifica a complexidade extra de um cursor para este caso de uso.

### 4.2.3 Cache vs. Queries Diretas: **Cache na Aplicação** (Opção B)

**Justificativa:**
Para a rota `/api/estatisticas`, que envolve cálculos agregados (somas, médias) sobre um grande volume de dados, a estratégia escolhida foi **cachear os resultados na memória da aplicação por um tempo determinado**.

1.  **Frequência de Atualização dos Dados:**
    - Os dados-fonte (demonstrações contábeis) são atualizados trimestralmente pela ANS. Não há necessidade de calcular estatísticas em tempo real (Opção A) para cada requisição, pois isso geraria uma carga desnecessária no banco de dados para obter um resultado que não muda.

2.  **Performance e Experiência do Usuário:**
    - O primeiro cálculo pode ser lento. Armazenar o resultado em cache faz com que todas as requisições subsequentes sejam praticamente instantâneas, melhorando drasticamente a performance da API e a experiência do usuário no frontend.

3.  **Simplicidade vs. Pré-cálculo:**
    - A Opção C (pré-calcular em uma tabela) oferece a melhor performance, mas adiciona uma complexidade significativa ao sistema (necessidade de jobs agendados, triggers no banco, etc.).
    - Um cache simples em memória (Opção B) atinge um balanço ideal: oferece ótima performance para a grande maioria das chamadas com uma implementação muito mais simples, adequada à escala deste projeto. A consistência dos dados é garantida por um TTL (Time-To-Live) de várias horas, mais do que suficiente para este cenário.

---

## Próximos Passos (Roadmap)

- [x] 4.1 Preparação de dados (Conexão validada)
- [x] 4.2 Setup do Servidor (FastAPI)
- [x] 4.2.1 Framework escolhido e justificado
- [x] 4.2.2 Paginação escolhida e justificada
- [x] 4.2.3 Cache/consulta direta escolhido e justificado
- [ ] 4.2.4 Estrutura de resposta escolhida e justificada
- [ ] 4.3 Setup do Frontend (Vue.js)
