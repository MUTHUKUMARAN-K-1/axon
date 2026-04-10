import React, { useEffect, useState } from 'react'
import {
  Activity, Zap, Layers, TrendingUp, BarChart3,
  ArrowUpRight, Clock, RefreshCw, ExternalLink,
  Globe, Database, ArrowRight
} from 'lucide-react'
import { getMarketOverview, getTopPools } from '../services/api'

interface Pool {
  pair: string
  tvl_usd: number
  volume_usd: number
  fee_pct: number
  address: string
}

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

export default function Dashboard() {
  const [market, setMarket] = useState<any>(null)
  const [pools, setPools] = useState<Pool[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchData = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true)
    try {
      const [m, p] = await Promise.all([
        getMarketOverview() as Promise<any>,
        getTopPools(8) as Promise<any>,
      ])
      setMarket(m)
      setPools(p.pools || [])
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

  const net = market?.network || {}
  const prices = market?.key_prices || {}

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
      value: prices.OKB ? `$${parseFloat(prices.OKB).toFixed(2)}` : '—',
      sub: 'Native token',
      icon: <TrendingUp size={20} color="white" />,
      gradient: 'linear-gradient(135deg, rgba(16,185,129,0.07) 0%, rgba(16,185,129,0.03) 100%)',
      iconBg: 'linear-gradient(135deg, #10B981, #34D399)',
      delay: 180,
    },
  ]

  return (
    <div style={{ padding: '32px', maxWidth: 1200 }}>
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
