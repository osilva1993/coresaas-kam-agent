# 📈 Skill: kam-expansion-mapping — Mapeamento & Oportunidades de Expansão

> **Versão:** 2.0 Enterprise Full Specification  
> **Aplica-se a:** Subestados **E1, E2, E3 e E4** (Modo EXPANSÃO)  
> **Objetivo:** Mapear e estruturar oportunidades orgânicas de expansão (Upsell e Cross-sell) para contas ativas e saudáveis, alinhando dores operacionais validadas a novos módulos ou licenças da CoreSaaS Platform, conduzindo POCs (Provas de Conceito) orientadas a dados e registrando os negócios de expansão no CRM.  
> **Camada de Integração:** B2B CRM Engine (Criação de Oportunidades em Pipeline e Registro de Propostas) + SaaS Telemetry API (Identificação de Atingimento de Teto de Uso) + SupportDesk Engine (Validação de Ausência de Atritos) + engine/state_machine.py (Validação de Elegibilidade de Expansão) + engine/health_score.py (Confirmação de Saúde Verde).

---

## 1. Gatilhos de Ativação

Esta skill é ativada quando:
1. O Radar da Carteira (`kam-radar-carteira`) classifica a conta no estado **🟢 Verde (Health Score $\ge$ 80)** e identifica utilização acima de 85% do limite de licenças ou capacidade contratada.
2. O cliente expressa voluntariamente uma nova dor de negócio ou necessidade de funcionalidade adicional durante um Pulse Check (`kam-value-cadence`).
3. O usuário solicita a análise ou estruturação de uma oportunidade de expansão (ex: *"Mapear expansão para o cliente X"*, *"Montar proposta de novos módulos para a empresa Y"*).

---

## 2. Requisitos Rígidos de Elegibilidade (Hard-Lock Validation)

Antes de executar qualquer subestado do Modo EXPANSÃO, o agente valida as precondições obrigatórias junto ao `engine/state_machine.py`:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   CHECKLIST DE ELEGIBILIDADE DE EXPANSÃO               │
├────────────────────────────────────────────────────────────────────────┤
│  ✔ Health Score da Conta ≥ 80 (Status: Verde)                          │
│  ✔ Ausência de Chamados Críticos Abertos no SupportDesk Engine         │
│  ✔ Adimplência Financeira e Contrato Ativo sem Risco de Churn           │
│  ✔ Dor de Negócio Confirmada ou Teto de Uso Atingido (Telemetria)       │
└────────────────────────────────────────────────────────────────────────┘
```
*Se qualquer requisito falhar, o agente aborta a skill de expansão e redireciona a conta para o modo correspondente (OPERAÇÃO O2 ou O3).*

---

## 3. Sequenciamento Rígido de Execução (Subestados E1 a E4)

```text
┌─────────────────────────┐     ┌─────────────────────────┐
│ E1: Mapeamento da Dor   │ ──► │ E2: Conversa de Valor   │
│ - Teto de Telemetria    │     │ - Proposta de Valor     │
│ - Módulo Correspondente │     │ - Teste Guiado / POC    │
└─────────────────────────┘     └─────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│ E4: Registro do Negócio │ ◄── │ E3: Dimensionamento     │
│ - Criar Deal de Expansão│     │ - Tabela de Preços      │
│ - Atualização do CRM    │     │ - Estimativa de ROI     │
└─────────────────────────┘     └─────────────────────────┘
```

### 3.1. Subestado E1 — Mapeamento da Oportunidade
* **Objetivo:** Cruzar a dor informada ou o limite técnico atingido com a matriz de soluções da CoreSaaS Platform.
* **Ações:** Analisar logs da SaaS Telemetry API para identificar atingimento de limite de licenças ou demanda por módulos complementares.

### 3.2. Subestado E2 — Conversa de Valor & POC (Proof of Concept)
* **Objetivo:** Apresentar a expansão sob a perspectiva do retorno sobre investimento (ROI) e ganhos de produtividade, propondo teste guiado se necessário.
* **Ações:** Estruturar a justificativa de valor e definir critérios claros de sucesso para a POC (duração máxima de 14 a 30 dias).

### 3.3. Subestado E3 — Dimensionamento Comercial
* **Objetivo:** Calcular o acréscimo de ARR/MRR com base nas tabelas de preços oficiais da plataforma.
* **Ações:** Determinar o volume adicional de licenças ou o valor dos novos módulos e gerar o resumo financeiro da expansão.

### 3.4. Subestado E4 — Fechamento & Registro no B2B CRM Engine
* **Objetivo:** Registrar formalmente a oportunidade de expansão no pipeline correspondente do CRM.
* **Ações:** Criar o novo negócio de expansão vinculado à conta principal com os valores e datas previstas de fechamento.

---

## 4. Matriz de Mapeamento de Valor & Módulos

O agente consulta a matriz para conectar a dor técnica identificada na telemetria/reunião à solução do portfólio:

| Sinal de Telemetria / Dor do Cliente | Módulo Recomendado | Métrica de Impacto / ROI Esperado |
| :--- | :--- | :--- |
| Uso > 85% do limite de usuários cadastrados | **Pacote Adicional de Licenças (Seats)** | Inclusão de novas equipes sem gargalos de acesso. |
| Exportação manual constante de relatórios em CSV | **Módulo Avançado de Analytics & BI** | Redução de até 80% no tempo de montagem de relatórios. |
| Alto volume de processos manuais entre sistemas | **Módulo de Automação & APIs Dedicadas** | Eliminação de erros de digitação e ganho de escala. |
| Demanda por suporte prioritário e SLA reduzido | **Plano Premium Support & CS Dedicado** | Atendimento prioritário em até 1 hora para chamados. |

---

## 5. Diretrizes de Rotulagem Estrita (Anti-Alucinação)

Todas as saídas geradas durante o processo de expansão **DEVEM** conter as marcadores de proveniência de dados:
* **`[VALIDADO]`**: Capacidade atingida, módulos contratados atuais ou valores de tabela extraídos via conectores.
* **`[HIPÓTESE]`**: Estimativa de ROI, potencial de adoção das novas equipes ou prazos de fechamento.
* **`[NÃO DITO]`**: Orçamento disponível não declarado pelo cliente ou prazos internos de aprovação não informados.

---

## 6. Templates Estritos de Saída

### 6.1. Briefing de Oportunidade de Expansão (Exibição na UI)

```text
🚀 [OPORTUNIDADE DE EXPANSÃO DETECTADA] — Empresa: [Nome do Cliente]
---------------------------------------------------------------------------------
Health Score Consolidado: [XX/100] (Status: 🟢 Verde) — Subestado: E1
Indicador de Telemetria: [Uso em X% do limite / Demanda declarada pelo cliente] [VALIDADO]

