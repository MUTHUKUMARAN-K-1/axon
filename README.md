# AXON — Neural Intelligence Layer for X Layer

> **Give your AI agents onchain senses.**
> AXON is a production-grade MCP skill that connects any AI agent to X Layer's complete onchain reality — portfolio intelligence, real-time security scanning, DeFi analytics, swap routing, yield discovery, smart money signals, natural language querying, and x402 micro-payments through a fully standardized MCP interface.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-axon--six--amber.vercel.app-brightgreen?style=for-the-badge)](https://axon-six-amber.vercel.app)
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger%20UI-blue?style=for-the-badge)](https://axon-onld.onrender.com/docs)
[![X Layer](https://img.shields.io/badge/Chain-X%20Layer%20196-blueviolet?style=for-the-badge)](https://www.okx.com/xlayer)
[![MCP Tools](https://img.shields.io/badge/MCP%20Tools-45%20Live-cyan?style=for-the-badge)](https://axon-onld.onrender.com/mcp/tools)
[![x402](https://img.shields.io/badge/x402-Payment%20Gate-yellow?style=for-the-badge)](https://axon-onld.onrender.com/api/x402/pricing)
[![Plugin Store](https://img.shields.io/badge/Plugin%20Store-PR%20%2393-orange?style=for-the-badge)](https://github.com/okx/plugin-store/pull/93)
[![LLMs.txt](https://img.shields.io/badge/LLMs.txt-AI%20Discoverable-brightgreen?style=for-the-badge)](https://axon-onld.onrender.com/llms.txt)
[![npm](https://img.shields.io/npm/v/@axon-xlayer/start?style=for-the-badge&logo=npm&label=npx%20%40axon-xlayer%2Fstart)](https://www.npmjs.com/package/@axon-xlayer/start)

---

## Judge Quick Reference

| Hackathon Criterion (25% each) | AXON Evidence |
|-------------------------------|---------------|
| **X Layer Integration** | 45 MCP tools hitting X Layer RPC, OKLink, OKX DEX, OKX Onchain OS — all on Chain ID 196. [Mainnet TX](https://www.oklink.com/x-layer/tx/0x14a9bd9d2cbbb80be3373dd8b414104d107466247c48a2bd3c8ceb8eee58360b) |
| **Smart Contracts** | 2 deployed contracts: [AxonVerdictLedger](https://www.oklink.com/xlayer/address/0x0191d5ada56672507fdb283ac59d45bde08a53f8) (public security oracle) + [AxonConfidenceBond](https://www.oklink.com/xlayer/address/0xe164011de202eb0ebf5f01ee5d9851c801a9c675) (skin-in-the-game bonds) |
| **MCP / Plugin Store** | [PR #93 submitted](https://github.com/okx/plugin-store/pull/93) · 45 tools live at `https://axon-onld.onrender.com/mcp/tools` · Full OpenAPI at `/docs` |
| **Innovation / AI** | x402 two-level micro-payments · Autonomous 5-min agent loop · 6-source parallel security scoring · Natural language → MCP tool routing · `/llms.txt` AI discovery · Agent registry + leaderboard · 10 on-chain task challenges |

---

## What is AXON?

AI agents can reason, plan, and execute — but they are **blind to onchain activity** by default. There is no standardized way for an AI agent to ask:

> *"Is this token a honeypot? What's the best yield on X Layer right now? Which wallets are accumulating smart money positions? What's the gas price?"*

**AXON solves this.** Named after the axon — the neural transmitter that carries signals between neurons — AXON is the intelligence transmitter between AI agents and X Layer's onchain reality.

AXON exposes **45 production-ready MCP tools** that any Claude, GPT, or open-source AI agent can call to:

- 🛡️ **Scan any token for scams** — 6-source security analysis with honeypot detection, holder concentration, rug risk scoring, and DexScreener pair data
- 💬 **Ask in plain English** — "Is this token safe?" → AXON routes, scans, and answers with structured risk data
- 📈 **Track smart money signals** — velocity-based accumulation detection across all Uniswap V3 pools
- 🔍 **Analyze wallets with AI** — risk scores, portfolio health, NFT holdings, net worth via Onchain OS
- 🦄 **Query Uniswap V3** — pool TVL, 7-day OHLC, yield APY, fee revenue, protocol stats, swap routing
- 🔎 **OKLink Explorer** — address info, block details, contract verification, pending TXs, rich list, internal traces
- 🌉 **Cross-chain bridge** — quote and route assets across chains via OKX DEX aggregator
- 🤖 **Autonomous agent loop** — monitors X Layer every 5 min for gas, yield, and security signals
- 💰 **x402 micro-payment gate** — premium tools require OKB payment, verified on-chain via OKLink

**Arena:** X Layer Arena + Skills Arena  
**Plugin Store:** [axon-xlayer-intelligence PR #93](https://github.com/okx/plugin-store/pull/93)  
**Mainnet TX:** [`0x14a9bd9d...58360b`](https://www.oklink.com/x-layer/tx/0x14a9bd9d2cbbb80be3373dd8b414104d107466247c48a2bd3c8ceb8eee58360b) — x402 premium tool call on X Layer block #57163818

---

## For AI Agents

AXON is built to be natively discoverable and usable by any AI agent — no API key, no account needed.

### Instant Orientation

```bash
GET https://axon-onld.onrender.com/llms.txt
```

Fetch `/llms.txt` and your agent immediately knows every tool, endpoint, payment flow, and contract address. Works with Claude Code, Codex, LangChain, or any HTTP-capable agent.

### Agent Registry & Leaderboard

```bash
# Register your agent
POST https://axon-onld.onrender.com/api/agents
{ "name": "my-agent", "wallet": "0x..." }

# See rankings by scan count
GET https://axon-onld.onrender.com/api/leaderboard
```

### Task Discovery (10 X Layer Challenges)

```bash
GET https://axon-onld.onrender.com/api/tasks
GET https://axon-onld.onrender.com/api/tasks/axon-001
```

Agents can discover and complete X Layer tasks — check gas, scan tokens for honeypots, read on-chain verdicts, batch security scan, and more. Each task includes a `proof_hint` so agents know exactly what to submit.

---

## CLI — `npx @axon-xlayer/start`

**Published on npm:** [`@axon-xlayer/start`](https://www.npmjs.com/package/@axon-xlayer/start)

The AXON CLI lets any developer or AI agent orient instantly — no API key, no install, zero deps.

```bash
# Orient any AI agent to AXON (full live stats + quick start)
npx @axon-xlayer/start

# Machine-readable JSON context for AI agents
npx @axon-xlayer/start --json > axon-context.json

# Security scan a token
npx @axon-xlayer/start scan 0x1e4a5963abfd975d8c9021ce480b42188849d41d

# Wallet portfolio + balances
npx @axon-xlayer/start wallet 0xDb82c0d91E057E05600C8F8dc836bEb41da6df14

# Live gas price on X Layer
npx @axon-xlayer/start gas

# Browse 10 X Layer agent challenges
npx @axon-xlayer/start tasks

# Agent leaderboard
npx @axon-xlayer/start leaderboard

# Register your agent
npx @axon-xlayer/start register my-agent 0xYourWallet

# API health + latency
npx @axon-xlayer/start health
```

All commands support `--json` for piping into other tools or AI agents.

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
│  │         MCP TOOL REGISTRY  (45 tools)  +  Chat NLP Router     │ │
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

## Onchain Contracts

### AxonVerdictLedger — Public Security Oracle

| Field | Value |
|-------|-------|
| **Contract** | [`0x0191d5ada56672507fdb283ac59d45bde08a53f8`](https://www.oklink.com/xlayer/address/0x0191d5ada56672507fdb283ac59d45bde08a53f8) |
| **Network** | X Layer Mainnet (Chain ID: 196) |
| **Deploy TX** | [`0x560e04f0161fdc70f261ad48bf2b71fe2d537b5eb389b67b9bcf0cfbc03d3f8d`](https://www.oklink.com/xlayer/tx/0x560e04f0161fdc70f261ad48bf2b71fe2d537b5eb389b67b9bcf0cfbc03d3f8d) |
| **Role** | Public on-chain oracle — stores every AXON security scan result permanently |
| **Interface** | `publishVerdict(token, risk, flags, hash)` · `getVerdict(token)` · `totalVerdicts()` |
| **Writes** | Every `scan_token_security()` call publishes a verdict transaction on X Layer |

Any contract or off-chain consumer can call `getVerdict(tokenAddress)` to read AXON's latest security score for any X Layer token — no API key needed, fully permissionless.

```solidity
// Read AXON's verdict for any token — on-chain, permissionless
(uint8 riskScore, uint32 timestamp, uint16 flagCount, bytes32 dataHash)
    = IAxonVerdictLedger(0x0191d5ada56672507fdb283ac59d45bde08a53f8).getVerdict(token);
```

### AxonConfidenceBond — Skin-in-the-Game Security Bonds

| Field | Value |
|-------|-------|
| **Contract** | [`0xe164011de202eb0ebf5f01ee5d9851c801a9c675`](https://www.oklink.com/xlayer/address/0xe164011de202eb0ebf5f01ee5d9851c801a9c675) |
| **Network** | X Layer Mainnet (Chain ID: 196) |
| **Deploy TX** | [`0xc6dbdcbc11ff27fc1db178d07f0c932ccb902b44a5dbfea5b4db0650e0ddb2e2`](https://www.oklink.com/xlayer/tx/0xc6dbdcbc11ff27fc1db178d07f0c932ccb902b44a5dbfea5b4db0650e0ddb2e2) |
| **Role** | AXON locks 0.001 OKB per SAFE verdict — challengers win the bond if verdict flips to HIGH RISK within 7 days |
| **Pre-funded** | 0.05 OKB (50 bonds) at deploy |
| **Auto-lock** | Every `scan_token_security()` call with risk < 20 automatically fires `lockBond()` on-chain (~15s after verdict confirm) |
| **Interface** | `lockBond(token)` · `challenge(token)` · `releaseExpired(token)` · `isChallengeOpen(token)` |

**Full automated flow:**
1. `scan_token_security(token)` → risk score computed
2. `publishVerdict(token, risk, flags, hash)` → written to AxonVerdictLedger (fire-and-forget)
3. If risk < 20 (SAFE): waits ~15s for confirmation → `lockBond(token)` → 0.001 OKB locked in AxonConfidenceBond
4. Anyone can call `challenge(token)` within 7 days if the token turns dangerous — wins the bond

```solidity
// Challenge a SAFE verdict — win the bond if token turns dangerous
AxonConfidenceBond(0xe164011de202eb0ebf5f01ee5d9851c801a9c675).challenge(tokenAddress);
```

### Agentic Wallet — x402 Payment Recipient

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

## MCP Tools — Complete List (45 Tools)

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
| 15 | `search_pools_by_token` | Uniswap | free | Find all Uniswap V3 pools containing a specific token |
| 16 | `get_pool_ohlc` | Uniswap | free | OHLC candlestick data for any pool (configurable days) |
| 17 | `get_pool_fees` | Uniswap | free | Fee revenue and estimated APY for any pool |
| 18 | `get_uniswap_protocol_stats` | Uniswap | free | Protocol-level TVL, volume, fee totals, pool count |
| 19 | `get_swap_quote` | Swap | free | Best route via OKX DEX aggregator |
| 20 | `get_yield_opportunities` | Intelligence | free | Yield farming above configurable APY threshold |
| 21 | `find_arbitrage_opportunities` | Intelligence | 🔒 x402 | Price discrepancy scanner across all routes |
| 22 | `scan_token_security` | Security | free | 6-source risk score: honeypot, tax, holders, liquidity, DexScreener, DefiLlama |
| 23 | `get_smart_money_signals` | Security | free | Velocity-based accumulation signals across all Uniswap V3 pools |
| 24 | `get_wallet_net_worth` | Onchain OS | free | Total portfolio value across all chains |
| 25 | `get_token_detail` | Onchain OS | free | Rich token metadata: holders, FDV, socials, description |
| 26 | `lookup_transaction` | Onchain OS | free | Decode any transaction: status, from/to, value, method |
| 27 | `get_supported_tokens` | Onchain OS | free | All tokens supported by OKX DEX on X Layer |
| 28 | `get_cross_chain_quote` | Onchain OS | free | Cross-chain bridge quote via OKX aggregator |
| 29 | `check_address_security` | Security | free | OKX on-chain address risk: blacklist, phishing, contract risk |
| 30 | `check_url_safety` | Security | free | Phishing/malicious URL detection via OKX |
| 31 | `get_nft_holdings` | Onchain OS | free | NFT portfolio for any wallet on X Layer |
| 32 | `get_yield_products` | Onchain OS | free | Available yield/farming products on X Layer |
| 33 | `get_swap_execution` | Onchain OS | free | Full swap calldata for execution via OKX aggregator |
| 34 | `get_address_info` | OKLink | free | Entity label, balance, tx count, first/last TX time |
| 35 | `get_token_transfers` | OKLink | free | ERC-20 token transfer history for any wallet |
| 36 | `get_block_list` | OKLink | free | Most recent blocks on X Layer |
| 37 | `get_block_detail` | OKLink | free | Full block details: gas, validator, base fee, TX count |
| 38 | `get_pending_transactions` | OKLink | free | Unconfirmed mempool transactions on X Layer |
| 39 | `get_contract_info` | OKLink | free | Contract verification, creator, deploy TX, license |
| 40 | `estimate_gas` | OKLink | free | Gas estimation for any transaction on X Layer |
| 41 | `get_token_transfer_list` | OKLink | free | All recent transfers for a specific token contract |
| 42 | `get_rich_list` | OKLink | free | Top holders (rich list) for OKB or any token |
| 43 | `get_internal_transactions` | OKLink | free | Internal contract calls (traces) for any transaction |
| 44 | `get_onchain_verdict` | Security | free | Read AXON's on-chain verdict for any token from AxonVerdictLedger |
| 45 | `get_total_verdicts` | Security | free | Total number of security verdicts published to the on-chain oracle |

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

### Live Scan Example — USDT on X Layer (`0x1e4a5963abfd975d8c9021ce480b42188849d41d`)

> Verified live output from `GET /api/token/0x1e4a5963abfd975d8c9021ce480b42188849d41d/security`

```json
{
  "success": true,
  "token_address": "0x1e4a5963abfd975d8c9021ce480b42188849d41d",
  "risk_score": 0,
  "risk_label": "SAFE",
  "risk_color": "#10B981",
  "chain": "X Layer",
  "flags": [],
  "flag_count": 0,
  "recommendation": "Core ecosystem token — verified safe",
  "scoring": {
    "method": "weighted_average",
    "weights": { "okx_security": 0.35, "onchain_os": 0.25, "dexscreener": 0.20, "uniswap": 0.10, "oklink": 0.10 },
    "raw_scores": { "okx_security": 0, "onchain_os": 0, "dexscreener": 0, "uniswap": 0, "oklink": 0 }
  }
}
```

### Live Scan Example — Unverified Micro-Cap Token (HIGH RISK)

> Actual output from a real X Layer scan. Token redacted to avoid amplifying scam signal.

```json
{
  "success": true,
  "risk_score": 74,
  "risk_label": "HIGH RISK",
  "risk_color": "#EF4444",
  "chain": "X Layer",
  "flags": [
    "Token is mintable — supply can inflate",
    "Upgradeable proxy — contract logic can change",
    "Token pair < 1 day old — very high rug risk",
    "Very low DEX liquidity: $3,200",
    "Dev still holds 18.4% of supply",
    "Contract source not verified on OKLink",
    "Very few holders: 12"
  ],
  "flag_count": 7,
  "recommendation": "DO NOT TRADE — high probability of scam or honeypot",
  "scoring": {
    "method": "weighted_average",
    "raw_scores": { "okx_security": 70, "onchain_os": 80, "dexscreener": 80, "uniswap": 0, "oklink": 75 },
    "weighted_contributions": {
      "okx_security": 24.5, "onchain_os": 20.0, "dexscreener": 16.0, "uniswap": 0.0, "oklink": 7.5
    }
  }
}
```

**Try it live:** `curl https://axon-onld.onrender.com/api/token/0x1e4a5963abfd975d8c9021ce480b42188849d41d/security`

---

## Onchain OS Integration

### 15 Onchain OS Modules Used

| Module | Endpoint | What AXON Does With It |
|--------|----------|------------------------|
| **Wallet Asset API** | `/api/v5/wallet/asset/all-token-balances-by-address` | Full portfolio with USD values for any wallet |
| **Wallet Net Worth** | `/api/v5/wallet/asset/net-worth` | Total portfolio value across all chains |
| **Token Price API** | `/api/v5/wallet/token/price` | Real-time price, 24h change, market cap |
| **Token Detail** | `/api/v5/wallet/token/token-detail` | Rich token metadata: holders, FDV, socials |
| **Transaction History** | `/api/v5/wallet/post-transaction/transactions-by-address` | Wallet activity for risk assessment |
| **Transaction Decode** | `/api/v5/wallet/post-transaction/transaction-by-hash` | Decode any TX: method, from/to, value, status |
| **DeFi Positions** | `/api/v5/wallet/defi/investment/positions` | Active LP + staking + lending positions |
| **NFT Holdings** | `/api/v5/wallet/asset/nft-list` | NFT portfolio for any wallet on X Layer |
| **Yield Products** | `/api/v5/wallet/defi/yield/product-list` | Available farming and yield opportunities |
| **DEX Aggregator Quote** | `/api/v5/dex/aggregator/quote` | Best swap route across all X Layer DEXes |
| **DEX Swap Execution** | `/api/v5/dex/aggregator/swap` | Full swap calldata for on-chain execution |
| **Cross-Chain Bridge** | `/api/v5/dex/cross-chain/quote` | Bridge quotes across chains |
| **All Tokens** | `/api/v5/dex/aggregator/all-tokens` | All tokens supported by OKX DEX on X Layer |
| **Address Security** | `/api/v5/dex/security/address` | Blacklist check, phishing risk, address type |
| **Token Security** | `/api/v5/dex/security/token` | Honeypot detection, buy/sell tax, proxy/mint flags |
| **URL Safety** | `/api/v5/dex/security/url` | Phishing and malicious URL detection |
| **Chain Metadata** | `/api/v5/wallet/chain/supported-chains` | X Layer network info + metadata |

### Uniswap V3 Integration (8 Features)

| Feature | Data Source | Implementation |
|---------|-------------|----------------|
| **Top pools by TVL** | The Graph subgraph | `pools` query ordered by `totalValueLockedUSD` |
| **Token 7-day OHLC** | Subgraph `tokenDayData` | Open/high/low/close/volume for price trend analysis |
| **Pool pair analytics** | Subgraph `poolDayData` | Fee APY estimation from volume/TVL ratios |
| **Smart money velocity** | Subgraph `pools` | Volume/TVL ratio cross-analysis for accumulation signals |
| **Pool search by token** | Subgraph `pools` | Find all pools containing a specific token address |
| **Pool OHLC candles** | Subgraph `poolDayData` | Candlestick data for any pool over configurable days |
| **Pool fee revenue** | Subgraph `poolDayData` | Fee earnings and estimated APY for any pool |
| **Protocol stats** | Subgraph `factories` | Total protocol TVL, volume, fees, pool count |

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

### Server Liveness & Replay Protection

AXON is deployed on Render free tier with **UptimeRobot** pinging `/health` every **5 minutes** — the server stays continuously warm and the autonomous agent loop never sleeps.

| Protection Layer | Mechanism |
|---|---|
| **Cold-start prevention** | UptimeRobot HTTP monitor → `GET /health` every 5 min |
| **In-memory replay cache** | `_USED_TX_HASHES` dict — 24h TTL per tx hash |
| **Verification cache** | `_PAYMENT_CACHE` — 5 min TTL prevents OKLink re-querying same tx |
| **OKLink primary verify** | Confirms tx `status=success`, `to=AXON_WALLET`, `value≥required_OKB` |
| **RPC fallback** | X Layer `eth_getTransactionReceipt` if OKLink unavailable |

Because UptimeRobot keeps the Render instance continuously alive, the in-memory replay dict persists across all normal operation windows. Tx hashes used for premium calls are invalidated immediately upon first use and cannot be reused within the 24-hour window.

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

AXON runs a persistent background agent every **5 minutes** that:

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

## Frontend — 11 Pages

| Page | Route | What It Does |
|------|-------|-------------|
| **Dashboard** | `/` | Market overview: gas, block, top pools, key prices |
| **Portfolio** | `/portfolio` | Wallet analysis: balances, DeFi positions, risk score |
| **Analytics** | `/analytics` | Token OHLC, Uniswap pool stats |
| **Swap** | `/swap` | DEX swap quotes via OKX aggregator |
| **Agent Terminal** | `/agent` | Live WebSocket MCP tool executor |
| **Ask AXON** | `/ask` | Natural language AI chat interface |
| **Agent Activity** | `/activity` | Live autonomous agent event feed |
| **Token Screener** | `/screener` | 5-tab security scanner: Overview, Security, Holders, Liquidity, Smart Money |
| **Explorer** | `/explorer` 🆕 | 4-tab OKLink explorer: address info, block detail, TX decode, contract verification + recent blocks feed |
| **Security Hub** | `/security` 🆕 | Address blacklist check, URL phishing scanner, full token security scan |
| **DeFi Hub** | `/defi` 🆕 | NFT portfolio, yield products, Uniswap V3 protocol stats (TVL / volume / fees) |

### UI Features

| Feature | Description |
|---------|-------------|
| **Dark / Light theme** | Toggle at any time — dark mode uses `#0a0e14` bg with JetBrains Mono font and green accents; preference persisted to localStorage |
| **Dashboard / Terminal mode** | Header toggle switches between the graphical dashboard and the agent terminal with tool drawer |
| **MCP Tool Drawer** | 43 tools organised by 7 domains (Portfolio, Market, Swap & Bridge, Security, Explorer, Agent, System) — collapsible, click any tool to pre-fill the terminal |
| **Impersonation mode** | Enter any `0x` address from the header popover to inspect its full portfolio, DeFi positions, and risk score without connecting a wallet |
| **MCP status badge** | Live connectivity indicator in header — shows `MCP LIVE` or `MCP OFF` based on `/health` ping |
| **x402 badge** | Always-visible premium gate indicator in header |
| **Wallet connection** | RainbowKit-style connect button in both sidebar and header |
| **Agent Activity feed** | Dark terminal-style live feed with timeline track, collapsible event rows, color-coded risk tags, copy-on-click token addresses, animated live pulse dot, and blinking newest-event glow |

---

## REST API Reference

```bash
# ── Health ────────────────────────────────────────
GET  /health                          → { status: "ok" }

# ── MCP Protocol ─────────────────────────────────
GET  /mcp/tools                       → List all 43 MCP tools
POST /mcp/call                        → Execute any MCP tool

# ── Portfolio ─────────────────────────────────────
POST /api/portfolio                   → Token balances + USD values
POST /api/analyze                     → AI wallet analysis (x402 premium)
POST /api/compare                     → Compare two wallets (x402 premium)
GET  /api/balance/{address}           → Native OKB balance
GET  /api/transactions/{address}      → Transaction history
GET  /api/defi/{address}              → DeFi positions

# ── Security ──────────────────────────────────────
GET  /api/token/{address}/security          → Full 6-source security scan
POST /api/security/batch                    → Batch scan up to 10 tokens
GET  /api/smart-money/signals               → Smart money accumulation signals
GET  /api/address/{address}/security-check → OKX address blacklist / risk check
POST /api/url/safety                        → Phishing URL detection

# ── Explorer (OKLink) ─────────────────────────────
GET  /api/address/{address}/info      → Entity label, balance, tx count
GET  /api/blocks/latest               → Most recent blocks on X Layer
GET  /api/block/{number}              → Full block detail: gas, validator, fees
GET  /api/contract/{address}/info     → Contract verification + creator + deploy TX

# ── DeFi Hub ──────────────────────────────────────
GET  /api/address/{address}/nft       → NFT holdings for any wallet
GET  /api/defi/yield-products         → Yield/farming products on X Layer
GET  /api/uniswap/stats               → Protocol TVL, volume, fees, pool count
GET  /api/uniswap/pool/{addr}/fees    → Pool fee revenue + estimated APY

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
AXON Chat → Groq LLaMA classifies intent: security scan + token address
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
[Background agent — runs every 5 min]
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

The skill exposes all 43 MCP tools with:
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

## Testing

### Test Coverage

| Suite | Tests | What It Covers |
|-------|-------|----------------|
| `TestHealth` | 3 | `/health`, `/mcp/tools`, server connectivity |
| `TestMCPTools` | 4 | MCP tool registry, schema validation, tool count |
| `TestFreeMCPCalls` | 3 | `get_market_overview`, `get_gas_price`, `get_uniswap_top_pools` |
| `TestX402Gate` | 4 | 402 rejection (no header), invalid tx, replay protection, valid OKB payment |
| `TestAgentActivity` | 2 | Activity feed format, signal type coverage |
| `TestChatAPI` | 2 | Intent routing (security, portfolio), response structure |
| `TestSecurityScanner` | 4 | 6-source scan, risk label, scoring weights, USDT safe scan |
| `TestOKLinkExplorer` | 3 | Address info, block detail, contract verification |
| `TestWebSocket` | 2 | WebSocket connect, progress streaming (start → progress → result) |
| **Total** | **27** | All critical paths covered |

### Run Tests

```bash
cd backend

# Full suite against live deployment
pytest tests/ -v

# Against local instance
AXON_TEST_URL=http://localhost:3000 pytest tests/ -v

# x402 gate only
pytest tests/ -v -k "X402"

# Security scanner only
pytest tests/ -v -k "Security"

# Skip LLM calls (fast, no GROQ_API_KEY needed)
pytest tests/ -v -k "not chat"
```

### Live Verification

All free MCP tools are callable without auth:

```bash
# Health
curl https://axon-onld.onrender.com/health

# List all 43 tools
curl https://axon-onld.onrender.com/mcp/tools | python -m json.tool

# Security scan (USDT on X Layer — should return risk_score: 0)
curl https://axon-onld.onrender.com/api/token/0x1e4a5963abfd975d8c9021ce480b42188849d41d/security

# Smart money signals
curl https://axon-onld.onrender.com/api/smart-money/signals

# Agent activity feed
curl https://axon-onld.onrender.com/api/agent/activity

# Natural language chat
curl -X POST https://axon-onld.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the gas price on X Layer?"}'
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
| **Token Security** | https://axon-onld.onrender.com/api/token/{address}/security |
| **Smart Money** | https://axon-onld.onrender.com/api/smart-money/signals |
| **Agent Activity** | https://axon-onld.onrender.com/api/agent/activity |
| **x402 Pricing** | https://axon-onld.onrender.com/api/x402/pricing |
| **Plugin Store** | https://github.com/okx/plugin-store/pull/93 |
| **GitHub** | https://github.com/MUTHUKUMARAN-K-1/axon |

---

## Deployment Address

| Role | Address | Network |
|------|---------|---------|
| **AxonVerdictLedger** (security oracle contract) | [`0x0191d5ada56672507fdb283ac59d45bde08a53f8`](https://www.oklink.com/xlayer/address/0x0191d5ada56672507fdb283ac59d45bde08a53f8) | X Layer Mainnet (Chain ID 196) |
| **AxonConfidenceBond** (skin-in-the-game bonds) | [`0xe164011de202eb0ebf5f01ee5d9851c801a9c675`](https://www.oklink.com/xlayer/address/0xe164011de202eb0ebf5f01ee5d9851c801a9c675) | X Layer Mainnet (Chain ID 196) |
| **Agentic Wallet** (x402 payment recipient / oracle) | [`0xDb82c0d91E057E05600C8F8dc836bEb41da6df14`](https://www.oklink.com/xlayer/address/0xDb82c0d91E057E05600C8F8dc836bEb41da6df14) | X Layer Mainnet (Chain ID 196) |

- VerdictLedger deploy TX: [`0x560e04f0...d3f8d`](https://www.oklink.com/xlayer/tx/0x560e04f0161fdc70f261ad48bf2b71fe2d537b5eb389b67b9bcf0cfbc03d3f8d)
- ConfidenceBond deploy TX: [`0xc6dbdcbc...db2e2`](https://www.oklink.com/xlayer/tx/0xc6dbdcbc11ff27fc1db178d07f0c932ccb902b44a5dbfea5b4db0650e0ddb2e2)
- x402 premium tool proof TX: [`0x14a9bd9d...360b`](https://www.oklink.com/x-layer/tx/0x14a9bd9d2cbbb80be3373dd8b414104d107466247c48a2bd3c8ceb8eee58360b) (block #57163818)

---

## Working Mechanics

### How AXON processes a request end-to-end

```
1. AI agent (Claude / GPT / open-source) calls POST /mcp/call
   with tool_name + arguments

2. MCP Router checks if tool is premium (x402 gate):
   └─ Premium → extract X-PAYMENT tx hash from header
              → query OKLink to confirm tx on X Layer (status, recipient, amount)
              → reject with HTTP 402 if invalid; consume tx if valid
   └─ Free    → skip payment check, proceed immediately

3. Tool dispatcher routes to one of 5 source modules:
   ├─ onchain_os.py   → OKX Onchain OS REST API (15 modules)
   ├─ oklink.py       → OKLink Explorer API (10 functions)
   ├─ uniswap.py      → Uniswap V3 The Graph subgraph (8 queries)
   ├─ xlayer.py       → X Layer RPC direct (gas, blocks, balances)
   └─ security_agent  → 6 parallel sources (honeypot, holders, pairs, yield, TVL)

4. Result returned as structured JSON to the AI agent

5. [Optional] Agent calls POST /api/chat with plain English question
   → Groq LLaMA 3.3 70B classifies intent + extracts args → dispatches tool → formats answer

6. Autonomous background loop (every 5 min):
   → Scans gas, yield opportunities, block health
   → Logs signals to /api/agent/activity feed
   → Frontend /activity page shows live alerts
```

### Natural Language Intent Routing

| User says | AXON calls |
|-----------|-----------|
| "is this token safe / honeypot / rug" | `scan_token_security` |
| "analyze wallet / risk score" | `analyze_wallet` (x402) |
| "gas price / gwei / fee" | `get_gas_price` |
| "yield / APY / farming" | `get_yield_opportunities` |
| "smart money / whale / accumulation" | `get_smart_money_signals` |
| "swap / best route / quote" | `get_swap_quote` |
| "pool / TVL / Uniswap" | `get_uniswap_top_pools` |
| "arbitrage / spread / MEV" | `find_arbitrage_opportunities` (x402) |
| "bridge / cross-chain" | `get_cross_chain_quote` |
| "NFT / holdings" | `get_nft_holdings` |

---

## X Layer Ecosystem Positioning

AXON fills a gap that no other project addresses: **onchain intelligence infrastructure for AI agents on X Layer.**

| Layer | What existed | What AXON adds |
|-------|-------------|----------------|
| **Data** | Raw RPC + OKLink explorer (human UI) | Machine-readable MCP interface for all X Layer data |
| **Security** | No multi-source token scanner on X Layer | 6-source scanner with honeypot, holder, and pair age analysis |
| **AI agents** | No standardized way to query X Layer | 43 MCP tools compatible with Claude, GPT, any open-source agent |
| **Payments** | No agentic payment primitive on X Layer | x402 gate with OKB, verified on-chain, replay-protected |
| **Skills** | No reusable X Layer skill in Plugin Store | First X Layer native skill — installable in one command |

AXON is not a DeFi app that uses AI as a gimmick. It is **the intelligence API layer** that lets any AI agent — today or in the future — participate in the X Layer ecosystem without needing to understand RPC, ABIs, or API authentication. Every DeFi protocol on X Layer becomes AI-accessible through AXON.

---

## Team

| Name | Role |
|------|------|
| Muthukumaran K | Full-stack development, AI integration, security engine, X Layer deployment |

---

## Judging Criteria Alignment

| Criterion (25% each) | AXON's Implementation |
|---|---|
| **Onchain OS / Uniswap integration & innovation** | 15 Onchain OS modules used: wallet assets, net worth, token detail, TX decode, DeFi positions, NFT holdings, yield products, swap execution, cross-chain bridge, address security, URL safety, token security, DEX tokens, price, chain metadata. Uniswap V3 subgraph for 8 features. **43 MCP tools** production-tested. **Published to Plugin Store** ([PR #93](https://github.com/okx/plugin-store/pull/93)). |
| **X Layer ecosystem integration** | 100% focused on X Layer (Chain ID 196). OKLink explorer (address/block/contract/TX), gas monitoring, OKB pricing, Uniswap V3 liquidity, autonomous scanning every 5 min, x402 payments verified on-chain — all X Layer-native. Live mainnet TX proof: block #57163818. |
| **AI interactive experience** | Natural language "Ask AXON" chat routes 8+ intent types. Real-time WebSocket Agent Terminal. Autonomous loop with security/yield/gas alerts. LLM-generated portfolio insights via Groq LLaMA 3.3 70B. 11-page React frontend covering explorer, security, DeFi, and trading. |
| **Product completeness** | 11-page React frontend. FastAPI backend with 50+ REST endpoints. WebSocket agent terminal. 43 MCP tools across 5 source files. 6-source security scanner. OKLink explorer. Security Hub. DeFi Hub. NFT viewer. x402 payment gate. Swagger docs. Deployed live on Vercel + Render. |

### Special Prize Targets

| Prize | Arena | AXON's Case |
|---|---|---|
| **Best x402 application** | X Layer | x402 payment gate with full OKLink on-chain verification + replay protection. Three premium tools: `analyze_wallet`, `compare_wallets`, `find_arbitrage_opportunities`. Every rejection returns structured 402 reason + payment instructions. Mainnet proof: block #57163818. |
| **Most active agent** | X Layer | Autonomous agent loop calls Onchain OS APIs every 5 min (gas, yield, block health). UptimeRobot keeps it alive 24/7. All activity logged to `/api/agent/activity`. |
| **Best MCP integration** | X Layer | 43 MCP tools across portfolio, market, OKLink explorer, swap, bridge, NFT, security, smart money, AI analysis + natural language routing. Plugin Store skill installable in one command. Compatible with Claude, GPT, any open-source agent. |
| **Best economy loop** | X Layer | Agents earn yield intelligence → pay OKB via x402 for premium analysis → use AI insights to optimize positions → repeat. Full earn-pay-earn cycle with on-chain OKB payments and Onchain OS yield data. |
| **Best Uniswap integration** | Skills | 8 Uniswap V3 subgraph features: top pools, token OHLC, pool fees/APY, protocol stats, pool search by token, smart money velocity signals, yield opportunities, arbitrage scanning. |
| **Best data analyst** | Skills | 15 Onchain OS modules → deterministic risk scoring + LLM narrative + 7-day Uniswap OHLC + yield APY + smart money velocity + holder concentration + OKLink block/contract/address data. |
| **Most innovative** | Skills | First X Layer-native AI intelligence layer. 43 MCP tools, 6-source security scanner (only multi-source token scanner on X Layer), one-command install, x402 agentic payment gate — all on a single reusable skill. |

---

## Why AXON Wins

**AXON is not a demo.** It is production infrastructure for the agentic era of X Layer:

1. **43 MCP tools** — the most comprehensive AI agent skill on X Layer, spanning portfolio, security, DeFi, explorer, swap, bridge, and yield
2. **15 Onchain OS modules** — deeper integration than any other hackathon project: NFT, yield products, address security, URL safety, cross-chain bridge, swap execution, TX decode, net worth, and more
3. **6-source security scanner** — multi-source consensus eliminates false negatives. Uses OKX's own security API, DexScreener, DefiLlama, Uniswap V3, OKLink, and Onchain OS simultaneously
4. **Real on-chain x402 verification** — not simulated. OKLink confirms every payment tx before execution. Replay protection prevents abuse. Mainnet proof: block #57163818
5. **Production-grade UI** — dark/light theme toggle, Dashboard + Terminal dual mode, collapsible 43-tool drawer organized by domain, impersonation mode to inspect any X Layer address, live MCP status badge
6. **Natural language routing** — Groq LLaMA 3.3 70B classifies 8+ intent types with keyword fallback — no regex brittle matching
7. **Plugin Store published** — [PR #93](https://github.com/okx/plugin-store/pull/93) — installable by any AI agent in one command
8. **Fully deployed and tested** — 27 automated tests, frontend on Vercel, backend on Render with UptimeRobot keeping it live 24/7, zero setup to evaluate

Every DeFi protocol on X Layer becomes AI-accessible through AXON. Every new token can be security-scanned. Every wallet can be analyzed. Every yield opportunity can be surfaced. That is the permanent intelligence layer X Layer deserves.

---

## License

MIT — Free to fork, extend, and build on.
