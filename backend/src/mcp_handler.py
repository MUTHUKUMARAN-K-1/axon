"""
AXON — MCP Protocol Handler
Exposes all AXON tools as standard MCP (Model Context Protocol) tools.
Compatible with Claude, GPT, and any MCP-enabled AI agent.
"""

import logging
from typing import Any, Dict
from .tools.onchain_os import (
    get_wallet_portfolio,
    get_token_price,
    get_transaction_history,
    get_defi_positions,
    get_xlayer_stats,
    get_swap_quote_onchain_os,
)
from .tools.uniswap import (
    get_uniswap_pool_data,
    get_uniswap_top_pools,
    get_uniswap_swap_quote,
    get_uniswap_token_analytics,
)
from .tools.xlayer import (
    get_gas_price,
    get_block_info,
    get_wallet_balance,
    get_contract_code,
    get_oklink_address_summary,
)
from .agents.portfolio_agent import analyze_wallet, compare_wallets
from .agents.market_agent import get_market_overview, find_arbitrage_opportunities, get_yield_opportunities
from .agents.security_agent import scan_token_security, get_smart_money_signals

logger = logging.getLogger("axon.mcp")

# ─── Tool Registry ─────────────────────────────────────────────────────────────
MCP_TOOLS = [
    {
        "name": "get_wallet_portfolio",
        "description": "Get all token balances and USD values for a wallet on X Layer (Chain ID 196)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "EVM wallet address (0x...)"},
                "chain_id": {"type": "string", "default": "196", "description": "Chain ID (196 = X Layer mainnet)"},
            },
            "required": ["address"],
        },
    },
    {
        "name": "get_token_price",
        "description": "Get real-time price, 24h change, market cap, and volume for any token on X Layer",
        "inputSchema": {
            "type": "object",
            "properties": {
                "token_address": {"type": "string", "description": "Token contract address"},
                "chain_id": {"type": "string", "default": "196"},
            },
            "required": ["token_address"],
        },
    },
    {
        "name": "get_transaction_history",
        "description": "Get recent transaction history for a wallet on X Layer",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {"type": "string"},
                "chain_id": {"type": "string", "default": "196"},
                "limit": {"type": "integer", "default": 20, "maximum": 100},
            },
            "required": ["address"],
        },
    },
    {
        "name": "get_defi_positions",
        "description": "Get active DeFi positions (liquidity pools, staking, lending) for a wallet on X Layer",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {"type": "string"},
                "chain_id": {"type": "string", "default": "196"},
            },
            "required": ["address"],
        },
    },
    {
        "name": "get_xlayer_stats",
        "description": "Get X Layer network stats: chain info, RPC, explorer, native token",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_swap_quote",
        "description": "Get best swap quote across all DEXes on X Layer via OKX DEX aggregator",
        "inputSchema": {
            "type": "object",
            "properties": {
                "from_token": {"type": "string", "description": "Input token address"},
                "to_token": {"type": "string", "description": "Output token address"},
                "amount": {"type": "string", "description": "Amount in smallest unit (wei)"},
                "slippage": {"type": "string", "default": "0.5", "description": "Slippage tolerance %"},
            },
            "required": ["from_token", "to_token", "amount"],
        },
    },
    {
        "name": "get_uniswap_pool_data",
        "description": "Get Uniswap V3 pool stats (TVL, volume, fees) for a token pair on X Layer",
        "inputSchema": {
            "type": "object",
            "properties": {
                "token0": {"type": "string"},
                "token1": {"type": "string"},
                "fee": {"type": "integer", "default": 3000, "description": "Fee tier: 500, 3000, or 10000"},
            },
            "required": ["token0", "token1"],
        },
    },
    {
        "name": "get_uniswap_top_pools",
        "description": "Get top Uniswap V3 pools on X Layer ranked by TVL",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 10, "maximum": 50},
            },
        },
    },
    {
        "name": "get_uniswap_token_analytics",
        "description": "Get 7-day OHLC, volume, and liquidity analytics for a token via Uniswap V3 on X Layer",
        "inputSchema": {
            "type": "object",
            "properties": {
                "token_address": {"type": "string"},
            },
            "required": ["token_address"],
        },
    },
    {
        "name": "get_gas_price",
        "description": "Get current gas price on X Layer in gwei",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_block_info",
        "description": "Get latest block info from X Layer (number, timestamp, gas utilization)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "block": {"type": "string", "default": "latest"},
            },
        },
    },
    {
        "name": "get_native_balance",
        "description": "Get native OKB balance for a wallet on X Layer",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {"type": "string"},
            },
            "required": ["address"],
        },
    },
    {
        "name": "analyze_wallet",
        "description": "Full AI-powered wallet analysis: portfolio health, risk score, and actionable recommendations for X Layer",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {"type": "string"},
                "include_ai_insights": {"type": "boolean", "default": True},
            },
            "required": ["address"],
        },
    },
    {
        "name": "compare_wallets",
        "description": "Side-by-side AI comparison of two X Layer wallets",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address_a": {"type": "string"},
                "address_b": {"type": "string"},
            },
            "required": ["address_a", "address_b"],
        },
    },
    {
        "name": "get_market_overview",
        "description": "Get X Layer market snapshot: top pools, gas price, key token prices, latest block",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_yield_opportunities",
        "description": "Find yield farming opportunities on X Layer above a minimum APY threshold",
        "inputSchema": {
            "type": "object",
            "properties": {
                "min_apy": {"type": "number", "default": 5.0, "description": "Minimum APY % filter"},
            },
        },
    },
    {
        "name": "find_arbitrage_opportunities",
        "description": "Scan for price discrepancies and arbitrage opportunities for a token on X Layer",
        "inputSchema": {
            "type": "object",
            "properties": {
                "token_address": {"type": "string"},
                "amount_usd": {"type": "number", "default": 1000.0},
            },
            "required": ["token_address"],
        },
    },
    {
        "name": "scan_token_security",
        "description": (
            "5-stage token security analysis: honeypot detection, holder concentration, "
            "liquidity safety, contract verification, and price anomalies. "
            "Returns risk score 0-100 with actionable flags. AXON's signature security feature."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "token_address": {"type": "string", "description": "Token contract address to scan"},
            },
            "required": ["token_address"],
        },
    },
    {
        "name": "get_smart_money_signals",
        "description": (
            "Identify tokens with smart money accumulation signals on X Layer. "
            "Uses volume/TVL velocity cross-analysis on all Uniswap V3 pools."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 10, "description": "Max signals to return"},
            },
        },
    },
]


