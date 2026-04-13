import { useState, useEffect, useCallback } from 'react'
import { BrowserRouter, Routes, Route, NavLink, useNavigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { Brain, LayoutDashboard, Wallet, BarChart3, ArrowLeftRight, Terminal,
  Zap, MessageSquare, Activity, Shield, Search, Sprout, ChevronRight, ChevronDown,
  Sun, Moon, Trophy, X as XIcon
} from 'lucide-react'
import WalletButton from './components/WalletButton'
import Dashboard from './pages/Dashboard'
import Portfolio from './pages/Portfolio'
import Analytics from './pages/Analytics'
import Swap from './pages/Swap'
import AgentTerminal from './pages/AgentTerminal'
import AskAxon from './pages/AskAxon'
import AgentActivity from './pages/AgentActivity'
import TokenScreener from './pages/TokenScreener'
import Explorer from './pages/Explorer'
import SecurityHub from './pages/SecurityHub'
import DefiHub from './pages/DefiHub'

/* ── All 43 AXON tools organised by domain ── */
const TOOL_DOMAINS = [
  {
    domain: 'Portfolio', icon: '📊', tools: [
      { name: 'get_wallet_assets', desc: 'Token balances for any address' },
      { name: 'get_net_worth', desc: 'Total portfolio net worth in USD' },
      { name: 'get_defi_positions', desc: 'Open DeFi positions' },
      { name: 'get_nft_holdings', desc: 'NFT collection holdings' },
      { name: 'get_l2_balances', desc: 'Balances across X Layer chains' },
    ],
  },
  {
    domain: 'Market', icon: '📈', tools: [
      { name: 'get_token_detail', desc: 'Price, volume, market cap' },
      { name: 'get_token_price', desc: 'Current token spot price' },
      { name: 'get_top_pools', desc: 'Uniswap V3 top liquidity pools' },
      { name: 'get_pool_ohlc', desc: 'OHLC candlestick data for pool' },
      { name: 'get_pool_fees', desc: 'Fee tier and APY for pool' },
      { name: 'get_protocol_stats', desc: 'Uniswap V3 protocol overview' },
      { name: 'get_dex_tokens', desc: 'DEX-listed token metadata' },
      { name: 'get_chain_metadata', desc: 'X Layer chain info' },
    ],
  },
  {
    domain: 'Swap & Bridge', icon: '⇄', tools: [
      { name: 'execute_swap', desc: 'OKX DEX token swap' },
      { name: 'get_swap_quote', desc: 'Quote before swap execution' },
      { name: 'cross_chain_bridge', desc: 'Bridge tokens cross-chain' },
      { name: 'get_yield_products', desc: 'Available yield/staking products' },
      { name: 'get_yield_opportunities', desc: 'Best Uniswap V3 yield' },
    ],
  },
  {
    domain: 'Security', icon: '🛡', tools: [
      { name: 'address_security_check', desc: 'OKX blacklist check for address' },
      { name: 'url_safety_scan', desc: 'Phishing URL detection' },
      { name: 'token_security_scan', desc: '5-source weighted risk score 0-100' },
      { name: 'smart_money_velocity', desc: 'Whale wallet movement tracker' },
      { name: 'arbitrage_detector', desc: 'Cross-pool arbitrage signal' },
    ],
  },
  {
    domain: 'Explorer', icon: '🔍', tools: [
      { name: 'get_address_info', desc: 'OKLink address overview' },
      { name: 'get_block_detail', desc: 'Block transactions and metadata' },
      { name: 'get_latest_blocks', desc: 'Recent block feed' },
      { name: 'get_contract_info', desc: 'Contract verification status' },
      { name: 'decode_transaction', desc: 'Human-readable TX decode' },
      { name: 'get_gas_estimate', desc: 'Current gas price estimate' },
      { name: 'get_pending_txs', desc: 'Mempool pending transactions' },
      { name: 'get_rich_list', desc: 'Top OKB holders on X Layer' },
      { name: 'get_internal_traces', desc: 'Internal transaction traces' },
      { name: 'get_token_transfers', desc: 'ERC-20 transfer history' },
    ],
  },
  {
    domain: 'Agent', icon: '🤖', tools: [
      { name: 'run_agent', desc: 'Execute autonomous AI agent loop' },
      { name: 'ask_axon', desc: 'Natural language DeFi intelligence' },
      { name: 'get_agent_activity', desc: 'Live agent execution log' },
      { name: 'get_recommendations', desc: 'AI portfolio recommendations' },
      { name: 'get_pool_by_token', desc: 'Find Uniswap pools for token' },
    ],
  },
  {
    domain: 'System', icon: '⚙', tools: [
      { name: 'health_check', desc: 'Backend connectivity status' },
      { name: 'get_mcp_tools', desc: 'List all registered MCP tools' },
      { name: 'x402_gate_status', desc: 'x402 premium gate state' },
    ],
  },
]

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
  { to: '/screener', icon: Shield, label: 'Token Screener', badge: 'HOT' },
  { to: '/explorer', icon: Search, label: 'Explorer', badge: '' },
  { to: '/security', icon: Shield, label: 'Security Hub', badge: '' },
  { to: '/defi', icon: Sprout, label: 'DeFi Hub', badge: '' },
]

