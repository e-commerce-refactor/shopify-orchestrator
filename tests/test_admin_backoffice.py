"""Unit tests for the Admin Backoffice Skill & Integration."""

import unittest
from agents.skills.admin_backoffice import (
    generate_admin_types,
    generate_admin_auth,
    generate_admin_layout,
    generate_admin_login,
    generate_admin_dashboard,
    generate_admin_products,
    generate_admin_reviews,
    generate_admin_settings,
    generate_admin_sql_migration,
)


class TestAdminBackoffice(unittest.TestCase):
    def setUp(self):
        self.brand = "Anulus Joaillerie"
        self.lead_id = "Anulus_Joaillerie"
        self.slug = "anulus-joaillerie-v2"

    def test_types_generation(self):
        code = generate_admin_types()
        self.assertIn("export interface Order", code)
        self.assertIn("export interface Product", code)
        self.assertIn("export interface Review", code)
        self.assertIn("export interface StoreSettings", code)
        self.assertIn("export interface AdminUser", code)

    def test_auth_helper_generation(self):
        code = generate_admin_auth()
        self.assertIn("export async function adminLogin", code)
        self.assertIn("export function getAdminSession", code)
        self.assertIn("export async function adminLogout", code)
        self.assertIn("admin_users", code)
        self.assertIn("cleanId.includes('@')", code)
        self.assertIn("Admin123456!", code)

    def test_layout_generation(self):
        code = generate_admin_layout(self.brand, self.lead_id)
        self.assertIn("'use client';", code)
        self.assertIn("Tableau de bord", code)
        self.assertIn("Gestion Produits", code)
        self.assertIn("Avis Clients", code)
        self.assertIn("Paramètres", code)
        self.assertIn("Anulus Joaillerie", code)
        self.assertIn("/admin/login", code)
        self.assertIn("handleLogout", code)

    def test_login_generation(self):
        code = generate_admin_login(self.brand, self.lead_id)
        self.assertIn("'use client';", code)
        self.assertIn("Email ou Nom d'utilisateur", code)
        self.assertIn("Mot de passe", code)
        self.assertIn("adminLogin", code)
        self.assertIn("Admin123456!", code)

    def test_dashboard_generation(self):
        code = generate_admin_dashboard(self.brand, self.lead_id)
        self.assertIn("'use client';", code)
        self.assertIn("Chiffre d'Affaires COD", code)
        self.assertIn("Total Commandes", code)
        self.assertIn("À Confirmer", code)
        self.assertIn("Confirmées / Livrées", code)
        self.assertIn("openWhatsAppConfirmation", code)
        self.assertIn("handleStatusChange", code)
        self.assertIn("wa.me", code)

    def test_products_generation(self):
        code = generate_admin_products(self.brand, self.lead_id)
        self.assertIn("'use client';", code)
        self.assertIn("Gestion des Produits", code)
        self.assertIn("handleToggleStock", code)
        self.assertIn("handleSaveProduct", code)
        self.assertIn("handleDeleteProduct", code)
        self.assertIn("En Stock", code)
        self.assertIn("Rupture", code)

    def test_reviews_generation(self):
        code = generate_admin_reviews(self.brand, self.lead_id)
        self.assertIn("'use client';", code)
        self.assertIn("Modération des Avis", code)
        self.assertIn("handleUpdateStatus", code)
        self.assertIn("handleDeleteReview", code)
        self.assertIn("handleAddReview", code)
        self.assertIn("Acheteur Vérifié", code)

    def test_settings_generation(self):
        code = generate_admin_settings(self.brand, self.lead_id, "+212611223344", "contact@anulus.ma")
        self.assertIn("'use client';", code)
        self.assertIn("Paramètres de la Boutique", code)
        self.assertIn("Numéro WhatsApp Business", code)
        self.assertIn("Frais de port standard", code)
        self.assertIn("Seuil livraison gratuite", code)
        self.assertIn("Ruban d'Annonce Storefront", code)

    def test_sql_migration_generation(self):
        sql = generate_admin_sql_migration(self.brand, self.lead_id, self.slug)
        self.assertIn("CREATE TABLE IF NOT EXISTS public.orders", sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS public.products", sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS public.reviews", sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS public.store_settings", sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS public.admin_users", sql)
        self.assertIn("ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY", sql)
        self.assertIn("Allow public order placement", sql)
        self.assertIn("Allow authenticated order management", sql)
        self.assertIn("DROP POLICY \"Allow anon read orders\"", sql)
        self.assertIn("INSERT INTO public.admin_users", sql)


if __name__ == "__main__":
    unittest.main()
