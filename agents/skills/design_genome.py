"""
Skill: Design Genome & Multi-Archetype Layout Engine
Implements authentic per-lead design genomes, distinctive page compositions,
component anatomy variants, deterministic seed variation, and anti-clone quality gates.
"""

import os
import re
import json
import math
import hashlib
from typing import Dict, Any, List, Tuple, Optional

# =============================================================================
# 1. Page Families and Architectural Blueprints
# =============================================================================

PAGE_FAMILIES = {
    "technical_commerce": {
        "id": "technical_commerce",
        "name": "Technical Commerce & High-Performance Gadgets",
        "density": "compact_high_info",
        "navigation_variants": ["dense_mega_menu", "sticky_compact_bar"],
        "hero_variants": ["TechnicalDemoHero"],
        "catalog_variants": ["SpecificationGrid", "ComparisonMatrix"],
        "card_anatomies": ["horizontal_spec_card", "compact_tile"],
        "trust_variants": ["technical_specs_strip"],
        "conversion_patterns": ["sticky_quick_order", "fast_cod_modal"],
        "image_treatment": "technical_sharp",
        "motion_signature": "laser_scan_and_radar_pulse",
        "section_permutations": [
            ["navigation", "hero", "specs_strip", "comparison_matrix", "catalog", "social_proof", "fast_checkout", "footer"],
            ["navigation", "hero", "specs_strip", "catalog", "comparison_matrix", "social_proof", "fast_checkout", "footer"],
            ["navigation", "hero", "comparison_matrix", "catalog", "specs_strip", "social_proof", "fast_checkout", "footer"]
        ]
    },
    "luxury_editorial": {
        "id": "luxury_editorial",
        "name": "Luxury Haute Joaillerie & High Editorial",
        "density": "spacious_cinematic",
        "navigation_variants": ["centered_minimal", "split_brand_nav"],
        "hero_variants": ["EditorialCampaignHero", "CollectionCollageHero"],
        "catalog_variants": ["EditorialLookbook", "CollectionCarousel"],
        "card_anatomies": ["portrait_hover_reveal", "editorial_framed_card"],
        "trust_variants": ["craftsmanship_seal", "social_proof_marquee"],
        "conversion_patterns": ["concierge_drawer", "fast_cod_modal"],
        "image_treatment": "warm_editorial",
        "motion_signature": "diamond_sparkle_and_velvet_float",
        "section_permutations": [
            ["navigation", "hero", "craftsmanship_seal", "instagram_stories", "catalog", "ugc_curated", "appointment_drawer", "footer"],
            ["navigation", "hero", "catalog", "craftsmanship_seal", "ugc_curated", "fast_checkout", "footer"],
            ["navigation", "hero", "instagram_stories", "catalog", "craftsmanship_seal", "ugc_curated", "appointment_drawer", "footer"],
            ["navigation", "hero", "craftsmanship_seal", "catalog", "ugc_curated", "appointment_drawer", "footer"]
        ]
    },
    "luxury_horlogerie": {
        "id": "luxury_horlogerie",
        "name": "Haute Horlogerie & Precision Chronometers",
        "density": "balanced_precision",
        "navigation_variants": ["split_brand_nav", "centered_minimal"],
        "hero_variants": ["HorlogerieCockpitHero"],
        "catalog_variants": ["SpecificationGrid", "CollectionCarousel"],
        "card_anatomies": ["editorial_framed_card", "horizontal_spec_card"],
        "trust_variants": ["chronometer_telemetry"],
        "conversion_patterns": ["fast_cod_modal", "concierge_drawer"],
        "image_treatment": "obsidian_sheen",
        "motion_signature": "tourbillon_sweep_and_sapphire_sheen",
        "section_permutations": [
            ["navigation", "hero", "chronometer_telemetry", "catalog", "instagram_stories", "ugc_curated", "fast_checkout", "footer"],
            ["navigation", "hero", "catalog", "chronometer_telemetry", "ugc_curated", "fast_checkout", "footer"],
            ["navigation", "hero", "instagram_stories", "chronometer_telemetry", "catalog", "ugc_curated", "fast_checkout", "footer"]
        ]
    },
    "fashion_lookbook": {
        "id": "fashion_lookbook",
        "name": "Streetwear & Kinetic Fashion Lookbook",
        "density": "brutalist_bold",
        "navigation_variants": ["split_brand_nav", "sticky_compact_bar"],
        "hero_variants": ["CollectionCollageHero", "EditorialCampaignHero"],
        "catalog_variants": ["EditorialLookbook", "CollectionCarousel"],
        "card_anatomies": ["portrait_hover_reveal", "compact_tile"],
        "trust_variants": ["streetwear_pills", "social_proof_marquee"],
        "conversion_patterns": ["bottom_sheet_drawer", "fast_cod_modal"],
        "image_treatment": "high_contrast_grain",
        "motion_signature": "marquee_ticker_and_stamp_bounce",
        "section_permutations": [
            ["navigation", "hero", "kinetic_ticker", "catalog", "instagram_stories", "social_proof", "fast_checkout", "footer"],
            ["navigation", "hero", "catalog", "kinetic_ticker", "social_proof", "fast_checkout", "footer"]
        ]
    },
    "artisan_story": {
        "id": "artisan_story",
        "name": "Artisanal Terroir, Leather & Heritage Story",
        "density": "organic_warm",
        "navigation_variants": ["centered_minimal", "split_brand_nav"],
        "hero_variants": ["FounderStoryHero", "EditorialCampaignHero"],
        "catalog_variants": ["HandcraftedTiles", "EditorialLookbook"],
        "card_anatomies": ["artisan_stamp_card", "editorial_framed_card"],
        "trust_variants": ["wax_seal_badges", "craftsmanship_seal"],
        "conversion_patterns": ["fast_cod_modal", "concierge_drawer"],
        "image_treatment": "natural_sunlight",
        "motion_signature": "stamp_bounce_and_velvet_float",
        "section_permutations": [
            ["navigation", "hero", "founder_story", "catalog", "wax_seal_badges", "ugc_curated", "fast_checkout", "footer"],
            ["navigation", "hero", "wax_seal_badges", "founder_story", "catalog", "ugc_curated", "fast_checkout", "footer"]
        ]
    },
    "beauty_routine": {
        "id": "beauty_routine",
        "name": "Clean Organic Beauty & Skincare Regimens",
        "density": "clean_fluid",
        "navigation_variants": ["centered_minimal", "dense_mega_menu"],
        "hero_variants": ["ClinicalAuthorityHero", "EditorialCampaignHero"],
        "catalog_variants": ["RoutineBuilder", "EditorialLookbook"],
        "card_anatomies": ["compact_tile", "portrait_hover_reveal"],
        "trust_variants": ["botanical_pills", "clinical_badges"],
        "conversion_patterns": ["fast_cod_modal", "concierge_drawer"],
        "image_treatment": "dewy_soft_focus",
        "motion_signature": "smooth_dew_float",
        "section_permutations": [
            ["navigation", "hero", "botanical_pills", "routine_builder", "catalog", "ugc_curated", "fast_checkout", "footer"],
            ["navigation", "hero", "routine_builder", "catalog", "botanical_pills", "ugc_curated", "fast_checkout", "footer"]
        ]
    },
    "clinical_trust": {
        "id": "clinical_trust",
        "name": "Medical, Orthopedic & Clinical Authority",
        "density": "structured_medical",
        "navigation_variants": ["dense_mega_menu", "sticky_compact_bar"],
        "hero_variants": ["ClinicalAuthorityHero", "TechnicalDemoHero"],
        "catalog_variants": ["SpecificationGrid", "ComparisonMatrix"],
        "card_anatomies": ["horizontal_spec_card", "compact_tile"],
        "trust_variants": ["clinical_badges", "technical_specs_strip"],
        "conversion_patterns": ["sticky_quick_order", "fast_cod_modal"],
        "image_treatment": "clinical_clean",
        "motion_signature": "radar_pulse_and_smooth_glide",
        "section_permutations": [
            ["navigation", "hero", "clinical_badges", "comparison_matrix", "catalog", "social_proof", "fast_checkout", "footer"],
            ["navigation", "hero", "clinical_badges", "catalog", "comparison_matrix", "social_proof", "fast_checkout", "footer"]
        ]
    }
}

