"""
AXON — Agent Loop + Chat + x402 Routes
Three win-level features:
1. POST /api/chat — Natural language → MCP tool routing
2. GET  /api/agent/activity — Autonomous agent activity feed
3. x402 premium tool gate with payment headers
"""

import asyncio
import logging
import json
import os
import time
from collections import deque
from typing import Any
from datetime import datetime, timezone

logger = logging.getLogger("axon.features")

# ─── Activity Feed (in-memory, last 100 events) ───────────────────────────────
ACTIVITY_LOG: deque = deque(maxlen=100)
_loop_running = False


def _log_activity(event_type: str, message: str, data: dict = None):
    ACTIVITY_LOG.appendleft({
        "id": int(time.time() * 1000),
        "type": event_type,           # "alert" | "info" | "action" | "yield" | "gas"
        "message": message,
        "data": data or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


async def start_agent_loop():
    """
    Autonomous agent loop — runs every 60s in the background.
    Monitors gas, yield, and market conditions on X Layer.
    Logs decisions to ACTIVITY_LOG.
    """
    global _loop_running
    if _loop_running:
        return
    _loop_running = True
    logger.info("AXON Autonomous Agent Loop started")
    _log_activity("info", "AXON Agent Loop initialized — monitoring X Layer", {})

    from .tools.xlayer import get_gas_price, get_block_info
    from .agents.market_agent import get_yield_opportunities

    cycle = 0
    while True:
        try:
            cycle += 1
            _log_activity("info", f"Agent cycle #{cycle} — scanning X Layer...", {"cycle": cycle})

            # 1. Gas price check
            gas = await get_gas_price()
            if gas.get("success"):
                gwei = gas.get("gas_price_gwei", 0)
                if gwei < 0.05:
                    _log_activity("alert", f"⚡ Low gas detected: {gwei} gwei — ideal execution window", {"gas_gwei": gwei})
                else:
                    _log_activity("gas", f"Gas price: {gwei} gwei", {"gas_gwei": gwei})

            # 2. Block health
            block = await get_block_info("latest")
            if block.get("success"):
                util = block.get("gas_utilization_pct", 0)
                blk = block.get("block_number", 0)
                _log_activity("info", f"Block #{blk:,} — {util}% gas utilization", {
                    "block": blk, "utilization": util
                })

            # 3. Yield scanner
            yields = await get_yield_opportunities(min_apy=8.0)
            opps = yields.get("opportunities", [])
            if opps:
                best = opps[0]
                _log_activity("yield", (
                    f"🌾 Yield opportunity: {best.get('pair','?')} "
                    f"@ {best.get('estimated_fee_apy_pct','?')}% APY "
                    f"(TVL ${best.get('tvl_usd',0):,.0f})"
                ), best)
            else:
                _log_activity("info", "No high-yield opportunities above 8% APY this cycle", {})

        except Exception as e:
            _log_activity("alert", f"Agent loop error: {str(e)[:80]}", {})
            logger.error(f"Agent loop error: {e}")

        await asyncio.sleep(60)  # run every 60 seconds


# ─── Intent Router ─────────────────────────────────────────────────────────────

INTENT_PATTERNS = [
    # (keywords, tool_name, arg_extractor)
    (["gas", "gwei", "fee", "cheap"], "get_gas_price", lambda _: {}),
    (["block", "latest block", "tps", "utilization"], "get_block_info", lambda _: {}),
    (["market", "overview", "snapshot"], "get_market_overview", lambda _: {}),
    (["yield", "apy", "farm", "earn", "opportunity", "opportunities"], "get_yield_opportunities",
        lambda q: {"min_apy": 5.0}),
    (["pool", "pools", "tvl", "top pool", "uniswap"], "get_uniswap_top_pools",
        lambda q: {"limit": 5}),
    (["arbitrage", "arb", "price difference", "spread"], "find_arbitrage_opportunities",
        lambda q: {"token_address": "0x1e4a5963abfd975d8c9021ce480b42188849d41d", "amount_usd": 1000}),
    (["chain", "x layer stats", "network info", "chain info"], "get_xlayer_stats", lambda _: {}),
]


def _detect_intent(question: str):
    """Map user question to the best MCP tool."""
    q = question.lower()

    # Wallet address detection
    import re
    addr = re.search(r'0x[a-fA-F0-9]{40}', question)
    if addr:
        address = addr.group(0)
        if any(w in q for w in ["analyze", "analysis", "portfolio", "wallet", "risk", "holding"]):
            return "analyze_wallet", {"address": address, "include_ai_insights": True}
        if any(w in q for w in ["balance", "okb", "how much"]):
            return "get_native_balance", {"address": address}
        if any(w in q for w in ["transaction", "tx", "history", "activity"]):
            return "get_transaction_history", {"address": address, "limit": 10}
        return "analyze_wallet", {"address": address, "include_ai_insights": True}

    for keywords, tool, arg_fn in INTENT_PATTERNS:
        if any(kw in q for kw in keywords):
            return tool, arg_fn(q)

    # Default fallback
    return "get_market_overview", {}


async def _llm_format_response(question: str, tool: str, result: dict) -> str:
    """Use LLM to format raw tool result as a natural language answer."""
    from .agents.portfolio_agent import _llm_analyze

    system = (
        "You are AXON, an expert X Layer DeFi intelligence agent. "
        "Answer the user's question naturally and concisely using the provided data. "
        "Be specific with numbers. Format key numbers in bold using **value**. "
        "Keep responses under 200 words. End with one actionable insight."
    )

    prompt = f"""User asked: "{question}"

You called the tool `{tool}` and got this data:
{json.dumps(result, indent=2)[:2000]}

Answer the question directly using this data. Be helpful and specific."""

    return await _llm_analyze(prompt, system)


async def handle_chat(question: str) -> dict:
    """
    Main chat handler: detect intent → call tool → LLM format → return.
    """
    from .mcp_handler import dispatch_tool

    tool_name, args = _detect_intent(question)
    _log_activity("action", f"Chat: routing '{question[:50]}' → {tool_name}", {"tool": tool_name})

    try:
        result = await dispatch_tool(tool_name, args)
        answer = await _llm_format_response(question, tool_name, result)
        _log_activity("info", f"Chat answered via {tool_name}", {})
        return {
            "success": True,
            "question": question,
            "tool_used": tool_name,
            "answer": answer,
            "raw_data": result,
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "success": False,
            "question": question,
            "tool_used": tool_name,
            "answer": f"I encountered an error: {str(e)}",
            "raw_data": {},
        }


# ─── x402 Payment Gate ─────────────────────────────────────────────────────────

AGENT_WALLET = os.getenv("AXON_AGENT_WALLET", "0xDb82c0d91E057E05600C8F8dc836bEb41da6df14")

# Premium tools require x402 payment
PREMIUM_TOOLS = {
    "analyze_wallet": {"price_okb": "0.001", "description": "AI wallet analysis"},
    "compare_wallets": {"price_okb": "0.002", "description": "Wallet comparison"},
    "find_arbitrage_opportunities": {"price_okb": "0.001", "description": "Arbitrage scan"},
}

TOOL_PRICE_USD = {
    "analyze_wallet": 0.01,
    "compare_wallets": 0.02,
    "find_arbitrage_opportunities": 0.01,
}


def get_x402_payment_info(tool_name: str) -> dict | None:
    """Returns x402 payment info if tool is premium, else None."""
    if tool_name in PREMIUM_TOOLS:
        info = PREMIUM_TOOLS[tool_name]
        return {
            "x402_version": "1",
            "accepts": [
                {
                    "scheme": "exact",
                    "network": "xlayer-mainnet",
                    "maxAmountRequired": info["price_okb"],
                    "resource": f"https://axon-onld.onrender.com/mcp/call",
                    "description": f"AXON Premium: {info['description']}",
                    "mimeType": "application/json",
                    "payTo": AGENT_WALLET,
                    "maxTimeoutSeconds": 300,
                    "asset": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                    "extra": {"name": "OKB", "decimals": 18}
                }
            ]
        }
    return None


def verify_x402_payment(payment_header: str, tool_name: str) -> bool:
    """
    Verify x402 payment proof.
    In production: verify OKB tx on X Layer.
    In demo: accept any non-empty payment header as proof.
    """
    if not payment_header:
        return False
    # Demo mode: decode and validate structure
    try:
        import base64
        decoded = base64.b64decode(payment_header + "==").decode("utf-8", errors="ignore")
        # In production: verify tx hash on X Layer RPC
        return len(decoded) > 10
    except Exception:
        # Accept raw tx hash format
        return len(payment_header) > 10
