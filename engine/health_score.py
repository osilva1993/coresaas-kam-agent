from typing import Dict, Any, Optional, Tuple

class HealthScoreEngine:
    """
    Motor determinístico para cálculo do Health Score proporcional da carteira CoreSaaS.
    Isola a lógica matemática da LLM, reponderando dinamicamente pilares ausentes.
    """
    
    BASE_WEIGHTS = {
        "uso": 0.35,
        "suporte": 0.25,
        "relacionamento": 0.20,
        "financeiro": 0.20
    }

    @classmethod
    def calculate_pillar_uso(cls, telemetry: Optional[Dict[str, Any]]) -> Optional[float]:
        if not telemetry:
            return None
        
        adoption = telemetry.get("feature_adoption_rate", 0)  # 0 a 100
        mau_var = telemetry.get("mau_variation_percentage", 0)  # variação %
        
        # Cálculo sintético do pilar de uso
        score_mau = min(max((mau_var + 50) * 1.0, 0), 100)
        score_uso = (adoption * 0.6) + (score_mau * 0.4)
        return round(min(max(score_uso, 0.0), 100.0), 2)

    @classmethod
    def calculate_pillar_suporte(cls, support: Optional[Dict[str, Any]]) -> Optional[float]:
        if not support:
            return None
        
        critical_bugs = support.get("critical_bugs_count", 0)
        sla_breached = support.get("sla_breached_count", 0)
        open_tickets = support.get("open_tickets_count", 0)

        # Penalidades por atrito técnico
        penalty = (critical_bugs * 35) + (sla_breached * 25) + (open_tickets * 5)
        score_suporte = 100.0 - penalty
        return round(min(max(score_suporte, 0.0), 100.0), 2)

    @classmethod
    def calculate_pillar_relacionamento(cls, crm_data: Optional[Dict[str, Any]]) -> Optional[float]:
        if not crm_data or "days_since_last_contact" not in crm_data:
            return None
        
        days = crm_data["days_since_last_contact"]
        has_sponsor = crm_data.get("has_active_sponsor", True)
        
        if days <= 15:
            score_days = 100.0
        elif days <= 30:
            score_days = 70.0
        elif days <= 60:
            score_days = 40.0
        else:
            score_days = 0.0

        if not has_sponsor:
            score_days *= 0.5  # Penalidade se perdeu o sponsor principal

        return round(score_days, 2)

    @classmethod
    def calculate_pillar_financeiro(cls, crm_data: Optional[Dict[str, Any]]) -> Optional[float]:
        if not crm_data or "adimplente" not in crm_data:
            return None
        
        is_adimplente = crm_data.get("adimplente", True)
        days_to_renewal = crm_data.get("days_to_renewal", 365)
        
        if not is_adimplente:
            return 0.0
        
        # Se renovação está próxima (<30 dias) e sem tratativa
        if days_to_renewal < 30 and not crm_data.get("renewal_in_progress", False):
            return 50.0
            
        return 100.0

    @classmethod
    def evaluate(
        cls,
        telemetry: Optional[Dict[str, Any]] = None,
        support: Optional[Dict[str, Any]] = None,
        crm_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calcula o Health Score consolidado utilizando apenas os pilares disponíveis.
        Formula: Sum(Score_i * Weight_i) / Sum(Weight_i)
        """
        pillars = {
            "uso": cls.calculate_pillar_uso(telemetry),
            "suporte": cls.calculate_pillar_suporte(support),
            "relacionamento": cls.calculate_pillar_relacionamento(crm_data),
            "financeiro": cls.calculate_pillar_financeiro(crm_data)
        }

        weighted_sum = 0.0
        weight_sum = 0.0
        pillars_breakdown = {}

        for pillar_name, score in pillars.items():
            if score is not None:
                weight = cls.BASE_WEIGHTS[pillar_name]
                weighted_sum += score * weight
                weight_sum += weight
                pillars_breakdown[pillar_name] = {
                    "score": score,
                    "weight": weight,
                    "status": "VALIDADO"
                }
            else:
                pillars_breakdown[pillar_name] = {
                    "score": None,
                    "weight": cls.BASE_WEIGHTS[pillar_name],
                    "status": "NÃO DITO"
                }

        if weight_sum == 0.0:
            return {
                "health_score": None,
                "status": "DESCONHECIDO",
                "pillars": pillars_breakdown,
                "error": "Nenhum pilar contendo dados válidos para cálculo."
            }

        final_score = round(weighted_sum / weight_sum, 2)

        if final_score >= 80.0:
            health_status = "VERDE"
        elif final_score >= 60.0:
            health_status = "AMARELO"
        else:
            health_status = "VERMELHO"

        return {
            "health_score": final_score,
            "status": health_status,
            "available_weight_ratio": round(weight_sum, 2),
            "pillars": pillars_breakdown
        }