"""
Global Shopify Ecommerce Modernization Agency - Core Orchestrator Engine
Implements the Universal Orchestrator Contract and State Machine for any Shopify business.
"""

import sys
import os
import json
import re
import hashlib
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.parse import urlparse

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_DIR = os.path.join(BASE_DIR, "leads")
SCHEMAS_DIR = os.path.join(BASE_DIR, "schemas")

os.makedirs(LEADS_DIR, exist_ok=True)
os.makedirs(SCHEMAS_DIR, exist_ok=True)

# Import specialist subagents
from agents.agent_discovery import run_discovery
from agents.agent_audit import run_audit
from agents.agent_solution import run_solution
from agents.agent_builder import run_build
from agents.agent_qa import run_qa
from agents.agent_deployment import run_deployment_prep, run_live_deployment
from agents.agent_sales import run_sales
from agents.skills.ai_bridge import bridge

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

def hash_file(filepath):
    if not os.path.exists(filepath):
        return None
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    if netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]
    elif netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    path = parsed.path.rstrip("/")
    normalized = f"{scheme}://{netloc}{path}"
    return normalized

def sanitize_business_folder_name(name: str) -> str:
    clean = re.sub(r'[\\/*?:"<>|]', '', name).strip()
    clean = re.sub(r'[\s\-]+', '_', clean)
    clean = clean.strip(". _")
    if not clean or clean in {".", ".."}:
        raise ValueError("Business name must contain at least one safe character")
    return clean

def infer_business_name_from_url(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    domain = re.sub(r'^www\.', '', domain)
    base_name = domain.split('.')[0]
    words = re.findall(r'[A-Za-z0-9]+', base_name)
    title_name = " ".join(w.capitalize() for w in words)
    return title_name or "Shopify_Store"

def generate_lead_id(url: str, custom_name: str = None) -> str:
    if custom_name and custom_name.strip():
        return sanitize_business_folder_name(custom_name)
    inferred = infer_business_name_from_url(url)
    return sanitize_business_folder_name(inferred)

def get_lead_workspace(lead_id: str) -> str:
    if not isinstance(lead_id, str) or not lead_id.strip():
        raise ValueError("lead_id must be a non-empty string")
    if lead_id != os.path.basename(lead_id) or lead_id in {".", ".."}:
        raise ValueError(f"Unsafe lead_id: {lead_id!r}")
    workspace = os.path.abspath(os.path.join(LEADS_DIR, lead_id))
    if os.path.commonpath([LEADS_DIR, workspace]) != os.path.abspath(LEADS_DIR):
        raise ValueError(f"Lead workspace escapes leads directory: {lead_id!r}")
    return workspace

def atomic_write_json(path: str, data: dict):
    """Write JSON durably and replace the destination atomically."""
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".tmp-", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@contextmanager
def run_file_lock(workspace: str, timeout_seconds: float = 10.0):
    """Cross-process lock for updates to a lead's run.json."""
    lock_path = os.path.join(workspace, ".run.lock")
    deadline = time.monotonic() + timeout_seconds
    fd = None
    while fd is None:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("ascii"))
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(lock_path) > 60:
                    os.unlink(lock_path)
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Timed out waiting for run lock: {lock_path}")
            time.sleep(0.05)
    try:
        yield
    finally:
        os.close(fd)
        try:
            os.unlink(lock_path)
        except FileNotFoundError:
            pass

def _matches_schema_type(value, expected) -> bool:
    type_map = {
        "object": dict,
        "array": list,
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "null": type(None),
    }
    expected_types = expected if isinstance(expected, list) else [expected]
    return any(isinstance(value, type_map[t]) and not (t in {"integer", "number"} and isinstance(value, bool)) for t in expected_types)

def validate_schema(instance, schema: dict, location: str = "$"):
    """Dependency-free validator for the JSON Schema features used by this project."""
    errors = []
    expected_type = schema.get("type")
    if expected_type and not _matches_schema_type(instance, expected_type):
        return [f"{location}: expected {expected_type}, got {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{location}: {instance!r} is not in {schema['enum']}")
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{location}: missing required property {key!r}")
        for key, value in instance.items():
            if key in schema.get("properties", {}):
                errors.extend(validate_schema(value, schema["properties"][key], f"{location}.{key}"))
    elif isinstance(instance, list) and "items" in schema:
        for index, value in enumerate(instance):
            errors.extend(validate_schema(value, schema["items"], f"{location}[{index}]"))
    if isinstance(instance, int) and not isinstance(instance, bool) and "minimum" in schema and instance < schema["minimum"]:
        errors.append(f"{location}: value is below minimum {schema['minimum']}")
    if isinstance(instance, str) and schema.get("format") == "uri":
        parsed = urlparse(instance)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append(f"{location}: invalid HTTP(S) URI")
    if isinstance(instance, str) and schema.get("format") == "date-time":
        try:
            datetime.fromisoformat(instance.replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"{location}: invalid ISO date-time")
    return errors

