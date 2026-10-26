"""
Skill: Motion & CSS Physics Engine
Generates tailored, GPU-accelerated CSS keyframe definitions, timing curves,
and micro-interaction specs for Next.js 14 & Tailwind storefronts.
Zero JavaScript bundle overhead, 60fps native performance.
"""

MOTION_PROFILES = {
    "tech_gadgets": {
        "archetype": "tech_gadgets",
        "signature_effect": "laser_scan_and_radar_pulse",
        "timing_curve": "cubic-bezier(0.16, 1, 0.3, 1)", # Cyber Snap
        "hero_entrance": "slide_down_fade",
        "card_hover": "glow_cyan_and_scale",
        "checkout_transition": "instant_slide_in",
        "tailwind_keyframes": """
        laser_scan: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '50%': { opacity: '0.8' },
          '100%': { transform: 'translateY(220%)', opacity: '0' },
        },
        radar_pulse: {
          '0%': { transform: 'scale(0.95)', boxShadow: '0 0 0 0 rgba(0, 229, 255, 0.7)' },
          '70%': { transform: 'scale(1)', boxShadow: '0 0 0 10px rgba(0, 229, 255, 0)' },
          '100%': { transform: 'scale(0.95)', boxShadow: '0 0 0 0 rgba(0, 229, 255, 0)' },
        },
        hud_glow: {
          '0%, 100%': { opacity: '0.8', filter: 'drop-shadow(0 0 8px rgba(0,229,255,0.4))' },
          '50%': { opacity: '1', filter: 'drop-shadow(0 0 16px rgba(0,229,255,0.8))' },
        }
        """,
        "tailwind_animations": """
        'laser-scan': 'laser_scan 3s cubic-bezier(0.16, 1, 0.3, 1) infinite',
        'radar-pulse': 'radar_pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'hud-glow': 'hud_glow 4s ease-in-out infinite',
        """
    },
    "fashion_streetwear": {
        "archetype": "fashion_streetwear",
        "signature_effect": "infinite_marquee_and_brutalist_pop",
        "timing_curve": "cubic-bezier(0.2, 0, 0, 1)", # Brutalist Snappy
        "hero_entrance": "staggered_fade_up",
        "card_hover": "offset_hard_shadow_shift",
        "checkout_transition": "bottom_drawer_spring",
        "tailwind_keyframes": """
        marquee: {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        badge_pop: {
          '0%': { transform: 'scale(0.9) rotate(-2deg)' },
          '50%': { transform: 'scale(1.05) rotate(1deg)' },
          '100%': { transform: 'scale(1) rotate(0deg)' },
        }
        """,
        "tailwind_animations": """
        'marquee-fast': 'marquee 14s linear infinite',
        'marquee-slow': 'marquee 28s linear infinite',
        'badge-pop': 'badge_pop 0.4s cubic-bezier(0.2, 0, 0, 1)',
        """
    },
    "artisanal_craft": {
        "archetype": "artisanal_craft",
        "signature_effect": "artisanal_stamp_and_warm_bloom",
        "timing_curve": "cubic-bezier(0.34, 1.56, 0.64, 1)", # Tactile Stamp
        "hero_entrance": "slow_organic_reveal",
        "card_hover": "warm_terracotta_lift",
        "checkout_transition": "gentle_modal_scale",
        "tailwind_keyframes": """
        stamp_imprint: {
          '0%': { transform: 'scale(1.3) rotate(-8deg)', opacity: '0' },
          '70%': { transform: 'scale(0.95) rotate(2deg)', opacity: '1' },
          '100%': { transform: 'scale(1) rotate(-1deg)', opacity: '1' },
        },
        warm_breathe: {
          '0%, 100%': { filter: 'drop-shadow(0 4px 12px rgba(196,98,56,0.15))' },
          '50%': { filter: 'drop-shadow(0 8px 24px rgba(196,98,56,0.30))' },
        }
        """,
        "tailwind_animations": """
        'stamp-imprint': 'stamp_imprint 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
        'warm-breathe': 'warm_breathe 4s ease-in-out infinite',
        """
    },
    "beauty_cosmetics": {
        "archetype": "beauty_cosmetics",
        "signature_effect": "dewy_ripple_and_rose_sheen",
        "timing_curve": "cubic-bezier(0.25, 1, 0.5, 1)", # Soft Dew
        "hero_entrance": "soft_gradient_float",
        "card_hover": "dewy_glow_lift",
        "checkout_transition": "smooth_pill_unfold",
        "tailwind_keyframes": """
        rose_sheen: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
        fluid_float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        }
        """,
        "tailwind_animations": """
        'rose-sheen': 'rose_sheen 6s ease-in-out infinite',
        'fluid-float': 'fluid_float 5s ease-in-out infinite',
        """
    },
    "health_medical": {
        "archetype": "health_medical",
        "signature_effect": "clinical_heartbeat_and_shield_pop",
        "timing_curve": "cubic-bezier(0.4, 0, 0.2, 1)", # Calm Reassurance
        "hero_entrance": "clean_fade_down",
        "card_hover": "crisp_border_glow",
        "checkout_transition": "direct_fade_scale",
        "tailwind_keyframes": """
        heartbeat_pulse: {
          '0%, 100%': { transform: 'scale(1)' },
          '14%': { transform: 'scale(1.08)' },
          '28%': { transform: 'scale(1)' },
          '42%': { transform: 'scale(1.04)' },
          '70%': { transform: 'scale(1)' },
        }
        """,
        "tailwind_animations": """
        'heartbeat': 'heartbeat_pulse 3s ease-in-out infinite',
        """
    },
    "luxury_prestige": {
        "archetype": "luxury_prestige",
        "signature_effect": "horlogerie_gear_sweep_and_gold_shimmer",
        "timing_curve": "cubic-bezier(0.25, 1, 0.5, 1)", # Swiss Prestige
        "hero_entrance": "slow_curtain_reveal",
        "card_hover": "gold_3d_tilt",
        "checkout_transition": "velvet_fade_up",
        "tailwind_keyframes": """
        gold_shimmer: {
          '0%': { transform: 'translateX(-100%) rotate(45deg)' },
          '100%': { transform: 'translateX(200%) rotate(45deg)' },
        },
        tourbillon: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        }
        """,
        "tailwind_animations": """
        'gold-shimmer': 'gold_shimmer 4s ease-in-out infinite',
        'tourbillon-slow': 'tourbillon 20s linear infinite',
        """
    }
}

def get_motion_profile(archetype_id: str) -> dict:
    """Returns the motion profile and CSS keyframes for the given archetype."""
    return MOTION_PROFILES.get(archetype_id, MOTION_PROFILES["fashion_streetwear"])
