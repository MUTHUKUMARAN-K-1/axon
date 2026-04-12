"""
AXON — Uniswap Skill Integration
Wraps Uniswap V3 on X Layer for swap quotes and pool analytics.
Uniswap Universal Router on X Layer: 0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD
"""

import httpx
import os
import logging
from typing import Optional

logger = logging.getLogger("axon.tools.uniswap")

# Uniswap V3 contracts on X Layer (196)
UNISWAP_UNIVERSAL_ROUTER = "0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD"
UNISWAP_QUOTER_V2 = "0x61fFE014bA17989E743c5F6cB21bF9697530B21e"
UNISWAP_FACTORY_V3 = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"
UNISWAP_GRAPH_XLAYER = "https://api.studio.thegraph.com/query/5765/uniswap-v3-xlayer/version/latest"

# Uniswap AI skill endpoint (if available from hackathon resources)
UNISWAP_AI_SKILL_URL = os.getenv("UNISWAP_AI_SKILL_URL", "")


async def get_uniswap_pool_data(
    token0: str, token1: str, fee: int = 3000
) -> dict:
    """
    MCP Tool: get_uniswap_pool_data
    Returns Uniswap V3 pool stats for a token pair on X Layer.
    Fee tiers: 500 (0.05%), 3000 (0.3%), 10000 (1%)
    """
    # BUG FIXED: feeTier is an Int in GraphQL schema, not a String.
    # Quoting it with "%s" caused 0 results returned for all pool queries.
    query = """
    {
      pools(
        where: {
          token0_contains_nocase: "%s",
          token1_contains_nocase: "%s",
          feeTier: %d
        }
        first: 5
        orderBy: totalValueLockedUSD
        orderDirection: desc
      ) {
        id
        token0 { symbol decimals }
        token1 { symbol decimals }
        feeTier
        liquidity
        totalValueLockedUSD
        volumeUSD
        txCount
        token0Price
        token1Price
        poolDayData(first: 7 orderBy: date orderDirection: desc) {
          date
          volumeUSD
          tvlUSD
          feesUSD
        }
      }
    }
    """ % (token0.lower(), token1.lower(), fee)

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(
                UNISWAP_GRAPH_XLAYER,
                json={"query": query},
                headers={"Content-Type": "application/json"},
            )
            data = r.json()

        # Check for GraphQL errors
        if data.get("errors"):
            logger.warning(f"GraphQL errors: {data['errors']}")

        pools = data.get("data", {}).get("pools", [])
        if not pools:
            return {
                "success": False,
                "error": "No pool found for this pair",
                "token0": token0,
                "token1": token1,
                "fee_tier": fee,
            }

        p = pools[0]
        daily = p.get("poolDayData", [])
        avg_daily_volume = (
            sum(float(d.get("volumeUSD", 0) or 0) for d in daily) / len(daily)
            if daily else 0
        )

        return {
            "success": True,
            "pool_address": p.get("id", ""),
            "token0": p["token0"]["symbol"],
            "token1": p["token1"]["symbol"],
            "fee_tier_bps": int(p.get("feeTier", 3000)) / 10000,
            "tvl_usd": round(float(p.get("totalValueLockedUSD", 0) or 0), 2),
            "volume_usd_total": round(float(p.get("volumeUSD", 0) or 0), 2),
            "avg_daily_volume_usd": round(avg_daily_volume, 2),
            "tx_count": p.get("txCount", 0),
            "price_token0_in_token1": p.get("token1Price", "0"),
            "price_token1_in_token0": p.get("token0Price", "0"),
            "chain": "X Layer",
            "protocol": "Uniswap V3",
        }

    except Exception as e:
        logger.error(f"get_uniswap_pool_data error: {e}")
        return {"success": False, "error": str(e)}


