"""
AI Agent Bridge for Global Shopify Modernization Orchestrator.
Enables the Orchestrator to coordinate external AI coding agents (Claude Code, OpenAI Codex, or direct LLM APIs)
as dynamic specialist subagents (Pattern A) with authentication checking, interactive login guidance,
and rich brand/social DNA context injection.
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

    def check_engine_auth(self, engine: str) -> Dict[str, Any]:
        """
        Check if a specific AI engine is authenticated and ready to execute.
        If it requires authentication, returns actionable login commands and diagnostic status.
        """
        engine = engine.lower()

        if engine == "codex":
            if not self.codex_path:
                return {
                    "engine": "codex",
                    "authenticated": False,
                    "available": False,
                    "message": "Codex CLI executable not found on system PATH."
                }
            try:
                proc = subprocess.run(
                    [self.codex_path, "login", "status"],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=8
                )
                output = proc.stdout.strip() + " " + proc.stderr.strip()
                if "Logged in" in output:
                    return {
                        "engine": "codex",
                        "authenticated": True,
                        "available": True,
                        "status": output.strip(),
                        "message": "Codex CLI authenticated and operational."
                    }
                else:
                    return {
                        "engine": "codex",
                        "authenticated": False,
                        "available": True,
                        "login_command": "codex login",
                        "message": "Codex CLI is not logged in. Run 'codex login' to authenticate."
                    }
            except Exception as exc:
                return {
                    "engine": "codex",
                    "authenticated": False,
                    "available": True,
                    "login_command": "codex login",
                    "message": f"Could not verify Codex login status: {exc}"
                }

        elif engine == "claude":
            if not self.claude_path:
                return {
                    "engine": "claude",
                    "authenticated": False,
                    "available": False,
                    "message": "Claude Code CLI executable not found on system PATH."
                }
            try:
                # Fast probe with short timeout
                proc = subprocess.Popen(
                    [self.claude_path, "-p", "echo ping", "--dangerously-skip-permissions"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = proc.communicate(input="", timeout=3)
                combined = stdout + " " + stderr
                if "OAuth session expired" in combined or "Failed to authenticate" in combined or proc.returncode != 0:
                    return {
                        "engine": "claude",
                        "authenticated": False,
                        "available": True,
                        "login_command": "claude login",
                        "message": "Claude Code OAuth session expired or not authenticated. Run 'claude login' to authenticate."
                    }
                return {
                    "engine": "claude",
                    "authenticated": True,
                    "available": True,
                    "message": "Claude Code CLI authenticated and operational."
                }
            except Exception as exc:
                return {
                    "engine": "claude",
                    "authenticated": False,
                    "available": True,
                    "login_command": "claude login",
                    "message": "Claude Code OAuth session expired or not authenticated. Run 'claude login' to authenticate."
                }

        elif engine == "anthropic_api":
            return {
                "engine": "anthropic_api",
                "authenticated": bool(self.anthropic_key),
                "available": bool(self.anthropic_key),
                "message": "Anthropic API Key configured." if self.anthropic_key else "ANTHROPIC_API_KEY environment variable not set."
            }

        elif engine == "openai_api":
            return {
                "engine": "openai_api",
                "authenticated": bool(self.openai_key),
                "available": bool(self.openai_key),
                "message": "OpenAI API Key configured." if self.openai_key else "OPENAI_API_KEY environment variable not set."
            }

        return {
            "engine": engine,
            "authenticated": False,
            "available": False,
            "message": f"Unknown engine '{engine}'."
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Inspect and report available AI agent execution engines and active selection."""
        # Check active selection from environment variable
        env_choice = (os.environ.get("ACTIVE_AI_AGENT") or os.environ.get("ORCHESTRATOR_AI_AGENT") or "auto").strip().lower()

        engines_info = {}
        if self.codex_path:
            engines_info["codex"] = self.check_engine_auth("codex")
        if self.claude_path:
            engines_info["claude"] = self.check_engine_auth("claude")
        if self.anthropic_key:
            engines_info["anthropic_api"] = self.check_engine_auth("anthropic_api")
        if self.openai_key:
            engines_info["openai_api"] = self.check_engine_auth("openai_api")

        available = list(engines_info.keys())

        # Determine active engine
        if env_choice in engines_info:
            active = env_choice
        elif env_choice == "none":
            active = "none"
        else:
            # Auto-selection: pick first authenticated engine
            active = "none"
            # Prioritize Codex if authenticated
            if engines_info.get("codex", {}).get("authenticated"):
                active = "codex"
            elif engines_info.get("claude", {}).get("authenticated"):
                active = "claude"
            elif engines_info.get("anthropic_api", {}).get("authenticated"):
                active = "anthropic_api"
            elif engines_info.get("openai_api", {}).get("authenticated"):
                active = "openai_api"
            elif available:
                active = available[0]

        return {
            "available_engines": available,
            "active_engine": active,
            "configured_choice": env_choice,
            "engines_auth": engines_info,
            "claude_cli_path": self.claude_path,
            "codex_cli_path": self.codex_path,
            "has_anthropic_api": bool(self.anthropic_key),
            "has_openai_api": bool(self.openai_key),
        }

    def ensure_authenticated(self, engine: str) -> Dict[str, Any]:
        """
        Verify that the chosen engine is logged in.
        If not, prompts the user with instructions to log in.
        """
        auth_status = self.check_engine_auth(engine)
        if not auth_status.get("authenticated", False):
            login_cmd = auth_status.get("login_command", f"{engine} login")
            msg = auth_status.get("message", f"Engine {engine} requires authentication.")
            print("\n" + "!" * 70)
            print(f"[!] AI AGENT AUTHENTICATION REQUIRED FOR '{engine.upper()}'")
            print(f"    Status: {msg}")
            print(f"    >> Action required: Open terminal and run: {login_cmd}")
            print("!" * 70 + "\n")
        return auth_status

    def invoke(
        self,
        prompt: str,
        cwd: Optional[str] = None,
        engine: str = "auto",
        timeout: int = 120,
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

        # Check authentication before invocation
        auth = self.ensure_authenticated(selected)
        if not auth.get("authenticated", False):
            # If auto and selected failed, attempt to find an alternate authenticated engine
            if engine == "auto":
                for alt in caps["available_engines"]:
                    alt_auth = self.check_engine_auth(alt)
                    if alt_auth.get("authenticated", False):
                        print(f"[*] Auto-switching AI engine from '{selected}' to authenticated '{alt}'...")
                        selected = alt
                        break

        # 1. OpenAI Codex CLI Dispatch
        if selected == "codex" and self.codex_path:
            return self._invoke_codex_cli(prompt, cwd=cwd, timeout=timeout)

        # 2. Claude Code CLI Dispatch
        if selected == "claude" and self.claude_path:
            return self._invoke_claude_cli(prompt, cwd=cwd, timeout=timeout, system_prompt=system_prompt)

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
        timeout: int = 120,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute non-interactive prompt via Claude Code CLI."""
        cmd = [self.claude_path, "-p", prompt, "--dangerously-skip-permissions"]
        if system_prompt:
            cmd.extend(["--append-system-prompt", system_prompt])

        try:
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            stdout, stderr = proc.communicate(input="", timeout=timeout)
            output = stdout.strip()

            if proc.returncode == 0:
                return {"success": True, "engine": "claude", "output": output, "error": None}
            else:
                err_msg = stderr.strip() or output or f"Process exited with code {proc.returncode}"
                return {"success": False, "engine": "claude", "output": output, "error": err_msg}

        except subprocess.TimeoutExpired:
            return {"success": False, "engine": "claude", "output": "", "error": f"Claude Code timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "engine": "claude", "output": "", "error": str(e)}

    def _invoke_codex_cli(
        self,
        prompt: str,
        cwd: Optional[str] = None,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """Execute non-interactive prompt via Codex CLI with clean EOF stdin closure."""
        cmd = [self.codex_path, "exec", "--dangerously-bypass-approvals-and-sandbox", prompt]
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            stdout, stderr = proc.communicate(input="", timeout=timeout)
            output = stdout.strip()

            if proc.returncode == 0:
                return {"success": True, "engine": "codex", "output": output, "error": None}
            else:
                err_msg = stderr.strip() or output or f"Codex exited with code {proc.returncode}"
                return {"success": False, "engine": "codex", "output": output, "error": err_msg}

        except subprocess.TimeoutExpired:
            return {"success": False, "engine": "codex", "output": "", "error": f"Codex timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "engine": "codex", "output": "", "error": str(e)}

    def _invoke_anthropic_api(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout: int = 90
    ) -> Dict[str, Any]:
        """Direct Anthropic Messages API dispatch."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.anthropic_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
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
        timeout: int = 90
    ) -> Dict[str, Any]:
        """Direct OpenAI Chat Completions API dispatch."""
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
        Ask AI coding agent (Claude Code / Codex / LLM) to inspect and refine generated Next.js 14 demo components
        using full Brand Dossier, Social DNA, and Archetype Layout rules.
        """
        source_dir = os.path.join(workspace, "demo", "source")
        if not os.path.exists(source_dir):
            return {"success": False, "error": f"Demo source directory not found at {source_dir}"}

        # 1. Load brand dossier
        dossier_file = os.path.join(workspace, "discovery", "brand_dossier.json")
        brand_dossier = {}
        if os.path.exists(dossier_file):
            try:
                with open(dossier_file, "r", encoding="utf-8") as f:
                    brand_dossier = json.load(f)
            except Exception:
                pass

        # 2. Load social DNA
        dna_file = os.path.join(workspace, "discovery", "social_dna.json")
        social_dna = {}
        if os.path.exists(dna_file):
            try:
                with open(dna_file, "r", encoding="utf-8") as f:
                    social_dna = json.load(f)
            except Exception:
                pass

        # 3. Load layout spec & tokens
        solution_file = os.path.join(workspace, "solution", "layout_spec.json")
        layout_spec = {}
        if os.path.exists(solution_file):
            try:
                with open(solution_file, "r", encoding="utf-8") as f:
                    layout_spec = json.load(f)
            except Exception:
                pass

        # 4. Load products catalog summary
        products_summary = "Niche-tailored inventory"
        pdata_path = os.path.join(source_dir, "data", "products.ts")
        if os.path.exists(pdata_path):
            try:
                with open(pdata_path, "r", encoding="utf-8") as pf:
                    pcontent = pf.read()
                    if "PRODUCTS: Product[] =" in pcontent:
                        json_str = pcontent.split("PRODUCTS: Product[] =")[1].strip().rstrip(";")
                        prods = json.loads(json_str)
                        products_summary = json.dumps([{
                            "name": p.get("name"),
                            "priceMad": p.get("priceMad"),
                            "category": p.get("category"),
                            "specs": p.get("specs", {})
                        } for p in prods[:4]], indent=2, ensure_ascii=False)
            except Exception:
                pass

        archetype_name = layout_spec.get("archetype_name") or brand_dossier.get("archetype_name", "E-Commerce Luxe")
        positioning = brand_dossier.get("positioning", "Excellence E-Commerce Maroc")
        vibe = social_dna.get("brand_vibe", "Modern Luxury")
        moodboard = json.dumps(social_dna.get("aesthetic_moodboard", {}), ensure_ascii=False)
        lexicon = json.dumps(social_dna.get("customer_lexicon", {}), ensure_ascii=False)
        hooks = json.dumps(social_dna.get("proven_ad_hooks", []), ensure_ascii=False)

        prompt = (
            f"You are a Principal Frontend Architect modernizing '{brand_name}' from Shopify to Next.js 14 App Router and Tailwind CSS.\n\n"
            f"=== 💎 BRAND IDENTITY & SOCIAL DNA ===\n"
            f"- Brand Vibe: {vibe}\n"
            f"- Positioning: {positioning}\n"
            f"- Slogan: {brand_dossier.get('slogan', '')}\n"
            f"- Aesthetic Moodboard: {moodboard}\n"
            f"- Customer Lexicon (French & Darija): {lexicon}\n"
            f"- Proven Ad Hooks: {hooks}\n\n"
            f"=== 📐 ARCHETYPE & UX BLUEPRINT ===\n"
            f"- Archetype: {archetype_name} ({layout_spec.get('page_family', 'luxury_editorial')})\n"
            f"- Density: {layout_spec.get('density', 'spacious_cinematic')}\n"
            f"- Hero Variant: {layout_spec.get('layout_components', {}).get('hero_variant', 'Hero')}\n"
            f"- Catalog Variant: {layout_spec.get('layout_components', {}).get('catalog_variant', 'ProductGrid')}\n"
            f"- Card Anatomy: {layout_spec.get('layout_components', {}).get('product_card_anatomy', 'editorial_framed_card')}\n\n"
            f"=== 📦 INVENTORY & REAL SPECS ===\n"
            f"{products_summary}\n\n"
            f"=== 🛠️ MANDATE (EDIT IN PLACE) ===\n"
            f"Review the generated Next.js 14 React components located in 'components/' and 'app/page.tsx':\n"
            f"1. Hero Section ('components/Hero.tsx'): Align the typography, headline, and atmospheric lighting to match the Brand Vibe ({vibe}).\n"
            f"2. Product Cards ('components/ProductCard.tsx'): Ensure cards display real specs and Moroccan MAD currency formatting ({brand_dossier.get('currency', 'MAD')}). Never display generic dashcam tags.\n"
            f"3. Social Proof & Stories ('components/InstagramStories.tsx' & 'components/SocialUgcGrid.tsx'): Populate authentic customer voices in French and Darija from the Customer Lexicon.\n"
            f"4. Fast COD Modal ('components/CodModal.tsx'): Verify smooth Moroccan phone validation (+212) and clear Cash On Delivery reassurance.\n"
            f"Apply any code refinements directly to the existing files."
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
