import { useState } from 'react'
import { Search, Blocks, FileCode, Clock, ArrowUpRight, Loader2 } from 'lucide-react'

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

export default function Explorer() {
  const [tab, setTab] = useState<'address' | 'block' | 'tx' | 'contract'>('address')
  const [input, setInput] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [blocks, setBlocks] = useState<any[]>([])
  const [blocksLoaded, setBlocksLoaded] = useState(false)

  const endpointMap = {
    address: `${API}/api/address/${input}/info`,
    tx: `${API}/api/tx/${input}`,
    contract: `${API}/api/contract/${input}/info`,
    block: `${API}/api/block/${input}`,
  }

  async function search() {
    if (!input.trim()) return
    setLoading(true); setResult(null)
    try {
      const r = await fetch(endpointMap[tab])
      setResult(await r.json())
    } catch { setResult({ error: 'Request failed' }) }
    finally { setLoading(false) }
  }

  async function loadBlocks() {
    setBlocksLoaded(false)
    try {
      const r = await fetch(`${API}/api/blocks/latest`)
      const d = await r.json()
      setBlocks(d.blocks || [])
    } catch {}
    setBlocksLoaded(true)
  }

  const tabs = [
    { key: 'address', label: 'Address', icon: Search, placeholder: '0x...' },
    { key: 'block', label: 'Block', icon: Blocks, placeholder: 'Block number' },
    { key: 'tx', label: 'Transaction', icon: ArrowUpRight, placeholder: '0x tx hash' },
    { key: 'contract', label: 'Contract', icon: FileCode, placeholder: '0x contract address' },
  ] as const

  return (
    <div style={{ padding: '32px 32px 32px', maxWidth: 960, margin: '0 auto' }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: 'var(--text-primary)', marginBottom: 6 }}>X Layer Explorer</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>Powered by OKLink — search addresses, blocks, transactions, and contracts on X Layer.</p>
      </div>

      {/* Tab bar */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {tabs.map(({ key, label, icon: Icon }) => (
          <button key={key} onClick={() => { setTab(key); setResult(null) }} style={{
            display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px', borderRadius: 99, border: 'none', cursor: 'pointer', fontSize: 13, fontWeight: 600,
            background: tab === key ? 'var(--axon-primary)' : 'var(--surface-card)',
            color: tab === key ? 'white' : 'var(--text-secondary)',
            boxShadow: tab === key ? '0 2px 8px rgba(91,60,245,0.3)' : '0 1px 4px rgba(0,0,0,0.08)',
            border: tab === key ? 'none' : '1px solid var(--border-default)',
          }}>
            <Icon size={13} />{label}
          </button>
        ))}
      </div>

      {/* Search bar */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 28 }}>
        <input value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && search()}
          placeholder={tabs.find(t => t.key === tab)?.placeholder}
          style={{ flex: 1, padding: '12px 16px', borderRadius: 12, border: '1.5px solid var(--border-default)', background: 'var(--surface-bg)', color: 'var(--text-primary)', fontSize: 14, fontFamily: 'monospace', outline: 'none' }}
        />
        <button onClick={search} disabled={loading} style={{
          padding: '12px 24px', borderRadius: 12, border: 'none', background: 'var(--axon-primary)', color: 'white', fontWeight: 700, fontSize: 14, cursor: 'pointer',
        }}>
          {loading ? <Loader2 size={16} className="spin" /> : 'Search'}
        </button>
      </div>

      {/* Result */}
      {result && (
        <Card title="Result">
          {result.error ? (
            <div style={{ color: '#EF4444', fontSize: 13 }}>{result.error}</div>
          ) : tab === 'address' ? (
            <>
              <Row label="Address" value={result.address || input} mono />
              <Row label="OKB Balance" value={result.balance_okb || '0'} />
              <Row label="Transactions" value={result.tx_count || 0} />
              <Row label="Token Count" value={result.token_count || 0} />
              <Row label="Is Contract" value={result.is_contract ? 'Yes' : 'No'} />
              {result.contract_name && <Row label="Contract Name" value={result.contract_name} />}
              {result.entity_tag && <Row label="Entity Tag" value={result.entity_tag} />}
              <Row label="First TX" value={result.first_tx_time || '—'} />
              <Row label="Last TX" value={result.last_tx_time || '—'} />
            </>
          ) : tab === 'tx' ? (
            <>
              <Row label="Hash" value={result.tx_hash || input} mono />
              <Row label="Status" value={result.status === '1' || result.status === 1 ? '✅ Success' : result.status || '—'} />
              <Row label="Block" value={result.block || '—'} />
              <Row label="From" value={result.from || '—'} mono />
              <Row label="To" value={result.to || '—'} mono />
              <Row label="Value" value={`${result.value || '0'} ${result.symbol || 'OKB'}`} />
              <Row label="Gas Fee" value={result.gas_fee || '0'} />
              <Row label="Type" value={result.type || '—'} />
            </>
          ) : tab === 'contract' ? (
            <>
              <Row label="Address" value={result.address || input} mono />
              <Row label="Verified" value={result.is_verified ? '✅ Yes' : '❌ No'} />
              <Row label="Name" value={result.contract_name || '—'} />
              <Row label="Compiler" value={result.compiler_version || '—'} />
              <Row label="Creator" value={result.creator || '—'} mono />
              <Row label="Deploy TX" value={result.deploy_tx || '—'} mono />
              <Row label="Deploy Time" value={result.deploy_time || '—'} />
              <Row label="License" value={result.license || '—'} />
            </>
          ) : (
            <>
              <Row label="Block" value={result.number || '—'} />
              <Row label="Timestamp" value={result.timestamp || '—'} />
              <Row label="Transactions" value={result.tx_count || 0} />
              <Row label="Gas Used" value={result.gas_used || '—'} />
              <Row label="Gas Limit" value={result.gas_limit || '—'} />
              <Row label="Utilization" value={`${result.gas_utilization_pct || 0}%`} />
              <Row label="Validator" value={result.validator || '—'} mono />
              <Row label="Base Fee" value={result.base_fee || '—'} />
            </>
          )}
        </Card>
      )}

      {/* Recent Blocks */}
      <div style={{ marginTop: 28 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Clock size={16} color="var(--axon-primary)" /> Recent Blocks
          </h2>
          <button onClick={loadBlocks} style={{ fontSize: 12, color: 'var(--axon-primary)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600 }}>
            Load Latest
          </button>
        </div>
        {blocks.length > 0 ? (
          <div style={{ display: 'grid', gap: 8 }}>
            {blocks.slice(0, 8).map((b: any, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: 'var(--surface-card)', borderRadius: 10, border: '1px solid var(--border-default)', boxShadow: 'var(--shadow-sm)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ width: 36, height: 36, borderRadius: 8, background: 'var(--axon-primary-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Blocks size={16} color="var(--axon-primary)" />
                  </div>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 700 }}>#{b.number}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{b.tx_count} txs</div>
                  </div>
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{b.timestamp}</div>
              </div>
            ))}
          </div>
        ) : blocksLoaded ? (
          <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>No blocks loaded.</div>
        ) : (
          <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>Click "Load Latest" to fetch recent blocks.</div>
        )}
      </div>
    </div>
  )
}
