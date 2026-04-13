import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Activity, Zap, Layers, TrendingUp, BarChart3,
  Clock, RefreshCw, ExternalLink,
  Globe, Database, ArrowRight, Shield, Brain,
  MessageSquare, Terminal, Trophy, Link
} from 'lucide-react'
import { getMarketOverview, getTopPools } from '../services/api'
import type { MarketOverview, Pool } from '../types/api'
import { formatTokenPrice } from '../utils/format'

const API = 'https://axon-onld.onrender.com'

interface StatCardProps {
  label: string
  value: string | number
  sub?: string
  icon: React.ReactNode
  gradient: string
  iconBg: string
  delay?: number
}

function StatCard({ label, value, sub, icon, gradient, iconBg, delay = 0 }: StatCardProps) {
  return (
    <div
      className="stat-card animate-fade-up"
      style={{
        animationDelay: `${delay}ms`,
        background: gradient,
        cursor: 'default',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'rgba(15,7,40,0.5)', marginBottom: 8 }}>
            {label}
          </p>
          <p style={{ fontSize: 26, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", color: 'var(--text-primary)', letterSpacing: '-0.03em', lineHeight: 1 }} className="num">
            {value}
          </p>
          {sub && (
            <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6 }}>{sub}</p>
          )}
        </div>
        <div
          style={{
            width: 44, height: 44, borderRadius: 12,
            background: iconBg,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          }}
        >
          {icon}
        </div>
      </div>
    </div>
  )
}

function SkeletonStat() {
  return (
    <div className="stat-card">
      <div className="skeleton" style={{ height: 14, width: '50%', marginBottom: 12 }} />
      <div className="skeleton" style={{ height: 28, width: '70%', marginBottom: 8 }} />
      <div className="skeleton" style={{ height: 12, width: '40%' }} />
    </div>
  )
}

