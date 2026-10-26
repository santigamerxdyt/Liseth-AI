# -*- coding: utf-8 -*-
"""
Injects marketing_growth, talent_management, and forex_radar into app/services/action_dispatcher.py
"""

DISPATCH_HOOK = '''            elif name in ("marketing_growth", "saas_metrics", "unit_economics", "cac_ltv", "embudo_ventas", "roas"):
                from app.actions.marketing_growth_action import marketing_growth_action
                res = marketing_growth_action(parameters=args)
                return res

            elif name in ("talent_management", "matriz_9box", "nine_box", "clima_laboral", "enps", "rotacion_personal"):
                from app.actions.talent_management_action import talent_management_action
                res = talent_management_action(parameters=args)
                return res

            elif name in ("forex_radar", "radar_cambiario", "trm_colombia", "dolar_colombia", "forward_hedging", "cobertura_divisas"):
                from app.actions.forex_radar_action import forex_radar_action
                res = forex_radar_action(parameters=args)
                return res
'''

SCHEMAS_HOOK = '''    {
        "name": "marketing_growth",
        "description": "Motor de Crecimiento & Unit Economics 360: CAC, LTV, ratio LTV/CAC, Payback, Churn mensual y anual, auditoría de embudos (funnels) y atribución de pauta publicitaria multicanal (ROAS).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action_type": {"type": "STRING", "description": "unit_economics | funnel | roas"},
                "cac": {"type": "NUMBER", "description": "Costo de Adquisición de Clientes en COP o USD"},
                "arpu": {"type": "NUMBER", "description": "Ingreso Promedio por Usuario mensual"},
                "churn_monthly_pct": {"type": "NUMBER", "description": "Porcentaje de churn mensual (ej: 3.5)"},
                "gross_margin_pct": {"type": "NUMBER", "description": "Margen bruto en porcentaje (ej: 80.0)"}
            },
            "required": []
        }
    },
    {
        "name": "talent_management",
        "description": "Gestión Estratégica de Talento Humano & Clima Organizacional: Evaluación de colaboradores en la Matriz 9-Box (Desempeño vs Potencial), cálculo de eNPS de clima y costo de rotación (turnover) con normativa colombiana.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action_type": {"type": "STRING", "description": "9box | enps | turnover"},
                "employee_name": {"type": "STRING", "description": "Nombre del colaborador"},
                "performance_score": {"type": "NUMBER", "description": "Desempeño 1.0 a 3.0"},
                "potential_score": {"type": "NUMBER", "description": "Potencial 1.0 a 3.0"},
                "role": {"type": "STRING", "description": "Cargo del colaborador"}
            },
            "required": []
        }
    },
    {
        "name": "forex_radar",
        "description": "Radar Cambiario, Arbitraje de Divisas y Cobertura Forward: TRM oficial Banco de la República, Dólar Cripto USDT P2P, Dólar Tarjeta, EUR/COP, spreads bancarios y simulador de contratos Forward para importaciones.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action_type": {"type": "STRING", "description": "radar | hedge"},
                "amount_usd": {"type": "NUMBER", "description": "Monto en dólares a convertir o cubrir"},
                "days_forward": {"type": "INTEGER", "description": "Días de plazo para la cobertura Forward (ej: 90)"}
            },
            "required": []
        }
    },
'''

def main():
    path = "app/services/action_dispatcher.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Inject schema declarations
    target_schema_spot = '    {\n        "name": "biocognitive_habits",'
    if target_schema_spot in content and '"name": "marketing_growth"' not in content:
        content = content.replace(target_schema_spot, SCHEMAS_HOOK + target_schema_spot)
        print("[SUCCESS] Schemas inyectados en action_dispatcher.py")

    # 2. Inject dispatch execution
    target_exec_spot = '            elif name in ("biocognitive_habits", "habitos_ejecutivos", "telemetria_ceo", "energia_cognitiva", "cronotipo"):'
    if target_exec_spot in content and '"marketing_growth"' not in content:
        content = content.replace(target_exec_spot, DISPATCH_HOOK + "\n" + target_exec_spot)
        print("[SUCCESS] Dispatch execution inyectada en action_dispatcher.py")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[SUCCESS] Guardado action_dispatcher.py")

if __name__ == "__main__":
    main()
