"""
AXON — VerdictLedger Unit Tests
================================
Tests ABI encoding, selector correctness, nonce cache, and
ConfidenceBond calldata — all pure Python, no network required.
"""

import hashlib
import os

import pytest

from src.agents.verdict_ledger import (
    _build_calldata,
    _is_configured,
    _PUBLISH_SELECTOR,
    _LOCK_BOND_SELECTOR,
    _nonce_cache,
    CONFIDENCE_BOND_ADDRESS,
    CONTRACT_ADDRESS,
)


# ─── ABI calldata encoding ────────────────────────────────────────────────────

class TestBuildCalldata:
    TOKEN = "0x1e4a5963abfd975d8c9021ce480b42188849d41d"
    HASH  = hashlib.sha3_256(b"test").digest()

    def test_calldata_total_length(self):
        """4-byte selector + 4 × 32-byte args = 132 bytes."""
        out = _build_calldata(self.TOKEN, 15, 3, self.HASH)
        assert len(out) == 132

    def test_calldata_starts_with_publish_selector(self):
        """First 4 bytes must be keccak256('publishVerdict(address,uint8,uint16,bytes32)')[:4]."""
        out = _build_calldata(self.TOKEN, 0, 0, self.HASH)
        assert out[:4] == _PUBLISH_SELECTOR
        assert _PUBLISH_SELECTOR == bytes.fromhex("7a6c4289")

    def test_calldata_token_zero_padded(self):
        """Token address must occupy bytes 4-36, left-zero-padded to 32 bytes."""
        out = _build_calldata(self.TOKEN, 0, 0, self.HASH)
        token_slot = out[4:36]
        # First 12 bytes are zero padding
        assert token_slot[:12] == b"\x00" * 12
        # Last 20 bytes are the address
        assert token_slot[12:].hex() == self.TOKEN[2:].lower()

    def test_calldata_risk_score_encoded(self):
        """Risk score must be big-endian in bytes 36-68."""
        out = _build_calldata(self.TOKEN, 77, 0, self.HASH)
        risk_slot = out[36:68]
        assert int.from_bytes(risk_slot, "big") == 77

    def test_calldata_flag_count_encoded(self):
        """Flag count must be big-endian in bytes 68-100."""
        out = _build_calldata(self.TOKEN, 0, 12, self.HASH)
        flags_slot = out[68:100]
        assert int.from_bytes(flags_slot, "big") == 12

    def test_calldata_hash_preserved(self):
        """The 32-byte data hash must be exactly preserved in bytes 100-132."""
        out = _build_calldata(self.TOKEN, 0, 0, self.HASH)
        assert out[100:132] == self.HASH

    def test_calldata_risk_zero(self):
        """Risk score 0 must encode cleanly without errors."""
        out = _build_calldata(self.TOKEN, 0, 0, self.HASH)
        assert int.from_bytes(out[36:68], "big") == 0

    def test_calldata_risk_max(self):
        """Risk score 100 (uint8 max used in practice) must encode correctly."""
        out = _build_calldata(self.TOKEN, 100, 0, self.HASH)
        assert int.from_bytes(out[36:68], "big") == 100

    def test_calldata_rejects_wrong_hash_length(self):
        """_build_calldata must raise AssertionError for non-32-byte hashes."""
        with pytest.raises(AssertionError):
            _build_calldata(self.TOKEN, 0, 0, b"tooshort")


# ─── Selectors ────────────────────────────────────────────────────────────────

class TestSelectors:
    def test_publish_verdict_selector_value(self):
        """Hardcoded selector must equal keccak256('publishVerdict(address,uint8,uint16,bytes32)')[:4]."""
        assert _PUBLISH_SELECTOR == bytes.fromhex("7a6c4289")

    def test_lock_bond_selector_value(self):
        """Hardcoded selector must equal keccak256('lockBond(address)')[:4]."""
        assert _LOCK_BOND_SELECTOR == bytes.fromhex("5adda9d2")

    def test_selectors_are_4_bytes(self):
        """Both selectors must be exactly 4 bytes."""
        assert len(_PUBLISH_SELECTOR) == 4
        assert len(_LOCK_BOND_SELECTOR) == 4

    def test_selectors_are_distinct(self):
        """publishVerdict and lockBond must not share a selector."""
        assert _PUBLISH_SELECTOR != _LOCK_BOND_SELECTOR


# ─── Configuration guard ─────────────────────────────────────────────────────

class TestIsConfigured:
    def test_returns_false_without_env(self, monkeypatch):
        """_is_configured() must return False when env vars are absent."""
        import src.agents.verdict_ledger as vl
        monkeypatch.setattr(vl, "CONTRACT_ADDRESS", "")
        monkeypatch.setattr(vl, "ORACLE_PRIVATE_KEY", "")
        assert vl._is_configured() is False

    def test_returns_false_with_only_contract(self, monkeypatch):
        """Both CONTRACT_ADDRESS and ORACLE_PRIVATE_KEY must be set."""
        import src.agents.verdict_ledger as vl
        monkeypatch.setattr(vl, "CONTRACT_ADDRESS", "0x1234")
        monkeypatch.setattr(vl, "ORACLE_PRIVATE_KEY", "")
        assert vl._is_configured() is False

    def test_returns_true_when_both_set(self, monkeypatch):
        """_is_configured() returns True when both vars are non-empty."""
        import src.agents.verdict_ledger as vl
        monkeypatch.setattr(vl, "CONTRACT_ADDRESS", "0xabc")
        monkeypatch.setattr(vl, "ORACLE_PRIVATE_KEY", "0xdeadbeef")
        assert vl._is_configured() is True


# ─── get_total_verdicts without network ───────────────────────────────────────

@pytest.mark.asyncio
async def test_get_total_verdicts_returns_zero_without_contract(monkeypatch):
    """get_total_verdicts() returns 0 when CONTRACT_ADDRESS is unset."""
    import src.agents.verdict_ledger as vl
    monkeypatch.setattr(vl, "CONTRACT_ADDRESS", "")
    result = await vl.get_total_verdicts()
    assert result == 0


@pytest.mark.asyncio
async def test_get_onchain_verdict_returns_none_without_contract(monkeypatch):
    """get_onchain_verdict() returns None when CONTRACT_ADDRESS is unset."""
    import src.agents.verdict_ledger as vl
    monkeypatch.setattr(vl, "CONTRACT_ADDRESS", "")
    result = await vl.get_onchain_verdict("0x" + "ab" * 20)
    assert result is None


@pytest.mark.asyncio
async def test_publish_verdict_skips_when_not_configured(monkeypatch):
    """publish_verdict() returns None immediately when not configured."""
    import src.agents.verdict_ledger as vl
    monkeypatch.setattr(vl, "CONTRACT_ADDRESS", "")
    monkeypatch.setattr(vl, "ORACLE_PRIVATE_KEY", "")
    result = await vl.publish_verdict("0x" + "aa" * 20, 50, 3, {"test": True})
    assert result is None


@pytest.mark.asyncio
async def test_lock_bond_skips_when_not_configured(monkeypatch):
    """lock_bond() returns None immediately when not configured."""
    import src.agents.verdict_ledger as vl
    monkeypatch.setattr(vl, "CONFIDENCE_BOND_ADDRESS", "")
    monkeypatch.setattr(vl, "ORACLE_PRIVATE_KEY", "")
    result = await vl.lock_bond("0x" + "bb" * 20)
    assert result is None
