// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title  AxonConfidenceBond
 * @notice AXON puts skin in the game — for every SAFE verdict (risk < 20),
 *         AXON locks a small OKB bond. Anyone can challenge within 7 days
 *         if the token turns out to be dangerous. A successful challenge
 *         (confirmed by the VerdictLedger being updated to HIGH RISK)
 *         transfers the bond to the challenger.
 *
 * @dev    Works alongside AxonVerdictLedger:
 *         - Oracle calls lockBond() when publishing a SAFE verdict
 *         - Challenger calls challenge() with the token address
 *         - If VerdictLedger now shows risk >= 65, challenger wins the bond
 *         - If 7 days pass without a successful challenge, bond is released
 *
 *         Deployed on X Layer Mainnet (Chain ID 196).
 */

interface IAxonVerdictLedger {
    function getVerdict(address token) external view returns (
        uint8  riskScore,
        uint32 timestamp,
        uint16 flagCount,
        bytes32 dataHash
    );
}

contract AxonConfidenceBond {
    // ── Constants ─────────────────────────────────────────────────────────────

    uint256 public constant CHALLENGE_WINDOW  = 7 days;
    uint8   public constant SAFE_THRESHOLD    = 20;   // risk < 20 → SAFE
    uint8   public constant DANGER_THRESHOLD  = 65;   // risk ≥ 65 → HIGH RISK
    uint256 public immutable BOND_AMOUNT;              // set in constructor (OKB wei)

    // ── Storage ───────────────────────────────────────────────────────────────

    address public oracle;
    address public verdictLedger;

    struct Bond {
        uint256 amount;      // OKB locked (wei)
        uint32  lockedAt;    // timestamp of lockBond()
        bool    active;      // false once claimed or expired
    }

    mapping(address => Bond) public bonds;            // token → bond
    address[] public bondedTokens;

    uint256 public totalLocked;       // total OKB currently at stake
    uint256 public totalChallenges;   // successful challenges won by challengers
    uint256 public totalExpired;      // bonds released after window with no challenge

    // ── Events ────────────────────────────────────────────────────────────────

    event BondLocked(address indexed token, uint256 amount, uint32 lockedAt);
    event BondChallenged(address indexed token, address indexed challenger, uint256 payout, uint8 newRiskScore);
    event BondExpired(address indexed token, uint256 amount);
    event OracleTransferred(address indexed oldOracle, address indexed newOracle);

    // ── Constructor ───────────────────────────────────────────────────────────

    constructor(address _oracle, address _verdictLedger, uint256 _bondAmountWei) payable {
        require(_oracle != address(0), "zero oracle");
        require(_verdictLedger != address(0), "zero ledger");
        require(_bondAmountWei > 0, "zero bond");
        oracle        = _oracle;
        verdictLedger = _verdictLedger;
        BOND_AMOUNT   = _bondAmountWei;
    }

    // ── Write — Oracle ────────────────────────────────────────────────────────

    /**
     * @notice Lock a bond for a SAFE verdict. Called by oracle after publishVerdict()
     *         when riskScore < SAFE_THRESHOLD. Sent with msg.value == BOND_AMOUNT.
     * @param  token  The token that was scored SAFE.
     */
    function lockBond(address token) external payable {
        require(msg.sender == oracle, "AXON: not oracle");
        require(msg.value == BOND_AMOUNT, "AXON: wrong bond amount");
        require(token != address(0), "zero token");
        require(!bonds[token].active, "bond already active");

        // Confirm VerdictLedger agrees this token is currently SAFE
        (uint8 risk, , , ) = IAxonVerdictLedger(verdictLedger).getVerdict(token);
        require(risk < SAFE_THRESHOLD, "AXON: not a SAFE verdict");

        bonds[token] = Bond({
            amount:   msg.value,
            lockedAt: uint32(block.timestamp),
            active:   true
        });
        bondedTokens.push(token);
        totalLocked += msg.value;

        emit BondLocked(token, msg.value, uint32(block.timestamp));
    }

    // ── Write — Anyone ────────────────────────────────────────────────────────

    /**
     * @notice Challenge a SAFE verdict. If VerdictLedger now rates the token
     *         as HIGH RISK (risk >= DANGER_THRESHOLD) within the challenge window,
     *         the bond is paid to the challenger.
     * @param  token  The bonded token to challenge.
     */
    function challenge(address token) external {
        Bond storage b = bonds[token];
        require(b.active, "no active bond");
        require(block.timestamp <= b.lockedAt + CHALLENGE_WINDOW, "challenge window closed");

        // Read current verdict from VerdictLedger
        (uint8 currentRisk, uint32 verdictTs, , ) = IAxonVerdictLedger(verdictLedger).getVerdict(token);

        // The new verdict must be issued AFTER the bond was locked (not a stale read)
        require(verdictTs >= b.lockedAt, "verdict predates bond");
        require(currentRisk >= DANGER_THRESHOLD, "token still safe - challenge rejected");

        // Challenger wins — transfer bond
        uint256 payout = b.amount;
        b.active = false;
        totalLocked  -= payout;
        totalChallenges++;

        emit BondChallenged(token, msg.sender, payout, currentRisk);
        payable(msg.sender).transfer(payout);
    }

    /**
     * @notice Release an expired bond back to the oracle (7-day window passed, no challenge).
     * @param  token  The token whose bond has expired unchallenged.
     */
    function releaseExpired(address token) external {
        Bond storage b = bonds[token];
        require(b.active, "no active bond");
        require(block.timestamp > b.lockedAt + CHALLENGE_WINDOW, "window still open");

        uint256 amount = b.amount;
        b.active = false;
        totalLocked -= amount;
        totalExpired++;

        emit BondExpired(token, amount);
        payable(oracle).transfer(amount);
    }

    // ── Read ──────────────────────────────────────────────────────────────────

    /// @notice Total number of tokens that ever had an active bond
    function totalBonded() external view returns (uint256) { return bondedTokens.length; }

    /// @notice Check if a bond is still within the challenge window
    function isChallengeOpen(address token) external view returns (bool) {
        Bond memory b = bonds[token];
        return b.active && block.timestamp <= b.lockedAt + CHALLENGE_WINDOW;
    }

    /// @notice Contract OKB balance (total at stake)
    function contractBalance() external view returns (uint256) { return address(this).balance; }

    // ── Admin ─────────────────────────────────────────────────────────────────

    function transferOracle(address newOracle) external {
        require(msg.sender == oracle, "AXON: not oracle");
        require(newOracle != address(0), "zero oracle");
        emit OracleTransferred(oracle, newOracle);
        oracle = newOracle;
    }

    /// @notice Fund the contract with OKB for future bonds
    receive() external payable {}
}
