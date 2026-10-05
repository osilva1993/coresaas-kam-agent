from connectors.crm_connector import CRMConnector
from connectors.support_connector import SupportConnector
from connectors.telemetry_connector import TelemetryConnector
from connectors.market_intelligence_connector import MarketIntelligenceConnector

from engine.health_score import HealthScoreEngine
from engine.state_machine import StateMachineEngine


def run_pipeline_for_client(client_id: str, target_stage_request: str = "E1"):
    print(f"\n==================================================")
    print(f"🚀 INICIANDO PROCESSAMENTO: {client_id}")
    print(f"==================================================")

    # 1. Coleta de dados via Conectores Sandbox
    crm_data = CRMConnector.get_account_data(client_id)
    support_data = SupportConnector.get_support_data(client_id)
    telemetry_data = TelemetryConnector.get_telemetry_data(client_id)
    market_data = MarketIntelligenceConnector.get_market_signals(client_id)

    if not crm_data:
        print(f"❌ Cliente {client_id} não foi encontrado no CRM.")
        return

    print(f"Empresa: {crm_data['company_name']} | Estágio Atual: {crm_data['current_stage']}")

    # 2. Cálculo Determinístico do Health Score
    health_result = HealthScoreEngine.evaluate(
        telemetry=telemetry_data,
        support=support_data,
        crm_data=crm_data
    )

    print("\n[📊 DIAGNÓSTICO DE SAÚDE]")
    print(f"Nota Health Score: {health_result['health_score']}/100")
    print(f"Status Calculado:  {health_result['status']}")

    # 3. Análise da Máquina de Estados
    current_stage = crm_data["current_stage"]
    allowed, reason = StateMachineEngine.validate_transition(
        current_stage=current_stage,
        target_stage=target_stage_request,
        health_score_data=health_result,
        crm_data=crm_data
    )

    print(f"\n[🔒 VALIDAÇÃO DA MÁQUINA DE ESTADOS]")
    print(f"Tentativa de Transição: {current_stage} ➔ {target_stage_request}")
    print(f"Autorizado: {'✅ SIM' if allowed else '❌ NÃO'}")
    print(f"Motivo: {reason}")

    # 4. Decisão da Próxima Ação Recomendada
    has_expansion_trigger = any(
        s["category"] == "Gatilho de Expansão" for s in market_data.get("signals", [])
    ) if market_data else False

    recommendation = StateMachineEngine.resolve_recommended_stage(
        current_stage=current_stage,
        health_score_data=health_result,
        crm_data=crm_data,
        has_market_expansion_trigger=has_expansion_trigger
    )

    print(f"\n[🎯 RECOMENDAÇÃO DO AGENTE]")
    print(f"Estágio Recomendado: {recommendation['recommended_stage']} (Modo: {recommendation['mode']})")
    print(f"Ação: {recommendation['action']}")

    # 5. Teste de Escrita Idempotente de Nota no CRM
    note_content = (
        f"[Radar · auto] Health Score: {health_result['health_score']} ({health_result['status']}). "
        f"Ação: {recommendation['action']}"
    )
    write_result = CRMConnector.add_note(client_id, note_content, tag="[Radar · auto]")
    print(f"\n[📝 ESCRITA NO CRM]")
    print(f"Status da Gravação: {write_result['status']}")


if __name__ == "__main__":
    # Teste 1: Cliente Saudável com Sinal de Expansão (Deve liberar ou encaminhar para E1)
    run_pipeline_for_client("CLI-101", target_stage_request="E1")

    # Teste 2: Cliente em Risco com Bug Crítico e Troca de Executivo (Deve bloquear E1 e forçar O3)
    run_pipeline_for_client("CLI-202", target_stage_request="E1")

    from agent_orchestrator import AgentOrchestrator

# Teste de montagem de prompt para a LLM
context = AgentOrchestrator.load_context("CLI-202")
final_prompt = AgentOrchestrator.build_llm_prompt(context)

print("\n==================================================")
print("PROMPT GERADO PELO ORQUESTRADOR PARA ENVIO À LLM:")
print("==================================================")
print(final_prompt[:1000] + "\n\n... [resto do prompt oculto por brevidade] ...")

import os
from dotenv import load_dotenv

# Carrega as variáveis declaradas no arquivo .env para o ambiente Python
load_dotenv()

from connectors.crm_connector import CRMConnector
from connectors.support_connector import SupportConnector
from connectors.telemetry_connector import TelemetryConnector
from connectors.market_intelligence_connector import MarketIntelligenceConnector

from engine.health_score import HealthScoreEngine
from engine.state_machine import StateMachineEngine
from agent_orchestrator import AgentOrchestrator
from llm_client import LLMClient


def run_full_agent_execution(client_id: str):
    print(f"\n==================================================")
    print(f"🤖 EXECUTANDO AGENTE CORESAAS KAM (GROQ / openai/gpt-oss-120b): {client_id}")
    print(f"==================================================")

    context = AgentOrchestrator.load_context(client_id)
    user_prompt = AgentOrchestrator.build_llm_prompt(context)
    system_instruction = context["system_instruction"]

    print(f"Empresa: {context['company_name']}")
    print(f"Health Score: {context['health_result']['health_score']} ({context['health_result']['status']})")
    print(f"Skill Ativada: {context['active_skill']}")
    print("\n[⏳ SOLICITANDO RESPOSTA À GROQ...]")

    llm_response = LLMClient.generate_response(
        system_instruction=system_instruction,
        user_prompt=user_prompt
    )

    print("\n[📄 RESPOSTA GERADA PELO AGENTE]:")
    print("--------------------------------------------------")
    print(llm_response)
    print("--------------------------------------------------")


if __name__ == "__main__":
    run_full_agent_execution("CLI-202")