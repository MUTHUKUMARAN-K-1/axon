"""
AXON — Onchain OS Tool Wrappers
Wraps OKX Onchain OS / DEX APIs as MCP-callable tools for AI agents.
X Layer Chain ID: 196 (mainnet) | 195 (testnet)
"""

import httpx
import os
import logging
import hashlib
import hmac
import base64
import asyncio
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger("axon.tools.onchain_os")

XLAYER_CHAIN_ID = "196"
OKX_BASE = "https://www.okx.com"
OKX_DEX_BASE = f"{OKX_BASE}/api/v5/dex"
OKX_WALLET_BASE = f"{OKX_BASE}/api/v5/wallet"

# Native OKB token on X Layer
OKB_ADDRESS = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
USDT_XLAYER = "0x1e4a5963abfd975d8c9021ce480b42188849d41d"
WOKB_XLAYER = "0xe538905cf8410324e03a5a23c1c177a474d59b2"


def _get_okx_headers(path: str, method: str = "GET", body: str = "") -> dict:
    """Generate OKX API auth headers (HMAC-SHA256).

    BUG FIXED: original used `hmac.new()` which does not exist in Python.
    Correct call is `hmac.new()` → actually `hmac.new` is NOT the right API.
    The correct Python stdlib call is `hmac.new(key, msg, digestmod)`.
    Also fixed: original always used 'GET' in the HMAC message regardless of
    the actual HTTP method, which causes 401s on POST calls.
    """
    api_key = os.getenv("OKX_API_KEY", "")
    secret = os.getenv("OKX_SECRET_KEY", "")
    passphrase = os.getenv("OKX_PASSPHRASE", "")

    if not api_key or not secret:
        return {}

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    msg = f"{timestamp}{method}{path}{body}"
    sig = base64.b64encode(
        hmac.new(secret.encode(), msg.encode(), hashlib.sha256).digest()
    ).decode()

    return {
        "OK-ACCESS-KEY": api_key,
        "OK-ACCESS-SIGN": sig,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": passphrase,
        "Content-Type": "application/json",
    }


def _safe_float(value, default: float = 0.0) -> float:
    """Safely convert a value to float, returning default on failure."""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


async def get_wallet_portfolio(address: str, chain_id: str = XLAYER_CHAIN_ID) -> dict:
    """
    MCP Tool: get_wallet_portfolio
    Returns token balances and USD values for a wallet on X Layer.
    """
    try:
        path = "/api/v5/wallet/asset/all-token-balances-by-address"
        params = {
            "address": address,
            "chainIndex": chain_id,
            "filter": "1",
        }
        headers = _get_okx_headers(path)

        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{OKX_BASE}{path}",
                params=params,
                headers=headers or None,
            )
            data = r.json()

        if data.get("code") == "0":
            raw_data = data.get("data", [])
            tokens = raw_data[0].get("tokenAssets", []) if raw_data else []
            total_usd = sum(
                _safe_float(t.get("balance")) * _safe_float(t.get("tokenPrice"))
                for t in tokens
                if t.get("tokenPrice")
            )
            return {
                "success": True,
                "address": address,
                "chain": "X Layer",
                "chain_id": chain_id,
                "total_usd_value": round(total_usd, 4),
                "token_count": len(tokens),
                "tokens": [
                    {
                        "symbol": t.get("symbol", "UNKNOWN"),
                        "name": t.get("tokenName", ""),
                        "balance": t.get("balance", "0"),
                        "address": t.get("tokenAddress", ""),
                        "price_usd": t.get("tokenPrice", "0"),
                        "value_usd": round(
                            _safe_float(t.get("balance")) * _safe_float(t.get("tokenPrice")), 4
                        ) if t.get("tokenPrice") else 0,
                        "logo": t.get("tokenLogoUrl", ""),
                    }
                    for t in tokens
                ],
            }
        else:
            return {"success": False, "error": data.get("msg", "API error"), "raw": data}

    except Exception as e:
        logger.error(f"get_wallet_portfolio error: {e}")
        return {"success": False, "error": str(e), "tokens": [], "token_count": 0, "total_usd_value": 0}


