# 🌐 Skill: kam-market-signals — Inteligência de Mercado & Monitoramento de Sinais Externa

> **Versão:** 2.0 Enterprise Full Specification  
> **Aplica-se a:** Modo OPERAÇÃO (Subestados **O1, O2, O3**) e Modo EXPANSÃO (Subestado **E1**)  
> **Objetivo:** Monitorar, capturar e estruturar informações públicas de mercado sobre as contas da carteira (aportes financeiros, trocas de diretoria/C-Level, M&A, expansão de equipes, novas filiais e notícias do setor), cruzando dados externos com a saúde interna para antecipar riscos relacionais e identificar gatilhos de expansão orgânica.  
> **Camada de Integração:** Market Intelligence Engine / Search API (Web Scraping / Google News / LinkedIn Data) + B2B CRM Engine (Gravação de Notas e Atualização de Stakeholders) + engine/state_machine.py (Gatilho de Transição) + engine/health_score.py (Impacto em Relacionamento).

---

## 1. Gatilhos de Ativação

Esta skill é acionada automaticamente pelo orquestrador ou pelo usuário quando:
1. É executado o ciclo semanal/mensal de varredura externa da carteira no **MODO OPERAÇÃO (Subestado O1)**.
2. Uma nova notícia ou sinal crítico de mercado é detectado via Webhooks do Market Intelligence Engine para uma conta ativa.
3. O usuário solicita um briefing de notícias ou contexto de mercado de uma conta antes de um ritual executivo (ex: *"Quais as últimas notícias sobre a empresa X?"*, *"Mapear sinais da conta Y"*).
4. Ocorre a identificação de teto de telemetria ou busca de gatilhos para ativação do **MODO EXPANSÃO (Subestado E1)**.

---

## 2. Matriz de Classificação de Sinais de Mercado

Os sinais capturados publicamente são categorizados em 3 vetores de impacto no ciclo de vida do cliente:

| Categoria do Sinal | Eventos Detectados na Mídia / Mercado | Impacto no Diagnóstico da Conta | Ação Automática Recomendada |
| :--- | :--- | :--- | :--- |
| **Risco Relacional** *(Alerta Amarelo/Vermelho)* | Troca de CEO/CTO/CFO, Reestruturação/Layoffs, Mudança na liderança da área contratante. | **Ameaça de Churn (Troca de Stack):** O novo líder pode trazer concorrentes. | Acionar `kam-churn-risk` (Playbook B - Relacional) para reconexão imediata. |
| **Gatilho de Expansão** *(Oportunidade Verde)* | Recebimento de Aporte (Aumento de Capital), Fusões e Aquisições (M&A), Expansão para novas filiais. | **Orçamento Aberto / Novas Demandas:** Necessidade imediata de mais licenças e suporte. | Acionar `kam-expansion-mapping` (Subestado E1) com proposta customizada. |
| **Contexto de Negócio** *(Informativo)* | Lançamento de novos produtos do cliente, premiações, resultados trimestrais publicados. | **Pauta Consultiva:** Enriquecimento para Pulse Checks e reuniões executivas. | Injetar insights na Skill `kam-value-cadence` para personalização da pauta. |

---

## 3. Fluxo de Processamento & Cruzamento com Dados Internos

```text
┌────────────────────────────────────────────────────────────────────────┐
│ PASSO 1: Coleta e Filtragem de Notícias (Market Intelligence Engine)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PASSO 2: Classificação e Descarte de Falsos Positivos                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PASSO 3: Cruzamento de Sinal Externo com Health Score Interno          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PASSO 4: Direcionamento para Skill Específica (O3 / E1 / O2)           │
│ e Registro de Nota no B2B CRM Engine (POST /notes)                    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Diretrizes de Rotulagem Estrita (Anti-Alucinação)

Todas as saídas baseadas em inteligência pública **DEVEM** conter as tags de proveniência de dados:
* **`[VALIDADO]`**: Notícia, fato público com fonte identificada (URL/Veículo) ou confirmação no CRM.
* **`[HIPÓTESE]`**: Dedução do agente sobre o impacto que aquele sinal público causará no contrato do cliente.
* **`[NÃO DITO]`**: Falta de confirmação sobre se a mudança de mercado afetará diretamente o escopo contratado.

---

## 5. Templates Estritos de Saída

### 5.1. Dashboard de Sinais de Mercado (Exibição na UI do Sistema)

```text
🌐 [RADAR DE INTELIGÊNCIA DE MERCADO] — Empresa: [Nome do Cliente]
---------------------------------------------------------------------------------
Health Score Interno Atual: [XX/100] (Status: [🟢 Verde / 🟡 Amarelo / 🔴 Vermelho])
Sinais Monitorados nos Últimos 30 Dias: [Nº de sinais encontrados]

