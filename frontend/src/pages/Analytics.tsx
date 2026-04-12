import { useEffect, useState } from 'react'
import { TrendingUp, BarChart3, Search, Loader2, Sparkles, AlertCircle } from 'lucide-react'
import { getYieldOpportunities, getTokenAnalytics } from '../services/api'
import type { TokenAnalyticsResponse, YieldOpportunity } from '../types/api'
import { formatTokenPrice, formatUsd, isEvmAddress } from '../utils/format'
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts'

const RISK_BADGE: Record<string, string> = {
  Low: 'badge-success',
  Medium: 'badge-warning',
  High: 'badge-danger',
}

interface ChartTooltipPayload {
  value?: number
}

interface ChartTooltipProps {
  active?: boolean
  payload?: ChartTooltipPayload[]
  label?: number
}

const CustomTooltip = ({ active, payload, label }: ChartTooltipProps) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'white', border: '1px solid var(--border-default)',
      borderRadius: 10, padding: '10px 14px', fontSize: 12,
      boxShadow: 'var(--shadow-md)',
    }}>
      <p style={{ color: 'var(--text-muted)', marginBottom: 4 }}>
        {label ? new Date(label * 1000).toLocaleDateString('en', { month: 'short', day: 'numeric' }) : '—'}
      </p>
      <p style={{ fontWeight: 600, color: 'var(--axon-primary)' }}>
        ${Number(payload[0]?.value ?? 0).toFixed(6)}
      </p>
    </div>
  )
}

