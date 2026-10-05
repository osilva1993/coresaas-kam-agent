# 🛡️ CoreSaaS KAM Agent — Agentic AI Copilot

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit UI](https://img.shields.io/badge/frontend-Streamlit-red.svg)](https://streamlit.io/)
[![Groq LPU](https://img.shields.io/badge/llm_engine-Groq_API-flash.svg)](https://groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Agente Autônomo B2B de Retenção e Expansão (Key Account Management)**, projetado para monitorar a saúde de contas SaaS, prevenir risco de churn através de travas determinísticas em Python e gerar diagnósticos estratégicos com aprovação humana (Human-in-the-Loop).

Link: https://coresaas-kam-agent.streamlit.app/

---

## 💡 O Desafio B2B & A Solução Agêntica

* **O Gargalo na Gestão de Contas:** Gestores de Contas (KAMs) e CSMs perdem horas cruzando manualmente dados dispersos de CRM, tickets de suporte, telemetria de uso e notícias de mercado. Quando utilizam LLMs puras, correm o risco de **alucinações em cálculos de saúde** ou **recomendações incoerentes de expansão** para contas com problemas técnicos críticos.
* **A Solução Agêntica Governada:** O **CoreSaaS KAM Agent** aplica uma arquitetura desacoplada. Um motor determinístico em Python isola os cálculos matemáticos e aplica **travas rígidas de transição de fase no CRM** (Hard-Lock). Em seguida, a LLM atua estritamente na síntese do contexto e na redação do diagnóstico, garantindo governança total e validação pelo KAM antes de registrar qualquer ação.

---

## 🧠 Biblioteca de Skills & Playbooks de Governança

O agente utiliza uma **arquitetura de habilidades desacopladas** em Markdown (`skills/`). Cada módulo funciona como um especialista que orienta o orquestrador na condução de planos de ação específicos:

| Skill / Módulo | Função Prática na Conta | Impacto na Retenção e Expansão |
| :--- | :--- | :--- |
| 🚨 **Churn Risk Playbook** | Mapeia indicadores de atrito (SLA violado, bugs críticos abertos, queda de MAU e perda de sponsor). | Bloqueia ofertas indevidas, gera plano de mitigação emergencial e alerta o KAM. |
| 📈 **Expansion Mapping** | Qualifica a conta para Upsell/Cross-sell identificando engajamento alto e adimplência financeira. | Garante abordagens comerciais apenas quando a conta está 100% saudável. |
| 🌐 **Market Signals Radar** | Monitora eventos externos (mudanças de C-Level/VP, fusões, aquisições e novas rodadas). | Converte movimentações do mercado em ganchos de reaproximação estratégica. |
| ⚙️ **Health Score Engine** | Aplica algoritmo determinístico ponderado (Telemetria, Suporte, CRM e Financeiro). | Padroniza a métrica de saúde real da conta, eliminando avaliações subjetivas. |
| 🔒 **State Machine Hard-Lock** | Valida as regras de transição de estágio do CRM em código Python puro. | Impede transições de estágio inválidas e garante governança operacional. |

---

## 🏗️ Arquitetura do Sistema & Fluxo de Dados

O fluxo utiliza motores determinísticos de validação antes de invocar a LLM, garantindo a proveniência dos dados (`[VALIDADO]`, `[HIPÓTESE]`, `[NÃO DITO]`) e revisão pelo KAM (Human-in-the-Loop).

```mermaid
graph TD
    A[📡 Connectors: CRM / Support / Telemetry / Market] -->|Injeção de Dados Brutos| B[🐍 Python Deterministic Engine]
    
    B --> C{⚙️ Health Score & State Machine}
    C -->|Saúde < 80 ou Bug Crítico| D[🔒 HARD-LOCK: Bloqueio de Expansão / Playbook Churn]
    C -->|Saúde >= 80 & Adimplente| E[🚀 AUTORIZADO: Mapeamento de Expansão]
    
    D --> F[🤖 Context Orchestrator & Skill Ingestion]
    E --> F
    
    F -->|Prompt Estruturado| G[🧠 Groq API / gpt-oss-120b]
    G -->|Síntese e Minuta de Ação| H[🖥️ Streamlit HITL Dashboard]
    H -->|Revisão e Aprovação do KAM| I[💾 Persistência de Notas & Estágio no CRM]