import html as _h
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from connectors.crm_connector import CRMConnector
from connectors.support_connector import SupportConnector
from connectors.telemetry_connector import TelemetryConnector
from connectors.market_intelligence_connector import MarketIntelligenceConnector
from engine.health_score import HealthScoreEngine
from engine.state_machine import StateMachineEngine
from agent_orchestrator import AgentOrchestrator
from llm_client import LLMClient

st.set_page_config(
    page_title="CoreSaaS KAM · Cockpit de contas",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

NOTE_MAX_CHARS = 300
NOTE_TAG = "[Radar · KAM Approved]"
CLIENTS = {
    "CLI-101": "Acme Logistics S.A.",
    "CLI-202": "TechPay Finanças",
}
# status do engine -> (rótulo, classe CSS, título do banner)
STATUS = {
    "VERDE": ("Saudável", "ok", "Avanço autorizado"),
    "AMARELO": ("Atenção", "warn", "Atenção necessária"),
    "VERMELHO": ("Risco crítico", "risk", "Avanço bloqueado"),
}
PILLAR_LABELS = {"telemetry": "Telemetria", "support": "Suporte", "crm": "Relacionamento (CRM)"}

# ---------------------------------------------------------
# DESIGN SYSTEM
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');
:root{--ink:#1B2430;--muted:#5B6675;--line:#E2E6EC;--bg:#F5F6F8;--card:#FFFFFF;--brand:#0F5C6E;
--ok:#1E7F5C;--okbg:#E6F4EE;--warn:#8A5A00;--warnbg:#FFF3D1;--risk:#B42318;--riskbg:#FDE8E6}
html,body,[class*="css"],.stApp{font-family:'IBM Plex Sans',system-ui,sans-serif;color:var(--ink)}
.stApp{background:var(--bg)}
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none}
.block-container{padding:2rem 2.5rem 4rem;max-width:1360px}
[data-testid="stSidebar"]{background:var(--card);border-right:1px solid var(--line)}
h1,h2,h3,h4{letter-spacing:-.01em;color:var(--ink)}
.stTabs [data-baseweb="tab-list"]{gap:1.5rem;border-bottom:1px solid var(--line)}
.stTabs [data-baseweb="tab"]{padding:.6rem 0;font-weight:500;color:var(--muted)}
.stTabs [aria-selected="true"]{color:var(--brand)}
.stTabs [data-baseweb="tab-highlight"]{background:var(--brand)}
[data-testid="stMetric"]{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:1rem 1.1rem}
[data-testid="stMetricLabel"]{color:var(--muted);font-size:.85rem}
[data-testid="stMetricValue"]{font-variant-numeric:tabular-nums;font-weight:600;font-size:1.6rem}
.stButton>button[kind="primary"]{background:var(--brand);border:0;border-radius:6px;font-weight:500}
.stButton>button:focus-visible,.stTextArea textarea:focus{outline:2px solid var(--brand);outline-offset:2px}
.hdr{display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;margin-bottom:1.25rem}
.hdr h1{margin:0;font-size:1.75rem;font-weight:600}
.hdr p{margin:.25rem 0 0;color:var(--muted);font-size:.9rem}
.pill{display:inline-flex;align-items:center;gap:.4rem;padding:.2rem .65rem;border-radius:999px;font-size:.8rem;font-weight:500}
.pill::before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor}
.pill.ok{background:var(--okbg);color:var(--ok)}.pill.warn{background:var(--warnbg);color:var(--warn)}
.pill.risk{background:var(--riskbg);color:var(--risk)}.pill.idle{background:var(--bg);color:var(--muted)}
.banner{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--muted);border-radius:8px;
padding:1rem 1.25rem;margin:1.25rem 0;display:flex;justify-content:space-between;gap:2rem;flex-wrap:wrap}
.banner.ok{border-left-color:var(--ok)}.banner.warn{border-left-color:var(--warn)}.banner.risk{border-left-color:var(--risk)}
.banner b{display:block;margin-bottom:.15rem}.banner span{color:var(--muted);font-size:.92rem}
.flow{display:flex;align-items:center;gap:.6rem;font-size:.9rem;white-space:nowrap}
.flow i{font-style:normal;color:var(--muted)}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:1.1rem 1.25rem;margin-bottom:1rem}
.card-h{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:.5rem}
.card-h h4{margin:0;font-size:1rem;font-weight:600}.card-h span{color:var(--muted);font-size:.8rem}
.kv{display:flex;justify-content:space-between;gap:1rem;padding:.5rem 0;border-top:1px solid var(--line);font-size:.92rem}
.kv span{color:var(--muted)}.kv b{font-weight:500;text-align:right;font-variant-numeric:tabular-nums}
.sig{padding:.7rem 0;border-top:1px solid var(--line);font-size:.92rem}
.sig small{display:block;color:var(--muted);margin-top:.2rem}
.prow{display:grid;grid-template-columns:200px 1fr 90px 120px;gap:1rem;align-items:center;padding:.75rem 0;border-top:1px solid var(--line);font-size:.92rem}
.prow small{display:block;color:var(--muted)}
.bar{height:8px;background:var(--bg);border-radius:4px;overflow:hidden}.bar>div{height:100%;border-radius:4px}
.bar .ok{background:var(--ok)}.bar .warn{background:#C98A00}.bar .risk{background:var(--risk)}
.conn{display:flex;justify-content:space-between;align-items:center;padding:.4rem 0;font-size:.88rem}
.conn small{color:var(--muted);display:block}
@media(max-width:800px){.block-container{padding:1rem}.prow{grid-template-columns:1fr}.flow{white-space:normal}}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def md(markup: str):
    st.markdown(markup, unsafe_allow_html=True)


def esc(v) -> str:
    return _h.escape(str(v))


def pill(label: str, kind: str) -> str:
    return f'<span class="pill {kind}">{esc(label)}</span>'


def brl(v) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def kv(rows) -> str:
    return "".join(f'<div class="kv"><span>{esc(k)}</span><b>{v}</b></div>' for k, v in rows)


def card(title: str, source: str, body: str) -> str:
    return f'<div class="card"><div class="card-h"><h4>{esc(title)}</h4><span>{esc(source)}</span></div>{body}</div>'


def yes_no(cond, yes: str, no: str, bad_when_no=True) -> str:
    return pill(yes, "ok") if cond else pill(no, "risk" if bad_when_no else "warn")


# ---------------------------------------------------------
# SIDEBAR - CONTA
# ---------------------------------------------------------
st.sidebar.markdown("### CoreSaaS KAM")
st.sidebar.caption("Cockpit de governança de contas")
client_id = st.sidebar.selectbox(
    "Conta",
    options=list(CLIENTS.keys()),
    format_func=lambda x: f"{CLIENTS[x]} ({x})",
)

# ---------------------------------------------------------
# DADOS E ENGINES
# ---------------------------------------------------------
crm = CRMConnector.get_account_data(client_id)
support = SupportConnector.get_support_data(client_id)
telemetry = TelemetryConnector.get_telemetry_data(client_id)
market = MarketIntelligenceConnector.get_market_signals(client_id) or {}

st.sidebar.divider()
st.sidebar.markdown("**Fontes de dados**")
for name, origin, payload in [
    ("CRM", "Salesforce / HubSpot", crm),
    ("Suporte", "Zendesk / Freshdesk", support),
    ("Telemetria", "PostHog / Mixpanel", telemetry),
    ("Mercado", "Web e notícias", market),
]:
    st.sidebar.markdown(
        f'<div class="conn"><div>{esc(name)}<small>{esc(origin)}</small></div>'
        f'{pill("Conectado", "ok") if payload else pill("Sem dados", "risk")}</div>',
        unsafe_allow_html=True,
    )
st.sidebar.caption("v1.2.0 · Engine determinístico + Groq")

if not crm:
    st.error(f"A conta {client_id} não foi encontrada no CRM. Verifique o ID ou a conexão com o CRM.")
    st.stop()

health = HealthScoreEngine.evaluate(telemetry=telemetry, support=support, crm_data=crm)
has_expansion = any(s["category"] == "Gatilho de Expansão" for s in market.get("signals", []))
reco = StateMachineEngine.resolve_recommended_stage(
    current_stage=crm["current_stage"],
    health_score_data=health,
    crm_data=crm,
    has_market_expansion_trigger=has_expansion,
)

score = health["score"] if "score" in health else health["health_score"]
label, kind, banner_title = STATUS.get(health["status"], STATUS["AMARELO"])

# ---------------------------------------------------------
# CABEÇALHO, DECISÃO E KPIs
# ---------------------------------------------------------
md(
    f'<div class="hdr"><div><h1>{esc(crm["company_name"])}</h1>'
    f'<p>{esc(client_id)} · KAM responsável: {esc(crm.get("owner_kam", "N/A"))}</p></div>'
    f'{pill(label, kind)}</div>'
)

md(
    f'<div class="banner {kind}"><div><b>{banner_title}</b><span>{esc(reco["action"])}</span></div>'
    f'<div class="flow">{pill(crm["current_stage"], "idle")}<i>→</i>'
    f'{pill(reco["recommended_stage"], kind)}<i>{esc(reco["mode"])}</i></div></div>'
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("MRR", brl(crm.get("mrr", 0)))
k2.metric("Health score", f"{score:.1f} / 100")
k3.metric("Renovação em", f"{crm.get('days_to_renewal', 0)} dias")
k4.metric("Módulos ativos", len(crm.get("active_modules", [])))

st.write("")
tab_overview, tab_health, tab_copilot = st.tabs(["Resumo da conta", "Health score", "Copiloto e aprovação"])

# ---------------------------------------------------------
# TAB 1 - RESUMO
# ---------------------------------------------------------
with tab_overview:
    left, right = st.columns(2, gap="medium")
    with left:
        md(card("Relacionamento", "CRM", kv([
            ("Oportunidade", esc(crm.get("deal_id", "N/A"))),
            ("Último contato", f"{crm.get('days_since_last_contact', 0)} dias atrás"),
            ("Adimplência", yes_no(crm.get("adimplente"), "Regular", "Inadimplente")),
            ("Patrocinador ativo", yes_no(crm.get("has_active_sponsor"), "Identificado", "Não identificado", False)),
            ("Módulos", esc(", ".join(crm.get("active_modules", [])) or "Nenhum")),
        ])))
        md(card("Uso do produto", "Telemetria", kv([
            ("Usuários ativos (MAU)", telemetry.get("mau", 0)),
            ("Engajamento mês a mês", f"{telemetry.get('engagement_trend_pct', 0)}%"),
            ("Adoção de features", f"{telemetry.get('feature_adoption_rate', 0)}%"),
            ("Frequência de uso", esc(telemetry.get("usage_frequency", "N/A"))),
        ])))
    with right:
        md(card("Suporte", "Service desk", kv([
            ("Tickets abertos", support.get("open_tickets_count", 0)),
            ("Tickets críticos", support.get("critical_tickets_count", 0)),
            ("Violações de SLA (30 dias)", support.get("sla_violations_last_30d", 0)),
            ("Tempo médio de resolução", f"{support.get('avg_resolution_time_hours', 0)} h"),
            ("Bugs críticos em aberto", yes_no(not crm.get("has_unresolved_critical_bugs"), "Nenhum", "Em aberto")),
        ])))
        signals = market.get("signals", [])
        body = "".join(
            f'<div class="sig">{pill(s["category"], "warn")} {esc(s["headline"])}'
            f'<small>{esc(s["event_date"])} · confiança {s["confidence_score"] * 100:.0f}%</small></div>'
            for s in signals
        ) or '<div class="sig"><small>Nenhum sinal de mercado relevante para esta conta nos últimos dias.</small></div>'
        md(card("Sinais de mercado", "Inteligência externa", body))

# ---------------------------------------------------------
# TAB 2 - HEALTH SCORE
# ---------------------------------------------------------
with tab_health:
    st.caption("Fórmula ponderada: telemetria 40% + suporte 30% + relacionamento 30%.")
    rows = ""
    pillars = health.get("pillars", {})
    for name, p in pillars.items():
        p_label, p_kind, _ = STATUS.get(p.get("status"), STATUS["AMARELO"])
        p_score = p.get("score", 0)
        rows += (
            f'<div class="prow"><div>{esc(PILLAR_LABELS.get(name, name.title()))}'
            f'<small>Peso {p.get("weight", 0) * 100:.0f}%</small></div>'
            f'<div class="bar"><div class="{p_kind}" style="width:{max(0, min(p_score, 100))}%"></div></div>'
            f'<b>{p_score:.1f}</b>{pill(p_label, p_kind)}</div>'
        )
    md(card("Composição do score", f"Total {score:.1f} / 100", rows))
    for name, p in pillars.items():
        if p.get("details"):
            with st.expander(f"Sub-indicadores · {PILLAR_LABELS.get(name, name.title())}"):
                md(kv([(k, f"<code>{esc(v)}</code>") for k, v in p["details"].items()]))

# ---------------------------------------------------------
# TAB 3 - COPILOTO + HUMAN-IN-THE-LOOP (estado isolado por conta)
# ---------------------------------------------------------
draft_key, edit_key, ok_key = f"draft_{client_id}", f"edit_{client_id}", f"confirm_{client_id}"
done_key, err_key = f"done_{client_id}", f"error_{client_id}"


def approve(cid: str, stage: str):
    try:
        text = st.session_state[f"edit_{cid}"]
        CRMConnector.add_note(
            client_id=cid,
            note_text=text[:NOTE_MAX_CHARS] + "... [relatório completo aprovado pelo KAM]",
            tag=NOTE_TAG,
        )
        CRMConnector.update_stage(cid, stage)
        for k in (f"draft_{cid}", f"edit_{cid}", f"confirm_{cid}", f"error_{cid}"):
            st.session_state.pop(k, None)
        st.session_state[f"done_{cid}"] = stage
    except Exception as exc:
        st.session_state[f"error_{cid}"] = str(exc)


def discard(cid: str):
    for k in (f"draft_{cid}", f"edit_{cid}", f"confirm_{cid}"):
        st.session_state.pop(k, None)


with tab_copilot:
    st.caption("A IA propõe o diagnóstico dentro das travas do engine. Nada é gravado no CRM sem a sua aprovação.")

    if st.session_state.get(done_key):
        st.success(f"Diagnóstico aprovado. Nota registrada e estágio atualizado para {st.session_state.pop(done_key)}.")
    if st.session_state.get(err_key):
        st.error(f"Não foi possível gravar no CRM: {st.session_state[err_key]}. Tente novamente ou registre manualmente.")

    md(card("Ação recomendada pelo engine", "Skill requerida", f'<div class="sig">{esc(reco["action"])}</div>'))

    if st.button("Gerar diagnóstico e minuta", type="primary", disabled=draft_key in st.session_state):
        with st.spinner("Compilando dados da conta e gerando a minuta…"):
            try:
                ctx = AgentOrchestrator.load_context(client_id)
                resp = LLMClient.generate_response(
                    system_instruction=ctx["system_instruction"],
                    user_prompt=AgentOrchestrator.build_llm_prompt(ctx),
                )
                st.session_state[draft_key] = resp
                st.session_state[edit_key] = resp
            except Exception as exc:
                st.error(f"Falha ao gerar a minuta: {exc}. Verifique a chave do modelo e tente novamente.")

    if draft_key in st.session_state:
        st.text_area("Minuta (editável antes da aprovação)", key=edit_key, height=420)
        md(
            f'<div class="flow">Ao aprovar: {pill(crm["current_stage"], "idle")}<i>→</i>'
            f'{pill(reco["recommended_stage"], kind)}</div>'
        )
        st.checkbox("Revisei a minuta e confirmo a gravação no CRM.", key=ok_key)
        a, b, _ = st.columns([2, 2, 5])
        a.button(
            "Aprovar e gravar no CRM",
            type="primary",
            disabled=not st.session_state.get(ok_key),
            on_click=approve,
            args=(client_id, reco["recommended_stage"]),
        )
        b.button("Descartar minuta", on_click=discard, args=(client_id,))
