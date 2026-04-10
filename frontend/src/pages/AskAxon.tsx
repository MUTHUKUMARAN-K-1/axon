import React, { useState, useRef, useEffect } from 'react'
import {
  Brain, Send, Loader2, Zap, TrendingUp, Wallet,
  BarChart3, ArrowLeftRight, Sparkles, ChevronRight,
  MessageSquare, Bot, User, Lock, ExternalLink, Copy, CheckCheck
} from 'lucide-react'

const API = import.meta.env.VITE_AXON_API_URL || 'https://axon-onld.onrender.com'

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  tool?: string
  loading?: boolean
  timestamp: Date
  payment402?: {
    payment_address: string
    amount_okb: string
    tool_name: string
    rejection_reason?: string
  }
}

const SUGGESTIONS = [
  { icon: Zap, text: "What's the gas price right now?", color: '#F59E0B' },
  { icon: TrendingUp, text: "Find the best yield opportunities on X Layer", color: '#10B981' },
  { icon: BarChart3, text: "Show me the top Uniswap V3 pools", color: '#5B3CF5' },
  { icon: Wallet, text: "What's the latest block on X Layer?", color: '#06C4D0' },
  { icon: ArrowLeftRight, text: "Give me the current X Layer market overview", color: '#EC4899' },
  { icon: Brain, text: "Analyze wallet 0xDb82c0d91E057E05600C8F8dc836bEb41da6df14", color: '#8B5CF6' },
]

function ToolBadge({ tool }: { tool: string }) {
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      background: 'linear-gradient(135deg, rgba(91,60,245,0.08), rgba(6,196,208,0.08))',
      border: '1px solid rgba(91,60,245,0.15)',
      borderRadius: 6, padding: '2px 8px',
      fontSize: 11, fontWeight: 600, color: 'var(--axon-primary)',
      fontFamily: "'JetBrains Mono', monospace",
      marginBottom: 8,
    }}>
      <Sparkles size={10} />
      {tool}
    </span>
  )
}

function PaymentCard({ p }: { p: NonNullable<Message['payment402']> }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(p.payment_address)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <div style={{
      marginTop: 10,
      background: 'linear-gradient(135deg, rgba(245,158,11,0.06), rgba(234,179,8,0.04))',
      border: '1.5px solid rgba(245,158,11,0.3)',
      borderRadius: 12, padding: '14px 16px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <Lock size={14} color="#D97706" />
        <span style={{ fontSize: 13, fontWeight: 700, color: '#92400E' }}>
          Premium Tool — OKB Payment Required
        </span>
      </div>
      {p.rejection_reason && (
        <div style={{ fontSize: 12, color: '#B45309', marginBottom: 8, fontStyle: 'italic' }}>
          ↳ {p.rejection_reason}
        </div>
      )}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 10 }}>
        <div style={{ background: 'white', borderRadius: 8, padding: '8px 10px', border: '1px solid rgba(245,158,11,0.2)' }}>
          <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 3 }}>Tool</div>
          <div style={{ fontSize: 12, fontFamily: "'JetBrains Mono', monospace", color: 'var(--text-primary)' }}>{p.tool_name}</div>
        </div>
        <div style={{ background: 'white', borderRadius: 8, padding: '8px 10px', border: '1px solid rgba(245,158,11,0.2)' }}>
          <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 3 }}>Amount</div>
          <div style={{ fontSize: 12, fontWeight: 700, color: '#D97706' }}>{p.amount_okb} OKB</div>
        </div>
      </div>
      <div style={{ background: 'white', borderRadius: 8, padding: '8px 10px', border: '1px solid rgba(245,158,11,0.2)', marginBottom: 10 }}>
        <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 3 }}>Pay to (X Layer)</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div style={{ fontSize: 11, fontFamily: "'JetBrains Mono', monospace", color: 'var(--text-primary)', flex: 1, wordBreak: 'break-all' }}>{p.payment_address}</div>
          <button onClick={copy} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: '#D97706', flexShrink: 0 }}>
            {copied ? <CheckCheck size={14} color="#10B981" /> : <Copy size={14} />}
          </button>
        </div>
      </div>
      <div style={{ fontSize: 11, color: '#92400E', lineHeight: 1.6 }}>
        <b>How to pay:</b> Send {p.amount_okb} OKB to the address above on X Layer (Chain 196).
        Copy the tx hash, include it as <code style={{ background: 'rgba(245,158,11,0.1)', padding: '1px 4px', borderRadius: 3 }}>X-PAYMENT: 0xYourTxHash</code> header, then retry.
        Use <a href={`${API}/api/x402/verify`} target="_blank" rel="noreferrer" style={{ color: '#D97706' }}>POST /api/x402/verify <ExternalLink size={10} style={{display:'inline'}} /></a> to pre-check.
      </div>
    </div>
  )
}