SINAIS EXTERNOS DETECTADOS:
• Evento Mapeado: [Ex: Aporte Série B de R$ 50 Mi / Troca de VP de Tecnologia] [VALIDADO]
• Fonte / Veículo: [Nome do Veículo, ex: Exame, Valor Econômico, LinkedIn] [VALIDADO]
• Categoria: [🚨 Risco Relacional / 🚀 Gatilho de Expansão / ℹ️ Contexto de Negócio]

ANÁLISE DE IMPACTO NO CONTRATO ATUAL:
• Diagnóstico: [Explicação curta sobre como o fato impacta o uso do produto] [HIPÓTESE]
• Risco / Oportunidade: [Descrição objetiva, ex: Risco de revisão do fornecedor pelo novo VP] [HIPÓTESE]

RECOMENDAÇÃO DO AGENTE:
• Rota de Ação: [Invocar kam-churn-risk (Playbook B) / Invocar kam-expansion-mapping (E1)]
• Próximo Passo: [Ex: Agendar reunião de apresentação institucional para o novo executivo]
---------------------------------------------------------------------------------
```

### 5.2. Minuta de Abordagem Baseada em Sinal de Mercado

```text
Assunto: Parabenização pela [Conquista/Notícia] & Atualização de Parceria — [Nome da Empresa]

Olá, [Nome do Contato/Sponsor], tudo bem?

Acompanhando os movimentos recentes do mercado, vimos a notícia sobre a [Mencionar a notícia: ex: captação da nova rodada de investimento / expansão da nova unidade em SP] da [Nome da Empresa]. Parabéns a todo o time por essa grande conquista! [VALIDADO]

Sabemos que movimentos como este costumam trazer desafios de escala e necessidade de expansão das operações. Do nosso lado, gostaríamos de garantir que a CoreSaaS Platform esteja 100% pronta para suportar esse novo momento.

Gostaria de agendar um breve alinhamento de 15 minutos nesta semana para apresentarmos como podemos apoiar essa nova fase e garantir o alinhamento das ferramentas.

Você teria disponibilidade em um dos horários abaixo?
- [Opção de Data 1] às [Horário 1]
- [Opção de Data 2] às [Horário 2]

Um abraço,
[Nome do KAM]
CoreSaaS Platform Team
```

### 5.3. Registro de Nota de Sinais no CRM (`POST /notes`)

```text
[Sinal de Mercado Detectado · auto] — DD/MM/AAAA
--------------------------------------------------
Status da Conta: [🟢 Verde / 🟡 Amarelo / 🔴 Vermelho] (Health Score: XX/100)
Subestado: O1 (Radar de Mercado)

SINTESE DO SINAL CAPTURADO:
• Notícia/Evento: [Descrição sucinta da notícia capturada] [VALIDADO]
• Categoria do Evento: [Risco Relacional / Expansão / Contexto] [VALIDADO]
• Fonte: [Nome do portal de notícias ou rede profissional] [VALIDADO]

IMPACTO RECOMENDADO NO CRM:
1. Recomenda-se atualização dos Stakeholders no B2B CRM Engine (Subestado S2).
2. Tarefa atribuída ao KAM: `[Abordagem por Sinal de Mercado] Realizar contato focado em [Aporte/Novo Executivo]` para [DD/MM/AAAA].
```

---

## 6. Tratamento de Exceções e Casos de Borda

1. **Falsos Positivos e Notícias Pertencentes a Empresas Homônimas:**
   * O agente valida obrigatoriamente o CNPJ, domínio do site ou cidade/estado da conta antes de confirmar o sinal no B2B CRM Engine. Caso haja ambiguidade, o sinal é descartado ou marcado estritamente como `[HIPÓTESE]` dependendo do nível de confiança (< 90%).
2. **Conflito entre Sinal de Expansão (Aporte) e Health Score Vermelho (Risco Interno):**
   * Se a mídia anunciar que a empresa recebeu um grande aporte, mas o Health Score interno for **Vermelho (< 60)** devido a bugs graves no SupportDesk Engine, a ação de expansão é **bloqueada pelo orquestrador**. O sinal de aporte é apenas registrado em nota no CRM e a skill prioriza a resolução dos problemas técnicos (`kam-churn-risk`).
3. **Ausência de Notícias Públicas (Contas Fechadas / Mid-Market Menor):**
   * Se a busca automatizada não retornar resultados para contas menores, a skill não interrompe a operação e registra no histórico: `[Sem sinais recentes mapeados]`.