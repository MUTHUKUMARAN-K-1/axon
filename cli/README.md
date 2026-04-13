<!-- AXON CLI -->
<div align="center">

```
 █████╗ ██╗  ██╗ ██████╗ ███╗   ██╗
██╔══██╗╚██╗██╔╝██╔═══██╗████╗  ██║
███████║ ╚███╔╝ ██║   ██║██╔██╗ ██║
██╔══██║ ██╔██╗ ██║   ██║██║╚██╗██║
██║  ██║██╔╝ ██╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
```

**Neural Intelligence Layer for X Layer**

[![npm version](https://img.shields.io/npm/v/@axon-xlayer/start?style=for-the-badge&color=7c5cf5&label=npm)](https://www.npmjs.com/package/@axon-xlayer/start)
[![X Layer](https://img.shields.io/badge/X%20Layer-Chain%20196-00d4ff?style=for-the-badge&logo=ethereum)](https://www.xlayer.network)
[![MCP Tools](https://img.shields.io/badge/MCP%20Tools-45%20Live-00ff88?style=for-the-badge)](https://axon-onld.onrender.com/mcp/tools)
[![x402](https://img.shields.io/badge/x402-OKB%20Payments-ff6b35?style=for-the-badge)](https://axon-onld.onrender.com/api/x402/pricing)
[![License](https://img.shields.io/badge/License-MIT-white?style=for-the-badge)](LICENSE)

```bash
npx @axon-xlayer/start
```

</div>

---

## What is AXON?

AXON is a **production MCP server** exposing 45 on-chain intelligence tools for [X Layer](https://www.xlayer.network) — accessible to any AI agent, CLI tool, or script with a single HTTP request. No account. No API key. Just call and get data.

- **45 MCP tools** — gas, blocks, wallets, tokens, DEX, yield, security, explorer
- **x402 micropayments** — premium AI analysis tools gated by OKB on X Layer
- **On-chain security oracle** — AxonVerdictLedger stores verdicts permanently on-chain
- **AI-agent native** — `/llms.txt`, `--json` mode, agent registry, task discovery

---

## Quick Start

```bash
# One-shot orient (no install needed)
npx @axon-xlayer/start

# Machine-readable JSON (for AI agents / scripts)
npx @axon-xlayer/start --json

# See all 45 tools
npx @axon-xlayer/start tools

# Call any tool directly
npx @axon-xlayer/start call get_gas_price
npx @axon-xlayer/start call scan_token_security --args '{"token_address":"0x..."}'
```

---

## Commands

| Command | Description |
|---------|-------------|
| `(none)` | Full orient screen — live stats, quick start, contracts |
| `tools [keyword]` | List all 45 MCP tools, optionally filtered by keyword |
| `call <tool> [--args '{}']` | Call **any** of the 45 tools directly from the CLI |
| `scan <token>` | Token security scan — 6 sources, on-chain verdict |
| `wallet <address>` | Wallet portfolio — tokens, balances, USD values |
| `gas` | Live gas price on X Layer mainnet |
| `tasks [task-id]` | Browse 10 X Layer agent challenges |
| `leaderboard` | Top agents ranked by scans completed |
| `register <name> <wallet>` | Register your AI agent on the leaderboard |
| `health` | API health check with latency |

### Global Flags

| Flag | Description |
|------|-------------|
| `--json` | Machine-readable JSON output for all commands |
| `--args '{}'` | JSON arguments for the `call` command |
| `--version` | Show CLI version |
| `--help` | Show help screen |

---

## All 45 MCP Tools

Access any tool via `npx @axon-xlayer/start call <tool_name>` or directly via `POST /mcp/call`.

### Chain & Gas (Free)

| Tool | Description | Args |
|------|-------------|------|
| `get_gas_price` | Live gas price on X Layer | — |
| `get_block_info` | Latest block number, timestamp, tx count | — |
| `get_block_list` | Recent blocks list | `limit` |
| `get_block_detail` | Block details by number | `block_number` |
| `get_xlayer_stats` | Chain-wide stats (TVL, tx volume) | — |
| `get_pending_transactions` | Mempool pending txs | — |
| `estimate_gas` | Gas estimate for a transaction | `to`, `data`, `value` |

### Wallet & Portfolio (Free)

| Tool | Description | Args |
|------|-------------|------|
| `get_wallet_portfolio` | Token balances + USD values | `address` |
| `get_native_balance` | OKB native balance | `address` |
| `get_wallet_net_worth` | Total net worth in USD | `address` |
| `get_transaction_history` | Recent transactions | `address`, `limit` |
| `get_token_transfers` | ERC-20 transfer history | `address`, `limit` |
| `get_token_transfer_list` | Filtered transfer list | `token_contract`, `limit` |
| `get_internal_transactions` | Internal tx trace | `tx_hash` |
| `get_defi_positions` | DeFi protocol positions | `address` |
| `get_nft_holdings` | NFT collection holdings | `address` |

### Token & Market (Free)

| Tool | Description | Args |
|------|-------------|------|
| `get_token_price` | Token price in USD | `token_address` |
| `get_token_detail` | Token metadata + supply | `token_address` |
| `get_market_overview` | X Layer market overview | — |
| `get_supported_tokens` | All DEX-listed tokens | — |
| `get_rich_list` | Top token holders | `token_address`, `limit` |

### Security & Oracle (Free)

| Tool | Description | Args |
|------|-------------|------|
| `scan_token_security` | 6-source honeypot + rug scan | `token_address` |
| `get_smart_money_signals` | Smart wallet activity signals | — |
| `get_onchain_verdict` | Read verdict from AxonVerdictLedger | `token_address` |
| `get_total_verdicts` | Total verdicts published on-chain | — |
| `check_address_security` | Address risk flags | `address` |
| `check_url_safety` | URL phishing detection | `url` |
| `get_address_info` | Address type + label | `address` |

### DEX & Uniswap (Free)

| Tool | Description | Args |
|------|-------------|------|
| `get_uniswap_top_pools` | Top liquidity pools | `limit` |
| `get_uniswap_pool_data` | Pool reserves + price | `pool_address` |
| `get_uniswap_token_analytics` | Token pool analytics | `token_address` |
| `get_uniswap_protocol_stats` | Protocol TVL + volume | — |
| `search_pools_by_token` | Find pools for a token | `token_address` |
| `get_pool_ohlc` | Pool OHLC candlestick data | `pool_address`, `period` |
| `get_pool_fees` | Pool fee tier info | `pool_address` |
| `get_swap_quote` | Best swap route + price | `token_in`, `token_out`, `amount` |
| `get_swap_execution` | Execute swap tx calldata | `token_in`, `token_out`, `amount`, `wallet` |
| `get_cross_chain_quote` | Bridge quote X Layer ↔ other chains | `from_chain`, `to_chain`, `token`, `amount` |

### Yield & DeFi (Free)

| Tool | Description | Args |
|------|-------------|------|
| `get_yield_opportunities` | APY opportunities on X Layer | `min_apy` |
| `get_yield_products` | Yield product catalog | — |

### Explorer (Free)

| Tool | Description | Args |
|------|-------------|------|
| `lookup_transaction` | Tx details by hash | `tx_hash` |
| `get_contract_info` | Contract ABI + verified status | `address` |

### Premium — x402 OKB Payment Required

| Tool | Price | Description | Args |
|------|-------|-------------|------|
| `analyze_wallet` | 0.001 OKB | AI risk analysis of any wallet | `wallet_address` |
| `compare_wallets` | 0.001 OKB | Side-by-side wallet comparison | `wallet_a`, `wallet_b` |
| `find_arbitrage_opportunities` | 0.002 OKB | Cross-pool price discrepancy scanner | — |

---

## x402 Payment Flow

```bash
# 1. Check premium tool pricing
curl https://axon-onld.onrender.com/api/x402/pricing

# 2. Send OKB on X Layer to AXON wallet
#    Address: 0xDb82c0d91E057E05600C8F8dc836bEb41da6df14
#    Network: X Layer Mainnet (Chain ID 196)

# 3. Call the premium tool with your tx hash
curl -X POST https://axon-onld.onrender.com/mcp/call \
  -H "Content-Type: application/json" \
  -H "X-PAYMENT: 0x<your_tx_hash>" \
  -d '{"tool_name":"analyze_wallet","arguments":{"wallet_address":"0x..."}}'
```

Via CLI (auto-shows payment instructions when 402 returned):
```bash
npx @axon-xlayer/start call analyze_wallet --args '{"wallet_address":"0x..."}'
```

---

## Direct API Access

All tools are also accessible via REST — no CLI needed.

```bash
# List all 45 tools
GET https://axon-onld.onrender.com/mcp/tools

# Call any tool
POST https://axon-onld.onrender.com/mcp/call
Content-Type: application/json

{"tool_name": "get_gas_price", "arguments": {}}
```

### Example: scan a token
```bash
curl -X POST https://axon-onld.onrender.com/mcp/call \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"scan_token_security","arguments":{"token_address":"0x1e4a5963abfd975d8c9021ce480b42188849d41d"}}'
```

### Example: get wallet portfolio
```bash
curl -X POST https://axon-onld.onrender.com/mcp/call \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"get_wallet_portfolio","arguments":{"address":"0xDb82c0d91E057E05600C8F8dc836bEb41da6df14"}}'
```

---

## Agent Registry & Leaderboard

Register your AI agent and compete on the leaderboard:

```bash
# Register
npx @axon-xlayer/start register my-agent 0xYourWallet

# View leaderboard
npx @axon-xlayer/start leaderboard

# Via API
curl -X POST https://axon-onld.onrender.com/api/agents \
  -H "Content-Type: application/json" \
  -d '{"name":"my-agent","wallet":"0x..."}'
```

---

## On-Chain Contracts

| Contract | Address | Purpose |
|----------|---------|---------|
| AxonVerdictLedger | `0x0191d5ada56672507fdb283ac59d45bde08a53f8` | Permanent security verdicts |
| AxonConfidenceBond | `0xe164011de202eb0ebf5f01ee5d9851c801a9c675` | 0.001 OKB bond per SAFE verdict |

Read verdicts permissionlessly:
```solidity
// AxonVerdictLedger
function getVerdict(address token) external view returns (Verdict memory)
function totalVerdicts() external view returns (uint256)
```

---

## AI Agent Integration

AXON is designed for autonomous AI agents. Use `/llms.txt` to orient any LLM:

```bash
# Get structured AI context
curl https://axon-onld.onrender.com/llms.txt

# Full JSON context for agents
npx @axon-xlayer/start --json

# All tasks / challenges
npx @axon-xlayer/start tasks --json
```

---

## Links

| | |
|--|--|
| API | https://axon-onld.onrender.com |
| Docs | https://axon-onld.onrender.com/docs |
| LLMs.txt | https://axon-onld.onrender.com/llms.txt |
| Frontend | https://axon-six-amber.vercel.app |
| GitHub | https://github.com/MUTHUKUMARAN-K-1/axon |
| Plugin Store PR | https://github.com/okx/plugin-store/pull/93 |
| X Layer | https://www.xlayer.network |

---

<div align="center">

Built for **OKX Build-X 2026 Hackathon** · X Layer Arena + Skills Arena

</div>