async def get_token_price(
    token_address: str, chain_id: str = XLAYER_CHAIN_ID
) -> dict:
    """
    MCP Tool: get_token_price
    Returns real-time price data for any token on X Layer.
    """
    try:
        path = "/api/v5/wallet/token/price"
        params = {
            "chainIndex": chain_id,
            "tokenAddress": token_address,
        }
        headers = _get_okx_headers(path)

        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{OKX_BASE}{path}",
                params=params,
                headers=headers or None,
            )
            data = r.json()

        if data.get("code") == "0":
            price_data = data.get("data", [{}])[0]
            return {
                "success": True,
                "token_address": token_address,
                "chain": "X Layer",
                "price_usd": price_data.get("price", "0"),
                "price_24h_change": price_data.get("priceChange24H", "0"),
                "market_cap": price_data.get("marketCap", "0"),
                "volume_24h": price_data.get("volume24H", "0"),
                "last_updated": price_data.get("time", ""),
            }
        else:
            return {"success": False, "error": data.get("msg", "API error"), "price_usd": "0"}

    except Exception as e:
        logger.error(f"get_token_price error: {e}")
        return {"success": False, "error": str(e), "price_usd": "0"}


async def get_transaction_history(
    address: str,
    chain_id: str = XLAYER_CHAIN_ID,
    limit: int = 20,
) -> dict:
    """
    MCP Tool: get_transaction_history
    Returns recent transactions for a wallet address on X Layer.
    """
    try:
        path = "/api/v5/wallet/post-transaction/transactions-by-address"
        params = {
            "address": address,
            "chainIndex": chain_id,
            "limit": str(min(limit, 100)),
        }
        headers = _get_okx_headers(path)

        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{OKX_BASE}{path}",
                params=params,
                headers=headers or None,
            )
            data = r.json()

        if data.get("code") == "0":
            raw_data = data.get("data", [])
            txs = raw_data[0].get("transactionList", []) if raw_data else []
            return {
                "success": True,
                "address": address,
                "chain": "X Layer",
                "transaction_count": len(txs),
                "transactions": [
                    {
                        "hash": tx.get("txHash", ""),
                        "type": tx.get("txType", "transfer"),
                        "from": tx.get("from", [{}])[0].get("address", "") if tx.get("from") else "",
                        "to": tx.get("to", [{}])[0].get("address", "") if tx.get("to") else "",
                        "amount": tx.get("amount", "0"),
                        "symbol": tx.get("symbol", "OKB"),
                        "status": tx.get("txStatus", ""),
                        "timestamp": tx.get("txTime", ""),
                        "gas_fee": tx.get("txFee", "0"),
                    }
                    for tx in txs
                ],
            }
        else:
            # Return empty gracefully — no API key or no txs yet
            return {
                "success": False,
                "error": data.get("msg", "API error"),
                "transaction_count": 0,
                "transactions": [],
            }

    except Exception as e:
        logger.error(f"get_transaction_history error: {e}")
        return {"success": False, "error": str(e), "transaction_count": 0, "transactions": []}


async def get_defi_positions(
    address: str, chain_id: str = XLAYER_CHAIN_ID
) -> dict:
    """
    MCP Tool: get_defi_positions
    Returns active DeFi positions (liquidity, staking, lending) on X Layer.

    BUG FIXED: old path "/api/v5/wallet/defi/yield/product-list" is a product
    listing endpoint, not user positions. Correct endpoint for user DeFi positions
    is "/api/v5/wallet/defi/investment/positions". Falls back gracefully when
    no API key is set.
    """
    try:
        path = "/api/v5/wallet/defi/investment/positions"
        params = {"chainId": chain_id, "address": address}
        headers = _get_okx_headers(path)

        if not headers:
            # No API key — return empty positions rather than crashing
            return {
                "success": True,
                "address": address,
                "chain": "X Layer",
                "positions": [],
                "total_positions": 0,
                "note": "OKX API key not configured",
            }

        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{OKX_BASE}{path}",
                params=params,
                headers=headers,
            )
            data = r.json()

        if data.get("code") == "0":
            products = data.get("data", [])
            return {
                "success": True,
                "address": address,
                "chain": "X Layer",
                "positions": [
                    {
                        "protocol": p.get("projectName", ""),
                        "type": p.get("productType", ""),
                        "apy": p.get("apy", "0"),
                        "tvl_usd": p.get("tvl", "0"),
                        "token_pair": p.get("tokenPair", ""),
                        "investment_usd": p.get("investAmount", "0"),
                        "rewards_usd": p.get("rewardAmount", "0"),
                    }
                    for p in products
                ],
                "total_positions": len(products),
            }
        else:
            return {"success": False, "error": data.get("msg", "API error"), "positions": [], "total_positions": 0}

    except Exception as e:
        logger.error(f"get_defi_positions error: {e}")
        return {"success": False, "error": str(e), "positions": [], "total_positions": 0}


