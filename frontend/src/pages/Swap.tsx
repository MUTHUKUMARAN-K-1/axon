import React, { useState } from 'react'
import { ArrowUpDown, Zap, Info, Loader2, ArrowRight, CheckCircle2, ExternalLink } from 'lucide-react'
import { getSwapQuote } from '../services/api'
import toast from 'react-hot-toast'

const TOKENS = [
  { symbol: 'OKB',  address: '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', decimals: 18, color: '#10B981', bg: '#D1FAE5' },
  { symbol: 'USDT', address: '0x1e4a5963abfd975d8c9021ce480b42188849d41d', decimals: 6,  color: '#059669', bg: '#ECFDF5' },
  { symbol: 'USDC', address: '0x74b7f16337b8972027f6196a17a631ac6de26d22', decimals: 6,  color: '#2563EB', bg: '#EFF6FF' },
  { symbol: 'WOKB', address: '0xe538905cf8410324e03a5a23c1c177a474d59b2', decimals: 18, color: '#7C3AED', bg: '#EDE9FE' },
]

function TokenAvatar({ symbol, color, bg }: { symbol: string; color: string; bg: string }) {
  return (
    <div style={{
      width: 36, height: 36, borderRadius: 10,
      background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 11, fontWeight: 700, color, flexShrink: 0,
    }}>
      {symbol.slice(0, 3)}
    </div>
  )
}

