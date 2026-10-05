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


📌 Visão Geral do Projeto

Em ambientes B2B SaaS de alto ticket, LLMs tradicionais alucinam ou tomam decisões imprecisas quando expostas a cálculos matemáticos ou regras de negócio complexas. O CoreSaaS KAM Agent resolve esse problema ao implementar uma Arquitetura Desacoplada:Motores Determinísticos em Python (engine/): Isolam 100% dos cálculos matemáticos, matrizes de risco, notas de saúde e validação rígida de estados (Hard-Lock).Conectores Abstratos (connectors/): Padronizam a ingestão de dados de múltiplos pontos de contato (CRM, SupportDesk, Telemetria e Inteligência de Mercado).Orquestrador de Contexto (agent_orchestrator.py): Monta prompts dinâmicos injetando o diagnóstico Python e os prompts de habilidades (skills/).LLM de Alta Performance (Groq / openai/gpt-oss-120b): Atua estritamente como interpretadora e geradora de comunicação humana, proibida de realizar cálculos ou alterar estados autonomamente.Governança Human-in-the-Loop (app.py): Interface interativa em Streamlit onde o KAM revisa, edita e aprova as ações recomendadas antes da persistência no CRM.🔑 Diferenciais de Engenharia de IAStrict Data Provenance Tagging: A LLM é forçada a etiquetar cada declaração gerada:[VALIDADO]: Informação factual confirmada diretamente pelos conectores de dados.[HIPÓTESE]: Sugestões estratégicas, hipóteses de ação e minutas geradas pela IA.[NÃO DITO]: Identificação explícita de ausência de dados na base.Hard-Lock State Machine: Impossibilita transições de fase inválidas no CRM. Exemplo: Se o Health Score for $< 80.0$ ou houver Bugs Críticos abertos, o sistema bloqueia programaticamente a entrada no modo de Expansão ($E1$) e redireciona para Mitigação de Churn ($O3$).Prompt Assembly baseada em Skills: Injeção modular de instruções especializadas contidas em arquivos .md na pasta skills/ conforme a necessidade da conta (kam-churn-risk.md, kam-expansion-mapping.md, kam-market-signals.md).🧠 Domínio de Negócio: Top Performance KAM & CS FrameworkO projeto incorpora os frameworks mais avançados de Customer Success e Key Account Management para B2B SaaS:1. Algoritmo de Health Score Ponderado ProporcionalO cálculo de saúde da conta é executado em código Python e repondera dinamicamente a nota caso algum pilar esteja ausente:$$\text{Health Score} = \frac{\sum (\text{Score}_i \times \text{Peso}_i)}{\sum \text{Peso}_i}$$Pilar Telemetria de Uso (35%): Taxa de adoção de features e variação mensal de usuários ativos (MAU Trend).Pilar Atrito & Suporte (25%): Penalidades severas por bugs críticos em aberto, chamados acumulados e violações de SLA.Pilar Relacionamento CRM (20%): Dias desde o último contato e presença de Executive Sponsor ativo.Pilar Financeiro (20%): Adimplência contratual e proximidade da janela de renovação sem tratativa.2. Ciclo de Vida da Conta e Matriz de EstágiosMODO SETUP ($S1 \rightarrow S4$): Onboarding técnico, saneamento cadastral e definição da linha de base de saúde.MODO OPERAÇÃO ($O1 \rightarrow O4$): Acompanhamento de rotina ($O1$), cadência de valor ($O2$), gestão prioritária de Risco de Churn ($O3$) e renovação contratual ($O4$).MODO EXPANSÃO ($E1 \rightarrow E4$): Mapeamento de oportunidades de Upsell/Cross-sell ($E1$), qualificação de valor ($E2$), negociação ($E3$) e fechamento ($E4$).🛠️ Tecnologias UtilizadasLinguagem Principal: Python 3.10+Interface Gráfica & UX: Streamlit (Vibecode Pattern para cockpits de governança)Provedor de Inferência de LLM: Groq API (Modelo: openai/gpt-oss-120b)Hospedagem & Nuvem: Streamlit Community CloudGerenciamento de Segredos: python-dotenv (Local) / streamlit.secrets (Nuvem)📂 Estrutura do RepositórioPlaintextmeu-projeto-kam/
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
├── engine/                       # Motores de validação determinística em Python
├── instructions/                 # Prompt mestre do comportamento do Agente
└── skills/                       # Instruções operacionais modularizadas (.md)
🚀 Como Executar LocalmenteClone o repositório:Bashgit clone [https://github.com/osilva1993/coresaas-kam-agent.git](https://github.com/osilva1993/coresaas-kam-agent.git)
cd coresaas-kam-agent
Instale as dependências:Bashpip install -r requirements.txt
Configure as Variáveis de Ambiente:Crie o arquivo .env na raiz do projeto:Snippet de códigoGROQ_API_KEY=gsk_sua_chave_aqui
Inicie o Dashboard:Bashpython -m streamlit run app.py
📄 LicençaEste projeto é disponibilizado sob a licença MIT — livre para estudos e demonstrações de portfólio.