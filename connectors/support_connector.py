from typing import Dict, Any, Optional

class SupportConnector:
    """
    Conector Mock do SupportDesk Engine (Leitura Exclusiva GET).
    """

    MOCK_DB = {
        "CLI-101": {
            "client_id": "CLI-101",
            "open_tickets_count": 1,
            "critical_bugs_count": 0,
            "sla_breached_count": 0,
            "avg_resolution_time_hours": 4.5,
            "tickets_summary": [
                {"ticket_id": "T-101", "severity": "Baixa", "status": "Em Andamento", "subject": "Dúvida sobre relatório exportado"}
            ]
        },
        "CLI-202": {
            "client_id": "CLI-202",
            "open_tickets_count": 5,
            "critical_bugs_count": 2,
            "sla_breached_count": 1,
            "avg_resolution_time_hours": 36.0,
            "tickets_summary": [
                {"ticket_id": "T-204", "severity": "Alta", "status": "Aberto", "subject": "Falha na sincronização da API de faturamento"},
                {"ticket_id": "T-208", "severity": "Média", "status": "Em Andamento", "subject": "SLA estourado no módulo de Analytics"}
            ]
        }
    }

    @classmethod
    def get_support_data(cls, client_id: str) -> Optional[Dict[str, Any]]:
        return cls.MOCK_DB.get(client_id)