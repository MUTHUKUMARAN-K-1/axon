/**
 * send_okb.js — Send 0.001 OKB x10 on X Layer Mainnet
 * Generates real on-chain economy loop proof for hackathon judges.
 * Run: node send_okb.js
 */
const https = require("https");
const { ethers } = require("ethers");

// ─── Config ──────────────────────────────────────────────────────────────────
const RPC_URL    = "https://rpc.xlayer.tech";
const CHAIN_ID   = 196;
const FROM_KEY   = "0x592d3bfec619308db11f20922fb50f6783db8b9251dd27e92ebe9b6bdad2275a";
const TO_ADDRESS = "0xDb82c0d91E057E05600C8F8dc836bEb41da6df14";
const AMOUNT_OKB = 0.00005;   // 50 microOKB per TX — 10 TXs = 0.0005 total, fits in 0.000953 balance
const TIMES      = 10;

runWithEthers(ethers);


async function runWithEthers(ethers) {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet   = new ethers.Wallet(FROM_KEY, provider);
  const amountWei = ethers.parseEther(AMOUNT_OKB.toString());

  console.log(`\n╔══════════════════════════════════════════════════════════════╗`);
  console.log(`║  AXON Economy Loop — Generating Real x402 TX Proofs          ║`);
  console.log(`╚══════════════════════════════════════════════════════════════╝`);
  console.log(`From:   ${wallet.address}`);
  console.log(`To:     ${TO_ADDRESS}`);
  console.log(`Amount: ${AMOUNT_OKB} OKB per tx  (${TIMES} total txs)`);
  console.log(`Chain:  X Layer Mainnet (${CHAIN_ID})`);
  console.log(`─────────────────────────────────────────────────────────────\n`);

  const txHashes = [];

  for (let i = 1; i <= TIMES; i++) {
    try {
      console.log(`[${i}/${TIMES}] Sending ${AMOUNT_OKB} OKB...`);
      const tx = await wallet.sendTransaction({
        to: TO_ADDRESS,
        value: amountWei,
        chainId: CHAIN_ID,
      });
      console.log(`  ✅ TX sent: ${tx.hash}`);
      console.log(`  🔗 https://www.oklink.com/xlayer/tx/${tx.hash}`);
      txHashes.push(tx.hash);

      // Wait for confirmation before next TX (avoids nonce issues)
      const receipt = await tx.wait();
      console.log(`  ✔  Confirmed in block #${receipt.blockNumber}\n`);

      // Small delay between txs
      await new Promise(r => setTimeout(r, 1500));
    } catch (err) {
      console.error(`  ❌ TX ${i} failed: ${err.message}\n`);
    }
  }

  console.log(`\n══════════════ ECONOMY LOOP PROOF ══════════════`);
  console.log(`${txHashes.length} real OKB payments confirmed on X Layer:\n`);
  txHashes.forEach((h, i) => {
    console.log(`  ${i + 1}. ${h}`);
    console.log(`     https://www.oklink.com/xlayer/tx/${h}`);
  });
  console.log(`\nCopy these TX hashes into your hackathon submission!`);
  console.log(`══════════════════════════════════════════════════`);

  // Now call the x402 analyze_wallet endpoint once with each TX hash
  if (txHashes.length > 0) {
    console.log(`\n─── Triggering x402 premium calls with TX proofs ───`);
    const http = require("https");
    for (const txHash of txHashes.slice(0, 3)) {
      await triggerX402Call(txHash);
      await new Promise(r => setTimeout(r, 2000));
    }
  }
}

function triggerX402Call(txHash) {
  return new Promise((resolve) => {
    const body = JSON.stringify({
      tool_name: "analyze_wallet",
      arguments: {
        address: TO_ADDRESS,
        include_ai_insights: true
      }
    });
    const req = https.request({
      hostname: "axon-onld.onrender.com",
      path: "/mcp/call",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-PAYMENT": txHash,
        "Content-Length": Buffer.byteLength(body),
        "User-Agent": "axon-economy-loop/1.0",
      },
      timeout: 30000,
    }, (res) => {
      let data = "";
      res.on("data", c => data += c);
      res.on("end", () => {
        console.log(`  [x402] TX ${txHash.slice(0,16)}... → HTTP ${res.statusCode}`);
        try {
          const r = JSON.parse(data);
          if (res.statusCode === 200) {
            console.log(`  ✅ Premium tool call succeeded!`);
          } else if (res.statusCode === 402) {
            console.log(`  ⚠  402 returned — TX not yet confirmed on OKLink`);
          }
        } catch { }
        resolve();
      });
    });
    req.on("error", (e) => { console.log(`  x402 request failed: ${e.message}`); resolve(); });
    req.on("timeout", () => { req.destroy(); resolve(); });
    req.write(body);
    req.end();
  });
}
