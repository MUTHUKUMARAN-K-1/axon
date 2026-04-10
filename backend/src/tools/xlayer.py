"""
AXON — X Layer Direct RPC Tools
Direct JSON-RPC calls to X Layer for gas, block, and contract data.
"""

import httpx
import logging
import os
from typing import Optional

logger = logging.getLogger("axon.tools.xlayer")

XLAYER_RPC = os.getenv("XLAYER_RPC_URL", "https://rpc.xlayer.tech")
XLAYER_CHAIN_ID = 196
OKLINK_BASE = "https://www.oklink.com/api/v5/explorer"
OKLINK_API_KEY = os.getenv("OKLINK_API_KEY", "")


async def _rpc_call(method: str, params: list) -> dict:
    """Execute a JSON-RPC call to X Layer."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            XLAYER_RPC,
            json={"jsonrpc": "2.0", "method": method, "params": params, "id": 1},
        )
        return r.json()


async def get_gas_price() -> dict:
    """
    MCP Tool: get_gas_price
    Returns current gas price on X Layer in gwei.
    """
    try:
        result = await _rpc_call("eth_gasPrice", [])
        gas_hex = result.get("result", "0x0")
        gas_wei = int(gas_hex, 16)
        gas_gwei = gas_wei / 1e9

        # Also get max priority fee
        prio_result = await _rpc_call("eth_maxPriorityFeePerGas", [])
        prio_hex = prio_result.get("result", "0x0")
        prio_gwei = int(prio_hex, 16) / 1e9

        return {
            "success": True,
            "chain": "X Layer",
            "gas_price_gwei": round(gas_gwei, 4),
            "max_priority_fee_gwei": round(prio_gwei, 4),
            "gas_price_wei": gas_wei,
            "estimated_transfer_cost_usd": round(gas_gwei * 21000 / 1e9 * 50, 6),  # rough OKB price
        }
    except Exception as e:
        logger.error(f"get_gas_price error: {e}")
        return {"success": False, "error": str(e)}


async def get_block_info(block: str = "latest") -> dict:
    """
    MCP Tool: get_block_info
    Returns latest block info from X Layer.
    """
    try:
        result = await _rpc_call("eth_getBlockByNumber", [block, False])
        b = result.get("result", {})
        if not b:
            return {"success": False, "error": "Block not found"}

        return {
            "success": True,
            "chain": "X Layer",
            "block_number": int(b.get("number", "0x0"), 16),
            "timestamp": int(b.get("timestamp", "0x0"), 16),
            "tx_count": len(b.get("transactions", [])),
            "gas_used": int(b.get("gasUsed", "0x0"), 16),
            "gas_limit": int(b.get("gasLimit", "0x0"), 16),
            "gas_utilization_pct": round(
                int(b.get("gasUsed", "0x0"), 16) / max(int(b.get("gasLimit", "0x1"), 16), 1) * 100, 2
            ),
            "base_fee_gwei": round(int(b.get("baseFeePerGas", "0x0"), 16) / 1e9, 4),
            "miner": b.get("miner", ""),
            "hash": b.get("hash", ""),
        }
    except Exception as e:
        logger.error(f"get_block_info error: {e}")
        return {"success": False, "error": str(e)}


async def get_wallet_balance(address: str) -> dict:
    """
    MCP Tool: get_native_balance
    Returns native OKB balance for a wallet on X Layer.
    """
    try:
        result = await _rpc_call("eth_getBalance", [address, "latest"])
        balance_hex = result.get("result", "0x0")
        balance_wei = int(balance_hex, 16)
        balance_okb = balance_wei / 1e18

        return {
            "success": True,
            "address": address,
            "chain": "X Layer",
            "balance_okb": round(balance_okb, 8),
            "balance_wei": balance_wei,
            "token": "OKB",
        }
    except Exception as e:
        logger.error(f"get_wallet_balance error: {e}")
        return {"success": False, "error": str(e)}


async def get_contract_code(address: str) -> dict:
    """
    MCP Tool: get_contract_code
    Checks if an address is a contract on X Layer.
    """
    try:
        result = await _rpc_call("eth_getCode", [address, "latest"])
        code = result.get("result", "0x")
        is_contract = len(code) > 2  # "0x" = EOA, longer = contract

        return {
            "success": True,
            "address": address,
            "chain": "X Layer",
            "is_contract": is_contract,
            "bytecode_size": (len(code) - 2) // 2 if is_contract else 0,
        }
    except Exception as e:
        logger.error(f"get_contract_code error: {e}")
        return {"success": False, "error": str(e)}


async def get_oklink_address_summary(address: str) -> dict:
    """
    MCP Tool: get_address_summary
    Returns OKLink explorer summary for an address (tx count, first seen, labels).
    """
    try:
        headers = {"Ok-Access-Key": OKLINK_API_KEY} if OKLINK_API_KEY else {}
        params = {"chainShortName": "xlayer", "address": address}

        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{OKLINK_BASE}/address/address-summary",
                params=params,
                headers=headers,
            )
            data = r.json()

        if data.get("code") == "0":
            info = data.get("data", [{}])[0]
            return {
                "success": True,
                "address": address,
                "chain": "X Layer",
                "tx_count": info.get("transactionCount", "0"),
                "token_tx_count": info.get("tokenTransactionCount", "0"),
                "first_tx_time": info.get("firstTransactionTime", ""),
                "last_tx_time": info.get("lastTransactionTime", ""),
                "is_contract": info.get("isContract", False),
                "contract_name": info.get("contractName", ""),
                "tags": info.get("tag", []),
            }
        else:
            # Fallback to RPC
            return await get_wallet_balance(address)

    except Exception as e:
        logger.error(f"get_oklink_address_summary error: {e}")
        return {"success": False, "error": str(e)}