async def get_uniswap_top_pools(limit: int = 10) -> dict:
    """
    MCP Tool: get_uniswap_top_pools
    Returns top Uniswap V3 pools on X Layer by TVL.
    """
    query = """
    {
      pools(
        first: %d
        orderBy: totalValueLockedUSD
        orderDirection: desc
      ) {
        id
        token0 { symbol }
        token1 { symbol }
        feeTier
        totalValueLockedUSD
        volumeUSD
        txCount
        token0Price
      }
    }
    """ % limit

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(
                UNISWAP_GRAPH_XLAYER,
                json={"query": query},
                headers={"Content-Type": "application/json"},
            )
            data = r.json()

        # Surface GraphQL errors
        if data.get("errors"):
            logger.warning(f"GraphQL errors on top pools: {data['errors']}")

        pools = data.get("data", {}).get("pools") or []
        return {
            "success": True,
            "chain": "X Layer",
            "protocol": "Uniswap V3",
            "pool_count": len(pools),
            "pools": [
                {
                    "address": p.get("id", ""),
                    "pair": f"{p['token0']['symbol']}/{p['token1']['symbol']}",
                    # feeTier=3000 → 0.3%, feeTier=500 → 0.05%
                    "fee_pct": int(p.get("feeTier", 0)) / 10000,
                    "tvl_usd": round(float(p.get("totalValueLockedUSD", 0) or 0), 2),
                    "volume_usd": round(float(p.get("volumeUSD", 0) or 0), 2),
                    "tx_count": int(p.get("txCount", 0) or 0),
                }
                for p in pools
            ],
        }

    except Exception as e:
        logger.error(f"get_uniswap_top_pools error: {e}")
        return {"success": False, "error": str(e), "pools": []}


async def get_uniswap_swap_quote(
    token_in: str,
    token_out: str,
    amount_in: str,
    fee: int = 3000,
) -> dict:
    """
    MCP Tool: get_uniswap_swap_quote
    Returns Uniswap V3 swap quote via OKX aggregator (routes through Uniswap on X Layer).
    """
    # Use Uniswap AI skill if configured
    if UNISWAP_AI_SKILL_URL:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.post(
                    f"{UNISWAP_AI_SKILL_URL}/quote",
                    json={
                        "chainId": 196,
                        "tokenIn": token_in,
                        "tokenOut": token_out,
                        "amountIn": amount_in,
                        "fee": fee,
                    },
                )
                data = r.json()
                data["source"] = "Uniswap AI Skill"
                data["chain"] = "X Layer"
                return data
        except Exception as e:
            logger.warning(f"Uniswap AI skill failed, falling back: {e}")

    # Fallback: OKX DEX aggregator which includes Uniswap routes
    from .onchain_os import get_swap_quote_onchain_os
    result = await get_swap_quote_onchain_os(token_in, token_out, amount_in)
    result["protocol_hint"] = "Routed via OKX DEX (includes Uniswap V3)"
    return result


async def search_pools_by_token(token_address: str, limit: int = 10) -> dict:
    """
    MCP Tool: search_pools_by_token
    Find all Uniswap V3 pools containing a specific token on X Layer.
    """
    query = """
    {
      pools(
        where: { token0_contains_nocase: "%s" }
        first: %d
        orderBy: totalValueLockedUSD
        orderDirection: desc
      ) {
        id
        token0 { symbol }
        token1 { symbol }
        feeTier
        totalValueLockedUSD
        volumeUSD
      }
    }
    """ % (token_address.lower(), limit)
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(UNISWAP_GRAPH_XLAYER, json={"query": query},
                                  headers={"Content-Type": "application/json"})
            data = r.json()
        pools = data.get("data", {}).get("pools", [])
        return {
            "success": True,
            "token": token_address,
            "chain": "X Layer",
            "pool_count": len(pools),
            "pools": [
                {
                    "address": p["id"],
                    "pair": f"{p['token0']['symbol']}/{p['token1']['symbol']}",
                    "fee_pct": int(p.get("feeTier", 0)) / 10000,
                    "tvl_usd": round(float(p.get("totalValueLockedUSD", 0) or 0), 2),
                    "volume_usd": round(float(p.get("volumeUSD", 0) or 0), 2),
                }
                for p in pools
            ],
        }
    except Exception as e:
        logger.error(f"search_pools_by_token error: {e}")
        return {"success": False, "error": str(e), "pools": []}


