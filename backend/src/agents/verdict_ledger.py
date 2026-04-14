"""
AXON — VerdictLedger On-Chain Publisher
========================================
Publishes security scan results to AxonVerdictLedger.sol on X Layer.

Every call to scan_token_security() fires a fire-and-forget background task
that encodes + signs + broadcasts a publishVerdict(token, risk, flags, hash)
transaction.  Failures are logged but never propagate to the caller.

Environment variables required:
  VERDICT_LEDGER_ADDRESS  — deployed contract address on X Layer
  ORACLE_PRIVATE_KEY      — 0x-prefixed private key of the AXON oracle wallet

Optional:
  XLAYER_RPC_URL          — default: https://rpc.xlayer.tech
"""

import hashlib
import json
import logging
import os
import struct
import time
from typing import Optional

import httpx

logger = logging.getLogger("axon.verdict_ledger")

XLAYER_RPC = os.getenv("XLAYER_RPC_URL", "https://rpc.xlayer.tech")
CONTRACT_ADDRESS = os.getenv("VERDICT_LEDGER_ADDRESS", "").strip()
ORACLE_PRIVATE_KEY = os.getenv("ORACLE_PRIVATE_KEY", "").strip()

# publishVerdict(address,uint8,uint16,bytes32) selector
# keccak256("publishVerdict(address,uint8,uint16,bytes32)")[:4]
_PUBLISH_SELECTOR = bytes.fromhex("7a6c4289")

# In-memory nonce tracker to avoid re-fetching (single-threaded asyncio safe)
_nonce_cache: dict = {"value": -1, "ts": 0}


def _is_configured() -> bool:
    return bool(CONTRACT_ADDRESS and ORACLE_PRIVATE_KEY)


def _build_calldata(token: str, risk: int, flags: int, data_hash: bytes) -> bytes:
    """
    ABI-encode publishVerdict(address token, uint8 risk, uint16 flags, bytes32 hash).
    All four args are padded to 32 bytes (EVM ABI standard).
    """
    # address → right-padded to 32 bytes (left-zero-padded)
    token_clean = token.lower().removeprefix("0x")
    token_bytes = bytes.fromhex(token_clean.zfill(64))

    # uint8 → 32-byte big-endian
    risk_bytes = risk.to_bytes(32, "big")

    # uint16 → 32-byte big-endian
    flags_bytes = flags.to_bytes(32, "big")

    # bytes32 → already 32 bytes
    assert len(data_hash) == 32, "data_hash must be exactly 32 bytes"

    return _PUBLISH_SELECTOR + token_bytes + risk_bytes + flags_bytes + data_hash


async def _rpc(method: str, params: list) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(
            XLAYER_RPC,
            json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        )
        data = r.json()
    if "error" in data:
        raise RuntimeError(f"RPC {method}: {data['error']}")
    return data["result"]


async def _get_nonce(address: str) -> int:
    """Return cached nonce, refresh if stale (>10s) or first call."""
    global _nonce_cache
    if time.time() - _nonce_cache["ts"] > 10 or _nonce_cache["value"] < 0:
        raw = await _rpc("eth_getTransactionCount", [address, "pending"])
        _nonce_cache = {"value": int(raw, 16), "ts": time.time()}
    n = _nonce_cache["value"]
    _nonce_cache["value"] += 1  # optimistic increment
    return n


async def publish_verdict(
    token_address: str,
    risk_score: int,
    flag_count: int,
    full_report: dict,
) -> Optional[str]:
    """
    Sign and broadcast publishVerdict() to AxonVerdictLedger.
    Returns tx_hash on success, None on failure or if not configured.

    Designed to be called as asyncio.create_task() — non-blocking.
    """
    if not _is_configured():
        return None

    try:
        from eth_account import Account

        acct = Account.from_key(ORACLE_PRIVATE_KEY)

        # data_hash = keccak256 of the full JSON report (deterministic)
        report_json = json.dumps(full_report, sort_keys=True, separators=(",", ":"))
        data_hash = hashlib.sha3_256(report_json.encode()).digest()  # 32 bytes

        calldata = _build_calldata(
            token=token_address,
            risk=int(risk_score),
            flags=int(flag_count),
            data_hash=data_hash,
        )

        nonce = await _get_nonce(acct.address)
        gas_price_hex = await _rpc("eth_gasPrice", [])
        gas_price = int(gas_price_hex, 16)

        from eth_utils import to_checksum_address
        tx = {
            "nonce": nonce,
            "to": to_checksum_address(CONTRACT_ADDRESS),
            "data": "0x" + calldata.hex(),
            "gas": 120_000,       # publishVerdict costs ~60k gas
            "gasPrice": gas_price,
            "chainId": 196,       # X Layer Mainnet
            "value": 0,
        }
        signed = acct.sign_transaction(tx)
        tx_hash = await _rpc("eth_sendRawTransaction", ["0x" + signed.raw_transaction.hex()])

        logger.info(
            f"VerdictLedger: published verdict for {token_address[:10]}... "
            f"risk={risk_score} flags={flag_count} tx={tx_hash[:18]}..."
        )
        return tx_hash

    except ImportError:
        logger.warning("eth-account not installed — skipping on-chain verdict publish")
        return None
    except Exception as e:
        logger.warning(f"VerdictLedger publish failed (non-critical): {e}")
        return None


