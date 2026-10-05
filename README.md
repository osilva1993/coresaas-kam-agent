# 🎯 CoreSaaS KAM Manager — Agentic AI Copilot

![python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square)
![frontend](https://img.shields.io/badge/frontend-Streamlit-red?style=flat-square)
![llm engine](https://img.shields.io/badge/llm_engine-Groq_API-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

> **Agente Autônomo B2B de Retenção & Expansão (Key Account Management)**, projetado para monitorar a saúde de contas SaaS, prevenir risco de churn através de travas determinísticas em Python e gerar diagnósticos estratégicos com aprovação humana (Human-in-the-Loop).

---

## 🌐 Demonstração Online

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://coresaas-kam-agent.streamlit.app)

👉 **[Acessar a Aplicação Online no Streamlit Cloud](https://coresaas-kam-agent.streamlit.app)**

---

## 🔄 Fluxo de Arquitetura & Governança

```mermaid
graph TD
    A[📡 Fontes de Dados Brutos<br/>CRM / Suporte / Telemetria] --> B[🐍 Python Engine Determinístico]
    B --> C{📊 Validação de Health Score<br/>& Trava de Estado}
    
    C -->|Saúde >= 80%| D[🚀 Modo Expansão]
    C -->|Saúde < 80%| E[🚨 Bloqueio de Expansão / Playbook Churn]
    
    D --> F[🤖 Orquestrador de Contexto & Prompt Assembly]
    E --> F
    
    F --> G[🧠 Groq LLM API<br/>gpt-oss-120b]
    G --> H[🖥️ Streamlit Cockpit<br/>Human-in-the-Loop]
    H -->|Aprovado pelo KAM| I[💾 Persistência & Ação no CRM]


## 📌 Visão Geral do Projeto

O **CoreSaaS KAM Agent** é um agente autônomo e modular projetado para automatizar a inteligência operacional, retenção de receita (Gross Retention) e expansão de carteira (Expansion/Upsell) em empresas **B2B SaaS Enterprise**.

Em ambientes B2B SaaS de alto ticket, **LLMs tradicionais alucinam ou tomam decisões imprecisas quando expostas a cálculos matemáticos ou regras de negócio complexas**. O agente resolve esse problema ao implementar uma **Arquitetura Desacoplada**:

1. **Motores Determinísticos em Python (`engine/`):** Isolam 100% dos cálculos matemáticos, matrizes de risco, notas de saúde e validação rígida de estados (Hard-Lock).
2. **Conectores Abstratos (`connectors/`):** Padronizam a ingestão de dados de múltiplos pontos de contato (CRM, SupportDesk, Telemetria e Inteligência de Mercado).
3. **Orquestrador de Contexto (`agent_orchestrator.py`):** Monta prompts dinâmicos injetando o diagnóstico Python e os prompts de habilidades (`skills/`).
4. **LLM de Alta Performance (Groq / `openai/gpt-oss-120b`):** Atua **estritamente como interpretadora e geradora de comunicação humana**, proibida de realizar cálculos ou alterar estados autonomamente.
5. **Governança Human-in-the-Loop (`app.py`):** Interface interativa em Streamlit onde o KAM revisa, edita e aprova as ações recomendadas antes da persistência no CRM.

## 🎯 Arquitetura do Agente & Engenharia de IA

Plaintext

```
                              [ DADOS BRUTOS ]
                 ┌───────────────────┼───────────────────┐
                 ▼                   ▼                   ▼
          ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
          │   B2B CRM   │     │ SupportDesk │     │ Telemetria  │
          └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
                 │                   │                   │
                 └───────────────────┼───────────────────┘
                                     ▼
                      ┌─────────────────────────────┐
                      │  engine/health_score.py     │ ◄── Cálculo Ponderado
                      └──────────────┬──────────────┘
                                     ▼
                      ┌─────────────────────────────┐
                      │  engine/state_machine.py    │ ◄── Hard-Lock Validation
                      └──────────────┬──────────────┘
                                     ▼
                      ┌─────────────────────────────┐
                      │    agent_orchestrator.py    │ ◄── Injeção de Skill (.md)
                      └──────────────┬──────────────┘
                                     ▼
                      ┌─────────────────────────────┐
                      │   Groq API (GPT-OSS-120B)   │ ◄── Raciocínio & Redação
                      └──────────────┬──────────────┘
                                     ▼
                      ┌─────────────────────────────┐
                      │  Streamlit UI (HITL Review) │ ◄── Aprovação Humana
                      └──────────────┬──────────────┘
                                     ▼
                      ┌─────────────────────────────┐
                      │  Streamlit Community Cloud  │ ◄── Public Host/Domain
                      └─────────────────────────────┘

```

### 🔑 Diferenciais de Engenharia de IA Aplicados

- **Strict Data Provenance Tagging:** A LLM é forçada a etiquetar cada declaração gerada:
  - `[VALIDADO]`: Informação factual confirmada diretamente pelos conectores de dados.
  - `[HIPÓTESE]`: Sugestões estratégicas, hipóteses de ação e minutas geradas pela IA.
  - `[NÃO DITO]`: Identificação explícita de ausência de dados na base.
- **Hard-Lock State Machine:** Impossibilita transições de fase inválidas no CRM. Exemplo: Se o *Health Score* for $< 80.0$ ou houver *Bugs Críticos abertos*, o sistema **bloqueia programaticamente** a entrada no modo de Expansão ($E1$) e redireciona para Mitigação de Churn ($O3$).
- **Prompt Assembly baseada em Skills:** Injeção modular de instruções especializadas contidas em arquivos `.md` na pasta `skills/` conforme a necessidade da conta (Ex: `kam-churn-risk.md`, `kam-expansion-mapping.md`, `kam-market-signals.md`).

## 🧠 Domínio de Negócio: Top Performance KAM & CS Framework

O projeto incorpora os frameworks mais avançados de **Customer Success e Key Account Management para B2B SaaS**:

### 1. Algoritmo de Health Score Ponderado Proporcional

O cálculo de saúde da conta é executado em código Python e repondera dinamicamente a nota caso algum pilar esteja ausente:

$$\text{Health Score} = \frac{\sum (\text{Score}\_i \times \text{Peso}\_i)}{\sum \text{Peso}\_i}$$

- **Pilar Telemetria de Uso (35%):** Taxa de adoção de features e variação mensal de usuários ativos (MAU Trend).
- **Pilar Atrito & Suporte (25%):** Penalidades severas por bugs críticos em aberto, chamados acumulados e violações de SLA.
- **Pilar Relacionamento CRM (20%):** Dias desde o último contato e presença de *Executive Sponsor* ativo.
- **Pilar Financeiro (20%):** Adimplência contratual e proximidade da janela de renovação sem tratativa.

### 2. Ciclo de Vida da Conta e Matriz de Estágios

- **MODO SETUP ($S1 \rightarrow S4$):** Onboarding técnico, saneamento cadastral e definição da linha de base de saúde.
- **MODO OPERAÇÃO ($O1 \rightarrow O4$):** Acompanhamento de rotina ($O1$), cadência de valor ($O2$), gestão prioritária de Risco de Churn ($O3$) e renovação contratual ($O4$).
- **MODO EXPANSÃO ($E1 \rightarrow E4$):** Mapeamento de oportunidades de Upsell/Cross-sell ($E1$), qualificação de valor ($E2$), negociação ($E3$) e fechamento ($E4$).

### 3. Monitoramento de Sinais de Mercado (Market Signals)

Acompanhamento ativo de eventos externos que impactam a retenção ou indicam gatilhos de expansão:

- **Gatilhos de Expansão:** Rodadas de investimento, expansão de filiais, lançamento de novos produtos.
- **Riscos Relacionais:** Mudança de executivos (C-Level/VPs), fusões e aquisições (M&A) ou entrada de concorrentes.

## 🛠️ Tecnologias Utilizadas

- **Linguagem Principal:** Python 3.10+
- **Interface Gráfica & UX:** Streamlit (Vibecode Pattern para cockpits de governança)
- **Provedor de Inferência de LLM:** Groq API (Modelo: `openai/gpt-oss-120b`)
- **Hospedagem & Nuvem:** Streamlit Community Cloud (Domínio Público Gratuito)
- **Gerenciamento de Segredos:** `python-dotenv` (Local) / `streamlit.secrets` (Nuvem)
- **Arquitetura de Código:** Modular, Orientada a Objetos e Desacoplada.

## 📂 Estrutura do Repositório

Plaintext

```
meu-projeto-kam/
├── .env                          # Variáveis de ambiente locais (Ignorado no Git)
├── .gitignore                    # Regras de exclusão do repositório
├── README.md                     # Documentação executiva e técnica do projeto
├── requirements.txt              # Dependências para deploy no Streamlit Cloud
├── app.py                        # Dashboard Streamlit (Interface Human-in-the-Loop)
├── agent_orchestrator.py         # Orquestrador de Contexto e Montagem de Prompts
├── llm_client.py                 # Cliente de integração com a API da Groq
├── main_test.py                  # Script de validação e testes dos fluxos em CLI
├── .streamlit/
│   └── secrets.toml              # Configuração de segredos no ambiente do Streamlit Cloud
├── connectors/                   # Camada de abstração e ingestão de dados
│   ├── __init__.py
│   ├── crm_connector.py          # Dados do CRM (MRR, Estágio, Contratos)
│   ├── support_connector.py      # Dados de Tickets, SLA e Bugs Críticos
│   ├── telemetry_connector.py    # Dados de Adoção de Produto e MAU
│   └── market_intelligence_connector.py # Captação de Sinais de Mercado e Notícias
├── engine/                       # Motores de validação determinística em Python
│   ├── __init__.py
│   ├── health_score.py           # Algoritmo de cálculo ponderado de saúde
│   └── state_machine.py          # Trava rígida de transições de estágio (Hard-Lock)
├── instructions/
│   └── core_kam_instruction.md   # Prompt mestre de comportamento do Agente
└── skills/                       # Instruções operacionais modularizadas (.md)
    ├── kam-churn-risk.md         # Playbook de contenção e mitigação de churn
    ├── kam-expansion-mapping.md  # Playbook de mapeamento de expansão
    └── kam-market-signals.md     # Análise de movimentações de mercado

```

## 🚀 Como Executar Localmente ou Publicar no Streamlit Cloud

### Opção A: Execução Local

1. **Clone o repositório:**

   Bash
   ```
   git clone https://github.com/seu-usuario/meu-projeto-kam.git
   cd meu-projeto-kam

   ```
2. **Instale as dependências:**

   Bash
   ```
   pip install -r requirements.txt

   ```
3. **Configure as Variáveis de Ambiente:**

   Crie um arquivo `.env` na raiz do projeto contendo sua chave da Groq:

   Snippet de código
   ```
   GROQ_API_KEY=gsk_sua_chave_aqui

   ```
4. **Inicie o Dashboard:**

   Bash
   ```
   python -m streamlit run app.py

   ```

### Opção B: Publicação em Domínio Público (Streamlit Community Cloud)

Para disponibilizar o projeto online para recrutadores e gestores técnicos:

1. Suba o código para um repositório no **GitHub**.
2. Acesse [**share.streamlit.io**](https://share.streamlit.io/) e faça login com sua conta do GitHub.
3. Clique em **"New App"**, selecione o repositório, a branch `main` e defina o arquivo principal como `app.py`.
4. Em **"Advanced Settings" -> "Secrets"**, cadastre a chave da API da Groq:

   Ini, TOML
   ```
   GROQ_API_KEY = "gsk_sua_chave_aqui"

   ```
5. Clique em **"Deploy!"**. O aplicativo gerará um domínio público acessível de qualquer dispositivo.

## 📄 Licença

Este projeto é disponibilizado sob a licença [MIT](https://www.google.com/search?q=LICENSE) — livre para estudos, demonstrações de portfólio e adaptações arquiteturais.