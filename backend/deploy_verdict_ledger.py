#!/usr/bin/env python3
"""
AXON — Deploy AxonVerdictLedger to X Layer Mainnet
===================================================
Usage:
    pip install eth-account py-solc-x
    ORACLE_PRIVATE_KEY=0x... python deploy_verdict_ledger.py

Requires:
  - ORACLE_PRIVATE_KEY  : private key of the AXON oracle wallet (AXON_AGENT_WALLET)
  - XLAYER_RPC_URL      : X Layer JSON-RPC (default: https://rpc.xlayer.tech)

The script:
  1. Compiles VerdictLedger.sol using the local solc compiler (auto-downloaded)
  2. Sends a deployment transaction from the oracle wallet
  3. Prints the deployed contract address → set as VERDICT_LEDGER_ADDRESS in .env
"""

import json
import os
import sys
import time

import httpx

# ── ABI (manually written — matches VerdictLedger.sol exactly) ───────────────
ABI = [
    {
        "type": "constructor",
        "inputs": [{"name": "_oracle", "type": "address"}],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "publishVerdict",
        "inputs": [
            {"name": "token",  "type": "address"},
            {"name": "risk",   "type": "uint8"},
            {"name": "flags",  "type": "uint16"},
            {"name": "hash",   "type": "bytes32"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "totalVerdicts",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "getVerdict",
        "inputs": [{"name": "token", "type": "address"}],
        "outputs": [
            {"name": "riskScore",  "type": "uint8"},
            {"name": "timestamp",  "type": "uint32"},
            {"name": "flagCount",  "type": "uint16"},
            {"name": "dataHash",   "type": "bytes32"},
        ],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "verdicts",
        "inputs": [{"name": "", "type": "address"}],
        "outputs": [
            {"name": "riskScore",  "type": "uint8"},
            {"name": "timestamp",  "type": "uint32"},
            {"name": "flagCount",  "type": "uint16"},
            {"name": "dataHash",   "type": "bytes32"},
        ],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "scannedTokens",
        "inputs": [{"name": "", "type": "uint256"}],
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "oracle",
        "inputs": [],
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
    },
    {
        "type": "event",
        "name": "VerdictPublished",
        "inputs": [
            {"name": "token",     "type": "address", "indexed": True},
            {"name": "riskScore", "type": "uint8",   "indexed": False},
            {"name": "flagCount", "type": "uint16",  "indexed": False},
            {"name": "dataHash",  "type": "bytes32", "indexed": False},
            {"name": "timestamp", "type": "uint32",  "indexed": False},
        ],
        "anonymous": False,
    },
]


def rpc(method: str, params: list, url: str) -> dict:
    """JSON-RPC call via httpx."""
    r = httpx.post(url, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=30)
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"RPC error: {data['error']}")
    return data["result"]


def main():
    from eth_account import Account
    from eth_account.signers.local import LocalAccount

    rpc_url = os.getenv("XLAYER_RPC_URL", "https://rpc.xlayer.tech")
    privkey = os.getenv("ORACLE_PRIVATE_KEY", "").strip()
    if not privkey:
        print("ERROR: Set ORACLE_PRIVATE_KEY env var (0x-prefixed private key)")
        sys.exit(1)

    acct: LocalAccount = Account.from_key(privkey)
    print(f"Oracle wallet: {acct.address}")

    # Balance check
    balance_hex = rpc("eth_getBalance", [acct.address, "latest"], rpc_url)
    balance_okb = int(balance_hex, 16) / 1e18
    print(f"OKB balance: {balance_okb:.6f} OKB")
    if balance_okb < 0.01:
        print("WARNING: Low OKB balance — deployment may fail. Need ~0.002 OKB for gas.")

    # Compile with py-solc-x
    try:
        from solcx import compile_files, install_solc
        install_solc("0.8.20")
        sol_path = os.path.join(os.path.dirname(__file__), "..", "contracts", "VerdictLedger.sol")
        sol_path = os.path.normpath(sol_path)
        print(f"Compiling {sol_path} ...")
        compiled = compile_files(
            [sol_path],
            output_values=["abi", "bin"],
            solc_version="0.8.20",
            optimize=True,
            optimize_runs=200,
        )
        contract_key = next(k for k in compiled if "VerdictLedger" in k)
        bytecode = compiled[contract_key]["bin"]
        print(f"Bytecode size: {len(bytecode)//2} bytes")
    except ImportError:
        print("ERROR: Install py-solc-x:  pip install py-solc-x")
        sys.exit(1)

    # Encode constructor args: abi.encode(address oracle)
    # address is right-padded to 32 bytes (zero-padded left)
    oracle_padded = acct.address[2:].lower().zfill(64)
    deploy_data = "0x" + bytecode + oracle_padded

    # Get nonce
    nonce_hex = rpc("eth_getTransactionCount", [acct.address, "latest"], rpc_url)
    nonce = int(nonce_hex, 16)

    # Gas estimate
    try:
        gas_est_hex = rpc("eth_estimateGas", [{"from": acct.address, "data": deploy_data}], rpc_url)
        gas_limit = int(int(gas_est_hex, 16) * 1.3)
    except Exception:
        gas_limit = 800_000

    gas_price_hex = rpc("eth_gasPrice", [], rpc_url)
    gas_price = int(gas_price_hex, 16)

    chain_id = int(rpc("eth_chainId", [], rpc_url), 16)
    print(f"Chain ID: {chain_id}  Nonce: {nonce}  Gas limit: {gas_limit:,}  Gas price: {gas_price/1e9:.4f} gwei")

    # Sign deployment tx
    tx = {
        "nonce": nonce,
        "gas": gas_limit,
        "gasPrice": gas_price,
        "data": deploy_data,
        "chainId": chain_id,
        "value": 0,
    }
    signed = acct.sign_transaction(tx)
    tx_hash = rpc("eth_sendRawTransaction", ["0x" + signed.raw_transaction.hex()], rpc_url)
    print(f"\nDeployment tx sent: {tx_hash}")
    print(f"Explorer: https://www.oklink.com/xlayer/tx/{tx_hash}")
    print("Waiting for confirmation (30s)...")
    time.sleep(30)

    receipt = rpc("eth_getTransactionReceipt", [tx_hash], rpc_url)
    if receipt and receipt.get("contractAddress"):
        contract_addr = receipt["contractAddress"]
        print(f"\n✅ VerdictLedger deployed at: {contract_addr}")
        print(f"   Add to .env:  VERDICT_LEDGER_ADDRESS={contract_addr}")
        print(f"   Explorer: https://www.oklink.com/xlayer/address/{contract_addr}")
        # Save ABI
        abi_path = os.path.join(os.path.dirname(__file__), "verdict_ledger_abi.json")
        with open(abi_path, "w") as f:
            json.dump(ABI, f, indent=2)
        print(f"   ABI saved to: {abi_path}")
    else:
        print(f"⚠️  Receipt: {receipt}")
        print("Check the tx on OKLink — deployment may still be confirming.")


if __name__ == "__main__":
    main()