async def get_pool_ohlc(pool_address: str, days: int = 7) -> dict:
    """
    MCP Tool: get_pool_ohlc
    Returns OHLC candle data for a Uniswap V3 pool on X Layer.
    """
    query = """
    {
      pool(id: "%s") {
        token0 { symbol }
        token1 { symbol }
        poolDayData(first: %d orderBy: date orderDirection: desc) {
          date
          open
          high
          low
          close
          volumeUSD
          tvlUSD
          feesUSD
          txCount
        }
      }
    }
    """ % (pool_address.lower(), min(days, 30))
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(UNISWAP_GRAPH_XLAYER, json={"query": query},
                                  headers={"Content-Type": "application/json"})
            data = r.json()
        pool = data.get("data", {}).get("pool")
        if not pool:
            return {"success": False, "error": "Pool not found"}
        candles = pool.get("poolDayData", [])
        return {
            "success": True,
            "pool": pool_address,
            "pair": f"{pool['token0']['symbol']}/{pool['token1']['symbol']}",
            "chain": "X Layer",
            "candle_count": len(candles),
            "candles": [
                {
                    "date": c.get("date"),
                    "open": c.get("open", "0"),
                    "high": c.get("high", "0"),
                    "low": c.get("low", "0"),
                    "close": c.get("close", "0"),
                    "volume_usd": round(float(c.get("volumeUSD", 0) or 0), 2),
                    "tvl_usd": round(float(c.get("tvlUSD", 0) or 0), 2),
                    "fees_usd": round(float(c.get("feesUSD", 0) or 0), 2),
                    "tx_count": int(c.get("txCount", 0) or 0),
                }
                for c in candles
            ],
        }
    except Exception as e:
        logger.error(f"get_pool_ohlc error: {e}")
        return {"success": False, "error": str(e), "candles": []}


async def get_pool_fees(pool_address: str) -> dict:
    """
    MCP Tool: get_pool_fees
    Returns cumulative fee revenue analytics for a Uniswap V3 pool on X Layer.
    """
    query = """
    {
      pool(id: "%s") {
        token0 { symbol }
        token1 { symbol }
        feeTier
        totalValueLockedUSD
        volumeUSD
        feesUSD
        txCount
        poolDayData(first: 7 orderBy: date orderDirection: desc) {
          date feesUSD volumeUSD
        }
      }
    }
    """ % pool_address.lower()
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(UNISWAP_GRAPH_XLAYER, json={"query": query},
                                  headers={"Content-Type": "application/json"})
            data = r.json()
        pool = data.get("data", {}).get("pool")
        if not pool:
            return {"success": False, "error": "Pool not found"}
        daily = pool.get("poolDayData", [])
        fees_7d = sum(float(d.get("feesUSD", 0) or 0) for d in daily)
        tvl = float(pool.get("totalValueLockedUSD", 0) or 0)
        fee_apy = (fees_7d / max(tvl, 1)) * 52 * 100 if tvl > 0 else 0
        return {
            "success": True,
            "pool": pool_address,
            "pair": f"{pool['token0']['symbol']}/{pool['token1']['symbol']}",
            "fee_tier_pct": int(pool.get("feeTier", 0)) / 10000,
            "total_fees_usd": round(float(pool.get("feesUSD", 0) or 0), 2),
            "fees_7d_usd": round(fees_7d, 2),
            "estimated_fee_apy_pct": round(fee_apy, 2),
            "tvl_usd": round(tvl, 2),
            "volume_total_usd": round(float(pool.get("volumeUSD", 0) or 0), 2),
            "chain": "X Layer",
        }
    except Exception as e:
        logger.error(f"get_pool_fees error: {e}")
        return {"success": False, "error": str(e)}


