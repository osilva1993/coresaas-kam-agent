# 🚨 Skill: kam-churn-risk — Gestão de Risco & Prevenção de Churn

> **Versão:** 2.0 Enterprise Full Specification  
> **Aplica-se a:** Subestado **O3** (Gestão de Risco & Churn Risk) — Modo OPERAÇÃO  
> **Objetivo:** Identificar atritos críticos, diagnosticar a causa-raiz de insatisfação ou desengajamento em contas com Health Score **Amarelo (60-79)** ou **Vermelho (0-59)**, travar programaticamente qualquer tentativa de expansão e aplicar playbooks de reativação (Técnico, Relacional e Adoção).  
> **Camada de Integração:** B2B CRM Engine (Leitura/Escrita de Atividades/Notas e Pipelining) + SupportDesk Engine (Análise de Chamados/SLA) + SaaS Telemetry API (Análise de Queda de MAU) + engine/state_machine.py (Hard-Lock de Estados) + engine/health_score.py (Validação da Saúde).

---

## 1. Gatilhos de Ativação

Esta skill é acionada obrigatoriamente quando:
1. O Radar da Carteira (`kam-radar-carteira`) detecta Health Score **Amarelo (< 80)** ou **Vermelho (< 60)** no **MODO OPERAÇÃO (Subestado O3)**.
2. A SaaS Telemetry API reporta uma queda abrupta de engajamento (queda de MAU > 20% em 30 dias).
3. O SupportDesk Engine registra $\ge 2$ bugs críticos abertos ou estouro sistemático de SLA de atendimento.
4. O B2B CRM Engine identifica que a conta está há mais de 30 dias sem qualquer contato efetivo com o Sponsor/Decisor.
5. O usuário aciona manualmente o protocolo de crise (ex: *"A conta X está ameaçando cancelar"*, *"Cliente Y relatou insatisfação grave"*).

---

## 2. Bloqueio Rígido de Expansão (Hard-Lock Engine)

Ao ser ativada para uma conta, a Skill `kam-churn-risk` comunica imediatamente o `engine/state_machine.py` para aplicar a seguinte regra inviolável:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        BLOQUEIO PROGRAMÁTICO                           │
│                                                                        │
│   Health Score < 80 OU Status = Amarelo / Vermelho                     │
│   ❌ PROIBIDO: Mover para MODO EXPANSÃO (E1, E2, E3, E4)              │
│   ❌ PROIBIDO: Gerar propostas de Upsell / Cross-sell                  │
│   ✔ OBRIGATÓRIO: Executar Playbook de Reativação O3                   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Matriz de Diagnóstico de Causa-Raiz & Playbooks de Ação

O agente deve analisar os dados combinados para isolar a origem primária do risco e selecionar o Playbook correspondente:

```text
                                 ┌──────────────────────────┐
                                 │ Leitura Integrada de     │
                                 │ Telemetria/CRM/Helpdesk  │
                                 └────────────┬─────────────┘
                                              │
      ┌───────────────────────────────────────┼───────────────────────────────────────┐
      ▼                                       ▼                                       ▼
┌───────────┐                           ┌───────────┐                           ┌───────────┐
│  PLAYBOOK │                           │  PLAYBOOK │                           │  PLAYBOOK │
│     A     │                           │     B     │                           │     C     │
│  Técnico  │                           │ Relacional│                           │  Adoção   │
└─────┬─────┘                           └─────┬─────┘                           └─────┬─────┘
      │                                       │                                       │
      ▼                                       ▼                                       ▼
• Bugs Críticos Abertos                 • Falta de Contato > 30d                • Queda de MAU > 20%
• Estouro de SLA                        • Troca do Sponsor/Decisor              • Subutilização de
• Suporte Travado                       • Insatisfação Comercial                • Módulos Contratados
```

### 3.1. Playbook A: Risco Técnico (SupportDesk Engine)
* **Indicadores:** High ticket count, bugs bloqueantes não resolvidos, insatisfação com suporte técnico.
* **Ação do Agente:**
  1. Compilar a lista exata dos tickets críticos pendentes (`ticket_id`, gravidade, dias em aberto).
  2. Estruturar solicitação de priorização interna junto ao time de Suporte/Engenharia.
  3. Gerar comunicação consultiva para o cliente apresentando o plano de ação de correção com prazos realistas.

### 3.2. Playbook B: Risco Relacional & Troca de Sponsor (B2B CRM Engine)
* **Indicadores:** Perda de interlocutor principal, ausência em reuniões de acompanhamento, mudança de gestão no cliente.
* **Ação do Agente:**
  1. Mapear contatos secundários registrados no cadastro do CRM.
  2. Elaborar minuta de reconexão executiva focada nos objetivos estratégicos da empresa (Executive Briefing).
  3. Recomendar ao KAM o agendamento de alinhamento com a nova liderança do cliente.

### 3.3. Playbook C: Risco de Adoção & Desengajamento (SaaS Telemetry API)
* **Indicadores:** Redução do número de usuários ativos, baixo acesso a funcionalidades chave contratadas.
* **Ação do Agente:**
  1. Mapear os módulos subutilizados pela equipe operacional.
  2. Criar plano de reciclagem e treinamento focado para os usuários chave.
  3. Elaborar e-mail propondo uma sessão de alinhamento técnico sem custos para reativação do uso.

