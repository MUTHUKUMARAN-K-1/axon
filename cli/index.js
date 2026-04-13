#!/usr/bin/env node

// AXON CLI — Neural Intelligence Layer for X Layer
// Usage: npx @axon-xlayer/start [command] [args] [--json]

const https = require("https");
const http = require("http");

const API = "https://axon-onld.onrender.com";
const FRONTEND = "https://axon-six-amber.vercel.app";
const AGENT_WALLET = "0xDb82c0d91E057E05600C8F8dc836bEb41da6df14";
const CHAIN_ID = 196;
const PLUGIN_PR = "https://github.com/okx/plugin-store/pull/93";
const GITHUB = "https://github.com/MUTHUKUMARAN-K-1/axon";
const VERSION = "1.3.0";

// ─── ANSI Colors (zero deps) ─────────────────────────────────────────────────
const c = {
  reset: "\x1b[0m",
  bold: "\x1b[1m",
  dim: "\x1b[2m",
  cyan: "\x1b[36m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  red: "\x1b[31m",
  magenta: "\x1b[35m",
  blue: "\x1b[34m",
  white: "\x1b[37m",
  bgCyan: "\x1b[46m\x1b[30m",
};
const dim = (s) => `${c.dim}${s}${c.reset}`;
const cyan = (s) => `${c.cyan}${s}${c.reset}`;
const green = (s) => `${c.green}${s}${c.reset}`;
const yellow = (s) => `${c.yellow}${s}${c.reset}`;
const red = (s) => `${c.red}${s}${c.reset}`;
const bold = (s) => `${c.bold}${s}${c.reset}`;

// ─── HTTP helper ─────────────────────────────────────────────────────────────
function fetch(url, opts = {}) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const lib = parsed.protocol === "https:" ? https : http;
    const options = {
      hostname: parsed.hostname,
      path: parsed.pathname + parsed.search,
      method: opts.method || "GET",
      headers: { "Content-Type": "application/json", "User-Agent": `axon-cli/${VERSION}`, ...(opts.headers || {}) },
      timeout: 15000,
    };
    const req = lib.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try { resolve({ ok: res.statusCode < 400, status: res.statusCode, json: () => JSON.parse(data), text: () => data }); }
        catch { resolve({ ok: false, status: res.statusCode, json: () => ({}), text: () => data }); }
      });
    });
    req.on("error", reject);
    req.on("timeout", () => { req.destroy(); reject(new Error("Request timed out")); });
    if (opts.body) req.write(opts.body);
    req.end();
  });
}

// ─── Spinner ─────────────────────────────────────────────────────────────────
function spinner(msg) {
  const frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];
  let i = 0;
  const iv = setInterval(() => {
    process.stdout.write(`\r${cyan(frames[i++ % frames.length])} ${msg}`);
  }, 80);
  return { stop: (done) => { clearInterval(iv); process.stdout.write(`\r${done}\n`); } };
}

// ─── Risk badge ──────────────────────────────────────────────────────────────
function riskBadge(score) {
  if (score < 20) return green(`✅ SAFE (${score})`);
  if (score < 45) return yellow(`⚠️  LOW RISK (${score})`);
  if (score < 65) return yellow(`🟡 MEDIUM RISK (${score})`);
  if (score < 80) return red(`🔴 HIGH RISK (${score})`);
  return red(`💀 CRITICAL — LIKELY SCAM (${score})`);
}

// ─── Banner ───────────────────────────────────────────────────────────────────
function banner() {
  const M = "\x1b[35m", R = c.reset, B = c.bold, D = c.dim;
  console.log(`
${M} █████╗ ██╗  ██╗ ██████╗ ███╗   ██╗${R}
${M}██╔══██╗╚██╗██╔╝██╔═══██╗████╗  ██║${R}
${M}███████║ ╚███╔╝ ██║   ██║██╔██╗ ██║${R}
${M}██╔══██║ ██╔██╗ ██║   ██║██║╚██╗██║${R}
${M}██║  ██║██╔╝ ██╗╚██████╔╝██║ ╚████║${R}
${M}╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝${R}  ${D}v${VERSION}${R}

  ${B}Neural Intelligence Layer for X Layer${R}
  ${cyan("45 MCP Tools")} · ${yellow("x402 OKB Payments")} · ${green("On-Chain Security Oracle")} · ${M}Chain 196${R}
${D}${"─".repeat(65)}${R}`);
}