async def get_uniswap_protocol_stats() -> dict:
    """
    MCP Tool: get_uniswap_protocol_stats
    Returns overall Uniswap V3 protocol statistics on X Layer.
    """
    query = """
    {
      factories(first: 1) {
        poolCount
        txCount
        totalVolumeUSD
        totalFeesUSD
        totalValueLockedUSD
      }
    }
    """
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(UNISWAP_GRAPH_XLAYER, json={"query": query},
                                  headers={"Content-Type": "application/json"})
            data = r.json()
        factories = data.get("data", {}).get("factories", [])
        if not factories:
            return {"success": False, "error": "No factory data"}
        f = factories[0]
        return {
            "success": True,
            "chain": "X Layer",
            "protocol": "Uniswap V3",
            "pool_count": int(f.get("poolCount", 0)),
            "tx_count": int(f.get("txCount", 0)),
            "total_volume_usd": round(float(f.get("totalVolumeUSD", 0) or 0), 2),
            "total_fees_usd": round(float(f.get("totalFeesUSD", 0) or 0), 2),
            "tvl_usd": round(float(f.get("totalValueLockedUSD", 0) or 0), 2),
        }
    except Exception as e:
        logger.error(f"get_uniswap_protocol_stats error: {e}")
        return {"success": False, "error": str(e)}


async def get_uniswap_token_analytics(token_address: str) -> dict:
    """
    MCP Tool: get_uniswap_token_analytics
    Returns 7-day volume, price, and liquidity analytics for a token via Uniswap subgraph.
    """
    query = """
    {
      token(id: "%s") {
        symbol
        name
        decimals
        totalValueLockedUSD
        volumeUSD
        txCount
        tokenDayData(first: 7 orderBy: date orderDirection: desc) {
          date
          priceUSD
          volumeUSD
          totalValueLockedUSD
          open
          high
          low
          close
        }
        whitelistPools(first: 3 orderBy: totalValueLockedUSD orderDirection: desc) {
          id
          token0 { symbol }
          token1 { symbol }
          totalValueLockedUSD
        }
      }
    }
    """ % token_address.lower()

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(
                UNISWAP_GRAPH_XLAYER,
                json={"query": query},
                headers={"Content-Type": "application/json"},
            )
            data = r.json()

        if data.get("errors"):
            logger.warning(f"GraphQL errors on token analytics: {data['errors']}")

        token = data.get("data", {}).get("token")
        if not token:
            return {"success": False, "error": "Token not found in Uniswap subgraph"}

        daily = token.get("tokenDayData", []) or []
        # Filter out zero/null prices
        prices = [
            float(d["priceUSD"])
            for d in daily
            if d.get("priceUSD") and float(d["priceUSD"]) > 0
        ]

        price_change = 0.0
        if len(prices) > 1 and prices[-1] > 0:
            price_change = round((prices[0] - prices[-1]) / prices[-1] * 100, 2)

        return {
            "success": True,
            "token_address": token_address,
            "symbol": token.get("symbol", ""),
            "name": token.get("name", ""),
            "decimals": token.get("decimals", 18),
            "tvl_usd": round(float(token.get("totalValueLockedUSD", 0) or 0), 2),
            "total_volume_usd": round(float(token.get("volumeUSD", 0) or 0), 2),
            "tx_count": int(token.get("txCount", 0) or 0),
            "price_now_usd": prices[0] if prices else 0,
            "price_7d_ago_usd": prices[-1] if len(prices) > 1 else 0,
            "price_change_7d_pct": price_change,
            "ohlc_7d": daily,
            "top_pools": token.get("whitelistPools", []),
            "chain": "X Layer",
            "protocol": "Uniswap V3",
        }

    except Exception as e:
        logger.error(f"get_uniswap_token_analytics error: {e}")
        return {"success": False, "error": str(e)}
