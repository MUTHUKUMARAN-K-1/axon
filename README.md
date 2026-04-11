# AXON — Neural Intelligence Layer for X Layer

> **Give your AI agents onchain senses.**
> AXON is a production-grade MCP skill that connects any AI agent to X Layer's complete onchain reality — portfolio intelligence, real-time security scanning, DeFi analytics, swap routing, yield discovery, smart money signals, natural language querying, and x402 micro-payments through a fully standardized MCP interface.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-axon--six--amber.vercel.app-brightgreen?style=for-the-badge)](https://axon-six-amber.vercel.app)
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger%20UI-blue?style=for-the-badge)](https://axon-onld.onrender.com/docs)
[![X Layer](https://img.shields.io/badge/Chain-X%20Layer%20196-blueviolet?style=for-the-badge)](https://www.okx.com/xlayer)
[![MCP Tools](https://img.shields.io/badge/MCP%20Tools-19%20Live-cyan?style=for-the-badge)](https://axon-onld.onrender.com/mcp/tools)
[![x402](https://img.shields.io/badge/x402-Payment%20Gate-yellow?style=for-the-badge)](https://axon-onld.onrender.com/api/x402/pricing)
[![Plugin Store](https://img.shields.io/badge/Plugin%20Store-PR%20%2393-orange?style=for-the-badge)](https://github.com/okx/plugin-store/pull/93)

---

## What is AXON?

AI agents can reason, plan, and execute — but they are **blind to onchain activity** by default. There is no standardized way for an AI agent to ask:

> *"Is this token a honeypot? What's the best yield on X Layer right now? Which wallets are accumulating smart money positions? What's the gas price?"*

**AXON solves this.** Named after the axon — the neural transmitter that carries signals between neurons — AXON is the intelligence transmitter between AI agents and X Layer's onchain reality.

AXON exposes **19 production-ready MCP tools** that any Claude, GPT, or open-source AI agent can call to:

- 🛡️ **Scan any token for scams** — 6-source security analysis with honeypot detection, holder concentration, rug risk scoring, and DexScreener pair data
- 💬 **Ask in plain English** — "Is this token safe?" → AXON routes, scans, and answers with structured risk data
- 📈 **Track smart money signals** — velocity-based accumulation detection across all Uniswap V3 pools
- 🔍 **Analyze wallets with AI** — risk scores, portfolio health, holdings analysis via Onchain OS
- 🦄 **Query Uniswap V3** — pool TVL, 7-day OHLC, yield APY, swap routing
- 🤖 **Autonomous agent loop** — monitors X Layer every 60s for gas, yield, and security signals
- 💰 **x402 micro-payment gate** — premium tools require OKB payment, verified on-chain via OKLink

**Arena:** X Layer Arena + Skills Arena  
**Plugin Store:** [axon-xlayer-intelligence PR #93](https://github.com/okx/plugin-store/pull/93)  
**Mainnet TX:** [`0x14a9bd9d...58360b`](https://www.oklink.com/x-layer/tx/0x14a9bd9d2cbbb80be3373dd8b414104d107466247c48a2bd3c8ceb8eee58360b) — x402 premium tool call on X Layer block #57163818

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      AI AGENT LAYER                                 │
│           Claude / GPT / Any MCP-Compatible Agent                  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │  MCP Protocol (REST + WebSocket)
┌──────────────────────────▼──────────────────────────────────────────┐
│                  AXON MCP SERVER  (FastAPI / Python)                │
│                                                                     │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────────────┐ │
│  │ Portfolio     │  │ Market        │  │ Security Intelligence    │ │
│  │ Agent         │  │ Agent         │  │ Agent                    │ │
│  │ ─ Risk score  │  │ ─ Yield scan  │  │ ─ Honeypot detection     │ │
│  │ ─ AI analysis │  │ ─ Arbitrage   │  │ ─ OKX Security API       │ │
│  │ ─ Compare     │  │ ─ Overview    │  │ ─ DexScreener pairs      │ │
│  └───────┬───────┘  └──────┬────────┘  │ ─ DefiLlama APY          │ │
│          │                 │           │ ─ Smart money signals    │ │
│          │                 │           └──────────────┬───────────┘ │
│          │                 │                          │             │
│  ┌───────▼─────────────────▼──────────────────────────▼──────────┐ │
│  │         MCP TOOL REGISTRY  (19 tools)  +  Chat NLP Router     │ │
│  │              x402 Payment Gate  +  Autonomous Loop            │ │
│  └───┬────────────────────────┬───────────────────────┬──────────┘ │
└──────┼────────────────────────┼───────────────────────┼────────────┘
       │                        │                        │
┌──────▼──────────┐  ┌──────────▼──────────┐  ┌────────▼───────────┐
│ OKX Onchain OS  │  │ X Layer RPC +       │  │ Free Public APIs   │
│ ─ Wallet assets │  │ OKLink Explorer     │  │ ─ DexScreener      │
│ ─ Token prices  │  │ ─ Gas / blocks      │  │ ─ DefiLlama yields │
│ ─ DeFi positions│  │ ─ Contract code     │  │ ─ Uniswap V3 Graph │
│ ─ DEX aggregator│  │ ─ Holder data       │  │                    │
│ ─ Security scan │  │ ─ Tx verification   │  │                    │
└─────────────────┘  └─────────────────────┘  └────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────────────┐
│              AXON Frontend  (React 18 + Vite + TypeScript)          │
│  Dashboard │ Portfolio │ Analytics │ Swap │ Agent Terminal          │
│  Ask AXON (Chat) │ Agent Activity Feed │ Token Screener 🆕          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Agentic Wallet

| Field | Value |
|-------|-------|
| **Address** | `0xDb82c0d91E057E05600C8F8dc836bEb41da6df14` |
| **Network** | X Layer Mainnet (Chain ID: 196) |
| **Role** | AXON's onchain identity — x402 payment recipient for premium tool calls |
| **Explorer** | [View on OKLink](https://www.oklink.com/xlayer/address/0xDb82c0d91E057E05600C8F8dc836bEb41da6df14) |
| **Mainnet TX** | [`0x14a9bd9d2cbbb80be3373dd8b414104d107466247c48a2bd3c8ceb8eee58360b`](https://www.oklink.com/x-layer/tx/0x14a9bd9d2cbbb80be3373dd8b414104d107466247c48a2bd3c8ceb8eee58360b) |
| **Block** | #57163818 — 0.001 OKB payment → `analyze_wallet` premium tool executed |
| **Proof** | Full x402 payment gate verified on X Layer mainnet via OKLink RPC |

---

## MCP Tools — Complete List (19 Tools)

| # | Tool | Category | Premium | Description |
|---|------|----------|---------|-------------|
| 1 | `get_wallet_portfolio` | Portfolio | free | All token balances + USD values on X Layer |
| 2 | `get_transaction_history` | Portfolio | free | Recent wallet transactions with type/value |
| 3 | `get_defi_positions` | Portfolio | free | Active DeFi positions (LP, staking, lending) |
| 4 | `get_native_balance` | Portfolio | free | Native OKB balance for any address |
| 5 | `analyze_wallet` | AI | 🔒 x402 | Full AI-powered wallet analysis: risk score + recommendations |
| 6 | `compare_wallets` | AI | 🔒 x402 | Side-by-side AI comparison of two wallets |
| 7 | `get_token_price` | Market | free | Real-time price, 24h change, market cap, volume |
| 8 | `get_market_overview` | Market | free | Gas + block + top pools + key prices snapshot |
| 9 | `get_gas_price` | Market | free | Current gas price in gwei + priority fee |
| 10 | `get_block_info` | Market | free | Latest block: number, timestamp, gas utilization |
| 11 | `get_xlayer_stats` | Market | free | X Layer chain metadata + ecosystem links |
| 12 | `get_uniswap_pool_data` | Uniswap | free | Pool TVL/volume/fees for any token pair |
| 13 | `get_uniswap_top_pools` | Uniswap | free | Top X Layer pools ranked by TVL |
| 14 | `get_uniswap_token_analytics` | Uniswap | free | 7-day OHLC + liquidity for any token |
| 15 | `get_swap_quote` | Swap | free | Best route via OKX DEX aggregator |
| 16 | `get_yield_opportunities` | Intelligence | free | Yield farming above configurable APY threshold |
| 17 | `find_arbitrage_opportunities` | Intelligence | 🔒 x402 | Price discrepancy scanner across all routes |
| 18 | `scan_token_security` | **Security 🆕** | free | 6-source risk score: honeypot, tax, holders, liquidity, DexScreener, DefiLlama |
| 19 | `get_smart_money_signals` | **Security 🆕** | free | Velocity-based accumulation signals across all Uniswap V3 pools |

> 🔒 x402 = Premium tool requiring OKB micro-payment on X Layer. See `/api/x402/pricing`.

---

## Signature Feature: Token Security Scanner

AXON's security scanner runs **6 independent data sources in parallel** and synthesizes them into a single risk score (0–100). No single-source bias. No false negatives.

### 6-Source Security Architecture

```
Token Address
    │
    ├── A. OKX Token Security API  ──→ isHoneypot, buyTax/sellTax, isMintable, isProxy
    │
    ├── B. Onchain OS Advanced     ──→ riskControlLevel, lpBurnedPct, devHoldPct,
    │                                  sniperHoldPct, bundlerHoldPct, tokenTags
    │
    ├── C. DexScreener API         ──→ pairAge (rug signal), volume24h, liquidity,
    │                                  FDV, price crash detection
    │
    ├── D. DefiLlama Yields        ──→ APY sanity check (>1000% APY = red flag)
    │
    ├── E. Uniswap V3 Subgraph     ──→ TVL depth, 7-day volume, price trend anomalies
    │
    └── F. OKLink Explorer         ──→ top-20 holder concentration, contract verification
                                       transaction history age
```

### Risk Scoring Breakdown

| Stage | Source | Max Points | Key Signals |
|-------|--------|-----------|-------------|
| Honeypot | OKX Security API | 50 pts | `isHoneypot`, extreme sell tax, sell simulation fail |
| Token Flags | OKX Security API | 35 pts | `isMintable`, `isProxy`, `isRiskToken` |
| Holder Danger | Onchain OS + OKLink | 40 pts | Dev hold %, sniper %, bundler %, top-10 concentration |
| Pair Safety | DexScreener | 40 pts | Pair age < 1 day, dust liquidity, dead volume, micro-FDV |
| Liquidity | Uniswap V3 | 20 pts | TVL < $5k, zero on-chain pools |
| Activity | OKLink + price | 15 pts | Zero tx history, extreme price pumps, unverified contract |

**Risk Labels:**

| Score | Label | Recommendation |
|-------|-------|---------------|
| 0–19 | ✅ SAFE | Standard due diligence |
| 20–44 | ⚠️ LOW RISK | Verify flags before investing |
| 45–64 | 🟠 MEDIUM RISK | Proceed with caution |
| 65–79 | 🔴 HIGH RISK | Avoid — multiple danger signals |
| 80–100 | ☠️ CRITICAL | DO NOT TRADE — likely scam or honeypot |

### Security API Endpoints

```bash
# Full security scan — 6 sources in parallel
GET /api/token/0xYourToken/security

# Batch scan up to 10 tokens
POST /api/security/batch
{ "token_addresses": ["0x...", "0x...", "0x..."] }

# Smart money accumulation signals
GET /api/smart-money/signals?limit=10

# Via MCP tool (AI agent callable)
POST /mcp/call
{ "tool_name": "scan_token_security", "arguments": { "token_address": "0x..." } }
```

---

## Onchain OS Integration

### 7 Onchain OS Modules Used

| Module | Endpoint | What AXON Does With It |
|--------|----------|------------------------|
| **Wallet Asset API** | `GET /api/v5/wallet/asset/all-token-balances-by-address` | Full portfolio with USD values for any wallet |
| **Token Price API** | `GET /api/v5/wallet/token/price` | Real-time price, 24h change, market cap |
| **Transaction History** | `GET /api/v5/wallet/post-transaction/transactions-by-address` | Wallet activity for risk assessment |
| **DeFi Positions** | `GET /api/v5/wallet/defi/investment/positions` | Active LP + staking + lending positions |
| **DEX Aggregator** | `GET /api/v5/dex/aggregator/quote` | Best swap route across all X Layer DEXes |
| **Chain Metadata** | `GET /api/v5/wallet/chain/supported-chains` | X Layer network info + metadata |
| **Token Security** | `GET /api/v5/dex/security/token` | Honeypot detection, buy/sell tax, proxy/mint flags |

### Uniswap V3 Integration (5 Features)

| Feature | Data Source | Implementation |
|---------|-------------|----------------|
| **Top pools by TVL** | The Graph subgraph | `pools` query ordered by `totalValueLockedUSD` |
| **Token 7-day OHLC** | Subgraph `tokenDayData` | Open/high/low/close/volume for price trend analysis |
| **Pool pair analytics** | Subgraph `poolDayData` | Fee APY estimation from volume/TVL ratios |
| **Smart money velocity** | Subgraph `pools` | Volume/TVL ratio cross-analysis for accumulation signals |
| **Swap routing** | OKX DEX aggregator | Routes through Uniswap V3 on X Layer |

---

## x402 Micro-Payment Gate

Premium MCP tools require OKB payment on X Layer, verified on-chain via **OKLink** before execution.

### How It Works

```
User/Agent sends X-PAYMENT: 0xTxHash
           │
           ▼
  1. Extract tx hash (raw / base64 / JSON-base64 all accepted)
           │
           ▼
  2. Replay protection — each tx can only be used ONCE (24h window)
           │
           ▼
  3. Query OKLink transaction-fills API
     → confirm: status=success, to=AXON_WALLET, value≥required_OKB
           │
           ▼
  4. Fallback to X Layer RPC (eth_getTransactionReceipt) if OKLink unavailable
           │
           ▼
  5. Mark tx as consumed → execute premium tool → return result
```

### Example Flow

```http
# Pre-verify your payment (recommended)
POST https://axon-onld.onrender.com/api/x402/verify
{ "tx_hash": "0xYourTxHash", "tool_name": "analyze_wallet" }
→ { "valid": true, "source": "oklink", "value_okb": 0.001 }

# Call premium tool with X-PAYMENT header
POST https://axon-onld.onrender.com/mcp/call
X-PAYMENT: 0xYourTxHash
{ "tool_name": "analyze_wallet", "arguments": { "address": "0x..." } }

# Without valid payment → 402
→ HTTP 402 Payment Required
  X-Payment-Address: 0xDb82c0d91E057E05600C8F8dc836bEb41da6df14
  X-Payment-Asset: OKB
  X-Payment-Amount: 0.001
  X-Payment-Network: xlayer-mainnet
  X-Payment-Rejection: "Transaction not found on X Layer"
```

### Premium Tool Pricing

| Tool | Price | Value |
|------|-------|-------|
| `analyze_wallet` | 0.001 OKB | Full AI portfolio analysis + risk score |
| `compare_wallets` | 0.002 OKB | Side-by-side AI wallet comparison |
| `find_arbitrage_opportunities` | 0.001 OKB | Live arbitrage scan across all routes |

---

## Natural Language Interface

```
POST /api/chat
{ "question": "Is 0xTokenAddress safe to trade?" }

→ AXON detects security intent → calls scan_token_security
→ Returns: "Risk score: 72/100 — HIGH RISK. 3 critical flags:
   1. Token is mintable — supply can inflate at any time
   2. Top-10 holders own 84% of supply
   3. Pair created 6 hours ago — very new token
   Recommendation: Do not trade until liquidity and distribution mature."
```

**Intent routing covers:**
- `"scan/safe/honeypot/rug" + 0x...` → `scan_token_security`  
- `"smart money/whale/signals"` → `get_smart_money_signals`
- `"analyze/portfolio/risk" + 0x...` → `analyze_wallet`
- `"gas/gwei/fee"` → `get_gas_price`
- `"yield/apy/farm"` → `get_yield_opportunities`
- `"pool/tvl/uniswap"` → `get_uniswap_top_pools`
- `"arbitrage/spread"` → `find_arbitrage_opportunities`
- `"market/overview"` → `get_market_overview`

---

## Autonomous Agent Loop

AXON runs a persistent background agent every **60 seconds** that:

1. Monitors X Layer gas prices → alerts when < 0.05 gwei (ideal execution window)
2. Scans Uniswap V3 yield opportunities → flags pools above 8% APY
3. Detects smart money signals → logs velocity spikes in top pools
4. Tracks block health and gas utilization percentages
5. Logs all decisions to a live, real-time activity feed

```bash
GET /api/agent/activity
→ {
    "activities": [
      { "type": "security", "message": "Smart money signal: WOKB/USDT — STRONG velocity 8.4x" },
      { "type": "yield",    "message": "Yield: ETH/USDT @ 14.2% APY (TVL $2,847,000)" },
      { "type": "gas",      "message": "Gas price: 0.02 gwei" },
      { "type": "info",     "message": "Block #12,847,291 — 43% gas utilization" }
    ]
  }
```

---

## Frontend — 8 Pages

| Page | Route | What It Does |
|------|-------|-------------|
| **Dashboard** | `/` | Market overview: gas, block, top pools, key prices |
| **Portfolio** | `/portfolio` | Wallet analysis: balances, DeFi positions, risk score |
| **Analytics** | `/analytics` | Token OHLC, Uniswap pool stats |
| **Swap** | `/swap` | DEX swap quotes via OKX aggregator |
| **Agent Terminal** | `/agent` | Live WebSocket MCP tool executor |
| **Ask AXON** | `/ask` | Natural language AI chat interface |
| **Agent Activity** | `/activity` | Live autonomous agent event feed |
| **Token Screener** | `/screener` 🆕 | 5-tab security scanner: Overview, Security, Holders, Liquidity, Smart Money |

---

## REST API Reference

```bash
# ── Health ────────────────────────────────────────
GET  /health                          → { status: "ok" }

# ── MCP Protocol ─────────────────────────────────
GET  /mcp/tools                       → List all 19 MCP tools
POST /mcp/call                        → Execute any MCP tool

# ── Portfolio ─────────────────────────────────────
POST /api/portfolio                   → Token balances + USD values
POST /api/analyze                     → AI wallet analysis (x402 premium)
POST /api/compare                     → Compare two wallets (x402 premium)
GET  /api/balance/{address}           → Native OKB balance
GET  /api/transactions/{address}      → Transaction history
GET  /api/defi/{address}              → DeFi positions

# ── Security (NEW) ────────────────────────────────
GET  /api/token/{address}/security    → Full 6-source security scan
POST /api/security/batch              → Batch scan up to 10 tokens
GET  /api/smart-money/signals         → Smart money accumulation signals

# ── Market ────────────────────────────────────────
GET  /api/market                      → Full market snapshot
POST /api/token/price                 → Real-time token price
GET  /api/token/{address}/analytics   → 7-day OHLC via Uniswap
GET  /api/gas                         → Gas price in gwei
GET  /api/block                       → Latest block info

# ── Uniswap ───────────────────────────────────────
GET  /api/uniswap/pools               → Top pools by TVL
POST /api/uniswap/pool                → Pool data for token pair
GET  /api/uniswap/yield               → Yield opportunities by APY

# ── Swap ──────────────────────────────────────────
POST /api/swap/quote                  → Best swap route (OKX aggregator)

# ── Intelligence ──────────────────────────────────
POST /api/arbitrage                   → Arbitrage opportunity scan
GET  /api/chain                       → X Layer chain info

# ── AI Chat ───────────────────────────────────────
POST /api/chat                        → Natural language → MCP tool routing

# ── Agent ─────────────────────────────────────────
GET  /api/agent/activity              → Autonomous agent activity feed

# ── x402 Payment ──────────────────────────────────
GET  /api/x402/pricing                → Premium tool pricing + payment info
POST /api/x402/verify                 → Pre-verify OKB payment tx

# ── WebSocket ─────────────────────────────────────
WS   /ws/agent                        → Real-time MCP tool executor
```

---

## Complete End-to-End Flows

### Flow 1: Security-First Token Research

```
User: "Is 0xSomeToken safe to buy?"
  │
  ▼
AXON Chat → detects 0x address + "safe" keyword
  │
  ▼
scan_token_security(token_address) — 6 parallel calls:
  ├── OKX Security API   → isHoneypot=false, sellTax=0%
  ├── Onchain OS Adv.    → devHold=2.1%, riskLevel=1 (medium)
  ├── DexScreener        → pair age 14 days, liquidity $127k
  ├── DefiLlama          → APY 8.2% (reasonable)
  ├── Uniswap V3         → TVL $89k, 7d volume $340k
  └── OKLink             → 847 holders, contract verified
  │
  ▼
Risk Score: 18/100 — SAFE ✅
  │
  ▼
LLM formats natural language response:
"Token looks safe. Risk score 18/100. Solid liquidity ($127k), 
 verified contract, 847 holders. Dev holds only 2.1% — healthy 
 distribution. OKX rates it medium risk due to age. Recommended 
 entry point if you believe in the project fundamentals."
```

### Flow 2: Premium Wallet Analysis with x402

```
Agent: POST /mcp/call
       X-PAYMENT: 0xOkbPaymentTxHash
       { "tool_name": "analyze_wallet", "arguments": { "address": "0xWallet" } }
  │
  ▼
x402 Gate:
  1. Extract tx hash from header
  2. Replay check → not used before ✅
  3. OKLink verify → status=success, to=AXON_WALLET, value=0.001 OKB ✅
  4. Mark tx as consumed
  │
  ▼
analyze_wallet(address) runs in parallel:
  ├── Onchain OS wallet assets → token balances + USD values
  ├── Transaction history      → activity patterns
  └── DeFi positions           → LP + staking exposure
  │
  ▼
Risk score computed deterministically (0-100)
LLaMA 3.3 70B generates portfolio narrative + 3 actionable recommendations
  │
  ▼
Returns: { risk_score: 34, risk_level: "LOW RISK", insights: "...", recommendations: [...] }
```

### Flow 3: Autonomous Smart Money Alert

```
[Background agent — runs every 60s]
  │
  ▼
get_smart_money_signals() → scans top 50 Uniswap V3 pools
  │
  Finds: WOKB/USDT pool — velocity ratio 11.2x (volume >> TVL)
          1,847 transactions in 24h — unusually high activity
  │
  ▼
Logs to activity feed:
{ type: "security", message: "Smart money signal: WOKB/USDT — STRONG velocity 11.2x",
  signal_label: "STRONG", velocity_ratio: 11.2, tvl_usd: 284700 }
  │
  ▼
Frontend /activity page shows live alert
User can click → runs full security scan → safe score 12/100
User can swap → POST /api/swap/quote → executes via OKX aggregator
```

---

## Onchain OS Plugin Store Skill

AXON is published as a reusable **Onchain OS skill** installable by any AI agent:

```bash
npx skills add okx/plugin-store --skill axon-xlayer-intelligence
```

The skill exposes all 19 MCP tools with:
- Full `curl` examples for every endpoint
- x402 payment flow documentation
- Security scanner usage guide
- Natural language chat integration

**Plugin Store PR:** https://github.com/okx/plugin-store/pull/93

---

## Local Setup

```bash
# Backend
cd backend
cp .env.example .env
# Fill in: OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE, OKX_PASSPHRASE,
#          OKLINK_API_KEY, GROQ_API_KEY, AXON_AGENT_WALLET
pip install -r requirements.txt
uvicorn src.server:app --reload --port 3000

# Frontend
cd frontend
npm install
echo "VITE_API_URL=http://localhost:3000" > .env
npm run dev
# Open http://localhost:5173
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OKX_API_KEY` | Yes | OKX Onchain OS + DEX APIs |
| `OKX_SECRET_KEY` | Yes | OKX HMAC signing key |
| `OKX_PASSPHRASE` | Yes | OKX account passphrase |
| `OKLINK_API_KEY` | Yes | OKLink explorer API (tx verification + holder data) |
| `GROQ_API_KEY` | Yes | LLaMA 3.3 70B for AI narratives |
| `AXON_AGENT_WALLET` | Yes | Wallet address to receive x402 OKB payments |
| `XLAYER_RPC_URL` | No | X Layer RPC (default: `https://rpc.xlayer.tech`) |

---

## Running Tests

```bash
cd backend

# Full test suite against live deployment
pytest tests/ -v

# Against local instance
AXON_TEST_URL=http://localhost:3000 pytest tests/ -v

# x402 payment tests only
pytest tests/ -v -k "X402"

# Skip LLM calls (fast)
pytest tests/ -v -k "not chat"
```

**Test suite:** `TestHealth` (3) · `TestMCPTools` (4) · `TestFreeMCPCalls` (3) · `TestX402` (4) · `TestAgentActivity` (2) · `TestChatAPI` (2) = **18 tests**

---

## Deployment

| Service | URL |
|---------|-----|
| **Frontend (Live)** | https://axon-six-amber.vercel.app |
| **Backend API (Live)** | https://axon-onld.onrender.com |
| **Swagger API Docs** | https://axon-onld.onrender.com/docs |
| **MCP Tools List** | https://axon-onld.onrender.com/mcp/tools |
| **Chat API** | https://axon-onld.onrender.com/api/chat |
| **Token Security** | https://axon-onld.onrender.com/api/token/{address}/security |
| **Smart Money** | https://axon-onld.onrender.com/api/smart-money/signals |
| **Agent Activity** | https://axon-onld.onrender.com/api/agent/activity |
| **x402 Pricing** | https://axon-onld.onrender.com/api/x402/pricing |
| **Plugin Store** | https://github.com/okx/plugin-store/pull/93 |
| **GitHub** | https://github.com/MUTHUKUMARAN-K-1/axon |

---

## Team

| Name | Role |
|------|------|
| Muthukumaran K | Full-stack development, AI integration, security engine, X Layer deployment |

---

## Judging Criteria Alignment

| Criterion (25% each) | AXON's Implementation |
|---|---|
| **Onchain OS / Uniswap integration & innovation** | 7 Onchain OS modules (incl. Token Security API) + Uniswap V3 subgraph + OKX DEX aggregator. 19 MCP tools production-tested on live endpoints. **Published to Onchain OS Plugin Store** ([PR #93](https://github.com/okx/plugin-store/pull/93)). Security scanner uses OKX's own `isHoneypot` and tax APIs directly. |
| **X Layer ecosystem integration** | 100% focused on X Layer (Chain ID 196). Gas monitoring, block analytics, OKB pricing, Uniswap V3 liquidity, autonomous scanning, x402 payments with OKLink verification — all X Layer-native. |
| **AI interactive experience** | Natural language "Ask AXON" chat routes 8+ intent types. Real-time WebSocket Agent Terminal. Autonomous 60s loop with security alerts. LLM-generated portfolio insights and security explanations via Groq LLaMA 3.3 70B. |
| **Product completeness** | 8-page React frontend. FastAPI backend with 35+ REST endpoints. WebSocket agent terminal. 19 MCP tools. 6-source security scanner. Smart money signal feed. x402 payment gate with OKLink verification. Swagger docs. Deployed live on Vercel + Render. |

### Special Prize Targets

| Prize | AXON's Case |
|---|---|
| **Best x402 application** | x402 payment gate with full OKLink on-chain verification + replay protection. Premium tools: `analyze_wallet`, `compare_wallets`, `find_arbitrage_opportunities`. Every rejection returns structured reason + payment instructions. |
| **Best MCP integration** | 19 MCP tools covering portfolio, market, DEX, swap, security, smart money, AI analysis + natural language chat routing. Plugin Store skill installable in one command. Compatible with Claude, GPT, any open-source agent. |
| **Best security application** | 6-source token security scanner: OKX honeypot API + Onchain OS risk control + DexScreener pair age + DefiLlama APY sanity + Uniswap V3 TVL + OKLink holder concentration. Autonomous agent monitors X Layer for threats. |
| **Best data analyst** | Onchain OS data → deterministic risk scoring + LLM narrative + 7-day Uniswap OHLC + yield APY estimation + smart money velocity signals + holder concentration analysis. |
| **Most innovative (Skills Arena)** | First X Layer-native security intelligence skill for AI agents. Wraps 19 live MCP tools including the only multi-source token security scanner on X Layer. One-command install via Plugin Store. |

---

## Why AXON Wins

**AXON is not a demo.** It is production infrastructure for the agentic era of X Layer:

1. **19 MCP tools** — the most comprehensive AI agent skill on X Layer
2. **6-source security scanner** — multi-source consensus eliminates false negatives. Uses OKX's own security API, DexScreener, DefiLlama, Uniswap V3, OKLink, and Onchain OS simultaneously
3. **Real on-chain x402 verification** — not simulated. OKLink confirms every payment tx before execution. Replay protection prevents abuse
4. **Natural language routing** — 8 intent patterns covering every major X Layer use case
5. **Autonomous intelligence** — AXON monitors X Layer 24/7, surfaces signals proactively
6. **Plugin Store published** — [PR #93](https://github.com/okx/plugin-store/pull/93) — installable by any AI agent on the planet in one command
7. **Fully deployed** — frontend on Vercel, backend on Render, live right now — zero setup to evaluate

Every DeFi protocol on X Layer becomes AI-accessible through AXON. Every new token can be security-scanned. Every wallet can be analyzed. Every yield opportunity can be surfaced. That is the permanent intelligence layer X Layer deserves.

---

## License

MIT — Free to fork, extend, and build on.