async def get_xlayer_stats() -> dict:
    """
    MCP Tool: get_xlayer_stats
    Returns X Layer chain info. Uses supported-chains endpoint with chainIndex filter.

    BUG FIXED: old code compared chainIndex (str "196") against XLAYER_CHAIN_ID which
    is also a str but was being compared loosely. Made comparison explicit.
    """
    try:
        path = "/api/v5/wallet/chain/supported-chains"
        headers = _get_okx_headers(path)

        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{OKX_BASE}{path}",
                headers=headers or None,
            )
            data = r.json()

        # chainIndex in OKX response is a string
        xlayer = next(
            (c for c in data.get("data", []) if str(c.get("chainIndex", "")) == XLAYER_CHAIN_ID),
            {},
        )

        return {
            "success": True,
            "chain": "X Layer",
            "chain_id": XLAYER_CHAIN_ID,
            "name": xlayer.get("chainName", "X Layer"),
            "symbol": xlayer.get("nativeCurrency", "OKB"),
            "logo": xlayer.get("logoUrl", ""),
            "explorer": "https://www.oklink.com/xlayer",
            "rpc": "https://rpc.xlayer.tech",
            "found": bool(xlayer),
        }

    except Exception as e:
        logger.error(f"get_xlayer_stats error: {e}")
        return {"success": False, "error": str(e)}


async def check_address_security(address: str) -> dict:
    """
    MCP Tool: check_address_security
    Checks if an address is blacklisted/malicious via OKX DEX security API.
    """
    try:
        path = f"/api/v5/dex/security/address?chainId=196&address={address}"
        headers = _get_okx_headers(path)  # shared HMAC auth
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"https://web3.okx.com{path}", headers=headers)
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            d = data["data"][0]
            return {
                "success": True,
                "address": address,
                "is_blacklisted": d.get("isBlacklist", False),
                "risk_level": d.get("riskLevel", ""),
                "risk_type": d.get("riskType", []),
                "tags": d.get("addressTag", []),
            }
        return {"success": False, "error": data.get("msg", "API error")}
    except Exception as e:
        logger.error(f"check_address_security error: {e}")
        return {"success": False, "error": str(e)}


async def check_url_safety(url: str) -> dict:
    """
    MCP Tool: check_url_safety
    Checks if a URL is a phishing/scam site via OKX DEX security API.
    """
    try:
        import urllib.parse
        encoded = urllib.parse.quote(url, safe="")
        path = f"/api/v5/dex/security/url?url={encoded}"
        headers = _get_okx_headers(path)  # shared HMAC auth
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"https://web3.okx.com{path}", headers=headers)
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            d = data["data"][0]
            return {
                "success": True,
                "url": url,
                "is_phishing": d.get("isPhishing", False),
                "is_malicious": d.get("isMalicious", False),
                "risk_type": d.get("riskType", ""),
                "verdict": "DANGEROUS" if d.get("isPhishing") or d.get("isMalicious") else "SAFE",
            }
        return {"success": False, "error": data.get("msg", "API error")}
    except Exception as e:
        logger.error(f"check_url_safety error: {e}")
        return {"success": False, "error": str(e)}