export default function Analytics() {
  const [yields, setYields] = useState<YieldOpportunity[]>([])
  const [tokenAddr, setTokenAddr] = useState('')
  const [tokenData, setTokenData] = useState<TokenAnalyticsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [tokenLoading, setTokenLoading] = useState(false)

  useEffect(() => {
    getYieldOpportunities(2.0).then((d) => {
      setYields(d.opportunities ?? [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const searchToken = async () => {
    if (!isEvmAddress(tokenAddr)) return
    setTokenLoading(true)
    setTokenData(null)
    try {
      const data = await getTokenAnalytics(tokenAddr)
      setTokenData(data)
    } catch (e) {
      console.error(e)
    } finally {
      setTokenLoading(false)
    }
  }

  const priceChange = tokenData?.price_change_7d_pct || 0
  const isPositive = priceChange >= 0
  const chartData = tokenData?.ohlc_7d ? [...tokenData.ohlc_7d].reverse() : []

  return (
    <div style={{ padding: '32px', maxWidth: 1100 }}>
      {/* Header */}
      <div className="animate-fade-up" style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 30, fontWeight: 700, fontFamily: "'Space Grotesk',sans-serif", letterSpacing: '-0.03em' }}>
          Analytics
        </h1>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4 }}>
          Yield opportunities & token analytics on X Layer
        </p>
      </div>

      {/* Token Analytics */}
      <div className="card animate-fade-up" style={{ animationDelay: '60ms', padding: 24, marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'var(--axon-primary-light)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <BarChart3 size={16} color="var(--axon-primary)" />
          </div>
          <span style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>Token Analytics</span>
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Uniswap V3 · X Layer</span>
        </div>

        <div style={{ display: 'flex', gap: 12 }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search
              size={15} color="var(--text-muted)"
              style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }}
            />
            <input
              id="token-analytics-input"
              type="text"
              value={tokenAddr}
              onChange={(e) => setTokenAddr(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && searchToken()}
              placeholder="Enter token contract address on X Layer..."
              className="input-field"
              style={{ paddingLeft: 42 }}
            />
          </div>
          <button
            id="token-analyze-btn"
            onClick={searchToken}
            disabled={tokenLoading}
            className="btn-primary"
            style={{ display: 'flex', alignItems: 'center', gap: 8, whiteSpace: 'nowrap' }}
          >
            {tokenLoading
              ? <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} />
              : <Sparkles size={15} />
            }
            {tokenLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {tokenData?.success && (
          <div className="animate-fade-up" style={{ marginTop: 24 }}>
            {/* Token Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
              {[
                { label: 'Symbol', value: tokenData.symbol, accent: true },
                { label: '7d Change', value: `${priceChange >= 0 ? '+' : ''}${priceChange}%`, positive: isPositive },
                { label: 'Current Price', value: formatTokenPrice(tokenData.price_now_usd) },
                { label: 'TVL', value: formatUsd(tokenData.tvl_usd || 0) },
              ].map(({ label, value, accent, positive }) => (
                <div key={label} style={{
                  background: accent ? 'var(--axon-primary-light)' : 'var(--surface-bg)',
                  border: '1px solid var(--border-default)', borderRadius: 12, padding: '14px 16px',
                }}>
                  <p style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
                    {label}
                  </p>
                  <p style={{
                    fontSize: 16, fontWeight: 700,
                    color: positive === true ? '#10B981' : positive === false ? '#EF4444' : accent ? 'var(--axon-primary)' : 'var(--text-primary)',
                    fontFamily: "'Space Grotesk',sans-serif",
                  }} className="num">
                    {value}
                  </p>
                </div>
              ))}
            </div>

            {/* Area Chart */}
            {chartData.length > 0 && (
              <div>
                <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  7-Day Price History
                </p>
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart data={chartData} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
                    <defs>
                      <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#5B3CF5" stopOpacity={0.15} />
                        <stop offset="100%" stopColor="#5B3CF5" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-default)" vertical={false} />
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
                      axisLine={false} tickLine={false}
                      tickFormatter={(v) => new Date(v * 1000).toLocaleDateString('en', { month: 'short', day: 'numeric' })}
                    />
                    <YAxis tick={{ fontSize: 10, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} width={60} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area
                      type="monotone" dataKey="priceUSD"
                      stroke="#5B3CF5" strokeWidth={2}
                      fill="url(#priceGrad)"
                      dot={false} activeDot={{ r: 4, fill: '#5B3CF5' }}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Yield Table */}
      <div className="card animate-fade-up" style={{ animationDelay: '120ms' }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 12,
          padding: '18px 24px 16px',
          borderBottom: '1px solid var(--border-default)',
        }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: '#D1FAE5',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <TrendingUp size={16} color="#10B981" />
          </div>
          <div>
            <p style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>Yield Opportunities</p>
            <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>Uniswap V3 on X Layer · estimated fee APY</p>
          </div>
          {!loading && yields.length > 0 && (
            <span className="badge badge-success" style={{ marginLeft: 'auto' }}>
              {yields.length} opportunities
            </span>
          )}
        </div>

        {loading ? (
          <div style={{ padding: 32 }}>
            {[0,1,2,3,4].map(i => (
              <div key={i} style={{ display: 'flex', gap: 16, marginBottom: 14 }}>
                <div className="skeleton" style={{ flex: 3, height: 16 }} />
                <div className="skeleton" style={{ flex: 1, height: 16 }} />
                <div className="skeleton" style={{ flex: 1, height: 16 }} />
                <div className="skeleton" style={{ flex: 1, height: 16 }} />
              </div>
            ))}
          </div>
        ) : yields.length === 0 ? (
          <div style={{ padding: '48px 32px', textAlign: 'center' }}>
            <AlertCircle size={28} color="var(--text-muted)" style={{ margin: '0 auto 12px', display: 'block', opacity: 0.5 }} />
            <p style={{ fontSize: 14, color: 'var(--text-muted)' }}>No opportunities above APY threshold</p>
            <p style={{ fontSize: 12, color: 'var(--text-placeholder)', marginTop: 4 }}>
              Uniswap subgraph data may not be available for X Layer yet.
            </p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Pool Pair</th>
                <th style={{ textAlign: 'right' }}>TVL</th>
                <th style={{ textAlign: 'right' }}>Est. APY</th>
                <th style={{ textAlign: 'center' }}>Risk</th>
              </tr>
            </thead>
            <tbody>
              {yields.map((y, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{y.pair}</td>
                  <td style={{ textAlign: 'right' }} className="num">
                    ${y.tvl_usd.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <span style={{
                      fontSize: 13, fontWeight: 700,
                      color: y.estimated_fee_apy_pct > 20 ? '#10B981' : y.estimated_fee_apy_pct > 10 ? '#F59E0B' : 'var(--text-primary)',
                    }} className="num">
                      {y.estimated_fee_apy_pct.toFixed(1)}%
                    </span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <span className={`badge ${RISK_BADGE[y.risk] || 'badge-info'}`}>{y.risk}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
