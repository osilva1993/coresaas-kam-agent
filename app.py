import os
import streamlit as st
from dotenv import load_dotenv

# Carrega variáveis de ambiente (.env)
load_dotenv()

from connectors.crm_connector import CRMConnector
from connectors.support_connector import SupportConnector
from connectors.telemetry_connector import TelemetryConnector
from connectors.market_intelligence_connector import MarketIntelligenceConnector

from engine.health_score import HealthScoreEngine
from engine.state_machine import StateMachineEngine
from agent_orchestrator import AgentOrchestrator
from llm_client import LLMClient

# Configuração da página Streamlit
st.set_page_config(
    page_title="CoreSaaS KAM Agent - Cockpit de Governança",
    page_icon="🛡️",
    layout="wide"
)

# Estilização CSS customizada para cards e status
st.markdown("""
<style>
    .connector-badge {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR - SELEÇÃO DE CLIENTE & STATUS DOS CONECTORES
# ---------------------------------------------------------
st.sidebar.title("🛡 CoreSaaS KAM")
st.sidebar.markdown("---")

st.sidebar.header("📋 Carteira de Contas")
available_clients = {
    "CLI-101": "Acme Logistics S.A. (Saudável / Expansão)",
    "CLI-202": "TechPay Finanças (Risco de Churn)"
}

selected_client_id = st.sidebar.selectbox(
    "Selecione a Conta:",
    options=list(available_clients.keys()),
    format_func=lambda x: f"{x} - {available_clients[x]}"
)

st.sidebar.markdown("---")
st.sidebar.header("🔌 Conectores Ativos & Status")
st.sidebar.caption("Sincronização em tempo real via APIs B2B:")

# Indicadores Visuais de Conexão Ativa
st.sidebar.success("🟢 **B2B CRM Engine** (HubSpot/Salesforce)")
st.sidebar.success("🟢 **SupportDesk Engine** (Zendesk API)")
st.sidebar.success("🟢 **SaaS Telemetry Engine** (PostHog/Mixpanel)")
st.sidebar.success("🟢 **Market Radar Engine** (Web & News API)")
st.sidebar.success("🟢 **Email & Outreach** (SMTP/Graph API)")

st.sidebar.markdown("---")
st.sidebar.caption("v1.2.0 • Engine Determinístico + Groq AI")

# ---------------------------------------------------------
# LEITURA E PROCESSAMENTO DOS DADOS
# ---------------------------------------------------------
crm_data = CRMConnector.get_account_data(selected_client_id)
support_data = SupportConnector.get_support_data(selected_client_id)
telemetry_data = TelemetryConnector.get_telemetry_data(selected_client_id)
market_data = MarketIntelligenceConnector.get_market_signals(selected_client_id)

if not crm_data:
    st.error(f"Cliente {selected_client_id} não encontrado.")
    st.stop()

health_result = HealthScoreEngine.evaluate(
    telemetry=telemetry_data,
    support=support_data,
    crm_data=crm_data
)

has_expansion_trigger = any(
    s["category"] == "Gatilho de Expansão" for s in market_data.get("signals", [])
) if market_data else False

recommendation = StateMachineEngine.resolve_recommended_stage(
    current_stage=crm_data["current_stage"],
    health_score_data=health_result,
    crm_data=crm_data,
    has_market_expansion_trigger=has_expansion_trigger
)

# ---------------------------------------------------------
# CABEÇALHO PRINCIPAL DA CONTA
# ---------------------------------------------------------
st.title(f"🏢 {crm_data['company_name']}")
st.caption(f"ID da Conta: `{selected_client_id}` | KAM Responsável: **{crm_data.get('owner_kam', 'N/A')}**")

# KPI Cards Topo
col1, col2, col3, col4 = st.columns(4)

score = health_result["score"] if "score" in health_result else health_result["health_score"]
status = health_result["status"]

with col1:
    st.metric("Receita Recorrente (MRR)", f"R$ {crm_data.get('mrr', 0):,.2f}")

with col2:
    if status == "VERDE":
        st.metric("Health Score", f"{score:.1f} / 100", delta="🟢 SAUDÁVEL", delta_color="normal")
    elif status == "AMARELO":
        st.metric("Health Score", f"{score:.1f} / 100", delta="🟡 ATENÇÃO", delta_color="off")
    else:
        st.metric("Health Score", f"{score:.1f} / 100", delta="🔴 RISCO CRÍTICO", delta_color="inverse")

with col3:
    st.metric("Estágio Atual CRM", crm_data["current_stage"])

with col4:
    st.metric("Recomendação do Engine", recommendation["recommended_stage"], delta=recommendation["mode"])

# Alerta de Governança
if status == "VERMELHO":
    st.error(f"🚨 **BLOQUEIO DE SEGURANÇA ATIVO**: {recommendation['action']}")
elif status == "AMARELO":
    st.warning(f"⚡ **ATENÇÃO REQUERIDA**: {recommendation['action']}")
else:
    st.success(f"🚀 **OPORTUNIDADE AUTORIZADA**: {recommendation['action']}")

st.markdown("---")

# ---------------------------------------------------------
# ABAS DA INTERFACE
# ---------------------------------------------------------
tab_overview, tab_pillars, tab_agent = st.tabs([
    "📊 Visão Geral & Hub dos Conectores", 
    "📈 Detalhamento do Health Score", 
    "🤖 Copiloto IA & Human-in-the-Loop"
])

# --- TAB 1: VISÃO GERAL & HUB DOS CONECTORES ---
with tab_overview:
    st.subheader("📡 Status e Mapeamento Integrado de Fontes de Dados")
    st.caption("Visão estruturada e executiva das informações extraídas automaticamente pelas APIs de conexão.")

    c_left, c_right = st.columns(2)

    with c_left:
        # CARD CRM
        with st.container(border=True):
            st.markdown("### 💼 B2B CRM Engine *(Salesforce / HubSpot)*")
            st.markdown("Status: <span class='connector-badge'>🟢 Sincronizado</span>", unsafe_allow_html=True)
            st.markdown("---")
            
            m1, m2 = st.columns(2)
            with m1:
                st.write("**Oportunidade ID:**", crm_data.get('deal_id', 'N/A'))
                st.write("**Dias p/ Renovação:**", f"⏱️ {crm_data.get('days_to_renewal', 0)} dias")
                st.write("**Último Contato:**", f"🗓️ {crm_data.get('days_since_last_contact', 0)} dias atrás")
            with m2:
                st.write("**Adimplência Financeira:**", "✅ Regular" if crm_data.get('adimplente') else "❌ Inadimplente")
                st.write("**Patrocinador Ativo (Sponsor):**", "✅ Sim" if crm_data.get('has_active_sponsor') else "⚠️ Não Identificado")
                st.write("**Módulos Ativos:**", ", ".join(crm_data.get('active_modules', [])))

        # CARD TELEMETRIA
        with st.container(border=True):
            st.markdown("### 📊 SaaS Telemetry Engine *(PostHog / Mixpanel)*")
            st.markdown("Status: <span class='connector-badge'>🟢 Sincronizado</span>", unsafe_allow_html=True)
            st.markdown("---")
            
            t1, t2, t3 = st.columns(3)
            with t1:
                st.metric("Usuários Ativos (MAU)", telemetry_data.get('mau', 0))
            with t2:
                st.metric("Engajamento M/M", f"{telemetry_data.get('engagement_trend_pct', 0)}%")
            with t3:
                st.metric("Adoção de Features", f"{telemetry_data.get('feature_adoption_rate', 0)}%")
            
            st.write("**Frequência de Uso:**", telemetry_data.get('usage_frequency', 'N/A'))

    with c_right:
        # CARD SUPORTE
        with st.container(border=True):
            st.markdown("### 🎧 SupportDesk Engine *(Zendesk / Freshdesk)*")
            st.markdown("Status: <span class='connector-badge'>🟢 Sincronizado</span>", unsafe_allow_html=True)
            st.markdown("---")
            
            s1, s2, s3 = st.columns(3)
            with s1:
                st.metric("Tickets Abertos", support_data.get('open_tickets_count', 0))
            with s2:
                st.metric("Tickets Críticos", support_data.get('critical_tickets_count', 0))
            with s3:
                st.metric("Violações de SLA", support_data.get('sla_violations_last_30d', 0))

            st.write("**Tempo Médio de Resolução:**", f"⏱️ {support_data.get('avg_resolution_time_hours', 0)} horas")
            st.write("**Bugs Críticos Em Aberto:**", "🔴 Sim (Atenção)" if crm_data.get('has_unresolved_critical_bugs') else "🟢 Nenhum")

        # CARD INTEL DE MERCADO
        with st.container(border=True):
            st.markdown("### 🌐 Market Intelligence Engine *(Web Radar & Social)*")
            st.markdown("Status: <span class='connector-badge'>🟢 Sincronizado</span>", unsafe_allow_html=True)
            st.markdown("---")
            
            signals = market_data.get("signals", [])
            if signals:
                for sig in signals:
                    st.warning(f"**[{sig['category']}]** {sig['headline']}")
                    st.caption(f"Data do Evento: {sig['event_date']} | Relevância: {sig['confidence_score']*100:.0f}%")
            else:
                st.success("Nenhum sinal crítico de mercado detectado para esta conta recentemente.")

# --- TAB 2: DETALHAMENTO DO HEALTH SCORE ---
with tab_pillars:
    st.subheader("📈 Decomposição Analítica dos Pilares de Saúde")
    st.caption("Fórmula Ponderada Determinística: Telemetria (40%) + Suporte (30%) + Relacionamento CRM (30%)")

    pillars = health_result.get("pillars", {})
    p_cols = st.columns(len(pillars))
    
    for i, (p_name, p_val) in enumerate(pillars.items()):
        with p_cols[i]:
            with st.container(border=True):
                st.markdown(f"### Pilar: {p_name.upper()}")
                p_score = p_val.get('score', 0)
                p_status = p_val.get('status', 'N/A')
                
                if p_status == "VERDE":
                    st.success(f"Nota: **{p_score:.1f} / 100**")
                elif p_status == "AMARELO":
                    st.warning(f"Nota: **{p_score:.1f} / 100**")
                else:
                    st.error(f"Nota: **{p_score:.1f} / 100**")
                    
                st.caption(f"Peso no Ponderado: **{p_val.get('weight', 0)*100:.0f}%**")
                
                if "details" in p_val:
                    st.markdown("**Sub-indicadores:**")
                    for k, v in p_val["details"].items():
                        st.write(f"- {k}: `{v}`")

# --- TAB 3: COPILOTO IA & HUMAN IN THE LOOP (INTERATIVO) ---
with tab_agent:
    st.subheader("🤖 Agente Copiloto KAM & Fluxo Human-in-the-Loop")
    st.caption("Interaja continuamente com o Copiloto. O agente refina diagnósticos, analisa e-mails e gera estratégias sob demanda baseando-se no contexto real da conta.")

    st.info(f"🎯 **Skill Requerida Identificada pelo Engine:** `{recommendation['action']}`")

    # Inicialização do Histórico de Chat por Cliente
    chat_key = f"chat_history_{selected_client_id}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    # Seção de Botões de Atalhos
    st.markdown("##### ⚡ Atalhos Rápidos & Sugestões de Requisição:")
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)

    prompt_triggered = None

    with col_b1:
        if st.button("🚀 Diagnóstico & Minuta Inicial", use_container_width=True, type="primary"):
            prompt_triggered = "Por favor, gere o diagnóstico estratégico completo e a minuta inicial de comunicação com a conta baseando-se no contexto determinístico."

    with col_b2:
        if st.button("📝 Tom C-Level / Executivo", use_container_width=True):
            prompt_triggered = "Reescreva a última proposta/diagnóstico em um tom estritamente executivo, resumido e com foco no ROI para ser apresentado a diretores."

    with col_b3:
        if st.button("📧 Analisar E-mail de Objeção", use_container_width=True):
            prompt_triggered = "Simulação: O cliente enviou um e-mail dizendo: 'Estamos revisando nossos custos operacionais deste trimestre e gostaríamos de negociar o valor da renovação'. Como o KAM deve responder mantendo a postura consultiva e o contrato saudável?"

    with col_b4:
        if st.button("📋 Briefing Pré-Reunião", use_container_width=True):
            prompt_triggered = "Gere um briefing executivo de 5 tópicos principais para minha próxima reunião com o cliente, destacando o Health Score, pendências e o próximo passo recomendado."

    # Campo de Entrada do Chat Livre
    user_input = st.chat_input("Digite sua dúvida, solicitação de ajuste ou instrução para o Copiloto KAM...")
    if user_input:
        prompt_triggered = user_input

    # Exibição do Histórico da Conversa
    st.markdown("---")
    st.markdown("#### 💬 Conversa com o Copiloto KAM")

    if not st.session_state[chat_key]:
        st.caption("Nenhuma interação ainda nesta conta. Clique em um dos atalhos acima ou digite uma mensagem no chat abaixo para iniciar.")

    for message in st.session_state[chat_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Processamento de Novo Prompt
    if prompt_triggered:
        st.session_state[chat_key].append({"role": "user", "content": prompt_triggered})
        with st.chat_message("user"):
            st.markdown(prompt_triggered)

        with st.chat_message("assistant"):
            with st.spinner("Copiloto KAM processando dados e consultando o modelo de linguagem..."):
                context = AgentOrchestrator.load_context(selected_client_id)
                base_prompt = AgentOrchestrator.build_llm_prompt(context)
                system_instruction = context["system_instruction"]

                # Monta histórico conversacional para manter o contexto dos turnos anteriores
                conversation_history = "\n\n".join([
                    f"{'KAM (Usuário)' if msg['role'] == 'user' else 'Copiloto KAM'}: {msg['content']}"
                    for msg in st.session_state[chat_key]
                ])

                full_llm_prompt = f"""
{base_prompt}

### HISTÓRICO DA CONVERSA CONTINUA NESTA SESSÃO:
{conversation_history}

Responda mantendo rigorosamente a postura de um especialista KAM, respeitando as travas do engine e aplicando as tags de proveniência de dados ao final das frases ([VALIDADO], [HIPÓTESE] ou [NÃO DITO]).
"""
                response = LLMClient.generate_response(
                    system_instruction=system_instruction,
                    user_prompt=full_llm_prompt
                )

                st.markdown(response)
                st.session_state[chat_key].append({"role": "assistant", "content": response})
                st.session_state[f"last_response_{selected_client_id}"] = response
                st.rerun()

    # Seção de Aprovação Human-in-the-Loop (para persistir a resposta mais recente no CRM)
    if st.session_state[chat_key]:
        st.markdown("---")
        with st.expander("✅ **Human-in-the-Loop: Revisar & Registrar Minuta Final no CRM**", expanded=False):
            latest_reply = st.session_state.get(
                f"last_response_{selected_client_id}", 
                st.session_state[chat_key][-1]["content"] if st.session_state[chat_key][-1]["role"] == "assistant" else ""
            )
            
            edited_text = st.text_area(
                "Ajuste fino da minuta/relatório antes do registro no CRM:",
                value=latest_reply,
                height=250
            )

            if st.button("💾 Aprovar & Gravar no CRM", type="primary"):
                note_tag = f"[Radar · KAM Approved]"
                CRMConnector.add_note(
                    client_id=selected_client_id,
                    note_text=edited_text[:300] + "... [relatório completo aprovado via Copiloto KAM]",
                    tag=note_tag
                )
                CRMConnector.update_stage(selected_client_id, recommendation["recommended_stage"])
                st.balloons()
                st.success(f"🎉 Diagnóstico e notas aprovados com sucesso! Registrado no CRM para a conta {crm_data['company_name']}.")