// ═══════════════════════════════════════════════════════════════════════════════
// COMMANDS
// ═══════════════════════════════════════════════════════════════════════════════

async function cmdOrient(jsonMode) {
  if (jsonMode) {
    const spin = spinner("Fetching live AXON context...");
    let toolCount = 45;
    let totalVerdicts = 0;
    try {
      const [toolsRes, verdictsRes] = await Promise.all([
        fetch(`${API}/mcp/tools`).catch(() => null),
        fetch(`${API}/mcp/call`, { method: "POST", body: JSON.stringify({ tool_name: "get_total_verdicts", arguments: {} }) }).catch(() => null),
      ]);
      if (toolsRes?.ok) { const d = toolsRes.json(); toolCount = Array.isArray(d?.tools) ? d.tools.length : 45; }
      if (verdictsRes?.ok) { const d = verdictsRes.json(); totalVerdicts = d?.result?.total_verdicts ?? 0; }
    } catch {}
    spin.stop(green("✔ Live data loaded"));
    console.log(JSON.stringify({
      name: "AXON", version: VERSION,
      tagline: "Neural Intelligence Layer for X Layer",
      chain: "X Layer Mainnet", chain_id: CHAIN_ID,
      api: API, frontend: FRONTEND,
      llms_txt: `${API}/llms.txt`,
      docs: `${API}/docs`,
      tools_endpoint: `${API}/mcp/tools`,
      call_endpoint: `${API}/mcp/call`,
      register_endpoint: `${API}/api/agents`,
      leaderboard_endpoint: `${API}/api/leaderboard`,
      tasks_endpoint: `${API}/api/tasks`,
      x402_pricing: `${API}/api/x402/pricing`,
      agentic_wallet: AGENT_WALLET,
      plugin_store_pr: PLUGIN_PR,
      github: GITHUB,
      stats: { tool_count: toolCount, on_chain_verdicts: totalVerdicts },
      quick_start: [
        `GET ${API}/mcp/tools`,
        `POST ${API}/mcp/call  {"tool_name":"get_gas_price","arguments":{}}`,
        `POST ${API}/api/agents  {"name":"my-agent","wallet":"0x..."}`,
        `GET ${API}/api/tasks`,
      ],
      free_tools: ["get_gas_price","get_block_info","get_market_overview","scan_token_security","get_smart_money_signals","get_onchain_verdict","get_total_verdicts","get_uniswap_top_pools","get_yield_opportunities","get_wallet_portfolio","get_token_price","get_swap_quote"],
      premium_tools_x402: [
        { tool: "analyze_wallet", price_okb: 0.001 },
        { tool: "compare_wallets", price_okb: 0.001 },
        { tool: "find_arbitrage_opportunities", price_okb: 0.002 },
      ],
      contracts: {
        verdict_ledger: { address: "0x0191d5ada56672507fdb283ac59d45bde08a53f8", network: "X Layer Mainnet", chain_id: CHAIN_ID },
        confidence_bond: { address: "0xe164011de202eb0ebf5f01ee5d9851c801a9c675", network: "X Layer Mainnet", chain_id: CHAIN_ID },
      },
    }, null, 2));
    return;
  }

  banner();

  // Live health check
  const spin = spinner("Checking live status...");
  let status = "unknown", gasPrice = null, totalVerdicts = null;
  try {
    const [healthRes, gasRes, verdictsRes] = await Promise.all([
      fetch(`${API}/health`).catch(() => null),
      fetch(`${API}/mcp/call`, { method: "POST", body: JSON.stringify({ tool_name: "get_gas_price", arguments: {} }) }).catch(() => null),
      fetch(`${API}/mcp/call`, { method: "POST", body: JSON.stringify({ tool_name: "get_total_verdicts", arguments: {} }) }).catch(() => null),
    ]);
    if (healthRes?.ok) status = "live";
    if (gasRes?.ok) { const d = gasRes.json(); gasPrice = d?.result?.gas_price_gwei ?? d?.result?.gas_price ?? null; }
    if (verdictsRes?.ok) { const d = verdictsRes.json(); totalVerdicts = d?.result?.total_verdicts ?? null; }
  } catch {}
  spin.stop(status === "live" ? green("✔ API is live") : yellow("⚠ API may be sleeping (Render cold start ~30s)"));

  console.log(`
${bold("  LIVE STATS")}
  Status:          ${status === "live" ? green("● LIVE") : yellow("● WAKING UP")}
  Gas Price:       ${gasPrice != null ? cyan(gasPrice + " gwei") : dim("fetching...")}
  On-Chain Verdicts: ${totalVerdicts != null ? cyan(totalVerdicts + " published") : dim("fetching...")}

${bold("─────────────────── QUICK START (3 STEPS) ───────────────────────")}

  ${cyan("Step 1")} — Discover all 45 tools:
  ${dim(`curl ${API}/mcp/tools`)}

  ${cyan("Step 2")} — Call a free tool (no auth needed):
  ${dim(`curl -X POST ${API}/mcp/call \\`)}
  ${dim(`  -H "Content-Type: application/json" \\`)}
  ${dim(`  -d '{"tool_name":"get_gas_price","arguments":{}}'`)}

  ${cyan("Step 3")} — Register as an agent:
  ${dim(`curl -X POST ${API}/api/agents \\`)}
  ${dim(`  -H "Content-Type: application/json" \\`)}
  ${dim(`  -d '{"name":"my-agent","wallet":"0xYourWallet"}'`)}

${bold("─────────────────────── COMMANDS ────────────────────────────────")}

  ${cyan("npx @axon-xlayer/start tools")}               List all 45 MCP tools
  ${cyan("npx @axon-xlayer/start tools")} ${dim("<keyword>")}    Filter tools (e.g. security, wallet)
  ${cyan("npx @axon-xlayer/start call")} ${dim("<tool>")}        Call any of the 45 tools
  ${cyan("npx @axon-xlayer/start call")} ${dim("<tool> --args '{}'")}  Call with arguments
  ${cyan("npx @axon-xlayer/start scan")} ${dim("<token>")}       Security scan any token
  ${cyan("npx @axon-xlayer/start wallet")} ${dim("<address>")}   Wallet portfolio + analysis
  ${cyan("npx @axon-xlayer/start gas")}                 Live gas price on X Layer
  ${cyan("npx @axon-xlayer/start tasks")}               10 X Layer agent challenges
  ${cyan("npx @axon-xlayer/start leaderboard")}         Top agents by scans
  ${cyan("npx @axon-xlayer/start register")} ${dim("<name> <wallet>")}  Register agent
  ${cyan("npx @axon-xlayer/start health")}              API health + latency
  ${cyan("npx @axon-xlayer/start")} ${dim("[cmd] --json")}      Machine-readable output

${bold("─────────────────── PREMIUM TOOLS (x402) ────────────────────────")}

  ${yellow("analyze_wallet")}              0.001 OKB — AI wallet risk analysis
  ${yellow("compare_wallets")}             0.001 OKB — Compare 2 wallets
  ${yellow("find_arbitrage_opportunities")} 0.002 OKB — Price discrepancy scanner

  ${dim("Payment →")} ${AGENT_WALLET}
  ${dim("Network  →")} X Layer Mainnet (Chain ID ${CHAIN_ID})
  ${dim("How      →")} Send OKB · copy tx hash · add X-PAYMENT: 0x<hash> header

${bold("─────────────────── ON-CHAIN CONTRACTS ──────────────────────────")}

  ${green("AxonVerdictLedger")} ${dim("(public security oracle)")}
  ${dim("0x0191d5ada56672507fdb283ac59d45bde08a53f8")}
  ${dim("getVerdict(token) · totalVerdicts() — permissionless read")}

  ${green("AxonConfidenceBond")} ${dim("(skin-in-the-game)")}
  ${dim("0xe164011de202eb0ebf5f01ee5d9851c801a9c675")}
  ${dim("0.001 OKB locked per SAFE verdict · challenge within 7 days")}

${bold("─────────────────────────────────────────────────────────────────")}

  Plugin Store:  ${dim(PLUGIN_PR)}
  GitHub:        ${dim(GITHUB)}
  Docs:          ${dim(`${API}/docs`)}
  LLMs context:  ${dim(`${API}/llms.txt`)}

${dim("  Tip: run with --json for AI-agent-readable output")}
${cyan("═════════════════════════════════════════════════════════════════")}
`);
}

