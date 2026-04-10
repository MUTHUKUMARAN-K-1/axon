import React, { useState, useEffect } from 'react'
import {
  Activity, Zap, TrendingUp, AlertTriangle, Info,
  RefreshCw, Bot, Clock, CheckCircle, Wifi
} from 'lucide-react'

const API = import.meta.env.VITE_AXON_API_URL || 'https://axon-onld.onrender.com'

interface AgentEvent {
  id: number
  type: 'alert' | 'info' | 'action' | 'yield' | 'gas'
  message: string
  data: Record<string, any>
  timestamp: string
}

const TYPE_CONFIG: Record<string, { icon: any; color: string; bg: string; label: string }> = {
  alert: { icon: AlertTriangle, color: '#F59E0B', bg: 'rgba(245,158,11,0.08)', label: 'Alert' },
  info:  { icon: Info,          color: '#5B3CF5', bg: 'rgba(91,60,245,0.06)',   label: 'Info' },
  action:{ icon: CheckCircle,   color: '#10B981', bg: 'rgba(16,185,129,0.08)', label: 'Action' },
  yield: { icon: TrendingUp,    color: '#06C4D0', bg: 'rgba(6,196,208,0.08)',  label: 'Yield' },
  gas:   { icon: Zap,           color: '#8B5CF6', bg: 'rgba(139,92,246,0.08)', label: 'Gas' },
}

