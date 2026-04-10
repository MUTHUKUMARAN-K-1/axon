"""
AXON — Portfolio Intelligence Agent
AI-powered analysis of X Layer wallet portfolios.
Synthesizes Onchain OS data into actionable insights using LLM.
"""

import os
import asyncio
import logging
import json
from typing import Optional
from ..tools.onchain_os import (
    get_wallet_portfolio,
    get_token_price,
    get_transaction_history,
    get_defi_positions,
)
from ..tools.xlayer import get_wallet_balance, get_oklink_address_summary
from ..tools.uniswap import get_uniswap_top_pools

logger = logging.getLogger("axon.agents.portfolio")


def _get_llm_client():
    """Returns available LLM client (Gemini > Groq > OpenAI)."""
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            return ("gemini", genai.GenerativeModel("gemini-1.5-flash"))
        except ImportError:
            logger.warning("google-generativeai not installed, falling through")

    if groq_key:
        try:
            from groq import Groq
            return ("groq", Groq(api_key=groq_key))
        except ImportError:
            logger.warning("groq not installed, falling through")

    if openai_key:
        try:
            from openai import AsyncOpenAI
            return ("openai", AsyncOpenAI(api_key=openai_key))
        except ImportError:
            logger.warning("openai not installed")

    return (None, None)


async def _llm_analyze(prompt: str, system: str = "") -> str:
    """Send prompt to available LLM and return response text.

    BUG FIXED: Groq client `.chat.completions.create()` is a SYNC call
    (not async). Running a sync call in an async function blocks the event loop.
    Fixed by wrapping the Groq sync call with asyncio.to_thread().
    """
    provider, client = _get_llm_client()

    if not client:
        return "LLM analysis unavailable — set GEMINI_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY"

    try:
        if provider == "gemini":
            full = f"{system}\n\n{prompt}" if system else prompt
            # Gemini generate_content is sync — run in thread
            response = await asyncio.to_thread(client.generate_content, full)
            return response.text

        elif provider == "groq":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            def _groq_call():
                return client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.3,
                )

            resp = await asyncio.to_thread(_groq_call)
            return resp.choices[0].message.content

        elif provider == "openai":
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1024,
                temperature=0.3,
            )
            return resp.choices[0].message.content

    except Exception as e:
        logger.error(f"LLM error: {e}")
        return f"LLM analysis failed: {str(e)}"

    return "LLM provider error — no response generated"


def _calculate_risk_score(portfolio: dict, txs: dict) -> dict:
    """Deterministic risk scoring — no LLM needed."""
    score = 50  # start neutral
    flags = []

    tokens = portfolio.get("tokens", [])
    total_usd = portfolio.get("total_usd_value", 0) or 0

    # Concentration risk
    if tokens and total_usd > 0:
        try:
            top_token_value = max(
                (float(t.get("value_usd", 0)) for t in tokens), default=0
            )
            concentration = top_token_value / total_usd
            if concentration > 0.9:
                score -= 20
                flags.append("HIGH_CONCENTRATION: >90% in single token")
            elif concentration > 0.7:
                score -= 10
                flags.append("MODERATE_CONCENTRATION: >70% in single token")
            else:
                score += 10
        except (ValueError, ZeroDivisionError):
            pass

    # Diversification bonus
    if len(tokens) >= 5:
        score += 10
        flags.append("DIVERSIFIED: 5+ tokens held")
    elif len(tokens) == 1:
        score -= 10

    # Transaction activity
    tx_count = txs.get("transaction_count", 0) or 0
    if tx_count > 50:
        score += 5
        flags.append("ACTIVE_WALLET: 50+ recent transactions")
    elif tx_count == 0:
        score -= 10
        flags.append("DORMANT_WALLET: no recent transactions")

    # Portfolio size
    if total_usd > 10000:
        score += 10
    elif total_usd < 10:
        score -= 15
        flags.append("DUST_PORTFOLIO: <$10 total value")

    score = max(0, min(100, score))

    if score >= 75:
        risk_label = "LOW"
        color = "green"
    elif score >= 50:
        risk_label = "MEDIUM"
        color = "yellow"
    else:
        risk_label = "HIGH"
        color = "red"

    return {
        "score": score,
        "risk_level": risk_label,
        "color": color,
        "flags": flags,
    }