OPORTUNIDADE E MÓDULO INDICADO:
• Solução Proposta: [Módulo / Licenças Adicionais] [VALIDADO]
• Dor de Negócio Mapeada: [Descrição sucinta da dor ou gargalo operacional] [VALIDADO / HIPÓTESE]
• ROI / Benefício Esperado: [Ganhos previstos de produtividade ou escala] [HIPÓTESE]

ESTRUTURA FINANCEIRA ESTIMADA (Subestado E3):
• Impacto no MRR: + R$ [Valor estimado]/mês [HIPÓTESE]
• Impacto no ARR: + R$ [Valor estimado]/ano [HIPÓTESE]

RECOMENDAÇÃO DE ABORDAGEM (Subestado E2):
• Agendar conversa consultiva de valor com o Sponsor [Nome do Sponsor] [VALIDADO]
• Apresentar proposta de teste guiado (POC) focado nos indicadores citados [HIPÓTESE]
---------------------------------------------------------------------------------
```

### 6.2. Minuta de Abordagem Consultiva de Expansão

```text
Assunto: CoreSaaS Platform | Ampliação de Eficiência e Novos Recorrentes — [Nome da Empresa]

Olá, [Nome do Sponsor], tudo bem?

Acompanhando a evolução e o uso da CoreSaaS Platform pela equipe da [Nome da Empresa], notamos que vocês atingiram [Métrica de Uso, ex: 90% da capacidade de licenças / alto engajamento no módulo operacional] [VALIDADO].

Com base no crescimento da operação de vocês, identificamos que a ativação do [Módulo Recomendado / Pacote Adicional] pode ajudar a [Benefício Principal, ex: automatizar a geração de relatórios e poupar horas da equipe] [HIPÓTESE].

Gostaria de sugerir uma breve conversa de 20 minutos nesta semana para apresentarmos uma demonstração prática desse impacto nas suas rotinas atuais.

Você teria disponibilidade em uma das opções abaixo?
- [Opção de Data 1] às [Horário 1]
- [Opção de Data 2] às [Horário 2]

Um abraço,
[Nome do KAM]
CoreSaaS Platform Team
```

### 6.3. Registro da Oportunidade no CRM (`POST /notes` e Registro de Deal)

```text
[Oportunidade de Expansão Criada · auto] — DD/MM/AAAA
--------------------------------------------------
Status da Conta: 🟢 Verde (Health Score: XX/100)
Modo: EXPANSÃO — Subestado: E4 (Fechamento / Registro no CRM)

DETALHES DO NEGÓCIO DE EXPANSÃO:
• Título da Oportunidade: `[Expansão] Módulo [Nome] — [Nome da Empresa]`
• Valor Estimado (MRR): + R$ [Valor] [HIPÓTESE]
• Pipeline / Estágio: Pipeline de Expansão / Qualificação Comercial
• Justificativa Técnica: Uso atual da plataforma atingiu [X%] da capacidade [VALIDADO]

AÇÃO EXECUTADA NO CRM:
1. Criado novo negócio de expansão vinculado ao cadastro do cliente [VALIDADO].
2. Tarefa atribuída ao KAM: `[Follow-up Expansão] Enviar proposta comercial para [Nome do Sponsor]` até [DD/MM/AAAA].
```

---

## 7. Tratamento de Exceções e Casos de Borda

1. **Queda do Health Score durante o Processo de Expansão:**
   * Se a nota da conta cair para abaixo de 80 (Amarelo ou Vermelho) enquanto o negócio estiver em negociação (E1 a E3), o `engine/state_machine.py` deve congelar imediatamente a oportunidade no CRM, emitir um alerta e mover a conta de volta para o **MODO OPERAÇÃO (Subestado O3 - Churn Risk)**.
2. **Rejeição Comercial da Expansão pelo Cliente:**
   * Caso o cliente decline a proposta, o agente deve registrar o motivo no CRM (`POST /notes`), encerrar o subestado de expansão sem alterar o contrato base e retornar a conta para o **MODO OPERAÇÃO (Subestado O1/O2)** mantendo os rituais regulares de valor.
3. **Solicitação de Expansão sem Validação da Telemetria ou Dor de Negócio:**
   * Se o usuário solicitar a criação de um negócio de expansão sem evidências de uso ou alinhamento com o cliente, o agente marca a oportunidade como `[HIPÓTESE]` e solicita confirmação explícita antes de efetuar o registro oficial de escrita no B2B CRM Engine.