async function cmdScan(token, jsonMode) {
  if (!token) { console.error(red("Usage: npx @axon-xlayer/start scan <token_address>")); process.exit(1); }
  const spin = spinner(`Scanning ${token.slice(0, 10)}...`);
  try {
    const res = await fetch(`${API}/mcp/call`, {
      method: "POST",
      body: JSON.stringify({ tool_name: "scan_token_security", arguments: { token_address: token } }),
    });
    const data = res.json();
    const r = data?.result ?? data;
    spin.stop(green("✔ Scan complete"));
    if (jsonMode) { console.log(JSON.stringify(r, null, 2)); return; }
    const score = r?.risk_score ?? r?.total_score ?? "?";
    const label = r?.risk_label ?? "";
    console.log(`
${bold("  TOKEN SECURITY SCAN")}  ${dim(token)}

  Risk Score:   ${riskBadge(score)}
  Risk Label:   ${bold(label)}
  Flags:        ${(r?.risks ?? r?.flags ?? []).length} issues detected
  ${r?.verdict_ledger ? `On-Chain TX: ${dim(r.verdict_ledger.explorer_url ?? "published")}` : ""}

  ${bold("Sources checked:")}
  ${(r?.risks ?? []).slice(0, 8).map(f => `  ${red("●")} ${f}`).join("\n") || dim("  No issues detected")}

  ${dim(`Full report: ${API}/docs → scan_token_security`)}
`);
  } catch (e) {
    spin.stop(red("✘ Scan failed"));
    console.error(red(e.message));
    process.exit(1);
  }
}

