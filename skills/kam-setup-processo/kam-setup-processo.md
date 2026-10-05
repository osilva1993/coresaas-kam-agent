# 🛠️️ Skill: kam-setup-processo — Estruturação & Saneamento de Contas

> **Versão:** 2.0 Enterprise Full Specification  
> **Aplica-se a:** Subestados **S1, S2, S3 e S4** (Modo SETUP)  
> **Objetivo:** Estruturar a conta recém-integrada ou não mapeada, auditando os campos obrigatórios do CRM, definindo rituais de governança, identificando stakeholders críticos e estabelecendo o Baseline de Saúde inicial.  
> **Camada de Integração:** B2B CRM Engine (Leitura/Escrita de Atributos) + engine/state_machine.py (Validação de Transição) + engine/health_score.py (Cálculo do Baseline Inicial).

---

## 1. Gatilhos de Ativação

Esta skill é acionada automaticamente pelo orquestrador ou pelo usuário quando:
1. Uma nova conta entra no pipeline "Carteira / Account Management" do B2B CRM Engine sem histórico prévio de acompanhamento.
2. A conta apresenta lacunas de cadastro crítico (mínimo de 1 campo obrigatório não preenchido).
3. O comando do usuário solicitar auditoria de cadastro, revisão de governança ou inicialização de baseline (ex: *"Sanear conta X"*, *"Iniciar setup da empresa Y"*).

---

## 2. Sequenciamento Rígido de Execução (Subestados S1 a S4)

O agente deve validar a evolução da conta em ordem cronológica estrita. Não é permitido saltar subestados sem preenchimento dos pré-requisitos anteriores.

```text
┌─────────────────────────┐     ┌─────────────────────────┐
│ S1: Validação de Posse  │ ──► │ S2: Cadastro Mestre     │
│ - Dono da Conta (KAM)   │     │ - Dados Financeiros     │
│ - Contrato Ativo        │     │ - Stakeholders-Chave    │
└─────────────────────────┘     └─────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│ S4: Baseline de Saúde   │ ◄── │ S3: Rituais Governança  │
│ - Registro no CRM       │     │ - Frequência de Matriz  │
│ - Liberação para OPERAÇÃO│    │ - Canais Oficiais       │
└─────────────────────────┘     └─────────────────────────┘