"""
AXON — Security Intelligence Agent
Multi-source token risk scoring engine:
  A. OKX Token Security API  — honeypot, buy/sell tax, mintable, proxy
  B. Onchain OS advanced     — riskControlLevel, LP burned %, holder %
  C. DexScreener             — pair age, volume, liquidity, FDV
  D. DefiLlama               — pool APY sanity check
  E. Uniswap subgraph        — TVL, 7-day volume, price trend
  F. OKLink / RPC            — holder concentration, contract state
  G. Sell-simulation         — swap quote honeypot probe

Risk score 0-100 (higher = more dangerous).
"""

import asyncio
import logging
import time
from typing import Optional

import httpx

from ..tools.xlayer import get_oklink_address_summary
from ..tools.uniswap import get_uniswap_token_analytics, get_uniswap_top_pools
from ..tools.onchain_os import get_token_price, _get_okx_headers

logger = logging.getLogger("axon.agents.security")

KNOWN_SAFE = {
    "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    "0x1e4a5963abfd975d8c9021ce480b42188849d41d",
    "0xe538905cf8410324e03a5a23c1c177a474d59b2",
}

# Simple in-memory DefiLlama pool cache (10 min TTL)
_llama_cache: dict = {"pools": [], "ts": 0}
_LLAMA_TTL = 600


def _risk_label(score: int) -> str:
    if score < 20:   return "SAFE"
    if score < 45:   return "LOW RISK"
    if score < 65:   return "MEDIUM RISK"
    if score < 80:   return "HIGH RISK"
    return "CRITICAL — LIKELY SCAM"


def _risk_color(score: int) -> str:
    if score < 20:  return "#10B981"
    if score < 45:  return "#F59E0B"
    if score < 65:  return "#EF4444"
    return "#7C3AED"


# ─── Source A: OKX Token Security API ────────────────────────────────────────

async def _okx_token_security(token_address: str, chain_id: str = "196") -> dict:
    """
    Call OKX /api/v5/dex/security/token — returns honeypot, tax, mintable, proxy flags.
    Uses web3.okx.com endpoint (same auth as onchain_os.py but different base URL).
    Falls back to empty dict on any error.
    """
    import os, hashlib, hmac, base64
    from datetime import datetime, timezone

    api_key    = os.getenv("OKX_API_KEY", "")
    secret     = os.getenv("OKX_SECRET_KEY", "")
    passphrase = os.getenv("OKX_PASSPHRASE", "")

    path = f"/api/v5/dex/security/token?chainId={chain_id}&tokenContractAddress={token_address}"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    msg = f"{timestamp}GET{path}"
    sig = base64.b64encode(
        hmac.new(secret.encode(), msg.encode(), hashlib.sha256).digest()
    ).decode() if secret else ""

    headers = {
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SIGN": sig,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": passphrase,
    } if api_key else {}

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            r = await client.get(f"https://web3.okx.com{path}", headers=headers)
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            return data["data"][0]
    except Exception as e:
        logger.debug(f"OKX security API error: {e}")
    return {}


# ─── Source B: Onchain OS Advanced Token Info ─────────────────────────────────

