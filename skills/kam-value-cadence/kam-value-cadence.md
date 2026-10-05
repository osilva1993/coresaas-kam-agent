# 🤝 Skill: kam-value-cadence — Cadência de Valor & Pulse Checks

> **Versão:** 2.0 Enterprise Full Specification  
> **Aplica-se a:** Subestado **O2** (Cadência de Valor & Rituais de Relacionamento) — Modo OPERAÇÃO  
> **Objetivo:** Conduzir a rotina continuada de engajamento focada no valor entregue ao cliente, gerando pautas estruturadas para reuniões curtas (*Pulse Checks* de 20-30 min), minutas de e-mail de acompanhamento e registros automatizados de atividades no CRM, sempre ancorados em dados reais de uso e suporte.  
> **Camada de Integração:** B2B CRM Engine (Agendamento de Atividades e Registros de Notas) + SupportDesk Engine (Evidências de Suporte) + SaaS Telemetry API (Métricas de Engajamento) + engine/health_score.py (Leitura do Score).

---

## 1. Gatilhos de Ativação

Esta skill é ativada quando:
1. O cronograma de governança indica a necessidade de agendar ou realizar um *Pulse Check* (quinzenal, mensal ou trimestral) no **MODO OPERAÇÃO (Subestado O2)**.
2. O usuário solicita a preparação de pauta para reunião de alinhamento com um cliente específico (ex: *"Preparar pauta de reunião para a empresa X"*, *"Montar e-mail de acompanhamento para o Sponsor da conta Y"*).
3. O Radar da Carteira (`kam-radar-carteira`) indica estabilidade ou recuperação de saúde e orienta a retomada de contato proativo de valor.

---

## 2. Fluxo Sequencial de Execução (O2)

O agente deve orquestrar as interações respeitando o ciclo de vida da comunicação consultiva:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ PASSO 1: Diagnóstico Rápido de Contexto (CRM + Telemetria + Suporte)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PASSO 2: Elaboração da Pauta Estruturada do Pulse Check (20-30 min)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PASSO 3: Geração da Minuta de E-mail / Convite Consultivo              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PASSO 4: Registro da Atividade Planejada no CRM (POST /activities)     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Metodologia e Estrutura do Pulse Check (20 a 30 Minutos)

Para maximizar a produtividade e respeitar o tempo do cliente (especialmente Decisores e Sponsors), as reuniões de Cadência de Valor projetadas pelo agente devem seguir estritamente o bloco de tempo de 30 minutos:

| Bloco de Tempo | Foco da Discussão | Origem dos Dados |
| :--- | :--- | :--- |
| **00 - 05 min** | **Abertura & Alinhamento:** Confirmação da pauta e checagem de prioridades imediatas do cliente. | B2B CRM Engine |
| **05 - 15 min** | **Demonstração de Valor & Adotação:** Apresentação de dados de uso, conquistas operacionais e ROI gerado. | SaaS Telemetry API |
| **15 - 25 min** | **Atritos & Desbloqueios:** Status de chamados críticos ou solicitações em aberto sem jargões técnicos. | SupportDesk Engine |
| **25 - 30 min** | **Próximos Passos & Encaminhamentos:** Definição objetiva de responsáveis, prazos e data da próxima sessão. | B2B CRM Engine |

---

## 4. Diretrizes de Rotulagem Estrita (Anti-Alucinação)

Todas as pautas, e-mails e notas gerados por esta skill **DEVEM** ser marcados com as tags de proveniência de dados:
* **`[VALIDADO]`**: Dados numéricos de uso, contratos, nomes de contatos e chamados confirmados no payload.
* **`[HIPÓTESE]`**: Oportunidades de melhoria de processo ou deduções de negócios a serem checadas na reunião.
* **`[NÃO DITO]`**: Tópicos onde faltam dados cadastrais ou históricos no CRM.

---

## 5. Templates Estritos de Saída

### 5.1. Pauta Estruturada para Pulse Check (Exibição na UI do Sistema)

