"""
AXON Integration Tests
======================
Tests hit the live deployment at axon-onld.onrender.com.
Free MCP endpoints only — no wallet/API key required.

Run with:
    pytest tests/ -v
    pytest tests/ -v --tb=short -x   # stop on first failure
    pytest tests/ -v -k "health"     # run a specific test

Set AXON_TEST_URL to override the base URL:
    AXON_TEST_URL=http://localhost:3000 pytest tests/ -v
"""

import os
import pytest
import httpx

BASE_URL = os.getenv("AXON_TEST_URL", "https://axon-onld.onrender.com")
TIMEOUT   = 30  # seconds — Render cold-start can be slow


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def client():
    """Shared httpx client for the test session."""
    with httpx.Client(base_url=BASE_URL, timeout=TIMEOUT) as c:
        yield c


# ─── Health & Root ─────────────────────────────────────────────────────────────

class TestHealth:
    def test_get_health_returns_ok(self, client):
        """GET /health should return 200 with status=ok."""
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["service"] == "AXON"

    def test_head_health_returns_200(self, client):
        """HEAD /health must succeed — Render uses this as the readiness probe."""
        r = client.head("/health")
        assert r.status_code == 200

    def test_root_exposes_key_metadata(self, client):
        """GET / should expose service name, version, chain info, and endpoint map."""
        r = client.get("/")
        assert r.status_code == 200
        body = r.json()
        assert body["service"] == "AXON"
        assert body["chain"] == "X Layer (Chain ID 196)"
        assert body["x402_enabled"] is True
        assert "chat_endpoint"    in body
        assert "agent_activity"   in body
        assert body["mcp_tools"]  >= 17  # must expose at least 17 tools


# ─── MCP Tool Discovery ────────────────────────────────────────────────────────

class TestMCPTools:
    def test_list_tools_returns_array(self, client):
        """GET /mcp/tools should return a tools array."""
        r = client.get("/mcp/tools")
        assert r.status_code == 200
        body = r.json()
        assert "tools" in body
        assert isinstance(body["tools"], list)

    def test_at_least_17_tools_registered(self, client):
        """AXON must expose all 17 documented MCP tools."""
        r = client.get("/mcp/tools")
        tools = r.json()["tools"]
        assert len(tools) >= 17, f"Expected ≥17 tools, got {len(tools)}"

    def test_tool_schema_has_required_fields(self, client):
        """Each tool must have name and description fields."""
        tools = client.get("/mcp/tools").json()["tools"]
        for tool in tools:
            assert "name"        in tool, f"Tool missing 'name': {tool}"
            assert "description" in tool, f"Tool {tool.get('name')} missing 'description'"

    def test_known_tools_are_present(self, client):
        """Core tools relied on by external agents must always be registered."""
        required = {
            "get_gas_price",
            "get_block_info",
            "get_market_overview",
            "get_uniswap_top_pools",
            "get_wallet_portfolio",
            "get_swap_quote",
            "get_yield_opportunities",
        }
        names = {t["name"] for t in client.get("/mcp/tools").json()["tools"]}
        missing = required - names
        assert not missing, f"Missing tools: {missing}"


# ─── Free MCP Tool Calls ───────────────────────────────────────────────────────

class TestFreeMCPCalls:
    """Call free (non-premium) tools via POST /mcp/call."""

    def _call(self, client, tool: str, args: dict = None) -> dict:
        r = client.post("/mcp/call", json={"tool_name": tool, "arguments": args or {}})
        assert r.status_code == 200, f"{tool} returned {r.status_code}: {r.text[:200]}"
        return r.json()

    def test_get_gas_price_structure(self, client):
        """get_gas_price should return a numeric gwei value for X Layer."""
        body = self._call(client, "get_gas_price")
        result = body["result"]
        assert result["success"] is True
        assert result["chain"] == "X Layer"
        assert isinstance(result["gas_price_gwei"], (int, float))
        assert result["gas_price_gwei"] >= 0

    def test_get_block_info_structure(self, client):
        """get_block_info should return a recent X Layer block number."""
        body = self._call(client, "get_block_info", {"block": "latest"})
        result = body["result"]
        assert result["success"] is True
        assert result["block_number"] > 1_000_000, "Block number suspiciously low"
        assert 0 <= result["gas_utilization_pct"] <= 100

    def test_get_uniswap_top_pools(self, client):
        """get_uniswap_top_pools should return a list of pool dicts."""
        body = self._call(client, "get_uniswap_top_pools", {"limit": 3})
        result = body["result"]
        assert result.get("success") is True
        pools = result.get("pools", [])
        assert isinstance(pools, list)
        # Each pool must have at minimum a pair identifier and TVL
        for pool in pools:
            assert "pair" in pool or "id" in pool, f"Pool missing identifier: {pool}"


