"""
AXON — Neural Intelligence Layer for X Layer
FastAPI server exposing MCP tools as REST + WebSocket endpoints.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.websockets import WebSocketState
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
import json
import asyncio
from typing import Any, Optional

from .models import (
    PortfolioRequest, TokenPriceRequest, SwapQuoteRequest,
    WalletAnalysisRequest, CompareWalletsRequest,
    UniswapPoolRequest, TokenAnalyticsRequest,
    ArbitrageRequest, YieldRequest, MCPCallRequest,
)
from .mcp_handler import MCP_TOOLS, dispatch_tool
from .features import (
    start_agent_loop, ACTIVITY_LOG,
    handle_chat, get_x402_payment_info, verify_x402_payment,
)
from .agents.security_agent import scan_token_security, get_smart_money_signals, batch_security_scan

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("axon.server")


def _parse_cors_origins() -> list[str]:
    raw_origins = os.getenv("AXON_CORS_ORIGINS", "*")
    if raw_origins.strip() == "*":
        return ["*"]
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background agent loop on startup."""
    asyncio.create_task(start_agent_loop())
    logger.info("AXON server started — autonomous agent loop running")
    yield
    logger.info("AXON server shutting down")


app = FastAPI(
    title="AXON — Neural Intelligence Layer for X Layer",
    description="MCP-native AI agent skill providing onchain intelligence for X Layer. "
                "Powered by Onchain OS + Uniswap V3 data.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

cors_origins = _parse_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


# ─── Health & Info ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
async def root():
    return {
        "service": "AXON",
        "tagline": "Neural Intelligence Layer for X Layer",
        "version": "1.0.0",
        "chain": "X Layer (Chain ID 196)",
        "mcp_tools": len(MCP_TOOLS),
        "docs": "/docs",
        "mcp_endpoint": "/mcp",
        "chat_endpoint": "/api/chat",
        "agent_activity": "/api/agent/activity",
        "x402_enabled": True,
        "status": "operational",
        "agentic_wallet": os.getenv("AXON_AGENT_WALLET", "0x0000000000000000000000000000000000000000"),
    }


@app.get("/health", tags=["Info"])
@app.head("/health", tags=["Info"])
async def health():
    return {"status": "ok", "service": "AXON"}


# ─── Chat Endpoint ───────────────────────────────────────────────────────────────
from pydantic import BaseModel as _BM

class ChatRequest(_BM):
    question: str

@app.post("/api/chat", tags=["AI Chat"])
async def chat(req: ChatRequest):
    """
    Natural language interface to all AXON tools.
    Ask anything about X Layer in plain English.
    Examples:
      - "What's the gas price right now?"
      - "Find the best yield opportunities"
      - "Analyze wallet 0x..."
      - "What are the top Uniswap pools?"
    """
    result = await handle_chat(req.question)
    return result


# ─── Agent Activity Feed ─────────────────────────────────────────────────────
@app.get("/api/agent/activity", tags=["Agent"])
async def get_agent_activity(limit: int = 20):
    """
    Returns the autonomous agent's recent activity log.
    The agent scans X Layer every 60s for gas, yield, and market signals.
    """
    return {
        "success": True,
        "agent": "AXON Autonomous Agent v1.0",
        "chain": "X Layer",
        "activity_count": len(ACTIVITY_LOG),
        "activities": list(ACTIVITY_LOG)[:limit],
    }


# ─── x402 Info + Verify Endpoints ────────────────────────────────────────────
@app.get("/api/x402/pricing", tags=["x402"])
async def x402_pricing():
    """Returns x402 payment requirements for all premium AXON tools."""
    from .features import PREMIUM_TOOLS, AGENT_WALLET
    return {
        "success": True,
        "protocol": "x402",
        "payment_asset": "OKB",
        "payment_network": "X Layer Mainnet (Chain ID 196)",
        "payment_address": AGENT_WALLET,
        "verification": "on-chain via OKLink API + RPC fallback",
        "replay_protection": True,
        "free_tools": ["get_gas_price", "get_block_info", "get_market_overview", "get_uniswap_top_pools"],
        "premium_tools": PREMIUM_TOOLS,
        "how_to_pay": {
            "step1": f"Send OKB to {AGENT_WALLET} on X Layer (Chain ID 196)",
            "step2": "Copy the tx hash (0x...)",
            "step3": "Include in X-PAYMENT header: X-PAYMENT: 0xYourTxHash",
            "step4": "POST /mcp/call — AXON verifies tx on OKLink before executing",
        },
        "header_formats": [
            "X-PAYMENT: 0x<64-hex-chars>  (raw tx hash)",
            "X-PAYMENT: <base64('0x...')>  (base64 encoded)",
            "X-PAYMENT: <base64(JSON{tx:'0x...'})>  (base64 JSON)",
        ],
    }


from pydantic import BaseModel as _VerifyBM
class VerifyPaymentRequest(_VerifyBM):
    tx_hash: str
    tool_name: str = "analyze_wallet"

@app.post("/api/x402/verify", tags=["x402"])
async def x402_verify(req: VerifyPaymentRequest):
    """
    Pre-check: verify an OKB payment tx on X Layer before calling a premium tool.
    Use this to confirm your payment will be accepted before submitting the MCP call.
    """
    from .features import PREMIUM_TOOLS, AGENT_WALLET
    from .tools.xlayer import verify_tx_on_xlayer

    if req.tool_name not in PREMIUM_TOOLS:
        return {
            "valid": True,
            "message": f"{req.tool_name} is a free tool — no payment needed",
        }

    required_okb = PREMIUM_TOOLS[req.tool_name]["price_okb"]
    result = await verify_tx_on_xlayer(
        tx_hash=req.tx_hash,
        expected_recipient=AGENT_WALLET,
        min_amount_okb=required_okb,
    )
    return {
        "success": True,
        "valid": result["valid"],
        "reason": result.get("reason", ""),
        "verification": result,
        "tool": req.tool_name,
        "required_okb": required_okb,
        "payment_address": AGENT_WALLET,
    }


# ─── MCP Protocol Endpoints ────────────────────────────────────────────────────

@app.get("/mcp/tools", tags=["MCP"])
async def list_tools():
    """MCP: List all available tools (skills) this server exposes."""
    return {"tools": MCP_TOOLS}


@app.post("/mcp/call", tags=["MCP"])
async def call_tool(
    req: MCPCallRequest,
    request: Request,
    x_payment: Optional[str] = Header(None, alias="X-PAYMENT"),
):
    """
    MCP: Call a specific tool by name with arguments.
    Premium tools require x402 payment (X-PAYMENT header = on-chain tx hash).
    AXON queries OKLink to confirm the tx on X Layer before executing.
    Returns 402 with full payment info if not paid or payment invalid.
    """
    payment_info = get_x402_payment_info(req.tool_name)
    if payment_info:
        paid, reason, verification = await verify_x402_payment(x_payment or "", req.tool_name)
        if not paid:
            return JSONResponse(
                status_code=402,
                content={
                    "error": "Payment Required",
                    "rejection_reason": reason,
                    "x402": payment_info,
                    "verification": verification,
                    "message": (
                        f"Tool '{req.tool_name}' requires OKB payment on X Layer. "
                        f"Rejection: {reason}"
                    ),
                    "free_alternative": "GET /api/balance/{address} for basic wallet info.",
                },
                headers={
                    "X-Payment-Required": "true",
                    "X-Payment-Address": payment_info["accepts"][0]["payTo"],
                    "X-Payment-Asset": "OKB",
                    "X-Payment-Network": "xlayer-mainnet",
                    "X-Payment-Amount": payment_info["accepts"][0]["maxAmountRequired"],
                    "X-Payment-Rejection": reason[:120] if reason else "",
                }
            )

    logger.info(f"MCP call: {req.tool_name} args={list(req.arguments.keys())}")
    result = await dispatch_tool(req.tool_name, req.arguments)
    return {"tool": req.tool_name, "result": result}


# ─── Portfolio & Wallet APIs ───────────────────────────────────────────────────

@app.post("/api/portfolio", tags=["Portfolio"])
async def get_portfolio(req: PortfolioRequest):
    """Get token balances and USD values for a wallet on X Layer."""
    from .tools.onchain_os import get_wallet_portfolio
    return await get_wallet_portfolio(req.address, req.chain_id)


@app.post("/api/analyze", tags=["Portfolio"])
async def analyze_wallet_endpoint(req: WalletAnalysisRequest):
    """Full AI-powered wallet analysis: risk score, portfolio health, recommendations."""
    from .agents.portfolio_agent import analyze_wallet
    return await analyze_wallet(req.address, req.include_ai_insights, req.chain_id)


@app.post("/api/compare", tags=["Portfolio"])
async def compare_wallets_endpoint(req: CompareWalletsRequest):
    """Compare two X Layer wallets side-by-side with AI analysis."""
    from .agents.portfolio_agent import compare_wallets
    return await compare_wallets(req.address_a, req.address_b)


@app.get("/api/balance/{address}", tags=["Portfolio"])
async def get_balance(address: str):
    """Get native OKB balance for any X Layer address."""
    from .tools.xlayer import get_wallet_balance
    return await get_wallet_balance(address)


@app.get("/api/transactions/{address}", tags=["Portfolio"])
async def get_transactions(address: str, limit: int = 20):
    """Get recent transaction history for an X Layer wallet."""
    from .tools.onchain_os import get_transaction_history
    return await get_transaction_history(address, "196", limit)


@app.get("/api/defi/{address}", tags=["Portfolio"])
async def get_defi(address: str):
    """Get active DeFi positions for an X Layer wallet."""
    from .tools.onchain_os import get_defi_positions
    return await get_defi_positions(address)


# ─── Market & Token APIs ───────────────────────────────────────────────────────

@app.get("/api/market", tags=["Market"])
async def market_overview():
    """X Layer market snapshot: gas, blocks, top pools, key prices."""
    from .agents.market_agent import get_market_overview
    return await get_market_overview()


@app.post("/api/token/price", tags=["Market"])
async def token_price(req: TokenPriceRequest):
    """Real-time price data for any token on X Layer."""
    from .tools.onchain_os import get_token_price
    return await get_token_price(req.token_address, req.chain_id)


@app.get("/api/token/{token_address}/analytics", tags=["Market"])
async def token_analytics(token_address: str):
    """7-day OHLC, volume, and liquidity analytics via Uniswap V3."""
    from .tools.uniswap import get_uniswap_token_analytics
    return await get_uniswap_token_analytics(token_address)


@app.get("/api/gas", tags=["Market"])
async def gas_price():
    """Current gas price on X Layer in gwei."""
    from .tools.xlayer import get_gas_price
    return await get_gas_price()


@app.get("/api/block", tags=["Market"])
async def latest_block():
    """Latest block info from X Layer."""
    from .tools.xlayer import get_block_info
    return await get_block_info("latest")


# ─── Uniswap APIs ─────────────────────────────────────────────────────────────

@app.get("/api/uniswap/pools", tags=["Uniswap"])
async def top_pools(limit: int = 10):
    """Top Uniswap V3 pools on X Layer by TVL."""
    from .tools.uniswap import get_uniswap_top_pools
    return await get_uniswap_top_pools(limit)


@app.post("/api/uniswap/pool", tags=["Uniswap"])
async def pool_data(req: UniswapPoolRequest):
    """Uniswap V3 pool stats for a specific token pair."""
    from .tools.uniswap import get_uniswap_pool_data
    return await get_uniswap_pool_data(req.token0, req.token1, req.fee)


@app.get("/api/uniswap/yield", tags=["Uniswap"])
async def yield_opportunities(min_apy: float = 5.0):
    """Best yield farming opportunities on X Layer via Uniswap V3."""
    from .agents.market_agent import get_yield_opportunities
    return await get_yield_opportunities(min_apy)


# ─── Swap APIs ─────────────────────────────────────────────────────────────────

@app.post("/api/swap/quote", tags=["Swap"])
async def swap_quote(req: SwapQuoteRequest):
    """Best swap route across all DEXes on X Layer (OKX aggregator)."""
    from .tools.onchain_os import get_swap_quote_onchain_os
    return await get_swap_quote_onchain_os(
        req.from_token, req.to_token, req.amount, req.chain_id, req.slippage
    )


# ─── Intelligence APIs ─────────────────────────────────────────────────────────

@app.post("/api/arbitrage", tags=["Intelligence"])
async def arbitrage_scan(req: ArbitrageRequest):
    """Scan for arbitrage opportunities for a token on X Layer."""
    from .agents.market_agent import find_arbitrage_opportunities
    return await find_arbitrage_opportunities(req.token_address, req.amount_usd)


@app.get("/api/chain", tags=["Intelligence"])
async def xlayer_chain_info():
    """X Layer chain info from Onchain OS."""
    from .tools.onchain_os import get_xlayer_stats
    return await get_xlayer_stats()


# ─── Security Intelligence APIs ────────────────────────────────────────────────

@app.get("/api/token/{token_address}/security", tags=["Security"])
async def token_security_scan(token_address: str):
    """
    Full 5-stage security analysis for any X Layer token.
    Returns risk score (0-100), honeypot flags, holder concentration,
    liquidity safety, contract verification, and activity anomalies.
    """
    return await scan_token_security(token_address)


@app.get("/api/smart-money/signals", tags=["Security"])
async def smart_money_signals(limit: int = 10):
    """
    Identify tokens with smart money accumulation signals on X Layer.
    Uses volume/TVL velocity cross-analysis on Uniswap V3 pools.
    """
    return await get_smart_money_signals(limit)


class BatchScanRequest(_BM):
    token_addresses: list[str]

@app.post("/api/security/batch", tags=["Security"])
async def batch_token_security(req: BatchScanRequest):
    """
    Batch security scan for up to 10 tokens in parallel.
    Returns risk-sorted leaderboard — highest risk first.
    """
    return await batch_security_scan(req.token_addresses)


# ─── Onchain OS Extended Endpoints ───────────────────────────────────────────

from .tools.onchain_os import (
    get_wallet_net_worth, get_token_detail,
    lookup_transaction, get_supported_tokens, get_cross_chain_quote,
)

@app.get("/api/wallet/{address}/net-worth", tags=["Portfolio"])
async def wallet_net_worth(address: str):
    """Total portfolio value across all chains."""
    return await get_wallet_net_worth(address)

@app.get("/api/token/{token_address}/detail", tags=["Token"])
async def token_detail(token_address: str, chain_id: str = "196"):
    """Rich token metadata: holders, FDV, socials, description."""
    return await get_token_detail(token_address, chain_id)

@app.get("/api/tx/{tx_hash}", tags=["Explorer"])
async def transaction_lookup(tx_hash: str, chain_id: str = "196"):
    """Decode any transaction hash on X Layer."""
    return await lookup_transaction(tx_hash, chain_id)

@app.get("/api/tokens/supported", tags=["DEX"])
async def supported_tokens(chain_id: str = "196"):
    """All tokens supported by OKX DEX aggregator on X Layer."""
    return await get_supported_tokens(chain_id)

class CrossChainQuoteRequest(_BM):
    from_chain_id: str
    to_chain_id: str = "196"
    from_token: str
    to_token: str
    amount: str
    user_wallet: str
    slippage: str = "0.5"

@app.post("/api/bridge/quote", tags=["DEX"])
async def cross_chain_quote(req: CrossChainQuoteRequest):
    """Cross-chain bridge quote via OKX DEX aggregator."""
    return await get_cross_chain_quote(
        req.from_chain_id, req.to_chain_id,
        req.from_token, req.to_token,
        req.amount, req.user_wallet, req.slippage,
    )


# ─── OKLink Explorer Endpoints ────────────────────────────────────────────────

from .tools.oklink import (
    get_address_info, get_block_list, get_block_detail, get_contract_info,
)

@app.get("/api/address/{address}/info", tags=["Explorer"])
async def address_info(address: str):
    """Address info via OKLink: balance, tx count, entity tag, first/last TX."""
    return await get_address_info(address)

@app.get("/api/blocks/latest", tags=["Explorer"])
async def latest_blocks(limit: int = 10):
    """Most recent blocks on X Layer via OKLink."""
    return await get_block_list(limit)

@app.get("/api/block/{block_number}", tags=["Explorer"])
async def block_detail(block_number: str):
    """Full details for a specific block number on X Layer via OKLink."""
    return await get_block_detail(block_number)

@app.get("/api/contract/{address}/info", tags=["Explorer"])
async def contract_info(address: str):
    """Contract verification, creator, deploy TX via OKLink."""
    return await get_contract_info(address)


# ─── Security Hub Endpoints ───────────────────────────────────────────────────

from .tools.onchain_os import check_address_security, check_url_safety

@app.get("/api/address/{address}/security-check", tags=["Security"])
async def address_security_check(address: str):
    """OKX on-chain address risk check: blacklisted, phishing, contract risk."""
    return await check_address_security(address)

class UrlSafetyRequest(_BM):
    url: str

@app.post("/api/url/safety", tags=["Security"])
async def url_safety_check(req: UrlSafetyRequest):
    """OKX phishing/malicious URL safety check."""
    return await check_url_safety(req.url)


# ─── DeFi Hub Endpoints ───────────────────────────────────────────────────────

from .tools.onchain_os import get_nft_holdings, get_yield_products
from .tools.uniswap import get_uniswap_protocol_stats, get_pool_fees

@app.get("/api/address/{address}/nft", tags=["DeFi"])
async def nft_holdings(address: str):
    """NFT holdings for a wallet on X Layer via OKX Onchain OS."""
    return await get_nft_holdings(address)

@app.get("/api/defi/yield-products", tags=["DeFi"])
async def yield_products():
    """Available yield/farming products on X Layer via OKX Onchain OS."""
    return await get_yield_products()

@app.get("/api/uniswap/stats", tags=["Uniswap"])
async def uniswap_protocol_stats():
    """Uniswap V3 protocol-level stats: total TVL, volume, fees on X Layer."""
    return await get_uniswap_protocol_stats()

@app.get("/api/uniswap/pool/{pool_address}/fees", tags=["Uniswap"])
async def pool_fees(pool_address: str):
    """Fee revenue and estimated APY for a specific Uniswap V3 pool."""
    return await get_pool_fees(pool_address)


# ─── WebSocket: Live Agent Terminal ───────────────────────────────────────────

# Progress step sequences for known long-running tools
_TOOL_STEPS: dict[str, list[str]] = {
    "scan_token_security": [
        "Querying OKX Security API (honeypot, tax flags)...",
        "Fetching Onchain OS advanced token info...",
        "Checking DexScreener pair data...",
        "Querying Uniswap V3 subgraph (TVL, OHLC)...",
        "Fetching OKLink holder concentration...",
        "Running sell-simulation probe...",
        "Computing weighted risk score...",
    ],
    "analyze_wallet": [
        "Loading wallet token balances via Onchain OS...",
        "Fetching transaction history...",
        "Scanning DeFi positions...",
        "Computing portfolio risk score...",
        "Generating AI narrative...",
    ],
    "get_market_overview": [
        "Fetching gas price from X Layer RPC...",
        "Reading latest block data...",
        "Querying top Uniswap V3 pools...",
        "Aggregating market snapshot...",
    ],
    "get_smart_money_signals": [
        "Loading top 50 Uniswap V3 pools...",
        "Computing volume/TVL velocity ratios...",
        "Ranking accumulation signals...",
    ],
    "find_arbitrage_opportunities": [
        "Fetching swap quotes across DEX routes...",
        "Comparing price spreads...",
        "Ranking arbitrage opportunities by profit...",
    ],
}


@app.websocket("/ws/agent")
async def agent_terminal(ws: WebSocket):
    """
    WebSocket endpoint for real-time agent interaction with streaming progress.
    Send: {"tool": "analyze_wallet", "args": {"address": "0x..."}}
    Receive: start → progress (step-by-step) → result
    """
    await ws.accept()
    logger.info("Agent terminal connected")

    try:
        while True:
            msg = await ws.receive_json()
            tool_name = msg.get("tool", "")
            args = msg.get("args", {})

            if not tool_name:
                await ws.send_json({"type": "error", "message": "No tool specified"})
                continue

            steps = _TOOL_STEPS.get(tool_name, [f"Executing {tool_name}..."])
            total = len(steps)

            await ws.send_json({
                "type": "start",
                "message": f"Starting {tool_name}",
                "tool": tool_name,
                "total_steps": total,
            })

            # Run tool in background task; stream progress while it runs
            task = asyncio.create_task(dispatch_tool(tool_name, args))
            step_idx = 0
            interval = max(0.6, 8.0 / total)  # spread steps across ~8s max

            while not task.done():
                if step_idx < total:
                    await ws.send_json({
                        "type": "progress",
                        "tool": tool_name,
                        "message": steps[step_idx],
                        "step": step_idx + 1,
                        "total_steps": total,
                        "pct": round((step_idx + 1) / total * 100),
                    })
                    step_idx += 1
                try:
                    await asyncio.wait_for(asyncio.shield(task), timeout=interval)
                except asyncio.TimeoutError:
                    pass

            result = task.result()

            await ws.send_json({
                "type": "result",
                "tool": tool_name,
                "data": result,
                "steps_shown": step_idx,
            })

    except WebSocketDisconnect:
        logger.info("Agent terminal disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            if ws.client_state == WebSocketState.CONNECTED:
                await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass


# ─── /llms.txt — LLM & AI Agent Context File ─────────────────────────────────

from fastapi.responses import PlainTextResponse

@app.get("/llms.txt", tags=["Info"], response_class=PlainTextResponse)
async def llms_txt():
    """Structured context file for LLMs and AI agents to discover AXON capabilities."""
    agent_wallet = os.getenv("AXON_AGENT_WALLET", "0xDb82c0d91E057E05600C8F8dc836bEb41da6df14")
    tool_count = len(MCP_TOOLS)
    return f"""# AXON — Neural Intelligence Layer for X Layer
# Version: 1.0 | Chain: X Layer (Chain ID 196)
# Purpose: Enable AI agents to query, scan, and transact on X Layer via 45 MCP tools

## IDENTITY

name: AXON
tagline: Neural Intelligence Layer for X Layer
network: X Layer Mainnet (Chain ID 196)
protocol: x402 (HTTP 402 micropayments in OKB)
currency: OKB
mcp_tools: {tool_count}
website: https://axon-six-amber.vercel.app
api: https://axon-onld.onrender.com
docs: https://axon-onld.onrender.com/docs
plugin_store_pr: https://github.com/okx/plugin-store/pull/93
github: https://github.com/MUTHUKUMARAN-K-1/axon

## WHAT IS THIS

AXON is a production MCP skill server. AI agents (Claude, GPT, LangChain, or any HTTP client) can:
1. Discover 45 tools via GET /mcp/tools
2. Call any tool via POST /mcp/call with JSON arguments
3. Pay for premium tools using OKB on X Layer (x402 protocol)
4. Read security verdicts published on-chain at AxonVerdictLedger
5. Register as an agent and track activity on the leaderboard

This is designed for AI agents. Agents do not need an account — only an X Layer wallet for premium tools.

## QUICK START (3 steps)

# 1. List all available tools
GET https://axon-onld.onrender.com/mcp/tools

# 2. Call a free tool
POST https://axon-onld.onrender.com/mcp/call
Content-Type: application/json
{{"tool_name": "get_gas_price", "arguments": {{}}}}

# 3. Call a premium tool (x402)
# First send 0.001 OKB to {agent_wallet} on X Layer (Chain ID 196)
# Then include the tx hash in the X-PAYMENT header:
POST https://axon-onld.onrender.com/mcp/call
X-PAYMENT: 0x<your_tx_hash>
Content-Type: application/json
{{"tool_name": "analyze_wallet", "arguments": {{"address": "0x..."}}}}

## API REFERENCE

Base URL: https://axon-onld.onrender.com

### MCP (primary interface)
GET  /mcp/tools                  List all 45 tools with schemas
POST /mcp/call                   Call any tool by name

### Security
GET  /api/token/{{address}}/security    6-source token security scan (honeypot, tax, holders, DEX, DeFi)
POST /api/security/batch               Batch scan up to 10 tokens
GET  /api/address/{{address}}/security-check  Address blacklist/phishing check

### On-Chain Oracle
GET  /mcp/call  {{get_onchain_verdict, token_address}}   Read verdict from AxonVerdictLedger
GET  /mcp/call  {{get_total_verdicts}}                   Total verdicts published on-chain

### Portfolio
GET  /api/balance/{{address}}          Native OKB balance
GET  /api/wallet/{{address}}/net-worth Total portfolio value (all chains)
GET  /api/transactions/{{address}}     Recent transaction history

### Market & DeFi
GET  /api/gas                    Current gas price (gwei)
GET  /api/block                  Latest block info
GET  /api/market                 Full market snapshot (gas + pools + prices)
GET  /api/uniswap/pools          Top Uniswap V3 pools by TVL
GET  /api/uniswap/yield          Yield opportunities above min APY

### Agent System
POST /api/agents                 Register an AI agent (name + wallet)
GET  /api/agents                 List all registered agents
GET  /api/leaderboard            Agent rankings by scans completed
GET  /api/tasks                  Discover tasks AI agents can complete on X Layer

### x402 Payments
GET  /api/x402/pricing           Premium tool prices and payment address
POST /api/x402/verify            Pre-verify a payment tx before calling premium tool

### Natural Language
POST /api/chat                   Ask AXON anything in plain English → auto-routed to the right tool

## TOOL CATEGORIES

| Category      | Count | Premium | Description |
|---------------|-------|---------|-------------|
| Security      | 5     | No      | Token scans, address checks, smart money signals |
| Portfolio     | 7     | 1x402   | Wallet balances, DeFi positions, NFTs, net worth |
| Market        | 5     | No      | Gas, blocks, prices, market overview |
| Uniswap V3    | 7     | No      | Pools, TVL, OHLC, yield, protocol stats |
| OKLink        | 10    | No      | Explorer: blocks, contracts, transfers, rich list |
| Onchain OS    | 7     | No      | OKX DEX, swap routing, cross-chain bridge |
| Intelligence  | 2     | 1x402   | Yield discovery, arbitrage scanner |
| AI Chat       | 1     | No      | Natural language → MCP tool router |
| On-Chain Oracle | 2   | No      | Read/count verdicts from AxonVerdictLedger |

## ON-CHAIN CONTRACTS

AxonVerdictLedger (security oracle):
  address: 0x0191d5ada56672507fdb283ac59d45bde08a53f8
  network: X Layer Mainnet (196)
  interface: publishVerdict(token,risk,flags,hash) + getVerdict(token) + totalVerdicts()
  note: Every scan_token_security call writes a verdict on-chain — permissionless reads

AxonConfidenceBond (skin-in-the-game):
  address: 0xe164011de202eb0ebf5f01ee5d9851c801a9c675
  interface: lockBond(token) + challenge(token) + releaseExpired(token)
  note: AXON locks 0.001 OKB per SAFE verdict. Challengers win bond if verdict flips within 7 days.

Agentic Wallet (x402 recipient):
  address: {agent_wallet}
  network: X Layer Mainnet (196)
  note: Send OKB here for premium tool access. Include tx hash in X-PAYMENT header.

## VERIFICATION TYPES (for /api/tasks)

  api_response_match  proof=JSON   server fetches live data, compares fields
  data_match          proof=JSON   validates against on-chain state
  text_quality        proof=text   word count + keywords + SHA-256 dedup
  text_contains       proof=text   pattern match against expected output

## RATE LIMITS

  Free tools: unlimited (no auth required)
  Premium tools: 1 x402 payment per call (OKB on X Layer)
  Chat endpoint: no limit

## ERROR CODES

  400 — Bad request (missing tool_name or arguments)
  402 — Payment Required (x402 — send OKB to agentic wallet, include tx hash)
  404 — Tool not found
  422 — Validation error (wrong argument types)
  500 — Server error (upstream API timeout)

## AGENT ECONOMY

Agents build reputation through:
  - Scans completed → visible on GET /api/leaderboard
  - Tasks completed → use GET /api/tasks to discover challenges
  - Register: POST /api/agents with name + wallet

## RECOMMENDED AGENT FLOW

1. DISCOVER  → GET /mcp/tools (see all 45 tools)
2. FREE SCAN → POST /mcp/call {{tool_name: "scan_token_security", arguments: {{token_address: "0x..."}}}}
3. ONCHAIN   → POST /mcp/call {{tool_name: "get_onchain_verdict", arguments: {{token_address: "0x..."}}}}
4. REGISTER  → POST /api/agents {{name: "my-agent", wallet: "0x..."}}
5. TASKS     → GET /api/tasks (discover what to do next)
6. PREMIUM   → Send 0.001 OKB → GET /api/x402/pricing for details

## LINKS

  API:         https://axon-onld.onrender.com
  Docs:        https://axon-onld.onrender.com/docs
  Frontend:    https://axon-six-amber.vercel.app
  Tools:       https://axon-onld.onrender.com/mcp/tools
  Leaderboard: https://axon-onld.onrender.com/api/leaderboard
  Tasks:       https://axon-onld.onrender.com/api/tasks
  LLMs.txt:    https://axon-onld.onrender.com/llms.txt
  Plugin PR:   https://github.com/okx/plugin-store/pull/93
  GitHub:      https://github.com/MUTHUKUMARAN-K-1/axon
"""


# ─── Agent Registry & Leaderboard ─────────────────────────────────────────────

from pydantic import BaseModel as _AgentBM

class AgentRegisterRequest(_AgentBM):
    name: str
    wallet: str

@app.post("/api/agents", tags=["Agents"])
async def register_agent_endpoint(req: AgentRegisterRequest):
    """
    Register an AI agent by wallet address.
    Tracked in the in-memory registry — appears on the leaderboard as the agent completes scans.
    """
    from .features import register_agent as _register
    if not req.wallet.startswith("0x") or len(req.wallet) != 42:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="wallet must be a valid 0x address (42 chars)")
    agent = _register(wallet=req.wallet, name=req.name)
    return {"success": True, "agent": agent, "message": f"Agent '{req.name}' registered. Complete tasks to climb the leaderboard."}


@app.get("/api/agents", tags=["Agents"])
async def list_agents():
    """List all registered AI agents and their scan counts."""
    from .features import AGENT_REGISTRY
    agents = sorted(AGENT_REGISTRY.values(), key=lambda a: a["scans"], reverse=True)
    return {"success": True, "total": len(agents), "agents": agents}


@app.get("/api/leaderboard", tags=["Agents"])
async def leaderboard(limit: int = 20):
    """
    AI agent leaderboard — ranked by security scans completed.
    Agents register via POST /api/agents then build reputation through tool usage.
    """
    from .features import get_leaderboard as _lb
    board = _lb(limit)
    return {
        "success": True,
        "total_agents": len(board),
        "metric": "scans_completed",
        "leaderboard": board,
        "note": "Register at POST /api/agents. Scans increment automatically when you call scan_token_security with your wallet.",
    }


# ─── Task Discovery ────────────────────────────────────────────────────────────

@app.get("/api/tasks", tags=["Tasks"])
async def list_tasks(category: str = None, difficulty: str = None):
    """
    Discover tasks AI agents can complete using AXON tools on X Layer.
    Filter by category (security, defi, onchain, portfolio, intelligence, ai) or difficulty (easy, medium, hard).
    """
    from .features import AXON_TASKS
    tasks = AXON_TASKS
    if category:
        tasks = [t for t in tasks if t["category"] == category]
    if difficulty:
        tasks = [t for t in tasks if t["difficulty"] == difficulty]
    return {
        "success": True,
        "total": len(tasks),
        "tasks": tasks,
        "how_to_complete": "Use POST /mcp/call with the tool listed in each task's 'tool' field.",
        "register_first": "POST /api/agents with your wallet to appear on the leaderboard.",
    }


@app.get("/api/tasks/{task_id}", tags=["Tasks"])
async def get_task(task_id: str):
    """Get full details for a specific AXON task by ID (e.g. axon-001)."""
    from .features import AXON_TASKS
    task = next((t for t in AXON_TASKS if t["id"] == task_id), None)
    if not task:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"success": True, "task": task}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    uvicorn.run("src.server:app", host="0.0.0.0", port=port, reload=True)