```text
🤝 [PAUTA DE PULSE CHECK] — Cliente: [Nome da Empresa]
---------------------------------------------------------------------------------
Participante Principal (Sponsor): [Nome do Contato] ([Cargo/Função]) [VALIDADO]
Health Score Atual: [XX/100] (Status: [🟢 Verde / 🟡 Amarelo]) | Subestado: O2
Duração Prevista: 20 a 30 minutos

OBJETIVOS DA SESSÃO:
1. Validar os ganhos operacionais obtidos com os módulos ativos [VALIDADO]
2. Tratar pendências técnicas ou gargalos operacionais [VALIDADO / HIPÓTESE]

BLOCO 1: VALOR E ADOÇÃO (10 min)
• Módulos em uso: [Lista de Módulos] [VALIDADO]
• Destaque de Telemetria: Adoção do sistema em [X%] com [Y] usuários ativos no mês [VALIDADO]
• Ponto de Atenção: Módulo [Nome do Módulo] com uso abaixo da média [HIPÓTESE]

BLOCO 2: SUPORTE E OPERAÇÃO (10 min)
• Status no SupportDesk: [Nº de chamados resolvidos] nos últimos 30 dias [VALIDADO]
• Pendências Abertas: [Descrição sucinta do chamado crítico, se houver, ou "Zero pendências impeditivas"] [VALIDADO]

BLOCO 3: ALINHAMENTO E PRÓXIMOS PASSOS (10 min)
• Checagem de prioridade do trimestre junto ao Sponsor [HIPÓTESE]
• Acordo de data para o próximo alinhamento [VALIDADO]
---------------------------------------------------------------------------------
```

### 5.2. Minuta de E-mail de Abordagem Consultiva

```text
Assunto: CoreSaaS Platform | Acompanhamento de Resultados e Evolução — [Nome da Empresa]

Olá, [Nome do Contato], tudo bem?

Passando para compartilhar um breve resumo do uso da CoreSaaS Platform na [Nome da Empresa]. Identificamos que a equipe manteve um engajamento consistente, atingindo [Métrica de Uso / % MAU] no último período [VALIDADO].

Para garantirmos que a solução continue gerando o máximo valor para as suas operações, gostaria de propor um rápido alinhamento de 20 minutos nesta semana. O objetivo é repassarmos os principais indicadores de uso e alinhar os próximos passos do projeto.

Temos disponibilidade nos seguintes horários:
- [Opção 1: Exemplo - Terça-feira, às 10h00]
- [Opção 2: Exemplo - Quinta-feira, às 14h30]

Qual dessas opções funciona melhor para você?

Um abraço,
[Nome do KAM]
CoreSaaS Platform Team
```

### 5.3. Registro de Nota e Atividade no CRM (`POST /notes`)

```text
[Pulse Check Agendado · auto] — DD/MM/AAAA
--------------------------------------------------
Status da Conta: [🟢 Verde / 🟡 Amarelo] (Health Score: XX/100)
Subestado: O2 (Cadência de Valor)

DETALHES DO AGENDAMENTO:
• Interlocutor: [Nome do Contato] ([Cargo]) [VALIDADO]
• Objetivos: Reunião de acompanhamento de valor e validação do uso do módulo [Nome do Módulo] [VALIDADO]

PAUTA REGISTRADA:
1. Apresentação dos dados de telemetria e engajamento das equipes [VALIDADO]
2. Revisão de chamados e suporte técnico do SupportDesk [VALIDADO]
3. Alinhamento de próximos marcos operacionais [HIPÓTESE]

AÇÃO REGISTRADA NO CRM:
• Criada tarefa de follow-up: `[Pulse Check] Reunião de Valor com [Nome da Empresa]` para [DD/MM/AAAA].
```

---

## 6. Tratamento de Exceções e Bloqueios

1. **Tentativa de Executar Cadência em Contas de Risco Crítico (Health Score < 60):**
   * A Cadência de Valor convencional (O2) é interrompida. O agente altera o direcionamento e emite o aviso: *"Esta conta apresenta Risco Crítico de Churn (Health Score: XX). A skill kam-value-cadence foi suspensa. Ative imediatamente a skill kam-churn-risk para executar o playbook de contenção de crise."*
2. **Falta de Resposta do Cliente aos E-mails de Cadência (> 30 dias sem contato):**
   * Após 2 tentativas de e-mail de valor sem retorno do Sponsor, o agente deve reclassificar o pilar de Relacionamento e sugerir uma abordagem de reconexão via canal secundário (ex: ligação direta ou mensagem para canal de suporte interno).
3. **Solicitação de Proposta Comercial / Expansão Durante a Preparação do Pulse Check:**
   * O agente só permite incluir tópicos de expansão na pauta se a conta estiver rigorosamente na faixa **Verde (Score ≥ 80)**. Caso contrário, responde: *"Inclusão de pauta comercial bloqueada. A prioridade atual desta conta é a consolidação de valor e estabilização operacional."*