async function cmdWallet(address, jsonMode) {
  if (!address) { console.error(red("Usage: npx @axon-xlayer/start wallet <address>")); process.exit(1); }
  const spin = spinner(`Loading wallet ${address.slice(0, 10)}...`);
  try {
    const [portfolioRes, balanceRes] = await Promise.all([
      fetch(`${API}/mcp/call`, { method: "POST", body: JSON.stringify({ tool_name: "get_wallet_portfolio", arguments: { address } }) }),
      fetch(`${API}/mcp/call`, { method: "POST", body: JSON.stringify({ tool_name: "get_native_balance", arguments: { address } }) }),
    ]);
    const portfolioData = portfolioRes.json();
    const balanceData = balanceRes.json();
    const portfolio = portfolioData?.result ?? {};
    const balance = balanceData?.result ?? {};
    spin.stop(green("✔ Wallet loaded"));
    if (jsonMode) { console.log(JSON.stringify({ address, portfolio, balance }, null, 2)); return; }
    const tokens = portfolio?.tokens ?? [];
    const nativeOKB = balance?.balance_okb ?? balance?.balance ?? balance?.native_balance ?? "?";
    const portfolioOk = portfolio?.success !== false;
    console.log(`
${bold("  WALLET PORTFOLIO")}  ${dim(address)}

  Native OKB:   ${cyan(nativeOKB + " OKB")}
  Tokens held:  ${portfolioOk ? cyan(String(tokens.length)) : yellow("requires OKX API key")}
  Net Worth:    ${portfolio?.total_usd_value != null ? cyan("$" + portfolio.total_usd_value) : dim("n/a")}

${portfolioOk
  ? tokens.slice(0, 10).map(t => `  ${green("●")} ${bold((t.symbol ?? "?").padEnd(8))}  ${(t.balance ?? "?").toString().padEnd(18)} ${dim("$" + (t.value_usd ?? t.usd_value ?? "?"))}`).join("\n") || dim("  Wallet is empty on X Layer")
  : `  ${yellow("●")} Token list unavailable: ${dim(portfolio?.error ?? "OKX API auth required")}`
}

  ${dim(`Analyze with AI: POST ${API}/mcp/call`)}
  ${dim(`{"tool_name":"analyze_wallet","arguments":{"address":"${address}"}}`)}
  ${dim("(requires 0.001 OKB x402 payment)")}
`);
  } catch (e) {
    spin.stop(red("✘ Failed"));
    console.error(red(e.message));
    process.exit(1);
  }
}

