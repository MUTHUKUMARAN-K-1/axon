import { useState } from 'react'
import {
  Search, Wallet, Brain,
  AlertCircle, ChevronRight, Sparkles, Loader2
} from 'lucide-react'
import { analyzeWallet } from '../services/api'
import toast from 'react-hot-toast'

interface Token {
  symbol: string
  name: string
  balance: string
  value_usd: number
  price_usd: string
  logo?: string
}

interface RiskAssessment {
  score: number
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH'
  color: string
  flags: string[]
}

interface WalletAnalysis {
  address: string
  snapshot: {
    native_balance_okb: number
    total_portfolio_usd: number
    token_count: number
    tokens: Token[]
    recent_transactions: unknown[]
    defi_positions: unknown[]
  }
  risk_assessment: RiskAssessment
  ai_insights: string
  recommendations: string[]
}

const RISK_META = {
  LOW:    { badge: 'badge-success', bar: '#10B981', bg: 'linear-gradient(135deg, rgba(16,185,129,0.08), rgba(16,185,129,0.04))', border: 'rgba(16,185,129,0.25)' },
  MEDIUM: { badge: 'badge-warning', bar: '#F59E0B', bg: 'linear-gradient(135deg, rgba(245,158,11,0.08), rgba(245,158,11,0.04))', border: 'rgba(245,158,11,0.25)' },
  HIGH:   { badge: 'badge-danger',  bar: '#EF4444', bg: 'linear-gradient(135deg, rgba(239,68,68,0.08), rgba(239,68,68,0.04))', border: 'rgba(239,68,68,0.25)' },
}

const EXAMPLE_ADDRESSES = [
  '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
  '0x8Ba1f109551bD432803012645Ac136ddd64DBA72',
]