async def analyze_wallet(
    address: str,
    include_ai_insights: bool = True,
    chain_id: str = "196",
) -> dict:
    """
    MCP Tool: analyze_wallet
    Full AI-powered wallet analysis combining portfolio, txs, DeFi, and risk scoring.

    BUG FIXED: Data gathering was sequential (4 separate awaits).
    Now runs all 4 fetches in parallel with asyncio.gather() for ~4x speedup.
    Each gather result handles errors via individual try/except in tool functions.
    """
    logger.info(f"Analyzing wallet: {address}")

    # Parallel data gathering — ~4x faster than sequential
    portfolio, txs, defi, native = await asyncio.gather(
        get_wallet_portfolio(address, chain_id),
        get_transaction_history(address, chain_id, limit=50),
        get_defi_positions(address, chain_id),
        get_wallet_balance(address),
        return_exceptions=False,
    )

    # Deterministic scoring
    risk = _calculate_risk_score(portfolio, txs)

    # Build data summary for LLM
    summary_data = {
        "address": address,
        "native_okb": native.get("balance_okb", 0),
        "total_usd": portfolio.get("total_usd_value", 0),
        "token_count": portfolio.get("token_count", 0),
        "top_tokens": [
            {"symbol": t["symbol"], "value_usd": t["value_usd"]}
            for t in portfolio.get("tokens", [])[:5]
        ],
        "recent_tx_count": txs.get("transaction_count", 0),
        "defi_positions": len(defi.get("positions", [])),
        "risk_score": risk["score"],
        "risk_level": risk["risk_level"],
        "risk_flags": risk["flags"],
    }

    ai_insights = ""
    recommendations = []

    if include_ai_insights:
        system = (
            "You are AXON, an expert onchain intelligence agent specializing in X Layer DeFi analysis. "
            "Be concise, specific, and actionable. Use data to back every claim."
        )
        prompt = f"""Analyze this X Layer wallet and provide:
1. A 2-3 sentence portfolio health summary
2. Top 3 specific, actionable recommendations (bulleted)
3. One key risk to watch

Wallet Data:
{json.dumps(summary_data, indent=2)}

Keep response under 300 words. Focus on X Layer ecosystem opportunities."""

        ai_insights = await _llm_analyze(prompt, system)

        # Extract recommendations as structured list
        if ai_insights and ("recommendation" in ai_insights.lower() or "•" in ai_insights or "-" in ai_insights):
            recommendations = [
                line.strip().lstrip("•-123456789. ")
                for line in ai_insights.split("\n")
                if line.strip() and (line.strip()[0] in "•-123456789")
            ][:3]

    return {
        "success": True,
        "address": address,
        "chain": "X Layer",
        "snapshot": {
            "native_balance_okb": native.get("balance_okb", 0),
            "total_portfolio_usd": portfolio.get("total_usd_value", 0),
            "token_count": portfolio.get("token_count", 0),
            "tokens": portfolio.get("tokens", [])[:10],
            "defi_positions": defi.get("positions", []),
            "recent_transactions": txs.get("transactions", [])[:10],
        },
        "risk_assessment": risk,
        "ai_insights": ai_insights,
        "recommendations": recommendations,
        "agent": "AXON Portfolio Intelligence v1.0",
    }


async def compare_wallets(address_a: str, address_b: str) -> dict:
    """
    MCP Tool: compare_wallets
    Side-by-side portfolio comparison of two X Layer wallets.

    BUG FIXED: Two sequential analyze_wallet calls → now parallel with asyncio.gather.
    """
    a, b = await asyncio.gather(
        analyze_wallet(address_a, include_ai_insights=False),
        analyze_wallet(address_b, include_ai_insights=False),
    )

    prompt = f"""Compare these two X Layer wallets as a financial analyst:

Wallet A ({address_a[:10]}...):
{json.dumps(a.get('snapshot', {}), indent=2)}
Risk: {a.get('risk_assessment', {}).get('risk_level')} ({a.get('risk_assessment', {}).get('score')}/100)

Wallet B ({address_b[:10]}...):
{json.dumps(b.get('snapshot', {}), indent=2)}
Risk: {b.get('risk_assessment', {}).get('risk_level')} ({b.get('risk_assessment', {}).get('score')}/100)

Provide: 1) Which wallet is better positioned and why, 2) Key differences, 3) One thing each wallet should do differently. Be concise (200 words max)."""

    comparison_text = await _llm_analyze(prompt)

    score_a = a.get("risk_assessment", {}).get("score", 0)
    score_b = b.get("risk_assessment", {}).get("score", 0)

    return {
        "success": True,
        "wallet_a": a,
        "wallet_b": b,
        "comparison": comparison_text,
        "winner": "A" if score_a > score_b else "B" if score_b > score_a else "TIE",
    }
