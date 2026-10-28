"""
Agent 2: Store Audit Analyst
Conducts technical, performance, checkout friction, and financial drain audits
for the targeted Shopify store.
"""

import os
import json
import hashlib
from datetime import datetime, timezone

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

def _run_audit_legacy(lead_id: str, workspace: str, brand_name: str, target_url: str):
    raise RuntimeError("Legacy synthetic audit generation has been disabled")
    audit_dir = os.path.join(workspace, "audit")
    discovery_dir = os.path.join(workspace, "discovery")
    os.makedirs(audit_dir, exist_ok=True)

    dossier_path = os.path.join(discovery_dir, "brand_dossier.json")
    brand_dossier = {}
    if os.path.exists(dossier_path):
        with open(dossier_path, "r", encoding="utf-8") as f:
            brand_dossier = json.load(f)

    report_path = os.path.join(audit_dir, "audit_report.json")
    summary_path = os.path.join(audit_dir, "audit_summary.md")

    is_watch = "montre" in lead_id.lower() or "montre" in brand_name.lower() or "horloger" in brand_dossier.get("niche", "").lower()
    product_type_label = "montres de prestige" if is_watch else "bijoux d'exception"
    niche_label = "l'horlogerie et les montres de prestige" if is_watch else "la bijouterie fine et joaillerie"

    # 1. Performance benchmarks (Mobile 4G Simulation)
    performance_audit = {
        "lighthouse_mobile_score": 38,
        "lighthouse_desktop_score": 71,
        "web_vitals": {
            "first_contentful_paint_sec": 2.4,
            "largest_contentful_paint_sec": 4.1,
            "speed_index_sec": 4.6,
            "total_blocking_time_ms": 640,
            "cumulative_layout_shift": 0.18,
            "time_to_first_byte_ms": 820
        },
        "payload_breakdown": {
            "total_scripts_count": 25,
            "total_javascript_kb": 1840,
            "shopify_core_kb": 650,
            "third_party_apps_kb": 920,
            "unoptimized_images_mb": 4.2
        },
        "root_causes": [
            "Releasit COD Form app injects heavy asynchronous script and custom CSS that blocks the main thread",
            "Shopify storefront renderer loads multiple tracking pixels (Meta, TikTok) synchronously on mobile",
            f"High-resolution {product_type_label} hero images served without modern WebP/AVIF compression or responsive srcset",
            "Shopify global CDN has routing latency to Morocco Telecom (IAM / Orange / Inwi 4G networks)"
        ]
    }

    # 2. Checkout Friction Audit
    checkout_audit = {
        "current_flow": "Shopify Default 3-Step Checkout with Releasit App Overlay",
        "friction_points": [
            {
                "issue": "Demande de Code Postal & Province",
                "severity": "HIGH",
                "impact": "Les clients marocains n'utilisent pas de code postal. Bloque ou perturbe 18% des paniers mobiles."
            },
            {
                "issue": "Tunnel d'achat en 3 étapes lentes",
                "severity": "HIGH",
                "impact": "Chaque étape de redirection Shopify recharge la page, entraînant une chute de conversion de 25%."
            },
            {
                "issue": "Absence de bouton direct 'Commander par WhatsApp'",
                "severity": "MEDIUM",
                "impact": f"Pour {niche_label}, les clients marocains exigent souvent un contact humain rassurant avant validation."
            },
            {
                "issue": "Calculateur de frais de livraison rigide",
                "severity": "MEDIUM",
                "impact": "Impossibilité de proposer un tarif différencié simple Casablanca (Livraison express le jour même) vs Autres Villes (48h)."
            }
        ]
    }

    # 3. Financial & Foreign Currency Drain Model
    saas_usd = 150 if is_watch else 180
    saas_mad = saas_usd * 10
    annual_saas_mad = saas_mad * 12
    annual_tx_mad = 36000
    total_annual_mad = annual_saas_mad + annual_tx_mad

    financial_audit = {
        "currency": "MAD",
        "assumed_monthly_revenue_mad": 150000,
        "monthly_breakdown": {
            "shopify_plan_usd": 79,
            "shopify_plan_mad": 790,
            "releasit_cod_app_usd": 39,
            "releasit_cod_app_mad": 390,
            "reviews_zoom_apps_usd": saas_usd - 118,
            "reviews_zoom_apps_mad": (saas_usd - 118) * 10,
            "total_monthly_saas_usd": saas_usd,
            "total_monthly_saas_mad": saas_mad,
            "shopify_cod_penalty_rate": 0.02,
            "shopify_cod_penalty_mad": 3000
        },
        "annual_summary": {
            "annual_saas_devise_drain_mad": annual_saas_mad,
            "annual_saas_devise_drain_usd": saas_usd * 12,
            "annual_transaction_penalty_mad": annual_tx_mad,
            "total_annual_drain_mad": total_annual_mad,
            "three_year_cumulative_drain_mad": total_annual_mad * 3
        },
        "dotation_ecommerce_impact": f"Consomme plus de {annual_saas_mad:,} DH/an de la dotation e-commerce officielle en devises, réduisant le budget publicitaire Facebook/TikTok Ads."
    }

    # Build report dict
    audit_report = {
        "lead_id": lead_id,
        "brand_name": brand_name,
        "target_url": target_url,
        "audited_at": utc_now_iso(),
        "performance_audit": performance_audit,
        "checkout_audit": checkout_audit,
        "financial_audit": financial_audit,
        "audit_verdict": "STRONG_MIGRATION_CANDIDATE",
        "summary": f"{brand_name} subit une triple pénalité sous Shopify : perte de vitesse mobile (38/100), fuite de devises ({annual_saas_mad:,} DH/an) et pénalité transactionnelle de 2% sur les commandes COD (36 000 DH/an)."
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2, ensure_ascii=False)
    rep_sha256 = hash_file(report_path)

    # 4. Generate audit_summary.md
    summary_md = f"""# 📑 Rapport d'Audit Technique & Financier — {brand_name}

**Boutique analysée :** [{brand_name}]({target_url})  
**Date de l'audit :** {datetime.now(timezone.utc).strftime("%d/%m/%Y")}  
**Localisation :** Casablanca, Maroc  
**Verdict de l'audit :** 🔥 **Priorité Haute — Candidat Idéal pour Migration Propriétaire**

---

## 1. Synthèse Exécutive

La boutique **{brand_name}** jouit d'une forte notoriété sur le marché de {niche_label} au Maroc. Cependant, son infrastructure actuelle hébergée sur **Shopify** génère d'importantes frictions commerciales et financières :

1. **Ralentissement Mobile Critique (Score PageSpeed : 38/100)** : Le script tiers `Releasit COD Form` et les 25 scripts JavaScript ralentissent le chargement sur réseau 4G marocain (LCP de 4.1s).
2. **Plafond Dotation E-commerce Consommé en Devises** : Plus de **{annual_saas_mad:,} DH/an** (${saas_usd * 12:,} USD) sont prélevés directement sur la dotation e-commerce internationale de la marque en abonnements Shopify et apps tierces.
3. **Pénalité de 2.0% sur le Cash-on-Delivery** : En l'absence de Shopify Payments au Maroc, Shopify taxe chaque commande COD, représentant une perte sèche estimée à **36 000 DH/an**.

---

## 2. Performances Techniques & Vitesse Mobile

| Indicateur Web Vitals | Mesure Actuelle (Shopify) | Cible Next.js Propriétaire | Impact Business |
| :--- | :---: | :---: | :--- |
| **Score Mobile PageSpeed** | **38 / 100** | **95+ / 100** | +25% de conversion sur les publicités Meta/TikTok |
| **Largest Contentful Paint (LCP)** | **4.1 secondes** | **< 1.2 seconde** | Affichage quasi-instantané des {product_type_label} |
| **First Contentful Paint (FCP)** | **2.4 secondes** | **< 0.6 seconde** | Fin de l'écran blanc au clic |
| **Scripts JavaScript chargés** | **25 scripts (1.8 MB)** | **< 70 KB gzipped** | Économie de batterie et de data 4G client |
| **Formulaire COD** | **Script externe lourd** | **Natif & instantané** | Zéro bug d'affichage sur smartphone |

---

## 3. Analyse du Tunnel d'Achat & Frictions COD Maroc

```mermaid
graph LR
    A["Visiteur Clique sur Pub Instagram"] --> B["Boutique Shopify (4.1s chargement)"]
    B --> C["App Releasit externe charge"]
    C --> D{"Formulaire lourd ou tunnel 3 étapes"}
    D -->|Friction: Abandon 35%| E["Panier Abandonné"]
    D -->|Conversion| F["Commande COD validée (-2% taxe Shopify)"]
```

### Problèmes relevés sur le terrain :
- **Dépendance à Releasit** : L'extension injecte des requêtes externes bloquantes vers des serveurs tiers.
- **Manque de personnalisation locale** : Impossibilité d'intégrer nativement un sélecteur intelligent de villes marocaines (avec délais express Casa vs provinces).
- **Pas de relais WhatsApp 1-Clic** : Pour {product_type_label}, les acheteurs hésitent et abandonnent sans canal d'échange direct.

---

## 4. Modèle Financier : Coût Shopify vs. Solution Next.js Propriétaire

| Poste de Dépense | Shopify Actuel (1 An) | Shopify Actuel (3 Ans) | Site Propriétaire (1 An) | Site Propriétaire (3 Ans) |
| :--- | :---: | :---: | :---: | :---: |
| **Abonnement Shopify & Apps** (${saas_usd}/m) | {annual_saas_mad:,} DH | {annual_saas_mad*3:,} DH | **0 DH** (Natif) | **0 DH** |
| **Pénalité Transaction 2.0% COD** | 36 000 DH | 108 000 DH | **0 DH** | **0 DH** |
| **Développement Sur-Mesure** | 0 DH | 0 DH | 18 000 DH (One-shot) | 18 000 DH |
| **Hébergement Cloud Haute Vitesse** | 0 DH | 0 DH | 1 200 DH (100 DH/m) | 3 600 DH |
| **TOTAL DÉPENSÉ** | **{total_annual_mad:,} DH** | **{total_annual_mad*3:,} DH** | **19 200 DH** | **21 600 DH** |
| **GAIN NET MARQUE** | — | — | **+{total_annual_mad - 19200:,} DH** | **+{total_annual_mad*3 - 21600:,} DH** |

> [!NOTE]
> Le développement d'une boutique propriétaire Next.js est **totalement amorti en moins de 5 mois**, tout en restituant **{annual_saas_mad:,} DH de devises internationales** pour alimenter les campagnes publicitaires de {brand_name}.

---

## 5. Recommandations Stratégiques

1. **Remplacer l'architecture Shopify** par un frontend Next.js 14 ultra-rapide avec hébergement Edge au plus près des utilisateurs marocains.
2. **Intégrer un Checkout COD Natif en 2 champs** (Nom + Téléphone WhatsApp) avec confirmation instantanée.
3. **Mettre en place une passerelle WhatsApp Directe** permettant aux clients d'échanger sur la disponibilité des modèles ou les détails de garantie.
"""

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_md)
    sum_sha256 = hash_file(summary_path)

    handoff = {
        "status": "passed",
        "summary": f"Agent 2 (Store Audit Analyst) completed in-depth performance, checkout friction, and financial drain analysis for {brand_name}.",
        "artifacts": [
            {"path": f"leads/{lead_id}/audit/audit_report.json", "schema_version": "1.0", "sha256": rep_sha256},
            {"path": f"leads/{lead_id}/audit/audit_summary.md", "schema_version": "1.0", "sha256": sum_sha256}
        ],
        "evidence": [
            {"source": target_url, "collected_at": utc_now_iso(), "method": "audit_pipeline_evaluation", "confidence": "high"}
        ],
        "assumptions": [
            "Monthly turnover of ~150,000 DH consistent with brand market profile and advertising intensity",
            "Shopify Basic/Standard plan + Releasit paid plan detected in source code"
        ],
        "risks": [
            "Continued Shopify operation costs merchant >57,000 DH/year in direct fees and commission penalties"
        ],
        "blockers": [],
        "gate_results": [
            {"criterion": "Multi-vector audit completeness", "result": "pass", "details": "Performance, checkout friction, and financial drain calculated"},
            {"criterion": "Evidence attribution", "result": "pass", "details": "Source URL and script signatures verified"},
            {"criterion": "Mathematical consistency", "result": "pass", "details": "Annual ROI calculations strictly aligned"}
        ],
        "recommended_next_action": f"Run Agent 3 (Solution Architect & UX Planner) on lead '{lead_id}'"
    }

    return handoff


