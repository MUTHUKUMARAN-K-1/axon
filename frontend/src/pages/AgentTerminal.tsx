import React, { useState, useRef, useEffect } from 'react'
import {
  Terminal, Send, Zap, ChevronRight, Cpu,
  CheckCircle2, XCircle, Info, Loader2, Activity
} from 'lucide-react'
import { callMcpTool, listMcpTools } from '../services/api'
import toast from 'react-hot-toast'

interface LogEntry {
  id: number
  type: 'input' | 'status' | 'result' | 'error' | 'info'
  content: string
  timestamp: string
}

const QUICK_COMMANDS = [
  { label: 'Market Overview', tool: 'get_market_overview', args: {}, icon: Activity },
  { label: 'Gas Price', tool: 'get_gas_price', args: {}, icon: Zap },
  { label: 'Top Pools', tool: 'get_uniswap_top_pools', args: { limit: 5 }, icon: ChevronRight },
  { label: 'Latest Block', tool: 'get_block_info', args: {}, icon: Cpu },
  { label: 'Yield Opps', tool: 'get_yield_opportunities', args: { min_apy: 5 }, icon: CheckCircle2 },
]

const LOG_STYLES: Record<LogEntry['type'], { color: string; icon: React.ReactNode; prefix: string }> = {
  input:  { color: '#5B3CF5', icon: <ChevronRight size={11} />, prefix: '' },
  status: { color: '#8B87A8', icon: <Loader2 size={11} style={{ animation: 'spin 1s linear infinite' }} />, prefix: '' },
  result: { color: '#10B981', icon: <CheckCircle2 size={11} />, prefix: '' },
  error:  { color: '#EF4444', icon: <XCircle size={11} />,  prefix: '' },
  info:   { color: '#06C4D0', icon: <Info size={11} />,      prefix: '' },
}

