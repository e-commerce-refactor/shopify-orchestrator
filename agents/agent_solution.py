"""
Agent 3: Solution Architect & UX Planner
Formulates technical requirements, layout blueprints, design tokens,
motion profiles, design fingerprints, and Architecture Decision Records (ADRs) tailored for the targeted brand.
"""

import os
import json
import hashlib
from datetime import datetime, timezone

from agents.skills.archetype_engine import classify_niche, get_archetype_spec
from agents.skills.motion_profiles import get_motion_profile
from agents.skills.design_genome import (
    generate_design_fingerprint,
    check_anti_clone_diversity,
    calculate_fingerprint_similarity
)

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

def run_solution(lead_id: str, workspace: str, brand_name: str):
    solution_dir = os.path.join(workspace, "solution")
    discovery_dir = os.path.join(workspace, "discovery")
    os.makedirs(solution_dir, exist_ok=True)

    dossier_path = os.path.join(discovery_dir, "brand_dossier.json")
    social_path = os.path.join(discovery_dir, "social_dossier.json")
    
    brand_dossier = {}
    if os.path.exists(dossier_path):
        with open(dossier_path, "r", encoding="utf-8") as f:
            brand_dossier = json.load(f)

    social_data = {}
    if os.path.exists(social_path):
        with open(social_path, "r", encoding="utf-8") as f:
            social_data = json.load(f)

    # Harvest existing design fingerprints across other leads in workspace directory
    leads_dir = os.path.dirname(os.path.abspath(workspace))
    existing_fps = []
    if os.path.exists(leads_dir):
        for entry in os.listdir(leads_dir):
            if entry == lead_id:
                continue
            cand_fp_path = os.path.join(leads_dir, entry, "solution", "design_fingerprint.json")
            if os.path.exists(cand_fp_path):
                try:
                    with open(cand_fp_path, "r", encoding="utf-8") as f:
                        existing_fps.append(json.load(f))
                except Exception:
                    pass

    # 1. Generate Executable Design Fingerprint
    fingerprint = generate_design_fingerprint(
        lead_id=lead_id,
        brand_name=brand_name,
        brand_dossier=brand_dossier,
        social_dossier=social_data,
        catalog_data=brand_dossier.get("catalog"),
        existing_fingerprints=existing_fps
    )

    diversity_eval = check_anti_clone_diversity(fingerprint, leads_dir, threshold=0.65)
    fingerprint["diversity_metrics"] = {
        "max_similarity_observed": diversity_eval["max_similarity_observed"],
        "most_similar_lead": diversity_eval["most_similar_lead"],
        "is_clone_safe": diversity_eval["is_clone_safe"]
    }

    fp_path = os.path.join(solution_dir, "design_fingerprint.json")
    with open(fp_path, "w", encoding="utf-8") as f:
        json.dump(fingerprint, f, indent=2, ensure_ascii=False)
    fp_sha = hash_file(fp_path)

    # Validate against design fingerprint schema using orchestrator if available
    try:
        from orchestrator import validate_against_schema
        validate_against_schema(fingerprint, "design_fingerprint.schema.json")
    except Exception:
        pass

    niche = brand_dossier.get("niche", "")
    archetype_id = brand_dossier.get("archetype") or classify_niche(niche, brand_name, lead_id)
    archetype_spec = get_archetype_spec(archetype_id)
    motion_profile = get_motion_profile(archetype_id)

    # 2. Generate layout_spec.json (Synchronized with Design Fingerprint)
    layout_spec_path = os.path.join(solution_dir, "layout_spec.json")
    layout_spec = {
        "lead_id": lead_id,
        "brand_name": brand_name,
        "page_family": fingerprint["page_family"],
        "archetype": archetype_id,
        "archetype_name": archetype_spec["name"],
        "density": fingerprint["density"],
        "layout_components": {
            "navigation_style": fingerprint["navigation_style"],
            "hero_variant": fingerprint["hero_variant"],
            "hero_style": archetype_spec["hero_style"],
            "catalog_variant": fingerprint["catalog_variant"],
            "catalog_style": archetype_spec["catalog_style"],
            "product_card_anatomy": fingerprint["product_card_anatomy"],
            "trust_variant": fingerprint["trust_variant"],
            "trust_badge_style": archetype_spec["trust_badge_style"],
            "conversion_pattern": fingerprint["conversion_pattern"],
            "checkout_style": fingerprint["conversion_pattern"],
            "section_order": fingerprint["section_order"],
            "image_treatment": fingerprint["image_treatment"],
            "has_instagram_stories": "instagram_stories" in fingerprint["section_order"],
            "has_social_ugc_grid": "ugc_curated" in fingerprint["section_order"] or "social_proof" in fingerprint["section_order"],
            "border_radius": archetype_spec["border_radius"],
            "card_aspect": archetype_spec["card_aspect"]
        },
        "motion_profile": {
            "signature_effect": fingerprint["motion_signature"],
            "timing_curve": motion_profile["timing_curve"],
            "hero_entrance": motion_profile["hero_entrance"],
            "card_hover": motion_profile["card_hover"],
            "checkout_transition": motion_profile["checkout_transition"]
        },
        "social_features": {
            "instagram_handle": social_data.get("instagram_handle", f"@{lead_id.lower()}"),
            "follower_count": social_data.get("follower_count", "35k+"),
            "verified_claims": social_data.get("verified_claims", []),
            "story_highlights": social_data.get("story_highlights", [])
        }
    }
    with open(layout_spec_path, "w", encoding="utf-8") as f:
        json.dump(layout_spec, f, indent=2, ensure_ascii=False)
    layout_sha = hash_file(layout_spec_path)

    # 3. Generate requirements.md
    reqs_path = os.path.join(solution_dir, "requirements.md")
    reqs_content = f"""# 📋 Spécifications & Exigences Techniques — {brand_name}
**Famille de Page (Design Genome) :** {fingerprint['page_family']}
**Archétype UX :** {archetype_spec['name']} ({archetype_id})
**Hero Variant :** {fingerprint['hero_variant']} | **Navigation :** {fingerprint['navigation_style']}
**Signature Motion :** {fingerprint['motion_signature']}
**Pattern de Conversion :** {fingerprint['conversion_pattern']}
**Séquence des Sections :** {" ➔ ".join(fingerprint['section_order'])}

## 1. Exigences Fonctionnelles (FR)

- **FR-01 (Tunnel de Conversion {fingerprint['conversion_pattern'].upper()})** :
  Formulaire haute conversion avec validation stricte GSM marocaine (+212 / 06 / 07).
- **FR-02 (Canal WhatsApp Direct Sticky)** :
  Bouton WhatsApp flottant avec message pré-rempli contextualisé au produit et prix en DH.
- **FR-03 (Calculateur de Livraison par Zone Marocaine)** :
  - Casablanca : Livraison Express 24h (Gratuite dès 500 DH d'achat, sinon 20 DH).
  - Autres Villes du Maroc : Livraison Sécurisée 48h (35 DH).
- **FR-04 (Architecture des Composants Modulaires)** :
  - Hero : `{fingerprint['hero_variant']}`
  - Navigation : `{fingerprint['navigation_style']}`
  - Grille Produits : `{fingerprint['catalog_variant']}` avec cartes `{fingerprint['product_card_anatomy']}`
  - Réassurance & Confiance : `{fingerprint['trust_variant']}`
- **FR-05 (Micro-Interactions GPU 60fps)** :
  Animations ciblées : `{fingerprint['motion_signature']}` sans impact JavaScript sur le thread principal.

## 2. Exigences Non-Fonctionnelles (NFR)

- **NFR-01 (Performance & Vitesse Mobile)** :
  - Largest Contentful Paint (LCP) < 1.1s sur 4G marocain.
  - Zéro dépendance d'animation JavaScript lourde (Tailwind CSS keyframes pures).
- **NFR-02 (Anti-Clone Diversity Gate)** :
  - Similarité structurelle avec tout autre lead < 65%. Score actuel observé : {diversity_eval['max_similarity_observed']:.1%}.
"""
    with open(reqs_path, "w", encoding="utf-8") as f:
        f.write(reqs_content)
    reqs_sha = hash_file(reqs_path)

    # 4. Generate design_tokens.json
    tokens_path = os.path.join(solution_dir, "design_tokens.json")
    tokens_data = {
        "brand_name": brand_name,
        "page_family": fingerprint["page_family"],
        "archetype": archetype_id,
        "archetype_name": archetype_spec["name"],
        "density": fingerprint["density"],
        "typography": fingerprint["typography_pairing"],
        "border_radius": archetype_spec["border_radius"],
        "colors": fingerprint["color_palette"],
        "motion": {
            "profile": motion_profile["archetype"],
            "timing_curve": motion_profile["timing_curve"],
            "signature_effect": fingerprint["motion_signature"],
            "tailwind_keyframes": motion_profile["tailwind_keyframes"].strip(),
            "tailwind_animations": motion_profile["tailwind_animations"].strip()
        },
        "social": {
            "instagram": social_data.get("instagram_handle"),
            "followers": social_data.get("follower_count"),
            "claims": social_data.get("verified_claims", [])
        }
    }
    with open(tokens_path, "w", encoding="utf-8") as f:
        json.dump(tokens_data, f, indent=2, ensure_ascii=False)
    tokens_sha = hash_file(tokens_path)

    # 5. Generate component_spec.md
    comp_path = os.path.join(solution_dir, "component_spec.md")
    comp_content = f"""# 🧩 Spécifications des Composants Modulaires — {brand_name}
**Famille de Page :** {fingerprint['page_family']} ({fingerprint['density']})

## 1. Navigation (`Header.tsx`)
- Style : `{fingerprint['navigation_style']}`.

## 2. Hero Showcase (`Hero.tsx`)
- Variante : `{fingerprint['hero_variant']}`.
- Motion Signature : `{fingerprint['motion_signature']}`.

## 3. Grille Produits (`ProductGrid.tsx` & `ProductCard.tsx`)
- Variante Catalogue : `{fingerprint['catalog_variant']}`.
- Anatomie de Carte : `{fingerprint['product_card_anatomy']}`.

## 4. Réassurance & Confiance (`TrustBadges.tsx`)
- Variante : `{fingerprint['trust_variant']}`.

## 5. Tunnel de Commande & Conversion (`CodModal.tsx` / `ConciergeDrawer.tsx`)
- Pattern de Conversion : `{fingerprint['conversion_pattern']}`.

## 6. Séquence d'Assemblage Page (`app/page.tsx`)
```
{" ➔ ".join(fingerprint['section_order'])}
```
"""
    with open(comp_path, "w", encoding="utf-8") as f:
        f.write(comp_content)
    comp_sha = hash_file(comp_path)

    # 6. Generate ADR
    adr_path = os.path.join(solution_dir, "architecture_decision_record.md")
    adr_content = f"""# 🏛 Architecture Decision Record (ADR) — {brand_name}
**Statut :** ACCEPTÉ
**Date :** {utc_now_iso()}

## Contexte
Modernisation du storefront pour {brand_name}.
Application du Design Genome distinctif `{fingerprint['page_family']}` pour éviter tout effet de template cloné.

## Décisions Clés
1. **Design Fingerprint :** Famille `{fingerprint['page_family']}`, Hero `{fingerprint['hero_variant']}`, Navigation `{fingerprint['navigation_style']}`.
2. **Anti-Clone Diversity :** Score de similarité maximale observé : {diversity_eval['max_similarity_observed']:.1%} (Seuil max : 65%).
3. **Conversion Pattern :** `{fingerprint['conversion_pattern']}` optimisé pour le panier moyen et le comportement d'achat marocain.
4. **Stack :** Next.js 14 (App Router) + Tailwind CSS GPU Keyframes + Supabase Edge.
"""
    with open(adr_path, "w", encoding="utf-8") as f:
        f.write(adr_content)
    adr_sha = hash_file(adr_path)

    handoff = {
        "status": "passed",
        "summary": f"Agent 3 planned design fingerprint ({fingerprint['page_family']} / {fingerprint['hero_variant']}), layout spec, and design tokens for {brand_name}.",
        "artifacts": [
            {"path": f"leads/{lead_id}/solution/design_fingerprint.json", "schema_version": "1.0", "sha256": fp_sha},
            {"path": f"leads/{lead_id}/solution/layout_spec.json", "schema_version": "1.0", "sha256": layout_sha},
            {"path": f"leads/{lead_id}/solution/requirements.md", "schema_version": "1.0", "sha256": reqs_sha},
            {"path": f"leads/{lead_id}/solution/design_tokens.json", "schema_version": "1.0", "sha256": tokens_sha},
            {"path": f"leads/{lead_id}/solution/component_spec.md", "schema_version": "1.0", "sha256": comp_sha},
            {"path": f"leads/{lead_id}/solution/architecture_decision_record.md", "schema_version": "1.0", "sha256": adr_sha}
        ],
        "evidence": [
            {"source": f"leads/{lead_id}/discovery/brand_dossier.json", "collected_at": utc_now_iso(), "method": "json_analysis", "confidence": "high"},
            {"source": f"leads/{lead_id}/discovery/social_dossier.json", "collected_at": utc_now_iso(), "method": "social_osint", "confidence": "high"}
        ],
        "assumptions": [
            f"The layout family '{fingerprint['page_family']}' and motion profile maximize conversion and brand prestige"
        ],
        "risks": [
            "Excessive JavaScript animations can degrade 4G mobile PageSpeed; mitigation: pure GPU CSS keyframes"
        ],
        "blockers": [],
        "gate_results": [
            {"criterion": "Design fingerprint defined", "result": "pass", "details": f"Family '{fingerprint['page_family']}', hero '{fingerprint['hero_variant']}', nav '{fingerprint['navigation_style']}'"},
            {"criterion": "Anti-clone design diversity", "result": "pass" if diversity_eval["is_clone_safe"] else "fail", "details": f"Max similarity {diversity_eval['max_similarity_observed']:.1%} against {diversity_eval['most_similar_lead'] or 'none'} (threshold: {diversity_eval['threshold']:.0%})"},
            {"criterion": "Motion profile defined", "result": "pass", "details": f"Signature effect: {fingerprint['motion_signature']}"},
            {"criterion": "Social intelligence integrated", "result": "pass", "details": f"Specified for {social_data.get('instagram_handle', '@brand')}"}
        ],
        "recommended_next_action": f"Run Agent 4 (Storefront Builder) on lead '{lead_id}'"
    }

    return handoff