// ── Hero Section ──────────────────────────────────────────────────────────────
function HeroSection({ totalVerdicts }: { totalVerdicts: number | null }) {
  const navigate = useNavigate()

  const features = [
    { label: '45 MCP Tools', variant: '', icon: <Brain size={12} /> },
    { label: '6-Source Security Scan', variant: 'feature-pill-accent', icon: <Shield size={12} /> },
    { label: 'x402 Micro-Payments', variant: 'feature-pill-green', icon: <Zap size={12} /> },
    { label: 'On-Chain Oracle', variant: '', icon: <Link size={12} /> },
    { label: 'Ask in Plain English', variant: 'feature-pill-accent', icon: <MessageSquare size={12} /> },
    { label: 'Autonomous Agent Loop', variant: 'feature-pill-green', icon: <Terminal size={12} /> },
  ]

  const contracts = [
    {
      label: 'VerdictLedger',
      addr: '0x0191d5ada5...8a53f8',
      url: 'https://www.oklink.com/xlayer/address/0x0191d5ada56672507fdb283ac59d45bde08a53f8',
      color: 'var(--axon-primary)',
    },
    {
      label: 'ConfidenceBond',
      addr: '0xe164011de2...ddb2e2',
      url: 'https://www.oklink.com/xlayer/address/0xe164011de202eb0ebf5f01ee5d9851c801a9c675',
      color: '#06C4D0',
    },
  ]

  return (
    <div className="hero-section animate-fade-up">
      <div className="hero-grid" />

      {/* Hackathon badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 6,
          padding: '4px 12px', borderRadius: 99,
          background: 'linear-gradient(135deg, rgba(245,158,11,0.15), rgba(234,179,8,0.10))',
          border: '1px solid rgba(245,158,11,0.35)',
        }}>
          <Trophy size={11} color="#F59E0B" />
          <span style={{ fontSize: 11, fontWeight: 700, color: '#B45309', letterSpacing: '0.04em' }}>
            OKX Build-X 2026 · X Layer Arena + Skills Arena
          </span>
        </div>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 5,
          padding: '4px 10px', borderRadius: 99,
          background: 'rgba(16,185,129,0.10)',
          border: '1px solid rgba(16,185,129,0.25)',
        }}>
          <span className="live-dot" style={{ width: 6, height: 6 }} />
          <span style={{ fontSize: 11, fontWeight: 600, color: '#059669' }}>LIVE on Mainnet</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 32, alignItems: 'center', position: 'relative', zIndex: 1 }}>
        {/* Left: headline + features */}
        <div>
          <h1 style={{
            fontSize: 'clamp(28px, 4vw, 44px)',
            fontWeight: 800,
            fontFamily: "'Space Grotesk', sans-serif",
            letterSpacing: '-0.04em',
            lineHeight: 1.1,
            marginBottom: 12,
          }}>
            <span className="text-gradient-animate">Neural Intelligence</span>
            <br />
            <span style={{ color: 'var(--text-primary)' }}>Layer for X Layer</span>
          </h1>
          <p style={{
            fontSize: 15,
            color: 'var(--text-secondary)',
            lineHeight: 1.6,
            maxWidth: 480,
            marginBottom: 20,
          }}>
            Give your AI agents onchain senses — 45 MCP tools for security scanning,
            DeFi analytics, wallet intelligence, and x402 micro-payments, all on X Layer Mainnet.
          </p>

          {/* CTA Buttons */}
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 24 }}>
            <button
              className="btn-primary"
              style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 13, padding: '9px 18px' }}
              onClick={() => navigate('/screener')}
            >
              <Shield size={14} /> Scan a Token
            </button>
            <button
              className="btn-ghost"
              style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 13 }}
              onClick={() => navigate('/ask')}
            >
              <MessageSquare size={14} /> Ask AXON
            </button>
            <a
              href={`${API}/llms.txt`}
              target="_blank"
              rel="noreferrer"
              className="btn-ghost"
              style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 13, textDecoration: 'none' }}
            >
              <Terminal size={14} /> llms.txt
            </a>
          </div>

          {/* Feature pills */}
          <div className="feature-pills">
            {features.map(f => (
              <span key={f.label} className={`feature-pill ${f.variant}`}>
                {f.icon}{f.label}
              </span>
            ))}
          </div>
        </div>

        {/* Right: stats + contracts */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, minWidth: 220 }}>
          {/* Live stats box */}
          <div style={{
            background: 'var(--surface-card)',
            border: '1px solid var(--border-default)',
            borderRadius: 14,
            overflow: 'hidden',
          }}>
            <div style={{
              padding: '8px 14px',
              borderBottom: '1px solid var(--border-default)',
              fontSize: 10, fontWeight: 700, letterSpacing: '0.08em',
              textTransform: 'uppercase', color: 'var(--text-muted)',
            }}>Live Stats</div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              {[
                { value: '45', label: 'MCP Tools' },
                { value: '2', label: 'Live Contracts' },
                { value: totalVerdicts != null ? String(totalVerdicts) : '—', label: 'On-Chain Verdicts' },
                { value: 'Chain 196', label: 'X Layer Mainnet' },
              ].map((s, i) => (
                <div key={i} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '8px 14px',
                  borderBottom: i < 3 ? '1px solid var(--border-default)' : 'none',
                }}>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{s.label}</span>
                  <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', fontFamily: "'Space Grotesk',sans-serif" }} className="num">{s.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Contract addresses */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {contracts.map(c => (
              <a
                key={c.label}
                href={c.url}
                target="_blank"
                rel="noreferrer"
                className="contract-chip"
                style={{ justifyContent: 'space-between' }}
              >
                <span style={{ color: c.color, fontWeight: 600, fontSize: 10 }}>{c.label}</span>
                <span>{c.addr}</span>
                <ExternalLink size={9} />
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [market, setMarket] = useState<MarketOverview | null>(null)
  const [pools, setPools] = useState<Pool[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [totalVerdicts, setTotalVerdicts] = useState<number | null>(null)

  const fetchData = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true)
    try {
      const [m, p] = await Promise.all([getMarketOverview(), getTopPools(8)])
      setMarket(m)
      setPools(p.pools ?? [])
      setLastUpdated(new Date())
    } catch (e) {
      console.error('Dashboard fetch error:', e)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(() => fetchData(), 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    fetch(`${API}/mcp/call`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool_name: 'get_total_verdicts', arguments: {} }),
      signal: AbortSignal.timeout(8000),
    })
      .then(r => r.json())
      .then(d => setTotalVerdicts(d?.result?.total_verdicts ?? null))
      .catch(() => {})
  }, [])

  const net = market?.network ?? {}
  const prices = market?.key_prices ?? {}

  const STATS = [
    {
      label: 'Latest Block',
      value: net.latest_block ? `#${net.latest_block.toLocaleString()}` : '—',
      sub: 'X Layer Mainnet',
      icon: <Layers size={20} color="white" />,
      gradient: 'linear-gradient(135deg, rgba(91,60,245,0.07) 0%, rgba(91,60,245,0.03) 100%)',
      iconBg: 'linear-gradient(135deg, #5B3CF5, #7C5CF5)',
      delay: 0,
    },
    {
      label: 'Gas Price',
      value: net.gas_price_gwei ? `${net.gas_price_gwei} Gwei` : '—',
      sub: 'Current base fee',
      icon: <Zap size={20} color="white" />,
      gradient: 'linear-gradient(135deg, rgba(245,158,11,0.07) 0%, rgba(245,158,11,0.03) 100%)',
      iconBg: 'linear-gradient(135deg, #F59E0B, #FBBF24)',
      delay: 60,
    },
    {
      label: 'Gas Utilization',
      value: net.gas_utilization_pct ? `${net.gas_utilization_pct}%` : '—',
      sub: 'Last block',
      icon: <Activity size={20} color="white" />,
      gradient: 'linear-gradient(135deg, rgba(6,196,208,0.07) 0%, rgba(6,196,208,0.03) 100%)',
      iconBg: 'linear-gradient(135deg, #06C4D0, #22D3EE)',
      delay: 120,
    },
    {
      label: 'OKB Price',
      value: prices.OKB ? formatTokenPrice(prices.OKB, 2) : '—',
      sub: 'Native token',
      icon: <TrendingUp size={20} color="white" />,
      gradient: 'linear-gradient(135deg, rgba(16,185,129,0.07) 0%, rgba(16,185,129,0.03) 100%)',
      iconBg: 'linear-gradient(135deg, #10B981, #34D399)',
      delay: 180,
    },
  ]

  return (
    <div style={{ padding: '32px', maxWidth: 1200 }}>
      {/* Hero */}
      <HeroSection totalVerdicts={totalVerdicts} />

      {/* Header */}
      <div
        className="animate-fade-up"
        style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 32 }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
            <span className="live-dot" />
            <span style={{ fontSize: 12, color: 'var(--axon-success)', fontWeight: 600 }}>Live</span>
          </div>
          <h1 style={{ fontSize: 30, fontWeight: 700, fontFamily: "'Space Grotesk',sans-serif", letterSpacing: '-0.03em' }}>
            X Layer Dashboard
          </h1>
          <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4 }}>
            Real-time neural intelligence · Powered by Onchain OS
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {lastUpdated && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: 6,
              fontSize: 12, color: 'var(--text-muted)',
              background: 'white', border: '1px solid var(--border-default)',
              borderRadius: 8, padding: '6px 12px',
            }}>
              <Clock size={12} />
              Updated {lastUpdated.toLocaleTimeString()}
            </div>
          )}
          <button
            id="dashboard-refresh-btn"
            onClick={() => fetchData(true)}
            disabled={refreshing}
            className="btn-ghost"
            style={{ display: 'flex', alignItems: 'center', gap: 6 }}
          >
            <RefreshCw size={14} style={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        {loading
          ? [0,1,2,3].map(i => <SkeletonStat key={i} />)
          : STATS.map(s => <StatCard key={s.label} {...s} />)
        }
      </div>

      {/* Pools Table */}
      <div className="card animate-fade-up" style={{ animationDelay: '200ms', marginBottom: 24 }}>
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          padding: '20px 24px 16px',
          borderBottom: '1px solid var(--border-default)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: 'var(--axon-primary-light)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <BarChart3 size={16} color="var(--axon-primary)" />
            </div>
            <div>
              <p style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>Uniswap V3 Top Pools</p>
              <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>on X Layer · {pools.length} pools</p>
            </div>
          </div>
          <a
            href="https://app.uniswap.org"
            target="_blank"
            rel="noreferrer"
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              fontSize: 12, fontWeight: 600, color: 'var(--axon-primary)',
              background: 'var(--axon-primary-light)',
              padding: '6px 12px', borderRadius: 8, textDecoration: 'none',
              transition: 'all 0.15s',
            }}
          >
            Open Uniswap <ExternalLink size={12} />
          </a>
        </div>

        {loading ? (
          <div style={{ padding: 32 }}>
            {[0,1,2,3].map(i => (
              <div key={i} style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
                <div className="skeleton" style={{ flex: 2, height: 16 }} />
                <div className="skeleton" style={{ flex: 1, height: 16 }} />
                <div className="skeleton" style={{ flex: 1, height: 16 }} />
                <div className="skeleton" style={{ flex: 1, height: 16 }} />
              </div>
            ))}
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Pool Pair</th>
                  <th style={{ textAlign: 'center' }}>Fee Tier</th>
                  <th style={{ textAlign: 'right' }}>TVL</th>
                  <th style={{ textAlign: 'right' }}>Volume</th>
                </tr>
              </thead>
              <tbody>
                {pools.length === 0 ? (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', padding: '40px 16px', color: 'var(--text-muted)' }}>
                      <Database size={24} style={{ margin: '0 auto 8px', opacity: 0.4, display: 'block' }} />
                      No pool data — check Uniswap subgraph connection
                    </td>
                  </tr>
                ) : (
                  pools.map((p, i) => (
                    <tr key={i}>
                      <td>
                        <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{p.pair}</span>
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <span className="badge badge-primary">{p.fee_pct}%</span>
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 600, color: 'var(--text-primary)' }} className="num">
                        ${p.tvl_usd.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      </td>
                      <td style={{ textAlign: 'right' }} className="num">
                        ${p.volume_usd.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Ecosystem Links */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        {[
          {
            label: 'OKLink Explorer',
            url: 'https://www.oklink.com/xlayer',
            desc: 'Block explorer for X Layer',
            icon: <Globe size={18} color="var(--axon-primary)" />,
            color: 'var(--axon-primary-light)',
          },
          {
            label: 'OKX Bridge',
            url: 'https://www.okx.com/xlayer/bridge',
            desc: 'Bridge assets to X Layer',
            icon: <ArrowRight size={18} color="#06C4D0" />,
            color: 'var(--axon-accent-light)',
          },
          {
            label: 'Onchain OS Docs',
            url: 'https://www.okx.com/web3/build',
            desc: 'Developer APIs & tools',
            icon: <Database size={18} color="#10B981" />,
            color: '#D1FAE5',
          },
        ].map((link) => (
          <a
            key={link.label}
            href={link.url}
            target="_blank"
            rel="noreferrer"
            className="card animate-fade-up"
            style={{
              display: 'block', padding: '20px', textDecoration: 'none',
              animationDelay: '300ms', cursor: 'pointer',
            }}
          >
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: link.color,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              marginBottom: 12,
            }}>
              {link.icon}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
              <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{link.label}</p>
              <ExternalLink size={13} color="var(--text-muted)" />
            </div>
            <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>{link.desc}</p>
          </a>
        ))}
      </div>
    </div>
  )
}