# =============================================================================
# 2. Color Palette Permutation Pools (Guarantees Distinct Visual Tonality)
# =============================================================================

COLOR_PALETTES = {
    "luxury_editorial": [
        {
            "name": "Warm Ivory & Champagne 18K",
            "background": "#FBF8F3",
            "surface": "#FFFFFF",
            "border": "#EADBCE",
            "text_primary": "#1F1F1F",
            "text_secondary": "#7D7065",
            "accent": "#C5A880",
            "accent_secondary": "#8C7A6B"
        },
        {
            "name": "Velvet Midnight & Rose Gold",
            "background": "#0F0D15",
            "surface": "#1A1724",
            "border": "#2E283E",
            "text_primary": "#FBF8F3",
            "text_secondary": "#A89FA8",
            "accent": "#E0A96D",
            "accent_secondary": "#B07D4C"
        },
        {
            "name": "Pearl Alabaster & White Gold",
            "background": "#F5F5F7",
            "surface": "#FFFFFF",
            "border": "#E2E2E8",
            "text_primary": "#18181B",
            "text_secondary": "#71717A",
            "accent": "#9E8A78",
            "accent_secondary": "#57534E"
        }
    ],
    "luxury_horlogerie": [
        {
            "name": "Obsidian Titanium & Emerald",
            "background": "#0B0E14",
            "surface": "#151B26",
            "border": "#253043",
            "text_primary": "#F1F5F9",
            "text_secondary": "#94A3B8",
            "accent": "#10B981",
            "accent_secondary": "#059669"
        },
        {
            "name": "Carbon Graphite & Sapphire Crown",
            "background": "#0D1117",
            "surface": "#161D2A",
            "border": "#243247",
            "text_primary": "#F8FAFC",
            "text_secondary": "#8899A6",
            "accent": "#38BDF8",
            "accent_secondary": "#0284C7"
        },
        {
            "name": "Matte Anthracite & Gold Chrono",
            "background": "#121214",
            "surface": "#1C1C20",
            "border": "#2D2D35",
            "text_primary": "#FFFFFF",
            "text_secondary": "#A1A1AA",
            "accent": "#D4AF37",
            "accent_secondary": "#A68020"
        }
    ],
    "technical_commerce": [
        {
            "name": "Cyber Blue & Neon Cyan",
            "background": "#070A10",
            "surface": "#0E131F",
            "border": "#1E293B",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "accent": "#00E5FF",
            "accent_secondary": "#10B981"
        },
        {
            "name": "Stealth Black & Electric Amber",
            "background": "#0A0B0E",
            "surface": "#14161C",
            "border": "#222631",
            "text_primary": "#F3F4F6",
            "text_secondary": "#9CA3AF",
            "accent": "#F59E0B",
            "accent_secondary": "#D97706"
        },
        {
            "name": "Carbon Slate & Signal Red",
            "background": "#0F1115",
            "surface": "#181B22",
            "border": "#2A2E39",
            "text_primary": "#F9FAFB",
            "text_secondary": "#9CA3AF",
            "accent": "#EF4444",
            "accent_secondary": "#DC2626"
        }
    ],
    "fashion_lookbook": [
        {
            "name": "Brutalist Neon Coral",
            "background": "#0F0F0F",
            "surface": "#1A1A1A",
            "border": "#333333",
            "text_primary": "#FFFFFF",
            "text_secondary": "#A3A3A3",
            "accent": "#FF3366",
            "accent_secondary": "#E5E5E5"
        },
        {
            "name": "Industrial Acid Lime",
            "background": "#0B0C0E",
            "surface": "#15171C",
            "border": "#272B33",
            "text_primary": "#FFFFFF",
            "text_secondary": "#9E9E9E",
            "accent": "#CCFF00",
            "accent_secondary": "#FFFFFF"
        }
    ],
    "artisan_story": [
        {
            "name": "Terracotta & Saddle Leather",
            "background": "#FBF8F3",
            "surface": "#FFFFFF",
            "border": "#EADBCE",
            "text_primary": "#2C221E",
            "text_secondary": "#6B5E55",
            "accent": "#C46238",
            "accent_secondary": "#8B5A2B"
        },
        {
            "name": "Olive Grove & Sunbaked Ochre",
            "background": "#FAF7F2",
            "surface": "#FFFFFF",
            "border": "#E5DDD3",
            "text_primary": "#242820",
            "text_secondary": "#606558",
            "accent": "#606C38",
            "accent_secondary": "#DDA15E"
        }
    ],
    "beauty_routine": [
        {
            "name": "Dewy Rose & Pure Pearl",
            "background": "#FCF9F9",
            "surface": "#FFFFFF",
            "border": "#F3E8E8",
            "text_primary": "#2A2426",
            "text_secondary": "#7D6E72",
            "accent": "#D47A88",
            "accent_secondary": "#A65965"
        },
        {
            "name": "Botanical Sage & Dewdrop",
            "background": "#F8FAF8",
            "surface": "#FFFFFF",
            "border": "#E2EAE2",
            "text_primary": "#1F2820",
            "text_secondary": "#68756A",
            "accent": "#5E8C6A",
            "accent_secondary": "#3E6649"
        }
    ],
    "clinical_trust": [
        {
            "name": "Clinical Cobalt & Sterile White",
            "background": "#F7FAFC",
            "surface": "#FFFFFF",
            "border": "#E2E8F0",
            "text_primary": "#0F172A",
            "text_secondary": "#64748B",
            "accent": "#2563EB",
            "accent_secondary": "#0D9488"
        }
    ]
}

