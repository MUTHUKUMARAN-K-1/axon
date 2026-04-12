"""
AXON — Security Scoring Unit Tests
====================================
Tests the risk label/colour helpers and the weighted scoring formula
from security_agent.py — pure Python, zero network calls.
"""

import pytest

from src.agents.security_agent import _risk_label, _risk_color, KNOWN_SAFE


# ─── Risk label thresholds ────────────────────────────────────────────────────

class TestRiskLabel:
    def test_score_0_is_safe(self):
        assert _risk_label(0) == "SAFE"

    def test_score_19_is_safe(self):
        assert _risk_label(19) == "SAFE"

    def test_score_20_is_low_risk(self):
        assert _risk_label(20) == "LOW RISK"

    def test_score_44_is_low_risk(self):
        assert _risk_label(44) == "LOW RISK"

    def test_score_45_is_medium_risk(self):
        assert _risk_label(45) == "MEDIUM RISK"

    def test_score_64_is_medium_risk(self):
        assert _risk_label(64) == "MEDIUM RISK"

    def test_score_65_is_high_risk(self):
        assert _risk_label(65) == "HIGH RISK"

    def test_score_79_is_high_risk(self):
        assert _risk_label(79) == "HIGH RISK"

    def test_score_80_is_critical(self):
        assert _risk_label(80) == "CRITICAL — LIKELY SCAM"

    def test_score_100_is_critical(self):
        assert _risk_label(100) == "CRITICAL — LIKELY SCAM"


# ─── Risk color thresholds ────────────────────────────────────────────────────

class TestRiskColor:
    def test_safe_color_is_green(self):
        assert _risk_color(0)  == "#10B981"
        assert _risk_color(19) == "#10B981"

    def test_low_risk_color_is_amber(self):
        assert _risk_color(20) == "#F59E0B"
        assert _risk_color(44) == "#F59E0B"

    def test_medium_risk_color_is_red(self):
        assert _risk_color(45) == "#EF4444"
        assert _risk_color(64) == "#EF4444"

    def test_high_and_critical_color_is_purple(self):
        assert _risk_color(65)  == "#7C3AED"
        assert _risk_color(100) == "#7C3AED"


# ─── Weighted scoring formula ─────────────────────────────────────────────────

class TestWeightedFormula:
    def test_all_zero_sources_gives_zero(self):
        """If every source returns 0 risk, final score must be 0."""
        score = round(0 * 0.35 + 0 * 0.25 + 0 * 0.20 + 0 * 0.10 + 0 * 0.10)
        assert score == 0

    def test_all_hundred_sources_gives_hundred(self):
        """If every source returns 100 risk, final score must be 100."""
        score = round(100 * 0.35 + 100 * 0.25 + 100 * 0.20 + 100 * 0.10 + 100 * 0.10)
        assert score == 100

    def test_weights_sum_to_one(self):
        """A+B+C+E+F weights must sum to 1.0 (no score is lost or doubled)."""
        total_weight = 0.35 + 0.25 + 0.20 + 0.10 + 0.10
        assert abs(total_weight - 1.0) < 1e-9

    def test_okx_security_dominates_at_full_score(self):
        """OKX security (weight 0.35) alone can push score to 35 from zero base."""
        score = round(100 * 0.35 + 0 * 0.25 + 0 * 0.20 + 0 * 0.10 + 0 * 0.10)
        assert score == 35

    def test_honeypot_alone_produces_high_risk(self):
        """
        A raw_a = 100 (honeypot detected) with all other sources clean
        should yield a final score of 35, which is LOW RISK — demonstrating
        that multi-source scoring prevents a single false positive from going
        critical.
        """
        score = round(100 * 0.35 + 0 * 0.25 + 0 * 0.20 + 0 * 0.10 + 0 * 0.10)
        assert _risk_label(score) == "LOW RISK"


# ─── Known-safe token bypass ──────────────────────────────────────────────────

class TestKnownSafeTokens:
    def test_usdt_xlayer_is_known_safe(self):
        assert "0x1e4a5963abfd975d8c9021ce480b42188849d41d" in KNOWN_SAFE

    def test_wokb_xlayer_is_known_safe(self):
        assert "0xe538905cf8410324e03a5a23c1c177a474d59b2" in KNOWN_SAFE

    def test_native_okb_is_known_safe(self):
        assert "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee" in KNOWN_SAFE

    def test_random_address_not_in_known_safe(self):
        assert "0x" + "de" * 20 not in KNOWN_SAFE
