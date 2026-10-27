# -*- coding: utf-8 -*-
"""
Unit tests for Stock Trading Engine, Risk Minimization, and Dividend Screener Services.
"""

import pytest
import asyncio
from app.services.stock_trading_service import stock_trading_service
from app.services.dividend_screener_service import dividend_screener_service
from app.actions.stock_trading_action import stock_trading_action
from app.actions.dividend_screener_action import dividend_screener_action
from app.services.action_dispatcher import SYSTEM_TOOL_DECLARATIONS


def test_stock_trading_bullish_signal():
    """Verify quantitative trading analysis with golden cross and bullish momentum."""
    res = stock_trading_service.analyze_trading_signal(
        ticker="ECOPETROL",
        current_price=2000.0,
        rsi=30.0,  # Oversold -> high score
        macd_signal="bullish_cross",
        ema_50=2050.0,
        ema_200=1950.0,  # Golden cross
        atr=50.0,
        total_trading_capital=10000000.0,
        currency="COP"
    )

    assert res["ticker"] == "ECOPETROL"
    assert res["current_price"] == 2000.0
    assert res["moving_averages"]["golden_cross"] is True
    assert res["volatility_atr"] == 50.0

    op = res["order_parameters"]
    assert "COMPRA" in op["recommendation"]
    assert op["action_code"] in ("BUY", "BUY_MODERATE")
    assert op["confidence_pct"] >= 75.0

    # ATR Stop Loss check: price - 1.5 * ATR = 2000 - 75 = 1925
    assert op["stop_loss"] == 1925.0
    # Risk per share = 75
    # Take Profit: 2000 + 75 * 2.5 = 2187.5
    assert op["take_profit"] == 2187.5
    assert op["risk_reward_ratio"] == "1 : 2.5"

    # Risk rule: 10,000,000 * 1.5% = 150,000 COP max risk
    assert op["max_risk_amount"] == 150000.0
    # Suggested shares: 150,000 / 75 = 2000 shares
    assert op["suggested_shares_to_buy"] == 2000
    assert op["total_order_value"] == 4000000.0


def test_stock_trading_bearish_signal():
    """Verify bearish signal leads to SELL/HOLD and defensive advice."""
    res = stock_trading_service.analyze_trading_signal(
        ticker="PFAVAL",
        current_price=500.0,
        rsi=75.0,  # Overbought
        macd_signal="bearish_cross",
        ema_50=480.0,
        ema_200=520.0,  # Death cross
        atr=15.0,
        total_trading_capital=5000000.0
    )

    op = res["order_parameters"]
    assert op["action_code"] in ("SELL", "HOLD")
    assert op["stop_loss"] < 500.0
    assert op["take_profit"] > 500.0


def test_dividend_screener_bvc_tight_budget():
    """Verify dividend screening for tight Colombian budget (e.g. 100,000 COP)."""
    res = dividend_screener_service.screen_dividend_stocks(
        budget=100000.0,
        market="BVC",
        min_yield_pct=6.0,
        reinvest_dividends=True,
        projection_years=5
    )

    assert res["status"] == "SUCCESS"
    assert res["currency"] == "COP"
    assert res["budget"] == 100000.0
    assert len(res["portfolio"]) > 0

    summ = res["summary"]
    assert summ["total_invested"] <= 100000.0
    assert summ["cash_remaining"] >= 0.0
    assert summ["expected_annual_dividend"] > 0.0
    assert summ["weighted_yield_pct"] >= 6.0

    # Verify DRIP projections
    assert len(res["drip_projections"]) == 5
    # With reinvestment and compound interest, year 5 value should exceed initial invested
    assert res["drip_projections"][-1]["projected_portfolio_value"] > summ["total_invested"]


def test_dividend_screener_us_tight_budget():
    """Verify dividend screening for tight US budget (e.g. 50 USD)."""
    res = dividend_screener_service.screen_dividend_stocks(
        budget=50.0,
        market="US",
        min_yield_pct=5.0,
        reinvest_dividends=True,
        projection_years=3
    )

    assert res["status"] == "SUCCESS"
    assert res["currency"] == "USD"
    assert res["summary"]["total_invested"] <= 50.0
    assert len(res["portfolio"]) > 0


def test_dividend_screener_insufficient_budget():
    """Verify handling when budget is lower than any available stock."""
    res = dividend_screener_service.screen_dividend_stocks(
        budget=100.0,
        market="BVC",
        min_yield_pct=5.0
    )
    assert res["status"] == "INSUFFICIENT_BUDGET"
    assert "El presupuesto" in res["recommendation"]
    assert res["cheapest_alternative"] is not None


def test_stock_trading_action_handler():
    """Verify the action wrapper formats text correctly."""
    out = stock_trading_action({
        "ticker": "ECOPETROL",
        "current_price": 1960.0,
        "rsi": 42.0,
        "macd_signal": "bullish_cross",
        "total_trading_capital": 20000000.0
    })

    assert "TERMINAL BURSÁTIL CUANTITATIVO" in out
    assert "ECOPETROL" in out
    assert "Stop-Loss Dinámico" in out
    assert "Take-Profit Objetivo" in out
    assert "Regla Máx 1.5% de Capital" in out


def test_dividend_screener_action_handler():
    """Verify the dividend screener action wrapper formats text correctly."""
    out = dividend_screener_action({
        "budget": 300000.0,
        "market": "BVC",
        "min_yield_pct": 7.0
    })

    assert "RADAR DE ACCIONES CON DIVIDENDOS" in out
    assert "Rendimiento por Dividendo Ponderado" in out
    assert "PROYECCIÓN DE INTERÉS COMPUESTO" in out


def test_tools_registered_in_system_declarations():
    """Verify tool schemas are registered in SYSTEM_TOOL_DECLARATIONS."""
    from app.services.action_dispatcher import SYSTEM_TOOL_DECLARATIONS
    schema_names = [t["name"] for t in SYSTEM_TOOL_DECLARATIONS]
    assert "stock_trading" in schema_names
    assert "dividend_screener" in schema_names