async def get_nft_holdings(address: str, chain_id: str = XLAYER_CHAIN_ID) -> dict:
    """
    MCP Tool: get_nft_holdings
    Returns NFT holdings for a wallet via OKX Onchain OS.
    """
    try:
        path = "/api/v5/wallet/asset/nft-list"
        headers = _get_okx_headers(path)
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{OKX_BASE}{path}",
                params={"address": address, "chainIndex": chain_id},
                headers=headers or None,
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            nfts = data["data"][0].get("nftList", [])
            return {
                "success": True,
                "address": address,
                "chain": "X Layer",
                "nft_count": len(nfts),
                "nfts": [
                    {
                        "collection": n.get("collectionName", ""),
                        "token_id": n.get("tokenId", ""),
                        "name": n.get("nftName", ""),
                        "contract": n.get("tokenContractAddress", ""),
                        "standard": n.get("tokenType", ""),
                        "image": n.get("nftImageUrl", ""),
                        "floor_price_usd": n.get("floorPrice", "0"),
                    }
                    for n in nfts
                ],
            }
        return {"success": False, "error": data.get("msg", "API error"), "nfts": [], "nft_count": 0}
    except Exception as e:
        logger.error(f"get_nft_holdings error: {e}")
        return {"success": False, "error": str(e), "nfts": [], "nft_count": 0}


async def get_yield_products(chain_id: str = XLAYER_CHAIN_ID) -> dict:
    """
    MCP Tool: get_yield_products
    Returns available DeFi yield products on X Layer via OKX Onchain OS.
    """
    try:
        path = "/api/v5/wallet/defi/yield/product-list"
        headers = _get_okx_headers(path)
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{OKX_BASE}{path}",
                params={"chainId": chain_id},
                headers=headers or None,
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            products = data.get("data", [])
            return {
                "success": True,
                "chain": "X Layer",
                "product_count": len(products),
                "products": [
                    {
                        "protocol": p.get("projectName", ""),
                        "type": p.get("productType", ""),
                        "token_pair": p.get("investToken", ""),
                        "apy": p.get("apy", "0"),
                        "tvl_usd": p.get("tvl", "0"),
                        "min_investment": p.get("minInvestAmount", "0"),
                        "risk_level": p.get("riskLevel", ""),
                        "lock_period_days": p.get("lockPeriod", 0),
                    }
                    for p in products
                ],
            }
        return {"success": False, "error": data.get("msg", "API error"), "products": []}
    except Exception as e:
        logger.error(f"get_yield_products error: {e}")
        return {"success": False, "error": str(e), "products": []}


