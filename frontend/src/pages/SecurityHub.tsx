import { useState } from 'react'
import { Shield, Search, AlertTriangle, CheckCircle, XCircle, Link, Loader2 } from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'https://axon-onld.onrender.com'

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ background: 'var(--surface-card)', borderRadius: 16, border: '1px solid var(--border-default)', padding: 24, boxShadow: 'var(--shadow-sm)' }}>
      <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 16 }}>{title}</div>
      {children}
    </div>
  )
}

function Row({ label, value, mono = false }: { label: string; value: string | number; mono?: boolean }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border-default)', gap: 12 }}>
      <span style={{ fontSize: 12, color: 'var(--text-muted)', flexShrink: 0 }}>{label}</span>
      <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', fontFamily: mono ? 'monospace' : undefined, wordBreak: 'break-all', textAlign: 'right' }}>{value}</span>
    </div>
  )
}

function RiskBadge({ level }: { level: string }) {
  const colors: Record<string, { bg: string; color: string }> = {
    safe: { bg: '#D1FAE5', color: '#065F46' },
    low: { bg: '#D1FAE5', color: '#065F46' },
    medium: { bg: '#FEF3C7', color: '#92400E' },
    high: { bg: '#FEE2E2', color: '#991B1B' },
    critical: { bg: '#FEE2E2', color: '#7F1D1D' },
    unknown: { bg: '#F3F4F6', color: '#6B7280' },
  }
  const c = colors[level?.toLowerCase()] || colors.unknown
  return (
    <span style={{ padding: '3px 10px', borderRadius: 99, fontSize: 11, fontWeight: 700, background: c.bg, color: c.color }}>
      {level?.toUpperCase() || 'UNKNOWN'}
    </span>
  )
}

