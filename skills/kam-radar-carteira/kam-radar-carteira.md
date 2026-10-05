# 📊 Skill: kam-radar-carteira — Diagnóstico, Saúde & Radar da Carteira

> **Versão:** 2.0 Enterprise Full Specification  
> **Aplica-se a:** Subestados **O1** (Radar Quinzenal da Carteira) e **O4** (Review de Carteira) — Modo OPERAÇÃO  
> **Objetivo:** Mapear continuadamente a saúde física, operacional e relacional de cada conta da carteira, consumindo o cálculo determinístico do Health Score, identificando sinais precoces de atrito e gerando o Radar de Riscos/Oportunidades.  
> **Camada de Integração:** B2B CRM Engine (Leitura de Atividades/Notas e Registros) + SupportDesk Engine (Leitura de Tickets/Bugs) + SaaS Telemetry API (Dados de Adoção) + engine/health_score.py (Cálculo de Nota).

---

## 1. Gatilhos de Ativação

Esta skill é acionada pelo orquestrador ou pelo usuário quando:
1. Ocorre o ciclo quinzenal/mensal de varredura automatizada da carteira B2B no **MODO OPERAÇÃO (Subestado O1)**.
2. O usuário solicita um diagnóstico imediato, briefing de saúde ou radar de riscos de uma conta específica (ex: *"Gerar radar da empresa X"*, *"Como está a saúde da conta Y?"*).
3. É acionada a rotina de preparação para a reunião executiva de alinhamento interno (**Subestado O4 - Review de Carteira**).

---

## 2. Sequenciamento de Execução e Integrações

Para consolidar o Radar sem alucinações matemáticas ou omissão de fontes, o agente deve seguir rigorosamente a sequência de 5 passos:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ PASSO 1: Coleta de Dados via Conectores (CRM + SupportDesk + Telemetry)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PASSO 2: Execução do Calculador Python (engine/health_score.py)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PASSO 3: Mapeamento de Sinais de Alerta e Análise de Causa-Raiz        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PASSO 4: Validação de Idempotência (Checagem de tags [Radar · auto])   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PASSO 5: Geração de Saídas (UI Dashboard + Nota POST /notes no CRM)    │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1. Detalhamento dos Passos:

* **Passo 1 — Coleta Unificada:** O agente lê as estruturas JSON do cliente vindas do B2B CRM Engine, do SupportDesk Engine e da SaaS Telemetry API.
* **Passo 2 — Processamento da Saúde:** O agente envia os dados brutos para o módulo `engine/health_score.py`, que devolve o número consolidado (0 a 100), a cor da faixa (**Verde**, **Amarelo**, **Vermelho**) e a discriminação dos 4 pilares.
* **Passo 3 — Mapeamento de Riscos:** O agente identifica os fatores causadores da queda de pontuação (ex: bugs no Helpdesk, queda de logins ou falta de contato com Sponsor).
* **Passo 4 — Checagem de Duplicidade (Idempotência):** O agente pesquisa no CRM por notas já registradas na mesma data com o título `[Radar · auto]`. Se já existir uma nota no mesmo dia, o agente atualiza o registro ou alerta a duplicidade na UI.
* **Passo 5 — Emissão de Resultados:** O agente formata os relatórios visuais e prepara o payload de escrita para o CRM.

---

## 3. Matriz de Leitura dos Pilares do Health Score

 O agente não calcula notas, mas deve interpretar a decomposição fornecida pelo `engine/health_score.py`:

| Pilar | Fonte Integrada | Métrica Mapeada | Indicador Crítico (Alerta) |
| :--- | :--- | :--- | :--- |
| **Uso & Engajamento** (35%) | SaaS Telemetry API | Variacao de MAU (Usuários Ativos), Frequência de Logins | Queda de MAU > 20% nos últimos 30 dias. |
| **Suporte & Atrito Técnico** (25%) | SupportDesk Engine | Tickets abertos, Bugs Críticos, Violação de SLA | ≥ 2 Bugs Críticos abertos ou SLA estourado. |
| **Relacionamento & Governança** (20%) | B2B CRM Engine | Dias sem contato efetivo, Engajamento do Sponsor | Período sem interação > 21 dias. |
| **Financeiro & Contratual** (20%) | B2B CRM Engine | Proximidade de Renovação, Inadimplência | Renovação em < 60 dias sem tratativa. |

---

## 4. Diretrizes de Rotulagem Estrita (Anti-Alucinação)

