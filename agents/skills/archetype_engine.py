"""
Skill: E-Commerce Layout Archetype Engine
Classifies store niches into 6 distinct design archetypes, each with unique
visual identities, typography pairings, wireframes, and checkout interactions.
"""

import re

ARCHETYPES = {
    "tech_gadgets": {
        "id": "tech_gadgets",
        "name": "Tech & High-Performance Gadgets",
        "vibe": "Futuristic, sleek, mechanical HUD, high-framerate precision",
        "hero_style": "hud_split_with_video",
        "catalog_style": "technical_specs_grid",
        "checkout_style": "inline_sticky_cod",
        "trust_badge_style": "specs_hud_chips",
        "border_radius": "rounded-lg",
        "card_aspect": "aspect-video",
        "fonts": {
            "headings": "Plus Jakarta Sans, system-ui, sans-serif",
            "body": "Inter, system-ui, sans-serif",
            "mono": "ui-monospace, SFMono-Regular, Menlo, monospace"
        },
        "color_tokens": {
            "background": "#070A10",
            "surface": "#0E131F",
            "border": "#1E293B",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "accent": "#00E5FF",       # Neon Cyber Cyan
            "accent_secondary": "#10B981" # Emerald Live Pulse
        }
    },
    "fashion_streetwear": {
        "id": "fashion_streetwear",
        "name": "Streetwear, Apparel & Footwear",
        "vibe": "Bold brutalism, kinetic typography, editorial lookbook",
        "hero_style": "kinetic_marquee_split",
        "catalog_style": "lookbook_masonry",
        "checkout_style": "bottom_sheet_drawer",
        "trust_badge_style": "streetwear_pills",
        "border_radius": "rounded-none",
        "card_aspect": "aspect-[3/4]",
        "fonts": {
            "headings": "Syne, Montserrat, sans-serif",
            "body": "Space Grotesk, Inter, sans-serif",
            "mono": "Space Mono, monospace"
        },
        "color_tokens": {
            "background": "#0F0F0F",
            "surface": "#1A1A1A",
            "border": "#333333",
            "text_primary": "#FFFFFF",
            "text_secondary": "#A3A3A3",
            "accent": "#FF3366",       # Electric Coral / Neon Punch
            "accent_secondary": "#E5E5E5"
        }
    },
    "artisanal_craft": {
        "id": "artisanal_craft",
        "name": "Artisanal Terroir, Leather & Lifestyle",
        "vibe": "Organic, warm earth tones, tactile craftsmanship, human heritage",
        "hero_style": "artisan_story_hero",
        "catalog_style": "handcrafted_tiles",
        "checkout_style": "fast_modal",
        "trust_badge_style": "wax_seal_badges",
        "border_radius": "rounded-xl",
        "card_aspect": "aspect-square",
        "fonts": {
            "headings": "Playfair Display, Georgia, serif",
            "body": "Plus Jakarta Sans, sans-serif",
            "mono": "monospace"
        },
        "color_tokens": {
            "background": "#FBF8F3",   # Warm Linen
            "surface": "#FFFFFF",
            "border": "#EADBCE",
            "text_primary": "#2C221E", # Roasted Espresso
            "text_secondary": "#6B5E55",
            "accent": "#C46238",       # Terracotta Clay
            "accent_secondary": "#8B5A2B" # Moroccan Saddle Leather
        }
    },
    "beauty_cosmetics": {
        "id": "beauty_cosmetics",
        "name": "Beauty, Skincare & Organic Wellness",
        "vibe": "Soft dewy glow, clean pastel minimalism, fluid elegance",
        "hero_style": "clean_organic_hero",
        "catalog_style": "skincare_routine_grid",
        "checkout_style": "fast_modal",
        "trust_badge_style": "botanical_pills",
        "border_radius": "rounded-2xl",
        "card_aspect": "aspect-[4/5]",
        "fonts": {
            "headings": "Playfair Display, serif",
            "body": "Outfit, Inter, sans-serif",
            "mono": "monospace"
        },
        "color_tokens": {
            "background": "#FAF7F5",   # Powder Cream
            "surface": "#FFFFFF",
            "border": "#F0E4DE",
            "text_primary": "#1F1A1C", # Deep Plum Plum
            "text_secondary": "#7A6B70",
            "accent": "#D48B77",       # Warm Rose Blush
            "accent_secondary": "#8EA89D" # Sage Botanical Green
        }
    },
    "health_medical": {
        "id": "health_medical",
        "name": "Health, Medical Devices & Care",
        "vibe": "Clinical clarity, certified authority, high-contrast reassurance",
        "hero_style": "clinical_trust_hero",
        "catalog_style": "medical_clarity_grid",
        "checkout_style": "fast_modal",
        "trust_badge_style": "certified_shield_badges",
        "border_radius": "rounded-lg",
        "card_aspect": "aspect-video",
        "fonts": {
            "headings": "Inter, system-ui, sans-serif",
            "body": "Inter, system-ui, sans-serif",
            "mono": "monospace"
        },
        "color_tokens": {
            "background": "#F8FAFC",
            "surface": "#FFFFFF",
            "border": "#E2E8F0",
            "text_primary": "#0F172A",
            "text_secondary": "#475569",
            "accent": "#0284C7",       # Medical Sky Blue
            "accent_secondary": "#059669" # Verified Emerald
        }
    },
    "luxury_prestige": {
        "id": "luxury_prestige",
        "name": "Haute Horlogerie & Joaillerie",
        "vibe": "Dark titanium obsidian, 18K champagne gold luster, Swiss precision",
        "hero_style": "luxury_split_hero",
        "catalog_style": "luxury_cards",
        "checkout_style": "fast_modal",
        "trust_badge_style": "luxury_gold_crests",
        "border_radius": "rounded-xl",
        "card_aspect": "aspect-[4/5]",
        "fonts": {
            "headings": "Playfair Display, Cormorant Garamond, serif",
            "body": "Inter, system-ui, sans-serif",
            "mono": "ui-monospace, monospace"
        },
        "color_tokens": {
            "background": "#07090E",   # Obsidian Titanium
            "surface": "#0E131F",
            "border": "#1E293B",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "accent": "#D4AF37",       # Imperial 18K Gold
            "accent_secondary": "#059669" # Rolex Imperial Green
        }
    }
}