function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === 'user'
  return (
    <div style={{
      display: 'flex', gap: 12,
      flexDirection: isUser ? 'row-reverse' : 'row',
      alignItems: 'flex-start',
      animation: 'fadeSlideUp 0.3s ease',
    }}>
      {/* Avatar */}
      <div style={{
        width: 36, height: 36, borderRadius: 10, flexShrink: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: isUser
          ? 'linear-gradient(135deg, #5B3CF5, #8B5CF6)'
          : 'linear-gradient(135deg, #06C4D0, #5B3CF5)',
        boxShadow: '0 4px 12px rgba(91,60,245,0.25)',
      }}>
        {isUser ? <User size={16} color="white" /> : <Bot size={16} color="white" />}
      </div>

      {/* Bubble */}
      <div style={{ maxWidth: '75%' }}>
        {msg.tool && !isUser && <ToolBadge tool={msg.tool} />}
        <div style={{
          background: isUser
            ? 'linear-gradient(135deg, #5B3CF5, #7C3AED)'
            : 'white',
          color: isUser ? 'white' : 'var(--text-primary)',
          border: isUser ? 'none' : '1px solid var(--border-default)',
          borderRadius: isUser ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
          padding: '12px 16px',
          fontSize: 14,
          lineHeight: 1.7,
          boxShadow: isUser
            ? '0 4px 16px rgba(91,60,245,0.3)'
            : 'var(--shadow-sm)',
          whiteSpace: 'pre-wrap',
        }}>
          {msg.loading ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-muted)' }}>
              <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
              <span>Querying X Layer...</span>
            </div>
          ) : (
            msg.content
              .replace(/\*\*(.*?)\*\*/g, '$1')
          )}
        </div>
        {msg.payment402 && <PaymentCard p={msg.payment402} />}
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4,
          textAlign: isUser ? 'right' : 'left' }}>
          {msg.timestamp.toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}

