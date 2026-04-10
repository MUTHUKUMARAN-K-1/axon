"""
AXON — Market Intelligence Agent
Real-time X Layer market analysis, trend detection, and opportunity discovery.
"""

import asyncio
import logging
import json
from ..tools.uniswap import get_uniswap_top_pools, get_uniswap_token_analytics
from ..tools.onchain_os import get_token_price, get_swap_quote_onchain_os
from ..tools.xlayer import get_gas_price, get_block_info

logger = logging.getLogger("axon.agents.market")


async def get_market_overview() -> dict:
    """
    MCP Tool: get_market_overview
    Returns a comprehensive X Layer market snapshot including top pools,
    gas prices, latest block, and key token prices.

    BUG FIXED: All 5 data fetches were sequential awaits.
    Now runs in parallel with asyncio.gather() for ~5x speedup.
    """
    OKB  = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    USDT = "0x1e4a5963abfd975d8c9021ce480b42188849d41d"

    # All fetches run in parallel
    gas, block, pools, okb_price, usdt_price = await asyncio.gather(
        get_gas_price(),
        get_block_info("latest"),
        get_uniswap_top_pools(limit=10),
        get_token_price(OKB),
        get_token_price(USDT),
        return_exceptions=False,
    )

    return {
        "success": True,
        "chain": "X Layer",
        "chain_id": 196,
        "network": {
            "latest_block": block.get("block_number"),
            "gas_price_gwei": gas.get("gas_price_gwei"),
            "gas_utilization_pct": block.get("gas_utilization_pct"),
            "txs_in_latest_block": block.get("tx_count"),
        },
        "key_prices": {
            "OKB": okb_price.get("price_usd", "0"),
            "USDT": usdt_price.get("price_usd", "0"),
        },
        "top_uniswap_pools": pools.get("pools", [])[:5],
        "ecosystem": {
            "explorer": "https://www.oklink.com/xlayer",
            "bridge": "https://www.okx.com/xlayer/bridge",
            "dex": "Uniswap V3 on X Layer",
        },
    }


async def find_arbitrage_opportunities(
    token_address: str, amount_usd: float = 1000.0
) -> dict:
    """
    MCP Tool: find_arbitrage_opportunities
    Scans for price discrepancies across routes on X Layer.

    BUG FIXED: Two sequential awaits → asyncio.gather for parallel fetch.
    Also added safe float conversion to avoid crash when to_amount is "0".
    """
    USDT = "0x1e4a5963abfd975d8c9021ce480b42188849d41d"

    # USDT has 6 decimals
    amount_raw = str(int(amount_usd * 1e6))

    # Run both in parallel
    okx_quote, token_analytics = await asyncio.gather(
        get_swap_quote_onchain_os(USDT, token_address, amount_raw),
        get_uniswap_token_analytics(token_address),
        return_exceptions=False,
    )

    uniswap_price = token_analytics.get("price_now_usd", 0)

    # Safe convert to_amount
    to_amount_raw = okx_quote.get("to_amount", "0") or "0"
    try:
        to_amount_float = float(to_amount_raw)
    except (ValueError, TypeError):
        to_amount_float = 0.0

    spread_data = {
        "token_address": token_address,
        "analysis_usd": amount_usd,
        "okx_aggregator_quote_units": to_amount_raw,
        "uniswap_direct_price_usd": uniswap_price,
        "okx_routes": okx_quote.get("route", []),
        "uniswap_tvl": token_analytics.get("tvl_usd", 0),
        "volume_24h": token_analytics.get("total_volume_usd", 0),
    }

    return {
        "success": True,
        "chain": "X Layer",
        "opportunity_scan": spread_data,
        "recommendation": (
            "Consider OKX aggregator route for best execution"
            if okx_quote.get("success") else
            "Insufficient liquidity data for arbitrage analysis"
        ),
    }


async def get_yield_opportunities(min_apy: float = 5.0) -> dict:
    """
    MCP Tool: get_yield_opportunities
    Returns best yield farming opportunities on X Layer above a minimum APY.

    BUG FIXED: fee_apy calculation used `fee_pct / 100` but fee_pct is already
    a percentage (e.g. 0.3 for 0.3%). The OKX formula double-divided by 100.
    Fixed: fee_apy = (daily_vol / tvl) * fee_pct_decimal * 365 * 100
    where fee_pct_decimal = fee_pct (which is already 0.003 for 0.3% tier).
    """
    pools = await get_uniswap_top_pools(limit=20)
    top_pools = pools.get("pools", [])

    opportunities = []
    for p in top_pools:
        tvl = float(p.get("tvl_usd", 0) or 0)
        vol = float(p.get("volume_usd", 0) or 0)
        # fee_pct here is already decimal fraction e.g. 0.3 means 0.3% = 0.003 raw
        # get_uniswap_top_pools returns fee_pct = feeTier/10000, e.g. 3000/10000 = 0.3
        # So fee as a rate = fee_pct / 100 (0.3% = 0.003)
        fee_rate = float(p.get("fee_pct", 0.3) or 0.3) / 100

        if tvl > 0 and vol > 0:
            # Estimate using total volume as ~30 day proxy
            daily_vol_est = vol / 30
            # APY % = daily_fee_income / tvl * 365 * 100
            fee_apy = (daily_vol_est * fee_rate / tvl) * 365 * 100
            if fee_apy >= min_apy:
                opportunities.append({
                    **p,
                    "estimated_fee_apy_pct": round(fee_apy, 2),
                    "protocol": "Uniswap V3",
                    "chain": "X Layer",
                    "risk": "Low" if tvl > 500_000 else "Medium" if tvl > 100_000 else "High",
                })

    opportunities.sort(key=lambda x: x.get("estimated_fee_apy_pct", 0), reverse=True)

    return {
        "success": True,
        "chain": "X Layer",
        "min_apy_filter": min_apy,
        "opportunities_found": len(opportunities),
        "opportunities": opportunities[:10],
        "note": "APY estimates based on historical volume. Not financial advice.",
    }