async function cmdGas(jsonMode) {
  const spin = spinner("Fetching gas price...");
  try {
    const res = await fetch(`${API}/mcp/call`, { method: "POST", body: JSON.stringify({ tool_name: "get_gas_price", arguments: {} }) });
    const data = res.json()?.result ?? res.json();
    spin.stop(green("✔ Gas data loaded"));
    if (jsonMode) { console.log(JSON.stringify(data, null, 2)); return; }
    console.log(`
${bold("  X LAYER GAS PRICE")}

  Gas Price:     ${cyan((data?.gas_price_gwei ?? data?.gas_price ?? "?") + " gwei")}
  Priority Fee:  ${cyan((data?.priority_fee_gwei ?? data?.priority_fee ?? "?") + " gwei")}
  Network:       X Layer Mainnet (Chain ID ${CHAIN_ID})

  ${dim(`Live: ${API}/mcp/call → get_gas_price`)}
`);
  } catch (e) {
    spin.stop(red("✘ Failed"));
    console.error(red(e.message));
    process.exit(1);
  }
}

async function cmdTasks(taskId, jsonMode) {
  const url = taskId ? `${API}/api/tasks/${taskId}` : `${API}/api/tasks`;
  const spin = spinner("Loading tasks...");
  try {
    const res = await fetch(url);
    const data = res.json();
    spin.stop(green("✔ Tasks loaded"));
    if (jsonMode) { console.log(JSON.stringify(data, null, 2)); return; }
    if (taskId) {
      const t = data?.task ?? data;
      console.log(`
${bold(`  TASK: ${t.title}`)}  ${dim(t.id)}

  Category:   ${cyan(t.category ?? "?")}
  Difficulty: ${t.difficulty === "easy" ? green("easy") : t.difficulty === "medium" ? yellow("medium") : red("hard")}
  Reward:     ${green((t.reward_okb ?? "?") + " OKB")}

  ${bold("Description:")}
  ${t.description ?? ""}

  ${bold("How to complete:")}
  ${(t.steps ?? []).map((s, i) => `  ${i + 1}. ${s}`).join("\n")}

  ${bold("Proof hint:")} ${dim(t.proof_hint ?? t.proof_format ?? "")}

  ${dim(`Submit: POST ${API}/api/tasks/${t.id}/submit`)}
`);
    } else {
      const tasks = data?.tasks ?? [];
      console.log(`\n${bold("  AXON TASK CHALLENGES")}  ${dim(tasks.length + " tasks on X Layer")}\n`);
      tasks.forEach(t => {
        const diff = t.difficulty === "easy" ? green("easy  ") : t.difficulty === "medium" ? yellow("medium") : red("hard  ");
        console.log(`  ${cyan(t.id.padEnd(12))} ${diff}  ${green((t.reward_okb ?? "?").toString().padEnd(6) + " OKB")}  ${t.title}`);
      });
      console.log(`\n  ${dim(`Details: npx @axon-xlayer/start tasks <task-id>`)}`);
      console.log(`  ${dim(`API:     GET ${API}/api/tasks`)}\n`);
    }
  } catch (e) {
    spin.stop(red("✘ Failed"));
    console.error(red(e.message));
    process.exit(1);
  }
}

async function cmdLeaderboard(jsonMode) {
  const spin = spinner("Loading leaderboard...");
  try {
    const res = await fetch(`${API}/api/leaderboard`);
    const data = res.json();
    spin.stop(green("✔ Leaderboard loaded"));
    if (jsonMode) { console.log(JSON.stringify(data, null, 2)); return; }
    const agents = data?.leaderboard ?? data?.agents ?? [];
    console.log(`\n${bold("  AXON AGENT LEADERBOARD")}\n`);
    if (agents.length === 0) {
      console.log(`  ${dim("No agents registered yet. Be the first!")}`);
      console.log(`  ${dim(`npx @axon-xlayer/start register <name> <wallet>`)}\n`);
    } else {
      agents.slice(0, 10).forEach((a, i) => {
        const medal = i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : `${i + 1}. `;
        console.log(`  ${medal}  ${bold((a.name ?? "?").padEnd(20))} ${cyan(a.scans + " scans")}  ${dim(a.wallet?.slice(0, 12) + "...")}`);
      });
    }
    console.log(`\n  ${dim(`Register: npx @axon-xlayer/start register <name> <wallet>`)}\n`);
  } catch (e) {
    spin.stop(red("✘ Failed"));
    console.error(red(e.message));
    process.exit(1);
  }
}

