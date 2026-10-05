from typing import Dict, Any, Optional
from datetime import datetime

class CRMConnector:
    """
    Conector Mock do B2B CRM Engine.
    Simula leitura e escrita de dados cadastrais, notas e estágios de pipeline.
    """

    MOCK_DB = {
        "CLI-101": {
            "deal_id": "DEAL-8891",
            "company_name": "Acme Logistics S.A.",
            "mrr": 25000.0,
            "contract_renewal_date": "2026-12-15",
            "owner_kam": "Carlos Andrade",
            "current_stage": "O1",
            "cadastre_complete": True,
            "days_since_last_contact": 10,
            "has_active_sponsor": True,
            "adimplente": True,
            "days_to_renewal": 72,
            "renewal_in_progress": False,
            "has_unresolved_critical_bugs": False,
            "active_modules": ["Core", "Logistics", "Billing"],
            "notes_history": []
        },
        "CLI-202": {
            "deal_id": "DEAL-4412",
            "company_name": "TechPay Finanças",
            "mrr": 40000.0,
            "contract_renewal_date": "2026-11-01",
            "owner_kam": "Mariana Costa",
            "current_stage": "O1",
            "cadastre_complete": True,
            "days_since_last_contact": 45,
            "has_active_sponsor": False,
            "adimplente": True,
            "days_to_renewal": 27,
            "renewal_in_progress": False,
            "has_unresolved_critical_bugs": True,
            "active_modules": ["Core", "Analytics"],
            "notes_history": []
        }
    }

    @classmethod
    def get_account_data(cls, client_id: str) -> Optional[Dict[str, Any]]:
        """Lê os dados da conta no CRM."""
        return cls.MOCK_DB.get(client_id)

    @classmethod
    def add_note(cls, client_id: str, note_text: str, tag: str = "[Radar · auto]") -> Dict[str, Any]:
        """
        Registra nota de forma idempotente. Evita duplicatas com a mesma tag no mesmo dia.
        """
        account = cls.get_account_data(client_id)
        if not account:
            return {"success": False, "error": f"Cliente {client_id} não encontrado."}

        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Checagem de idempotência
        for note in account["notes_history"]:
            if note["tag"] == tag and note["date"] == today_str:
                return {
                    "success": True,
                    "status": "SKIPPED",
                    "message": f"Nota com a tag '{tag}' já registrada para o dia {today_str}."
                }

        new_entry = {
            "date": today_str,
            "tag": tag,
            "content": note_text
        }
        account["notes_history"].append(new_entry)
        return {"success": True, "status": "CREATED", "note": new_entry}

    @classmethod
    def update_stage(cls, client_id: str, new_stage: str) -> Dict[str, Any]:
        """Atualiza o estágio do pipeline da conta."""
        account = cls.get_account_data(client_id)
        if not account:
            return {"success": False, "error": f"Cliente {client_id} não encontrado."}
        
        old_stage = account["current_stage"]
        account["current_stage"] = new_stage
        return {
            "success": True,
            "old_stage": old_stage,
            "new_stage": new_stage
        }