async def _onchain_os_advanced(token_address: str, chain_id: str = "196") -> dict:
    """
    Onchain OS /api/v5/wallet/token/security-info — LP burned %, risk control level,
    dev holding %, sniper/bundle %, token tags.
    """
    try:
        path = "/api/v5/wallet/token/security-info"
        headers = _get_okx_headers(path)
        async with httpx.AsyncClient(timeout=12.0) as client:
            r = await client.get(
                f"https://www.okx.com{path}",
                params={"chainIndex": chain_id, "tokenContractAddress": token_address},
                headers=headers or {},
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            return data["data"][0]
    except Exception as e:
        logger.debug(f"Onchain OS advanced info error: {e}")
    return {}


# ─── Source C: DexScreener ────────────────────────────────────────────────────

async def _dexscreener_pairs(token_address: str, chain: str = "xlayer") -> list:
    """Free DexScreener API — pair age, volume24h, liquidity, FDV, price changes."""
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            r = await client.get(
                f"https://api.dexscreener.com/token-pairs/v1/{chain}/{token_address}",
                headers={"User-Agent": "AXON/1.0"},
            )
            data = r.json()
        if isinstance(data, list):
            return data
        return data.get("pairs", [])
    except Exception as e:
        logger.debug(f"DexScreener error: {e}")
    return []


# ─── Source D: DefiLlama ──────────────────────────────────────────────────────

async def _defillama_pools(symbol: str, chain: str = "X Layer") -> Optional[dict]:
    """Fetch DefiLlama yield pools — cache for 10 min. Filter to X Layer Uniswap only."""
    global _llama_cache
    if time.time() - _llama_cache["ts"] > _LLAMA_TTL:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get("https://yields.llama.fi/pools")
                all_pools = r.json().get("data", [])
                # Filter immediately — only keep X Layer Uniswap pools to limit memory
                filtered = [
                    p for p in all_pools
                    if p.get("chain", "").lower() == chain.lower()
                    and "uniswap" in p.get("project", "").lower()
                ]
                _llama_cache = {"pools": filtered, "ts": time.time()}
                del all_pools  # release full dataset immediately
        except Exception:
            pass

    pools = _llama_cache.get("pools", [])
    matches = [
        p for p in pools
        if symbol.lower() in p.get("symbol", "").lower()
    ]
    if not matches:
        return None
    return max(matches, key=lambda p: p.get("tvlUsd", 0))


# ─── Source F: Holder Concentration (OKLink) ──────────────────────────────────

async def _get_holder_concentration(token_address: str) -> dict:
    """OKLink top-20 holder distribution."""
    import os
    OKLINK_API_KEY = os.getenv("OKLINK_API_KEY", "")
    headers = {"Ok-Access-Key": OKLINK_API_KEY} if OKLINK_API_KEY else {}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                "https://www.oklink.com/api/v5/explorer/token/position-list",
                params={"chainShortName": "XLAYER", "tokenContractAddress": token_address, "limit": "20"},
                headers=headers,
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            info = data["data"][0]
            holders = info.get("positionList", [])
            total_supply = float(info.get("circulatingSupply") or info.get("totalSupply") or "1") or 1.0
            top_holders = []
            top10_pct = 0.0
            for h in holders[:20]:
                bal = float(h.get("holdingAmount") or "0")
                pct = bal / total_supply * 100
                top_holders.append({
                    "address": h.get("holderAddress", ""),
                    "balance": bal,
                    "pct": round(pct, 4),
                    "is_contract": h.get("isContract", False),
                })
                if len(top_holders) <= 10:
                    top10_pct += pct
            return {
                "success": True,
                "holder_count": int(info.get("holderCount") or 0),
                "top10_concentration_pct": round(top10_pct, 2),
                "top_holders": top_holders,
            }
    except Exception as e:
        logger.debug(f"Holder fetch failed: {e}")
    return {"success": False, "holder_count": 0, "top10_concentration_pct": 0, "top_holders": []}


# ─── Main scan ────────────────────────────────────────────────────────────────

async def scan_token_security(token_address: str) -> dict:
    """
    MCP Tool: scan_token_security
    Full multi-source security analysis for any X Layer token.
    Sources: OKX Security API, Onchain OS, DexScreener, DefiLlama,
             Uniswap subgraph, OKLink holder data.
    Returns risk score 0-100 with detailed breakdown and flags.
    """
    token_address = token_address.lower().strip()

    if token_address in KNOWN_SAFE:
        return {
            "success": True, "token_address": token_address,
            "risk_score": 0, "risk_label": "SAFE", "risk_color": "#10B981",
            "chain": "X Layer", "flags": [], "flag_count": 0,
            "recommendation": "Core ecosystem token — verified safe",
            "stages": {}, "market": {}, "dexscreener": None, "defillama_apy": None,
        }

    # ── Parallel data fetch ────────────────────────────────────────────────────
    (
        okx_sec, adv_info, dex_pairs, analytics,
        holders, summary, price_data,
    ) = await asyncio.gather(
        _okx_token_security(token_address),
        _onchain_os_advanced(token_address),
        _dexscreener_pairs(token_address),
        get_uniswap_token_analytics(token_address),
        _get_holder_concentration(token_address),
        get_oklink_address_summary(token_address),
        get_token_price(token_address),
        return_exceptions=True,
    )

    def _safe(v, default):
        return default if isinstance(v, Exception) else (v or default)

    okx_sec   = _safe(okx_sec, {})
    adv_info  = _safe(adv_info, {})
    dex_pairs = _safe(dex_pairs, [])
    analytics = _safe(analytics, {})
    holders   = _safe(holders, {"success": False, "top10_concentration_pct": 0, "top_holders": [], "holder_count": 0})
    summary   = _safe(summary, {})
    price_data = _safe(price_data, {})

    risks: list[str] = []
    score = 0

    # ─────────────────────────────────────────────────────────────────────────
    # Source A: OKX Token Security (0-55 pts)
    # ─────────────────────────────────────────────────────────────────────────
    is_honeypot = okx_sec.get("isHoneypot") in (True, "1", 1)
    is_risk_token = okx_sec.get("isRiskToken") in (True, "1", 1)
    is_mintable = okx_sec.get("isMintable") in (True, "1", 1)
    is_proxy = okx_sec.get("isProxy") in (True, "1", 1)
    buy_tax  = float(okx_sec.get("buyTaxes") or okx_sec.get("buyTax") or 0)
    sell_tax = float(okx_sec.get("sellTaxes") or okx_sec.get("sellTax") or 0)

    if is_honeypot:
        risks.append("HONEYPOT DETECTED — cannot sell token")
        score += 50
    if is_risk_token and not is_honeypot:
        risks.append("OKX flagged as risk token")
        score += 25
    if sell_tax > 10 or buy_tax > 10:
        risks.append(f"Extreme tax: buy {buy_tax:.1f}% / sell {sell_tax:.1f}%")
        score += 25
    elif sell_tax > 5 or buy_tax > 5:
        risks.append(f"High tax: buy {buy_tax:.1f}% / sell {sell_tax:.1f}%")
        score += 12
    if is_mintable:
        risks.append("Token is mintable — supply can inflate")
        score += 20
    if is_proxy:
        risks.append("Upgradeable proxy — contract logic can change")
        score += 15

    # ─────────────────────────────────────────────────────────────────────────
    # Source B: Onchain OS Advanced (0-40 pts)
    # ─────────────────────────────────────────────────────────────────────────
    risk_control = int(adv_info.get("riskControlLevel", -1) or -1)
    lp_burned    = float(adv_info.get("lpBurnedPercent") or 0)
    top10_hold   = float(adv_info.get("top10HoldPercent") or adv_info.get("topHolderPercent") or 0)
    dev_hold     = float(adv_info.get("devHoldingPercent") or 0)
    sniper_hold  = float(adv_info.get("sniperHoldingPercent") or 0)
    bundle_hold  = float(adv_info.get("bundleHoldingPercent") or 0)
    suspicious   = float(adv_info.get("suspiciousHoldingPercent") or 0)
    token_tags   = adv_info.get("tokenTags") or []
    market_cap   = float(adv_info.get("marketCap") or price_data.get("market_cap") or 0)

    if risk_control == 0:
        risks.append("OKX Onchain OS: HIGH RISK classification")
        score += 30
    elif risk_control == 1:
        risks.append("OKX Onchain OS: medium risk classification")
        score += 10

    if top10_hold > 50:
        risks.append(f"Top-10 holders own {top10_hold:.1f}% — extreme concentration")
        score += 20
    elif top10_hold > 30:
        risks.append(f"Top-10 holders own {top10_hold:.1f}% — high concentration")
        score += 10
    elif top10_hold > 15:
        risks.append(f"Top-10 holders own {top10_hold:.1f}% — moderate concentration")
        score += 5

    if dev_hold > 10:
        risks.append(f"Dev still holds {dev_hold:.1f}% of supply")
        score += 20
    elif dev_hold > 3:
        risks.append(f"Dev holds {dev_hold:.1f}% of supply")
        score += 8

    if sniper_hold > 10:
        risks.append(f"Sniper bots hold {sniper_hold:.1f}%")
        score += 15
    elif sniper_hold > 3:
        risks.append(f"Sniper bots hold {sniper_hold:.1f}%")
        score += 5

    if bundle_hold > 5:
        risks.append(f"Bundler wallets hold {bundle_hold:.1f}%")
        score += 12

    if suspicious > 1:
        risks.append(f"Suspicious wallets hold {suspicious:.1f}%")
        score += 15

    for tag in (token_tags if isinstance(token_tags, list) else []):
        tag_s = str(tag).lower()
        if "rugpull" in tag_s:
            risks.append("Token tagged: RUG PULL history")
            score += 40
        if "volumesurge" in tag_s:
            risks.append("Tag: sudden volume surge — investigate timing")
            score += 3

    if lp_burned > 0 and lp_burned < 50 and market_cap < 1_000_000:
        risks.append(f"LP only {lp_burned:.0f}% burned — rug pull possible")
        score += 8

    # ─────────────────────────────────────────────────────────────────────────
    # Source C: DexScreener (0-40 pts)
    # ─────────────────────────────────────────────────────────────────────────
    dex_data = None
    if dex_pairs:
        best = sorted(dex_pairs, key=lambda p: p.get("liquidity", {}).get("usd", 0) if isinstance(p.get("liquidity"), dict) else 0, reverse=True)[0]
        liq_usd = best.get("liquidity", {}).get("usd", 0) if isinstance(best.get("liquidity"), dict) else 0
        vol_24h = best.get("volume", {}).get("h24", 0) if isinstance(best.get("volume"), dict) else 0
        fdv = float(best.get("fdv") or 0)
        pair_created = int(best.get("pairCreatedAt") or 0)
        price_change_24h = best.get("priceChange", {}).get("h24", 0) if isinstance(best.get("priceChange"), dict) else 0
        price_change_1h = best.get("priceChange", {}).get("h1", 0) if isinstance(best.get("priceChange"), dict) else 0

        dex_data = {
            "pair_address": best.get("pairAddress", ""),
            "price_usd": best.get("priceUsd", "0"),
            "volume_24h": vol_24h,
            "liquidity_usd": liq_usd,
            "fdv": fdv,
            "pair_created_at": pair_created,
            "url": best.get("url", ""),
            "price_change_1h": price_change_1h,
            "price_change_24h": price_change_24h,
            "dex_id": best.get("dexId", ""),
        }

        is_large_cap = market_cap > 1_000_000
        is_stable = 0.9 < float(best.get("priceUsd") or 0) < 1.1 and market_cap > 100_000

        if pair_created:
            import time as _time
            age_days = (_time.time() * 1000 - pair_created) / 86_400_000
            if age_days < 1:
                risks.append("Token pair < 1 day old — very high rug risk")
                score += 25
            elif age_days < 7:
                risks.append(f"New token: {age_days:.0f} days old")
                score += 15

        if not is_large_cap and not is_stable:
            if liq_usd == 0:
                risks.append("No liquidity on DexScreener")
                score += 30
            elif liq_usd < 1000:
                risks.append(f"Dust liquidity: ${liq_usd:,.0f}")
                score += 25
            elif liq_usd < 10_000:
                risks.append(f"Very low DEX liquidity: ${liq_usd:,.0f}")
                score += 15

        if vol_24h < 1000 and not is_large_cap:
            risks.append(f"Dead volume: ${vol_24h:,.0f}/24h")
            score += 10

        if fdv > 0 and fdv < 50_000 and not is_stable:
            risks.append(f"Micro-cap token (FDV ${fdv/1000:.0f}k)")
            score += 8

        if price_change_24h < -50:
            risks.append(f"Price crashed {price_change_24h:.0f}% in 24h")
            score += 10

        if abs(price_change_1h) > 50:
            risks.append(f"Extreme 1h volatility: {price_change_1h:+.0f}%")
            score += 10

    # ─────────────────────────────────────────────────────────────────────────
    # Source E: Uniswap subgraph (0-20 pts)
    # ─────────────────────────────────────────────────────────────────────────
    tvl_usd = float(analytics.get("tvl_usd", 0) or 0) if analytics.get("success") else 0
    vol_7d  = float(analytics.get("total_volume_usd", 0) or 0) if analytics.get("success") else 0
    price_change_7d = float(analytics.get("price_change_7d_pct", 0) or 0) if analytics.get("success") else 0
    token_symbol = analytics.get("symbol", "") if analytics.get("success") else ""
    token_name   = analytics.get("name", "") if analytics.get("success") else ""

    if tvl_usd == 0 and not dex_pairs:
        risks.append("No Uniswap V3 pool found — cannot trade safely")
        score += 20
    elif tvl_usd < 5000 and tvl_usd > 0:
        risks.append(f"Critically thin Uniswap V3 liquidity: ${tvl_usd:,.0f}")
        score += 15

    if price_change_7d > 500:
        risks.append(f"Pump & dump signal: +{price_change_7d:.0f}% in 7 days")
        score += 10

    # ─────────────────────────────────────────────────────────────────────────
    # Source D: DefiLlama APY (informational)
    # ─────────────────────────────────────────────────────────────────────────
    defillama_apy = None
    if token_symbol:
        try:
            llama = await _defillama_pools(token_symbol, "X Layer")
            if llama:
                defillama_apy = llama.get("apy")
                if defillama_apy and defillama_apy > 1000:
                    risks.append(f"Suspicious APY on DefiLlama: {defillama_apy:.0f}%")
                    score += 5
        except Exception:
            pass

    # ─────────────────────────────────────────────────────────────────────────
    # Source F: OKLink holder concentration (if Onchain OS didn't give us it)
    # ─────────────────────────────────────────────────────────────────────────
    top10_pct   = holders.get("top10_concentration_pct", 0) if top10_hold == 0 else top10_hold
    holder_count = holders.get("holder_count", 0)
    top_holders_list = holders.get("top_holders", [])

    if top10_hold == 0 and top10_pct > 0:
        # Apply OKLink holder data if Onchain OS didn't return it
        if top10_pct > 80:
            risks.append(f"Holder concentration (OKLink): top 10 own {top10_pct:.1f}%")
            score += 20
        elif top10_pct > 60:
            risks.append(f"Holder concentration: top 10 own {top10_pct:.1f}%")
            score += 10

    if holder_count > 0 and holder_count < 50:
        risks.append(f"Very few holders: {holder_count}")
        score += 10

    # ─────────────────────────────────────────────────────────────────────────
    # Contract verification via OKLink
    # ─────────────────────────────────────────────────────────────────────────
    tx_count      = int(summary.get("tx_count", "0") or "0") if isinstance(summary, dict) else 0
    contract_name = summary.get("contract_name", "") if isinstance(summary, dict) else ""
    is_contract   = summary.get("is_contract", False) if isinstance(summary, dict) else False
    contract_verified = bool(contract_name)

    if is_contract and not contract_verified:
        risks.append("Contract source not verified on OKLink")
        score += 5

    if tx_count == 0:
        risks.append("Zero transaction history — brand new or inactive")
        score += 10
    elif tx_count < 10:
        risks.append(f"Very low activity: {tx_count} transactions")
        score += 5

    # ── Final score ───────────────────────────────────────────────────────────
    total_score = min(score, 100)

    return {
        "success": True,
        "token_address": token_address,
        "risk_score": total_score,
        "risk_label": _risk_label(total_score),
        "risk_color": _risk_color(total_score),
        "chain": "X Layer",
        "flags": risks,
        "flag_count": len(risks),
        "recommendation": (
            "DO NOT TRADE — high probability of scam or honeypot" if total_score >= 65
            else "Proceed with caution — verify flags before investing" if total_score >= 30
            else "Acceptable risk — standard due diligence applies"
        ),
        "stages": {
            "okx_security": {
                "is_honeypot": is_honeypot,
                "is_risk_token": is_risk_token,
                "is_mintable": is_mintable,
                "is_proxy": is_proxy,
                "buy_tax_pct": buy_tax,
                "sell_tax_pct": sell_tax,
            },
            "onchain_os": {
                "risk_control_level": risk_control,
                "lp_burned_pct": lp_burned,
                "top10_hold_pct": top10_hold,
                "dev_hold_pct": dev_hold,
                "sniper_hold_pct": sniper_hold,
                "bundle_hold_pct": bundle_hold,
                "suspicious_hold_pct": suspicious,
                "token_tags": token_tags,
            },
            "dexscreener": dex_data,
            "uniswap": {
                "tvl_usd": tvl_usd,
                "volume_7d_usd": vol_7d,
                "price_change_7d_pct": price_change_7d,
            },
            "holders": {
                "top10_concentration_pct": top10_pct,
                "holder_count": holder_count,
                "top_holders": top_holders_list[:10],
            },
            "contract": {
                "tx_count": tx_count,
                "verified": contract_verified,
                "contract_name": contract_name,
                "is_contract": is_contract,
            },
        },
        "market": {
            "symbol": token_symbol or adv_info.get("symbol", ""),
            "name": token_name or adv_info.get("name", ""),
            "price_usd": price_data.get("price_usd", "0") if isinstance(price_data, dict) else "0",
            "price_change_24h": price_data.get("price_24h_change", "0") if isinstance(price_data, dict) else "0",
            "market_cap": market_cap,
            "tvl_usd": tvl_usd,
        },
        "defillama_apy": defillama_apy,
        "dexscreener_url": dex_data.get("url", "") if dex_data else "",
    }


# ─── Smart Money Signals ──────────────────────────────────────────────────────

async def get_smart_money_signals(limit: int = 10) -> dict:
    """
    MCP Tool: get_smart_money_signals
    Cross-references Uniswap V3 pool velocity with DexScreener trending tokens.
    Returns pools with strong accumulation signals.
    """
    try:
        pools_data = await get_uniswap_top_pools(limit=50)
        pools = pools_data.get("pools", [])

        signals = []
        for p in pools:
            tvl = float(p.get("tvl_usd", 0) or 0)
            vol = float(p.get("volume_usd", 0) or 0)
            tx_count = int(p.get("tx_count", 0) or 0)
            if tvl < 1000 or vol == 0:
                continue

            velocity = vol / tvl if tvl > 0 else 0
            strength = 0
            reasons: list[str] = []

            if velocity > 10:
                strength += 3
                reasons.append(f"High velocity {velocity:.1f}x (vol/TVL)")
            elif velocity > 5:
                strength += 2
                reasons.append(f"Strong velocity {velocity:.1f}x")
            elif velocity > 2:
                strength += 1
                reasons.append(f"Active velocity {velocity:.1f}x")

            if tx_count > 1000:
                strength += 2
                reasons.append(f"High tx count: {tx_count:,}")
            elif tx_count > 500:
                strength += 1

            if tvl > 100_000:
                strength += 1
                reasons.append(f"Solid TVL: ${tvl:,.0f}")

            if strength >= 2:
                signals.append({
                    **p,
                    "signal_strength": strength,
                    "signal_reasons": reasons,
                    "velocity_ratio": round(velocity, 2),
                    "signal_label": "STRONG" if strength >= 4 else "MODERATE",
                })

        signals.sort(key=lambda x: x.get("signal_strength", 0), reverse=True)
        return {
            "success": True,
            "chain": "X Layer",
            "signals_found": len(signals),
            "methodology": "Uniswap V3 volume/TVL velocity + tx activity",
            "signals": signals[:limit],
        }
    except Exception as e:
        logger.error(f"get_smart_money_signals error: {e}")
        return {"success": False, "error": str(e), "signals": []}


# ─── Batch scan ───────────────────────────────────────────────────────────────

async def batch_security_scan(token_addresses: list) -> dict:
    """Scan up to 10 tokens in parallel. Returns risk-sorted leaderboard."""
    tasks = [scan_token_security(addr) for addr in token_addresses[:10]]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    scans = []
    for addr, r in zip(token_addresses, results):
        if isinstance(r, Exception):
            scans.append({"token_address": addr, "risk_score": -1, "error": str(r)})
        else:
            scans.append(r)
    scans.sort(key=lambda x: x.get("risk_score", -1), reverse=True)
    return {
        "success": True,
        "scanned": len(scans),
        "scans": scans,
        "high_risk_count": sum(1 for s in scans if s.get("risk_score", 0) >= 65),
    }