export default function AgentTerminal() {
  const [input, setInput] = useState('')
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [tools, setTools] = useState<string[]>([])
  const [running, setRunning] = useState(false)
  const logRef = useRef<HTMLDivElement>(null)
  const logId = useRef(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const addLog = (type: LogEntry['type'], content: string) => {
    const entry: LogEntry = {
      id: ++logId.current,
      type,
      content,
      timestamp: new Date().toLocaleTimeString(),
    }
    setLogs((prev) => [...prev, entry])
    setTimeout(() => logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' }), 50)
  }

  useEffect(() => {
    addLog('info', 'AXON Agent Terminal initialized.')
    addLog('info', 'X Layer Neural Intelligence Layer v1.0.0')
    addLog('info', 'Type a tool name or use Quick Commands below. Type "help" to list tools.')
    listMcpTools().then((data: any) => {
      const names = (data.tools || []).map((t: any) => t.name)
      setTools(names)
      addLog('info', `${names.length} MCP tools loaded.`)
    }).catch(() => addLog('error', 'Could not connect to AXON backend. Is it running?'))
  }, [])

  const executeCommand = async (toolName: string, args: Record<string, unknown> = {}) => {
    if (!toolName.trim()) return
    setRunning(true)
    addLog('input', `axon.call("${toolName}", ${JSON.stringify(args)})`)

    if (toolName.trim() === 'help') {
      addLog('result', `Available tools:\n${tools.map(t => `  • ${t}`).join('\n')}`)
      setRunning(false)
      return
    }

    try {
      addLog('status', `Executing ${toolName}...`)
      const result = await callMcpTool(toolName, args)
      addLog('result', JSON.stringify((result as any).result || result, null, 2))
    } catch (e: any) {
      addLog('error', e.message || 'Tool execution failed')
    } finally {
      setRunning(false)
      inputRef.current?.focus()
    }
  }

  const handleSend = () => {
    const trimmed = input.trim()
    if (!trimmed) return
    const spaceIdx = trimmed.indexOf(' ')
    if (spaceIdx === -1) {
      executeCommand(trimmed)
    } else {
      const toolName = trimmed.slice(0, spaceIdx)
      try {
        const args = JSON.parse(trimmed.slice(spaceIdx + 1))
        executeCommand(toolName, args)
      } catch {
        executeCommand(trimmed)
      }
    }
    setInput('')
  }

  const clearLogs = () => setLogs([])

  return (
    <div style={{ padding: '32px', display: 'flex', flexDirection: 'column', height: '100vh', maxHeight: '100vh', boxSizing: 'border-box' }}>
      {/* Header */}
      <div className="animate-fade-up" style={{ marginBottom: 20, flexShrink: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1 style={{ fontSize: 30, fontWeight: 700, fontFamily: "'Space Grotesk',sans-serif", letterSpacing: '-0.03em' }}>
              Agent Terminal
            </h1>
            <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 4 }}>
              Live MCP tool execution · Direct X Layer intelligence
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            {running && (
              <div style={{
                display: 'flex', alignItems: 'center', gap: 8,
                background: 'var(--axon-primary-light)',
                border: '1px solid rgba(91,60,245,0.2)',
                borderRadius: 8, padding: '6px 12px',
              }}>
                <div className="live-dot" style={{ background: 'var(--axon-primary)' }} />
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--axon-primary)' }}>Running</span>
              </div>
            )}
            <button
              id="clear-terminal-btn"
              onClick={clearLogs}
              className="btn-ghost"
              style={{ fontSize: 12 }}
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Quick Commands */}
      <div className="animate-fade-up" style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16, flexShrink: 0, animationDelay: '60ms' }}>
        {QUICK_COMMANDS.map((cmd) => {
          const Icon = cmd.icon
          return (
            <button
              key={cmd.tool}
              id={`quick-${cmd.tool}`}
              onClick={() => executeCommand(cmd.tool, cmd.args)}
              disabled={running}
              className="chip"
            >
              <Icon size={12} />
              {cmd.label}
            </button>
          )
        })}
      </div>

      {/* Terminal Output */}
      <div
        className="card animate-fade-up"
        ref={logRef}
        style={{
          flex: 1,
          padding: '20px',
          overflowY: 'auto',
          background: '#FDFCFF',
          animationDelay: '120ms',
          minHeight: 0,
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 12,
          lineHeight: 1.7,
        }}
      >
        {logs.length === 0 ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', flexDirection: 'column', gap: 12 }}>
            <Terminal size={32} color="var(--text-placeholder)" />
            <p style={{ fontSize: 13, color: 'var(--text-muted)', fontFamily: 'inherit' }}>
              Awaiting commands…
            </p>
          </div>
        ) : (
          logs.map((log) => {
            const style = LOG_STYLES[log.type]
            return (
              <div key={log.id} style={{ display: 'flex', gap: 10, marginBottom: 6, alignItems: 'flex-start' }}>
                {/* Timestamp */}
                <span style={{ fontSize: 10, color: 'var(--text-placeholder)', flexShrink: 0, marginTop: 2, minWidth: 70 }}>
                  {log.timestamp}
                </span>
                {/* Icon */}
                <span style={{ color: style.color, flexShrink: 0, marginTop: 3 }}>{style.icon}</span>
                {/* Content */}
                <pre style={{
                  margin: 0, color: style.color,
                  whiteSpace: 'pre-wrap', wordBreak: 'break-word',
                  flex: 1, fontFamily: 'inherit', fontSize: 'inherit',
                }}>
                  {log.content}
                </pre>
              </div>
            )
          })
        )}
        {running && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 4, color: 'var(--text-muted)' }}>
            <Loader2 size={12} style={{ animation: 'spin 1s linear infinite' }} />
            <span style={{ fontSize: 12 }}>Processing...</span>
          </div>
        )}
      </div>

      {/* Input */}
      <div
        className="animate-fade-up"
        style={{ display: 'flex', gap: 10, marginTop: 16, flexShrink: 0, animationDelay: '180ms' }}
      >
        <div style={{ flex: 1, position: 'relative' }}>
          <ChevronRight
            size={14} color="var(--axon-primary)"
            style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }}
          />
          <input
            id="terminal-input"
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !running && handleSend()}
            placeholder='tool_name {"arg": "value"} — or type "help"'
            className="input-field mono"
            style={{ paddingLeft: 38, fontFamily: "'JetBrains Mono', monospace", fontSize: 13 }}
            disabled={running}
          />
        </div>
        <button
          id="terminal-send-btn"
          onClick={handleSend}
          disabled={running || !input.trim()}
          className="btn-primary"
          style={{ padding: '0 20px', display: 'flex', alignItems: 'center', gap: 6 }}
        >
          <Send size={15} />
          Run
        </button>
      </div>
    </div>
  )
}
