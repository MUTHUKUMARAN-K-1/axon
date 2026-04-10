"""AXON — Pydantic models for all API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List


class PortfolioRequest(BaseModel):
    address: str
    chain_id: str = "196"
    include_ai_insights: bool = True


class TokenPriceRequest(BaseModel):
    token_address: str
    chain_id: str = "196"


class SwapQuoteRequest(BaseModel):
    from_token: str
    to_token: str
    amount: str
    chain_id: str = "196"
    slippage: str = "0.5"


class WalletAnalysisRequest(BaseModel):
    address: str
    chain_id: str = "196"
    include_ai_insights: bool = True


class CompareWalletsRequest(BaseModel):
    address_a: str
    address_b: str


class UniswapPoolRequest(BaseModel):
    token0: str
    token1: str
    fee: int = 3000


class TokenAnalyticsRequest(BaseModel):
    token_address: str


class ArbitrageRequest(BaseModel):
    token_address: str
    amount_usd: float = 1000.0


class YieldRequest(BaseModel):
    min_apy: float = 5.0


# MCP Protocol Models
class MCPTool(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}


class MCPListToolsResponse(BaseModel):
    tools: List[MCPTool]


class AgentWalletConfig(BaseModel):
    address: str = Field(..., description="X Layer Agentic Wallet address")
    label: str = "AXON Agent Wallet"
    chain_id: int = 196
    network: str = "X Layer Mainnet"