def classify_niche(niche: str, brand_name: str = "", lead_id: str = "") -> str:
    """Classifies a lead into one of 6 distinct e-commerce design archetypes."""
    text = f"{niche} {brand_name} {lead_id}".lower()
    
    # 1. Tech & Gadgets
    if any(k in text for k in ["dashcam", "auto", "high-tech", "gadget", "domotique", "connect", "serrure", "photo", "studio", "caméra", "tech", "matériel", "smart home"]):
        return "tech_gadgets"
        
    # 2. Luxury Horlogerie & Joaillerie
    if any(k in text for k in ["montre", "horloger", "joaillerie", "bijou", "or 18k", "argent 925", "solitaire", "diamant", "prestige", "luxe", "clakovs", "anulus", "mamontre", "viba", "aurea"]):
        return "luxury_prestige"
        
    # 3. Artisanal & Terroir
    if any(k in text for k in ["céramique", "artisan", "cuir", "maroquinerie", "fès", "marrakech", "chabi", "terroir", "café", "torréfié", "tableau", "art de vivre", "feskin", "bleather", "darna", "massinart"]):
        return "artisanal_craft"
        
    # 4. Beauty & Cosmetics
    if any(k in text for k in ["cosmétique", "skincare", "cheveux", "argan", "bio", "beauté", "soin", "parfum", "fragrance", "fenna", "beauty"]):
        return "beauty_cosmetics"
        
    # 5. Health & Medical
    if any(k in text for k in ["santé", "médical", "diabète", "capteur", "orthopédique", "médicaux"]):
        return "health_medical"
        
    # 6. Fashion & Streetwear (Shoes, abayas, clothing, modest fashion)
    if any(k in text for k in ["streetwear", "fashion", "chaussure", "soulier", "basket", "sneaker", "vêtement", "prêt-à-porter", "lingerie", "pyjama", "abaya", "voile", "modest", "caftan", "sac", "dynasty", "flex", "arwa", "skyeveil"]):
        return "fashion_streetwear"
        
    # Default fallback based on high-conversion Moroccan e-commerce standard
    return "fashion_streetwear"

def get_archetype_spec(archetype_id: str) -> dict:
    """Retrieves the full UI & UX design tokens for a given archetype."""
    return ARCHETYPES.get(archetype_id, ARCHETYPES["fashion_streetwear"])
