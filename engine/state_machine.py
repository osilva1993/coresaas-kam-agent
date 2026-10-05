from typing import Dict, Any, Tuple

class StateMachineEngine:
    """
    Validador rígido de transições de estado da carteira (Hard-Lock Engine).
    Impede que a LLM avance estágios no CRM sem satisfazer critérios de negócio.
    """

    VALID_STAGES = [
        "S1", "S2", "S3", "S4",  # MODO SETUP
        "O1", "O2", "O3", "O4",  # MODO OPERAÇÃO
        "E1", "E2", "E3", "E4"   # MODO EXPANSÃO
    ]

    STAGE_MODES = {
        "S1": "SETUP", "S2": "SETUP", "S3": "SETUP", "S4": "SETUP",
        "O1": "OPERAÇÃO", "O2": "OPERAÇÃO", "O3": "OPERAÇÃO", "O4": "OPERAÇÃO",
        "E1": "EXPANSÃO", "E2": "EXPANSÃO", "E3": "EXPANSÃO", "E4": "EXPANSÃO"
    }

    @classmethod
    def validate_transition(
        cls,
        current_stage: str,
        target_stage: str,
        health_score_data: Dict[str, Any],
        crm_data: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Valida se a transição entre current_stage e target_stage é permitida.
        Retorna (True, "OK") ou (False, "Motivo do bloqueio").
        """
        if target_stage not in cls.VALID_STAGES:
            return False, f"Estágio destino inválido: {target_stage}"

        health_score = health_score_data.get("health_score")
        health_status = health_score_data.get("status")

        # Regra 1: Saída do MODO SETUP para OPERAÇÃO (Transição S4 -> O1)
        if current_stage.startswith("S") and target_stage.startswith("O"):
            if not crm_data.get("cadastre_complete", False):
                return False, "Bloqueio SETUP: Cadastro mestre incompleto (Requer S2 saneado)."
            if health_score is None:
                return False, "Bloqueio SETUP: Baseline de Health Score não calculado (Requer S4)."

        # Regra 2: Entrada no MODO EXPANSÃO (O1-O4 -> E1-E4)
        if target_stage.startswith("E"):
            if health_score is None or health_score < 80.0 or health_status != "VERDE":
                return False, (
                    f"Bloqueio de Expansão: Health Score atual é {health_score} ({health_status}). "
                    "Expansão exige Health Score Verde (>= 80.0)."
                )
            if crm_data.get("has_unresolved_critical_bugs", False):
                return False, "Bloqueio de Expansão: Existem chamados de bugs críticos abertos no SupportDesk."

        # Regra 3: Redirecionamento obrigatório para Gestão de Risco (O3 - Churn Risk)
        if health_status in ["AMARELO", "VERMELHO"] and target_stage.startswith("E"):
            return False, (
                f"Conta em Risco ({health_status}). Requer execução prioritária do playbook de retenção (Subestado O3)."
            )

        return True, "Transição autorizada."

    @classmethod
    def resolve_recommended_stage(
        cls,
        current_stage: str,
        health_score_data: Dict[str, Any],
        crm_data: Dict[str, Any],
        has_market_expansion_trigger: bool = False
    ) -> Dict[str, Any]:
        """
        Determina deterministicamente o estágio ideal para o qual a conta deve ir.
        """
        health_status = health_score_data.get("status")
        health_score = health_score_data.get("health_score")

        # Se cadastro estiver incompleto, força MODO SETUP (S2)
        if not crm_data.get("cadastre_complete", False):
            return {
                "recommended_stage": "S2",
                "mode": "SETUP",
                "action": "Sanear cadastro mestre no B2B CRM Engine."
            }

        # Se em Risco (Amarelo/Vermelho), força Gestão de Churn Risk (O3)
        if health_status in ["AMARELO", "VERMELHO"]:
            return {
                "recommended_stage": "O3",
                "mode": "OPERAÇÃO",
                "action": f"Acionar Playbook de Churn Risk (Skill: kam-churn-risk). Health Score: {health_score}."
            }

        # Se Verde com gatilho de mercado/telemetria confirmado e na fase de Operação
        if health_status == "VERDE" and has_market_expansion_trigger and current_stage.startswith("O"):
            return {
                "recommended_stage": "E1",
                "mode": "EXPANSÃO",
                "action": "Acionar Mapeamento de Oportunidade (Skill: kam-expansion-mapping)."
            }

        # Manutenção de rotina
        return {
            "recommended_stage": current_stage if current_stage.startswith("O") else "O1",
            "mode": cls.STAGE_MODES.get(current_stage, "OPERAÇÃO"),
            "action": "Manter cadência regular de acompanhamento (Skill: kam-value-cadence)."
        }