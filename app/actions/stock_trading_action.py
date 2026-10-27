# -*- coding: utf-8 -*-
"""
Action handler for Quantitative Stock Trading & Precision Market Execution.
Evaluates technical indicators (RSI, MACD, EMA 50/200), dynamic ATR stop-loss/take-profit,
and 1.5% maximum capital risk rule to minimize margin of error.
"""

from typing import Any, Dict
from app.services.stock_trading_service import stock_trading_service


def stock_trading_action(parameters: Dict[str, Any]) -> str:
    ticker = str(parameters.get("ticker", "ECOPETROL")).strip().upper()
    current_price = float(parameters.get("current_price", 1960.0))
    rsi = float(parameters.get("rsi", 45.0))
    macd_signal = str(parameters.get("macd_signal", "bullish_cross")).strip()
    ema_50 = float(parameters.get("ema_50", 0.0))
    ema_200 = float(parameters.get("ema_200", 0.0))
    atr = float(parameters.get("atr", 0.0))
    total_capital = float(parameters.get("total_trading_capital", 10000000.0))
    currency = str(parameters.get("currency", "COP")).strip().upper()

    res = stock_trading_service.analyze_trading_signal(
        ticker=ticker,
        current_price=current_price,
        rsi=rsi,
        macd_signal=macd_signal,
        ema_50=ema_50,
        ema_200=ema_200,
        atr=atr,
        total_trading_capital=total_capital,
        currency=currency
    )

    op = res["order_parameters"]
    return (
        f"📈 **TERMINAL BURSÁTIL CUANTITATIVO & ANÁLISIS DE TRADING DE PRECISIÓN**\n\n"
        f"• **Activo / Ticker:** **{res['ticker']}** | **Precio de Mercado:** {currency} ${res['current_price']:,.2f}\n"
        f"• **Estructura de Tendencia:** {res['trend']}\n"
        f"• **RSI (14 períodos):** {res['rsi']['value']} — _{res['rsi']['diagnosis']}_\n"
        f"• **MACD Momentum:** _{res['macd']['diagnosis']}_\n"
        f"• **Medias Móviles (EMA 50 / 200):** EMA(50): ${res['moving_averages']['ema_50']:,.2f} | EMA(200): ${res['moving_averages']['ema_200']:,.2f} (Golden Cross: {'SÍ' if res['moving_averages']['golden_cross'] else 'NO'})\n"
        f"• **Volatilidad ATR (Average True Range):** ${res['volatility_atr']:,.2f}\n\n"
        f"🎯 **ORDEN TÉCNICA SUGERIDA (MARGEN DE ERROR MINIMIZADO):**\n"
        f"• **Dictamen:** **{op['recommendation']}** (Confianza: {op['confidence_pct']}%)\n"
        f"• **Precio de Entrada:** {currency} ${op['entry_price']:,.2f}\n"
        f"• **Stop-Loss Dinámico (1.5 × ATR):** **{currency} ${op['stop_loss']:,.2f}**\n"
        f"• **Take-Profit Objetivo (Ratio 1 : 2.5):** **{currency} ${op['take_profit']:,.2f}**\n"
        f"• **Gestión de Riesgo Estricta (Regla Máx 1.5% de Capital):**\n"
        f"  - Capital Máximo Arriesgado por Trade: {currency} ${op['max_risk_amount']:,.2f}\n"
        f"  - Tamaño de Posición Sugerido: **{op['suggested_shares_to_buy']} acciones** ({currency} ${op['total_order_value']:,.2f})"
    )