Cada afirmação no diagnóstico do Radar **DEVE** ser encerrada com uma das três tags:
* **`[VALIDADO]`**: Fato confirmado diretamente pelos payloads de CRM, SupportDesk ou Telemetria.
* **`[HIPÓTESE]`**: Dedução analítica do agente que requer confirmação prática em reunião.
* **`[NÃO DITO]`**: Dados não encontrados nos conectores ou pilares sem telemetria disponível.

---

## 5. Templates Estritos de Saída

### 5.1. Dashboard do Radar da Carteira (Exibição na UI do Sistema)

```text
📊 [RADAR DE SAÚDE DA CARTEIRA] — Empresa: [Nome do Cliente]
---------------------------------------------------------------------------------
Health Score Consolidado: [XX/100] — Status: [🟢 VERDE / 🟡 AMARELO / 🔴 VERMELHO]
Subestado Atual: [O1 - Radar Quinzenal / O4 - Review de Carteira]
Última Varredura: [DD/MM/AAAA]

DECOMPOSIÇÃO DOS PILARES (Processado via engine/health_score.py):
• Uso & Engajamento (Peso 35%): Nota [XX/100] — MAU: [Variação %] [VALIDADO / NÃO DITO]
• Suporte & Atrito Técnico (Peso 25%): Nota [XX/100] — Tickets: [Nº abertos | Nº bugs] [VALIDADO / NÃO DITO]
• Relacionamento (Peso 20%): Nota [XX/100] — Último Contato: [Há N dias] [VALIDADO / NÃO DITO]
• Financeiro (Peso 20%): Nota [XX/100] — Renovação em: [DD/MM/AAAA] [VALIDADO / NÃO DITO]

DIAGNÓSTICO E PONTOS DE ATENÇÃO:
1. [Detalhamento do ponto de atenção 1] [VALIDADO / HIPÓTESE]
2. [Detalhamento do ponto de atenção 2] [VALIDADO / HIPÓTESE]

RECOMENDAÇÃO DO AGENTE (Direcionamento de Execução):
• Modo Mantido: [OPERAÇÃO / Ativar Playbook de Risco O3 em kam-churn-risk]
• Ação Imediata: [Descrição clara do próximo passo recomendado]
---------------------------------------------------------------------------------
```

### 5.2. Nota Automática de Radar no CRM (`POST /notes`)

```text
[Radar · auto] — DD/MM/AAAA
--------------------------------------------------
Status da Conta: [🟢 Verde / 🟡 Amarelo / 🔴 Vermelho] (Score: XX/100)
Subestado: O1 (Radar da Carteira)

SÍNTESE DE EVIDÊNCIAS:
• SupportDesk: [X chamados abertos | Y bugs críticos pendentes] [VALIDADO]
• B2B CRM Engine: [Última interação realizada há Z dias com o Sponsor] [VALIDADO]
• SaaS Telemetry API: [Adoção da plataforma em W% da capacidade contratada] [VALIDADO]

GATILHOS E ALERTAS:
- [Alerta 1, ex: Queda de logins da equipe de suporte no módulo de analytics] [VALIDADO / HIPÓTESE]
- [Alerta 2, ex: Contrato vencendo em 45 dias sem reunião de alinhamento agendada] [VALIDADO]

PLANO DE AÇÃO:
1. [Ação objetiva 1, ex: Invocar skill kam-value-cadence para agendar Pulse Check com Sponsor]
2. [Ação objetiva 2, ex: Cobrar resolução dos chamados críticos junto ao Suporte]
```

---

## 6. Trata de Casos de Borda e Erros de Coleta

1. **Falha na Telemetria de Uso:**
   * Caso os dados da SaaS Telemetry API retornem nulos, o agente aciona o `engine/health_score.py` com a flag de ausência de pilar. A nota total é recalculada proporcionalmente sobre os 3 pilares restantes e o pilar de Uso é exibido como `[NÃO DITO]`.
2. **Contas em Estado Amarelo ou Vermelho:**
   * Se o resultado do Health Score for **Amarelo (< 80)** ou **Vermelho (< 60)**, a Skill `kam-radar-carteira` imediatamente emite um alerta na UI e recomenda o acionamento automático da Skill **`kam-churn-risk`** (Gestão de Risco e Playbooks de Reativação).
3. **Solicitação de Expansão Durante o Radar:**
   * Se o usuário tentar forçar uma ação de expansão durante a geração do Radar para uma conta com saúde < 80, o agente emite uma mensagem de bloqueio: *"Transição bloqueada. A conta possui Health Score XX/100. Apenas contas na faixa Verde com dore mapeadas podem avançar para MODO EXPANSÃO."*