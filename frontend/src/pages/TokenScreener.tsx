import React, { useState } from 'react'
import { Shield, AlertTriangle, CheckCircle, XCircle, TrendingUp,
  Users, Droplets, FileCode, Activity, Search, Loader, Zap, ChevronRight } from 'lucide-react'
import { getSmartMoneySignals, getTokenSecurityScan } from '../services/api'
import type { SecurityScanResponse, SmartMoneySignal } from '../types/api'
import { isEvmAddress } from '../utils/format'

type Tab = 'overview' | 'security' | 'holders' | 'liquidity' | 'signals'

function RiskGauge({ score, color }: { score: number; color: string }) {
  const pct = Math.min(score, 100)
  const r = 52
  const circ = 2 * Math.PI * r
  const dash = (pct / 100) * circ

  return (
    <div style={{ position: 'relative', width: 140, height: 140, margin: '0 auto' }}>
      <svg width={140} height={140} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={70} cy={70} r={r} fill="none" stroke="var(--border-default)" strokeWidth={10} />
        <circle
          cx={70} cy={70} r={r} fill="none"
          stroke={color} strokeWidth={10}
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.8s ease' }}
        />
      </svg>
      <div style={{
        position: 'absolute', inset: 0, display: 'flex',
        flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      }}>
        <div style={{ fontSize: 32, fontWeight: 800, color, lineHeight: 1 }}>{score}</div>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>/ 100</div>
      </div>
    </div>
  )
}

function StageBar({ label, score, max, flags, icon: Icon }: {
  label: string; score: number; max: number; flags: string[]; icon: React.ElementType
}) {
  const pct = (score / max) * 100
  const color = pct > 60 ? '#EF4444' : pct > 30 ? '#F59E0B' : '#10B981'
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
        <Icon size={13} color={color} />
        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', flex: 1 }}>{label}</span>
        <span style={{ fontSize: 11, fontWeight: 700, color }}>{score}/{max}</span>
      </div>
      <div style={{ height: 6, background: 'var(--border-default)', borderRadius: 99, overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: 99, transition: 'width 0.6s ease' }} />
      </div>
      {flags.map((f, i) => (
        <div key={i} style={{
          display: 'flex', alignItems: 'flex-start', gap: 6, marginTop: 5,
          padding: '4px 8px', borderRadius: 6,
          background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.12)',
        }}>
          <AlertTriangle size={10} color="#EF4444" style={{ marginTop: 2, flexShrink: 0 }} />
          <span style={{ fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.4 }}>{f}</span>
        </div>
      ))}
    </div>
  )
}