async function cmdRegister(name, wallet, jsonMode) {
  if (!name || !wallet) { console.error(red("Usage: npx @axon-xlayer/start register <name> <wallet>")); process.exit(1); }
  const spin = spinner(`Registering agent "${name}"...`);
  try {
    const res = await fetch(`${API}/api/agents`, {
      method: "POST",
      body: JSON.stringify({ name, wallet }),
    });
    const data = res.json();
    spin.stop(res.ok ? green("✔ Agent registered!") : red("✘ Registration failed"));
    if (jsonMode) { console.log(JSON.stringify(data, null, 2)); return; }
    if (res.ok) {
      const agent = data?.agent ?? data;
      console.log(`
${bold("  AGENT REGISTERED")}

  Name:    ${cyan(agent.name ?? name)}
  Wallet:  ${dim(agent.wallet ?? wallet)}
  Scans:   ${agent.scans ?? 0}
  Joined:  ${agent.registered_at ?? "just now"}

  ${dim("Your scans now appear on the leaderboard.")}
  ${dim(`Leaderboard: npx @axon-xlayer/start leaderboard`)}
`);
    } else {
      console.error(red(data?.error ?? data?.detail ?? "Registration failed"));
      process.exit(1);
    }
  } catch (e) {
    spin.stop(red("✘ Failed"));
    console.error(red(e.message));
    process.exit(1);
  }
}

async function cmdTools(filter, jsonMode) {
  const spin = spinner("Loading all 45 MCP tools...");
  try {
    const res = await fetch(`${API}/mcp/tools`);
    const data = res.json();
    let tools = data?.tools ?? [];
    if (filter) tools = tools.filter(t => t.name.includes(filter) || (t.description ?? "").toLowerCase().includes(filter.toLowerCase()));
    spin.stop(green(`✔ ${tools.length} tools loaded`));
    if (jsonMode) { console.log(JSON.stringify({ tools }, null, 2)); return; }

    // Group by category tag
    const groups = {};
    tools.forEach(t => {
      const tag = (t.tags?.[0] ?? t.category ?? "general").toLowerCase();
      if (!groups[tag]) groups[tag] = [];
      groups[tag].push(t);
    });

    console.log(`\n${bold("  AXON MCP TOOLS")}  ${dim(tools.length + " tools available")}\n`);
    Object.entries(groups).forEach(([tag, list]) => {
      console.log(`  ${cyan(tag.toUpperCase())}`);
      list.forEach(t => {
        const premium = t.premium ? yellow(" [x402]") : "";
        console.log(`    ${green("●")} ${bold(t.name.padEnd(35))}${premium}  ${dim(t.description ?? "")}`);
      });
      console.log();
    });
    console.log(`  ${dim(`Call any tool: npx @axon-xlayer/start call <tool_name>`)}`);
    console.log(`  ${dim(`Filter:        npx @axon-xlayer/start tools <keyword>`)}`);
    console.log(`  ${dim(`API:           GET ${API}/mcp/tools`)}\n`);
  } catch (e) {
    spin.stop(red("✘ Failed"));
    console.error(red(e.message));
    process.exit(1);
  }
}