# ─── x402 Endpoints ────────────────────────────────────────────────────────────

class TestX402:
    def test_pricing_endpoint_structure(self, client):
        """GET /api/x402/pricing must return payment address, premium tools, and header formats."""
        r = client.get("/api/x402/pricing")
        assert r.status_code == 200
        body = r.json()
        assert body["protocol"] == "x402"
        assert body["payment_asset"] == "OKB"
        assert body["payment_network"] == "X Layer Mainnet (Chain ID 196)"
        assert body["replay_protection"] is True
        assert "premium_tools" in body
        assert "how_to_pay"    in body
        assert "header_formats" in body

    def test_premium_tool_returns_402_without_payment(self, client):
        """Calling a premium tool without X-PAYMENT must return HTTP 402."""
        r = client.post("/mcp/call", json={
            "tool_name": "analyze_wallet",
            "arguments": {"address": "0xDb82c0d91E057E05600C8F8dc836bEb41da6df14"},
        })
        assert r.status_code == 402
        body = r.json()
        assert body["error"] == "Payment Required"
        assert "x402"             in body
        assert "rejection_reason" in body
        # Response headers must follow x402 spec
        assert r.headers.get("X-Payment-Required") == "true"
        assert r.headers.get("X-Payment-Asset")    == "OKB"

    def test_verify_endpoint_rejects_invalid_hash(self, client):
        """POST /api/x402/verify with a fake tx hash should return valid=False."""
        r = client.post("/api/x402/verify", json={
            "tx_hash":   "0x" + "de" * 32,   # valid format, does not exist on-chain
            "tool_name": "analyze_wallet",
        })
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert body["valid"]   is False       # tx doesn't exist → should fail
        assert "reason"        in body
        assert body["required_okb"]    > 0
        assert body["payment_address"] != ""

    def test_verify_endpoint_free_tool_skips_payment(self, client):
        """POST /api/x402/verify for a free tool should return valid=True immediately."""
        r = client.post("/api/x402/verify", json={
            "tx_hash":   "0x0000000000000000000000000000000000000000000000000000000000000000",
            "tool_name": "get_gas_price",
        })
        assert r.status_code == 200
        body = r.json()
        assert body["valid"] is True


# ─── Agent Activity Feed ───────────────────────────────────────────────────────

class TestAgentActivity:
    def test_activity_feed_structure(self, client):
        """GET /api/agent/activity must return a structured activity log."""
        r = client.get("/api/agent/activity")
        assert r.status_code == 200
        body = r.json()
        assert body["success"]          is True
        assert body["chain"]            == "X Layer"
        assert isinstance(body["activities"], list)
        assert "activity_count"         in body

    def test_activity_events_have_required_fields(self, client):
        """Each activity event must have id, type, message, and timestamp."""
        activities = client.get("/api/agent/activity").json()["activities"]
        for event in activities[:5]:  # check first 5
            assert "id"        in event
            assert "type"      in event
            assert "message"   in event
            assert "timestamp" in event


# ─── Chat API ─────────────────────────────────────────────────────────────────

class TestChatAPI:
    def test_chat_gas_query_returns_answer(self, client):
        """POST /api/chat with a gas question should return a non-empty LLM answer."""
        r = client.post("/api/chat", json={"question": "What is the current gas price on X Layer?"})
        assert r.status_code == 200
        body = r.json()
        assert body["success"]   is True
        assert body["answer"]    != ""
        assert body["tool_used"] == "get_gas_price"

    def test_chat_yields_tool_used_field(self, client):
        """Every /api/chat response must include which MCP tool was called."""
        r = client.post("/api/chat", json={"question": "Show me X Layer market overview"})
        assert r.status_code == 200
        assert "tool_used" in r.json()