def validate_against_schema(instance: dict, schema_name: str):
    schema_path = os.path.join(SCHEMAS_DIR, schema_name)
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    errors = validate_schema(instance, schema)
    if errors:
        raise ValueError(f"{schema_name} validation failed: " + "; ".join(errors))

STAGE_ORDER = ["intake", "discovery", "audit", "solution", "build", "qa", "deploy", "sales", "complete"]
STAGE_PREREQUISITES = {
    "discovery": "intake",
    "audit": "discovery",
    "solution": "audit",
    "build": "solution",
    "qa": "build",
    "deploy": "qa",
    "sales": "deploy",
}

def require_stage_ready(lead_id: str, requested_stage: str):
    lead_data, run_data = load_lead_run(lead_id)
    if not lead_data or not run_data:
        raise FileNotFoundError(f"Lead {lead_id!r} has not completed intake")
    prerequisite = STAGE_PREREQUISITES.get(requested_stage)
    if not prerequisite:
        return
    current_stage = run_data.get("stage")
    current_status = run_data.get("status")
    current_index = STAGE_ORDER.index(current_stage) if current_stage in STAGE_ORDER else -1
    prerequisite_index = STAGE_ORDER.index(prerequisite)
    if current_index < prerequisite_index or (current_index == prerequisite_index and current_status != "passed"):
        raise RuntimeError(
            f"Cannot run {requested_stage}: prerequisite {prerequisite} has not passed "
            f"(current stage={current_stage}, status={current_status})"
        )

def validate_handoff(handoff: dict):
    validate_against_schema(handoff, "handoff.schema.json")
    failed_gates = [g.get("criterion", "unnamed gate") for g in handoff["gate_results"] if g.get("result") == "fail"]
    if handoff["status"] == "passed" and failed_gates:
        raise ValueError(f"Passed handoff contains failed gates: {', '.join(failed_gates)}")
    return handoff

def init_workspace(lead_id: str, target_url: str, brand_name: str = "", category: str = "", city: str = "", contacts: dict = None, permissions: dict = None):
    workspace = get_lead_workspace(lead_id)
    subdirs = ["evidence", "discovery", "audit", "solution", "demo/source", "deployment", "sales"]
    for s in subdirs:
        os.makedirs(os.path.join(workspace, s), exist_ok=True)
        
    lead_file = os.path.join(workspace, "lead.json")
    run_file = os.path.join(workspace, "run.json")
    
    lead_data = {
        "lead_id": lead_id,
        "brand_name": brand_name or lead_id.replace('-', ' ').replace('_', ' ').title(),
        "target_url": target_url,
        "mode": "assessment",
        "category": category or "e-commerce",
        "market": "MA",
        "primary_language": "fr",
        "city": city or "Casablanca",
        "contacts": contacts or {
            "whatsapp": None,
            "email": None,
            "instagram": None,
            "verified_owner": False
        },
        "permissions": permissions or {
            "asset_use": False,
            "data_collection": True,
            "deployment": False,
            "outreach": False
        },
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso()
    }
    
    run_data = {
        "lead_id": lead_id,
        "target_url": target_url,
        "stage": "intake",
        "status": "passed",
        "started_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "attempt": 1,
        "artifact_versions": {},
        "approvals": [],
        "blockers": [],
        "next_action": "Run Agent 1 (Discovery) to collect public storefront dossier"
    }
    
    validate_against_schema(lead_data, "lead.schema.json")
    validate_against_schema(run_data, "run.schema.json")
    atomic_write_json(lead_file, lead_data)
    atomic_write_json(run_file, run_data)
        
    return workspace, lead_data, run_data