function EventCard({ event, index }: { event: AgentEvent; index: number }) {
  const cfg = TYPE_CONFIG[event.type] || TYPE_CONFIG.info
  const Icon = cfg.icon
  const ts = new Date(event.timestamp)

  return (
    <div
      style={{
        display: 'flex', gap: 14, alignItems: 'flex-start',
        padding: '14px 18px',
        background: index === 0 ? cfg.bg : 'transparent',
        borderBottom: '1px solid var(--border-default)',
        transition: 'background 0.2s ease',
        animation: index === 0 ? 'fadeSlideIn 0.35s ease' : 'none',
      }}
    >
      {/* Icon */}
      <div style={{
        width: 36, height: 36, borderRadius: 10, flexShrink: 0,
        background: cfg.bg, border: `1px solid ${cfg.color}30`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <Icon size={16} color={cfg.color} />
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.5 }}>
          {event.message}
        </div>
        {Object.keys(event.data).length > 0 && (
          <div style={{
            marginTop: 6, display: 'flex', gap: 8, flexWrap: 'wrap',
          }}>
            {Object.entries(event.data).slice(0, 3).map(([k, v]) => (
              <span key={k} style={{
                fontSize: 10, fontFamily: "'JetBrains Mono', monospace",
                color: cfg.color, background: cfg.bg,
                border: `1px solid ${cfg.color}25`,
                borderRadius: 4, padding: '2px 6px',
              }}>
                {k}: {typeof v === 'number' ? v.toLocaleString() : String(v)}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Time */}
      <div style={{ fontSize: 11, color: 'var(--text-muted)', flexShrink: 0, textAlign: 'right' }}>
        <div style={{ fontFamily: "'JetBrains Mono', monospace" }}>
          {ts.toLocaleTimeString()}
        </div>
        <div style={{ marginTop: 2 }}>
          <span style={{
            background: cfg.bg, color: cfg.color, fontSize: 10, fontWeight: 600,
            borderRadius: 4, padding: '1px 5px', border: `1px solid ${cfg.color}30`,
          }}>
            {cfg.label}
          </span>
        </div>
      </div>
    </div>
  )
}

export default function AgentActivity() {
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [stats, setStats] = useState({ total: 0, alerts: 0, yields: 0 })

  const fetchActivity = async () => {
    try {
      const res = await fetch(`${API}/api/agent/activity?limit=50`)
      const data = await res.json()
      const acts: AgentEvent[] = data.activities || []
      setEvents(acts)
      setLastRefresh(new Date())
      setStats({
        total: data.activity_count || acts.length,
        alerts: acts.filter(e => e.type === 'alert').length,
        yields: acts.filter(e => e.type === 'yield').length,
      })
    } catch (err) {
      console.error('Failed to fetch activity:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchActivity()
  }, [])

  useEffect(() => {
    if (!autoRefresh) return
    const t = setInterval(fetchActivity, 15000) // refresh every 15s
    return () => clearInterval(t)
  }, [autoRefresh])

  return (
    <div style={{ padding: '32px', maxWidth: 900, margin: '0 auto' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 28 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 44, height: 44, borderRadius: 12,
              background: 'linear-gradient(135deg, #10B981, #06C4D0)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 4px 16px rgba(16,185,129,0.3)',
            }}>
              <Bot size={22} color="white" />
            </div>
            <div>
              <h1 style={{
                margin: 0, fontSize: 24, fontWeight: 700,
                fontFamily: "'Space Grotesk', sans-serif",
                color: 'var(--text-primary)', letterSpacing: '-0.02em',
              }}>
                Agent Activity
              </h1>
              <p style={{ margin: 0, fontSize: 13, color: 'var(--text-muted)' }}>
                AXON autonomous agent — scanning X Layer every 60s
              </p>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {/* Auto-refresh toggle */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '8px 14px', borderRadius: 10, cursor: 'pointer',
              background: autoRefresh ? 'rgba(16,185,129,0.08)' : 'var(--bg-subtle)',
              border: autoRefresh ? '1px solid rgba(16,185,129,0.3)' : '1px solid var(--border-default)',
              fontSize: 12, fontWeight: 600,
              color: autoRefresh ? '#059669' : 'var(--text-muted)',
              transition: 'all 0.2s ease',
            }}
          >
            <Wifi size={13} />
            {autoRefresh ? 'Live' : 'Paused'}
          </button>

          <button
            onClick={fetchActivity}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '8px 14px', borderRadius: 10, cursor: 'pointer',
              background: 'white', border: '1px solid var(--border-default)',
              fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)',
              transition: 'all 0.2s ease',
            }}
          >
            <RefreshCw size={13} />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 24 }}>
        {[
          { label: 'Total Events', value: stats.total, icon: Activity, color: '#5B3CF5' },
          { label: 'Alerts Fired', value: stats.alerts, icon: AlertTriangle, color: '#F59E0B' },
          { label: 'Yield Signals', value: stats.yields, icon: TrendingUp, color: '#06C4D0' },
          { label: 'Uptime',        value: '60s cycles', icon: Clock, color: '#10B981' },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} style={{
            background: 'white', border: '1px solid var(--border-default)',
            borderRadius: 14, padding: '16px 18px',
            boxShadow: 'var(--shadow-sm)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <Icon size={14} color={color} />
              <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600,
                textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</span>
            </div>
            <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--text-primary)',
              fontFamily: "'Space Grotesk', sans-serif" }}>
              {value}
            </div>
          </div>
        ))}
      </div>

      {/* Last refresh */}
      {lastRefresh && (
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 12,
          display: 'flex', alignItems: 'center', gap: 6 }}>
          <Clock size={11} />
          Last updated: {lastRefresh.toLocaleTimeString()}
          {autoRefresh && <span style={{ color: '#10B981' }}> · Auto-refreshing every 15s</span>}
        </div>
      )}

      {/* Event Feed */}
      <div style={{
        background: 'white', border: '1px solid var(--border-default)',
        borderRadius: 16, overflow: 'hidden',
        boxShadow: 'var(--shadow-sm)',
      }}>
        <div style={{
          padding: '14px 18px', borderBottom: '1px solid var(--border-default)',
          background: 'linear-gradient(135deg, rgba(91,60,245,0.03), rgba(6,196,208,0.03))',
          display: 'flex', alignItems: 'center', gap: 8,
        }}>
          <span className="live-dot" />
          <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
            Live Activity Feed
          </span>
          <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 'auto' }}>
            {events.length} events
          </span>
        </div>

        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)', fontSize: 14 }}>
            <Activity size={24} style={{ margin: '0 auto 12px', opacity: 0.3, display: 'block' }} />
            Loading agent activity...
          </div>
        ) : events.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)', fontSize: 14 }}>
            <Bot size={24} style={{ margin: '0 auto 12px', opacity: 0.3, display: 'block' }} />
            Agent is starting up — check back in 60 seconds
          </div>
        ) : (
          events.map((event, i) => <EventCard key={event.id} event={event} index={i} />)
        )}
      </div>

      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; background: rgba(91,60,245,0.1); }
          to   { opacity: 1; }
        }
      `}</style>
    </div>
  )
}