async def dispatch_tool(tool_name: str, args: Dict[str, Any]) -> Any:
    """Route an MCP tool call to the correct implementation."""
    dispatch = {
        "get_wallet_portfolio": lambda: get_wallet_portfolio(
            args["address"], args.get("chain_id", "196")
        ),
        "get_token_price": lambda: get_token_price(
            args["token_address"], args.get("chain_id", "196")
        ),
        "get_transaction_history": lambda: get_transaction_history(
            args["address"], args.get("chain_id", "196"), args.get("limit", 20)
        ),
        "get_defi_positions": lambda: get_defi_positions(
            args["address"], args.get("chain_id", "196")
        ),
        "get_xlayer_stats": lambda: get_xlayer_stats(),
        "get_swap_quote": lambda: get_swap_quote_onchain_os(
            args["from_token"], args["to_token"], args["amount"],
            args.get("chain_id", "196"), args.get("slippage", "0.5"),
        ),
        "get_uniswap_pool_data": lambda: get_uniswap_pool_data(
            args["token0"], args["token1"], args.get("fee", 3000)
        ),
        "get_uniswap_top_pools": lambda: get_uniswap_top_pools(args.get("limit", 10)),
        "get_uniswap_token_analytics": lambda: get_uniswap_token_analytics(args["token_address"]),
        "get_gas_price": lambda: get_gas_price(),
        "get_block_info": lambda: get_block_info(args.get("block", "latest")),
        "get_native_balance": lambda: get_wallet_balance(args["address"]),
        "analyze_wallet": lambda: analyze_wallet(
            args["address"], args.get("include_ai_insights", True)
        ),
        "compare_wallets": lambda: compare_wallets(args["address_a"], args["address_b"]),
        "get_market_overview": lambda: get_market_overview(),
        "get_yield_opportunities": lambda: get_yield_opportunities(args.get("min_apy", 5.0)),
        "find_arbitrage_opportunities": lambda: find_arbitrage_opportunities(
            args["token_address"], args.get("amount_usd", 1000.0)
        ),
        "scan_token_security": lambda: scan_token_security(args["token_address"]),
        "get_smart_money_signals": lambda: get_smart_money_signals(args.get("limit", 10)),
    }

    handler = dispatch.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool: {tool_name}", "available_tools": list(dispatch.keys())}

    return await handler()