const BACKEND = 'https://axon-onld.onrender.com'

/* ── Tool Drawer component ── */
function ToolDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({})
  const navigate = useNavigate()

  const toggle = (domain: string) =>
    setCollapsed(p => ({ ...p, [domain]: !p[domain] }))

  const totalTools = TOOL_DOMAINS.reduce((s, d) => s + d.tools.length, 0)

  const handleToolClick = (toolName: string) => {
    // Navigate to agent terminal and pre-fill the tool name
    navigate('/agent')
    onClose()
    // Post a custom event so AgentTerminal can pick it up
    window.dispatchEvent(new CustomEvent('axon:tool-select', { detail: toolName }))
  }

  return (
    <aside className={`tool-drawer ${open ? '' : 'closed'}`}>
      <div className="tool-drawer-header">
        <span className="tool-drawer-title">MCP Tools</span>
        <span className="tool-drawer-count">{totalTools}</span>
      </div>
      <div className="tool-drawer-body">
        {TOOL_DOMAINS.map(({ domain, icon, tools }) => {
          const isOpen = !collapsed[domain]
          return (
            <div key={domain} className="tool-domain-group">
              <button className="tool-domain-header" onClick={() => toggle(domain)}>
                <span className="tool-domain-icon">{icon}</span>
                <span className="tool-domain-label">{domain}</span>
                <span className="tool-domain-n">{tools.length}</span>
                <span className={`tool-domain-chevron ${isOpen ? 'open' : ''}`}>›</span>
              </button>
              {isOpen && (
                <div className="tool-item-list">
                  {tools.map(t => (
                    <button
                      key={t.name}
                      className="tool-item-btn"
                      onClick={() => handleToolClick(t.name)}
                    >
                      <span className="tool-item-name">{t.name}</span>
                      <span className="tool-item-desc">{t.desc}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </aside>
  )
}

/* ── Main App ── */
export default function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>(() =>
    (localStorage.getItem('axon-theme') as 'light' | 'dark') || 'dark'
  )
  const [announcementVisible, setAnnouncementVisible] = useState(() =>
    localStorage.getItem('axon-announcement-dismissed') !== '1'
  )
  const [mode, setMode] = useState<'dashboard' | 'terminal'>('dashboard')
  const [toolDrawerOpen, setToolDrawerOpen] = useState(false)
  const [mcpConnected, setMcpConnected] = useState(false)
  const [impersonateAddr, setImpersonateAddr] = useState('')
  const [impersonateInput, setImpersonateInput] = useState('')
  const [showImpersonatePopover, setShowImpersonatePopover] = useState(false)

  const isImpersonating = !!impersonateAddr

  // Apply theme
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('axon-theme', theme)
  }, [theme])

  // Check MCP connectivity
  useEffect(() => {
    fetch(`${BACKEND}/health`, { signal: AbortSignal.timeout(5000) })
      .then(r => { if (r.ok) setMcpConnected(true) })
      .catch(() => setMcpConnected(false))
  }, [])

  const handleImpersonate = useCallback(() => {
    const addr = impersonateInput.trim()
    if (/^0x[a-fA-F0-9]{40}$/.test(addr)) {
      setImpersonateAddr(addr)
      setShowImpersonatePopover(false)
    }
  }, [impersonateInput])

  const clearImpersonation = useCallback(() => {
    setImpersonateAddr('')
    setImpersonateInput('')
  }, [])

  return (
    <BrowserRouter>
      {/* ─── Hackathon Announcement Bar ─── */}
      {announcementVisible && (
        <div className="announcement-bar">
          <Trophy size={12} />
          <span>OKX Build-X 2026 Hackathon</span>
          <span className="announcement-bar-sep">·</span>
          <span>X Layer Arena + Skills Arena</span>
          <span className="announcement-bar-sep">·</span>
          <a href="https://github.com/okx/plugin-store/pull/93" target="_blank" rel="noreferrer">Plugin Store PR #93</a>
          <span className="announcement-bar-sep">·</span>
          <a href="https://axon-onld.onrender.com/llms.txt" target="_blank" rel="noreferrer">llms.txt</a>
          <span className="announcement-bar-sep">·</span>
          <a href="https://axon-onld.onrender.com/docs" target="_blank" rel="noreferrer">API Docs</a>
          <button
            className="announcement-bar-dismiss"
            onClick={() => { setAnnouncementVisible(false); localStorage.setItem('axon-announcement-dismissed', '1') }}
            aria-label="Dismiss"
          ><XIcon size={12} /></button>
        </div>
      )}

      {/* ─── Top Header Bar ─── */}
      <header className="axon-topbar">
        <div className="axon-topbar-left">
          {/* Tools sidebar toggle (terminal mode) */}
          {mode === 'terminal' && (
            <button
              className="theme-toggle-btn"
              onClick={() => setToolDrawerOpen(o => !o)}
              title="Toggle tool drawer"
              style={{ fontSize: 16 }}
            >
              {toolDrawerOpen ? <ChevronRight size={15} /> : <ChevronDown size={15} />}
            </button>
          )}

          {/* Logo (compact) */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{
              width: 24, height: 24, borderRadius: 6,
              background: 'linear-gradient(135deg, #5B3CF5 0%, #06C4D0 100%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}>
              <Brain size={13} color="white" />
            </div>
            <span style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontWeight: 700, fontSize: 15, letterSpacing: '-0.02em',
              color: 'var(--text-primary)',
            }}>AXON</span>
            <span style={{ fontSize: 10, color: 'var(--text-muted)', display: 'none' }}>X Layer</span>
          </div>

          {/* Dashboard / Terminal mode toggle */}
          <div className="mode-toggle">
            <button
              className={`mode-btn ${mode === 'dashboard' ? 'active' : ''}`}
              onClick={() => setMode('dashboard')}
            >Dashboard</button>
            <button
              className={`mode-btn ${mode === 'terminal' ? 'active' : ''}`}
              onClick={() => { setMode('terminal'); setToolDrawerOpen(true) }}
            >Terminal</button>
          </div>

          {/* MCP Status */}
          <div className="mcp-status-badge">
            <span className={`mcp-dot ${mcpConnected ? 'connected' : ''}`} />
            <span>MCP {mcpConnected ? 'LIVE' : 'OFF'}</span>
          </div>

          {/* Network */}
          <div className="mcp-status-badge" style={{ cursor: 'default' }}>
            <span className="live-dot" style={{ width: 6, height: 6 }} />
            <span>X Layer · 196</span>
          </div>
        </div>

        <div className="axon-topbar-right">
          {/* Theme toggle */}
          <button
            className="theme-toggle-btn"
            onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
          </button>

          {/* Impersonate */}
          <div className="impersonate-wrapper">
            <button
              className={`theme-toggle-btn ${isImpersonating ? 'active' : ''}`}
              onClick={() => setShowImpersonatePopover(p => !p)}
              title="View any X Layer address"
              style={isImpersonating ? { borderColor: '#F59E0B' } : {}}
            ><Search size={14} /></button>
            {showImpersonatePopover && (
              <>
                <div
                  style={{ position: 'fixed', inset: 0, zIndex: 199 }}
                  onClick={() => setShowImpersonatePopover(false)}
                />
                <div className="impersonate-popover">
                  <div className="impersonate-popover-title" style={{ display: 'flex', alignItems: 'center', gap: 6 }}><Search size={13} /> View Any Address</div>
                  <div className="impersonate-popover-desc">
                    Inspect any X Layer wallet's portfolio, DeFi positions, and security score without connecting.
                  </div>
                  <input
                    className="impersonate-popover-input"
                    type="text"
                    placeholder="0x..."
                    value={impersonateInput}
                    onChange={e => setImpersonateInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleImpersonate()}
                    autoFocus
                  />
                  <button
                    className="impersonate-popover-btn"
                    onClick={handleImpersonate}
                    disabled={!/^0x[a-fA-F0-9]{40}$/.test(impersonateInput.trim())}
                  >
                    Inspect Address →
                  </button>
                </div>
              </>
            )}
          </div>

          {/* x402 badge */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 5,
            border: '1px solid rgba(245,158,11,0.3)',
            borderRadius: 99, padding: '3px 10px',
          }}>
            <Zap size={10} color="#F59E0B" />
            <span style={{ fontSize: 10, fontWeight: 600, color: '#F59E0B' }}>x402</span>
          </div>

          {/* Wallet */}
          <WalletButton />
        </div>
      </header>

      {/* Impersonation banner */}
      {isImpersonating && (
        <div className="impersonate-banner">
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}><Search size={12} /> Viewing <strong>{impersonateAddr.slice(0, 6)}…{impersonateAddr.slice(-4)}</strong> on X Layer</span>
          <button className="impersonate-exit" onClick={clearImpersonation}>✕ Exit</button>
        </div>
      )}

      {/* ─── Body: sidebar + main ─── */}
      <div style={{ display: 'flex', height: 'calc(100vh - 48px)', overflow: 'hidden' }}>

        {/* ─── Left Nav Sidebar ─── */}
        <aside
          style={{
            width: 220,
            flexShrink: 0,
            background: 'var(--surface-card)',
            borderRight: '1px solid var(--border-default)',
            display: 'flex',
            flexDirection: 'column',
            overflowY: 'auto',
            boxShadow: '2px 0 16px rgba(91,60,245,0.04)',
          }}
        >
          {/* Logo section */}
          <div style={{ padding: '18px 16px 14px', borderBottom: '1px solid var(--border-default)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{
                width: 38, height: 38, borderRadius: 11,
                background: 'linear-gradient(135deg, #5B3CF5 0%, #06C4D0 100%)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 4px 14px rgba(91,60,245,0.35)',
                flexShrink: 0,
              }}>
                <Brain size={19} color="white" />
              </div>
              <div>
                <div style={{
                  fontFamily: "'Space Grotesk', sans-serif",
                  fontWeight: 700, fontSize: 18, letterSpacing: '-0.03em',
                  color: 'var(--text-primary)', lineHeight: 1.1,
                }}>AXON</div>
                <div style={{ fontSize: 9, color: 'var(--text-muted)', marginTop: 2, letterSpacing: '0.03em' }}>
                  X Layer Intelligence
                </div>
              </div>
            </div>
          </div>

          {/* Network status */}
          <div style={{ padding: '10px 12px', borderBottom: '1px solid var(--border-default)' }}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 8,
              background: 'linear-gradient(135deg, rgba(16,185,129,0.08), rgba(6,196,208,0.06))',
              border: '1px solid rgba(16,185,129,0.2)',
              borderRadius: 8, padding: '7px 10px',
            }}>
              <span className="live-dot" />
              <div>
                <div style={{ fontSize: 11, fontWeight: 600, color: '#065F46' }}>X Layer Mainnet</div>
                <div style={{ fontSize: 9, color: 'var(--text-muted)' }}>Chain ID: 196</div>
              </div>
            </div>
          </div>

          {/* Nav */}
          <nav style={{ flex: 1, padding: '12px 10px', display: 'flex', flexDirection: 'column', gap: 3, overflowY: 'auto' }}>
            <div className="section-label" style={{ marginBottom: 6, paddingLeft: 4 }}>Core</div>
            {NAV_CORE.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              >
                <Icon size={15} />
                {label}
              </NavLink>
            ))}

            <div style={{ height: 1, background: 'var(--border-default)', margin: '8px 4px' }} />

            <div className="section-label" style={{ marginBottom: 6, paddingLeft: 4 }}>AI Features</div>
            {NAV_AI.map(({ to, icon: Icon, label, badge }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              >
                <Icon size={15} />
                <span style={{ flex: 1 }}>{label}</span>
                {badge && (
                  <span style={{
                    fontSize: 9, fontWeight: 700, letterSpacing: '0.05em',
                    padding: '2px 5px', borderRadius: 99,
                    background: badge === 'NEW'
                      ? 'linear-gradient(135deg, #5B3CF5, #06C4D0)'
                      : badge === 'HOT'
                      ? 'linear-gradient(135deg, #EF4444, #F59E0B)'
                      : 'linear-gradient(135deg, #10B981, #06C4D0)',
                    color: 'white',
                  }}>{badge}</span>
                )}
              </NavLink>
            ))}
          </nav>

          {/* Footer */}
          <div style={{ padding: '12px 14px', borderTop: '1px solid var(--border-default)' }}>
            <div style={{ marginBottom: 8 }}>
              <WalletButton />
            </div>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6,
              background: 'linear-gradient(135deg, rgba(245,158,11,0.08), rgba(234,179,8,0.06))',
              border: '1px solid rgba(245,158,11,0.2)',
              borderRadius: 7, padding: '5px 9px',
            }}>
              <Zap size={10} color="#F59E0B" />
              <span style={{ fontSize: 10, fontWeight: 600, color: '#92400E' }}>x402 Premium Gate Active</span>
            </div>
            <div style={{
              background: 'linear-gradient(135deg, var(--axon-primary-light), var(--axon-accent-light))',
              borderRadius: 8, padding: '8px 10px',
            }}>
              <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--axon-primary)', marginBottom: 1 }}>Powered by</div>
              <div style={{ fontSize: 9, color: 'var(--text-secondary)' }}>Onchain OS · Uniswap V3 · OKX DEX</div>
            </div>
          </div>
        </aside>

        {/* ─── Tool Drawer (terminal mode) ─── */}
        <ToolDrawer open={mode === 'terminal' && toolDrawerOpen} onClose={() => setToolDrawerOpen(false)} />

        {/* ─── Main Content ─── */}
        <main style={{ flex: 1, overflowX: 'hidden', overflowY: 'auto', minWidth: 0 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/portfolio" element={<Portfolio impersonateAddr={impersonateAddr} />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/swap" element={<Swap />} />
            <Route path="/agent" element={<AgentTerminal />} />
            <Route path="/ask" element={<AskAxon />} />
            <Route path="/activity" element={<AgentActivity />} />
            <Route path="/screener" element={<TokenScreener />} />
            <Route path="/explorer" element={<Explorer />} />
            <Route path="/security" element={<SecurityHub />} />
            <Route path="/defi" element={<DefiHub />} />
          </Routes>
        </main>
      </div>

      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: 'var(--surface-card)',
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
