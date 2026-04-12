/**
 * WalletButton — MetaMask connect/disconnect button for AXON sidebar.
 * Shows: Connect | Connecting... | 0xABC...DEF (connected) | Wrong Network warning.
 */
import { Wallet, AlertTriangle, Loader2, Unplug } from 'lucide-react'
import { useWallet } from '../hooks/useWallet'

function short(addr: string) {
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`
}

export default function WalletButton() {
  const { address, isXLayer, connecting, error, isAvailable, connect, disconnect, switchToXLayer } = useWallet()

  // Not connected
  if (!address) {
    return (
      <div>
        <button
          id="wallet-connect-btn"
          onClick={connect}
          disabled={connecting}
          style={{
            width: '100%',
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '9px 12px',
            background: connecting
              ? 'var(--surface-bg)'
              : 'linear-gradient(135deg, #5B3CF5 0%, #06C4D0 100%)',
            color: connecting ? 'var(--text-muted)' : 'white',
            border: connecting ? '1px solid var(--border-default)' : 'none',
            borderRadius: 10, cursor: connecting ? 'not-allowed' : 'pointer',
            fontSize: 12, fontWeight: 600,
            boxShadow: connecting ? 'none' : '0 4px 14px rgba(91,60,245,0.35)',
            transition: 'all 0.2s',
          }}
        >
          {connecting ? (
            <Loader2 size={13} style={{ animation: 'spin 1s linear infinite', flexShrink: 0 }} />
          ) : (
            <Wallet size={13} style={{ flexShrink: 0 }} />
          )}
          {connecting ? 'Connecting...' : isAvailable ? 'Connect Wallet' : 'Install MetaMask'}
        </button>
        {error && (
          <div style={{ fontSize: 10, color: '#EF4444', marginTop: 4, lineHeight: 1.4 }}>
            {error}
          </div>
        )}
      </div>
    )
  }

  // Connected but wrong network
  if (!isXLayer) {
    return (
      <button
        id="wallet-switch-network-btn"
        onClick={switchToXLayer}
        style={{
          width: '100%',
          display: 'flex', alignItems: 'center', gap: 8,
          padding: '9px 12px',
          background: 'linear-gradient(135deg, rgba(245,158,11,0.1), rgba(234,179,8,0.08))',
          border: '1px solid rgba(245,158,11,0.4)',
          borderRadius: 10, cursor: 'pointer',
          fontSize: 12, fontWeight: 600, color: '#92400E',
          transition: 'all 0.2s',
        }}
      >
        <AlertTriangle size={13} color="#F59E0B" style={{ flexShrink: 0 }} />
        Switch to X Layer
      </button>
    )
  }

  // Connected on X Layer
  return (
    <div
      style={{
        background: 'linear-gradient(135deg, rgba(16,185,129,0.08), rgba(6,196,208,0.06))',
        border: '1px solid rgba(16,185,129,0.25)',
        borderRadius: 10, padding: '8px 12px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <span className="live-dot" />
        <span style={{ fontSize: 11, fontWeight: 700, color: '#065F46', flex: 1 }}>
          {short(address)}
        </span>
        <button
          id="wallet-disconnect-btn"
          onClick={disconnect}
          title="Disconnect"
          style={{
            background: 'none', border: 'none', cursor: 'pointer', padding: 2,
            color: 'var(--text-muted)', display: 'flex',
          }}
        >
          <Unplug size={12} />
        </button>
      </div>
      <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>X Layer Mainnet · OKB</div>
    </div>
  )
}
