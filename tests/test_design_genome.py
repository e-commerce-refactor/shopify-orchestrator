import os
import json
import tempfile
import unittest

from agents.skills.design_genome import (
    PAGE_FAMILIES,
    generate_design_fingerprint,
    calculate_fingerprint_similarity,
    check_anti_clone_diversity,
    infer_page_family_from_signals
)
from orchestrator import validate_against_schema
from agents.agent_solution import run_solution
from agents.agent_builder import run_build
from agents.agent_qa import run_qa


class DesignGenomeAndAntiCloneTests(unittest.TestCase):
    def test_page_families_have_distinct_section_orders_and_components(self):
        # 1. Technical Commerce vs Luxury Editorial
        tech = PAGE_FAMILIES["technical_commerce"]
        lux = PAGE_FAMILIES["luxury_editorial"]
        chrono = PAGE_FAMILIES["luxury_horlogerie"]

        self.assertNotEqual(tech["density"], lux["density"])
        self.assertNotEqual(tech["navigation_variants"][0], lux["navigation_variants"][0])
        self.assertNotEqual(tech["hero_variants"][0], lux["hero_variants"][0])
        self.assertNotEqual(tech["card_anatomies"][0], lux["card_anatomies"][0])
        self.assertNotEqual(tech["conversion_patterns"][0], lux["conversion_patterns"][0])

        # Technical Commerce should have specs strip and comparison matrix
        tech_sections = tech["section_permutations"][0]
        self.assertIn("specs_strip", tech_sections)
        self.assertIn("comparison_matrix", tech_sections)

        # Luxury Editorial should have craftsmanship seal
        lux_sections = lux["section_permutations"][0]
        self.assertIn("craftsmanship_seal", lux_sections)
        self.assertNotIn("comparison_matrix", lux_sections)

        # Horlogerie should have chronometer telemetry
        chrono_sections = chrono["section_permutations"][0]
        self.assertIn("chronometer_telemetry", chrono_sections)

    def test_brand_signals_classify_families_accurately(self):
        f_70mai = infer_page_family_from_signals(
            "70mai_Maroc", "70mai Maroc",
            {"niche": "dashcam camera tech automobile"}, {}
        )
        self.assertEqual(f_70mai, "technical_commerce")

        f_anulus = infer_page_family_from_signals(
            "Anulus_Joaillerie", "Anulus Joaillerie",
            {"niche": "haute joaillerie or 18k diamants", "archetype": "luxury_joaillerie"}, {}
        )
        self.assertEqual(f_anulus, "luxury_editorial")

        f_montre = infer_page_family_from_signals(
            "Ma_Montre_Maroc", "Ma Montre Maroc",
            {"niche": "montres horlogerie chronometres", "archetype": "luxury_horlogerie"}, {}
        )
        self.assertEqual(f_montre, "luxury_horlogerie")

        f_cuir = infer_page_family_from_signals(
            "Bleather_Maroc", "Bleather Maroc",
            {"niche": "cuir maroquinerie fait main artisanat"}, {}
        )
        self.assertEqual(f_cuir, "artisan_story")

        f_skincare = infer_page_family_from_signals(
            "Beauty_Market", "Beauty Market",
            {"niche": "cosmetique beaute soins skincare argan"}, {}
        )
        self.assertEqual(f_skincare, "beauty_routine")

    def test_similarity_metric_contrasts_technical_and_luxury(self):
        fp_tech = generate_design_fingerprint(
            "70mai_Maroc", "70mai Maroc",
            {"niche": "dashcam tech"}, {}
        )
        fp_lux = generate_design_fingerprint(
            "Anulus_Joaillerie", "Anulus Joaillerie",
            {"niche": "joaillerie or", "archetype": "luxury_joaillerie"}, {}
        )
        similarity = calculate_fingerprint_similarity(fp_tech, fp_lux)
        self.assertLess(similarity, 0.35, f"Expected < 35% similarity between tech and luxury, got {similarity}")

    def test_controlled_seed_variation_ensures_intra_archetype_diversity(self):
        # Two brands in the exact same luxury jewelry archetype
        fp1 = generate_design_fingerprint(
            "Anulus_Joaillerie", "Anulus Joaillerie",
            {"niche": "joaillerie or 18k", "archetype": "luxury_joaillerie"}, {}
        )
        fp2 = generate_design_fingerprint(
            "Lamoura_Bijoux", "Lamoura Bijoux",
            {"niche": "joaillerie or 18k", "archetype": "luxury_joaillerie"}, {},
            existing_fingerprints=[fp1]
        )

        similarity = calculate_fingerprint_similarity(fp1, fp2)
        self.assertLessEqual(similarity, 0.65, f"Expected intra-archetype similarity <= 65%, got {similarity}")
        self.assertTrue(fp2.get("diversity_metrics", {}).get("is_clone_safe", False))

    def test_design_fingerprint_schema_conformance(self):
        for lid, niche in [("70mai_Maroc", "dashcam"), ("Anulus_Joaillerie", "joaillerie"), ("Ma_Montre_Maroc", "montres")]:
            fp = generate_design_fingerprint(lid, lid, {"niche": niche}, {})
            # Must not raise
            validate_against_schema(fp, "design_fingerprint.schema.json")

    def test_solution_agent_generates_design_fingerprint(self):
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as workspace:
            disc_dir = os.path.join(workspace, "discovery")
            os.makedirs(disc_dir, exist_ok=True)
            with open(os.path.join(disc_dir, "brand_dossier.json"), "w", encoding="utf-8") as f:
                json.dump({"niche": "dashcam tech 4k", "archetype": "tech_gadgets"}, f)
            with open(os.path.join(disc_dir, "social_dossier.json"), "w", encoding="utf-8") as f:
                json.dump({"instagram_handle": "@techstore", "follower_count": "50k"}, f)

            handoff = run_solution("Tech_Store", workspace, "Tech Store")
            self.assertEqual(handoff["status"], "passed")

            fp_path = os.path.join(workspace, "solution", "design_fingerprint.json")
            self.assertTrue(os.path.exists(fp_path))

            with open(fp_path, "r", encoding="utf-8") as f:
                fp = json.load(f)
            self.assertEqual(fp["page_family"], "technical_commerce")
            self.assertIn("comparison_matrix", fp["section_order"])

    def test_builder_assembles_dynamic_page_from_fingerprint(self):
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as workspace:
            sol_dir = os.path.join(workspace, "solution")
            disc_dir = os.path.join(workspace, "discovery")
            os.makedirs(sol_dir, exist_ok=True)
            os.makedirs(disc_dir, exist_ok=True)

            with open(os.path.join(disc_dir, "brand_dossier.json"), "w", encoding="utf-8") as f:
                json.dump({"niche": "dashcam tech 4k", "archetype": "tech_gadgets"}, f)

            # Generate solution
            run_solution("Tech_Store", workspace, "Tech Store")

            # Generate build
            build_handoff = run_build("Tech_Store", workspace, "Tech Store")
            self.assertEqual(build_handoff["status"], "passed")

            page_file = os.path.join(workspace, "demo", "source", "app", "page.tsx")
            self.assertTrue(os.path.exists(page_file))

            with open(page_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Technical commerce page must include ComparisonTable and Hero
            self.assertIn("<ComparisonTable />", content)
            self.assertIn("<Hero />", content)
            self.assertIn("<Header />", content)


if __name__ == "__main__":
    unittest.main()
