import { useState, useEffect } from 'react'
import {
  Activity, Zap, TrendingUp, AlertTriangle, Info,
  RefreshCw, Bot, Clock, CheckCircle, ChevronDown, ChevronRight, Copy
} from 'lucide-react'
import { getAgentActivity } from '../services/api'
import type { AgentEvent } from '../types/api'

type IconComponent = typeof Activity

const TYPE_CONFIG: Record<string, { icon: IconComponent; color: string; label: string }> = {
  alert:  { icon: AlertTriangle, color: '#F59E0B', label: 'Alert'  },
  info:   { icon: Info,          color: '#5B3CF5', label: 'Info'   },
  action: { icon: CheckCircle,   color: '#10B981', label: 'Action' },
  yield:  { icon: TrendingUp,    color: '#06C4D0', label: 'Yield'  },
  gas:    { icon: Zap,           color: '#8B5CF6', label: 'Gas'    },
}

function formatValue(k: string, v: unknown): { text: string; color?: string } {
  if (v === null || v === undefined) return { text: '—' }
  if (typeof v === 'number') return { text: v.toLocaleString() }
  if (typeof v === 'object') {
    const obj = v as Record<string, unknown>
    if (obj.type && obj.from) return { text: `${obj.type} ${String(obj.from).slice(0, 8)}…`, color: '#10B981' }
    if (obj.amount_usdt)      return { text: `$${obj.amount_usdt} USDT`, color: '#06C4D0' }
    return { text: JSON.stringify(v).slice(0, 36) }
  }
  const s = String(v)
  if (k === 'risk_label') {
    const colors: Record<string, string> = { SAFE: '#10B981', 'LOW RISK': '#F59E0B', 'MEDIUM RISK': '#EF4444', 'HIGH RISK': '#7C3AED', 'CRITICAL': '#ef4444' }
    const c = Object.entries(colors).find(([lbl]) => s.includes(lbl))
    return { text: s, color: c?.[1] }
  }
  if (k === 'token' || k === 'token_address') {
    return { text: s.slice(0, 6) + '…' + s.slice(-4) }
  }
  return { text: s }
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text).catch(() => {})
}