# Evidence-only implementation. Kept below the original generator so imports resolve
# to this stricter version while existing historical reports remain readable.
def run_audit(lead_id: str, workspace: str, brand_name: str, target_url: str):
    audit_dir = os.path.join(workspace, "audit")
    evidence_dir = os.path.join(workspace, "evidence")
    os.makedirs(audit_dir, exist_ok=True)
    network_path = os.path.join(evidence_dir, "network_evidence.json")
    lead_path = os.path.join(workspace, "lead.json")
    report_path = os.path.join(audit_dir, "audit_report.json")
    summary_path = os.path.join(audit_dir, "audit_summary.md")

    network = {}
    lead = {}
    if os.path.exists(network_path):
        with open(network_path, "r", encoding="utf-8") as f:
            network = json.load(f)
    if os.path.exists(lead_path):
        with open(lead_path, "r", encoding="utf-8") as f:
            lead = json.load(f)

    collection_method = network.get("method", "missing")
    http_status = network.get("http_status")
    live_evidence = (collection_method == "live_http_get" and http_status == 200) or bool(network.get("raw_html_sha256"))
    detected_apps = network.get("detected_apps", [])
    script_count = network.get("total_external_scripts")
    measured = {
        "http_status": http_status,
        "external_script_count": script_count,
        "detected_apps": detected_apps,
        "server_header": network.get("server"),
        "collection_method": collection_method,
        "raw_html_sha256": network.get("raw_html_sha256"),
    }

    financial_inputs = lead.get("financial_inputs", {})
    required_financial = {"monthly_revenue_mad", "monthly_saas_usd", "usd_mad_rate", "transaction_fee_rate"}
    if required_financial.issubset(financial_inputs):
        monthly_revenue = float(financial_inputs["monthly_revenue_mad"])
        monthly_saas_usd = float(financial_inputs["monthly_saas_usd"])
        usd_mad_rate = float(financial_inputs["usd_mad_rate"])
        fee_rate = float(financial_inputs["transaction_fee_rate"])
        annual_saas = monthly_saas_usd * usd_mad_rate * 12
        annual_fees = monthly_revenue * fee_rate * 12
        financial = {
            "status": "calculated_from_user_inputs",
            "inputs": financial_inputs,
            "annual_saas_mad": round(annual_saas, 2),
            "annual_transaction_fees_mad": round(annual_fees, 2),
            "annual_total_mad": round(annual_saas + annual_fees, 2),
        }
    else:
        financial = {
            "status": "not_calculated",
            "missing_inputs": sorted(required_financial - set(financial_inputs)),
            "note": "No merchant financial figures were supplied; no cost or savings claim is made.",
        }

    findings = []
    if script_count is not None:
        findings.append(f"Observed {script_count} external script tags in the captured storefront HTML.")
    if detected_apps:
        findings.append("Detected script signatures: " + ", ".join(detected_apps) + ".")
    if not findings:
        findings.append("No technical finding could be substantiated from the captured evidence.")

    report = {
        "lead_id": lead_id,
        "brand_name": brand_name,
        "target_url": target_url,
        "audited_at": utc_now_iso(),
        "evidence_quality": "verified_live_capture" if live_evidence else "insufficient",
        "measured_storefront_facts": measured,
        "financial_analysis": financial,
        "findings": findings,
        "not_measured": [
            "Lighthouse performance score",
            "Core Web Vitals",
            "JavaScript transfer size",
            "conversion or abandonment rate",
        ],
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    financial_text = (
        f"Calculated annual scenario: {financial['annual_total_mad']:,.2f} MAD from supplied merchant inputs."
        if financial["status"] == "calculated_from_user_inputs"
        else "Financial impact was not calculated because merchant-specific inputs were not supplied."
    )
    summary = f"""# Evidence-backed audit — {brand_name}

**Store:** {target_url}
**Captured:** {network.get('collected_at', 'unknown')}
**Evidence quality:** {report['evidence_quality']}

## Verified observations

{os.linesep.join(f'- {item}' for item in findings)}

## Financial analysis

{financial_text}

## Explicit limitations

- Lighthouse and Core Web Vitals were not run and are not claimed.
- Script tags do not by themselves prove performance impact.
- App signatures indicate presence, not subscription tier or merchant cost.
- Conversion, revenue, Shopify fees, and savings require merchant-supplied figures.
"""
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)

    status = "passed" if live_evidence else "blocked"
    blocker = [] if live_evidence else ["A successful live storefront capture is required for an evidence-backed audit"]
    return {
        "status": status,
        "summary": f"Evidence-backed audit completed for {brand_name}." if live_evidence else f"Audit blocked for {brand_name}: live evidence is unavailable.",
        "artifacts": [
            {"path": f"leads/{lead_id}/audit/audit_report.json", "schema_version": "2.0", "sha256": hash_file(report_path)},
            {"path": f"leads/{lead_id}/audit/audit_summary.md", "schema_version": "2.0", "sha256": hash_file(summary_path)},
        ],
        "evidence": [{"source": target_url, "collected_at": network.get("collected_at", utc_now_iso()), "method": collection_method, "confidence": "high" if live_evidence else "low"}],
        "assumptions": [],
        "risks": ["HTML-only inspection cannot establish runtime performance"],
        "blockers": blocker,
        "gate_results": [
            {"criterion": "Live evidence available", "result": "pass" if live_evidence else "fail", "details": f"method={collection_method}, HTTP={http_status}"},
            {"criterion": "No invented performance metrics", "result": "pass", "details": "Unmeasured values are explicitly null/not measured"},
            {"criterion": "Financial claims require supplied inputs", "result": "pass", "details": financial["status"]},
        ],
        "recommended_next_action": f"Run Agent 3 (Solution Architect) for '{lead_id}'" if status == "passed" else f"Rerun discovery for '{lead_id}' with network access",
    }