export default function SecurityHub() {
  const [addressInput, setAddressInput] = useState('')
  const [urlInput, setUrlInput] = useState('')
  const [tokenInput, setTokenInput] = useState('')
  const [addressResult, setAddressResult] = useState<any>(null)
  const [urlResult, setUrlResult] = useState<any>(null)
  const [tokenResult, setTokenResult] = useState<any>(null)
  const [loadingAddr, setLoadingAddr] = useState(false)
  const [loadingUrl, setLoadingUrl] = useState(false)
  const [loadingToken, setLoadingToken] = useState(false)

  async function checkAddress() {
    if (!addressInput.trim()) return
    setLoadingAddr(true); setAddressResult(null)
    try {
      const r = await fetch(`${API}/api/address/${addressInput.trim()}/security-check`)
      setAddressResult(await r.json())
    } catch { setAddressResult({ error: 'Request failed' }) }
    finally { setLoadingAddr(false) }
  }

  async function checkUrl() {
    if (!urlInput.trim()) return
    setLoadingUrl(true); setUrlResult(null)
    try {
      const r = await fetch(`${API}/api/url/safety`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: urlInput.trim() }),
      })
      setUrlResult(await r.json())
    } catch { setUrlResult({ error: 'Request failed' }) }
    finally { setLoadingUrl(false) }
  }

  async function checkToken() {
    if (!tokenInput.trim()) return
    setLoadingToken(true); setTokenResult(null)
    try {
      const r = await fetch(`${API}/api/token/${tokenInput.trim()}/security`)
      setTokenResult(await r.json())
    } catch { setTokenResult({ error: 'Request failed' }) }
    finally { setLoadingToken(false) }
  }

  return (
    <div style={{ padding: '32px', maxWidth: 960, margin: '0 auto' }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: 'var(--text-primary)', marginBottom: 6 }}>Security Hub</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>Powered by OKX Onchain OS — check addresses, URLs, and tokens for risk on X Layer.</p>
      </div>

      <div style={{ display: 'grid', gap: 20 }}>

        {/* Address Security */}
        <Card title="Address Risk Check">
          <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
            <input value={addressInput} onChange={e => setAddressInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && checkAddress()}
              placeholder="0x wallet or contract address"
              style={{ flex: 1, padding: '10px 14px', borderRadius: 10, border: '1.5px solid var(--border-default)', background: 'var(--surface-bg)', color: 'var(--text-primary)', fontSize: 13, fontFamily: 'monospace', outline: 'none' }}
            />
            <button onClick={checkAddress} disabled={loadingAddr} style={{ padding: '10px 20px', borderRadius: 10, border: 'none', background: 'var(--axon-primary)', color: 'white', fontWeight: 700, fontSize: 13, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
              {loadingAddr ? <Loader2 size={14} className="spin" /> : <><Shield size={14} /> Check</>}
            </button>
          </div>
          {addressResult && (
            addressResult.error ? (
              <div style={{ color: '#EF4444', fontSize: 13 }}>{addressResult.error}</div>
            ) : (
              <>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12, padding: '10px 14px', borderRadius: 10, background: addressResult.is_blacklisted ? '#FEE2E2' : '#D1FAE5' }}>
                  {addressResult.is_blacklisted
                    ? <XCircle size={18} color="#EF4444" />
                    : <CheckCircle size={18} color="#10B981" />}
                  <span style={{ fontWeight: 700, fontSize: 14, color: addressResult.is_blacklisted ? '#991B1B' : '#065F46' }}>
                    {addressResult.is_blacklisted ? 'BLACKLISTED ADDRESS' : 'Address looks clean'}
                  </span>
                </div>
                <Row label="Risk Level" value={addressResult.risk_level || '—'} />
                <Row label="Address Type" value={addressResult.address_type || '—'} />
                <Row label="Is Contract" value={addressResult.is_contract ? 'Yes' : 'No'} />
                {addressResult.labels?.length > 0 && <Row label="Labels" value={addressResult.labels.join(', ')} />}
                {addressResult.related_addresses?.length > 0 && <Row label="Related Addresses" value={addressResult.related_addresses.length} />}
              </>
            )
          )}
        </Card>

        {/* URL Safety */}
        <Card title="URL Phishing Check">
          <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
            <input value={urlInput} onChange={e => setUrlInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && checkUrl()}
              placeholder="https://..."
              style={{ flex: 1, padding: '10px 14px', borderRadius: 10, border: '1.5px solid var(--border-default)', background: 'var(--surface-bg)', color: 'var(--text-primary)', fontSize: 13, outline: 'none' }}
            />
            <button onClick={checkUrl} disabled={loadingUrl} style={{ padding: '10px 20px', borderRadius: 10, border: 'none', background: 'var(--axon-primary)', color: 'white', fontWeight: 700, fontSize: 13, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
              {loadingUrl ? <Loader2 size={14} className="spin" /> : <><Link size={14} /> Scan</>}
            </button>
          </div>
          {urlResult && (
            urlResult.error ? (
              <div style={{ color: '#EF4444', fontSize: 13 }}>{urlResult.error}</div>
            ) : (
              <>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12, padding: '10px 14px', borderRadius: 10, background: urlResult.is_malicious ? '#FEE2E2' : '#D1FAE5' }}>
                  {urlResult.is_malicious
                    ? <AlertTriangle size={18} color="#EF4444" />
                    : <CheckCircle size={18} color="#10B981" />}
                  <span style={{ fontWeight: 700, fontSize: 14, color: urlResult.is_malicious ? '#991B1B' : '#065F46' }}>
                    {urlResult.is_malicious ? 'MALICIOUS / PHISHING URL' : 'URL appears safe'}
                  </span>
                </div>
                <Row label="Risk Level" value={urlResult.risk_level || '—'} />
                <Row label="Category" value={urlResult.category || '—'} />
                {urlResult.description && <Row label="Detail" value={urlResult.description} />}
              </>
            )
          )}
        </Card>

        {/* Token Security Scan */}
        <Card title="Token Security Scan">
          <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
            <input value={tokenInput} onChange={e => setTokenInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && checkToken()}
              placeholder="0x token contract address"
              style={{ flex: 1, padding: '10px 14px', borderRadius: 10, border: '1.5px solid var(--border-default)', background: 'var(--surface-bg)', color: 'var(--text-primary)', fontSize: 13, fontFamily: 'monospace', outline: 'none' }}
            />
            <button onClick={checkToken} disabled={loadingToken} style={{ padding: '10px 20px', borderRadius: 10, border: 'none', background: 'var(--axon-primary)', color: 'white', fontWeight: 700, fontSize: 13, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
              {loadingToken ? <Loader2 size={14} className="spin" /> : <><AlertTriangle size={14} /> Scan</>}
            </button>
          </div>
          {tokenResult && (
            tokenResult.error ? (
              <div style={{ color: '#EF4444', fontSize: 13 }}>{tokenResult.error}</div>
            ) : (
              <>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                  <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{tokenResult.token_name || tokenResult.token_address || tokenInput}</span>
                  <RiskBadge level={tokenResult.risk_level || 'unknown'} />
                </div>
                <Row label="Risk Score" value={`${tokenResult.risk_score ?? '—'} / 100`} />
                <Row label="Honeypot" value={tokenResult.is_honeypot ? '⚠️ YES' : '✅ No'} />
                <Row label="Contract Verified" value={tokenResult.contract_verified ? '✅ Yes' : '❌ No'} />
                <Row label="Holders" value={tokenResult.holder_count ?? '—'} />
                <Row label="Top 10 Concentration" value={tokenResult.top10_holder_pct ? `${tokenResult.top10_holder_pct}%` : '—'} />
                <Row label="Liquidity Locked" value={tokenResult.liquidity_locked ? '✅ Yes' : '❌ No / Unknown'} />
                {tokenResult.risk_flags?.length > 0 && (
                  <div style={{ marginTop: 12 }}>
                    <div style={{ fontSize: 12, fontWeight: 600, color: '#EF4444', marginBottom: 6 }}>Risk Flags</div>
                    {tokenResult.risk_flags.map((f: string, i: number) => (
                      <div key={i} style={{ fontSize: 12, color: '#B91C1C', padding: '4px 0', display: 'flex', gap: 6, alignItems: 'flex-start' }}>
                        <AlertTriangle size={11} style={{ marginTop: 1, flexShrink: 0 }} />
                        {f}
                      </div>
                    ))}
                  </div>
                )}
              </>
            )
          )}
        </Card>

      </div>
    </div>
  )
}
