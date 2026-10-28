"""
AI Agent Bridge for Global Shopify Modernization Orchestrator.
Enables the Orchestrator to coordinate external AI coding agents (Claude Code, OpenAI Codex, or direct LLM APIs)
as dynamic specialist subagents (Pattern A) with graceful fallback to deterministic pipelines.
"""

import os
import sys
import json
import shutil
import subprocess
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

def find_executable(name: str) -> Optional[str]:
    """Locate CLI executable on Windows or POSIX."""
    found = shutil.which(name)
    if found:
        return found
    if sys.platform == "win32":
        # Check standard user local bin paths
        candidates = [
            os.path.expandvars(rf"%USERPROFILE%\.local\bin\{name}.exe"),
            os.path.expandvars(rf"%USERPROFILE%\AppData\Local\Programs\OpenAI\Codex\bin\{name}.exe"),
            os.path.expandvars(rf"%LOCALAPPDATA%\Programs\{name}\{name}.exe"),
            os.path.expandvars(rf"%APPDATA%\npm\{name}.cmd"),
            os.path.expandvars(rf"%ProgramFiles%\{name}\{name}.exe"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
    return None

class AIAgentBridge:
    """Universal AI coding agent dispatcher supporting Claude Code, Codex, and direct LLM APIs."""

    def __init__(self):
        self.claude_path = find_executable("claude")
        self.codex_path = find_executable("codex")
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        self.openai_key = os.environ.get("OPENAI_API_KEY", "").strip()

    def get_capabilities(self) -> Dict[str, Any]:
        """Inspect and report available AI agent execution engines."""
        engines = []
        if self.claude_path:
            engines.append("claude")
        if self.codex_path:
            engines.append("codex")
        if self.anthropic_key:
            engines.append("anthropic_api")
        if self.openai_key:
            engines.append("openai_api")

        preferred = os.environ.get("ORCHESTRATOR_AI_AGENT", "").strip().lower()
        if preferred and preferred in ["claude", "codex", "anthropic_api", "openai_api", "none"]:
            active = preferred
        elif "claude" in engines:
            active = "claude"
        elif "codex" in engines:
            active = "codex"
        elif engines:
            active = engines[0]
        else:
            active = "none"

        return {
            "available_engines": engines,
            "active_engine": active,
            "claude_cli_path": self.claude_path,
            "codex_cli_path": self.codex_path,
            "has_anthropic_api": bool(self.anthropic_key),
            "has_openai_api": bool(self.openai_key),
        }

    def invoke(
        self,
        prompt: str,
        cwd: Optional[str] = None,
        engine: str = "auto",
        timeout: int = 90,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute an AI prompt using the selected engine.
        Returns a dict: {"success": bool, "engine": str, "output": str, "error": str | None}
        """
        caps = self.get_capabilities()
        selected = engine.lower() if engine and engine != "auto" else caps["active_engine"]

        if selected == "none" or not caps["available_engines"]:
            return {
                "success": False,
                "engine": "none",
                "output": "",
                "error": "No AI coding agent (Claude Code, Codex, or API keys) available or AI is disabled."
            }

        # 1. Claude Code CLI Dispatch
        if selected == "claude" and self.claude_path:
            return self._invoke_claude_cli(prompt, cwd=cwd, timeout=timeout, system_prompt=system_prompt)

        # 2. OpenAI Codex CLI Dispatch
        if selected == "codex" and self.codex_path:
            return self._invoke_codex_cli(prompt, cwd=cwd, timeout=timeout)

        # 3. Direct Anthropic API Fallback
        if selected in ("anthropic_api", "claude") and self.anthropic_key:
            return self._invoke_anthropic_api(prompt, system_prompt=system_prompt, timeout=timeout)

        # 4. Direct OpenAI API Fallback
        if selected in ("openai_api", "codex") and self.openai_key:
            return self._invoke_openai_api(prompt, system_prompt=system_prompt, timeout=timeout)

        return {
            "success": False,
            "engine": selected,
            "output": "",
            "error": f"Engine '{selected}' requested but required binary/credentials are not configured."
        }

    def _invoke_claude_cli(
        self,
        prompt: str,
        cwd: Optional[str] = None,
        timeout: int = 90,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute non-interactive prompt via Claude Code CLI."""
        cmd = [self.claude_path, "-p", prompt, "--dangerously-skip-permissions"]
        if system_prompt:
            cmd.extend(["--append-system-prompt", system_prompt])

        try:
            # We redirect stdin to DEVNULL so Claude Code doesn't wait for interactive input
            proc = subprocess.run(
                cmd,
                cwd=cwd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )
            output = proc.stdout.strip()
            stderr = proc.stderr.strip()

            if proc.returncode == 0:
                return {"success": True, "engine": "claude", "output": output, "error": None}
            else:
                err_msg = stderr or output or f"Process exited with code {proc.returncode}"
                return {"success": False, "engine": "claude", "output": output, "error": err_msg}

        except subprocess.TimeoutExpired:
            return {"success": False, "engine": "claude", "output": "", "error": f"Claude Code timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "engine": "claude", "output": "", "error": str(e)}

    def _invoke_codex_cli(
        self,
        prompt: str,
        cwd: Optional[str] = None,
        timeout: int = 90
    ) -> Dict[str, Any]:
        """Execute non-interactive prompt via Codex CLI."""
        cmd = [self.codex_path, "exec", "--dangerously-bypass-approvals-and-sandbox", prompt]
        try:
            proc = subprocess.run(
                cmd,
                cwd=cwd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )
            output = proc.stdout.strip()
            stderr = proc.stderr.strip()

            if proc.returncode == 0:
                return {"success": True, "engine": "codex", "output": output, "error": None}
            else:
                err_msg = stderr or output or f"Codex exited with code {proc.returncode}"
                return {"success": False, "engine": "codex", "output": output, "error": err_msg}

        except subprocess.TimeoutExpired:
            return {"success": False, "engine": "codex", "output": "", "error": f"Codex timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "engine": "codex", "output": "", "error": str(e)}

    def _invoke_anthropic_api(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """Direct Anthropic REST API call using pure standard library (no pip dependencies required)."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        body: Dict[str, Any] = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system_prompt:
            body["system"] = system_prompt

        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
                return {"success": True, "engine": "anthropic_api", "output": text, "error": None}
        except Exception as e:
            return {"success": False, "engine": "anthropic_api", "output": "", "error": str(e)}

    def _invoke_openai_api(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """Direct OpenAI REST API call using pure standard library (no pip dependencies required)."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": "gpt-4o",
            "messages": messages,
            "temperature": 0.3
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {"success": True, "engine": "openai_api", "output": text, "error": None}
        except Exception as e:
            return {"success": False, "engine": "openai_api", "output": "", "error": str(e)}

    # High-level domain workflows
    def enhance_storefront(self, workspace: str, brand_name: str, engine: str = "auto") -> Dict[str, Any]:
        """
        Ask Claude Code / Codex to inspect and refine generated Next.js 14 demo components.
        """
        source_dir = os.path.join(workspace, "demo", "source")
        if not os.path.exists(source_dir):
            return {"success": False, "error": f"Demo source directory not found at {source_dir}"}

        solution_file = os.path.join(workspace, "solution", "layout_spec.json")
        layout_spec = {}
        if os.path.exists(solution_file):
            try:
                with open(solution_file, "r", encoding="utf-8") as f:
                    layout_spec = json.load(f)
            except Exception:
                pass

        archetype = layout_spec.get("archetype_name", "High-Converting COD E-Commerce")
        prompt = (
            f"You are a Senior Frontend Engineer modernizing '{brand_name}' from Shopify to Next.js 14 App Router and Tailwind CSS.\n"
            f"Archetype: {archetype}.\n"
            f"Review the generated React components in 'src/components/' and 'src/app/page.tsx'.\n"
            f"1. Refine the typography, Moroccan MAD pricing formatting, and responsive padding.\n"
            f"2. Ensure the COD checkout modal has seamless animations and GSM validation.\n"
            f"3. Make any code polishing edits directly in place."
        )

        res = self.invoke(prompt, cwd=source_dir, engine=engine, timeout=120)

        # Log AI enhancement artifact
        log_path = os.path.join(workspace, "demo", "ai_enhancement.json")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump({
                    "timestamp": utc_now_iso(),
                    "agent_engine": res.get("engine"),
                    "status": "enhanced" if res["success"] else "fallback_retained",
                    "details": res.get("output") if res["success"] else res.get("error")
                }, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        return res

    def craft_sales_outreach(
        self,
        workspace: str,
        brand_name: str,
        target_url: str,
        engine: str = "auto"
    ) -> Dict[str, Any]:
        """
        Use Claude Code / Codex / LLM to compose hyper-personalized bilingual sales pitches.
        """
        audit_file = os.path.join(workspace, "audit", "audit_report.json")
        audit_data = {}
        if os.path.exists(audit_file):
            try:
                with open(audit_file, "r", encoding="utf-8") as f:
                    audit_data = json.load(f)
            except Exception:
                pass

        facts = audit_data.get("measured_storefront_facts", {})
        financial = audit_data.get("financial_analysis", {})

        prompt = (
            f"You are an Elite E-Commerce Growth Consultant crafting a migration pitch for Moroccan brand '{brand_name}' ({target_url}).\n"
            f"Measured Facts:\n"
            f"- Scripts detected: {facts.get('external_script_count', 0)}\n"
            f"- Apps detected: {', '.join(facts.get('detected_apps', []))}\n"
            f"- Estimated annual Shopify & App drain: {financial.get('estimated_annual_cost_mad', 0):,} MAD\n\n"
            f"Draft two distinct, respectful, high-converting messages citing these exact facts:\n"
            f"1. French Executive Email for the CEO/Founder.\n"
            f"2. Conversational Moroccan Darija WhatsApp audio script/text.\n"
            f"Include an explicit STOP opt-out at the end of each message."
        )

        res = self.invoke(prompt, cwd=workspace, engine=engine, timeout=90)
        return res

    def qa_autofix(self, workspace: str, qa_report: Dict[str, Any], engine: str = "auto") -> Dict[str, Any]:
        """
        Autonomous QA Loop: If QA detects issues, dispatch Claude Code or Codex to fix the offending code.
        """
        source_dir = os.path.join(workspace, "demo", "source")
        blockers = qa_report.get("blockers", [])
        if not blockers:
            return {"success": True, "output": "No QA blockers to fix."}

        prompt = (
            f"The following automated QA checks failed on the Next.js 14 demo project:\n"
            + "\n".join(f"- {b}" for b in blockers) + "\n\n"
            f"Fix the offending TypeScript or CSS files in place so that all checks pass."
        )

        return self.invoke(prompt, cwd=source_dir, engine=engine, timeout=90)

# Global singleton bridge instance
bridge = AIAgentBridge()
