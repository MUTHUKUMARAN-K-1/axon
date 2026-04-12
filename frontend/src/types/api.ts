export interface Pool {
  pair: string
  tvl_usd: number
  volume_usd: number
  fee_pct: number
  address: string
}

export interface NetworkOverview {
  latest_block?: number
  gas_price_gwei?: number
  gas_utilization_pct?: number
}

export interface MarketOverview {
  success?: boolean
  network?: NetworkOverview
  key_prices?: Record<string, string>
}

export interface PoolsResponse {
  success?: boolean
  pools: Pool[]
}

export interface YieldOpportunity {
  pair: string
  tvl_usd: number
  estimated_fee_apy_pct: number
  protocol: string
  risk: string
  address: string
}

export interface YieldOpportunitiesResponse {
  success?: boolean
  opportunities: YieldOpportunity[]
}

export interface OhlcPoint {
  date: number
  priceUSD: number
}

export interface TokenAnalyticsResponse {
  success?: boolean
  symbol?: string
  price_now_usd?: string
  price_change_7d_pct?: number
  tvl_usd?: number
  ohlc_7d?: OhlcPoint[]
}

export interface AgentEvent {
  id: number
  type: 'alert' | 'info' | 'action' | 'yield' | 'gas' | 'security'
  message: string
  data: Record<string, unknown>
  timestamp: string
}

export interface AgentActivityResponse {
  success: boolean
  chain: string
  activity_count: number
  activities: AgentEvent[]
}

export interface TokenHolder {
  address: string
  pct: number
  is_contract: boolean
}

export interface SecurityScanResponse {
  success: boolean
  token_address: string
  risk_score: number
  risk_label: string
  risk_color: string
  flags: string[]
  flag_count: number
  recommendation: string
  stages: {
    honeypot: { score: number; max: number; flags: string[] }
    holder_concentration: {
      score: number
      max: number
      flags: string[]
      top10_pct: number
      holder_count: number
      top_holders: TokenHolder[]
    }
    liquidity: { score: number; max: number; flags: string[]; tvl_usd: number; volume_7d_usd: number }
    contract: { score: number; max: number; flags: string[]; tx_count: number; verified: boolean; contract_name: string }
    activity: { score: number; max: number; flags: string[]; price_change_7d_pct: number }
  }
  market: { price_usd: string; price_change_24h: string; tvl_usd: number; symbol: string; name: string }
}

export interface SmartMoneySignal {
  pair: string
  address: string
  tvl_usd: number
  volume_usd: number
  velocity_ratio: number
  signal_label: string
  signal_strength: number
  signal_reasons: string[]
  fee_pct: number
}

export interface SmartMoneySignalsResponse {
  success?: boolean
  signals: SmartMoneySignal[]
}
