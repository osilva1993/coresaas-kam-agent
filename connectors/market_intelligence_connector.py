from typing import Dict, Any, Optional

class MarketIntelligenceConnector:
    """
    Conector Mock do Market Intelligence Engine (Coleta e Análise de Sinais Públicos).
    """

    MOCK_DB = {
        "CLI-101": {
            "client_id": "CLI-101",
            "company_name": "Acme Logistics S.A.",
            "signals_count": 1,
            "signals": [
                {
                    "signal_id": "SIG-901",
                    "category": "Gatilho de Expansão",
                    "headline": "Acme Logistics capta R$ 35 Milhões em rodada Série B para expandir filiais",
                    "source_url": "https://noticias.exemplo.com/acme-serie-b",
                    "event_date": "2026-09-30",
                    "confidence_score": 0.95
                }
            ]
        },
        "CLI-202": {
            "client_id": "CLI-202",
            "company_name": "TechPay Finanças",
            "signals_count": 1,
            "signals": [
                {
                    "signal_id": "SIG-402",
                    "category": "Risco Relacional",
                    "headline": "TechPay anuncia novo VP de Tecnologia vindo da concorrente StackX",
                    "source_url": "https://linkedin.com/news/techpay-new-vp",
                    "event_date": "2026-10-01",
                    "confidence_score": 0.92
                }
            ]
        }
    }

    @classmethod
    def get_market_signals(cls, client_id: str) -> Optional[Dict[str, Any]]:
        return cls.MOCK_DB.get(client_id)