async function cmdCall(toolName, rawArgs, jsonMode) {
  if (!toolName) {
    console.error(red("Usage: npx @axon-xlayer/start call <tool_name> [--args '{\"key\":\"value\"}']"));
    console.error(red("       npx @axon-xlayer/start tools   (to see all tool names)"));
    process.exit(1);
  }
  let toolArgs = {};
  if (rawArgs) {
    try { toolArgs = JSON.parse(rawArgs); }
    catch { console.error(red("Invalid --args JSON. Example: --args '{\"wallet_address\":\"0x...\"}'"));  process.exit(1); }
  }

  const spin = spinner(`Calling ${toolName}...`);
  try {
    const res = await fetch(`${API}/mcp/call`, {
      method: "POST",
      body: JSON.stringify({ tool_name: toolName, arguments: toolArgs }),
    });

    if (res.status === 402) {
      const data = res.json();
      spin.stop(yellow("⚠ Payment Required (x402)"));
      if (jsonMode) { console.log(JSON.stringify(data, null, 2)); return; }
      const x402 = data?.x402 ?? {};
      const accepts = x402?.accepts?.[0] ?? {};
      console.log(`
${bold("  PREMIUM TOOL — x402 PAYMENT REQUIRED")}

  Tool:     ${cyan(toolName)}
  Price:    ${yellow(accepts.maxAmountRequired ?? "?")} ${accepts.asset ?? "OKB"}
  Pay to:   ${dim(accepts.payTo ?? AGENT_WALLET)}
  Network:  X Layer Mainnet (Chain ID ${CHAIN_ID})

  ${bold("How to pay:")}
  1. Send OKB to the address above on X Layer
  2. Copy the transaction hash
  3. Add header: ${cyan("X-PAYMENT: 0x<tx_hash>")}

  ${dim(`curl -X POST ${API}/mcp/call \\`)}
  ${dim(`  -H "Content-Type: application/json" \\`)}
  ${dim(`  -H "X-PAYMENT: 0x<your_tx_hash>" \\`)}
  ${dim(`  -d '{"tool_name":"${toolName}","arguments":${JSON.stringify(toolArgs)}}'`)}
`);
      return;
    }

    const data = res.json();
    const result = data?.result ?? data;
    spin.stop(res.ok ? green(`✔ ${toolName} complete`) : red(`✘ ${toolName} failed`));

    if (jsonMode) { console.log(JSON.stringify(result, null, 2)); return; }

    // Pretty-print the result
    console.log(`\n${bold(`  ${toolName.toUpperCase().replace(/_/g, " ")}`)}\n`);
    function printObj(obj, indent = "  ") {
      if (typeof obj !== "object" || obj === null) { console.log(`${indent}${cyan(String(obj))}`); return; }
      if (Array.isArray(obj)) {
        obj.slice(0, 20).forEach((item, i) => {
          if (typeof item === "object") { console.log(`${indent}${dim("[" + i + "]")}`); printObj(item, indent + "  "); }
          else console.log(`${indent}${dim("[" + i + "]")} ${cyan(String(item))}`);
        });
        if (obj.length > 20) console.log(`${indent}${dim(`... +${obj.length - 20} more`)}`);
        return;
      }
      Object.entries(obj).slice(0, 30).forEach(([k, v]) => {
        if (typeof v === "object" && v !== null) { console.log(`${indent}${bold(k)}:`); printObj(v, indent + "  "); }
        else console.log(`${indent}${bold(k.padEnd(25))} ${cyan(String(v ?? ""))}`);
      });
    }
    printObj(result);
    console.log(`\n  ${dim(`Raw JSON: npx @axon-xlayer/start call ${toolName} --json`)}`);
    if (Object.keys(toolArgs).length === 0) {
      console.log(`  ${dim(`With args: npx @axon-xlayer/start call ${toolName} --args '{"key":"value"}' `)}\n`);
    } else { console.log(); }

  } catch (e) {
    spin.stop(red("✘ Failed"));
    console.error(red(e.message));
    process.exit(1);
  }
}

async function cmdHealth(jsonMode) {
  const spin = spinner("Checking AXON health...");
  try {
    const start = Date.now();
    const [healthRes, toolsRes] = await Promise.all([
      fetch(`${API}/health`),
      fetch(`${API}/mcp/tools`),
    ]);
    const latency = Date.now() - start;
    const health = healthRes.json();
    const tools = toolsRes.json();
    const toolCount = Array.isArray(tools?.tools) ? tools.tools.length : "?";
    spin.stop(green("✔ Health check complete"));
    if (jsonMode) {
      console.log(JSON.stringify({ status: health?.status ?? "ok", latency_ms: latency, tool_count: toolCount, api: API }, null, 2));
      return;
    }
    console.log(`
${bold("  AXON HEALTH CHECK")}

  Status:    ${health?.status === "ok" ? green("● LIVE") : yellow("● DEGRADED")}
  Latency:   ${latency < 500 ? green(latency + "ms") : latency < 2000 ? yellow(latency + "ms") : red(latency + "ms")}
  Tools:     ${cyan(toolCount + " MCP tools available")}
  API:       ${dim(API)}

  ${dim("Docs: " + API + "/docs")}
`);
  } catch (e) {
    spin.stop(red("✘ Health check failed"));
    console.log(`
  ${red("API may be sleeping.")} Render free tier cold starts in ~30s.
  ${dim("Try again in 30 seconds, or visit:")}
  ${dim(API)}
`);
    if (jsonMode) console.log(JSON.stringify({ status: "error", error: e.message }));
  }
}

