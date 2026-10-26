"""
Specialized skills package for the Global Shopify Modernization Orchestrator.
Provides modular intelligence for social OSINT, headless catalog extraction,
niche-based design archetypes, and GPU-accelerated motion profiles.
"""

from .archetype_engine import classify_niche, get_archetype_spec
from .motion_profiles import get_motion_profile
from .social_extractor import extract_social_intelligence
from .shopify_catalog import harvest_shopify_catalog

__all__ = [
    "classify_niche",
    "get_archetype_spec",
    "get_motion_profile",
    "extract_social_intelligence",
    "harvest_shopify_catalog"
]
