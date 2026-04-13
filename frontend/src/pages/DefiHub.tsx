import { useState, useEffect } from 'react'
import { Wallet, TrendingUp, Image, BarChart3, Loader2, RefreshCw } from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'https://axon-onld.onrender.com'

function Card({ title, children, action }: { title: string; children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <div style={{ background: 'var(--surface-card)', borderRadius: 16, border: '1px solid var(--border-default)', padding: 24, boxShadow: 'var(--shadow-sm)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{title}</div>
        {action}
      </div>
      {children}
    </div>
  )
}

function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div style={{ padding: '12px 16px', background: 'var(--axon-primary-light)', borderRadius: 12, textAlign: 'center' }}>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)' }}>{value}</div>
      {sub && <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>{sub}</div>}
    </div>
  )
}

function fmt(n: string | number, decimals = 2) {
  const v = parseFloat(String(n))
  if (isNaN(v)) return '—'
  if (v >= 1e9) return `$${(v / 1e9).toFixed(decimals)}B`
  if (v >= 1e6) return `$${(v / 1e6).toFixed(decimals)}M`
  if (v >= 1e3) return `$${(v / 1e3).toFixed(decimals)}K`
  return `$${v.toFixed(decimals)}`
}

export default function DefiHub() {
  const [address, setAddress] = useState('')
  const [nfts, setNfts] = useState<any>(null)
  const [loadingNft, setLoadingNft] = useState(false)

  const [yields, setYields] = useState<any>(null)
  const [loadingYield, setLoadingYield] = useState(false)

  const [stats, setStats] = useState<any>(null)
  const [loadingStats, setLoadingStats] = useState(false)

  useEffect(() => { loadStats() }, [])

  async function loadNfts() {
    if (!address.trim()) return
    setLoadingNft(true); setNfts(null)
    try {
      const r = await fetch(`${API}/api/address/${address.trim()}/nft`)
      setNfts(await r.json())
    } catch { setNfts({ error: 'Request failed' }) }
    finally { setLoadingNft(false) }
  }

  async function loadYield() {
    setLoadingYield(true); setYields(null)
    try {
      const r = await fetch(`${API}/api/defi/yield-products`)
      setYields(await r.json())
    } catch { setYields({ error: 'Request failed' }) }
    finally { setLoadingYield(false) }
  }

  async function loadStats() {
    setLoadingStats(true); setStats(null)
    try {
      const r = await fetch(`${API}/api/uniswap/stats`)
      setStats(await r.json())
    } catch { setStats({ error: 'Request failed' }) }
    finally { setLoadingStats(false) }
  }

  return (
    <div style={{ padding: '32px', maxWidth: 960, margin: '0 auto' }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: 'var(--text-primary)', marginBottom: 6 }}>DeFi Hub</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>NFT portfolio, yield products, and Uniswap V3 protocol stats on X Layer.</p>
      </div>

      <div style={{ display: 'grid', gap: 20 }}>

        {/* Uniswap Protocol Stats */}
        <Card
          title="Uniswap V3 Protocol Stats"
          action={
            <button onClick={loadStats} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--axon-primary)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}>
              <RefreshCw size={12} /> Refresh
            </button>
          }
        >
          {loadingStats ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 24 }}>
              <Loader2 size={24} className="spin" color="var(--axon-primary)" />
            </div>
          ) : stats?.error ? (
            <div style={{ color: '#EF4444', fontSize: 13 }}>{stats.error}</div>
          ) : stats ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
              <Stat label="Total TVL" value={fmt(stats.total_tvl_usd)} sub="Uniswap V3 X Layer" />
              <Stat label="Total Volume" value={fmt(stats.total_volume_usd)} sub="All-time" />
              <Stat label="Total Fees" value={fmt(stats.total_fees_usd)} sub="All-time" />
              <Stat label="Pool Count" value={String(stats.pool_count ?? '—')} sub="Active pools" />
              <Stat label="TX Count" value={String(stats.tx_count ?? '—')} sub="All-time" />
              <Stat label="Protocol" value="Uniswap V3" sub="X Layer Mainnet" />
            </div>
          ) : (
            <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>Loading protocol stats...</div>
          )}
        </Card>

        {/* Yield Products */}
        <Card
          title="Yield Products on X Layer"
          action={
            <button onClick={loadYield} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--axon-primary)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}>
              {loadingYield ? <Loader2 size={12} className="spin" /> : <TrendingUp size={12} />} Load Products
            </button>
          }
        >
          {yields?.error ? (
            <div style={{ color: '#EF4444', fontSize: 13 }}>{yields.error}</div>
          ) : yields?.products?.length > 0 ? (
            <div style={{ display: 'grid', gap: 8 }}>
              {yields.products.slice(0, 8).map((p: any, i: number) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', background: 'var(--axon-primary-light)', borderRadius: 10 }}>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 700 }}>{p.name || p.protocol || 'Product'}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{p.token || p.asset || '—'}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 14, fontWeight: 800, color: '#059669' }}>{p.apy ? `${parseFloat(p.apy).toFixed(2)}%` : '—'} APY</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{p.tvl ? fmt(p.tvl) : ''} TVL</div>
                  </div>
                </div>
              ))}
            </div>
          ) : yields ? (
            <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>No yield products found for X Layer.</div>
          ) : (
            <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>Click "Load Products" to fetch available yield opportunities.</div>
          )}
        </Card>

        {/* NFT Holdings */}
        <Card title="NFT Portfolio">
          <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
            <input value={address} onChange={e => setAddress(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && loadNfts()}
              placeholder="0x wallet address"
              style={{ flex: 1, padding: '10px 14px', borderRadius: 10, border: '1.5px solid var(--border-default)', background: 'var(--surface-bg)', color: 'var(--text-primary)', fontSize: 13, fontFamily: 'monospace', outline: 'none' }}
            />
            <button onClick={loadNfts} disabled={loadingNft} style={{ padding: '10px 20px', borderRadius: 10, border: 'none', background: 'var(--axon-primary)', color: 'white', fontWeight: 700, fontSize: 13, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
              {loadingNft ? <Loader2 size={14} className="spin" /> : <><Image size={14} /> Load NFTs</>}
            </button>
          </div>
          {nfts?.error ? (
            <div style={{ color: '#EF4444', fontSize: 13 }}>{nfts.error}</div>
          ) : nfts?.nfts?.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 12 }}>
              {nfts.nfts.slice(0, 12).map((n: any, i: number) => (
                <div key={i} style={{ borderRadius: 12, border: '1px solid var(--border-default)', overflow: 'hidden', background: 'var(--surface-card)' }}>
                  {n.image_url ? (
                    <img src={n.image_url} alt={n.name} style={{ width: '100%', aspectRatio: '1', objectFit: 'cover' }} />
                  ) : (
                    <div style={{ width: '100%', aspectRatio: '1', background: 'var(--axon-primary-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Image size={32} color="var(--axon-primary)" />
                    </div>
                  )}
                  <div style={{ padding: '8px 10px' }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{n.name || `#${n.token_id}`}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{n.collection_name || '—'}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : nfts?.nft_count === 0 ? (
            <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>No NFTs found for this address on X Layer.</div>
          ) : nfts ? (
            <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>No NFT data returned.</div>
          ) : (
            <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>Enter a wallet address and click "Load NFTs".</div>
          )}
        </Card>

      </div>
    </div>
  )
}
