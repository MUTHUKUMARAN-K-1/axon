"""AXON — Pydantic models for all API requests and responses."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

XLAYER_CHAIN_ID = "196"
EVM_ADDRESS_LENGTH = 42


class AxonBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


def _normalize_evm_address(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("address must be a string")
    normalized = value.strip()
    if len(normalized) != EVM_ADDRESS_LENGTH or not normalized.startswith("0x"):
        raise ValueError("must be a valid EVM address")
    try:
        int(normalized[2:], 16)
    except ValueError as exc:
        raise ValueError("must be a valid EVM address") from exc
    return normalized


class PortfolioRequest(AxonBaseModel):
    address: str
    chain_id: str = XLAYER_CHAIN_ID
    include_ai_insights: bool = True

    _validate_address = field_validator("address")(_normalize_evm_address)


class TokenPriceRequest(AxonBaseModel):
    token_address: str
    chain_id: str = XLAYER_CHAIN_ID

    _validate_address = field_validator("token_address")(_normalize_evm_address)


class SwapQuoteRequest(AxonBaseModel):
    from_token: str
    to_token: str
    amount: str
    chain_id: str = XLAYER_CHAIN_ID
    slippage: str = "0.5"

    _validate_from_token = field_validator("from_token")(_normalize_evm_address)
    _validate_to_token = field_validator("to_token")(_normalize_evm_address)


class WalletAnalysisRequest(AxonBaseModel):
    address: str
    chain_id: str = XLAYER_CHAIN_ID
    include_ai_insights: bool = True

    _validate_address = field_validator("address")(_normalize_evm_address)


class CompareWalletsRequest(AxonBaseModel):
    address_a: str
    address_b: str

    _validate_address_a = field_validator("address_a")(_normalize_evm_address)
    _validate_address_b = field_validator("address_b")(_normalize_evm_address)


class UniswapPoolRequest(AxonBaseModel):
    token0: str
    token1: str
    fee: int = 3000

    _validate_token0 = field_validator("token0")(_normalize_evm_address)
    _validate_token1 = field_validator("token1")(_normalize_evm_address)


class TokenAnalyticsRequest(AxonBaseModel):
    token_address: str

    _validate_address = field_validator("token_address")(_normalize_evm_address)


class ArbitrageRequest(AxonBaseModel):
    token_address: str
    amount_usd: float = 1000.0

    _validate_address = field_validator("token_address")(_normalize_evm_address)


class YieldRequest(AxonBaseModel):
    min_apy: float = 5.0


# MCP Protocol Models
class MCPTool(AxonBaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]


class MCPCallRequest(AxonBaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class MCPListToolsResponse(AxonBaseModel):
    tools: list[MCPTool]


class AgentWalletConfig(AxonBaseModel):
    address: str = Field(..., description="X Layer Agentic Wallet address")
    label: str = "AXON Agent Wallet"
    chain_id: int = 196
    network: str = "X Layer Mainnet"

    _validate_address = field_validator("address")(_normalize_evm_address)