// ─── Router ───────────────────────────────────────────────────────────────────
async function main() {
  const args = process.argv.slice(2);
  const jsonMode = args.includes("--json");
  const filteredArgs = args.filter(a => a !== "--json");
  const cmd = filteredArgs[0];

  if (args.includes("--version") || args.includes("-v")) {
    console.log(`@axon-xlayer/start v${VERSION}`);
    return;
  }

  if (args.includes("--help") || args.includes("-h")) {
    banner();
    console.log(`
  ${bold("Usage:")} npx @axon-xlayer/start [command] [args] [--json]

  ${bold("Commands:")}
    ${cyan("(no command)")}                       Full orient screen + live stats
    ${cyan("tools")} [keyword]                    List all 45 MCP tools (filter by keyword)
    ${cyan("call")} <tool> [--args '{}']          Call any of the 45 tools directly
    ${cyan("scan")} <token>                       Token security scan (6 sources)
    ${cyan("wallet")} <address>                   Wallet portfolio + token balances
    ${cyan("gas")}                                Live gas price on X Layer
    ${cyan("tasks")} [task-id]                    List tasks (or get single task detail)
    ${cyan("leaderboard")}                        Top agents by scans completed
    ${cyan("register")} <name> <wallet>           Register your agent
    ${cyan("health")}                             API health + latency check

  ${bold("Flags:")}
    ${cyan("--json")}    Machine-readable JSON output (for AI agents)
    ${cyan("--version")} Show version
    ${cyan("--help")}    Show this help

  ${bold("Examples:")}
    npx @axon-xlayer/start
    npx @axon-xlayer/start tools
    npx @axon-xlayer/start tools security
    npx @axon-xlayer/start call get_gas_price
    npx @axon-xlayer/start call get_rich_list --args '{"limit":5}'
    npx @axon-xlayer/start call get_wallet_portfolio --args '{"wallet_address":"0x..."}'
    npx @axon-xlayer/start scan 0x1e4a5963abfd975d8c9021ce480b42188849d41d
    npx @axon-xlayer/start wallet 0xDb82c0d91E057E05600C8F8dc836bEb41da6df14
    npx @axon-xlayer/start tasks
    npx @axon-xlayer/start tasks axon-002
    npx @axon-xlayer/start register my-agent 0xYourWallet
    npx @axon-xlayer/start --json > axon-context.json

  ${dim(`API: ${API}  |  Docs: ${API}/docs  |  LLMs: ${API}/llms.txt`)}
`);
    return;
  }

  switch (cmd) {
    case "scan":        return cmdScan(filteredArgs[1], jsonMode);
    case "wallet":      return cmdWallet(filteredArgs[1], jsonMode);
    case "gas":         return cmdGas(jsonMode);
    case "tasks":       return cmdTasks(filteredArgs[1], jsonMode);
    case "leaderboard": return cmdLeaderboard(jsonMode);
    case "register":    return cmdRegister(filteredArgs[1], filteredArgs[2], jsonMode);
    case "health":      return cmdHealth(jsonMode);
    case "tools":       return cmdTools(filteredArgs[1], jsonMode);
    case "call": {
      // Find --args value
      const argsIdx = args.indexOf("--args");
      const rawArgs = argsIdx !== -1 ? args[argsIdx + 1] : null;
      return cmdCall(filteredArgs[1], rawArgs, jsonMode);
    }
    default:            return cmdOrient(jsonMode);
  }
}

main().catch(e => { console.error(red(e.message)); process.exit(1); });
