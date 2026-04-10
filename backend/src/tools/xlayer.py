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


async def verify_tx_on_xlayer(
    tx_hash: str,
    expected_recipient: str,
    min_amount_okb: float = 0.0,
) -> dict:
    """
    Verify a transaction on X Layer via OKLink explorer API.
    Falls back to direct RPC eth_getTransactionReceipt.

    Returns:
        {
          "valid": bool,
          "reason": str,         # why it failed (if valid=False)
          "tx_hash": str,
          "from": str,
          "to": str,
          "value_okb": float,
          "status": int,         # 1=success 0=reverted
          "block": int,
          "source": str,         # "oklink" | "rpc"
        }
    """
    if not tx_hash or len(tx_hash) < 10:
        return {"valid": False, "reason": "tx_hash missing or too short", "tx_hash": tx_hash}

    # Normalise hash — pad if needed
    if not tx_hash.startswith("0x"):
        tx_hash = "0x" + tx_hash

    # ── Primary: OKLink transaction fills API ──────────────────────────────
    try:
        headers = {"Ok-Access-Key": OKLINK_API_KEY} if OKLINK_API_KEY else {}
        params = {"chainShortName": "XLAYER", "txid": tx_hash}

        async with httpx.AsyncClient(timeout=18.0) as client:
            r = await client.get(
                f"{OKLINK_BASE}/transaction/transaction-fills",
                params=params,
                headers=headers,
            )
            data = r.json()

        if data.get("code") == "0" and data.get("data"):
            tx = data["data"][0]

            status = 1 if tx.get("state", "").lower() == "success" else 0
            to_addr = (tx.get("to") or "").lower()
            from_addr = (tx.get("from") or "").lower()
            # OKLink returns amount in token units (OKB)
            amount_str = tx.get("amount") or tx.get("transactionValue") or "0"
            try:
                value_okb = float(amount_str)
            except ValueError:
                value_okb = 0.0

            block_height = int(tx.get("height") or tx.get("blockHeight") or 0)

            result = {
                "tx_hash": tx_hash,
                "from": from_addr,
                "to": to_addr,
                "value_okb": value_okb,
                "status": status,
                "block": block_height,
                "source": "oklink",
            }

            # Validation checks
            if status != 1:
                return {**result, "valid": False, "reason": "Transaction reverted or pending"}

            if expected_recipient and to_addr != expected_recipient.lower():
                return {**result,
                        "valid": False,
                        "reason": f"Wrong recipient: expected {expected_recipient}, got {to_addr}"}

            if value_okb < min_amount_okb:
                return {**result,
                        "valid": False,
                        "reason": f"Insufficient amount: need {min_amount_okb} OKB, got {value_okb} OKB"}

            return {**result, "valid": True, "reason": ""}

    except Exception as e:
        logger.warning(f"OKLink tx verify failed ({e}), falling back to RPC")

    # ── Fallback: direct RPC eth_getTransactionReceipt ─────────────────────
    try:
        receipt_result = await _rpc_call("eth_getTransactionReceipt", [tx_hash])
        receipt = receipt_result.get("result")

        if not receipt:
            # Try eth_getTransactionByHash (pending/unmined)
            tx_result = await _rpc_call("eth_getTransactionByHash", [tx_hash])
            tx = tx_result.get("result")
            if not tx:
                return {
                    "valid": False,
                    "reason": "Transaction not found on X Layer",
                    "tx_hash": tx_hash,
                    "source": "rpc",
                }
            return {
                "valid": False,
                "reason": "Transaction is pending (not yet mined)",
                "tx_hash": tx_hash,
                "source": "rpc",
            }

        status = int(receipt.get("status", "0x0"), 16)
        to_addr = (receipt.get("to") or "").lower()
        block_num = int(receipt.get("blockNumber", "0x0"), 16)

        # Get value from the original tx (receipt doesn't include value)
        tx_result = await _rpc_call("eth_getTransactionByHash", [tx_hash])
        tx = tx_result.get("result") or {}
        value_wei = int(tx.get("value", "0x0"), 16)
        value_okb = value_wei / 1e18
        from_addr = (tx.get("from") or "").lower()

        result = {
            "tx_hash": tx_hash,
            "from": from_addr,
            "to": to_addr,
            "value_okb": round(value_okb, 8),
            "status": status,
            "block": block_num,
            "source": "rpc",
        }

        if status != 1:
            return {**result, "valid": False, "reason": "Transaction reverted"}

        if expected_recipient and to_addr != expected_recipient.lower():
            return {**result,
                    "valid": False,
                    "reason": f"Wrong recipient: expected {expected_recipient}, got {to_addr}"}

        if value_okb < min_amount_okb:
            return {**result,
                    "valid": False,
                    "reason": f"Insufficient: need {min_amount_okb} OKB, sent {value_okb} OKB"}

        return {**result, "valid": True, "reason": ""}

    except Exception as e:
        logger.error(f"RPC tx verify failed: {e}")
        return {
            "valid": False,
            "reason": f"Verification error: {str(e)}",
            "tx_hash": tx_hash,
            "source": "error",
        }


async def get_xlayer_stats() -> dict:
    """
    MCP Tool: get_xlayer_stats
    Returns X Layer chain statistics and metadata.
    """
    try:
        gas_result, block_result = await __import__("asyncio").gather(
            get_gas_price(), get_block_info("latest"), return_exceptions=False
        )
        return {
            "success": True,
            "chain": "X Layer",
            "chain_id": XLAYER_CHAIN_ID,
            "native_token": "OKB",
            "rpc_url": XLAYER_RPC,
            "explorer": "https://www.oklink.com/xlayer",
            "bridge": "https://www.okx.com/xlayer/bridge",
            "gas_price_gwei": gas_result.get("gas_price_gwei", 0),
            "latest_block": block_result.get("block_number", 0),
            "gas_utilization_pct": block_result.get("gas_utilization_pct", 0),
            "ecosystem": {
                "dex": "Uniswap V3",
                "data": "Onchain OS by OKX",
                "indexer": "The Graph",
            },
        }
    except Exception as e:
        logger.error(f"get_xlayer_stats error: {e}")
        return {"success": False, "error": str(e)}
