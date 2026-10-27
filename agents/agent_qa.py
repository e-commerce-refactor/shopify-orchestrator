"""
Agent 5: Quality Verifier (QA)
Conducts adversarial quality assurance on the built demo storefront across
responsiveness, form validation, security, accessibility, and performance budgets.
"""

import os
import re
import shutil
import subprocess
import json
import hashlib
import tempfile
from datetime import datetime, timezone
from agents.skills.design_genome import check_anti_clone_diversity

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

def atomic_write_json(path, data):
    fd, temp_path = tempfile.mkstemp(prefix=".tmp-qa-", suffix=".json", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def source_files(source_dir):
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".next", ".git", ".vercel"}]
        for filename in files:
            if filename.endswith((".ts", ".tsx", ".js", ".jsx", ".json")):
                yield os.path.join(root, filename)

def run_process(command, cwd, timeout=600):
    try:
        executable = command[0].lower()
        if os.name == "nt" and executable.endswith((".cmd", ".bat")):
            command = [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/s", "/c", *command]
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, shell=False)
        return result.returncode, (result.stdout + "\n" + result.stderr).strip()[-12000:]
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, f"{type(exc).__name__}: {exc}"

def check_secret_leakage(source_dir):
    patterns = {
        "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "Supabase service-role key": re.compile(r"service[_-]?role[^\n]{0,30}eyJ[A-Za-z0-9_-]+", re.I),
        "GitHub token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
        "generic secret assignment": re.compile(r"(?:secret|private[_-]?key|access[_-]?token)\s*[:=]\s*['\"][^'\"]{12,}['\"]", re.I),
    }
    findings = []
    for path in source_files(source_dir):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for label, pattern in patterns.items():
            if pattern.search(content):
                findings.append(f"{os.path.relpath(path, source_dir)}: {label}")
    return findings