async def get_onchain_verdict(token_address: str) -> Optional[dict]:
    """
    Read the latest verdict for a token from the contract.
    Uses eth_call to getVerdict(address).
    """
    if not CONTRACT_ADDRESS:
        return None
    try:
        # getVerdict(address) selector
        selector = bytes.fromhex("5d9d40fe")
        token_clean = token_address.lower().removeprefix("0x").zfill(64)
        calldata = "0x" + selector.hex() + token_clean

        raw = await _rpc("eth_call", [{"to": CONTRACT_ADDRESS, "data": calldata}, "latest"])
        if not raw or raw == "0x":
            return None

        data = bytes.fromhex(raw[2:])
        if len(data) < 128:
            return None

        # Decode: uint8(32), uint32(32), uint16(32), bytes32(32)
        risk_score = int.from_bytes(data[0:32], "big")
        timestamp  = int.from_bytes(data[32:64], "big")
        flag_count = int.from_bytes(data[64:96], "big")
        data_hash  = data[96:128].hex()

        return {
            "token": token_address,
            "risk_score": risk_score,
            "timestamp": timestamp,
            "flag_count": flag_count,
            "data_hash": "0x" + data_hash,
            "contract": CONTRACT_ADDRESS,
            "explorer": f"https://www.oklink.com/xlayer/address/{CONTRACT_ADDRESS}",
        }
    except Exception as e:
        logger.debug(f"getVerdict failed: {e}")
        return None


CONFIDENCE_BOND_ADDRESS = os.getenv("CONFIDENCE_BOND_ADDRESS", "0xe164011de202eb0ebf5f01ee5d9851c801a9c675").strip()

# lockBond(address) selector — keccak256("lockBond(address)")[:4]
_LOCK_BOND_SELECTOR = bytes.fromhex("5adda9d2")

# BOND_AMOUNT_WEI must match what was set in the constructor (0.001 OKB)
_BOND_AMOUNT_WEI = 1_000_000_000_000_000


async def lock_bond(token_address: str) -> Optional[str]:
    """
    Call lockBond(token) on AxonConfidenceBond, sending BOND_AMOUNT_WEI as msg.value.
    Only called after a SAFE verdict (risk < 20) has been published to VerdictLedger.
    Returns tx_hash or None. Fire-and-forget — never raises.
    """
    if not (CONFIDENCE_BOND_ADDRESS and ORACLE_PRIVATE_KEY):
        return None
    try:
        from eth_account import Account

        from eth_utils import to_checksum_address
        acct = Account.from_key(ORACLE_PRIVATE_KEY)
        token_clean = token_address.lower().removeprefix("0x").zfill(64)
        calldata = "0x" + _LOCK_BOND_SELECTOR.hex() + token_clean

        nonce = await _get_nonce(acct.address)
        gas_price = int(await _rpc("eth_gasPrice", []), 16)

        tx = {
            "nonce": nonce,
            "to": to_checksum_address(CONFIDENCE_BOND_ADDRESS),
            "data": calldata,
            "gas": 120_000,
            "gasPrice": gas_price,
            "chainId": 196,
            "value": _BOND_AMOUNT_WEI,
        }
        signed = acct.sign_transaction(tx)
        tx_hash = await _rpc("eth_sendRawTransaction", ["0x" + signed.raw_transaction.hex()])
        logger.info(f"ConfidenceBond: locked bond for {token_address[:10]}... tx={tx_hash[:18]}...")
        return tx_hash
    except ImportError:
        logger.warning("eth-account not installed — skipping bond lock")
        return None
    except Exception as e:
        logger.warning(f"ConfidenceBond lockBond failed (non-critical): {e}")
        return None


async def get_total_verdicts() -> int:
    """Returns scannedTokens.length from the contract."""
    if not CONTRACT_ADDRESS:
        return 0
    try:
        # totalVerdicts() selector
        selector = "0x09e985ab"
        raw = await _rpc("eth_call", [{"to": CONTRACT_ADDRESS, "data": selector}, "latest"])
        return int(raw, 16) if raw and raw != "0x" else 0
    except Exception:
        return 0
