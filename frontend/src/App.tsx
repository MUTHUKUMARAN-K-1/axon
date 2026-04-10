import React from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { Brain, LayoutDashboard, Wallet, BarChart3, ArrowLeftRight, Terminal,
  Zap, Network, ExternalLink, MessageSquare, Activity
} from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Portfolio from './pages/Portfolio'
import Analytics from './pages/Analytics'
import Swap from './pages/Swap'
import AgentTerminal from './pages/AgentTerminal'
import AskAxon from './pages/AskAxon'
import AgentActivity from './pages/AgentActivity'

const NAV_CORE = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/portfolio', icon: Wallet, label: 'Portfolio' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/swap', icon: ArrowLeftRight, label: 'Swap' },
  { to: '/agent', icon: Terminal, label: 'Agent Terminal' },
]

const NAV_AI = [
  { to: '/ask', icon: MessageSquare, label: 'Ask AXON', badge: 'NEW' },
  { to: '/activity', icon: Activity, label: 'Agent Activity', badge: 'LIVE' },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen">
        {/* ─── Sidebar ─── */}
        <aside
          style={{
            width: 240,
            flexShrink: 0,
            background: 'white',
            borderRight: '1px solid var(--border-default)',
            display: 'flex',
            flexDirection: 'column',
            position: 'sticky',
            top: 0,
            height: '100vh',
            boxShadow: '2px 0 16px rgba(91,60,245,0.04)',
          }}
        >
          {/* Logo */}
          <div style={{ padding: '24px 20px 20px', borderBottom: '1px solid var(--border-default)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 40, height: 40, borderRadius: 12,
                  background: 'linear-gradient(135deg, #5B3CF5 0%, #06C4D0 100%)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  boxShadow: '0 4px 16px rgba(91,60,245,0.35)',
                  flexShrink: 0,
                }}
              >
                <Brain size={20} color="white" />
              </div>
              <div>
                <div style={{
                  fontFamily: "'Space Grotesk', sans-serif",
                  fontWeight: 700, fontSize: 20, letterSpacing: '-0.03em',
                  color: 'var(--text-primary)', lineHeight: 1.1,
                }}>
                  AXON
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2, letterSpacing: '0.03em' }}>
                  X Layer Intelligence
                </div>
              </div>
            </div>
          </div>

          {/* Network Status */}
          <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border-default)' }}>
            <div
              style={{
                display: 'flex', alignItems: 'center', gap: 10,
                background: 'linear-gradient(135deg, rgba(16,185,129,0.08), rgba(6,196,208,0.06))',
                border: '1px solid rgba(16,185,129,0.2)',
                borderRadius: 10, padding: '8px 12px',
              }}
            >
              <span className="live-dot" />
              <div>
                <div style={{ fontSize: 12, fontWeight: 600, color: '#065F46' }}>X Layer Mainnet</div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Chain ID: 196</div>
              </div>
            </div>
          </div>

          {/* Nav — Core */}
          <nav style={{ flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: 4, overflowY: 'auto' }}>
            <div className="section-label" style={{ marginBottom: 8, paddingLeft: 4 }}>Core</div>
            {NAV_CORE.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              >
                <Icon size={16} />
                {label}
              </NavLink>
            ))}

            {/* Divider */}
            <div style={{ height: 1, background: 'var(--border-default)', margin: '10px 4px' }} />

            <div className="section-label" style={{ marginBottom: 8, paddingLeft: 4 }}>AI Features</div>
            {NAV_AI.map(({ to, icon: Icon, label, badge }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                style={({ isActive }) => isActive ? {} : {}}
              >
                <Icon size={16} />
                <span style={{ flex: 1 }}>{label}</span>
                {badge && (
                  <span style={{
                    fontSize: 9, fontWeight: 700, letterSpacing: '0.05em',
                    padding: '2px 6px', borderRadius: 99,
                    background: badge === 'NEW'
                      ? 'linear-gradient(135deg, #5B3CF5, #06C4D0)'
                      : 'linear-gradient(135deg, #10B981, #06C4D0)',
                    color: 'white',
                    boxShadow: badge === 'NEW'
                      ? '0 2px 6px rgba(91,60,245,0.4)'
                      : '0 2px 6px rgba(16,185,129,0.4)',
                  }}>
                    {badge}
                  </span>
                )}
              </NavLink>
            ))}
          </nav>

          {/* Footer */}
          <div style={{ padding: '16px', borderTop: '1px solid var(--border-default)' }}>
            {/* x402 badge */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8,
              background: 'linear-gradient(135deg, rgba(245,158,11,0.08), rgba(234,179,8,0.06))',
              border: '1px solid rgba(245,158,11,0.2)',
              borderRadius: 8, padding: '6px 10px',
            }}>
              <Zap size={11} color="#F59E0B" />
              <span style={{ fontSize: 10, fontWeight: 600, color: '#92400E' }}>x402 Premium Gate Active</span>
            </div>
            <div style={{
              background: 'linear-gradient(135deg, var(--axon-primary-light), var(--axon-accent-light))',
              borderRadius: 10, padding: '10px 12px',
            }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--axon-primary)', marginBottom: 2 }}>
                Powered by
              </div>
              <div style={{ fontSize: 10, color: 'var(--text-secondary)' }}>
                Onchain OS · Uniswap V3 · OKX DEX
              </div>
            </div>
          </div>
        </aside>

        {/* ─── Main ─── */}
        <main style={{ flex: 1, overflowX: 'hidden', minWidth: 0 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/swap" element={<Swap />} />
            <Route path="/agent" element={<AgentTerminal />} />
            <Route path="/ask" element={<AskAxon />} />
            <Route path="/activity" element={<AgentActivity />} />
          </Routes>
        </main>
      </div>

      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: 'white',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-default)',
            borderRadius: 12,
            fontSize: 13,
            boxShadow: 'var(--shadow-md)',
          },
        }}
      />
    </BrowserRouter>
  )
}
