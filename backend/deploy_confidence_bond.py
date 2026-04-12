#!/usr/bin/env python3
"""
AXON — Deploy AxonConfidenceBond to X Layer Mainnet
=====================================================
Usage:
    ORACLE_PRIVATE_KEY=0x... python deploy_confidence_bond.py

Requires VERDICT_LEDGER_ADDRESS to be set (already deployed).
Sends BOND_AMOUNT * INITIAL_BONDS OKB as initial funding.
"""

import os, sys, time
import httpx

VERDICT_LEDGER = "0x0191d5ada56672507fdb283ac59d45bde08a53f8"
BOND_AMOUNT_WEI = 1_000_000_000_000_000   # 0.001 OKB per bond (18 decimals)
INITIAL_FUND_BONDS = 50                    # pre-fund for 50 SAFE verdicts = 0.05 OKB


def rpc(method, params, url):
    r = httpx.post(url, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=30)
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"RPC error: {data['error']}")
    return data["result"]


def main():
    from eth_account import Account

    rpc_url = os.getenv("XLAYER_RPC_URL", "https://rpc.xlayer.tech")
    privkey = os.getenv("ORACLE_PRIVATE_KEY", "").strip()
    if not privkey:
        print("ERROR: Set ORACLE_PRIVATE_KEY env var")
        sys.exit(1)

    acct = Account.from_key(privkey)
    print(f"Oracle wallet : {acct.address}")
    print(f"VerdictLedger : {VERDICT_LEDGER}")
    print(f"Bond amount   : {BOND_AMOUNT_WEI / 1e18:.6f} OKB per SAFE verdict")
    print(f"Initial fund  : {BOND_AMOUNT_WEI * INITIAL_FUND_BONDS / 1e18:.4f} OKB ({INITIAL_FUND_BONDS} bonds)")

    bal_hex = rpc("eth_getBalance", [acct.address, "latest"], rpc_url)
    balance = int(bal_hex, 16) / 1e18
    print(f"OKB balance   : {balance:.6f} OKB")

    initial_fund = BOND_AMOUNT_WEI * INITIAL_FUND_BONDS
    if balance * 1e18 < initial_fund + 500_000 * 200_000:  # rough gas check
        print(f"WARNING: Low balance. Need at least {initial_fund/1e18:.4f} OKB + gas.")

    # Compile
    try:
        from solcx import compile_files, install_solc
        install_solc("0.8.20")
        sol_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "contracts", "ConfidenceBond.sol")
        )
        print(f"\nCompiling {sol_path} ...")
        compiled = compile_files(
            [sol_path], output_values=["abi", "bin"],
            solc_version="0.8.20", optimize=True, optimize_runs=200,
        )
        key = next(k for k in compiled if "ConfidenceBond" in k)
        bytecode = compiled[key]["bin"]
        print(f"Bytecode size : {len(bytecode)//2} bytes")
    except ImportError:
        print("ERROR: pip install py-solc-x")
        sys.exit(1)

    # Encode constructor: (address oracle, address verdictLedger, uint256 bondAmountWei)
    oracle_pad  = acct.address[2:].lower().zfill(64)
    ledger_pad  = VERDICT_LEDGER[2:].lower().zfill(64)
    bond_pad    = hex(BOND_AMOUNT_WEI)[2:].zfill(64)
    deploy_data = "0x" + bytecode + oracle_pad + ledger_pad + bond_pad

    nonce     = int(rpc("eth_getTransactionCount", [acct.address, "pending"], rpc_url), 16)
    gas_price = int(rpc("eth_gasPrice", [], rpc_url), 16)
    chain_id  = int(rpc("eth_chainId", [], rpc_url), 16)

    try:
        gas_est = rpc("eth_estimateGas", [{
            "from": acct.address, "data": deploy_data, "value": hex(initial_fund)
        }], rpc_url)
        gas_limit = int(int(gas_est, 16) * 1.3)
    except Exception:
        gas_limit = 900_000

    print(f"Chain ID: {chain_id}  Nonce: {nonce}  Gas: {gas_limit:,}  Gas price: {gas_price/1e9:.4f} gwei")
    print(f"Sending {initial_fund/1e18:.4f} OKB as initial bond fund...")

    tx = {
        "nonce": nonce, "gas": gas_limit, "gasPrice": gas_price,
        "data": deploy_data, "chainId": chain_id, "value": initial_fund,
    }
    signed = acct.sign_transaction(tx)
    tx_hash = rpc("eth_sendRawTransaction", ["0x" + signed.raw_transaction.hex()], rpc_url)
    print(f"\nDeployment tx: {tx_hash}")
    print(f"Explorer: https://www.oklink.com/xlayer/tx/{tx_hash}")
    print("Waiting 30s for confirmation...")
    time.sleep(30)

    receipt = rpc("eth_getTransactionReceipt", [tx_hash], rpc_url)
    if receipt and receipt.get("contractAddress"):
        addr = receipt["contractAddress"]
        print(f"\n✅ ConfidenceBond deployed at: {addr}")
        print(f"   Add to .env:  CONFIDENCE_BOND_ADDRESS={addr}")
        print(f"   Explorer: https://www.oklink.com/xlayer/address/{addr}")
        print(f"   Pre-funded with {initial_fund/1e18:.4f} OKB for {INITIAL_FUND_BONDS} SAFE verdict bonds")
    else:
        print(f"Receipt: {receipt}")


if __name__ == "__main__":
    main()