export default function Swap() {
  const [fromIdx, setFromIdx] = useState(0)
  const [toIdx, setToIdx] = useState(1)
  const [amount, setAmount] = useState('')
  const [quote, setQuote] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const fromToken = TOKENS[fromIdx]
  const toToken = TOKENS[toIdx]

  const flip = () => {
    setFromIdx(toIdx)
    setToIdx(fromIdx)
    setQuote(null)
  }

  const handleQuote = async () => {
    if (!amount || isNaN(parseFloat(amount))) {
      toast.error('Enter a valid amount')
      return
    }
    setLoading(true)
    setQuote(null)
    try {
      const rawAmount = String(Math.floor(parseFloat(amount) * 10 ** fromToken.decimals))
      const result = await getSwapQuote(fromToken.address, toToken.address, rawAmount)
      setQuote(result)
    } catch {
      toast.error('Quote failed — check API connection')
    } finally {
      setLoading(false)
    }
  }

  const outAmount = quote?.to_amount
    ? (parseInt(quote.to_amount) / 10 ** toToken.decimals).toFixed(6)
    : null

  const priceImpact = quote?.price_impact ? parseFloat(quote.price_impact) : 0

  return (
    <div style={{ padding: '32px', maxWidth: 560, margin: '0 auto' }}>
      {/* Header */}
      <div className="animate-fade-up" style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 30, fontWeight: 700, fontFamily: "'Space Grotesk',sans-serif", letterSpacing: '-0.03em' }}>
          Swap
        </h1>
        <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4 }}>
          Best route via OKX DEX aggregator on X Layer
        </p>
      </div>

      {/* Swap Card */}
      <div className="card animate-fade-up" style={{ animationDelay: '60ms', padding: 24 }}>
        {/* From Token */}
        <div style={{ marginBottom: 8 }}>
          <label style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 10 }}>
            You Pay
          </label>
          <div style={{
            display: 'flex', gap: 12, alignItems: 'center',
            background: 'var(--surface-bg)',
            border: '1.5px solid var(--border-default)',
            borderRadius: 14, padding: '14px 16px',
            transition: 'border-color 0.15s',
          }}>
            <TokenAvatar symbol={fromToken.symbol} color={fromToken.color} bg={fromToken.bg} />
            <select
              id="from-token-select"
              value={fromIdx}
              onChange={(e) => { setFromIdx(parseInt(e.target.value)); setQuote(null) }}
              style={{
                background: 'transparent',
                border: 'none',
                fontWeight: 700, fontSize: 16,
                color: 'var(--text-primary)',
                cursor: 'pointer', outline: 'none',
                fontFamily: "'Space Grotesk', sans-serif",
              }}
            >
              {TOKENS.map((t, i) => (
                <option key={t.symbol} value={i}>{t.symbol}</option>
              ))}
            </select>
            <input
              id="swap-amount-input"
              type="number"
              value={amount}
              onChange={(e) => { setAmount(e.target.value); setQuote(null) }}
              placeholder="0.00"
              style={{
                flex: 1, background: 'transparent', border: 'none',
                textAlign: 'right', fontSize: 22, fontWeight: 700,
                color: 'var(--text-primary)', outline: 'none',
                fontFamily: "'Space Grotesk', sans-serif",
              }}
            />
          </div>
        </div>

        {/* Flip Button */}
        <div style={{ display: 'flex', justifyContent: 'center', margin: '8px 0' }}>
          <button
            id="flip-tokens-btn"
            onClick={flip}
            style={{
              width: 40, height: 40, borderRadius: 12,
              background: 'white',
              border: '1.5px solid var(--border-default)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer', transition: 'all 0.2s',
              boxShadow: 'var(--shadow-xs)',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background = 'var(--axon-primary-light)'
              ;(e.currentTarget as HTMLElement).style.borderColor = 'var(--axon-primary)'
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background = 'white'
              ;(e.currentTarget as HTMLElement).style.borderColor = 'var(--border-default)'
            }}
          >
            <ArrowUpDown size={16} color="var(--axon-primary)" />
          </button>
        </div>

        {/* To Token */}
        <div style={{ marginBottom: 20 }}>
          <label style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 10 }}>
            You Receive
          </label>
          <div style={{
            display: 'flex', gap: 12, alignItems: 'center',
            background: 'var(--surface-bg)',
            border: '1.5px solid var(--border-default)',
            borderRadius: 14, padding: '14px 16px',
          }}>
            <TokenAvatar symbol={toToken.symbol} color={toToken.color} bg={toToken.bg} />
            <select
              id="to-token-select"
              value={toIdx}
              onChange={(e) => { setToIdx(parseInt(e.target.value)); setQuote(null) }}
              style={{
                background: 'transparent', border: 'none',
                fontWeight: 700, fontSize: 16,
                color: 'var(--text-primary)',
                cursor: 'pointer', outline: 'none',
                fontFamily: "'Space Grotesk', sans-serif",
              }}
            >
              {TOKENS.map((t, i) => (
                <option key={t.symbol} value={i}>{t.symbol}</option>
              ))}
            </select>
            <div style={{
              flex: 1, textAlign: 'right',
              fontSize: 22, fontWeight: 700,
              color: outAmount ? 'var(--text-primary)' : 'var(--text-placeholder)',
              fontFamily: "'Space Grotesk', sans-serif",
            }} className="num">
              {outAmount || '—'}
            </div>
          </div>
        </div>

        <button
          id="get-quote-btn"
          onClick={handleQuote}
          disabled={loading || !amount}
          className="btn-primary"
          style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, padding: '13px' }}
        >
          {loading ? (
            <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
          ) : (
            <Zap size={16} />
          )}
          {loading ? 'Finding Best Route...' : 'Get Quote'}
        </button>
      </div>

      {/* Quote Result */}
      {quote?.success && (
        <div
          className="card animate-fade-up"
          style={{
            marginTop: 16, padding: 0, overflow: 'hidden',
            border: '1.5px solid rgba(16,185,129,0.3)',
          }}
        >
          <div style={{
            background: 'linear-gradient(135deg, rgba(16,185,129,0.08), rgba(16,185,129,0.04))',
            padding: '16px 20px',
            borderBottom: '1px solid rgba(16,185,129,0.15)',
            display: 'flex', alignItems: 'center', gap: 8,
          }}>
            <CheckCircle2 size={16} color="#10B981" />
            <span style={{ fontSize: 14, fontWeight: 700, color: '#065F46', fontFamily: "'Space Grotesk',sans-serif" }}>
              Best Route Found
            </span>
            <span className="badge badge-success" style={{ marginLeft: 'auto' }}>OKX DEX</span>
          </div>

          <div style={{ padding: '16px 20px' }}>
            {[
              { label: 'You receive', value: `${outAmount} ${toToken.symbol}`, highlight: true },
              {
                label: 'Price impact',
                value: `${quote.price_impact}%`,
                danger: priceImpact > 3,
              },
              { label: 'Est. gas', value: `${quote.gas_estimate} OKB` },
              { label: 'Route', value: 'OKX DEX Aggregator', accent: true },
            ].map(({ label, value, highlight, danger, accent }) => (
              <div key={label} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '8px 0',
                borderBottom: '1px solid var(--border-default)',
              }}>
                <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{label}</span>
                <span style={{
                  fontSize: 13, fontWeight: 600,
                  color: danger ? '#EF4444' : accent ? 'var(--axon-primary)' : highlight ? 'var(--text-primary)' : 'var(--text-secondary)',
                }} className="num">
                  {value}
                </span>
              </div>
            ))}

            <a
              href={`https://www.okx.com/web3/dex-swap#inputChain=196&inputCurrency=${fromToken.address}&outputChain=196&outputCurrency=${toToken.address}`}
              target="_blank"
              rel="noreferrer"
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                marginTop: 16, padding: '12px',
                background: 'linear-gradient(135deg, #10B981, #34D399)',
                color: 'white', borderRadius: 12, textDecoration: 'none',
                fontSize: 14, fontWeight: 600,
                boxShadow: '0 4px 16px rgba(16,185,129,0.3)',
                transition: 'all 0.2s',
              }}
            >
              Execute on OKX DEX <ExternalLink size={14} />
            </a>
          </div>
        </div>
      )}

      {/* Info Box */}
      <div style={{
        marginTop: 16, padding: '14px 18px',
        background: 'white', border: '1px solid var(--border-default)',
        borderRadius: 12,
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
          <Info size={14} color="var(--axon-primary)" style={{ marginTop: 2, flexShrink: 0 }} />
          <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6 }}>
            <strong style={{ color: 'var(--text-secondary)' }}>Powered by Onchain OS</strong> — Routes via OKX DEX
            aggregator, finding the best price across all liquidity sources including Uniswap V3 on X Layer.
          </p>
        </div>
      </div>
    </div>
  )
}