# =============================================================================
# 3. Typography Pairings
# =============================================================================

TYPOGRAPHY_PAIRINGS = {
    "luxury_editorial": [
        {"headings": "Playfair Display, Cormorant Garamond, serif", "body": "Plus Jakarta Sans, sans-serif", "mono": "monospace"},
        {"headings": "Bodoni Moda, Didot, serif", "body": "Inter, sans-serif", "mono": "monospace"},
        {"headings": "Cinzel, Cormorant, serif", "body": "Outfit, sans-serif", "mono": "monospace"}
    ],
    "luxury_horlogerie": [
        {"headings": "Plus Jakarta Sans, system-ui, sans-serif", "body": "Inter, sans-serif", "mono": "ui-monospace, Menlo, monospace"},
        {"headings": "Chakra Petch, system-ui, sans-serif", "body": "Plus Jakarta Sans, sans-serif", "mono": "monospace"},
        {"headings": "Outfit, sans-serif", "body": "Inter, sans-serif", "mono": "monospace"}
    ],
    "technical_commerce": [
        {"headings": "Plus Jakarta Sans, system-ui, sans-serif", "body": "Inter, sans-serif", "mono": "ui-monospace, Menlo, monospace"},
        {"headings": "Space Grotesk, sans-serif", "body": "Inter, sans-serif", "mono": "monospace"}
    ],
    "fashion_lookbook": [
        {"headings": "Syne, Montserrat, sans-serif", "body": "Space Grotesk, Inter, sans-serif", "mono": "Space Mono, monospace"},
        {"headings": "Clash Display, Montserrat, sans-serif", "body": "Inter, sans-serif", "mono": "monospace"}
    ],
    "artisan_story": [
        {"headings": "Playfair Display, Georgia, serif", "body": "Plus Jakarta Sans, sans-serif", "mono": "monospace"},
        {"headings": "Lora, Georgia, serif", "body": "Outfit, sans-serif", "mono": "monospace"}
    ],
    "beauty_routine": [
        {"headings": "Playfair Display, serif", "body": "Outfit, Inter, sans-serif", "mono": "monospace"},
        {"headings": "Cormorant Garamond, serif", "body": "Plus Jakarta Sans, sans-serif", "mono": "monospace"}
    ],
    "clinical_trust": [
        {"headings": "Plus Jakarta Sans, sans-serif", "body": "Inter, sans-serif", "mono": "monospace"}
    ]
}