---

## 4. Diretrizes de Rotulagem Estrita (Anti-Alucinação)

Todas as saídas geradas durante o diagnósticos de crise **DEVEM** utilizar as tags:
* **`[VALIDADO]`**: Dados extraídos diretamente de logs de telemetria, chamados abertos no suporte ou campos do CRM.
* **`[HIPÓTESE]`**: Causas deduzidas pelo agente (ex: *"Queda de uso pode indicar rotatividade na equipe do cliente"*).
* **`[NÃO DITO]`**: Ausência de informações contratuais ou falta de histórico recente no CRM.

---

## 5. Templates Estritos de Saída

### 5.1. Relatório de Diagnóstico de Risco e Plano de Crisis (Exibição na UI)

```text
🚨 [DIAGNÓSTICO DE RISCO DE CHURN] — Empresa: [Nome do Cliente]
---------------------------------------------------------------------------------
Health Score Atual: [XX/100] — Status: [🟡 AMARELO / 🔴 VERMELHO]
Subestado de Risco: O3 (Gestão de Churn Risk)
Gatilho Identificado: [Risco Técnico / Risco Relacional / Risco de Adoção]

ANÁLISE DE CAUSA-RAIZ:
• SupportDesk Engine: [Nº chamados críticos abertos | Status de SLA] [VALIDADO]
• SaaS Telemetry API: [Variação de MAU % nos últimos 30 dias] [VALIDADO]
• B2B CRM Engine: [Último contato realizado em DD/MM/AAAA com Sponsor] [VALIDADO]

PLAYBOOK SELECIONADO: [Playbook A - Técnico / Playbook B - Relacional / Playbook C - Adoção]

PLANO DE CONTENÇÃO E REVERSÃO:
1. Ação Imediata (Interna): [Ação curta e objetiva, ex: Cobrar SLA dos tickets X e Y]
2. Ação Externa (Cliente): [Ação curta e objetiva, ex: Enviar e-mail de reconexão executiva]
3. Prazo de Reavaliação: [DD/MM/AAAA] (Meta de Score: ≥ 80)
---------------------------------------------------------------------------------
```

### 5.2. Minuta de Comunicação de Crise / Reativação Executiva

```text
Assunto: CoreSaaS Platform | Priorização e Alinhamento Operacional — [Nome da Empresa]

Olá, [Nome do Sponsor/Contato], tudo bem?

Acompanhando os indicadores operacionais da [Nome da Empresa] na CoreSaaS Platform, identifiquei [Ponto Crítico, ex: a pendência na resolução do chamado #1234 relacionado ao módulo principal] [VALIDADO].

Sabemos do impacto dessa demanda nas suas operações diárias e já acionei diretamente nossa equipe de suporte e engenharia para priorizar essa tratativa [VALIDADO].

Gostaria de agendar um breve alinhamento de 15 minutos amanhã para lhe apresentar a solução desse ponto e alinharmos os próximos passos do projeto.

Você teria disponibilidade em um dos horários abaixo?
- [Opção de Data 1] às [Horário 1]
- [Opção de Data 2] às [Horário 2]

Um abraço,
[Nome do KAM]
CoreSaaS Platform Team
```

### 5.3. Registro de Nota de Contingência no CRM (`POST /notes`)

```text
[Reativação · auto] — DD/MM/AAAA
--------------------------------------------------
Status da Conta: [🟡 Amarelo / 🔴 Vermelho] (Health Score: XX/100)
Modo: OPERAÇÃO — Subestado: O3 (Gestão de Churn Risk)

ALERTA DE RISCO REGISTRADO:
• Causa-Raiz: [Descrição suscinta do motivo do risco] [VALIDADO]
• Evidências: SupportDesk: [Nº tickets] | Telemetria: [Queda de uso %] [VALIDADO]

ACOES DE CONTENCAO INICIADAS:
1. Playbook acionado: [Playbook A - Técnico / B - Relacional / C - Adoção].
2. Trava de Expansão mantida até a recuperação do Health Score (Meta: ≥ 80).
3. Tarefa criada no CRM: `[Contenção de Crise] Acompanhar resolução dos tickets do cliente` para [DD/MM/AAAA].
```

---

## 6. Tratamento de Exceções e Regras de Segurança

1. **Solicitação do Usuário para Ignorar o Risco e Criar Oportunidade de Venda:**
   * O agente deve negar a operação e responder: *"Operação bloqueada pela máquina de estados. A conta apresenta risco crítico (Health Score: XX/100). Finalize primeiro o playbook de reativação (Subestado O3) antes de tentar qualquer ação comercial."*
2. **Cliente Irresponsivo no E-mail de Crise (> 7 dias no estado Vermelho):**
   * O agente deve emitir um alerta de **Risco Iminente de Cancelamento** na UI e recomendar a escalada do caso para a gestão executiva de Account Management.
3. **Ausência de Mapeamento do Sponsor no CRM durante a Crise:**
   * O agente rebaixa temporariamente a conta para o subestado **S2 (Saneamento de Cadastro)** para forçar o mapeamento do interlocutor antes de prosseguir com o plano de ação.