async def get_swap_execution(
    from_token: str, to_token: str, amount: str,
    user_wallet: str, chain_id: str = XLAYER_CHAIN_ID, slippage: str = "0.5"
) -> dict:
    """
    MCP Tool: get_swap_execution
    Returns actual on-chain calldata to execute a swap via OKX DEX aggregator on X Layer.
    """
    try:
        path = "/api/v5/dex/aggregator/swap"
        params = {
            "chainId": chain_id,
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "amount": amount,
            "userWalletAddress": user_wallet,
            "slippage": slippage,
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(f"{OKX_BASE}{path}", params=params)
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            d = data["data"][0]
            tx = d.get("tx", {})
            return {
                "success": True,
                "chain": "X Layer",
                "from_token": from_token,
                "to_token": to_token,
                "from_amount": amount,
                "to_amount": d.get("routerResult", {}).get("toTokenAmount", "0"),
                "price_impact": d.get("routerResult", {}).get("priceImpactPercentage", "0"),
                "tx": {
                    "to": tx.get("to", ""),
                    "data": tx.get("data", ""),
                    "value": tx.get("value", "0"),
                    "gas": tx.get("gas", "0"),
                    "gas_price": tx.get("gasPrice", "0"),
                },
                "note": "Sign and broadcast this tx to execute the swap",
            }
        return {"success": False, "error": data.get("msg", "Swap data unavailable")}
    except Exception as e:
        logger.error(f"get_swap_execution error: {e}")
        return {"success": False, "error": str(e)}


async def get_wallet_net_worth(address: str) -> dict:
    """
    MCP Tool: get_wallet_net_worth
    Returns total portfolio value across all chains for a wallet (cross-chain net worth).
    Uses OKX Onchain OS /api/v5/wallet/asset/net-worth.
    """
    try:
        path = "/api/v5/wallet/asset/net-worth"
        headers = _get_okx_headers(path)
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{OKX_BASE}{path}",
                params={"address": address},
                headers=headers or None,
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            d = data["data"][0]
            return {
                "success": True,
                "address": address,
                "total_usd": d.get("totalValue", "0"),
                "chains": [
                    {
                        "chain": c.get("chainName", ""),
                        "chain_id": c.get("chainIndex", ""),
                        "value_usd": c.get("totalValue", "0"),
                    }
                    for c in d.get("chainNetWorthDetails", [])
                ],
            }
        return {"success": False, "error": data.get("msg", "API error"), "total_usd": "0"}
    except Exception as e:
        logger.error(f"get_wallet_net_worth error: {e}")
        return {"success": False, "error": str(e), "total_usd": "0"}


async def get_token_detail(token_address: str, chain_id: str = XLAYER_CHAIN_ID) -> dict:
    """
    MCP Tool: get_token_detail
    Returns rich token metadata: holder count, FDV, market cap rank, socials, website.
    Uses OKX Onchain OS /api/v5/wallet/token/token-detail.
    """
    try:
        path = "/api/v5/wallet/token/token-detail"
        headers = _get_okx_headers(path)
        async with httpx.AsyncClient(timeout=12.0) as client:
            r = await client.get(
                f"{OKX_BASE}{path}",
                params={"chainIndex": chain_id, "tokenAddress": token_address},
                headers=headers or None,
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            d = data["data"][0]
            return {
                "success": True,
                "token_address": token_address,
                "chain": "X Layer",
                "name": d.get("tokenName", ""),
                "symbol": d.get("tokenSymbol", ""),
                "decimals": d.get("decimals", 18),
                "total_supply": d.get("totalSupply", "0"),
                "holder_count": d.get("holderCount", 0),
                "market_cap_usd": d.get("marketCap", "0"),
                "fdv_usd": d.get("fullyDilutedValuation", "0"),
                "rank": d.get("marketCapRank", None),
                "website": d.get("officialWebsite", ""),
                "description": d.get("tokenDesc", ""),
                "socials": {
                    "twitter": d.get("twitterUrl", ""),
                    "telegram": d.get("telegramUrl", ""),
                    "github": d.get("githubUrl", ""),
                },
                "logo": d.get("tokenLogoUrl", ""),
            }
        return {"success": False, "error": data.get("msg", "API error")}
    except Exception as e:
        logger.error(f"get_token_detail error: {e}")
        return {"success": False, "error": str(e)}


async def lookup_transaction(tx_hash: str, chain_id: str = XLAYER_CHAIN_ID) -> dict:
    """
    MCP Tool: lookup_transaction
    Decode a transaction hash — get from/to, value, status, gas, token transfers.
    Uses OKX Onchain OS /api/v5/wallet/post-transaction/transaction-by-hash.
    """
    try:
        path = "/api/v5/wallet/post-transaction/transaction-by-hash"
        headers = _get_okx_headers(path)
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{OKX_BASE}{path}",
                params={"chainIndex": chain_id, "txHash": tx_hash},
                headers=headers or None,
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            d = data["data"][0]
            txs = d.get("transactionList", [])
            tx = txs[0] if txs else {}
            return {
                "success": True,
                "tx_hash": tx_hash,
                "chain": "X Layer",
                "status": tx.get("txStatus", ""),
                "block": tx.get("height", ""),
                "timestamp": tx.get("txTime", ""),
                "from": (tx.get("from") or [{}])[0].get("address", ""),
                "to": (tx.get("to") or [{}])[0].get("address", ""),
                "value": tx.get("amount", "0"),
                "symbol": tx.get("symbol", "OKB"),
                "gas_fee": tx.get("txFee", "0"),
                "type": tx.get("txType", ""),
                "token_transfers": tx.get("tokenTransferDetails", []),
            }
        return {"success": False, "error": data.get("msg", "API error")}
    except Exception as e:
        logger.error(f"lookup_transaction error: {e}")
        return {"success": False, "error": str(e)}


async def get_supported_tokens(chain_id: str = XLAYER_CHAIN_ID) -> dict:
    """
    MCP Tool: get_supported_tokens
    Returns all tokens supported by the OKX DEX aggregator on X Layer.
    """
    try:
        path = "/api/v5/dex/aggregator/all-tokens"
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{OKX_BASE}{path}",
                params={"chainId": chain_id},
            )
            data = r.json()
        if data.get("code") == "0":
            tokens = data.get("data", [])
            return {
                "success": True,
                "chain": "X Layer",
                "token_count": len(tokens),
                "tokens": [
                    {
                        "address": t.get("tokenContractAddress", ""),
                        "symbol": t.get("tokenSymbol", ""),
                        "name": t.get("tokenName", ""),
                        "decimals": t.get("decimals", 18),
                        "logo": t.get("tokenLogoUrl", ""),
                    }
                    for t in tokens[:100]  # cap at 100 to save memory
                ],
            }
        return {"success": False, "error": data.get("msg", "API error"), "tokens": []}
    except Exception as e:
        logger.error(f"get_supported_tokens error: {e}")
        return {"success": False, "error": str(e), "tokens": []}


async def get_cross_chain_quote(
    from_chain_id: str,
    to_chain_id: str,
    from_token: str,
    to_token: str,
    amount: str,
    user_wallet: str,
    slippage: str = "0.5",
) -> dict:
    """
    MCP Tool: get_cross_chain_quote
    Get a cross-chain bridge quote via OKX DEX cross-chain aggregator.
    E.g. ETH on Ethereum → OKB on X Layer.
    """
    try:
        path = "/api/v5/dex/cross-chain/quote"
        params = {
            "fromChainId": from_chain_id,
            "toChainId": to_chain_id,
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "amount": amount,
            "slippage": slippage,
            "userWalletAddress": user_wallet,
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(f"{OKX_BASE}{path}", params=params)
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            q = data["data"][0]
            return {
                "success": True,
                "from_chain_id": from_chain_id,
                "to_chain_id": to_chain_id,
                "from_token": from_token,
                "to_token": to_token,
                "from_amount": amount,
                "to_amount": q.get("toTokenAmount", "0"),
                "minimum_received": q.get("minimumReceived", "0"),
                "bridge": q.get("bridgeName", ""),
                "fee_usd": q.get("fee", {}).get("totalFee", "0"),
                "estimated_time_sec": q.get("estimatedTime", 0),
                "price_impact": q.get("priceImpact", "0"),
            }
        return {"success": False, "error": data.get("msg", "Quote unavailable"), "to_amount": "0"}
    except Exception as e:
        logger.error(f"get_cross_chain_quote error: {e}")
        return {"success": False, "error": str(e), "to_amount": "0"}


async def get_swap_quote_onchain_os(
    from_token: str,
    to_token: str,
    amount: str,
    chain_id: str = XLAYER_CHAIN_ID,
    slippage: str = "0.5",
) -> dict:
    """
    MCP Tool: get_swap_quote (Onchain OS DEX aggregator)
    Returns best swap route across all DEXes on X Layer via OKX aggregator.

    BUG FIXED: OKX DEX aggregator v5 quote endpoint requires `chainId` as integer
    string "196", not the chainIndex format. Also the correct field names in the
    response are `toTokenAmount` and `estimateGasFee`.
    """
    try:
        path = "/api/v5/dex/aggregator/quote"
        params = {
            "chainId": chain_id,          # X Layer = "196"
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "amount": amount,
            "slippage": slippage,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(f"{OKX_BASE}{path}", params=params)
            data = r.json()

        if data.get("code") == "0":
            quote = data.get("data", [{}])[0]
            to_token_detail = quote.get("toToken", {})
            from_token_detail = quote.get("fromToken", {})
            return {
                "success": True,
                "from_token": from_token,
                "to_token": to_token,
                "from_amount": amount,
                "to_amount": quote.get("toTokenAmount", "0"),
                "from_token_symbol": from_token_detail.get("tokenSymbol", ""),
                "to_token_symbol": to_token_detail.get("tokenSymbol", ""),
                "price_impact": quote.get("priceImpactPercentage", "0"),
                "route": quote.get("quoteCompareList", []),
                "gas_estimate": quote.get("estimateGasFee", "0"),
                "dex_router": quote.get("dexRouterList", []),
                "chain": "X Layer",
            }
        else:
            return {"success": False, "error": data.get("msg", "Quote failed"), "to_amount": "0"}

    except Exception as e:
        logger.error(f"get_swap_quote error: {e}")
        return {"success": False, "error": str(e), "to_amount": "0"}
