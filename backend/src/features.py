"""
AXON — Features: Agent Loop + Chat + x402 Payment Gate
Three win-level capabilities:
1. POST /api/chat — Natural language → MCP tool routing
2. GET  /api/agent/activity — Autonomous agent activity feed
3. x402 premium tool gate with real on-chain OKLink verification
"""

import asyncio
import logging
import json
import os
import time
import base64
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger("axon.features")

# ─── Activity Feed ────────────────────────────────────────────────────────────
ACTIVITY_LOG: deque = deque(maxlen=100)
_loop_running = False


def _log_activity(event_type: str, message: str, data: dict = None):
    ACTIVITY_LOG.appendleft({
        "id": int(time.time() * 1000),
        "type": event_type,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


async def start_agent_loop():
    """Autonomous agent loop — runs every 60s, scans X Layer for signals."""
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

            gas, block, yields = await asyncio.gather(
                get_gas_price(),
                get_block_info("latest"),
                get_yield_opportunities(min_apy=8.0),
                return_exceptions=True,
            )

            if isinstance(gas, dict) and gas.get("success"):
                gwei = gas.get("gas_price_gwei", 0)
                if gwei < 0.05:
                    _log_activity("alert", f"Low gas: {gwei} gwei — ideal execution window", {"gas_gwei": gwei})
                else:
                    _log_activity("gas", f"Gas price: {gwei} gwei", {"gas_gwei": gwei})

            if isinstance(block, dict) and block.get("success"):
                blk = block.get("block_number", 0)
                util = block.get("gas_utilization_pct", 0)
                _log_activity("info", f"Block #{blk:,} — {util}% gas utilization",
                              {"block": blk, "utilization": util})

            if isinstance(yields, dict):
                opps = yields.get("opportunities", [])
                if opps:
                    best = opps[0]
                    _log_activity("yield",
                        f"Yield: {best.get('pair','?')} @ {best.get('estimated_fee_apy_pct','?')}% APY "
                        f"(TVL ${best.get('tvl_usd',0):,.0f})", best)
                else:
                    _log_activity("info", "No high-yield opportunities above 8% APY this cycle", {})

        except Exception as e:
            _log_activity("alert", f"Agent loop error: {str(e)[:80]}", {})
            logger.error(f"Agent loop error: {e}")

        await asyncio.sleep(300)  # 5 min — reduce memory pressure on free tier


# ─── Intent Router ─────────────────────────────────────────────────────────────
INTENT_PATTERNS = [
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
    (["smart money", "whale", "signal", "accumulation", "hot token"], "get_smart_money_signals",
     lambda q: {"limit": 10}),
]


def _detect_intent(question: str):
    import re
    q = question.lower()
    addr = re.search(r'0x[a-fA-F0-9]{40}', question)
    if addr:
        address = addr.group(0)
        if any(w in q for w in ["scan", "safe", "honeypot", "rug", "scam", "security", "risky", "dangerous"]):
            return "scan_token_security", {"token_address": address}
        if any(w in q for w in ["analyze", "analysis", "portfolio", "wallet", "risk", "holding"]):
            return "analyze_wallet", {"address": address, "include_ai_insights": True}
        if any(w in q for w in ["balance", "okb", "how much"]):
            return "get_native_balance", {"address": address}
        if any(w in q for w in ["transaction", "tx", "history", "activity"]):
            return "get_transaction_history", {"address": address, "limit": 10}
        if any(w in q for w in ["price", "token", "analytics"]):
            return "get_uniswap_token_analytics", {"token_address": address}
        return "analyze_wallet", {"address": address, "include_ai_insights": True}

    for keywords, tool, arg_fn in INTENT_PATTERNS:
        if any(kw in q for kw in keywords):
            return tool, arg_fn(q)

    return "get_market_overview", {}


async def _llm_format_response(question: str, tool: str, result: dict) -> str:
    from .agents.portfolio_agent import _llm_analyze
    system = (
        "You are AXON, an expert X Layer DeFi intelligence agent. "
        "Answer the user's question naturally and concisely using the provided data. "
        "Be specific with numbers. Keep responses under 200 words. "
        "End with one actionable insight."
    )
    prompt = f"""User asked: "{question}"

You called the tool `{tool}` and got this data:
{json.dumps(result, indent=2)[:2000]}

Answer the question directly using this data."""
    return await _llm_analyze(prompt, system)


async def handle_chat(question: str) -> dict:
    from .mcp_handler import dispatch_tool
    tool_name, args = _detect_intent(question)
    _log_activity("action", f"Chat: '{question[:50]}' → {tool_name}", {"tool": tool_name})
    try:
        result = await dispatch_tool(tool_name, args)
        answer = await _llm_format_response(question, tool_name, result)
        _log_activity("info", f"Chat answered via {tool_name}", {})
        return {
            "success": True, "question": question,
            "tool_used": tool_name, "answer": answer, "raw_data": result,
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "success": False, "question": question,
            "tool_used": tool_name, "answer": f"Error: {str(e)}", "raw_data": {},
        }


# ─── x402 Configuration ────────────────────────────────────────────────────────
AGENT_WALLET = os.getenv("AXON_AGENT_WALLET", "0xDb82c0d91E057E05600C8F8dc836bEb41da6df14")

PREMIUM_TOOLS = {
    "analyze_wallet":              {"price_okb": 0.001, "description": "AI wallet analysis + risk score"},
    "compare_wallets":             {"price_okb": 0.002, "description": "Side-by-side wallet comparison"},
    "find_arbitrage_opportunities":{"price_okb": 0.001, "description": "Arbitrage opportunity scan"},
}

# ─── Replay Protection Cache ───────────────────────────────────────────────────
# Maps tx_hash → (verified_at_utc, tool_name) — prevents reusing the same payment
# for multiple calls. Entries expire after 24h (server restart also clears it).
_USED_TX_HASHES: dict[str, tuple[datetime, str]] = {}
_PAYMENT_CACHE:  dict[str, tuple[datetime, bool]] = {}  # tx_hash → (checked_at, valid)
_CACHE_TTL_SEC = 300  # re-verify after 5 minutes


def _clean_expired_cache():
    """Remove expired entries from both caches."""
    now = datetime.now(timezone.utc)
    cutoff_24h = now - timedelta(hours=24)
    cutoff_ttl = now - timedelta(seconds=_CACHE_TTL_SEC)

    expired_used = [k for k, (ts, _) in _USED_TX_HASHES.items() if ts < cutoff_24h]
    for k in expired_used:
        del _USED_TX_HASHES[k]

    expired_cache = [k for k, (ts, _) in _PAYMENT_CACHE.items() if ts < cutoff_ttl]
    for k in expired_cache:
        del _PAYMENT_CACHE[k]


def _extract_tx_hash(payment_header: str) -> Optional[str]:
    """
    Extract real tx hash from X-PAYMENT header.
    Agents may send:
      - Raw hex:  0xabc123...
      - Base64 encoded hex: <base64 of "0xabc123...">
      - JSON base64: <base64 of '{"tx":"0xabc123..."}'>
    """
    if not payment_header:
        return None

    raw = payment_header.strip()

    # 1. Direct tx hash (0x + 64 hex chars)
    if raw.startswith("0x") and len(raw) == 66 and all(c in "0123456789abcdefABCDEF" for c in raw[2:]):
        return raw

    # 2. Try base64 decode
    try:
        # Add padding if needed
        padded = raw + "=" * (4 - len(raw) % 4)
        decoded = base64.b64decode(padded).decode("utf-8", errors="ignore").strip()

        # Decoded may be JSON {"tx": "0x..."} or {"txHash": "0x..."} or raw hash
        try:
            obj = json.loads(decoded)
            tx = obj.get("tx") or obj.get("txHash") or obj.get("hash") or obj.get("transaction")
            if tx and tx.startswith("0x") and len(tx) == 66:
                return tx
        except json.JSONDecodeError:
            pass

        # Decoded is raw 0x hash
        if decoded.startswith("0x") and len(decoded) == 66:
            return decoded

    except Exception:
        pass

    # 3. Raw unpadded hex without 0x prefix (64 chars)
    if len(raw) == 64 and all(c in "0123456789abcdefABCDEF" for c in raw):
        return "0x" + raw

    return None


async def verify_x402_payment(payment_header: str, tool_name: str) -> tuple[bool, str, dict]:
    """
    Full x402 payment verification pipeline:
      1. Extract tx hash from X-PAYMENT header
      2. Check replay protection (same tx reused?)
      3. Check payment cache (recently verified?)
      4. Query OKLink → confirm tx on X Layer, correct recipient, sufficient amount
      5. Mark tx as used (replay protection)

    Returns:
      (valid: bool, reason: str, verification_detail: dict)
    """
    _clean_expired_cache()

    tx_hash = _extract_tx_hash(payment_header)
    if not tx_hash:
        return False, "Cannot extract tx hash from X-PAYMENT header. Send a valid 0x... tx hash.", {}

    # Replay protection
    if tx_hash in _USED_TX_HASHES:
        used_at, used_for = _USED_TX_HASHES[tx_hash]
        return False, (
            f"Payment already used for `{used_for}` at {used_at.strftime('%H:%M:%S UTC')}. "
            "Each payment tx can only be used once."
        ), {"tx_hash": tx_hash, "replay": True}

    # Payment cache — avoid hammering OKLink for same tx in short window
    if tx_hash in _PAYMENT_CACHE:
        cached_at, cached_valid = _PAYMENT_CACHE[tx_hash]
        if cached_valid:
            # Mark as used now that it's being consumed
            _USED_TX_HASHES[tx_hash] = (datetime.now(timezone.utc), tool_name)
            return True, "", {"tx_hash": tx_hash, "source": "cache"}
        else:
            return False, "Cached verification failed — send a valid OKB payment tx.", {"tx_hash": tx_hash}

    # Real on-chain verification via OKLink
    from .tools.xlayer import verify_tx_on_xlayer

    required_okb = PREMIUM_TOOLS.get(tool_name, {}).get("price_okb", 0.001)

    logger.info(f"x402: verifying tx {tx_hash} for tool {tool_name} (need {required_okb} OKB)")
    _log_activity("action", f"x402: verifying payment for {tool_name}", {"tx_hash": tx_hash[:20] + "..."})

    result = await verify_tx_on_xlayer(
        tx_hash=tx_hash,
        expected_recipient=AGENT_WALLET,
        min_amount_okb=required_okb,
    )

    # Cache the result
    _PAYMENT_CACHE[tx_hash] = (datetime.now(timezone.utc), result["valid"])

    if result["valid"]:
        # Mark as used — replay protection
        _USED_TX_HASHES[tx_hash] = (datetime.now(timezone.utc), tool_name)
        _log_activity(
            "action",
            f"x402: payment verified for {tool_name} — {result.get('value_okb', 0)} OKB "
            f"from {result.get('from', '?')[:10]}... (via {result.get('source', '?')})",
            result,
        )
        return True, "", result

    _log_activity("alert", f"x402: payment rejected for {tool_name}: {result.get('reason')}", result)
    return False, result.get("reason", "Payment verification failed"), result


def get_x402_payment_info(tool_name: str) -> Optional[dict]:
    """Returns x402 payment requirements if tool is premium, else None."""
    if tool_name not in PREMIUM_TOOLS:
        return None
    info = PREMIUM_TOOLS[tool_name]
    return {
        "x402_version": "1",
        "accepts": [{
            "scheme": "exact",
            "network": "xlayer-mainnet",
            "maxAmountRequired": str(info["price_okb"]),
            "resource": "https://axon-onld.onrender.com/mcp/call",
            "description": f"AXON Premium: {info['description']}",
            "mimeType": "application/json",
            "payTo": AGENT_WALLET,
            "maxTimeoutSeconds": 300,
            "asset": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
            "extra": {"name": "OKB", "decimals": 18},
        }],
    }