export default function AskAxon() {
  const [messages, setMessages] = useState<Message[]>([{
    id: 0,
    role: 'assistant',
    content: "Hi! I'm AXON, your X Layer intelligence agent. Ask me anything about gas prices, yield opportunities, wallet analysis, Uniswap pools, or market conditions — in plain English.",
    timestamp: new Date(),
  }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (question: string) => {
    if (!question.trim() || loading) return
    setInput('')
    setLoading(true)

    const userMsg: Message = {
      id: Date.now(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    }
    const loadingMsg: Message = {
      id: Date.now() + 1,
      role: 'assistant',
      content: '',
      loading: true,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMsg, loadingMsg])

    try {
      const res = await fetch(`${API}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })
      const data = await res.json()

      setMessages(prev => prev.map(m =>
        m.id === loadingMsg.id
          ? {
              ...m,
              loading: false,
              content: data.answer || 'No response received.',
              tool: data.tool_used,
            }
          : m
      ))
    } catch (err) {
      setMessages(prev => prev.map(m =>
        m.id === loadingMsg.id
          ? { ...m, loading: false, content: 'Connection error — check if the AXON backend is running.' }
          : m
      ))
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: 'var(--bg-base)' }}>

      {/* Header */}
      <div style={{
        padding: '20px 32px 16px',
        borderBottom: '1px solid var(--border-default)',
        background: 'white',
        boxShadow: 'var(--shadow-sm)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{
            width: 44, height: 44, borderRadius: 12,
            background: 'linear-gradient(135deg, #5B3CF5, #06C4D0)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 16px rgba(91,60,245,0.3)',
          }}>
            <MessageSquare size={22} color="white" />
          </div>
          <div>
            <h1 style={{
              margin: 0, fontSize: 22, fontWeight: 700,
              fontFamily: "'Space Grotesk', sans-serif",
              color: 'var(--text-primary)', letterSpacing: '-0.02em',
            }}>
              Ask AXON
            </h1>
            <p style={{ margin: 0, fontSize: 13, color: 'var(--text-muted)' }}>
              Natural language interface to X Layer intelligence
            </p>
          </div>
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8,
            background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)',
            borderRadius: 8, padding: '6px 12px' }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#10B981',
              boxShadow: '0 0 6px #10B981', display: 'block' }} />
            <span style={{ fontSize: 12, fontWeight: 600, color: '#065F46' }}>X Layer Live</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px', display: 'flex', flexDirection: 'column', gap: 20 }}>

        {/* Suggestions (shown only at start) */}
        {messages.length === 1 && (
          <div style={{ animation: 'fadeSlideUp 0.4s ease' }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)',
              textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>
              Try asking
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              {SUGGESTIONS.map(({ icon: Icon, text, color }) => (
                <button
                  key={text}
                  onClick={() => sendMessage(text)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    background: 'white', border: '1px solid var(--border-default)',
                    borderRadius: 12, padding: '12px 14px', cursor: 'pointer',
                    textAlign: 'left', transition: 'all 0.15s ease',
                    boxShadow: 'var(--shadow-sm)',
                  }}
                  onMouseEnter={e => {
                    (e.currentTarget as HTMLElement).style.borderColor = color
                    ;(e.currentTarget as HTMLElement).style.boxShadow = `0 4px 16px ${color}22`
                  }}
                  onMouseLeave={e => {
                    (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-default)'
                    ;(e.currentTarget as HTMLElement).style.boxShadow = 'var(--shadow-sm)'
                  }}
                >
                  <div style={{
                    width: 32, height: 32, borderRadius: 8, flexShrink: 0,
                    background: `${color}15`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <Icon size={16} color={color} />
                  </div>
                  <span style={{ fontSize: 13, color: 'var(--text-secondary)', flex: 1 }}>{text}</span>
                  <ChevronRight size={14} color="var(--text-muted)" />
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map(msg => (
          <MessageBubble key={msg.id} msg={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: '16px 32px 24px',
        borderTop: '1px solid var(--border-default)',
        background: 'white',
      }}>
        <div style={{
          display: 'flex', gap: 12, alignItems: 'center',
          background: 'var(--bg-subtle)',
          border: '2px solid var(--border-default)',
          borderRadius: 16, padding: '8px 8px 8px 16px',
          transition: 'border-color 0.15s ease',
        }}
          onFocusCapture={e => (e.currentTarget.style.borderColor = 'var(--axon-primary)')}
          onBlurCapture={e => (e.currentTarget.style.borderColor = 'var(--border-default)')}
        >
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask about gas, yields, wallets, pools..."
            disabled={loading}
            style={{
              flex: 1, border: 'none', background: 'transparent',
              fontSize: 14, color: 'var(--text-primary)', outline: 'none',
              fontFamily: "'Inter', sans-serif",
            }}
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={loading || !input.trim()}
            style={{
              width: 40, height: 40, borderRadius: 12, border: 'none',
              background: loading || !input.trim()
                ? 'var(--border-default)'
                : 'linear-gradient(135deg, #5B3CF5, #06C4D0)',
              cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              transition: 'all 0.2s ease',
              flexShrink: 0,
              boxShadow: loading || !input.trim() ? 'none' : '0 4px 12px rgba(91,60,245,0.35)',
            }}
          >
            {loading
              ? <Loader2 size={16} color="var(--text-muted)" style={{ animation: 'spin 1s linear infinite' }} />
              : <Send size={16} color={input.trim() ? 'white' : 'var(--text-muted)'} />
            }
          </button>
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 8, textAlign: 'center' }}>
          Powered by AXON MCP Tools + Groq LLaMA 3.3 · Include a wallet address (0x...) for portfolio analysis
        </div>
      </div>

      <style>{`
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
