"""
AXON — OKLink Explorer Tools
Wraps OKX OKLink blockchain explorer APIs for X Layer intelligence.
Chain short name: XLAYER | Chain ID: 196
"""

import httpx
import os
import logging

logger = logging.getLogger("axon.tools.oklink")

OKLINK_BASE = "https://www.oklink.com"
XLAYER_SHORT = "XLAYER"


def _oklink_headers() -> dict:
    key = os.getenv("OKLINK_API_KEY", "")
    return {"Ok-Access-Key": key} if key else {}


def _safe_float(v, default: float = 0.0) -> float:
    try:
        return float(v) if v is not None else default
    except (ValueError, TypeError):
        return default


async def get_address_info(address: str) -> dict:
    """
    MCP Tool: get_address_info
    Returns address entity label, balance, tx count, first/last tx time via OKLink.
    """
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            r = await client.get(
                f"{OKLINK_BASE}/api/v5/explorer/address/information-evm",
                params={"chainShortName": XLAYER_SHORT, "address": address},
                headers=_oklink_headers(),
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            d = data["data"][0]
            return {
                "success": True,
                "address": address,
                "chain": "X Layer",
                "balance_okb": d.get("balance", "0"),
                "balance_usd": d.get("balanceSymbol", ""),
                "tx_count": d.get("transactionCount", 0),
                "transfer_count": d.get("transferCount", 0),
                "token_count": d.get("tokenAmount", 0),
                "first_tx_time": d.get("firstTransactionTime", ""),
                "last_tx_time": d.get("lastTransactionTime", ""),
                "is_contract": d.get("isContract", False),
                "contract_name": d.get("contractName", ""),
                "entity_tag": d.get("entityTag", ""),
            }
        return {"success": False, "error": data.get("msg", "API error")}
    except Exception as e:
        logger.error(f"get_address_info error: {e}")
        return {"success": False, "error": str(e)}


async def get_token_transfers(address: str, token_contract: str = "", limit: int = 20) -> dict:
    """
    MCP Tool: get_token_transfers
    Returns ERC-20 token transfer history for a wallet via OKLink.
    """
    params = {
        "chainShortName": XLAYER_SHORT,
        "address": address,
        "limit": str(min(limit, 100)),
    }
    if token_contract:
        params["tokenContractAddress"] = token_contract
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{OKLINK_BASE}/api/v5/explorer/address/token-transfer-list",
                params=params,
                headers=_oklink_headers(),
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            transfers = data["data"][0].get("tokenTransferDetails", [])
            return {
                "success": True,
                "address": address,
                "chain": "X Layer",
                "transfer_count": len(transfers),
                "transfers": [
                    {
                        "tx_hash": t.get("txId", ""),
                        "block": t.get("height", ""),
                        "timestamp": t.get("transactionTime", ""),
                        "from": t.get("from", ""),
                        "to": t.get("to", ""),
                        "amount": t.get("amount", "0"),
                        "symbol": t.get("tokenContractAddress", ""),
                        "token_name": t.get("symbol", ""),
                    }
                    for t in transfers
                ],
            }
        return {"success": False, "error": data.get("msg", "API error"), "transfers": []}
    except Exception as e:
        logger.error(f"get_token_transfers error: {e}")
        return {"success": False, "error": str(e), "transfers": []}


async def get_block_list(limit: int = 10) -> dict:
    """
    MCP Tool: get_block_list
    Returns the most recent blocks on X Layer via OKLink.
    """
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            r = await client.get(
                f"{OKLINK_BASE}/api/v5/explorer/block/block-list",
                params={"chainShortName": XLAYER_SHORT, "limit": str(min(limit, 50))},
                headers=_oklink_headers(),
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            blocks = data["data"][0].get("blockList", [])
            return {
                "success": True,
                "chain": "X Layer",
                "blocks": [
                    {
                        "number": b.get("height", ""),
                        "hash": b.get("hash", ""),
                        "timestamp": b.get("blockTime", ""),
                        "tx_count": b.get("txAmount", 0),
                        "validator": b.get("miner", ""),
                        "gas_used": b.get("gasUsed", "0"),
                        "gas_limit": b.get("gasLimit", "0"),
                    }
                    for b in blocks
                ],
            }
        return {"success": False, "error": data.get("msg", "API error"), "blocks": []}
    except Exception as e:
        logger.error(f"get_block_list error: {e}")
        return {"success": False, "error": str(e), "blocks": []}


async def get_block_detail(block_number: str) -> dict:
    """
    MCP Tool: get_block_detail
    Returns full details for a specific block on X Layer via OKLink.
    """
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            r = await client.get(
                f"{OKLINK_BASE}/api/v5/explorer/block/block-detail",
                params={"chainShortName": XLAYER_SHORT, "height": block_number},
                headers=_oklink_headers(),
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            d = data["data"][0]
            return {
                "success": True,
                "chain": "X Layer",
                "number": d.get("height", ""),
                "hash": d.get("hash", ""),
                "parent_hash": d.get("parentHash", ""),
                "timestamp": d.get("blockTime", ""),
                "tx_count": d.get("txAmount", 0),
                "validator": d.get("miner", ""),
                "gas_used": d.get("gasUsed", "0"),
                "gas_limit": d.get("gasLimit", "0"),
                "gas_utilization_pct": round(
                    _safe_float(d.get("gasUsed")) / max(_safe_float(d.get("gasLimit")), 1) * 100, 2
                ),
                "base_fee": d.get("baseFeePerGas", "0"),
                "size_bytes": d.get("size", 0),
            }
        return {"success": False, "error": data.get("msg", "API error")}
    except Exception as e:
        logger.error(f"get_block_detail error: {e}")
        return {"success": False, "error": str(e)}


async def get_pending_transactions(address: str = "", limit: int = 20) -> dict:
    """
    MCP Tool: get_pending_transactions
    Returns unconfirmed/pending transactions on X Layer mempool via OKLink.
    """
    params = {"chainShortName": XLAYER_SHORT, "limit": str(min(limit, 100))}
    if address:
        params["address"] = address
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            r = await client.get(
                f"{OKLINK_BASE}/api/v5/explorer/transaction/unconfirmed-list",
                params=params,
                headers=_oklink_headers(),
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            txs = data["data"][0].get("transactionList", [])
            return {
                "success": True,
                "chain": "X Layer",
                "pending_count": len(txs),
                "transactions": [
                    {
                        "hash": t.get("txId", ""),
                        "from": t.get("from", ""),
                        "to": t.get("to", ""),
                        "value": t.get("amount", "0"),
                        "gas_price": t.get("gasPrice", "0"),
                        "nonce": t.get("nonce", ""),
                        "submitted_at": t.get("transactionTime", ""),
                    }
                    for t in txs
                ],
            }
        return {"success": False, "error": data.get("msg", "API error"), "transactions": []}
    except Exception as e:
        logger.error(f"get_pending_transactions error: {e}")
        return {"success": False, "error": str(e), "transactions": []}


async def get_contract_info(contract_address: str) -> dict:
    """
    MCP Tool: get_contract_info
    Returns contract verification status, ABI availability, creator, deploy TX via OKLink.
    """
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            r = await client.get(
                f"{OKLINK_BASE}/api/v5/explorer/contract/information",
                params={"chainShortName": XLAYER_SHORT, "contractAddress": contract_address},
                headers=_oklink_headers(),
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            d = data["data"][0]
            return {
                "success": True,
                "chain": "X Layer",
                "address": contract_address,
                "is_verified": d.get("isVerified", False),
                "contract_name": d.get("contractName", ""),
                "compiler_version": d.get("compilerVersion", ""),
                "creator": d.get("deployAddress", ""),
                "deploy_tx": d.get("deployTxHash", ""),
                "deploy_time": d.get("deployTime", ""),
                "license": d.get("licenseType", ""),
                "proxy": d.get("proxyAddress", ""),
            }
        return {"success": False, "error": data.get("msg", "API error")}
    except Exception as e:
        logger.error(f"get_contract_info error: {e}")
        return {"success": False, "error": str(e)}


async def estimate_gas(to: str, data: str = "0x", value: str = "0") -> dict:
    """
    MCP Tool: estimate_gas
    Estimates gas cost for a transaction on X Layer via OKLink.
    """
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            r = await client.get(
                f"{OKLINK_BASE}/api/v5/explorer/gas/estimation",
                params={
                    "chainShortName": XLAYER_SHORT,
                    "to": to,
                    "txData": data,
                    "value": value,
                },
                headers=_oklink_headers(),
            )
            resp = r.json()
        if resp.get("code") == "0" and resp.get("data"):
            d = resp["data"][0]
            return {
                "success": True,
                "chain": "X Layer",
                "gas_limit": d.get("gasLimit", "21000"),
                "gas_price_gwei": d.get("gasPrice", "0"),
                "estimated_cost_okb": d.get("txFee", "0"),
                "estimated_cost_usd": d.get("txFeeUsd", "0"),
            }
        return {"success": False, "error": resp.get("msg", "API error")}
    except Exception as e:
        logger.error(f"estimate_gas error: {e}")
        return {"success": False, "error": str(e)}


async def get_token_transfer_list(token_contract: str, limit: int = 20) -> dict:
    """
    MCP Tool: get_token_transfer_list
    Returns all recent transfers for a specific token contract on X Layer via OKLink.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{OKLINK_BASE}/api/v5/explorer/token/transaction-list",
                params={
                    "chainShortName": XLAYER_SHORT,
                    "tokenContractAddress": token_contract,
                    "limit": str(min(limit, 100)),
                },
                headers=_oklink_headers(),
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            txs = data["data"][0].get("transactionList", [])
            return {
                "success": True,
                "chain": "X Layer",
                "token_contract": token_contract,
                "transfer_count": len(txs),
                "transfers": [
                    {
                        "tx_hash": t.get("txId", ""),
                        "block": t.get("height", ""),
                        "timestamp": t.get("transactionTime", ""),
                        "from": t.get("from", ""),
                        "to": t.get("to", ""),
                        "amount": t.get("amount", "0"),
                        "symbol": t.get("symbol", ""),
                    }
                    for t in txs
                ],
            }
        return {"success": False, "error": data.get("msg", "API error"), "transfers": []}
    except Exception as e:
        logger.error(f"get_token_transfer_list error: {e}")
        return {"success": False, "error": str(e), "transfers": []}


async def get_rich_list(token_contract: str = "", limit: int = 20) -> dict:
    """
    MCP Tool: get_rich_list
    Returns top holders (rich list) for OKB or any token on X Layer via OKLink.
    """
    params = {
        "chainShortName": XLAYER_SHORT,
        "limit": str(min(limit, 50)),
    }
    if token_contract:
        params["tokenContractAddress"] = token_contract
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{OKLINK_BASE}/api/v5/explorer/token/position-list",
                params=params,
                headers=_oklink_headers(),
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            d = data["data"][0]
            holders = d.get("positionList", [])
            return {
                "success": True,
                "chain": "X Layer",
                "token": token_contract or "OKB (native)",
                "holder_count": d.get("holderCount", 0),
                "top_holders": [
                    {
                        "rank": idx + 1,
                        "address": h.get("holderAddress", ""),
                        "balance": h.get("holdingAmount", "0"),
                        "pct_of_supply": h.get("proportion", "0"),
                        "is_contract": h.get("isContract", False),
                    }
                    for idx, h in enumerate(holders)
                ],
            }
        return {"success": False, "error": data.get("msg", "API error"), "top_holders": []}
    except Exception as e:
        logger.error(f"get_rich_list error: {e}")
        return {"success": False, "error": str(e), "top_holders": []}


async def get_internal_transactions(tx_hash: str) -> dict:
    """
    MCP Tool: get_internal_transactions
    Returns internal contract calls (traces) for a transaction on X Layer via OKLink.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{OKLINK_BASE}/api/v5/explorer/transaction/internal-transaction-detail",
                params={"chainShortName": XLAYER_SHORT, "txId": tx_hash},
                headers=_oklink_headers(),
            )
            data = r.json()
        if data.get("code") == "0" and data.get("data"):
            calls = data["data"][0].get("internalTransactionDetails", [])
            return {
                "success": True,
                "chain": "X Layer",
                "tx_hash": tx_hash,
                "internal_call_count": len(calls),
                "calls": [
                    {
                        "from": c.get("from", ""),
                        "to": c.get("to", ""),
                        "value": c.get("amount", "0"),
                        "type": c.get("operation", ""),
                        "gas_limit": c.get("gasLimit", "0"),
                        "input": c.get("methodId", ""),
                    }
                    for c in calls
                ],
            }
        return {"success": False, "error": data.get("msg", "API error"), "calls": []}
    except Exception as e:
        logger.error(f"get_internal_transactions error: {e}")
        return {"success": False, "error": str(e), "calls": []}
