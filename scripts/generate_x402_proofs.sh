#!/bin/bash
# Run this to generate 10+ real x402 OKB payments on X Layer mainnet
# Each call triggers an on-chain payment verification via OKLink
# Copy the TX hashes — put them in your README as "Economy Loop Proof"

API="https://axon-onld.onrender.com"
WALLET="0xDb82c0d91E057E05600C8F8dc836bEb41da6df14"

echo "=== AXON Economy Loop — Generating Real x402 TX Proofs ==="
echo ""
echo "Step 1: Make a real OKB payment from your wallet to agent wallet"
echo "Amount: 0.001 OKB"
echo "Network: X Layer Mainnet (Chain ID 196)"
echo "To: $WALLET"
echo ""
echo "After each payment, copy the TX hash and run:"
echo ""

# Replace TX_HASH with your actual OKLink TX hash each time
# Use MetaMask or cast to send 0.001 OKB to the agent wallet

# Then call analyze_wallet with the payment header:
cat << 'EOF'
curl -X POST https://axon-onld.onrender.com/api/v2/premium/analyze_wallet \
  -H "Content-Type: application/json" \
  -H "X-PAYMENT: <YOUR_TX_HASH_HERE>" \
  -d '{"address": "0xDb82c0d91E057E05600C8F8dc836bEb41da6df14", "include_ai_insights": true}'

# Or via MCP call endpoint:
curl -X POST https://axon-onld.onrender.com/mcp/call \
  -H "Content-Type: application/json" \
  -H "X-PAYMENT: <YOUR_TX_HASH_HERE>" \
  -d '{"tool_name": "analyze_wallet", "arguments": {"address": "0xDb82c0d91E057E05600C8F8dc836bEb41da6df14", "include_ai_insights": true}}'
EOF

echo ""
echo "Do this 10 times with real TX hashes."
echo "Save all TX hashes for README evidence."
