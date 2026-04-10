"""
AXON — Neural Intelligence Layer for X Layer
FastAPI server exposing MCP tools as REST + WebSocket endpoints.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("axon.server")

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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# ─── x402 Info Endpoint ──────────────────────────────────────────────────────
@app.get("/api/x402/pricing", tags=["x402"])
async def x402_pricing():
    """Returns x402 payment requirements for premium AXON tools."""
    from .features import PREMIUM_TOOLS, AGENT_WALLET
    return {
        "success": True,
        "protocol": "x402",
        "payment_asset": "OKB",
        "payment_network": "X Layer Mainnet (Chain ID 196)",
        "payment_address": AGENT_WALLET,
        "free_tools": ["get_gas_price", "get_block_info", "get_market_overview", "get_uniswap_top_pools"],
        "premium_tools": PREMIUM_TOOLS,
        "how_to_pay": {
            "step1": "Send OKB to payment_address on X Layer",
            "step2": "Get transaction hash",
            "step3": "Encode as base64 and include in X-PAYMENT header",
            "step4": "Call /mcp/call with X-PAYMENT header",
        }
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
    Premium tools require x402 payment header (X-PAYMENT).
    Returns 402 with payment info if not paid.
    """
    # x402 gate for premium tools
    payment_info = get_x402_payment_info(req.tool_name)
    if payment_info and not verify_x402_payment(x_payment or "", req.tool_name):
        return JSONResponse(
            status_code=402,
            content={
                "error": "Payment Required",
                "x402": payment_info,
                "message": f"Tool '{req.tool_name}' requires micro-payment. "
                           f"Send X-PAYMENT header with OKB tx proof.",
                "free_alternative": "Use /api/balance/{address} for basic wallet info.",
            },
            headers={
                "X-Payment-Required": "true",
                "X-Payment-Address": payment_info["accepts"][0]["payTo"],
                "X-Payment-Asset": "OKB",
                "X-Payment-Network": "xlayer-mainnet",
                "X-Payment-Amount": payment_info["accepts"][0]["maxAmountRequired"],
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


# ─── WebSocket: Live Agent Terminal ───────────────────────────────────────────

@app.websocket("/ws/agent")
async def agent_terminal(ws: WebSocket):
    """
    WebSocket endpoint for real-time agent interaction.
    Send: {"tool": "analyze_wallet", "args": {"address": "0x..."}}
    Receive: streaming tool results + status updates
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

            await ws.send_json({
                "type": "status",
                "message": f"Executing {tool_name}...",
                "tool": tool_name,
            })

            result = await dispatch_tool(tool_name, args)

            await ws.send_json({
                "type": "result",
                "tool": tool_name,
                "data": result,
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


if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    uvicorn.run("src.server:app", host="0.0.0.0", port=port, reload=True)
