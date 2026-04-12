import base64
import json

from src.features import _keyword_fallback as _detect_intent, _extract_tx_hash


def test_extract_tx_hash_accepts_raw_hash():
    tx_hash = "0x" + "ab" * 32
    assert _extract_tx_hash(tx_hash) == tx_hash


def test_extract_tx_hash_accepts_base64_json_payload():
    tx_hash = "0x" + "cd" * 32
    payload = base64.b64encode(json.dumps({"tx": tx_hash}).encode("utf-8")).decode("utf-8")
    assert _extract_tx_hash(payload) == tx_hash


def test_detect_intent_routes_security_queries_to_scanner():
    token = "0x" + "12" * 20
    tool_name, args = _detect_intent(f"Is this token a scam? {token}")
    assert tool_name == "scan_token_security"
    assert args == {"token_address": token}


def test_detect_intent_routes_generic_gas_queries():
    tool_name, args = _detect_intent("What is the gas price right now on X Layer?")
    assert tool_name == "get_gas_price"
    assert args == {}
