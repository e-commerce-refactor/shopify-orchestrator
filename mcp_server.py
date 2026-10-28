#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for the Global Shopify Modernization Orchestrator.
Exposes the complete multi-agent pipeline as standard MCP tools (Pattern C).

Compatible with:
- Claude Code (`claude mcp add shopify-orchestrator python path/to/mcp_server.py`)
- OpenAI Codex (`codex mcp add shopify-orchestrator python path/to/mcp_server.py`)
- Cursor IDE
- Claude Desktop
- Antigravity / Gemini

Zero third-party dependencies: runs on pure Python 3.10+ standard library.
"""

import sys
import os
import json
import io
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, List, Optional

# Ensure UTF-8 I/O
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from orchestrator import (
    step_intake,
    step_discovery,
    step_audit,
    step_solution,
    step_build,
    step_qa,
    step_deploy_prep,
    step_sales,
    run_all,
    resolve_lead_id,
    generate_lead_id,
    normalize_url,
    load_lead_run,
    LEADS_DIR,
)
from agents.skills.ai_bridge import bridge

# Define MCP Tool Schemas
TOOLS_METADATA = [
    {
        "name": "shopify_orchestrator_assess",
        "description": "Intake a Shopify store URL and brand name into the modernization pipeline. Sets up dedicated workspace under leads/<brand>.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Storefront URL (e.g. 'https://flexshoes.ma' or 'anulus.ma')"
                },
                "brand_name": {
                    "type": "string",
                    "description": "Human-readable brand name (optional; inferred if omitted)"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "shopify_orchestrator_discover",
        "description": "Collect public storefront evidence, /products.json catalog, social proof (Instagram/Facebook OSINT), and classify the brand archetype.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lead_id": {
                    "type": "string",
                    "description": "Lead identifier (e.g. '70mai_Maroc') or 1-based index (e.g. '1')"
                }
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "shopify_orchestrator_audit",
        "description": "Audit storefront performance, count third-party tracking scripts, and compute financial drain (Shopify 2% transaction fee penalty on COD + app costs).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lead_id": {
                    "type": "string",
                    "description": "Lead identifier or 1-based index"
                }
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "shopify_orchestrator_solution",
        "description": "Formulate modernization solution: design archetype, design tokens, 60fps GPU motion profile, and Architecture Decision Record (ADR).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lead_id": {
                    "type": "string",
                    "description": "Lead identifier or 1-based index"
                }
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "shopify_orchestrator_build",
        "description": "Scaffold the high-performance Next.js 14 App Router, Tailwind CSS, and localized COD checkout demo codebase. Optionally invoke Claude Code or Codex for AI component enhancement.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lead_id": {
                    "type": "string",
                    "description": "Lead identifier or 1-based index"
                },
                "use_ai_agent": {
                    "type": "boolean",
                    "description": "Whether to dispatch to Claude Code or Codex to refine code",
                    "default": False
                },
                "ai_engine": {
                    "type": "string",
                    "enum": ["claude", "codex", "auto"],
                    "description": "AI engine to use if use_ai_agent is True",
                    "default": "auto"
                }
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "shopify_orchestrator_qa",
        "description": "Execute automated QA verification across responsiveness, Moroccan phone number regex validation, security headers, and build tests. Can optionally invoke AI to autofix blockers.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lead_id": {
                    "type": "string",
                    "description": "Lead identifier or 1-based index"
                },
                "autofix_with_ai": {
                    "type": "boolean",
                    "description": "If true and QA finds issues, dispatch AI agent to patch the code",
                    "default": False
                }
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "shopify_orchestrator_deploy",
        "description": "Generate deployment plan or live provision GitHub repo, Supabase PostgreSQL with RLS, and Vercel Edge instance.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lead_id": {
                    "type": "string",
                    "description": "Lead identifier or 1-based index"
                },
                "live": {
                    "type": "boolean",
                    "description": "Set to true to execute live provisioning (creates real GitHub, Supabase, Vercel resources)",
                    "default": False
                }
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "shopify_orchestrator_sales",
        "description": "Generate respectful, audit-backed sales outreach letters in French and Moroccan Darija citing verified store facts and savings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lead_id": {
                    "type": "string",
                    "description": "Lead identifier or 1-based index"
                },
                "use_ai_agent": {
                    "type": "boolean",
                    "description": "Whether to use Claude Code / Codex for hyper-personalized copywriting",
                    "default": False
                }
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "shopify_orchestrator_run_all",
        "description": "Execute the complete modernization pipeline end-to-end in one single call (Intake -> Discovery -> Audit -> Solution -> Build -> QA -> Deploy -> Sales).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "Lead ID, 1-based index (e.g. '1'), or storefront URL"
                },
                "live_deploy": {
                    "type": "boolean",
                    "description": "Whether to run live GitHub/Supabase/Vercel deployment",
                    "default": False
                },
                "use_ai_agent": {
                    "type": "boolean",
                    "description": "Whether to enable AI agent enhancements in builder & sales",
                    "default": False
                }
            },
            "required": ["target"]
        }
    },
    {
        "name": "shopify_orchestrator_status",
        "description": "Retrieve current state machine stage, quality gate results, and findings for a lead.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lead_id": {
                    "type": "string",
                    "description": "Lead identifier or 1-based index"
                }
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "shopify_orchestrator_list_leads",
        "description": "List all tracked Shopify stores in the local pipeline with their current stage.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "shopify_orchestrator_ai_status",
        "description": "Inspect local AI agent availability (Claude Code CLI, Codex CLI, Anthropic API, OpenAI API).",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

def capture_execution(func, *args, **kwargs):
    """Run a function capturing printed output and returning (result, stdout_str)."""
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        res = func(*args, **kwargs)
    return res, buf.getvalue()

def execute_tool(name: str, args: Dict[str, Any]) -> str:
    """Dispatch MCP tool execution to Orchestrator functions."""
    try:
        if name == "shopify_orchestrator_assess":
            raw_url = args["url"]
            brand_name = args.get("brand_name")
            normalized = normalize_url(raw_url)
            lead_id = generate_lead_id(normalized, brand_name)
            _, out = capture_execution(step_intake, lead_id, target_url=normalized, brand_name=brand_name)
            return f"Assessed and initialized lead '{lead_id}'.\n\nExecution Log:\n{out}"

        elif name == "shopify_orchestrator_discover":
            lead_id = resolve_lead_id(args["lead_id"])
            handoff, out = capture_execution(step_discovery, lead_id)
            return f"Discovery completed for '{lead_id}' (Status: {handoff.get('status')}).\n\n{out}"

        elif name == "shopify_orchestrator_audit":
            lead_id = resolve_lead_id(args["lead_id"])
            handoff, out = capture_execution(step_audit, lead_id)
            return f"Audit completed for '{lead_id}' (Status: {handoff.get('status')}).\n\n{out}"

        elif name == "shopify_orchestrator_solution":
            lead_id = resolve_lead_id(args["lead_id"])
            handoff, out = capture_execution(step_solution, lead_id)
            return f"Solution synthesized for '{lead_id}' (Status: {handoff.get('status')}).\n\n{out}"

        elif name == "shopify_orchestrator_build":
            lead_id = resolve_lead_id(args["lead_id"])
            use_ai = bool(args.get("use_ai_agent", False))
            ai_engine = args.get("ai_engine", "auto")
            handoff, out = capture_execution(step_build, lead_id)
            
            ai_out = ""
            if use_ai:
                workspace = os.path.join(LEADS_DIR, lead_id)
                ai_res = bridge.enhance_storefront(workspace, lead_id.replace("_", " "), engine=ai_engine)
                ai_out = f"\nAI Enhancement ({ai_res.get('engine')}): Success={ai_res.get('success')}\n{ai_res.get('output') or ai_res.get('error')}"

            return f"Demo build completed for '{lead_id}' (Status: {handoff.get('status')}).\n\n{out}{ai_out}"

        elif name == "shopify_orchestrator_qa":
            lead_id = resolve_lead_id(args["lead_id"])
            handoff, out = capture_execution(step_qa, lead_id)
            
            ai_out = ""
            if args.get("autofix_with_ai", False) and handoff.get("status") == "failed":
                workspace = os.path.join(LEADS_DIR, lead_id)
                qa_file = os.path.join(workspace, "demo", "qa_report.json")
                if os.path.exists(qa_file):
                    with open(qa_file, "r", encoding="utf-8") as f:
                        qdata = json.load(f)
                    fix_res = bridge.qa_autofix(workspace, qdata)
                    ai_out = f"\nAI Autofix Attempt ({fix_res.get('engine')}): {fix_res.get('output') or fix_res.get('error')}"

            return f"QA verification completed for '{lead_id}' (Status: {handoff.get('status')}).\n\n{out}{ai_out}"

        elif name == "shopify_orchestrator_deploy":
            lead_id = resolve_lead_id(args["lead_id"])
            live = bool(args.get("live", False))
            handoff, out = capture_execution(step_deploy_prep, lead_id, live=live)
            return f"Deployment {'execution' if live else 'preparation'} completed for '{lead_id}' (Status: {handoff.get('status')}).\n\n{out}"

        elif name == "shopify_orchestrator_sales":
            lead_id = resolve_lead_id(args["lead_id"])
            handoff, out = capture_execution(step_sales, lead_id)
            return f"Sales outreach drafted for '{lead_id}' (Status: {handoff.get('status')}).\n\n{out}"

        elif name == "shopify_orchestrator_run_all":
            target = args["target"]
            live = bool(args.get("live_deploy", False))
            lead_id = resolve_lead_id(target)
            _, out = capture_execution(run_all, lead_id, live=live)
            return f"Full lifecycle completed for '{lead_id}'.\n\n{out}"

        elif name == "shopify_orchestrator_status":
            lead_id = resolve_lead_id(args["lead_id"])
            lead_data, run_data = load_lead_run(lead_id)
            if not lead_data:
                return f"Lead '{lead_id}' not found."
            return json.dumps({"lead": lead_data, "run": run_data}, indent=2, ensure_ascii=False)

        elif name == "shopify_orchestrator_list_leads":
            if not os.path.exists(LEADS_DIR):
                return "No leads workspace found."
            leads = [d for d in os.listdir(LEADS_DIR) if os.path.isdir(os.path.join(LEADS_DIR, d))]
            items = []
            for lid in leads:
                ldata, rdata = load_lead_run(lid)
                if ldata and rdata:
                    items.append({
                        "lead_id": lid,
                        "brand_name": ldata.get("brand_name"),
                        "target_url": ldata.get("target_url"),
                        "stage": rdata.get("stage"),
                        "status": rdata.get("status")
                    })
            return json.dumps({"total": len(items), "leads": items}, indent=2, ensure_ascii=False)

        elif name == "shopify_orchestrator_ai_status":
            caps = bridge.get_capabilities()
            return json.dumps(caps, indent=2, ensure_ascii=False)

        else:
            return f"Unknown tool: '{name}'"

    except Exception as e:
        return f"Error executing tool '{name}': {type(e).__name__}: {str(e)}"

def send_response(resp: Dict[str, Any]):
    """Write standard JSON-RPC 2.0 response to stdout."""
    payload = json.dumps(resp, ensure_ascii=False)
    sys.stdout.write(payload + "\n")
    sys.stdout.flush()

def handle_message(msg: Dict[str, Any]):
    """Process incoming JSON-RPC 2.0 message."""
    msg_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params", {})

    # 1. Initialize
    if method == "initialize":
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "shopify-modernization-orchestrator",
                    "version": "1.0.0"
                }
            }
        })
        return

    # 2. Initialized Notification
    if method == "notifications/initialized":
        # Notification: no response needed
        return

    # 3. Ping
    if method == "ping":
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {}
        })
        return

    # 4. Tools List
    if method == "tools/list":
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": TOOLS_METADATA
            }
        })
        return

    # 5. Tools Call
    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        result_text = execute_tool(tool_name, tool_args)
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
        })
        return

    # Unknown Method
    if msg_id is not None:
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: '{method}'"
            }
        })

def run_server():
    """Main stdio JSON-RPC loop supporting line-delimited and Content-Length framed streams."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue

            # Support Content-Length header framing if present
            if line.lower().startswith("content-length:"):
                length = int(line.split(":")[1].strip())
                # Read until empty line
                while True:
                    hdr = sys.stdin.readline()
                    if not hdr or hdr.strip() == "":
                        break
                raw_body = sys.stdin.read(length)
                msg = json.loads(raw_body)
                handle_message(msg)
            else:
                # Direct JSON line
                msg = json.loads(line)
                handle_message(msg)

        except json.JSONDecodeError:
            continue
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            # Send JSON-RPC internal error if possible
            try:
                send_response({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal server error: {str(e)}"
                    }
                })
            except Exception:
                pass

if __name__ == "__main__":
    run_server()
