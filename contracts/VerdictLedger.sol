// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title  AxonVerdictLedger
 * @notice Public on-chain oracle for AXON security verdicts on X Layer.
 *         The AXON backend wallet (oracle) publishes a verdict after every
 *         multi-source security scan.  Any contract or off-chain consumer
 *         can query the latest verdict for any token address.
 *
 * @dev    Deployed on X Layer Mainnet (Chain ID 196).
 *         Only the oracle address set in the constructor may publish verdicts.
 */
contract AxonVerdictLedger {
    // ── Structs ──────────────────────────────────────────────────────────────

    struct Verdict {
        uint8   riskScore;    // 0-100  (0 = SAFE, 100 = CRITICAL SCAM)
        uint32  timestamp;    // Unix timestamp of scan
        uint16  flagCount;    // Number of risk flags raised
        bytes32 dataHash;     // keccak256(full JSON report) — verifiable off-chain
    }

    // ── Storage ───────────────────────────────────────────────────────────────

    /// @notice Latest verdict for each token address
    mapping(address => Verdict) public verdicts;

    /// @notice Ordered list of all scanned token addresses
    address[] public scannedTokens;

    /// @notice The AXON oracle wallet — only account allowed to publish verdicts
    address public oracle;

    // ── Events ────────────────────────────────────────────────────────────────

    event VerdictPublished(
        address indexed token,
        uint8   riskScore,
        uint16  flagCount,
        bytes32 dataHash,
        uint32  timestamp
    );

    event OracleTransferred(address indexed oldOracle, address indexed newOracle);

    // ── Constructor ───────────────────────────────────────────────────────────

    constructor(address _oracle) {
        require(_oracle != address(0), "zero oracle");
        oracle = _oracle;
    }

    // ── Write ─────────────────────────────────────────────────────────────────

    /**
     * @notice Publish a security verdict for a token.
     * @param  token    ERC-20 token contract address on X Layer
     * @param  risk     Risk score 0-100 computed by AXON's 5-source weighted model
     * @param  flags    Number of risk flags raised during the scan
     * @param  hash     keccak256 of the full JSON scan report for off-chain verification
     */
    function publishVerdict(
        address token,
        uint8   risk,
        uint16  flags,
        bytes32 hash
    ) external {
        require(msg.sender == oracle, "AXON: not oracle");
        require(token != address(0), "AXON: zero token");

        // Only push to scannedTokens on first verdict for this token
        if (verdicts[token].timestamp == 0) {
            scannedTokens.push(token);
        }

        verdicts[token] = Verdict({
            riskScore:  risk,
            timestamp:  uint32(block.timestamp),
            flagCount:  flags,
            dataHash:   hash
        });

        emit VerdictPublished(token, risk, flags, hash, uint32(block.timestamp));
    }

    // ── Read ──────────────────────────────────────────────────────────────────

    /// @notice Total number of unique tokens ever scanned by AXON
    function totalVerdicts() external view returns (uint256) {
        return scannedTokens.length;
    }

    /// @notice Returns all fields of the latest verdict for a token
    function getVerdict(address token) external view returns (
        uint8  riskScore,
        uint32 timestamp,
        uint16 flagCount,
        bytes32 dataHash
    ) {
        Verdict memory v = verdicts[token];
        return (v.riskScore, v.timestamp, v.flagCount, v.dataHash);
    }

    /// @notice Paginated list of scanned tokens (for explorers / dashboards)
    function getScannedTokens(uint256 offset, uint256 limit)
        external
        view
        returns (address[] memory)
    {
        uint256 total = scannedTokens.length;
        if (offset >= total) return new address[](0);
        uint256 end = offset + limit > total ? total : offset + limit;
        address[] memory out = new address[](end - offset);
        for (uint256 i = offset; i < end; i++) {
            out[i - offset] = scannedTokens[i];
        }
        return out;
    }

    // ── Admin ─────────────────────────────────────────────────────────────────

    /// @notice Transfer oracle role (e.g. to a new AXON wallet)
    function transferOracle(address newOracle) external {
        require(msg.sender == oracle, "AXON: not oracle");
        require(newOracle != address(0), "zero oracle");
        emit OracleTransferred(oracle, newOracle);
        oracle = newOracle;
    }
}