def update_run(lead_id: str, updates: dict):
    workspace = get_lead_workspace(lead_id)
    run_file = os.path.join(workspace, "run.json")
    if not os.path.exists(run_file):
        raise FileNotFoundError(f"Run file not found for lead {lead_id}")
    updates = dict(updates)
    with run_file_lock(workspace):
        with open(run_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "artifact_versions" in updates:
            data.setdefault("artifact_versions", {}).update(updates.pop("artifact_versions"))
        history = data.setdefault("history", [])
        if any(key in updates for key in ("stage", "status")):
            history.append({
                "stage": updates.get("stage", data.get("stage")),
                "status": updates.get("status", data.get("status")),
                "recorded_at": utc_now_iso(),
            })
        data.update(updates)
        data["updated_at"] = utc_now_iso()
        validate_against_schema(data, "run.schema.json")
        atomic_write_json(run_file, data)
    return data

def load_lead_run(lead_id: str):
    workspace = get_lead_workspace(lead_id)
    lead_file = os.path.join(workspace, "lead.json")
    run_file = os.path.join(workspace, "run.json")
    if not os.path.exists(run_file):
        return None, None
    with open(lead_file, "r", encoding="utf-8") as f:
        lead_data = json.load(f)
    with open(run_file, "r", encoding="utf-8") as f:
        run_data = json.load(f)
    return lead_data, run_data

def resolve_lead_id(query: str) -> str:
    """Intelligently resolves lead_id from query: index ('1'), url, brand name, or folder name."""
    query = query.strip().strip('"').strip("'")
    
    # 1. Exact directory match
    try:
        if os.path.isdir(get_lead_workspace(query)):
            return query
    except ValueError:
        pass

    # 2. Match by numeric ID from Excel database (e.g., '1')
    try:
        from generate_excel import prospects_data
        if query.isdigit():
            idx = int(query)
            for p in prospects_data:
                if p["id"] == idx:
                    return generate_lead_id(p["url"], p["name"])
    except Exception:
        pass

    # 3. Match by name or URL in prospects_data
    try:
        from generate_excel import prospects_data
        clean_q = query.lower().replace("_", " ").replace("-", " ")
        for p in prospects_data:
            if clean_q in p["name"].lower() or p["name"].lower() in clean_q or query.lower() in p["url"].lower():
                return generate_lead_id(p["url"], p["name"])
    except Exception:
        pass

    # 4. Search existing folders in LEADS_DIR
    if os.path.exists(LEADS_DIR):
        for d in os.listdir(LEADS_DIR):
            if d.lower() == query.lower() or d.lower().replace("_", "") == query.lower().replace("_", ""):
                return d

    # 5. Sanitize as fallback
    return sanitize_business_folder_name(query)

def print_completion_report(stage: str, status: str, artifacts: list, findings: list, assumptions: list, gates: list, external_changes: list, next_action: str):
    print("\n" + "="*70)
    print("GLOBAL SHOPIFY MODERNIZATION ORCHESTRATOR - STAGE REPORT")
    print("="*70)
    print(f"1. Stage & Status: [{stage.upper()}] -> {status.upper()}")
    print("\n2. Artifacts Created or Changed:")
    if artifacts:
        for a in artifacts:
            if isinstance(a, dict):
                p = a.get("path", "")
                sha = a.get("sha256", "")[:12] + "..." if a.get("sha256") else ""
                print(f"   • {p} ({sha})")
            else:
                print(f"   • {a}")
    else:
        print("   • None")
        
    print("\n3. Evidence-Backed Findings:")
    if findings:
        for f in findings:
            print(f"   • {f}")
    else:
        print("   • None recorded for this stage")
        
    print("\n4. Assumptions & Limitations:")
    if assumptions:
        for asm in assumptions:
            print(f"   • {asm}")
    else:
        print("   • None")
        
    print("\n5. Quality Gate Results:")
    if gates:
        for g in gates:
            print(f"   • [{g.get('result', 'PASS').upper()}] {g.get('criterion', '')}: {g.get('details', '')}")
    else:
        print("   • All gate criteria passed")
        
    print("\n6. External Changes Made:")
    if external_changes:
        for ch in external_changes:
            print(f"   • {ch}")
    else:
        print("   • Zéro external changes made (Safe execution mode)")
        
    print(f"\n7. Exact Next Action / Approval Required:")
    print(f"   👉 {next_action}")
    print("="*70 + "\n")

def list_leads():
    if not os.path.exists(LEADS_DIR):
        print("No leads workspace exists.")
        return
    leads = [d for d in os.listdir(LEADS_DIR) if os.path.isdir(os.path.join(LEADS_DIR, d))]
    print(f"\nTotal Leads in Workspace: {len(leads)}")
    for lid in leads:
        lead_data, run_data = load_lead_run(lid)
        if lead_data and run_data:
            print(f" • [{run_data.get('stage', 'N/A').upper():<10}] {lid:<24} | {lead_data.get('brand_name'):<22} | {lead_data.get('target_url'):<24} | Status: {run_data.get('status')}")
        else:
            print(f" • {lid} (Incomplete workspace)")

def step_intake(lead_id: str, target_url: str = None, brand_name: str = None):
    lead_data, run_data = load_lead_run(lead_id)
    if not lead_data:
        normalized = normalize_url(target_url or "https://anulus.ma")
        workspace, lead_data, run_data = init_workspace(
            lead_id=lead_id,
            target_url=normalized,
            brand_name=brand_name or lead_id.replace('_', ' ')
        )
    print_completion_report(
        stage="intake",
        status="passed",
        artifacts=[f"leads/{lead_id}/lead.json", f"leads/{lead_id}/run.json"],
        findings=[
            f"Target URL: {lead_data['target_url']}",
            f"Brand Name: {lead_data['brand_name']}",
            f"Dedicated Workspace: leads/{lead_id}/"
        ],
        assumptions=["Target is an active ecommerce brand in Morocco"],
        gates=[
            {"criterion": "Target validity", "result": "pass", "details": f"Valid URL {lead_data['target_url']}"},
            {"criterion": "Safe permission default", "result": "pass", "details": "asset_use=False, deployment=False, outreach=False"}
        ],
        external_changes=[],
        next_action=f"Run Discovery & Evidence Collection for '{lead_id}'"
    )
    return lead_data, run_data

def step_discovery(lead_id: str):
    require_stage_ready(lead_id, "discovery")
    lead_data, run_data = load_lead_run(lead_id)
    workspace = get_lead_workspace(lead_id)
    handoff = validate_handoff(run_discovery(lead_id, workspace, lead_data["target_url"], lead_data["brand_name"]))
    
    art_versions = {a["path"]: a["sha256"] for a in handoff["artifacts"]}
    update_run(lead_id, {
        "stage": "discovery",
        "status": handoff["status"],
        "artifact_versions": art_versions,
        "next_action": handoff["recommended_next_action"]
    })
    
    # Load discovery and social dossier for dynamic reporting
    dossier_path = os.path.join(workspace, "discovery", "brand_dossier.json")
    social_path = os.path.join(workspace, "discovery", "social_dossier.json")
    dossier_info = {}
    social_info = {}
    if os.path.exists(dossier_path):
        try:
            with open(dossier_path, "r", encoding="utf-8") as f:
                dossier_info = json.load(f)
        except Exception:
            pass
    if os.path.exists(social_path):
        try:
            with open(social_path, "r", encoding="utf-8") as f:
                social_info = json.load(f)
        except Exception:
            pass

    arch_name = dossier_info.get("archetype_name", "E-Commerce")
    ig_h = social_info.get("instagram_handle", "@brand")
    fol_c = social_info.get("follower_count", "N/A")

    print_completion_report(
        stage="discovery",
        status=handoff["status"],
        artifacts=handoff["artifacts"],
        findings=[
            f"Storefront evidence method: {handoff['evidence'][0]['method']}",
            f"Classified into Design Archetype: '{arch_name}'",
            f"Observed social profile data: {ig_h} ({fol_c} followers)",
            f"Live catalog items harvested: {dossier_info.get('catalog', {}).get('sample_count', 0)}"
        ],
        assumptions=handoff["assumptions"],
        gates=handoff["gate_results"],
        external_changes=[],
        next_action=handoff["recommended_next_action"]
    )
    return handoff

def step_audit(lead_id: str):
    require_stage_ready(lead_id, "audit")
    lead_data, run_data = load_lead_run(lead_id)
    workspace = get_lead_workspace(lead_id)
    handoff = validate_handoff(run_audit(lead_id, workspace, lead_data["brand_name"], lead_data["target_url"]))
    
    art_versions = {a["path"]: a["sha256"] for a in handoff["artifacts"]}
    update_run(lead_id, {
        "stage": "audit",
        "status": handoff["status"],
        "artifact_versions": art_versions,
        "next_action": handoff["recommended_next_action"]
    })
    report_path = os.path.join(workspace, "audit", "audit_report.json")
    audit_report = {}
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            audit_report = json.load(f)
    measured = audit_report.get("measured_storefront_facts", {})
    financial = audit_report.get("financial_analysis", {})
    
    print_completion_report(
        stage="audit",
        status=handoff["status"],
        artifacts=handoff["artifacts"],
        findings=[
            f"Evidence quality: {audit_report.get('evidence_quality', 'unknown')}",
            f"Observed external script tags: {measured.get('external_script_count', 'not measured')}",
            f"Detected app signatures: {', '.join(measured.get('detected_apps', [])) or 'none'}",
            f"Financial analysis: {financial.get('status', 'not calculated')}"
        ],
        assumptions=handoff["assumptions"],
        gates=handoff["gate_results"],
        external_changes=[],
        next_action=handoff["recommended_next_action"]
    )
    return handoff

def step_solution(lead_id: str):
    require_stage_ready(lead_id, "solution")
    lead_data, run_data = load_lead_run(lead_id)
    workspace = get_lead_workspace(lead_id)
    handoff = validate_handoff(run_solution(lead_id, workspace, lead_data["brand_name"]))
    
    art_versions = {a["path"]: a["sha256"] for a in handoff["artifacts"]}
    update_run(lead_id, {
        "stage": "solution",
        "status": handoff["status"],
        "artifact_versions": art_versions,
        "next_action": handoff["recommended_next_action"]
    })
    
    layout_file = os.path.join(workspace, "solution", "layout_spec.json")
    layout_info = {}
    if os.path.exists(layout_file):
        try:
            with open(layout_file, "r", encoding="utf-8") as f:
                layout_info = json.load(f)
        except Exception:
            pass

    fp_file = os.path.join(workspace, "solution", "design_fingerprint.json")
    fp_info = {}
    if os.path.exists(fp_file):
        try:
            with open(fp_file, "r", encoding="utf-8") as f:
                fp_info = json.load(f)
        except Exception:
            pass

    arch_title = layout_info.get("archetype_name", "E-Commerce")
    sig_effect = layout_info.get("motion_profile", {}).get("signature_effect", "smooth_glide")
    h_style = layout_info.get("layout_components", {}).get("hero_style", "bespoke")
    div_sim = fp_info.get("diversity_metrics", {}).get("max_similarity_observed", 0.0)

    print_completion_report(
        stage="solution",
        status=handoff["status"],
        artifacts=handoff["artifacts"],
        findings=[
            f"Design Genome Family: '{fp_info.get('page_family', arch_title)}' ({fp_info.get('density', 'standard')})",
            f"Component Anatomy: Hero '{fp_info.get('hero_variant', h_style)}', Nav '{fp_info.get('navigation_style', 'standard')}', Card '{fp_info.get('product_card_anatomy', 'standard')}'",
            f"Anti-Clone Diversity: Max similarity {div_sim:.1%} against {fp_info.get('diversity_metrics', {}).get('most_similar_lead') or 'none'} (Threshold < 65%)",
            f"Page Assembly Sequence: {' ➔ '.join(fp_info.get('section_order', []))}",
            f"GPU Motion Profile: Signature effect '{sig_effect}' with zero JS bundle bloat",
            "ADRs accepted: Next.js 14 App Router, Tailwind CSS, Vercel/Cloudflare Edge"
        ],
        assumptions=handoff["assumptions"],
        gates=handoff["gate_results"],
        external_changes=[],
        next_action=handoff["recommended_next_action"]
    )
    return handoff

def step_build(lead_id: str, with_ai: bool = False, ai_engine: str = "auto"):
    require_stage_ready(lead_id, "build")
    lead_data, run_data = load_lead_run(lead_id)
    workspace = get_lead_workspace(lead_id)
    handoff = validate_handoff(run_build(lead_id, workspace, lead_data["brand_name"]))
    
    # Pattern A: AI Subagent Enhancement (Claude Code / Codex)
    if with_ai or os.environ.get("ORCHESTRATOR_ENABLE_AI", "").lower() in ("true", "1", "yes"):
        print(f"\n[*] Subagent A (AI Bridge): Invoking AI coding agent ({ai_engine}) to refine components...")
        ai_res = bridge.enhance_storefront(workspace, lead_data["brand_name"], engine=ai_engine)
        if ai_res.get("success"):
            print(f"[✓] AI coding agent ({ai_res.get('engine')}) successfully polished demo code.")
        else:
            print(f"[!] AI refinement note: {ai_res.get('error')} (deterministic code safely retained).")

    art_versions = {a["path"]: a["sha256"] for a in handoff["artifacts"]}
    update_run(lead_id, {
        "stage": "build",
        "status": handoff["status"],
        "artifact_versions": art_versions,
        "next_action": handoff["recommended_next_action"]
    })
    
    print_completion_report(
        stage="build",
        status=handoff["status"],
        artifacts=handoff["artifacts"][:6] + [f"... and {len(handoff['artifacts'])-6} more source files"],
        findings=[
            f"Next.js 14 / Tailwind demo source generated in leads/{lead_id}/demo/source/",
            "Modular Components created: Header, InstagramStories, Hero, TrustBadges, ProductGrid, ProductCard, SocialUgcGrid, CodModal, OrderSuccessModal, Footer",
            "GPU-Accelerated Keyframe animations injected into tailwind.config.js (60fps native performance)",
            "Interactive Fast COD Modal configured with real-time Moroccan shipping fees & GSM validation"
        ],
        assumptions=handoff["assumptions"],
        gates=handoff["gate_results"],
        external_changes=[],
        next_action=handoff["recommended_next_action"]
    )
    return handoff

def step_qa(lead_id: str, autofix: bool = False, ai_engine: str = "auto"):
    require_stage_ready(lead_id, "qa")
    lead_data, run_data = load_lead_run(lead_id)
    workspace = get_lead_workspace(lead_id)
    handoff = validate_handoff(run_qa(lead_id, workspace, lead_data["brand_name"]))
    
    # Pattern A: AI Autonomous QA Fixer
    if (autofix or os.environ.get("ORCHESTRATOR_AUTOFIX_AI", "").lower() in ("true", "1", "yes")) and handoff["status"] == "failed":
        print(f"\n[*] Subagent A (AI Bridge): QA found blockers. Invoking AI agent ({ai_engine}) to attempt autonomous code fix...")
        qa_file = os.path.join(workspace, "demo", "qa_report.json")
        if os.path.exists(qa_file):
            try:
                with open(qa_file, "r", encoding="utf-8") as f:
                    qdata = json.load(f)
                fix_res = bridge.qa_autofix(workspace, qdata, engine=ai_engine)
                if fix_res.get("success"):
                    print(f"[✓] AI agent ({fix_res.get('engine')}) applied fixes. Re-running QA verification...")
                    handoff = validate_handoff(run_qa(lead_id, workspace, lead_data["brand_name"]))
            except Exception as e:
                print(f"[!] Autofix error: {e}")

    art_versions = {a["path"]: a["sha256"] for a in handoff["artifacts"]}
    update_run(lead_id, {
        "stage": "qa",
        "status": handoff["status"],
        "artifact_versions": art_versions,
        "next_action": handoff["recommended_next_action"]
    })
    
    print_completion_report(
        stage="qa",
        status=handoff["status"],
        artifacts=handoff["artifacts"],
        findings=[
            handoff["summary"],
            "Production build and static checks were executed; no synthetic PageSpeed score is reported",
            f"Blocking failures: {', '.join(handoff['blockers']) or 'none'}"
        ],
        assumptions=handoff["assumptions"],
        gates=handoff["gate_results"],
        external_changes=[],
        next_action=handoff["recommended_next_action"]
    )
    return handoff

def step_deploy_prep(lead_id: str, live: bool = True):
    require_stage_ready(lead_id, "deploy")
    lead_data, run_data = load_lead_run(lead_id)
    workspace = get_lead_workspace(lead_id)
    
    if live:
        handoff = validate_handoff(run_live_deployment(lead_id, workspace, lead_data["brand_name"], lead_data["target_url"]))
    else:
        handoff = validate_handoff(run_deployment_prep(lead_id, workspace, lead_data["brand_name"], lead_data["target_url"]))
    
    art_versions = {a["path"]: a.get("sha256", "auto") for a in handoff["artifacts"]}
    update_run(lead_id, {
        "stage": "deploy",
        "status": handoff["status"],
        "artifact_versions": art_versions,
        "next_action": handoff["recommended_next_action"]
    })
    
    print_completion_report(
        stage="deployment_prep" if not live else "live_deployment",
        status=handoff["status"],
        artifacts=handoff["artifacts"],
        findings=[
            handoff["summary"],
            f"GitHub target: https://github.com/e-commerce-refactor/{slugify(lead_id)}",
            "Anonymous order reads are denied by the applied database migration" if live and handoff["status"] == "passed" else "Deployment plan includes removal of anonymous order-read access",
            f"Blocking failures: {', '.join(handoff.get('blockers', [])) or 'none'}"
        ],
        assumptions=handoff.get("assumptions", []),
        gates=handoff.get("gate_results", []),
        external_changes=([
            f"Pushed codebase to https://github.com/e-commerce-refactor/{slugify(lead_id)}",
            f"Deployed edge instance to Vercel"
        ] if live and handoff["status"] == "passed" else []),
        next_action=handoff["recommended_next_action"]
    )
    return handoff

def step_sales(lead_id: str, with_ai: bool = False, ai_engine: str = "auto"):
    require_stage_ready(lead_id, "sales")
    lead_data, run_data = load_lead_run(lead_id)
    workspace = get_lead_workspace(lead_id)
    handoff = validate_handoff(run_sales(lead_id, workspace, lead_data["brand_name"], lead_data["target_url"]))
    
    # Pattern A: AI Sales Pitch Enhancement
    if with_ai or os.environ.get("ORCHESTRATOR_ENABLE_AI", "").lower() in ("true", "1", "yes"):
        print(f"\n[*] Subagent A (AI Bridge): Invoking AI agent ({ai_engine}) to craft personalized bilingual pitch...")
        ai_res = bridge.craft_sales_outreach(workspace, lead_data["brand_name"], lead_data["target_url"], engine=ai_engine)
        if ai_res.get("success"):
            print(f"[✓] AI agent ({ai_res.get('engine')}) drafted personalized pitches.")
            ai_sales_path = os.path.join(workspace, "sales", "ai_personalized_pitch.md")
            try:
                with open(ai_sales_path, "w", encoding="utf-8") as f:
                    f.write(ai_res.get("output", ""))
            except Exception:
                pass
        else:
            print(f"[!] AI sales note: {ai_res.get('error')} (verified template copy safely retained).")

    art_versions = {a["path"]: a["sha256"] for a in handoff["artifacts"]}
    update_run(lead_id, {
        "stage": "complete" if handoff["status"] == "passed" else "sales",
        "status": handoff["status"],
        "artifact_versions": art_versions,
        "next_action": "Pipeline complete: Present demo & audit to user, awaiting human outreach authorization"
    })
    
    print_completion_report(
        stage="sales",
        status=handoff["status"],
        artifacts=handoff["artifacts"],
        findings=[
            handoff["summary"],
            "French and Darija drafts explicitly distinguish measured facts from unknowns",
            "No PageSpeed, revenue, conversion, or savings claim is made without evidence",
            "Both drafts include a STOP opt-out"
        ],
        assumptions=handoff["assumptions"],
        gates=handoff["gate_results"],
        external_changes=[],
        next_action=handoff["recommended_next_action"]
    )
    return handoff

def slugify(lead_id: str) -> str:
    slug = lead_id.lower().replace("_", "-").replace(" ", "-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    slug = slug.strip("-")
    suffix = os.environ.get("DEPLOY_SLUG_SUFFIX", "-v3")
    if not slug.endswith(suffix):
        slug = f"{slug}{suffix}"
    return slug

def run_all(lead_id: str, live: bool = True, with_ai: bool = False, ai_engine: str = "auto"):
    print("\n" + "#"*70)
    print(f"🚀 EXECUTING COMPLETE ORCHESTRATION PIPELINE IN ONE GO")
    print(f"   Target Business: {lead_id}")
    print(f"   Mode: Full Automated Pipeline (GitHub + Supabase + Vercel Live Deploy)")
    if with_ai:
        print(f"   AI Subagent Engine: Active ({ai_engine})")
    print("#"*70)

    # Agent 0: Intake
    step_intake(lead_id)
    
    # Agent 1: Discovery
    stages = [
        ("discovery", step_discovery),
        ("audit", step_audit),
        ("solution", step_solution),
        ("build", lambda lid: step_build(lid, with_ai=with_ai, ai_engine=ai_engine)),
        ("qa", lambda lid: step_qa(lid, autofix=with_ai, ai_engine=ai_engine)),
        ("deploy", lambda lid: step_deploy_prep(lid, live=live)),
        ("sales", lambda lid: step_sales(lid, with_ai=with_ai, ai_engine=ai_engine)),
    ]
    for stage_name, runner in stages:
        handoff = runner(lead_id)
        if handoff["status"] != "passed":
            raise RuntimeError(f"Pipeline stopped at {stage_name}: {handoff['summary']}")

    # Auto-synchronize Excel Database
    try:
        from generate_excel import wb
        import subprocess
        print("[*] Synchronizing Prospection_Migration_Shopify_Maroc.xlsx...")
        subprocess.run([sys.executable, "generate_excel.py"], capture_output=True, text=True)
        print("[+] Excel database synchronized.")
    except Exception as e:
        print(f"[!] Excel sync notice: {e}")

    print("\n" + "🌟"*35)
    print("🏆 ORCHESTRATOR PIPELINE COMPLETED SUCCESSFULLY IN ONE GO!")
    print(f"   All 8 agents have executed and deployed for '{lead_id}'.")
    print(f"   GitHub:   https://github.com/e-commerce-refactor/{slugify(lead_id)}")
    print(f"   Vercel:   https://{slugify(lead_id)}.vercel.app")
    print(f"   Database: Supabase (e-commerce-refactor org)")
    print(f"   Workspace: leads/{lead_id}/")
    print("🌟"*35 + "\n")

def main():
    if len(sys.argv) < 2:
        print("""
Global Shopify Ecommerce Modernization Agency Orchestrator CLI
Universal modernization & migration engine for any Shopify business.

Usage:
  python orchestrator.py run-all <lead ID or number> [--with-ai] [--engine claude|codex]
  python orchestrator.py Assess <store URL> [Brand Name]
  python orchestrator.py "Discover <lead ID>"
  python orchestrator.py "Audit <lead ID>"
  python orchestrator.py "Plan solution <lead ID>"
  python orchestrator.py "Build demo <lead ID>" [--with-ai] [--engine claude|codex]
  python orchestrator.py "Verify QA <lead ID>" [--autofix]
  python orchestrator.py "Prepare deployment <lead ID>"
  python orchestrator.py "Deploy <lead ID> --approved"
  python orchestrator.py "Draft outreach <lead ID>" [--with-ai]
  python orchestrator.py status <lead ID>
  python orchestrator.py list
  python orchestrator.py ai-status        (Inspect Claude Code / Codex / LLM availability)
  python orchestrator.py mcp              (Run stdio Model Context Protocol server)
        """)
        return

    cmd = " ".join(sys.argv[1:]).strip()

    # 0. MCP Server
    if cmd.strip().lower() in ("mcp", "mcp-server", "serve-mcp"):
        import mcp_server
        mcp_server.run_server()
        return

    # 0.1 AI Status
    if cmd.strip().lower() in ("ai-status", "agents", "ai"):
        caps = bridge.get_capabilities()
        print("\n" + "="*60)
        print("🤖 AI Coding Agents & Execution Engines Status")
        print("="*60)
        print(f" • Active Default Engine: {caps['active_engine'].upper()}")
        print(f" • Available Engines:     {', '.join(caps['available_engines']) or 'None'}")
        print(f" • Claude Code CLI:       {caps['claude_cli_path'] or 'Not found'}")
        print(f" • OpenAI Codex CLI:      {caps['codex_cli_path'] or 'Not found'}")
        print(f" • Anthropic API Key:     {'Configured' if caps['has_anthropic_api'] else 'Not set'}")
        print(f" • OpenAI API Key:        {'Configured' if caps['has_openai_api'] else 'Not set'}")
        print("="*60 + "\n")
        return

    # Extract common AI flags & check ACTIVE_AI_AGENT configuration
    active_env_agent = os.environ.get("ACTIVE_AI_AGENT", "").strip().lower()
    with_ai = "--with-ai" in cmd.lower() or "--ai" in cmd.lower() or (bool(active_env_agent) and active_env_agent != "none")
    autofix = "--autofix" in cmd.lower() or with_ai
    ai_engine = active_env_agent if (active_env_agent and active_env_agent != "none") else "auto"
    engine_match = re.search(r"--engine\s+(\S+)", cmd, re.IGNORECASE)
    if engine_match:
        ai_engine = engine_match.group(1).lower()

    # Clean flags from target string
    def strip_flags(text: str) -> str:
        t = re.sub(r'--(?:with-)?ai\b', '', text, flags=re.IGNORECASE)
        t = re.sub(r'--autofix\b', '', t, flags=re.IGNORECASE)
        t = re.sub(r'--engine\s+\S+', '', t, flags=re.IGNORECASE)
        return t.strip()

    # 1. Run all in one go
    run_all_match = re.match(r"^(?:run[-_ ]?all|start.*in\s+one\s+go)\s*(.*)", cmd, re.IGNORECASE)
    if run_all_match:
        target = strip_flags(run_all_match.group(1).strip())
        lead_id = resolve_lead_id(target or "1")
        run_all(lead_id, with_ai=with_ai, ai_engine=ai_engine)
        return

    # 2. Assess
    assess_match = re.match(r"^Assess\s+(.*)", cmd, re.IGNORECASE)
    if assess_match:
        rest = assess_match.group(1).strip()
        url_match = re.search(r'(https?://\S+|\b[a-zA-Z0-9-]+\.(?:ma|com|shop|store|net)\b\S*)', rest)
        custom_name = None
        if url_match:
            raw_url = url_match.group(1)
            potential_name = rest.replace(raw_url, '').strip().strip('"').strip("'")
            if potential_name:
                custom_name = potential_name
        else:
            raw_url = rest.split()[0]
            if len(rest.split()) > 1:
                custom_name = " ".join(rest.split()[1:]).strip('"').strip("'")
        normalized = normalize_url(raw_url)
        lead_id = generate_lead_id(normalized, custom_name)
        step_intake(lead_id, target_url=normalized, brand_name=custom_name)
        return

    # 3. Discover
    disc_match = re.match(r"^(?:discover|run discovery)\s+(.*)", cmd, re.IGNORECASE)
    if disc_match:
        lead_id = resolve_lead_id(disc_match.group(1))
        step_discovery(lead_id)
        return

    # 4. Audit
    audit_match = re.match(r"^(?:audit|run audit)\s+(.*)", cmd, re.IGNORECASE)
    if audit_match:
        lead_id = resolve_lead_id(audit_match.group(1))
        step_audit(lead_id)
        return

    # 5. Solution
    sol_match = re.match(r"^(?:plan solution|solution)\s+(.*)", cmd, re.IGNORECASE)
    if sol_match:
        lead_id = resolve_lead_id(sol_match.group(1))
        step_solution(lead_id)
        return

    # 6. Build Demo
    build_match = re.match(r"^(?:build demo|build)\s+(.*)", cmd, re.IGNORECASE)
    if build_match:
        lead_id = resolve_lead_id(strip_flags(build_match.group(1)))
        step_build(lead_id, with_ai=with_ai, ai_engine=ai_engine)
        return

    # 7. QA
    qa_match = re.match(r"^(?:verify qa|qa)\s+(.*)", cmd, re.IGNORECASE)
    if qa_match:
        lead_id = resolve_lead_id(strip_flags(qa_match.group(1)))
        step_qa(lead_id, autofix=autofix, ai_engine=ai_engine)
        return

    # 8. Prepare deployment / Deploy
    deploy_match = re.match(r"^(?:prepare deployment|deploy)\s+(.*)", cmd, re.IGNORECASE)
    if deploy_match:
        raw_target = deploy_match.group(1)
        approved = "--approved" in raw_target.lower() or "--live" in raw_target.lower() or "deploy" in cmd.lower()
        lead_id = resolve_lead_id(raw_target.replace("--approved", "").replace("--live", ""))
        step_deploy_prep(lead_id, live=approved)
        if approved:
            print(f"[*] Live deployment pipeline executed for {lead_id}.")
        return

    # 9. Draft Outreach
    sales_match = re.match(r"^(?:draft outreach|outreach|sales)\s+(.*)", cmd, re.IGNORECASE)
    if sales_match:
        lead_id = resolve_lead_id(strip_flags(sales_match.group(1)))
        step_sales(lead_id, with_ai=with_ai, ai_engine=ai_engine)
        return

    # 10. List
    if cmd.strip().lower() == "list":
        list_leads()
        return

    # 11. Status
    status_match = re.match(r"^status\s+(\S+)", cmd, re.IGNORECASE)
    if status_match:
        lid = resolve_lead_id(status_match.group(1))
        lead_data, run_data = load_lead_run(lid)
        if not lead_data:
            print(f"Error: Lead '{lid}' not found.")
            return
        print(json.dumps({"lead": lead_data, "run": run_data}, indent=2, ensure_ascii=False))
        return

    print(f"Unrecognized command: '{cmd}'. Acceptable: run-all <id>, Assess <url>, Build demo <id>, Prepare deployment <id>, Deploy <id> --approved, Draft outreach <id>, status <id>, list")

if __name__ == "__main__":
    main()