function EventCard({ event, index }: { event: AgentEvent; index: number }) {
  const cfg = TYPE_CONFIG[event.type] || TYPE_CONFIG.info
  const Icon = cfg.icon
  const ts = new Date(event.timestamp)
  const [expanded, setExpanded] = useState(false)
  const isNewest = index === 0
  const dataEntries = Object.entries(event.data)

  return (
    <div style={{
      display: 'flex', gap: 0, position: 'relative',
      borderBottom: '1px solid #21262d',
      animation: isNewest ? 'fadeSlideIn 0.4s ease' : 'none',
    }}>
      {/* Left accent border */}
      <div style={{
        width: 3, flexShrink: 0,
        background: isNewest ? cfg.color : 'transparent',
        borderRadius: '0 2px 2px 0',
        transition: 'background 0.3s',
      }} />

      {/* Timeline track */}
      <div style={{
        width: 48, flexShrink: 0, display: 'flex', flexDirection: 'column',
        alignItems: 'center', paddingTop: 16,
      }}>
        {/* Vertical line */}
        <div style={{
          position: 'absolute', left: 26, top: 0, bottom: 0,
          width: 1, background: '#21262d', zIndex: 0,
        }} />
        {/* Icon dot */}
        <div style={{
          width: 32, height: 32, borderRadius: '50%', zIndex: 1,
          background: `${cfg.color}18`,
          border: `1.5px solid ${cfg.color}60`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: isNewest ? `0 0 12px ${cfg.color}40` : 'none',
          animation: isNewest ? 'iconPulse 2s ease-in-out infinite' : 'none',
        }}>
          <Icon size={14} color={cfg.color} />
        </div>
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0, padding: '12px 12px 12px 4px' }}>
        {/* Message row */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
          <div
            style={{
              flex: 1, fontSize: 12.5, color: '#e6edf3', lineHeight: 1.5,
              overflow: 'hidden',
              display: '-webkit-box', WebkitLineClamp: expanded ? 99 : 1,
              WebkitBoxOrient: 'vertical' as const,
              cursor: dataEntries.length > 0 ? 'pointer' : 'default',
            }}
            onClick={() => setExpanded(!expanded)}
          >
            {event.message}
          </div>
          {/* Expand toggle */}
          {dataEntries.length > 0 && (
            <button
              onClick={() => setExpanded(!expanded)}
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                color: '#6e7681', padding: 0, flexShrink: 0, marginTop: 1,
              }}
            >
              {expanded ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
            </button>
          )}
        </div>

        {/* Tags */}
        {dataEntries.length > 0 && (
          <div style={{ marginTop: 7, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {dataEntries.slice(0, expanded ? 99 : 3).map(([k, v]) => {
              const { text, color } = formatValue(k, v)
              const isAddr = (k === 'token' || k === 'token_address') && typeof v === 'string' && v.startsWith('0x')
              return (
                <span
                  key={k}
                  onClick={isAddr ? () => copyToClipboard(String(v)) : undefined}
                  title={isAddr ? `Copy: ${v}` : undefined}
                  style={{
                    fontSize: 10, fontFamily: "'JetBrains Mono', monospace",
                    color: color || cfg.color,
                    background: `${cfg.color}12`,
                    border: `1px solid ${cfg.color}22`,
                    borderRadius: 4, padding: '2px 7px',
                    display: 'inline-flex', alignItems: 'center', gap: 4,
                    cursor: isAddr ? 'pointer' : 'default',
                    maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                  }}
                >
                  <span style={{ color: '#6e7681' }}>{k}</span>
                  <span style={{ color: '#30363d' }}>·</span>
                  {text}
                  {isAddr && <Copy size={9} style={{ opacity: 0.5, flexShrink: 0 }} />}
                </span>
              )
            })}
            {!expanded && dataEntries.length > 3 && (
              <span
                onClick={() => setExpanded(true)}
                style={{
                  fontSize: 10, color: '#6e7681', cursor: 'pointer',
                  padding: '2px 6px', borderRadius: 4,
                  border: '1px solid #30363d',
                }}
              >
                +{dataEntries.length - 3} more
              </span>
            )}
          </div>
        )}
      </div>

      {/* Time + badge */}
      <div style={{ flexShrink: 0, padding: '12px 16px 12px 0', textAlign: 'right' }}>
        <div style={{
          fontSize: 10, fontFamily: "'JetBrains Mono', monospace",
          color: '#6e7681',
        }}>
          {ts.toLocaleTimeString()}
        </div>
        <div style={{ marginTop: 4 }}>
          <span style={{
            fontSize: 9, fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase',
            color: cfg.color, background: `${cfg.color}18`,
            border: `1px solid ${cfg.color}30`,
            borderRadius: 3, padding: '2px 5px',
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
      const data = await getAgentActivity(50)
      const acts = data.activities ?? []
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

  useEffect(() => { fetchActivity() }, [])

  useEffect(() => {
    if (!autoRefresh) return
    const t = setInterval(fetchActivity, 15000)
    return () => clearInterval(t)
  }, [autoRefresh])

  const metrics = [
    { label: 'Events',  value: stats.total,      icon: Activity,      color: '#5B3CF5' },
    { label: 'Alerts',  value: stats.alerts,      icon: AlertTriangle, color: '#F59E0B' },
    { label: 'Yields',  value: stats.yields,      icon: TrendingUp,    color: '#06C4D0' },
    { label: 'Cycle',   value: '60s',             icon: Clock,         color: '#10B981' },
  ]

  return (
    <div style={{ padding: '28px 32px', maxWidth: 860, margin: '0 auto' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 22 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 42, height: 42, borderRadius: 11,
            background: 'linear-gradient(135deg, #10B981 0%, #06C4D0 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 16px rgba(16,185,129,0.35)',
          }}>
            <Bot size={20} color="white" />
          </div>
          <div>
            <h1 style={{
              margin: 0, fontSize: 22, fontWeight: 700,
              fontFamily: "'Space Grotesk', sans-serif",
              color: 'var(--text-primary)', letterSpacing: '-0.02em',
            }}>Agent Activity</h1>
            <p style={{ margin: 0, fontSize: 12, color: 'var(--text-muted)' }}>
              AXON autonomous agent — scanning X Layer every 60s
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '7px 13px', borderRadius: 8, cursor: 'pointer',
              background: autoRefresh ? 'rgba(16,185,129,0.1)' : '#161b22',
              border: autoRefresh ? '1px solid rgba(16,185,129,0.35)' : '1px solid #30363d',
              fontSize: 12, fontWeight: 600,
              color: autoRefresh ? '#10B981' : '#6e7681',
            }}
          >
            <span style={{
              width: 7, height: 7, borderRadius: '50%',
              background: autoRefresh ? '#10B981' : '#6e7681',
              boxShadow: autoRefresh ? '0 0 6px #10B981' : 'none',
              animation: autoRefresh ? 'livePulse 1.5s ease-in-out infinite' : 'none',
              display: 'inline-block',
            }} />
            {autoRefresh ? 'Live' : 'Paused'}
          </button>
          <button
            onClick={fetchActivity}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '7px 13px', borderRadius: 8, cursor: 'pointer',
              background: '#161b22', border: '1px solid #30363d',
              fontSize: 12, fontWeight: 600, color: '#8b949e',
            }}
          >
            <RefreshCw size={12} />
            Refresh
          </button>
        </div>
      </div>

      {/* Metrics bar */}
      <div style={{
        display: 'flex', background: '#0d1117',
        border: '1px solid #21262d', borderRadius: 12, overflow: 'hidden',
        marginBottom: 18,
      }}>
        {metrics.map(({ label, value, icon: Icon, color }, i) => (
          <div key={label} style={{
            flex: 1, padding: '14px 18px', display: 'flex', alignItems: 'center', gap: 12,
            borderLeft: i === 0 ? 'none' : '1px solid #21262d',
          }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8, flexShrink: 0,
              background: `${color}18`, border: `1px solid ${color}30`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Icon size={14} color={color} />
            </div>
            <div>
              <div style={{ fontSize: 10, color: '#6e7681', fontWeight: 600,
                textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 2 }}>
                {label}
              </div>
              <div style={{ fontSize: 20, fontWeight: 700, color: '#e6edf3',
                fontFamily: "'Space Grotesk', sans-serif", lineHeight: 1 }}>
                {value}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Last refresh */}
      {lastRefresh && (
        <div style={{ fontSize: 11, color: '#6e7681', marginBottom: 10,
          display: 'flex', alignItems: 'center', gap: 5 }}>
          <Clock size={10} />
          {lastRefresh.toLocaleTimeString()}
          {autoRefresh && <span style={{ color: '#10B981' }}> · auto-refresh 15s</span>}
        </div>
      )}

      {/* Feed */}
      <div style={{
        background: '#0d1117', border: '1px solid #21262d',
        borderRadius: 14, overflow: 'hidden',
      }}>
        {/* Feed header */}
        <div style={{
          padding: '11px 16px', borderBottom: '1px solid #21262d',
          display: 'flex', alignItems: 'center', gap: 8,
          background: '#161b22',
        }}>
          <span style={{
            width: 8, height: 8, borderRadius: '50%', background: '#10B981',
            boxShadow: '0 0 8px #10B981',
            animation: 'livePulse 1.5s ease-in-out infinite',
            display: 'inline-block', flexShrink: 0,
          }} />
          <span style={{ fontSize: 12, fontWeight: 600, color: '#e6edf3' }}>
            Live Activity Feed
          </span>
          <span style={{
            marginLeft: 'auto', fontSize: 11, color: '#6e7681',
            fontFamily: "'JetBrains Mono', monospace",
          }}>
            {events.length} events
          </span>
        </div>

        {loading ? (
          <div style={{ padding: 48, textAlign: 'center', color: '#6e7681', fontSize: 13 }}>
            <Activity size={22} style={{ margin: '0 auto 10px', opacity: 0.3, display: 'block' }} />
            Loading agent activity...
          </div>
        ) : events.length === 0 ? (
          <div style={{ padding: 48, textAlign: 'center', color: '#6e7681', fontSize: 13 }}>
            <Bot size={22} style={{ margin: '0 auto 10px', opacity: 0.3, display: 'block' }} />
            Agent starting up — check back in 60s
          </div>
        ) : (
          events.map((event, i) => <EventCard key={event.id} event={event} index={i} />)
        )}
      </div>

      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(-6px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes livePulse {
          0%, 100% { opacity: 1; }
          50%       { opacity: 0.4; }
        }
        @keyframes iconPulse {
          0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
          50%       { box-shadow: 0 0 14px rgba(16,185,129,0.35); }
        }
      `}</style>
    </div>
  )
}
