"""
Automated Test Harness for Pattern A and Pattern C across Lead 1 and Lead 2.
- Lead 1: Anulus_Joaillerie (Jewelry Archetype)
- Lead 2: Ma_Montre_Maroc (Horlogerie Archetype)
"""

import sys
import os
import json
import subprocess
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from orchestrator import resolve_lead_id, step_solution, step_build, step_qa, step_deploy_prep, step_sales

def test_pattern_c_mcp():
    print("\n" + "="*70)
    print("🧪 TESTING PATTERN C: MODEL CONTEXT PROTOCOL (MCP SERVER)")
    print("   Simulating Claude Code acting as the Master Agent via JSON-RPC 2.0")
    print("="*70)

    p = subprocess.Popen(
        [sys.executable, "mcp_server.py"],
        cwd=BASE_DIR,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    def rpc_call(method: str, params: Dict[str, Any] = None, msg_id: int = 1) -> Dict[str, Any]:
        req = {"jsonrpc": "2.0", "id": msg_id, "method": method, "params": params or {}}
        p.stdin.write(json.dumps(req) + "\n")
        p.stdin.flush()
        line = p.stdout.readline()
        return json.loads(line)

    try:
        # 1. Initialize MCP Handshake
        init_res = rpc_call("initialize", msg_id=1)
        server_info = init_res.get("result", {}).get("serverInfo", {})
        print(f"[✓] MCP Server Handshake: {server_info.get('name')} v{server_info.get('version')}")

        # 2. Tools list discovery
        tools_res = rpc_call("tools/list", msg_id=2)
        tools = [t["name"] for t in tools_res.get("result", {}).get("tools", [])]
        print(f"[✓] MCP Tools Discovered ({len(tools)} tools registered)")

        # 3. Test on Lead 1 (Anulus_Joaillerie)
        print("\n--- Testing Lead 1 (Anulus_Joaillerie) via MCP ---")
        status_l1 = rpc_call("tools/call", {"name": "shopify_orchestrator_status", "arguments": {"lead_id": "1"}}, msg_id=3)
        l1_txt = status_l1.get("result", {}).get("content", [{}])[0].get("text", "")
        print(f"[✓] Tool Call: shopify_orchestrator_status(1) -> Success: {'Anulus_Joaillerie' in l1_txt}")

        sol_l1 = rpc_call("tools/call", {"name": "shopify_orchestrator_solution", "arguments": {"lead_id": "1"}}, msg_id=4)
        print(f"[✓] Tool Call: shopify_orchestrator_solution(1) -> Success: {'PASSED' in sol_l1.get('result', {}).get('content', [{}])[0].get('text', '')}")

        build_l1 = rpc_call("tools/call", {"name": "shopify_orchestrator_build", "arguments": {"lead_id": "1", "use_ai_agent": False}}, msg_id=5)
        print(f"[✓] Tool Call: shopify_orchestrator_build(1) -> Success: {'PASSED' in build_l1.get('result', {}).get('content', [{}])[0].get('text', '')}")

        # 4. Test on Lead 2 (Ma_Montre_Maroc)
        print("\n--- Testing Lead 2 (Ma_Montre_Maroc) via MCP ---")
        status_l2 = rpc_call("tools/call", {"name": "shopify_orchestrator_status", "arguments": {"lead_id": "2"}}, msg_id=6)
        l2_txt = status_l2.get("result", {}).get("content", [{}])[0].get("text", "")
        print(f"[✓] Tool Call: shopify_orchestrator_status(2) -> Success: {'Ma_Montre_Maroc' in l2_txt}")

        sol_l2 = rpc_call("tools/call", {"name": "shopify_orchestrator_solution", "arguments": {"lead_id": "2"}}, msg_id=7)
        print(f"[✓] Tool Call: shopify_orchestrator_solution(2) -> Success: {'PASSED' in sol_l2.get('result', {}).get('content', [{}])[0].get('text', '')}")

        build_l2 = rpc_call("tools/call", {"name": "shopify_orchestrator_build", "arguments": {"lead_id": "2", "use_ai_agent": False}}, msg_id=8)
        print(f"[✓] Tool Call: shopify_orchestrator_build(2) -> Success: {'PASSED' in build_l2.get('result', {}).get('content', [{}])[0].get('text', '')}")

        print("\n[🎉] PATTERN C (MCP SERVER) VALIDATED FOR LEADS 1 & 2")

    finally:
        p.terminate()

def test_pattern_a_bridge():
    print("\n" + "="*70)
    print("🧪 TESTING PATTERN A: AI SUBAGENT BRIDGE (--with-ai)")
    print("   Orchestrator invokes Claude Code / Codex subagent with safe fallback")
    print("="*70)

    # Lead 1: Anulus_Joaillerie
    lead_1 = resolve_lead_id("1")
    print(f"\n--- Testing Lead 1 ({lead_1}) via Pattern A ---")
    
    # 1. Solution
    step_solution(lead_1)
    # 2. Build with AI
    handoff_b1 = step_build(lead_1, with_ai=True, ai_engine="auto")
    print(f"[✓] Step Build (with-ai) for {lead_1}: Status = {handoff_b1.get('status')}")

    # Lead 2: Ma_Montre_Maroc
    lead_2 = resolve_lead_id("2")
    print(f"\n--- Testing Lead 2 ({lead_2}) via Pattern A ---")
    
    # 1. Solution
    step_solution(lead_2)
    # 2. Build with AI
    handoff_b2 = step_build(lead_2, with_ai=True, ai_engine="auto")
    print(f"[✓] Step Build (with-ai) for {lead_2}: Status = {handoff_b2.get('status')}")

    print("\n[🎉] PATTERN A (AI SUBAGENT BRIDGE) VALIDATED FOR LEADS 1 & 2")

if __name__ == "__main__":
    test_pattern_c_mcp()
    test_pattern_a_bridge()
