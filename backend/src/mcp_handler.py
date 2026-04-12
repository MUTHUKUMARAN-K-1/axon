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
    get_wallet_net_worth,
    get_token_detail,
    lookup_transaction,
    get_supported_tokens,
    get_cross_chain_quote,
    check_address_security,
    check_url_safety,
    get_nft_holdings,
    get_yield_products,
    get_swap_execution,
)
from .tools.oklink import (
    get_address_info,
    get_token_transfers,
    get_block_list,
    get_block_detail,
    get_pending_transactions,
    get_contract_info,
    estimate_gas,
    get_token_transfer_list,
    get_rich_list,
    get_internal_transactions,
)
from .tools.uniswap import (
    get_uniswap_pool_data,
    get_uniswap_top_pools,
    get_uniswap_token_analytics,
    search_pools_by_token,
    get_pool_ohlc,
    get_pool_fees,
    get_uniswap_protocol_stats,
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
from .agents.verdict_ledger import get_onchain_verdict, get_total_verdicts

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
    {
        "name": "get_onchain_verdict",
        "description": (
            "Query the AxonVerdictLedger smart contract on X Layer for the latest "
            "published security verdict for any token. Returns risk score, flag count, "
            "timestamp, and data hash — all verifiable on-chain."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "token_address": {"type": "string", "description": "Token contract address to look up"},
            },
            "required": ["token_address"],
        },
    },
    {
        "name": "get_total_verdicts",
        "description": "Return the total number of unique tokens AXON has published security verdicts for on X Layer.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_wallet_net_worth",
        "description": "Get total portfolio value across all chains for a wallet via OKX Onchain OS",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "EVM wallet address"},
            },
            "required": ["address"],
        },
    },
    {
        "name": "get_token_detail",
        "description": "Get rich token metadata: holder count, FDV, market cap rank, website, socials, description via Onchain OS",
        "inputSchema": {
            "type": "object",
            "properties": {
                "token_address": {"type": "string"},
                "chain_id": {"type": "string", "default": "196"},
            },
            "required": ["token_address"],
        },
    },
    {
        "name": "lookup_transaction",
        "description": "Decode any transaction hash on X Layer — from/to, value, status, gas, token transfers via Onchain OS",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tx_hash": {"type": "string", "description": "Transaction hash (0x...)"},
                "chain_id": {"type": "string", "default": "196"},
            },
            "required": ["tx_hash"],
        },
    },
    {
        "name": "get_supported_tokens",
        "description": "List all tokens supported by OKX DEX aggregator on X Layer",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chain_id": {"type": "string", "default": "196"},
            },
        },
    },
    # ── Security (OKX) ──────────────────────────────────────────────────────────
    {
        "name": "check_address_security",
        "description": "Check if a wallet address is blacklisted or malicious via OKX DEX security API",
        "inputSchema": {"type": "object", "properties": {"address": {"type": "string"}}, "required": ["address"]},
    },
    {
        "name": "check_url_safety",
        "description": "Check if a URL is a phishing or scam site via OKX DEX security API",
        "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
    },
    # ── NFT & DeFi Products ─────────────────────────────────────────────────────
    {
        "name": "get_nft_holdings",
        "description": "Get NFT portfolio for a wallet on X Layer via OKX Onchain OS",
        "inputSchema": {"type": "object", "properties": {"address": {"type": "string"}, "chain_id": {"type": "string", "default": "196"}}, "required": ["address"]},
    },
    {
        "name": "get_yield_products",
        "description": "List available DeFi yield/earning products on X Layer via OKX Onchain OS",
        "inputSchema": {"type": "object", "properties": {"chain_id": {"type": "string", "default": "196"}}},
    },
    {
        "name": "get_swap_execution",
        "description": "Get signed calldata to execute a swap on X Layer via OKX DEX aggregator — ready to broadcast",
        "inputSchema": {
            "type": "object",
            "properties": {
                "from_token": {"type": "string"}, "to_token": {"type": "string"},
                "amount": {"type": "string"}, "user_wallet": {"type": "string"},
                "chain_id": {"type": "string", "default": "196"}, "slippage": {"type": "string", "default": "0.5"},
            },
            "required": ["from_token", "to_token", "amount", "user_wallet"],
        },
    },
    # ── OKLink Explorer ─────────────────────────────────────────────────────────
    {
        "name": "get_address_info",
        "description": "Get address entity label, balance, tx count, first/last tx via OKLink explorer",
        "inputSchema": {"type": "object", "properties": {"address": {"type": "string"}}, "required": ["address"]},
    },
    {
        "name": "get_token_transfers",
        "description": "Get ERC-20 token transfer history for a wallet on X Layer via OKLink",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {"type": "string"}, "token_contract": {"type": "string", "default": ""},
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["address"],
        },
    },
    {
        "name": "get_block_list",
        "description": "Get most recent blocks on X Layer via OKLink explorer",
        "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 10}}},
    },
    {
        "name": "get_block_detail",
        "description": "Get full details for a specific block on X Layer via OKLink",
        "inputSchema": {"type": "object", "properties": {"block_number": {"type": "string"}}, "required": ["block_number"]},
    },
    {
        "name": "get_pending_transactions",
        "description": "Get unconfirmed/pending transactions in the X Layer mempool via OKLink",
        "inputSchema": {
            "type": "object",
            "properties": {"address": {"type": "string", "default": ""}, "limit": {"type": "integer", "default": 20}},
        },
    },
    {
        "name": "get_contract_info",
        "description": "Get contract verification status, creator, deploy TX, compiler version via OKLink",
        "inputSchema": {"type": "object", "properties": {"contract_address": {"type": "string"}}, "required": ["contract_address"]},
    },
    {
        "name": "estimate_gas",
        "description": "Estimate gas cost for a transaction on X Layer via OKLink",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to": {"type": "string"}, "data": {"type": "string", "default": "0x"}, "value": {"type": "string", "default": "0"},
            },
            "required": ["to"],
        },
    },
    {
        "name": "get_token_transfer_list",
        "description": "Get all recent transfers for a token contract on X Layer via OKLink",
        "inputSchema": {
            "type": "object",
            "properties": {"token_contract": {"type": "string"}, "limit": {"type": "integer", "default": 20}},
            "required": ["token_contract"],
        },
    },
    {
        "name": "get_rich_list",
        "description": "Get top holders (rich list) for OKB or any token on X Layer via OKLink",
        "inputSchema": {
            "type": "object",
            "properties": {"token_contract": {"type": "string", "default": ""}, "limit": {"type": "integer", "default": 20}},
        },
    },
    {
        "name": "get_internal_transactions",
        "description": "Get internal contract calls (traces) for a transaction on X Layer via OKLink",
        "inputSchema": {"type": "object", "properties": {"tx_hash": {"type": "string"}}, "required": ["tx_hash"]},
    },
    # ── Uniswap V3 Extended ─────────────────────────────────────────────────────
    {
        "name": "search_pools_by_token",
        "description": "Find all Uniswap V3 pools containing a specific token on X Layer",
        "inputSchema": {
            "type": "object",
            "properties": {"token_address": {"type": "string"}, "limit": {"type": "integer", "default": 10}},
            "required": ["token_address"],
        },
    },
    {
        "name": "get_pool_ohlc",
        "description": "Get daily OHLC candle data for a Uniswap V3 pool on X Layer",
        "inputSchema": {
            "type": "object",
            "properties": {"pool_address": {"type": "string"}, "days": {"type": "integer", "default": 7}},
            "required": ["pool_address"],
        },
    },
    {
        "name": "get_pool_fees",
        "description": "Get cumulative fee revenue and estimated APY for a Uniswap V3 pool on X Layer",
        "inputSchema": {"type": "object", "properties": {"pool_address": {"type": "string"}}, "required": ["pool_address"]},
    },
    {
        "name": "get_uniswap_protocol_stats",
        "description": "Get overall Uniswap V3 protocol statistics on X Layer: pool count, total volume, TVL, fees",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_cross_chain_quote",
        "description": "Get a cross-chain bridge quote via OKX DEX — e.g. ETH on Ethereum to OKB on X Layer",
        "inputSchema": {
            "type": "object",
            "properties": {
                "from_chain_id": {"type": "string", "description": "Source chain ID (e.g. 1 for Ethereum)"},
                "to_chain_id": {"type": "string", "default": "196", "description": "Destination chain ID"},
                "from_token": {"type": "string", "description": "Source token address"},
                "to_token": {"type": "string", "description": "Destination token address"},
                "amount": {"type": "string", "description": "Amount in smallest unit (wei)"},
                "user_wallet": {"type": "string", "description": "User wallet address"},
                "slippage": {"type": "string", "default": "0.5"},
            },
            "required": ["from_chain_id", "from_token", "to_token", "amount", "user_wallet"],
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
        "get_onchain_verdict": lambda: get_onchain_verdict(args["token_address"]),
        "get_total_verdicts": lambda: get_total_verdicts(),
        "get_wallet_net_worth": lambda: get_wallet_net_worth(args["address"]),
        "get_token_detail": lambda: get_token_detail(args["token_address"], args.get("chain_id", "196")),
        "lookup_transaction": lambda: lookup_transaction(args["tx_hash"], args.get("chain_id", "196")),
        "get_supported_tokens": lambda: get_supported_tokens(args.get("chain_id", "196")),
        "get_cross_chain_quote": lambda: get_cross_chain_quote(
            args["from_chain_id"], args.get("to_chain_id", "196"),
            args["from_token"], args["to_token"], args["amount"],
            args["user_wallet"], args.get("slippage", "0.5"),
        ),
        # Security
        "check_address_security": lambda: check_address_security(args["address"]),
        "check_url_safety": lambda: check_url_safety(args["url"]),
        # NFT & DeFi
        "get_nft_holdings": lambda: get_nft_holdings(args["address"], args.get("chain_id", "196")),
        "get_yield_products": lambda: get_yield_products(args.get("chain_id", "196")),
        "get_swap_execution": lambda: get_swap_execution(
            args["from_token"], args["to_token"], args["amount"],
            args["user_wallet"], args.get("chain_id", "196"), args.get("slippage", "0.5"),
        ),
        # OKLink Explorer
        "get_address_info": lambda: get_address_info(args["address"]),
        "get_token_transfers": lambda: get_token_transfers(
            args["address"], args.get("token_contract", ""), args.get("limit", 20)
        ),
        "get_block_list": lambda: get_block_list(args.get("limit", 10)),
        "get_block_detail": lambda: get_block_detail(args["block_number"]),
        "get_pending_transactions": lambda: get_pending_transactions(
            args.get("address", ""), args.get("limit", 20)
        ),
        "get_contract_info": lambda: get_contract_info(args["contract_address"]),
        "estimate_gas": lambda: estimate_gas(
            args["to"], args.get("data", "0x"), args.get("value", "0")
        ),
        "get_token_transfer_list": lambda: get_token_transfer_list(
            args["token_contract"], args.get("limit", 20)
        ),
        "get_rich_list": lambda: get_rich_list(
            args.get("token_contract", ""), args.get("limit", 20)
        ),
        "get_internal_transactions": lambda: get_internal_transactions(args["tx_hash"]),
        # Uniswap V3 Extended
        "search_pools_by_token": lambda: search_pools_by_token(
            args["token_address"], args.get("limit", 10)
        ),
        "get_pool_ohlc": lambda: get_pool_ohlc(args["pool_address"], args.get("days", 7)),
        "get_pool_fees": lambda: get_pool_fees(args["pool_address"]),
        "get_uniswap_protocol_stats": lambda: get_uniswap_protocol_stats(),
    }

    handler = dispatch.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool: {tool_name}", "available_tools": list(dispatch.keys())}

    return await handler()
