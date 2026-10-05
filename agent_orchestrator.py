import os
from typing import Dict, Any, Optional

from engine.health_score import HealthScoreEngine
from engine.state_machine import StateMachineEngine
from connectors.crm_connector import CRMConnector
from connectors.support_connector import SupportConnector
from connectors.telemetry_connector import TelemetryConnector
from connectors.market_intelligence_connector import MarketIntelligenceConnector


class AgentOrchestrator:
    """
    Orquestrador central do CoreSaaS KAM.
    Carrega instruções, monta contextos e interfaceia a LLM com o Engine Python.
    """

    MAPPING_SKILL_FILES = {
        "kam-expansion-mapping": "skills/kam-expansion-mapping.md",
        "kam-churn-risk": "skills/kam-churn-risk.md",
        "kam-market-signals": "skills/kam-market-signals.md",
        "kam-value-cadence": "skills/kam-value-cadence.md",
        "kam-setup-processo": "skills/kam-setup-processo.md"
    }

    @classmethod
    def _read_file_safe(cls, filepath: str) -> str:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return f"[Aviso: Arquivo {filepath} não encontrado no repositório]"

    @classmethod
    def load_context(cls, client_id: str, target_stage_request: str = "E1") -> Dict[str, Any]:
        """
        Executa a coleta de dados e análise determinística, preparando o payload para a LLM.
        """
        # 1. Coleta de dados
        crm_data = CRMConnector.get_account_data(client_id)
        support_data = SupportConnector.get_support_data(client_id)
        telemetry_data = TelemetryConnector.get_telemetry_data(client_id)
        market_data = MarketIntelligenceConnector.get_market_signals(client_id)

        if not crm_data:
            raise ValueError(f"Cliente {client_id} não encontrado.")

        # 2. Avaliação Determinística
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

        # 3. Mapeamento da Skill a carregar
        action_text = recommendation["action"]
        active_skill = "kam-value-cadence"
        for skill_key in cls.MAPPING_SKILL_FILES.keys():
            if skill_key in action_text:
                active_skill = skill_key
                break

        # 4. Leitura dos prompts de instrução e skill
        system_instruction = cls._read_file_safe("instructions/core_kam_instruction.md")
        skill_instruction = cls._read_file_safe(cls.MAPPING_SKILL_FILES.get(active_skill, ""))

        return {
            "client_id": client_id,
            "company_name": crm_data["company_name"],
            "health_result": health_result,
            "recommendation": recommendation,
            "active_skill": active_skill,
            "system_instruction": system_instruction,
            "skill_instruction": skill_instruction,
            "raw_payloads": {
                "crm": crm_data,
                "support": support_data,
                "telemetry": telemetry_data,
                "market_intelligence": market_data
            }
        }

    @classmethod
    def build_llm_prompt(cls, context: Dict[str, Any]) -> str:
        """
        Gera a mensagem de usuário (User Prompt) formatada para ser enviada à LLM.
        """
        health = context["health_result"]
        rec = context["recommendation"]
        raw = context["raw_payloads"]

        prompt = f"""
### CONTEXTO DETERMINÍSTICO DO ENGINE PYTHON (DADOS INVIOLÁVEIS):
- Empresa: {context['company_name']} (ID: {context['client_id']})
- Health Score Calculado: {health['health_score']}/100 (Status: {health['status']})
- Subestado Recomendado: {rec['recommended_stage']} (Modo: {rec['mode']})
- Direcionamento do Engine: {rec['action']}
- Skill Ativada: {context['active_skill']}

### DADOS BRUTOS CONSOLIDADOS DOS CONECTORES:
1. B2B CRM Engine: {raw['crm']}
2. SupportDesk Engine: {raw['support']}
3. SaaS Telemetry API: {raw['telemetry']}
4. Market Intelligence Engine: {raw['market_intelligence']}

### TAREFA DA LLM:
Com base nas diretrizes da instrução do sistema e na skill ativada abaixo, gere o relatório completo de diagnóstico da conta e a minuta de comunicação adequada.

Lembre-se de aplicar estritamente as tags de proveniência de dados ao final das frases: [VALIDADO], [HIPÓTESE] ou [NÃO DITO].

---
### SKILL REQUERIDA PARA ESTE FLUXO:
{context['skill_instruction']}
"""
        return prompt