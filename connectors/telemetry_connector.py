from typing import Dict, Any, Optional

class TelemetryConnector:
    """
    Conector Mock da SaaS Telemetry API (Métricas de Adoção e Uso do Produto).
    """

    MOCK_DB = {
        "CLI-101": {
            "client_id": "CLI-101",
            "monthly_active_users": 142,
            "mau_variation_percentage": 15.5,
            "last_login_date": "2026-10-04",
            "feature_adoption_rate": 88.0
        },
        "CLI-202": {
            "client_id": "CLI-202",
            "monthly_active_users": 38,
            "mau_variation_percentage": -42.0,
            "last_login_date": "2026-09-28",
            "feature_adoption_rate": 32.5
        }
    }

    @classmethod
    def get_telemetry_data(cls, client_id: str) -> Optional[Dict[str, Any]]:
        return cls.MOCK_DB.get(client_id)