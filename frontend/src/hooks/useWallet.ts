/**
 * useWallet — MetaMask / EIP-1193 wallet hook for AXON
 * Auto-prompts to switch to X Layer (Chain ID 196) on connect.
 */
import { useState, useEffect, useCallback } from 'react'

const X_LAYER_CHAIN_ID = '0xc4' // 196 in hex

export interface WalletState {
  address: string | null
  chainId: string | null
  isXLayer: boolean
  connecting: boolean
  error: string | null
}

export function useWallet() {
  const [state, setState] = useState<WalletState>({
    address: null,
    chainId: null,
    isXLayer: false,
    connecting: false,
    error: null,
  })

  const eth = typeof window !== 'undefined' ? (window as any).ethereum : null
  const isAvailable = !!eth

  // Sync state from provider
  const sync = useCallback(async () => {
    if (!eth) return
    try {
      const accounts: string[] = await eth.request({ method: 'eth_accounts' })
      const chainId: string = await eth.request({ method: 'eth_chainId' })
      setState(s => ({
        ...s,
        address: accounts[0] ?? null,
        chainId,
        isXLayer: chainId === X_LAYER_CHAIN_ID,
        error: null,
      }))
    } catch {/* ignore */}
  }, [eth])

  useEffect(() => {
    sync()
    if (!eth) return
    eth.on('accountsChanged', sync)
    eth.on('chainChanged', sync)
    return () => {
      eth.removeListener('accountsChanged', sync)
      eth.removeListener('chainChanged', sync)
    }
  }, [eth, sync])

  const connect = useCallback(async () => {
    if (!eth) {
      setState(s => ({ ...s, error: 'MetaMask not detected. Install it at metamask.io.' }))
      return
    }
    setState(s => ({ ...s, connecting: true, error: null }))
    try {
      await eth.request({ method: 'eth_requestAccounts' })

      // Auto-switch to X Layer
      try {
        await eth.request({ method: 'wallet_switchEthereumChain', params: [{ chainId: X_LAYER_CHAIN_ID }] })
      } catch (switchErr: any) {
        // Chain not added — add it
        if (switchErr.code === 4902) {
          await eth.request({
            method: 'wallet_addEthereumChain',
            params: [{
              chainId: X_LAYER_CHAIN_ID,
              chainName: 'X Layer Mainnet',
              nativeCurrency: { name: 'OKB', symbol: 'OKB', decimals: 18 },
              rpcUrls: ['https://rpc.xlayer.tech'],
              blockExplorerUrls: ['https://www.oklink.com/xlayer'],
            }],
          })
        }
      }
      await sync()
    } catch (err: any) {
      setState(s => ({ ...s, error: err?.message ?? 'Connection rejected' }))
    } finally {
      setState(s => ({ ...s, connecting: false }))
    }
  }, [eth, sync])

  const disconnect = useCallback(() => {
    setState({ address: null, chainId: null, isXLayer: false, connecting: false, error: null })
  }, [])

  const switchToXLayer = useCallback(async () => {
    if (!eth) return
    try {
      await eth.request({ method: 'wallet_switchEthereumChain', params: [{ chainId: X_LAYER_CHAIN_ID }] })
      await sync()
    } catch {/* silently ignore */}
  }, [eth, sync])

  return { ...state, isAvailable, connect, disconnect, switchToXLayer }
}
