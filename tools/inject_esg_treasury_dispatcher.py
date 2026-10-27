# -*- coding: utf-8 -*-
"""
Injects esg_governance and treasury_working_capital into app/services/action_dispatcher.py.
"""

SCHEMAS_HOOK = '''    {
        "name": "esg_governance",
        "description": "Gobierno Corporativo & Sostenibilidad ESG: Evaluaciones Ambientales (E), Sociales (S) y Gobernanza (G) bajo estándares IFRS S1/S2 y GRI, calificación compuesta (AAA a CCC) y plan de acción de descarbonización y ética corporativa.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "company_name": {"type": "STRING", "description": "Nombre de la empresa"},
                "environmental_score": {"type": "NUMBER", "description": "Puntaje Ambiental (0 a 100)"},
                "social_score": {"type": "NUMBER", "description": "Puntaje Social (0 a 100)"},
                "governance_score": {"type": "NUMBER", "description": "Puntaje Gobernanza (0 a 100)"},
                "sector": {"type": "STRING", "description": "Sector económico"}
            },
            "required": []
        }
    },
    {
        "name": "treasury_working_capital",
        "description": "Tesorería Corporativa, Capital de Trabajo (KTNO) y Factoring: Ciclo de Conversión de Efectivo (CCC = DSO + DIO - DPO), liquidez atrapada y simulador de descuento de facturas electrónicas (RADIAN / DIAN) con Tasa Efectiva Anual (E.A.).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action_type": {"type": "STRING", "description": "ccc | factoring"},
                "dso_receivables_days": {"type": "NUMBER", "description": "Días de cobro a clientes (DSO)"},
                "dio_inventory_days": {"type": "NUMBER", "description": "Días de rotación de inventarios (DIO)"},
                "dpo_payables_days": {"type": "NUMBER", "description": "Días de pago a proveedores (DPO)"},
                "invoice_face_value_cop": {"type": "NUMBER", "description": "Valor nominal de factura en factoring"},
                "days_to_maturity": {"type": "INTEGER", "description": "Días restantes para el vencimiento de la factura"}
            },
            "required": []
        }
    },
'''

DISPATCH_HOOK = '''            elif name in ("esg_governance", "sostenibilidad_esg", "gobierno_corporativo", "esg_score"):
                from app.actions.esg_governance_action import esg_governance_action
                res = esg_governance_action(parameters=args)
                return res

            elif name in ("treasury_working_capital", "capital_trabajo", "ktno", "ciclo_efectivo", "ccc", "factoring", "radian"):
                from app.actions.treasury_working_capital_action import treasury_working_capital_action
                res = treasury_working_capital_action(parameters=args)
                return res
'''

def main():
    path = "app/services/action_dispatcher.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Inject schema declarations right before forex_radar
    target_schema = '    {\n        "name": "forex_radar",'
    if target_schema in content and '"name": "esg_governance"' not in content:
        content = content.replace(target_schema, SCHEMAS_HOOK + target_schema)
        print("[SUCCESS] Schemas ESG y Treasury inyectados")

    # 2. Inject dispatch execution right after forex_radar execution
    target_exec = '            elif name in ("forex_radar", "radar_cambiario", "trm_colombia", "dolar_colombia", "forward_hedging", "cobertura_divisas"):\n                from app.actions.forex_radar_action import forex_radar_action\n                res = forex_radar_action(parameters=args)\n                return res\n'
    if target_exec in content and '"esg_governance"' not in content:
        content = content.replace(target_exec, target_exec + "\n" + DISPATCH_HOOK)
        print("[SUCCESS] Dispatch execution ESG y Treasury inyectada")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[SUCCESS] Guardado action_dispatcher.py")

if __name__ == "__main__":
    main()