export default function Portfolio() {
  const [address, setAddress] = useState('')
  const [analysis, setAnalysis] = useState<WalletAnalysis | null>(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    if (!address.match(/^0x[a-fA-F0-9]{40}$/)) {
      toast.error('Enter a valid EVM address (0x...)')
      return
    }
    setLoading(true)
    setAnalysis(null)
    try {
      const result = await analyzeWallet(address, true) as WalletAnalysis
      setAnalysis(result)
    } catch {
      toast.error('Analysis failed — check backend connection')
    } finally {
      setLoading(false)
    }
  }

  const riskLevel = (analysis?.risk_assessment?.risk_level || 'MEDIUM') as 'LOW' | 'MEDIUM' | 'HIGH'
  const riskScore = analysis?.risk_assessment?.score || 0
  const riskMeta = RISK_META[riskLevel]

  return (
    <div style={{ padding: '32px', maxWidth: 1100 }}>
      {/* Header */}
      <div className="animate-fade-up" style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 30, fontWeight: 700, fontFamily: "'Space Grotesk',sans-serif", letterSpacing: '-0.03em' }}>
          Portfolio Intelligence
        </h1>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4 }}>
          AI-powered X Layer wallet analysis with risk scoring
        </p>
      </div>

      {/* Search Box */}
      <div className="card animate-fade-up" style={{ animationDelay: '60ms', padding: 24, marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'var(--axon-primary-light)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Brain size={16} color="var(--axon-primary)" />
          </div>
          <span style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>Analyze Wallet</span>
        </div>

        <div style={{ display: 'flex', gap: 12 }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search
              size={15}
              color="var(--text-muted)"
              style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }}
            />
            <input
              id="wallet-address-input"
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
              placeholder="Enter X Layer wallet address (0x...)"
              className="input-field"
              style={{ paddingLeft: 42 }}
            />
          </div>
          <button
            id="analyze-wallet-btn"
            onClick={handleAnalyze}
            disabled={loading}
            className="btn-primary"
            style={{ display: 'flex', alignItems: 'center', gap: 8, whiteSpace: 'nowrap' }}
          >
            {loading ? <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} /> : <Sparkles size={15} />}
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {/* Quick fill examples */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 12 }}>
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Try:</span>
          {EXAMPLE_ADDRESSES.map((addr) => (
            <button
              key={addr}
              onClick={() => setAddress(addr)}
              className="chip"
              style={{ fontSize: 10 }}
            >
              {addr.slice(0, 10)}…{addr.slice(-4)}
            </button>
          ))}
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="card animate-fade-in" style={{ padding: '48px 32px', textAlign: 'center' }}>
          <div style={{
            width: 52, height: 52, borderRadius: '50%',
            background: 'var(--axon-primary-light)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 16px',
            animation: 'float 2s ease-in-out infinite',
          }}>
            <Brain size={24} color="var(--axon-primary)" />
          </div>
          <p style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>
            AXON is analyzing this wallet
          </p>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Fetching on-chain data, running AI risk scoring...
          </p>
        </div>
      )}

      {/* Results */}
      {analysis && !loading && (
        <div className="animate-fade-up" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Summary Row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
            {/* Total Value */}
            <div className="stat-card" style={{ background: 'linear-gradient(135deg, rgba(91,60,245,0.06), rgba(91,60,245,0.02))' }}>
              <p style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 8 }}>
                Total Portfolio Value
              </p>
              <p style={{ fontSize: 28, fontWeight: 700, fontFamily: "'Space Grotesk',sans-serif", letterSpacing: '-0.03em', color: 'var(--text-primary)', lineHeight: 1 }} className="num">
                ${analysis.snapshot.total_portfolio_usd.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </p>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6 }}>
                {analysis.snapshot.native_balance_okb.toFixed(4)} OKB native
              </p>
            </div>

            {/* Tokens */}
            <div className="stat-card" style={{ background: 'linear-gradient(135deg, rgba(6,196,208,0.06), rgba(6,196,208,0.02))' }}>
              <p style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 8 }}>
                Assets Held
              </p>
              <p style={{ fontSize: 28, fontWeight: 700, fontFamily: "'Space Grotesk',sans-serif", letterSpacing: '-0.03em', color: 'var(--text-primary)', lineHeight: 1 }}>
                {analysis.snapshot.token_count}
              </p>
              <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6 }}>
                {analysis.snapshot.defi_positions.length} DeFi positions
              </p>
            </div>

            {/* Risk */}
            <div
              className="stat-card"
              style={{ background: riskMeta.bg, border: `1px solid ${riskMeta.border}` }}
            >
              <p style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 8 }}>
                Risk Score
              </p>
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, marginBottom: 8 }}>
                <p style={{ fontSize: 28, fontWeight: 700, fontFamily: "'Space Grotesk',sans-serif", letterSpacing: '-0.03em', color: 'var(--text-primary)', lineHeight: 1 }} className="num">
                  {riskScore}
                </p>
                <span style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 2 }}>/100</span>
                <span className={`badge ${riskMeta.badge}`} style={{ marginBottom: 2 }}>{riskLevel} RISK</span>
              </div>
              <div style={{ height: 6, borderRadius: 99, background: 'rgba(0,0,0,0.08)' }}>
                <div style={{
                  height: '100%', borderRadius: 99,
                  background: riskMeta.bar,
                  width: `${riskScore}%`,
                  transition: 'width 0.8s ease',
                }} />
              </div>
            </div>
          </div>

          {/* AI Insights */}
          {analysis.ai_insights && (
            <div style={{
              padding: '20px 24px',
              background: 'linear-gradient(135deg, var(--axon-primary-light), rgba(237,233,254,0.5))',
              border: '1px solid rgba(91,60,245,0.2)',
              borderRadius: 16,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <div style={{
                  width: 32, height: 32, borderRadius: 8,
                  background: 'var(--axon-primary)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <Brain size={16} color="white" />
                </div>
                <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--axon-primary)', fontFamily: "'Space Grotesk',sans-serif" }}>
                  AXON AI Analysis
                </span>
                <span className="badge badge-primary" style={{ marginLeft: 'auto' }}>AI-Powered</span>
              </div>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7, whiteSpace: 'pre-line' }}>
                {analysis.ai_insights}
              </p>
            </div>
          )}

          {/* Risk Flags */}
          {analysis.risk_assessment.flags.length > 0 && (
            <div className="card" style={{ padding: '20px 24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                <AlertCircle size={16} color="#F59E0B" />
                <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>Risk Flags</span>
                <span className="badge badge-warning">{analysis.risk_assessment.flags.length}</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {analysis.risk_assessment.flags.map((flag, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '10px 14px',
                    background: 'rgba(245,158,11,0.06)',
                    border: '1px solid rgba(245,158,11,0.15)',
                    borderRadius: 10, fontSize: 13, color: 'var(--text-secondary)',
                  }}>
                    <ChevronRight size={13} color="#F59E0B" style={{ flexShrink: 0 }} />
                    {flag}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Token Table */}
          {analysis.snapshot.tokens.length > 0 && (
            <div className="card">
              <div style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '18px 24px 16px',
                borderBottom: '1px solid var(--border-default)',
              }}>
                <Wallet size={16} color="var(--axon-primary)" />
                <span style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>Token Holdings</span>
                <span className="badge badge-primary">{analysis.snapshot.tokens.length} tokens</span>
              </div>
              <div style={{ overflowX: 'auto' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Token</th>
                      <th style={{ textAlign: 'right' }}>Balance</th>
                      <th style={{ textAlign: 'right' }}>Price</th>
                      <th style={{ textAlign: 'right' }}>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analysis.snapshot.tokens.map((t, i) => (
                      <tr key={i}>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                            <div style={{
                              width: 32, height: 32, borderRadius: 10,
                              background: 'linear-gradient(135deg, var(--axon-primary-light), var(--axon-accent-light))',
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                              fontSize: 11, fontWeight: 700, color: 'var(--axon-primary)',
                              flexShrink: 0,
                            }}>
                              {t.symbol.slice(0, 2)}
                            </div>
                            <div>
                              <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{t.symbol}</div>
                              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{t.name}</div>
                            </div>
                          </div>
                        </td>
                        <td style={{ textAlign: 'right' }} className="num">
                          {parseFloat(t.balance).toLocaleString(undefined, { maximumFractionDigits: 4 })}
                        </td>
                        <td style={{ textAlign: 'right' }} className="num">
                          ${parseFloat(t.price_usd || '0').toFixed(4)}
                        </td>
                        <td style={{ textAlign: 'right', fontWeight: 600, color: 'var(--text-primary)' }} className="num">
                          ${t.value_usd.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!analysis && !loading && (
        <div className="card animate-fade-up" style={{
          animationDelay: '120ms',
          padding: '64px 32px', textAlign: 'center',
          background: 'linear-gradient(135deg, rgba(91,60,245,0.03), rgba(6,196,208,0.02))',
        }}>
          <div style={{
            width: 64, height: 64, borderRadius: 20,
            background: 'var(--axon-primary-light)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 20px',
          }}>
            <Wallet size={28} color="var(--axon-primary)" />
          </div>
          <p style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8, fontFamily: "'Space Grotesk',sans-serif" }}>
            Analyze any X Layer wallet
          </p>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 400, margin: '0 auto' }}>
            Enter a wallet address above to get an AI-powered portfolio breakdown, risk assessment, and insights.
          </p>
        </div>
      )}
    </div>
  )
}