# =============================================================================
# 4. Deterministic Seed and Brand Signal Analysis
# =============================================================================

def compute_layout_seed(lead_id: str) -> int:
    """Computes a deterministic integer seed from the lead_id string."""
    h = hashlib.sha256(lead_id.strip().lower().encode("utf-8")).hexdigest()
    return int(h[:8], 16)

def infer_page_family_from_signals(
    lead_id: str,
    brand_name: str,
    brand_dossier: Dict[str, Any],
    social_dossier: Dict[str, Any],
    catalog_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Examines real brand signals (archetype, niche, keywords, prices, product catalog, social presence)
    to classify the store into its genuine Page Family.
    """
    existing_arch = brand_dossier.get("archetype", "")
    if existing_arch == "luxury_joaillerie":
        return "luxury_editorial"
    if existing_arch == "luxury_horlogerie":
        return "luxury_horlogerie"
    if existing_arch == "tech_gadgets":
        return "technical_commerce"
    if existing_arch == "fashion_streetwear":
        return "fashion_lookbook"
    if existing_arch == "artisanal_craft":
        return "artisan_story"
    if existing_arch == "beauty_cosmetics":
        return "beauty_routine"
    if existing_arch == "health_medical":
        return "clinical_trust"

    text_corpus = f"{lead_id} {brand_name} {brand_dossier.get('niche', '')} {brand_dossier.get('category', '')}".lower()
    
    products = []
    if catalog_data and "products" in catalog_data:
        products = catalog_data["products"]
    elif "catalog" in brand_dossier and "products" in brand_dossier["catalog"]:
        products = brand_dossier["catalog"]["products"]
        
    avg_price = 0.0
    if products:
        prices = [float(p.get("price", 0)) for p in products if p.get("price")]
        if prices:
            avg_price = sum(prices) / len(prices)

    if any(k in text_corpus for k in ["70mai", "dashcam", "camera", "tech", "gadget", "gps", "electronique", "smart"]):
        return "technical_commerce"

    if any(k in text_corpus for k in ["joaillerie", "anulus", "diamant", "or 18k", "bague", "solitaire", "collier", "bijoux"]):
        return "luxury_editorial"

    if any(k in text_corpus for k in ["montre", "horlogerie", "watch", "chrono", "tourbillon", "automatique"]):
        return "luxury_horlogerie"

    if any(k in text_corpus for k in ["cuir", "artisanat", "beldi", "maroquinerie", "fait main", "tannage", "terroir"]):
        return "artisan_story"

    if any(k in text_corpus for k in ["beaute", "beauty", "cosmetique", "soin", "skincare", "visage", "argan", "parfum"]):
        return "beauty_routine"

    if any(k in text_corpus for k in ["sante", "medical", "orthopedique", "diabete", "clinique"]):
        return "clinical_trust"

    if any(k in text_corpus for k in ["fashion", "streetwear", "shoes", "chaussures", "mode", "vetement", "sneakers"]):
        return "fashion_lookbook"

    if avg_price >= 1200:
        return "luxury_editorial"
    elif avg_price <= 400 and avg_price > 0:
        return "technical_commerce"
        
    return "luxury_editorial"

# =============================================================================
# 5. Anti-Clone Quality Gate & Similarity Metrics
# =============================================================================

def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    clean = hex_str.lstrip("#")
    if len(clean) == 3:
        clean = "".join(c * 2 for c in clean)
    try:
        return int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)
    except Exception:
        return 128, 128, 128

def color_distance(hex1: str, hex2: str) -> float:
    """Calculates Euclidean RGB distance between two hex colors (max sqrt(3*255^2) ≈ 441.67)."""
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

def calculate_fingerprint_similarity(fp1: Dict[str, Any], fp2: Dict[str, Any]) -> float:
    """
    Computes a composite structural and visual similarity score between two design fingerprints.
    Scale: 0.0 (completely distinct) to 1.0 (identical clone).
    """
    # 1. Page Family Match (Weight: 15%)
    family_match = 1.0 if fp1.get("page_family") == fp2.get("page_family") else 0.0

    # 2. Hero Variant Match (Weight: 15%)
    hero_match = 1.0 if fp1.get("hero_variant") == fp2.get("hero_variant") else 0.0

    # 3. Navigation Style Match (Weight: 10%)
    nav_match = 1.0 if fp1.get("navigation_style") == fp2.get("navigation_style") else 0.0

    # 4. Product Card Anatomy Match (Weight: 15%)
    card_match = 1.0 if fp1.get("product_card_anatomy") == fp2.get("product_card_anatomy") else 0.0

    # 5. Conversion Pattern Match (Weight: 10%)
    conv_match = 1.0 if fp1.get("conversion_pattern") == fp2.get("conversion_pattern") else 0.0

    # 6. Section Order Alignment (Weight: 20%)
    s1 = fp1.get("section_order", [])
    s2 = fp2.get("section_order", [])
    set1, set2 = set(s1), set(s2)
    jaccard = len(set1 & set2) / max(len(set1 | set2), 1)
    
    min_len = min(len(s1), len(s2))
    pos_match = sum(1 for i in range(min_len) if s1[i] == s2[i]) / max(len(s1), len(s2), 1)
    section_score = (0.5 * jaccard) + (0.5 * pos_match)

    # 7. Color Palette Similarity (Weight: 15%)
    pal1 = fp1.get("color_palette", {})
    pal2 = fp2.get("color_palette", {})
    bg_dist = color_distance(pal1.get("background", "#FFFFFF"), pal2.get("background", "#000000"))
    acc_dist = color_distance(pal1.get("accent", "#C5A880"), pal2.get("accent", "#00E5FF"))
    bg_sim = max(0.0, 1.0 - (bg_dist / 441.67))
    acc_sim = max(0.0, 1.0 - (acc_dist / 441.67))
    color_sim = (0.5 * bg_sim) + (0.5 * acc_sim)

    total_similarity = (
        0.15 * family_match +
        0.15 * hero_match +
        0.10 * nav_match +
        0.15 * card_match +
        0.10 * conv_match +
        0.20 * section_score +
        0.15 * color_sim
    )

    return round(total_similarity, 4)

def check_anti_clone_diversity(
    fingerprint: Dict[str, Any],
    leads_dir: str,
    threshold: float = 0.65
) -> Dict[str, Any]:
    """
    Checks the proposed fingerprint against all other generated leads in `leads_dir`.
    Returns evaluation metrics and whether the design passes the anti-clone gate.
    """
    max_similarity = 0.0
    most_similar_lead = None
    comparisons = []

    if os.path.exists(leads_dir):
        for entry in os.listdir(leads_dir):
            if entry == fingerprint.get("lead_id"):
                continue
            cand_fp_path = os.path.join(leads_dir, entry, "solution", "design_fingerprint.json")
            if os.path.exists(cand_fp_path):
                try:
                    with open(cand_fp_path, "r", encoding="utf-8") as f:
                        cand_fp = json.load(f)
                    sim = calculate_fingerprint_similarity(fingerprint, cand_fp)
                    comparisons.append({"lead_id": entry, "similarity": sim})
                    if sim > max_similarity:
                        max_similarity = sim
                        most_similar_lead = entry
                except Exception:
                    continue

    is_clone_safe = max_similarity <= threshold

    return {
        "max_similarity_observed": max_similarity,
        "most_similar_lead": most_similar_lead,
        "is_clone_safe": is_clone_safe,
        "threshold": threshold,
        "comparisons_count": len(comparisons)
    }

# =============================================================================
# 6. Master Design Fingerprint Generator with Controlled Variation
# =============================================================================

def generate_design_fingerprint(
    lead_id: str,
    brand_name: str,
    brand_dossier: Dict[str, Any],
    social_dossier: Dict[str, Any],
    catalog_data: Optional[Dict[str, Any]] = None,
    existing_fingerprints: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generates a full executable Design Fingerprint for the lead.
    Incorporates brand signals and controlled deterministic seed variations,
    and applies anti-clone pertubations if similarity to an existing lead exceeds 65%.
    """
    seed = compute_layout_seed(lead_id)
    page_family_id = infer_page_family_from_signals(
        lead_id, brand_name, brand_dossier, social_dossier, catalog_data
    )
    family_blueprint = PAGE_FAMILIES.get(page_family_id, PAGE_FAMILIES["luxury_editorial"])

    best_candidate = None
    min_observed_similarity = 1.0

    # Up to 8 attempts systematically shifting all components
    for attempt in range(8):
        cur_seed = seed + (attempt * 1013)

        palettes = COLOR_PALETTES.get(page_family_id, COLOR_PALETTES["luxury_editorial"])
        palette_idx = (cur_seed // 7 + attempt) % len(palettes)
        palette = palettes[palette_idx]

        typo_list = TYPOGRAPHY_PAIRINGS.get(page_family_id, TYPOGRAPHY_PAIRINGS["luxury_editorial"])
        typo_idx = (cur_seed // 13 + attempt) % len(typo_list)
        typography = typo_list[typo_idx]

        nav_pool = family_blueprint["navigation_variants"]
        hero_pool = family_blueprint["hero_variants"]
        cat_pool = family_blueprint["catalog_variants"]
        card_pool = family_blueprint["card_anatomies"]
        trust_pool = family_blueprint["trust_variants"]
        conv_pool = family_blueprint["conversion_patterns"]
        sec_pool = family_blueprint["section_permutations"]

        nav_style = nav_pool[(cur_seed + attempt) % len(nav_pool)]
        hero_var = hero_pool[(cur_seed // 2 + attempt) % len(hero_pool)]
        cat_var = cat_pool[(cur_seed // 3 + attempt) % len(cat_pool)]
        card_anat = card_pool[(cur_seed // 4 + attempt) % len(card_pool)]
        trust_var = trust_pool[(cur_seed // 5 + attempt) % len(trust_pool)]
        conv_pattern = conv_pool[(cur_seed // 6 + attempt) % len(conv_pool)]
        sec_order = list(sec_pool[(cur_seed // 7 + attempt) % len(sec_pool)])

        candidate_fp = {
            "lead_id": lead_id,
            "brand_name": brand_name,
            "page_family": page_family_id,
            "layout_seed": cur_seed,
            "density": family_blueprint["density"],
            "navigation_style": nav_style,
            "hero_variant": hero_var,
            "section_order": sec_order,
            "catalog_variant": cat_var,
            "product_card_anatomy": card_anat,
            "trust_variant": trust_var,
            "conversion_pattern": conv_pattern,
            "image_treatment": family_blueprint["image_treatment"],
            "typography_pairing": typography,
            "color_palette": palette,
            "motion_signature": family_blueprint["motion_signature"],
            "brand_signals": {
                "inferred_family": page_family_id,
                "attempt_modifier": attempt
            }
        }

        if existing_fingerprints:
            max_sim = 0.0
            most_sim = None
            for ef in existing_fingerprints:
                if ef.get("lead_id") == lead_id:
                    continue
                s = calculate_fingerprint_similarity(candidate_fp, ef)
                if s > max_sim:
                    max_sim = s
                    most_sim = ef.get("lead_id")
            
            candidate_fp["diversity_metrics"] = {
                "max_similarity_observed": max_sim,
                "most_similar_lead": most_sim,
                "is_clone_safe": max_sim <= 0.65
            }

            if max_sim < min_observed_similarity:
                min_observed_similarity = max_sim
                best_candidate = candidate_fp

            if max_sim <= 0.65:
                return candidate_fp
        else:
            return candidate_fp

    return best_candidate or candidate_fp