export default function TokenScreener() {
  const [address, setAddress] = useState('')
  const [tab, setTab] = useState<Tab>('overview')
  const [scan, setScan] = useState<SecurityScanResponse | null>(null)
  const [signals, setSignals] = useState<SmartMoneySignal[]>([])
  const [loading, setLoading] = useState(false)
  const [signalsLoading, setSignalsLoading] = useState(false)
  const [error, setError] = useState('')

  async function runScan() {
    if (!isEvmAddress(address.trim())) {
      setError('Enter a valid token contract address')
      return
    }
    setLoading(true)
    setError('')
    setScan(null)
    try {
      const data = await getTokenSecurityScan(address.trim())
      setScan(data)
      setTab('overview')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Scan failed')
    } finally {
      setLoading(false)
    }
  }

  async function loadSignals() {
    setSignalsLoading(true)
    try {
      const data = await getSmartMoneySignals(15)
      setSignals(data.signals ?? [])
      setTab('signals')
    } catch { /* silent */ } finally {
      setSignalsLoading(false)
    }
  }

  const TABS: { key: Tab; label: string; icon: React.ElementType }[] = [
    { key: 'overview', label: 'Overview', icon: Shield },
    { key: 'security', label: 'Security Stages', icon: AlertTriangle },
    { key: 'holders', label: 'Holders', icon: Users },
    { key: 'liquidity', label: 'Liquidity', icon: Droplets },
    { key: 'signals', label: 'Smart Money', icon: TrendingUp },
  ]

  return (
    <div style={{ padding: '28px 32px', maxWidth: 900, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg, #EF4444 0%, #7C3AED 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(239,68,68,0.3)',
          }}>
            <Shield size={18} color="white" />
          </div>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 800, color: 'var(--text-primary)', margin: 0, letterSpacing: '-0.02em' }}>
              Token Screener
            </h1>
            <p style={{ fontSize: 12, color: 'var(--text-muted)', margin: 0 }}>
              5-stage security analysis · Honeypot detection · Smart money signals
            </p>
          </div>
        </div>
      </div>

      {/* Search bar */}
      <div style={{
        display: 'flex', gap: 10, marginBottom: 24,
        background: 'white', border: '1px solid var(--border-default)',
        borderRadius: 14, padding: '10px 14px',
        boxShadow: '0 2px 12px rgba(0,0,0,0.05)',
      }}>
        <Search size={16} color="var(--text-muted)" style={{ marginTop: 2, flexShrink: 0 }} />
        <input
          value={address}
          onChange={e => setAddress(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && runScan()}
          placeholder="Enter token contract address (0x...) and press Enter"
          style={{
            flex: 1, border: 'none', outline: 'none',
            fontSize: 13, color: 'var(--text-primary)',
            background: 'transparent', fontFamily: 'monospace',
          }}
        />
        <button
          onClick={runScan}
          disabled={loading || !address.trim()}
          style={{
            padding: '6px 16px', borderRadius: 8, border: 'none', cursor: 'pointer',
            background: loading ? 'var(--border-default)' : 'linear-gradient(135deg, #5B3CF5, #7C3AED)',
            color: 'white', fontSize: 12, fontWeight: 700,
            display: 'flex', alignItems: 'center', gap: 6,
          }}
        >
          {loading ? <Loader size={13} style={{ animation: 'spin 1s linear infinite' }} /> : <Shield size={13} />}
          {loading ? 'Scanning...' : 'Scan'}
        </button>
        <button
          onClick={loadSignals}
          disabled={signalsLoading}
          style={{
            padding: '6px 14px', borderRadius: 8, border: '1px solid var(--border-default)',
            cursor: 'pointer', background: 'white',
            color: 'var(--text-primary)', fontSize: 12, fontWeight: 600,
            display: 'flex', alignItems: 'center', gap: 6,
          }}
        >
          {signalsLoading
            ? <Loader size={13} style={{ animation: 'spin 1s linear infinite' }} />
            : <TrendingUp size={13} color="#5B3CF5" />
          }
          Smart Money
        </button>
      </div>

      {error && (
        <div style={{
          padding: '12px 16px', borderRadius: 10, marginBottom: 20,
          background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)',
          color: '#EF4444', fontSize: 13,
        }}>
          {error}
        </div>
      )}

      {/* Tabs — only show if scan exists or signals loaded */}
      {(scan || signals.length > 0) && (
        <div style={{ display: 'flex', gap: 4, marginBottom: 20, borderBottom: '1px solid var(--border-default)', paddingBottom: 0 }}>
          {TABS.map(({ key, label, icon: Icon }) => {
            const active = tab === key
            const disabled = key !== 'signals' && !scan
            return (
              <button
                key={key}
                onClick={() => !disabled && setTab(key)}
                disabled={disabled}
                style={{
                  padding: '8px 14px', border: 'none', cursor: disabled ? 'not-allowed' : 'pointer',
                  background: 'transparent', borderBottom: active ? '2px solid #5B3CF5' : '2px solid transparent',
                  color: active ? '#5B3CF5' : disabled ? 'var(--text-muted)' : 'var(--text-secondary)',
                  fontSize: 12, fontWeight: active ? 700 : 500,
                  display: 'flex', alignItems: 'center', gap: 6, marginBottom: -1,
                  transition: 'all 0.15s',
                }}
              >
                <Icon size={13} />
                {label}
              </button>
            )
          })}
        </div>
      )}

      {/* ── Tab: Overview ── */}
      {scan && tab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: 20 }}>
          {/* Risk gauge */}
          <div style={{
            background: 'white', border: '1px solid var(--border-default)',
            borderRadius: 16, padding: 24, textAlign: 'center',
            boxShadow: '0 2px 12px rgba(0,0,0,0.04)',
          }}>
            <RiskGauge score={scan.risk_score} color={scan.risk_color} />
            <div style={{
              marginTop: 14, padding: '6px 12px', borderRadius: 8,
              background: `${scan.risk_color}18`, border: `1px solid ${scan.risk_color}30`,
              color: scan.risk_color, fontSize: 12, fontWeight: 700, letterSpacing: '0.05em',
            }}>
              {scan.risk_label}
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 10, lineHeight: 1.5 }}>
              {scan.flag_count} flag{scan.flag_count !== 1 ? 's' : ''} detected
            </div>
          </div>

          {/* Info panel */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Recommendation */}
            <div style={{
              padding: '14px 18px', borderRadius: 12,
              background: scan.risk_score >= 65
                ? 'rgba(239,68,68,0.06)' : scan.risk_score >= 30
                ? 'rgba(245,158,11,0.06)' : 'rgba(16,185,129,0.06)',
              border: `1px solid ${scan.risk_color}25`,
            }}>
              {scan.risk_score >= 65
                ? <XCircle size={16} color={scan.risk_color} style={{ marginBottom: 6 }} />
                : scan.risk_score >= 30
                ? <AlertTriangle size={16} color={scan.risk_color} style={{ marginBottom: 6 }} />
                : <CheckCircle size={16} color={scan.risk_color} style={{ marginBottom: 6 }} />
              }
              <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
                {scan.recommendation}
              </div>
            </div>

            {/* Market data */}
            <div style={{
              background: 'white', border: '1px solid var(--border-default)',
              borderRadius: 12, padding: '14px 18px',
              display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12,
            }}>
              {[
                { label: 'Symbol', value: scan.market.symbol || '—' },
                { label: 'Price', value: scan.market.price_usd !== '0' ? `$${parseFloat(scan.market.price_usd).toFixed(6)}` : '—' },
                { label: '24h Change', value: scan.market.price_change_24h !== '0' ? `${scan.market.price_change_24h}%` : '—' },
                { label: 'TVL (Uni V3)', value: scan.market.tvl_usd > 0 ? `$${scan.market.tvl_usd.toLocaleString()}` : '—' },
              ].map(({ label, value }) => (
                <div key={label}>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 2 }}>{label}</div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{value}</div>
                </div>
              ))}
            </div>

            {/* Flags summary */}
            {scan.flags.length > 0 && (
              <div style={{
                background: 'white', border: '1px solid var(--border-default)',
                borderRadius: 12, padding: '14px 18px',
              }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Detected Flags
                </div>
                {scan.flags.map((f, i) => (
                  <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 8, alignItems: 'flex-start' }}>
                    <AlertTriangle size={11} color="#EF4444" style={{ marginTop: 2, flexShrink: 0 }} />
                    <span style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>{f}</span>
                  </div>
                ))}
              </div>
            )}
            {scan.flags.length === 0 && (
              <div style={{
                padding: '12px 16px', borderRadius: 12,
                background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.15)',
                display: 'flex', alignItems: 'center', gap: 8,
              }}>
                <CheckCircle size={15} color="#10B981" />
                <span style={{ fontSize: 13, color: '#065F46', fontWeight: 600 }}>No risk flags detected</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Tab: Security Stages ── */}
      {scan && tab === 'security' && (
        <div style={{
          background: 'white', border: '1px solid var(--border-default)',
          borderRadius: 16, padding: 24,
        }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 20 }}>
            5-Stage Security Analysis
          </div>
          <StageBar label="Honeypot Detection" score={scan.stages.honeypot.score} max={scan.stages.honeypot.max} flags={scan.stages.honeypot.flags} icon={AlertTriangle} />
          <StageBar label="Holder Concentration" score={scan.stages.holder_concentration.score} max={scan.stages.holder_concentration.max} flags={scan.stages.holder_concentration.flags} icon={Users} />
          <StageBar label="Liquidity Safety" score={scan.stages.liquidity.score} max={scan.stages.liquidity.max} flags={scan.stages.liquidity.flags} icon={Droplets} />
          <StageBar label="Contract Verification" score={scan.stages.contract.score} max={scan.stages.contract.max} flags={scan.stages.contract.flags} icon={FileCode} />
          <StageBar label="Activity Anomalies" score={scan.stages.activity.score} max={scan.stages.activity.max} flags={scan.stages.activity.flags} icon={Activity} />
        </div>
      )}

      {/* ── Tab: Holders ── */}
      {scan && tab === 'holders' && (
        <div style={{
          background: 'white', border: '1px solid var(--border-default)',
          borderRadius: 16, padding: 24,
        }}>
          <div style={{ display: 'flex', gap: 20, marginBottom: 20 }}>
            <div style={{ flex: 1, padding: '14px 18px', borderRadius: 12, background: 'var(--axon-primary-light)' }}>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 4 }}>Top 10 Concentration</div>
              <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--axon-primary)' }}>
                {scan.stages.holder_concentration.top10_pct.toFixed(1)}%
              </div>
            </div>
            <div style={{ flex: 1, padding: '14px 18px', borderRadius: 12, background: 'var(--axon-accent-light)' }}>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 4 }}>Total Holders</div>
              <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--axon-accent)' }}>
                {scan.stages.holder_concentration.holder_count.toLocaleString()}
              </div>
            </div>
          </div>
          <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Top Holders
          </div>
          {scan.stages.holder_concentration.top_holders.length === 0
            ? <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>Holder data unavailable (requires OKLink API key)</div>
            : scan.stages.holder_concentration.top_holders.map((h, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: 12,
                padding: '10px 0', borderBottom: '1px solid var(--border-default)',
              }}>
                <div style={{
                  width: 24, height: 24, borderRadius: '50%',
                  background: 'var(--axon-primary-light)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 10, fontWeight: 700, color: 'var(--axon-primary)', flexShrink: 0,
                }}>
                  {i + 1}
                </div>
                <div style={{ flex: 1, fontFamily: 'monospace', fontSize: 12, color: 'var(--text-secondary)' }}>
                  {h.address.slice(0, 10)}...{h.address.slice(-6)}
                  {h.is_contract && (
                    <span style={{ marginLeft: 6, fontSize: 9, padding: '1px 5px', borderRadius: 4, background: 'rgba(91,60,245,0.1)', color: '#5B3CF5', fontWeight: 700 }}>
                      CONTRACT
                    </span>
                  )}
                </div>
                <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>{h.pct.toFixed(2)}%</div>
              </div>
            ))
          }
        </div>
      )}

      {/* ── Tab: Liquidity ── */}
      {scan && tab === 'liquidity' && (
        <div style={{
          background: 'white', border: '1px solid var(--border-default)',
          borderRadius: 16, padding: 24,
        }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
            {[
              { label: 'Total Value Locked', value: `$${scan.stages.liquidity.tvl_usd.toLocaleString()}`, color: '#10B981' },
              { label: '7-Day Volume', value: `$${scan.stages.liquidity.volume_7d_usd.toLocaleString()}`, color: '#5B3CF5' },
              { label: '7-Day Price Change', value: `${scan.stages.activity.price_change_7d_pct.toFixed(2)}%`, color: scan.stages.activity.price_change_7d_pct > 0 ? '#10B981' : '#EF4444' },
              { label: 'Contract Txs', value: scan.stages.contract.tx_count.toLocaleString(), color: '#06C4D0' },
            ].map(({ label, value, color }) => (
              <div key={label} style={{
                padding: '16px 18px', borderRadius: 12,
                background: 'var(--bg-secondary)', border: '1px solid var(--border-default)',
              }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 6 }}>{label}</div>
                <div style={{ fontSize: 20, fontWeight: 800, color }}>{value}</div>
              </div>
            ))}
          </div>
          <div style={{
            padding: '12px 16px', borderRadius: 10,
            background: scan.stages.contract.verified ? 'rgba(16,185,129,0.06)' : 'rgba(245,158,11,0.06)',
            border: `1px solid ${scan.stages.contract.verified ? 'rgba(16,185,129,0.2)' : 'rgba(245,158,11,0.2)'}`,
            display: 'flex', alignItems: 'center', gap: 8,
          }}>
            {scan.stages.contract.verified
              ? <CheckCircle size={14} color="#10B981" />
              : <AlertTriangle size={14} color="#F59E0B" />
            }
            <span style={{ fontSize: 12, fontWeight: 600 }}>
              {scan.stages.contract.verified
                ? `Contract verified: ${scan.stages.contract.contract_name}`
                : 'Contract source not verified on OKLink'
              }
            </span>
          </div>
        </div>
      )}

      {/* ── Tab: Smart Money ── */}
      {tab === 'signals' && (
        <div>
          {signals.length === 0
            ? (
              <div style={{
                padding: 40, textAlign: 'center',
                background: 'white', border: '1px solid var(--border-default)', borderRadius: 16,
              }}>
                <TrendingUp size={32} color="var(--text-muted)" style={{ marginBottom: 12 }} />
                <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>
                  Click "Smart Money" to load accumulation signals
                </div>
              </div>
            )
            : signals.map((s, i) => (
              <div key={i} style={{
                background: 'white', border: '1px solid var(--border-default)',
                borderRadius: 14, padding: '16px 20px', marginBottom: 12,
                display: 'flex', alignItems: 'center', gap: 16,
              }}>
                <div style={{
                  width: 44, height: 44, borderRadius: 12, flexShrink: 0,
                  background: s.signal_label === 'STRONG'
                    ? 'linear-gradient(135deg,#10B981,#06C4D0)'
                    : 'linear-gradient(135deg,#F59E0B,#EF4444)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <Zap size={20} color="white" />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <span style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>{s.pair}</span>
                    <span style={{
                      fontSize: 9, fontWeight: 700, letterSpacing: '0.05em',
                      padding: '2px 7px', borderRadius: 99,
                      background: s.signal_label === 'STRONG' ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)',
                      color: s.signal_label === 'STRONG' ? '#10B981' : '#F59E0B',
                    }}>
                      {s.signal_label}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                    {s.signal_reasons.map((r, j) => (
                      <span key={j} style={{ fontSize: 11, color: 'var(--text-muted)' }}>· {r}</span>
                    ))}
                  </div>
                </div>
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <div style={{ fontSize: 16, fontWeight: 800, color: 'var(--axon-primary)' }}>
                    {s.velocity_ratio}x
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>velocity</div>
                  <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginTop: 2 }}>
                    ${s.tvl_usd.toLocaleString()} TVL
                  </div>
                </div>
                <ChevronRight size={16} color="var(--text-muted)" />
              </div>
            ))
          }
        </div>
      )}

      {/* Empty state */}
      {!scan && signals.length === 0 && !loading && (
        <div style={{
          padding: '48px 32px', textAlign: 'center',
          background: 'white', border: '1px solid var(--border-default)', borderRadius: 20,
          boxShadow: '0 2px 20px rgba(0,0,0,0.04)',
        }}>
          <div style={{
            width: 64, height: 64, borderRadius: 20, margin: '0 auto 20px',
            background: 'linear-gradient(135deg, rgba(91,60,245,0.1), rgba(6,196,208,0.1))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Shield size={30} color="#5B3CF5" />
          </div>
          <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 8 }}>
            Scan any X Layer token
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 380, margin: '0 auto', lineHeight: 1.6 }}>
            Paste a token contract address above to run a full 5-stage security analysis —
            honeypot detection, holder concentration, liquidity safety, contract verification,
            and price anomaly detection.
          </div>
          <div style={{ marginTop: 20, display: 'flex', justifyContent: 'center', gap: 16 }}>
            {['Honeypot Detection', 'Holder Analysis', 'Rug Risk Score', 'Smart Money Signals'].map(f => (
              <span key={f} style={{
                fontSize: 11, fontWeight: 600, padding: '4px 10px', borderRadius: 8,
                background: 'var(--axon-primary-light)', color: 'var(--axon-primary)',
              }}>{f}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
