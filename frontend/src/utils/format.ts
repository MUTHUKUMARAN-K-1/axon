export function formatUsd(value: number, maximumFractionDigits = 2): string {
  return `$${value.toLocaleString(undefined, { maximumFractionDigits })}`
}

export function formatTokenPrice(value: string | number | undefined, digits = 6): string {
  const numeric = typeof value === 'string' ? Number.parseFloat(value) : value
  return Number.isFinite(numeric) ? `$${numeric!.toFixed(digits)}` : '—'
}

export function isEvmAddress(value: string): boolean {
  return /^0x[a-fA-F0-9]{40}$/.test(value)
}
