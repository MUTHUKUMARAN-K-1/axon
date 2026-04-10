# AXON — Neural Intelligence Layer for X Layer

> **Give your AI agents onchain senses.**
> AXON is a reusable MCP skill that connects any AI agent to X Layer's onchain reality — portfolio intelligence, DeFi analytics, swap routing, yield discovery, natural language querying, and x402 micro-payments through a standardized MCP interface.

[![Live Demo](https://img.shields.io/badge/Live-axon--six--amber.vercel.app-brightgreen)](https://axon-six-amber.vercel.app)
[![API](https://img.shields.io/badge/API-axon--onld.onrender.com-blue)](https://axon-onld.onrender.com/docs)
[![X Layer](https://img.shields.io/badge/Chain-X%20Layer%20196-blueviolet)](https://www.okx.com/xlayer)
[![Onchain OS](https://img.shields.io/badge/Powered%20by-Onchain%20OS-orange)](https://www.okx.com/web3/build)
[![Uniswap V3](https://img.shields.io/badge/DEX-Uniswap%20V3-pink)](https://app.uniswap.org)
[![MCP](https://img.shields.io/badge/Protocol-MCP%2017%20Tools-cyan)](https://axon-onld.onrender.com/mcp/tools)
[![x402](https://img.shields.io/badge/x402-Payment%20Gate-yellow)](https://axon-onld.onrender.com/api/x402/pricing)

---

## Project Introduction

AI agents can reason, plan, and execute — but they are **blind to onchain activity** by default. There is no standardized way for an AI agent to ask: *"What's in this wallet? What's the gas price? Where's the best yield on X Layer right now?"*

**AXON solves this.** It is named after the axon — the neural transmitter that carries signals between neurons. AXON is the transmitter between AI agents and X Layer's onchain reality.

AXON exposes **17 production-ready MCP tools** any Claude, GPT, or open-source agent can call to:

- 💬 **Ask in plain English** — "What's the best yield right now?" → AXON routes, executes, and answers
- 🔍 Analyze wallet portfolios with AI-generated risk scores (0–100)
- 📊 Monitor real-time gas, blocks, and X Layer network health
- 🦄 Query Uniswap V3 pool data, 7-day OHLC, and yield APY
- 🔄 Find the best swap route via OKX DEX aggregator across all X Layer DEXes
- 🌾 Scan for yield farming and arbitrage opportunities
- 🤖 Autonomous background agent — scans X Layer every 60s, logs gas alerts and yield signals
- 💰 **x402 micro-payment gate** — premium tools require OKB payment on X Layer

**Arena:** Skills Arena | **Bonus:** Deployed on X Layer (Chain ID 196)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    AI AGENT LAYER                            │
│         Claude / GPT / Any MCP-compatible Agent             │
└───────────────────────┬──────────────────────────────────────┘
                        │  MCP Protocol (REST + WebSocket)
┌───────────────────────▼──────────────────────────────────────┐
│               AXON MCP SERVER  (FastAPI + Python)            │
│                                                              │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Portfolio Agent  │  │ Market Agent │  │  Features      │  │
│  │ - Risk scoring  │  │ - Yield scan │  │  - Chat/NLP    │  │
│  │ - AI analysis   │  │ - Arbitrage  │  │  - Agent Loop  │  │
│  │ - Wallet compare│  │ - Overview   │  │  - x402 Gate   │  │
│  └────────┬────────┘  └──────┬───────┘  └───────┬────────┘  │
│           │                  │                   │            │
│  ┌────────▼──────────────────▼───────────────────▼────────┐  │
│  │           MCP TOOL REGISTRY  (17 tools)                 │  │
│  └────────┬───────────────────────────────┬───────────────┘  │
└───────────┼───────────────────────────────┼──────────────────┘
            │                               │
┌───────────▼───────────┐    ┌──────────────▼───────────────┐
│   OKX Onchain OS API  │    │  X Layer RPC + OKLink API    │
│  Wallet balances      │    │  Block data / Gas prices     │
│  Token prices         │    │  Contract detection          │
│  DeFi positions       │    │  Address summaries           │
│  DEX aggregator       │    │  Native OKB balance          │
└───────────┬───────────┘    └──────────────────────────────┘
            │
┌───────────▼───────────────────────────────────────────────┐
│             Uniswap V3 on X Layer (The Graph)              │
│   Pool TVL / Volume / Fees  │  Token OHLC (7d)            │
│   Yield APY estimation      │  Swap routing               │
└───────────────────────────────────────────────────────────┘
            │
┌───────────▼───────────────────────────────────────────────┐
│         AXON Frontend  (React 18 + Vite)                   │
│  Dashboard  │  Portfolio  │  Analytics  │  Swap  │ Agent  │
│  Ask AXON (Chat) │  Agent Activity Feed                    │
└───────────────────────────────────────────────────────────┘
```

---

## Agentic Wallet

| Field | Value |
|-------|-------|
| **Address** | `0xDb82c0d91E057E05600C8F8dc836bEb41da6df14` |
| **Network** | X Layer Mainnet (Chain ID: 196) |
| **Role** | AXON's onchain identity — x402 payment recipient for premium tool calls |
| **Explorer** | [View on OKLink](https://www.oklink.com/xlayer/address/0xDb82c0d91E057E05600C8F8dc836bEb41da6df14) |

---

## Onchain OS / Uniswap Skill Usage

### Onchain OS Modules (6 core modules)

| Module | Usage | Endpoint |
|--------|-------|----------|
| **Wallet Asset API** | All token balances + USD values for any X Layer wallet | `GET /api/v5/wallet/asset/all-token-balances-by-address` |
| **Token Price API** | Real-time price, 24h change, market cap, volume | `GET /api/v5/wallet/token/price` |
| **Transaction History** | Recent tx analysis for risk assessment | `GET /api/v5/wallet/post-transaction/transactions-by-address` |
| **DeFi Positions API** | Active DeFi positions, staking, liquidity | `GET /api/v5/wallet/defi/investment/positions` |
| **DEX Aggregator** | Best swap route across all X Layer DEXes | `GET /api/v5/dex/aggregator/quote` |
| **Chain API** | X Layer network metadata and supported chains | `GET /api/v5/wallet/chain/supported-chains` |

### Uniswap V3 Integration (5 features)

| Feature | Implementation |
|---------|----------------|
| **Top pools by TVL** | The Graph subgraph — `pools` query ordered by TVL |
| **Token 7-day OHLC** | Subgraph `tokenDayData` — open/high/low/close/volume |
| **Pool pair analytics** | Fee APY estimation from volume/TVL ratios |
| **Swap routing** | OKX DEX aggregator routing through Uniswap V3 |
| **Yield opportunities** | Scanner finding pools above configurable APY threshold |

---

## MCP Tools — Complete List (17 tools)

| Tool | Category | Description |
|------|----------|-------------|
| `get_wallet_portfolio` | Portfolio | All token balances + USD values on X Layer |
| `get_transaction_history` | Portfolio | Recent wallet transactions with type/value |
| `get_defi_positions` | Portfolio | Active DeFi positions (liquidity, staking, lending) |
| `get_native_balance` | Portfolio | Native OKB balance for any address |
| `analyze_wallet` | AI 🔒 x402 | **AI-powered** full analysis: risk score + recommendations |
| `compare_wallets` | AI 🔒 x402 | Side-by-side AI comparison of two wallets |
| `get_token_price` | Market | Real-time price, 24h change, market cap |
| `get_market_overview` | Market | Gas + block + top pools + key prices snapshot |
| `get_gas_price` | Market | Current gas price in gwei |
| `get_block_info` | Market | Latest block data and gas utilization |
| `get_xlayer_stats` | Market | X Layer chain metadata |
| `get_uniswap_pool_data` | Uniswap | Pool TVL/volume/fees for any token pair |
| `get_uniswap_top_pools` | Uniswap | Top X Layer pools ranked by TVL |
| `get_uniswap_token_analytics` | Uniswap | 7-day OHLC + liquidity for any token |
| `get_swap_quote` | Swap | Best route via OKX DEX aggregator |
| `get_yield_opportunities` | Intelligence | Yield farming above configurable APY threshold |
| `find_arbitrage_opportunities` | Intelligence 🔒 x402 | Price discrepancy scanner across routes |

> 🔒 x402 = Premium tool. Requires OKB micro-payment on X Layer. See `/api/x402/pricing`.

---

## New Features (v1.1)

### 💬 Ask AXON — Natural Language Interface
Chat with AXON in plain English. No API knowledge needed.

```
User: "What's the gas price right now?"
AXON: Calls get_gas_price() → "Gas is currently 0.02 gwei — 98% cheaper than Ethereum. 
      This is a great time to execute swaps."

User: "Find yield opportunities above 10% APY"
AXON: Calls get_yield_opportunities() → Lists pools with APY, TVL, risk level

User: "Analyze wallet 0xDb82c..."
AXON: Calls analyze_wallet() → Risk score, holdings, AI recommendations
```

Endpoint: `POST /api/chat` `{ "question": "your question" }`

### 🤖 Autonomous Agent Loop
AXON runs a background agent every 60 seconds that:
- Monitors X Layer gas prices (alerts when < 0.05 gwei)
- Scans yield opportunities (flags when APY > 8%)
- Tracks block health and gas utilization
- Logs all decisions to a live activity feed

Endpoint: `GET /api/agent/activity`  
Frontend: `/activity` page — live auto-refreshing event feed

### 💰 x402 Micro-Payment Gate
Premium tools require OKB payment on X Layer before execution.

```http
# Without payment — returns 402
POST /mcp/call
{ "tool_name": "analyze_wallet", "arguments": {"address": "0x..."} }

→ 402 Payment Required
  X-Payment-Address: 0xDb82c0d91E057E05600C8F8dc836bEb41da6df14
  X-Payment-Amount: 0.001
  X-Payment-Asset: OKB
  X-Payment-Network: xlayer-mainnet

# With payment — executes and returns result
POST /mcp/call
X-PAYMENT: <base64-encoded-tx-hash>
{ "tool_name": "analyze_wallet", "arguments": {"address": "0x..."} }
```

Pricing info: `GET /api/x402/pricing`

---

## Working Mechanics

### MCP Integration (any AI agent)
```bash
# List all 17 tools
GET https://axon-onld.onrender.com/mcp/tools

# Call a free tool
POST https://axon-onld.onrender.com/mcp/call
{ "tool_name": "get_market_overview", "arguments": {} }

# Chat interface
POST https://axon-onld.onrender.com/api/chat
{ "question": "What's the best yield on X Layer?" }

# Agent activity feed
GET https://axon-onld.onrender.com/api/agent/activity

# x402 pricing
GET https://axon-onld.onrender.com/api/x402/pricing

# Real-time WebSocket
WS wss://axon-onld.onrender.com/ws/agent
→ {"tool": "get_market_overview", "args": {}}
← {"type": "result", "data": { "gas_price_gwei": 0.02 ... }}
```

### End-to-End Agent Flow
```
User:  "Analyze this X Layer wallet and tell me what to do"
Agent: POST /api/chat { "question": "Analyze wallet 0x..." }
AXON:  1. Intent detected → analyze_wallet tool
       2. Checks x402 payment (or uses free endpoint)
       3. Fetches portfolio via Onchain OS wallet API (parallel)
       4. Fetches tx history via Onchain OS transaction API (parallel)
       5. Fetches DeFi positions via Onchain OS yield API (parallel)
       6. Computes risk score (0-100) deterministically
       7. Calls Groq LLaMA 3.3 70B for AI narrative + recommendations
       8. Returns structured report with risk level, insights, and actions
Agent: Delivers natural language answer to user
```

### Running Locally
```bash
# Backend
cd backend
cp .env.example .env   # add OKX + Groq API keys
pip install -r requirements.txt
uvicorn src.server:app --reload --port 3000

# Frontend
cd frontend
npm install
echo "VITE_AXON_API_URL=http://localhost:3000" > .env
npm run dev
```

---

## Deployment

| Service | URL |
|---------|-----|
| **Frontend (Live)** | https://axon-six-amber.vercel.app |
| **Backend API (Live)** | https://axon-onld.onrender.com |
| **Swagger API Docs** | https://axon-onld.onrender.com/docs |
| **MCP Tools List** | https://axon-onld.onrender.com/mcp/tools |
| **Chat API** | https://axon-onld.onrender.com/api/chat |
| **Agent Activity** | https://axon-onld.onrender.com/api/agent/activity |
| **x402 Pricing** | https://axon-onld.onrender.com/api/x402/pricing |
| **GitHub** | https://github.com/MUTHUKUMARAN-K-1/axon |

---

## Team

| Name | Role |
|------|------|
| Muthukumaran K | Full-stack development, AI integration, X Layer deployment |

---

## X Layer Ecosystem Positioning

AXON is **infrastructure for the agentic era of X Layer**:

- **Any DeFi protocol** on X Layer becomes AI-accessible — agents can query, analyze, and act on it through AXON's MCP interface
- **OKX Onchain OS** is the data backbone — AXON wraps 6 core Onchain OS modules into agent-callable tools
- **Uniswap V3** analytics bring the leading DEX's liquidity intelligence into every agent workflow
- **MCP standard** means AXON works with Claude, GPT, and any open-source LLM out of the box — zero integration friction
- **x402 payment protocol** enables monetization of AI agent skills natively on X Layer — agents pay agents with OKB
- **Autonomous loop** means AXON doesn't just respond to queries — it proactively monitors X Layer and surfaces opportunities
- **Natural language interface** lowers the barrier to entry — any user can access X Layer intelligence without knowing APIs

As X Layer's ecosystem grows, every new protocol, token, and DeFi primitive becomes queryable through AXON — a permanent intelligence layer for the chain.

---

## Judging Criteria Alignment

| Criterion (25% each) | AXON's Implementation |
|---|---|
| **Onchain OS / Uniswap integration & innovation** | 6 Onchain OS modules + Uniswap V3 subgraph + OKX DEX aggregator. All 17 MCP tools are production-tested live endpoints. Unique: x402 payment gate using OKB on X Layer as the monetization layer. |
| **X Layer ecosystem integration** | 100% focused on X Layer (Chain ID 196). Gas monitoring, block analytics, OKB pricing, pool liquidity, autonomous agent loop, and x402 payments are all X Layer-native. |
| **AI interactive experience** | Natural language "Ask AXON" chat, real-time Agent Terminal (live MCP execution), autonomous activity feed, LLM-generated portfolio insights via Groq LLaMA 3.3 70B. |
| **Product completeness** | 7-page React frontend, FastAPI backend, WebSocket agent terminal, REST + MCP API, Chat API, x402 gate, Swagger docs, deployed to Vercel + Render. Works end-to-end with zero setup. |

### Special Prize Targets

| Prize | Implementation |
|---|---|
| **Best x402 application** | x402 payment gate on premium MCP tools — agents pay OKB on X Layer to access `analyze_wallet`, `compare_wallets`, `find_arbitrage_opportunities` |
| **Best MCP integration** | 17 MCP tools covering all aspects of X Layer: portfolio, market, DEX, swap, AI analysis — plus chat interface for natural language access |
| **Best economy loop** | Autonomous agent monitors yield → surfaces opportunity → user swaps via OKX DEX aggregator → earns yield → pays x402 for more analysis |
| **Best data analyst** | Onchain OS data → deterministic risk scoring + LLM narrative + 7-day Uniswap OHLC + yield APY estimation |

---

## License

MIT — Free to fork, extend, and build on.
