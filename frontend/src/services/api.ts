/**
 * AXON Frontend API Service
 * Connects to AXON backend MCP server
 */

const BACKEND = import.meta.env.VITE_AXON_API_URL || 'http://localhost:3000'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BACKEND}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`)
  return res.json() as Promise<T>
}

// ── Portfolio ──────────────────────────────────────────────────────────────────
export const getPortfolio = (address: string) =>
  request('/api/portfolio', { method: 'POST', body: JSON.stringify({ address }) })

export const analyzeWallet = (address: string, includeAI = true) =>
  request('/api/analyze', {
    method: 'POST',
    body: JSON.stringify({ address, include_ai_insights: includeAI }),
  })

export const compareWallets = (address_a: string, address_b: string) =>
  request('/api/compare', { method: 'POST', body: JSON.stringify({ address_a, address_b }) })

export const getBalance = (address: string) =>
  request(`/api/balance/${address}`)

export const getTransactions = (address: string, limit = 20) =>
  request(`/api/transactions/${address}?limit=${limit}`)

export const getDefiPositions = (address: string) =>
  request(`/api/defi/${address}`)

// ── Market ─────────────────────────────────────────────────────────────────────
export const getMarketOverview = () => request('/api/market')
export const getGasPrice = () => request('/api/gas')
export const getLatestBlock = () => request('/api/block')
export const getChainInfo = () => request('/api/chain')

export const getTokenPrice = (token_address: string) =>
  request('/api/token/price', { method: 'POST', body: JSON.stringify({ token_address }) })

export const getTokenAnalytics = (token_address: string) =>
  request(`/api/token/${token_address}/analytics`)

// ── Uniswap ────────────────────────────────────────────────────────────────────
export const getTopPools = (limit = 10) =>
  request(`/api/uniswap/pools?limit=${limit}`)

export const getPoolData = (token0: string, token1: string, fee = 3000) =>
  request('/api/uniswap/pool', { method: 'POST', body: JSON.stringify({ token0, token1, fee }) })

export const getYieldOpportunities = (min_apy = 5.0) =>
  request(`/api/uniswap/yield?min_apy=${min_apy}`)

// ── Swap ───────────────────────────────────────────────────────────────────────
export const getSwapQuote = (from_token: string, to_token: string, amount: string, slippage = '0.5') =>
  request('/api/swap/quote', {
    method: 'POST',
    body: JSON.stringify({ from_token, to_token, amount, slippage }),
  })

// ── Intelligence ───────────────────────────────────────────────────────────────
export const scanArbitrage = (token_address: string, amount_usd = 1000) =>
  request('/api/arbitrage', { method: 'POST', body: JSON.stringify({ token_address, amount_usd }) })

// ── MCP ───────────────────────────────────────────────────────────────────────
export const listMcpTools = () => request('/mcp/tools')

export const callMcpTool = (tool_name: string, arguments_: Record<string, unknown>) =>
  request('/mcp/call', { method: 'POST', body: JSON.stringify({ tool_name, arguments: arguments_ }) })

// ── WebSocket Agent Terminal ───────────────────────────────────────────────────
export function createAgentSocket(onMessage: (msg: unknown) => void): WebSocket {
  const wsUrl = BACKEND.replace(/^http/, 'ws') + '/ws/agent'
  const ws = new WebSocket(wsUrl)
  ws.onmessage = (e) => {
    try { onMessage(JSON.parse(e.data)) } catch { onMessage(e.data) }
  }
  return ws
}