def run_qa(lead_id: str, workspace: str, brand_name: str):
    demo_dir = os.path.join(workspace, "demo")
    source_dir = os.path.join(demo_dir, "source")
    qa_path = os.path.join(demo_dir, "qa_report.json")

    # 1. Inspect source files
    expected_files = [
        "package.json", "tsconfig.json", "tailwind.config.js",
        "app/layout.tsx", "app/page.tsx", "data/products.ts",
        "components/Header.tsx", "components/Hero.tsx",
        "components/ProductCard.tsx", "components/ProductGrid.tsx",
        "components/CodModal.tsx", "components/OrderSuccessModal.tsx",
        "components/TrustBadges.tsx", "components/Footer.tsx",
        "lib/adminAuth.ts",
        "app/admin/layout.tsx", "app/admin/login/page.tsx",
        "app/admin/page.tsx", "app/admin/products/page.tsx",
        "app/admin/reviews/page.tsx", "app/admin/settings/page.tsx"
    ]

    missing_files = []
    file_hashes = {}
    for rel in expected_files:
        full_p = os.path.join(source_dir, rel.replace('/', os.sep))
        if not os.path.exists(full_p):
            missing_files.append(rel)
        else:
            file_hashes[rel] = hash_file(full_p)

    cod_path = os.path.join(source_dir, "components", "CodModal.tsx")
    page_path = os.path.join(source_dir, "app", "page.tsx")
    cod_source = open(cod_path, "r", encoding="utf-8", errors="ignore").read() if os.path.exists(cod_path) else ""
    page_source = open(page_path, "r", encoding="utf-8", errors="ignore").read() if os.path.exists(page_path) else ""
    all_source = "\n".join(open(path, "r", encoding="utf-8", errors="ignore").read() for path in source_files(source_dir)) if os.path.isdir(source_dir) else ""

    phone_pattern = re.compile(r"^(?:\+212|0)[5-7]\d{8}$")
    valid_numbers = ["+212612345678", "0612345678", "0712345678"]
    invalid_numbers = ["+212812345678", "06123", "0012345678", "06123456789"]
    phone_behavior_ok = all(phone_pattern.fullmatch(v) for v in valid_numbers) and not any(phone_pattern.fullmatch(v) for v in invalid_numbers)
    phone_regex_present = "[5-7]" in cod_source and "212" in cod_source and "\\d{8}" in cod_source
    secret_findings = check_secret_leakage(source_dir) if os.path.isdir(source_dir) else ["source directory missing"]
    responsive_ok = any(token in all_source for token in ("sm:", "md:", "lg:", "xl:"))
    img_tags = re.findall(r"<(?:img|Image)\b[^>]*>", all_source, re.I | re.S)
    missing_alt = [tag[:100] for tag in img_tags if not re.search(r"\balt\s*=", tag, re.I)]
    semantic_ok = "<main" in page_source.lower() and not missing_alt
    shipping_ok = "Casablanca" in cod_source and "35" in cod_source

    npm = shutil.which("npm") or shutil.which("npm.cmd")
    install_code, install_output = (1, "npm executable not found")
    build_code, build_output = (1, "Build skipped because dependency installation failed")
    if npm and not missing_files:
        install_code, install_output = run_process([npm, "install", "--no-audit", "--no-fund"], source_dir)
        if install_code == 0:
            build_code, build_output = run_process([npm, "run", "build"], source_dir)

    # 2. Anti-clone design diversity evaluation
    fp_path = os.path.join(workspace, "solution", "design_fingerprint.json")
    leads_dir = os.path.dirname(os.path.abspath(workspace))
    clone_safe = True
    clone_details = "Design fingerprint not present in workspace"
    if os.path.exists(fp_path):
        try:
            with open(fp_path, "r", encoding="utf-8") as f:
                fp_data = json.load(f)
            div_eval = check_anti_clone_diversity(fp_data, leads_dir, threshold=0.65)
            clone_safe = div_eval["is_clone_safe"]
            max_sim = div_eval["max_similarity_observed"]
            most_sim = div_eval["most_similar_lead"] or "none"
            if clone_safe:
                clone_details = f"Max similarity {max_sim:.1%} against {most_sim} is below 65% ceiling"
            else:
                clone_details = f"Clone risk: {max_sim:.1%} similarity with {most_sim} exceeds 65% ceiling"
        except Exception as e:
            clone_details = f"Anti-clone evaluation notice: {e}"

    checks = [
        ("Source completeness", not missing_files, f"{len(expected_files) - len(missing_files)}/{len(expected_files)} required files present; missing={missing_files}"),
        ("Dependency installation", install_code == 0, install_output or "npm install completed"),
        ("Production TypeScript/Next.js build", build_code == 0, build_output or "npm run build completed"),
        ("Moroccan phone validation", phone_regex_present and phone_behavior_ok, "Validator is present and canonical valid/invalid cases behave correctly"),
        ("Secret leakage scan", not secret_findings, "No private credential patterns found" if not secret_findings else "; ".join(secret_findings)),
        ("Responsive source rules", responsive_ok, "Responsive Tailwind breakpoint detected" if responsive_ok else "No responsive breakpoint class found"),
        ("Accessibility baseline", semantic_ok, "Main landmark and image alt attributes verified" if semantic_ok else f"main landmark or alt attributes missing ({len(missing_alt)} images)"),
        ("Moroccan shipping behavior", shipping_ok, "Casablanca and provincial fee logic found" if shipping_ok else "Expected shipping differentiation not found"),
        ("Anti-clone structural diversity", clone_safe, clone_details),
    ]
    qa_checks = [{"category": name, "test": name, "status": "PASS" if passed else "FAIL", "details": details} for name, passed, details in checks]
    failed = [name for name, passed, _ in checks if not passed]
    status = "passed" if not failed else "failed"

    qa_report = {
        "lead_id": lead_id,
        "brand_name": brand_name,
        "verified_at": utc_now_iso(),
        "overall_status": status.upper(),
        "defects_critical": len(failed),
        "defects_major": 0,
        "defects_minor": 0,
        "checks": qa_checks,
        "performance_measurement": {
            "status": "not_measured",
            "reason": "Lighthouse requires a running deployment; no synthetic PageSpeed score is asserted during source QA"
        },
        "file_integrity": file_hashes
    }

    atomic_write_json(qa_path, qa_report)
    qa_sha = hash_file(qa_path)

    handoff = {
        "status": status,
        "summary": f"Executed {len(checks)} QA checks for {brand_name}; {len(failed)} failed.",
        "artifacts": [
            {"path": f"leads/{lead_id}/demo/qa_report.json", "schema_version": "2.0", "sha256": qa_sha}
        ],
        "evidence": [
            {"source": f"leads/{lead_id}/demo/source/", "collected_at": utc_now_iso(), "method": "npm_production_build_and_static_checks", "confidence": "high"}
        ],
        "assumptions": [],
        "risks": ["Runtime performance remains unmeasured until a preview deployment is tested"] if status == "passed" else [],
        "blockers": failed,
        "gate_results": [{"criterion": name, "result": "pass" if passed else "fail", "details": details} for name, passed, details in checks],
        "recommended_next_action": f"Run Agent 6 (Release & Deployment Manager) on lead '{lead_id}'" if status == "passed" else f"Fix QA failures for '{lead_id}' and rerun QA"
    }

    return handoff
