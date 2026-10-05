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
st.sidebar.title("🛡️️ CoreSaaS KAM")
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

    # Grid de Cards dos Conectores (2x2)
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

# --- TAB 3: COPILOTO IA & HUMAN IN THE LOOP ---
with tab_agent:
    st.subheader("🤖 Agente Copiloto KAM & Fluxo Human-in-the-Loop")
    st.caption("A IA gera a proposta estratégica baseando-se estritamente nas travas determinísticas. Você revisa e aprova antes de qualquer escrita no CRM.")

    st.info(f"🎯 **Skill Requerida Identificada pelo Engine:** `{recommendation['action']}`")

    if st.button("🚀 Gerar Diagnóstico & Minuta com IA", type="primary", use_container_width=True):
        with st.spinner("Conectando ao modelo Groq (openai/gpt-oss-120b) e compilando dados..."):
            context = AgentOrchestrator.load_context(selected_client_id)
            user_prompt = AgentOrchestrator.build_llm_prompt(context)
            system_instruction = context["system_instruction"]

            llm_response = LLMClient.generate_response(
                system_instruction=system_instruction,
                user_prompt=user_prompt
            )
            st.session_state["llm_response"] = llm_response

    if "llm_response" in st.session_state:
        st.markdown("---")
        st.markdown("#### ✏️ Minuta do Diagnóstico & Plano de Ação (Ajustável pelo KAM):")
        
        edited_response = st.text_area(
            "Edite o conteúdo abaixo caso queira ajustar alguma informação antes de registrar no CRM:",
            value=st.session_state["llm_response"],
            height=450
        )

        col_approve, col_reject = st.columns([1, 4])
        with col_approve:
            if st.button("✅ Aprovar & Registrar no CRM", type="primary"):
                note_tag = f"[Radar · KAM Approved]"
                CRMConnector.add_note(
                    client_id=selected_client_id,
                    note_text=edited_response[:300] + "... [relatório completo aprovado pelo KAM]",
                    tag=note_tag
                )
                CRMConnector.update_stage(selected_client_id, recommendation["recommended_stage"])
                st.balloons()
                st.success("🎉 Diagnóstico aprovado com sucesso! Alteração de estágio e nota registradas no CRM.")