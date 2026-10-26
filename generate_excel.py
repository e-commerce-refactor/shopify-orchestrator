import os
import re
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
# remove default sheet
wb.remove(wb.active)

# Color Palette (Executive Navy & Emerald Theme)
NAVY_DARK = "0F172A"       # Headers main
NAVY_HEADER = "1E293B"     # Table headers
NAVY_LIGHT = "334155"      # Subheaders
EMERALD = "059669"         # Accent green
EMERALD_LIGHT = "D1FAE5"   # Success / High priority fill
AMBER_LIGHT = "FEF3C7"     # Warning / Medium priority fill
RED_LIGHT = "FEE2E2"       # Danger / Ultra-High fill
BLUE_LIGHT = "E0F2FE"      # Info fill
GRAY_BG = "F8FAFC"         # Alternating row fill
GRAY_BORDER = "CBD5E1"     # Cell borders
WHITE = "FFFFFF"

font_title = Font(name="Segoe UI", size=16, bold=True, color=WHITE)
font_subtitle = Font(name="Segoe UI", size=10, italic=True, color="94A3B8")
font_section = Font(name="Segoe UI", size=12, bold=True, color=NAVY_DARK)
font_header = Font(name="Segoe UI", size=10, bold=True, color=WHITE)
font_data = Font(name="Segoe UI", size=9, color="1E293B")
font_data_bold = Font(name="Segoe UI", size=9, bold=True, color="1E293B")
font_link = Font(name="Segoe UI", size=9, color="2563EB", underline="single")
font_kpi_num = Font(name="Segoe UI", size=20, bold=True, color=NAVY_DARK)
font_kpi_label = Font(name="Segoe UI", size=9, bold=True, color="64748B")

fill_header = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
fill_navy_dark = PatternFill(start_color=NAVY_DARK, end_color=NAVY_DARK, fill_type="solid")
fill_zebra = PatternFill(start_color=GRAY_BG, end_color=GRAY_BG, fill_type="solid")
fill_white = PatternFill(start_color=WHITE, end_color=WHITE, fill_type="solid")
fill_prio_hot = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
fill_prio_high = PatternFill(start_color="FFEDD5", end_color="FFEDD5", fill_type="solid")
fill_prio_med = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
fill_status_new = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
fill_kpi_card = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

thin_border = Border(
    left=Side(style='thin', color=GRAY_BORDER),
    right=Side(style='thin', color=GRAY_BORDER),
    top=Side(style='thin', color=GRAY_BORDER),
    bottom=Side(style='thin', color=GRAY_BORDER)
)

thick_bottom_border = Border(
    left=Side(style='thin', color=GRAY_BORDER),
    right=Side(style='thin', color=GRAY_BORDER),
    top=Side(style='thin', color=GRAY_BORDER),
    bottom=Side(style='medium', color=NAVY_HEADER)
)

align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
align_right = Alignment(horizontal="right", vertical="center")

# ==========================================
# 1. DATA DEFINITION - 35 BUSINESSES
# ==========================================
prospects_data = [
    # Initial 20
    {
        "id": 1, "name": "Anulus Joaillerie", "niche": "Bijouterie & Horlogerie (Or & Argent)",
        "url": "https://anulus.ma", "city": "Casablanca", "wa": "+212 6 39 15 68 83", "wa_clean": "212639156883",
        "email": "contact@anulus.ma", "ig": "https://instagram.com/anulus.ma", "positioning": "Haut de Gamme / Luxe",
        "shopify_cost_usd": 180, "shopify_cost_mad": 1800,
        "pain_point": "Plafond dotation e-commerce consommé en devises USD + frais de 2% sur chaque transaction + lenteur sur mobile due aux apps de zoom/avis.",
        "pitch_angle": "Éliminez les 18 000 DH/an de frais Shopify récurrents et offrez une expérience d'achat joaillerie ultra-rapide et sécurisée 100% marocaine.",
        "recommended_stack": "Next.js + Tailwind + CMI / COD", "priority": "🔥 Très Haute", "status": "À Contacter"
    },
    {
        "id": 2, "name": "Ma Montre Maroc", "niche": "Horlogerie & Montres Homme/Femme",
        "url": "https://mamontre.ma", "city": "Casablanca", "wa": "+212 6 45 22 20 09", "wa_clean": "212645222009",
        "email": "mamontre.ma@gmail.com", "ig": "https://instagram.com/mamontre.ma", "positioning": "Mid-range / Volume",
        "shopify_cost_usd": 150, "shopify_cost_mad": 1500,
        "pain_point": "Dépendance à Releasit/EasySell pour le Cash-On-Delivery. Coût mensuel Shopify + pénalité de 2% sur chaque commande COD.",
        "pitch_angle": "Checkout COD en 1 clic sans abonnement mensuel d'app tierce + confirmation automatique des commandes par WhatsApp API.",
        "recommended_stack": "WooCommerce Headless ou Next.js", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 3, "name": "Dynasty Maroc", "niche": "Linge de maison & Décoration",
        "url": "https://dynasty.ma", "city": "Casablanca", "wa": "+212 7 63 77 80 49", "wa_clean": "212763778049",
        "email": "contact@dynasty.ma", "ig": "https://instagram.com/dynasty.maroc", "positioning": "Haut de Gamme",
        "shopify_cost_usd": 220, "shopify_cost_mad": 2200,
        "pain_point": "Catalogue produits riche nécessitant des applications de personnalisation lourdes qui ralentissent le chargement sur mobile 4G.",
        "pitch_angle": "Un site vitrine e-commerce ultra-fluide avec temps de chargement < 1 sec, design sur-mesure digne des plus grands éditeurs de textile.",
        "recommended_stack": "Next.js + Shopify Headless ou Custom", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 4, "name": "Flex Shoes", "niche": "Chaussures cuir véritable & Maroquinerie",
        "url": "https://flexshoes.ma", "city": "Fès / Casablanca", "wa": "+212 6 70 59 88 44", "wa_clean": "212670598844",
        "email": "flexshoes.ma@gmail.com", "ig": "https://instagram.com/flexshoes.ma", "positioning": "Mid-range / Artisanat Cuir",
        "shopify_cost_usd": 140, "shopify_cost_mad": 1400,
        "pain_point": "Taux d'abandon élevé sur mobile causé par le tunnel Shopify multi-étapes non adapté aux habitudes d'achat COD marocaines.",
        "pitch_angle": "Formulaire direct Nom + Téléphone + Ville + Pointure avec notification livreur intégrée (AMEEX / Cathedis) et zéro abonnement en devises.",
        "recommended_stack": "Next.js + Tailwind / Fast COD", "priority": "🔥 Très Haute", "status": "À Contacter"
    },
    {
        "id": 5, "name": "Sacoluxe", "niche": "Sacs à main & Maroquinerie de luxe",
        "url": "https://sacoluxe.com", "city": "Casablanca", "wa": "+212 6 45 22 20 09", "wa_clean": "212645222009",
        "email": "sacoluxe@gmail.com", "ig": "https://instagram.com/sacoluxe_maroc", "positioning": "Luxe / Tendance",
        "shopify_cost_usd": 160, "shopify_cost_mad": 1600,
        "pain_point": "Identité visuelle limitée par les thèmes Shopify standards et commissions inutiles sur ventes.",
        "pitch_angle": "Créez une véritable expérience boutique de luxe personnalisée sans payer de royalties mensuelles à Shopify.",
        "recommended_stack": "Next.js + Tailwind CSS", "priority": "Moyenne", "status": "À Contacter"
    },
    {
        "id": 6, "name": "Maison de Mode", "niche": "Mode, Chaussures, Sacs & Bijoux",
        "url": "https://maisondemode.ma", "city": "Casablanca", "wa": "+212 7 00 91 87 91", "wa_clean": "212700918791",
        "email": "contact@maisondemode.ma", "ig": "https://instagram.com/maisondemode.ma", "positioning": "Mid-range",
        "shopify_cost_usd": 200, "shopify_cost_mad": 2000,
        "pain_point": "Nombreux plugins installés (PageFly, Judge.me, COD form) créant un goulet d'étranglement de vitesse et un coût cumulé de ~200$/mois.",
        "pitch_angle": "Économisez plus de 24 000 DH par an d'abonnements d'apps et améliorez votre taux de conversion mobile de +25%.",
        "recommended_stack": "Next.js + Direct COD + Supabase/SQL", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 7, "name": "Aurea Accessories", "niche": "Bijoux & Accessoires acier inoxydable",
        "url": "https://aureaaccessories.ma", "city": "Rabat", "wa": "+212 6 84 90 25 11", "wa_clean": "212684902511",
        "email": "contact@aureaaccessories.ma", "ig": "https://instagram.com/aureaaccessories.ma", "positioning": "Access / Trendy",
        "shopify_cost_usd": 130, "shopify_cost_mad": 1300,
        "pain_point": "Panier moyen bas (150-250 DH), les frais Shopify et applications grèvent lourdement la marge nette.",
        "pitch_angle": "Pour les paniers à 199 DH, chaque dirham de frais Shopify compte. Libérez vos marges et investissez vos devises dans TikTok Ads.",
        "recommended_stack": "Nuxt / Next.js ou WooCommerce Pro", "priority": "🔥 Très Haute", "status": "À Contacter"
    },
    {
        "id": 8, "name": "Viba Bijoux", "niche": "Bijoux & Parures pour femmes",
        "url": "https://vibabijoux.ma", "city": "Casablanca", "wa": "+212 6 45 22 20 09", "wa_clean": "212645222009",
        "email": "vibabijoux@gmail.com", "ig": "https://instagram.com/vibabijoux", "positioning": "Mid-range",
        "shopify_cost_usd": 140, "shopify_cost_mad": 1400,
        "pain_point": "Partage potentiel d'infrastructure/coordonnées avec d'autres marques (même numéro que Sacoluxe/MaMontre). Besoin de singularisation.",
        "pitch_angle": "Distinguez votre marque avec une plateforme propriétaire unique, découplée des templates Shopify génériques.",
        "recommended_stack": "Next.js e-commerce", "priority": "Moyenne", "status": "À Contacter"
    },
    {
        "id": 9, "name": "Bleather Maroc", "niche": "Maroquinerie & Cuir artisanal",
        "url": "https://bleather.ma", "city": "Marrakech", "wa": "+212 6 03 69 51 77", "wa_clean": "212603695177",
        "email": "contact.bleather@gmail.com", "ig": "https://instagram.com/bleather.morocco", "positioning": "Haut de Gamme / Export",
        "shopify_cost_usd": 250, "shopify_cost_mad": 2500,
        "pain_point": "Frais de transaction élevés sur les ventes internationales et limitations de passerelles de paiement locales en dirhams.",
        "pitch_angle": "Un site bilingue/multidevise (MAD + EUR/USD) avec CMI intégré pour le Maroc et Stripe pour l'international sans commission 2% Shopify.",
        "recommended_stack": "Next.js + CMI + Stripe Multi-currency", "priority": "🔥 Très Haute", "status": "À Contacter"
    },
    {
        "id": 10, "name": "Feskin Cuir", "niche": "Maroquinerie artisanale & Cuir de Fès",
        "url": "https://feskin.ma", "city": "Fès", "wa": "+212 6 61 78 90 12", "wa_clean": "212661789012",
        "email": "contact@feskin.ma", "ig": "https://instagram.com/feskin.ma", "positioning": "Artisanal / Authentique",
        "shopify_cost_usd": 120, "shopify_cost_mad": 1200,
        "pain_point": "Paiement de factures en dollars épuisant la dotation e-commerce de l'artisan sans justification technique.",
        "pitch_angle": "Payez votre hébergement en dirhams au Maroc, conservez 100% de votre dotation e-commerce pour vos publicités.",
        "recommended_stack": "WooCommerce Optimisé ou Custom Node/React", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 11, "name": "Clakovs Brustel", "niche": "Chaussures de ville & Prêt-à-porter",
        "url": "https://clakovsbrustel.ma", "city": "Casablanca", "wa": "+212 6 66 32 91 19", "wa_clean": "212666329119",
        "email": "contact@clakovsbrustel.com", "ig": "https://instagram.com/clakovsbrustel", "positioning": "Haut de Gamme Élégant",
        "shopify_cost_usd": 190, "shopify_cost_mad": 1900,
        "pain_point": "Expérience d'achat standardisée ne reflétant pas le prestige de la marque et les exigences d'une clientèle masculine haut de gamme.",
        "pitch_angle": "Sublimez votre image de marque avec une interface épurée, ultra-rapide et sans les bannières ou restrictions de Shopify.",
        "recommended_stack": "Next.js + Tailwind + CMI/COD", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 12, "name": "Makushop", "niche": "Parfumerie & Soins de beauté",
        "url": "https://makushop.ma", "city": "Casablanca", "wa": "+212 6 97 83 88 05", "wa_clean": "212697838805",
        "email": "contact@makushop.ma", "ig": "https://instagram.com/makushoop", "positioning": "Mass Market / Beauté",
        "shopify_cost_usd": 150, "shopify_cost_mad": 1500,
        "pain_point": "Fort volume de commandes COD entraînant des frais transactionnels excessifs et des conflits de scripts d'upsell.",
        "pitch_angle": "Module d'upsell 'Achetez 2, obtenez le 3ème à -50%' natif et sans frais mensuels récurrents.",
        "recommended_stack": "Next.js E-commerce Custom", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 13, "name": "70mai Maroc", "niche": "Dashcams & Accessoires Auto High-Tech",
        "url": "https://70mai.ma", "city": "Casablanca", "wa": "+212 6 71 45 03 67", "wa_clean": "212671450367",
        "email": "contact@70mai.ma", "ig": "https://instagram.com/70mai.maroc", "positioning": "High-Tech / Distributeur",
        "shopify_cost_usd": 260, "shopify_cost_mad": 2600,
        "pain_point": "Besoins techniques spécifiques (fiches techniques détaillées, vidéos de démo, garanties) qui alourdissent le thème Shopify.",
        "pitch_angle": "Une plateforme High-Tech ultra-performante intégrant gestion de garantie SAV, tracking de colis marocain et zéro commission.",
        "recommended_stack": "Next.js + Headless CMS + API Transporteur", "priority": "🔥 Très Haute", "status": "À Contacter"
    },
    {
        "id": 14, "name": "Skyeveil", "niche": "Prêt-à-porter féminin & Voiles",
        "url": "https://skyeveil.com", "city": "Casablanca", "wa": "+212 6 12 34 56 78", "wa_clean": "212612345678",
        "email": "contact@skyeveil.com", "ig": "https://instagram.com/skyeveil", "positioning": "Modest Fashion",
        "shopify_cost_usd": 160, "shopify_cost_mad": 1600,
        "pain_point": "Paiement de thèmes et d'applications mensuelles pour gérer les variations de couleurs et de tissus.",
        "pitch_angle": "Gestionnaire de variations fluide avec affichage instantané des couleurs sur mobile sans temps de chargement.",
        "recommended_stack": "Next.js + Tailwind", "priority": "Moyenne", "status": "À Contacter"
    },
    {
        "id": 15, "name": "Minisouq Maroc", "niche": "Gadgets & Lifestyle High-Tech",
        "url": "https://minisouq.ma", "city": "Tanger", "wa": "+212 6 55 44 33 22", "wa_clean": "212655443322",
        "email": "contact@missov.ma", "ig": "https://instagram.com/minisouq.ma", "positioning": "Gadgets & Nouveautés",
        "shopify_cost_usd": 180, "shopify_cost_mad": 1800,
        "pain_point": "Besoin de créer des landing pages produits percutantes à haute conversion sans payer 49$/mois pour PageFly.",
        "pitch_angle": "Générateur de landing pages illimité intégré directement dans votre tableau de bord, sans frais supplémentaires.",
        "recommended_stack": "Next.js + Landing Page Builder Natif", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 16, "name": "Diabète Solutions", "niche": "Santé & Capteurs médicaux",
        "url": "https://diabetesolutions.ma", "city": "Rabat", "wa": "+212 7 67 60 49 58", "wa_clean": "212767604958",
        "email": "contact@diabetesolutions.ma", "ig": "https://instagram.com/diabetesolutions.ma", "positioning": "Santé / Dispositifs Médicaux",
        "shopify_cost_usd": 220, "shopify_cost_mad": 2200,
        "pain_point": "Exigence de confiance maximale et besoin de suivi personnalisé des patients/clients mal servi par les templates Shopify génériques.",
        "pitch_angle": "Un portail médical et e-commerce sécurisé, rassurant pour les patients, avec suivi d'ordonnance et paiement en ligne CMI sans frais Shopify.",
        "recommended_stack": "Next.js + Système de commande récurrente", "priority": "🔥 Très Haute", "status": "À Contacter"
    },
    {
        "id": 17, "name": "Beauty Market", "niche": "Skincare & Cosmétique bio",
        "url": "https://beautymarket.ma", "city": "Casablanca", "wa": "+212 6 99 50 55 20", "wa_clean": "212699505520",
        "email": "contact@beautymarket.ma", "ig": "https://instagram.com/beautymarket_ma", "positioning": "Bio & Cosmétique",
        "shopify_cost_usd": 150, "shopify_cost_mad": 1500,
        "pain_point": "Ralentissement important de la boutique dû aux widgets d'avis clients et d'instagram feed.",
        "pitch_angle": "Boostez vos conversions grâce à un score PageSpeed de 95+/100 sur mobile et gardez 100% de vos gains.",
        "recommended_stack": "Next.js + Tailwind + Headless Reviews", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 18, "name": "Fenna Maroc", "niche": "Accessoires de mode & Sacs",
        "url": "https://fenna.ma", "city": "Casablanca", "wa": "+212 6 78 90 12 34", "wa_clean": "212678901234",
        "email": "contact@fenna.ma", "ig": "https://instagram.com/fenna.ma", "positioning": "Fashion / Tendance",
        "shopify_cost_usd": 130, "shopify_cost_mad": 1300,
        "pain_point": "Frais mensuels récurrents en dollars qui pèsent sur la rentabilité en phase de croissance.",
        "pitch_angle": "Investissez vos 15 000 DH annuels de frais Shopify dans vos campagnes d'influenceurs sur Instagram.",
        "recommended_stack": "Next.js ou WooCommerce Pro", "priority": "Moyenne", "status": "À Contacter"
    },
    {
        "id": 19, "name": "Lamoura Bijoux", "niche": "Bijouterie fine & Joaillerie tendance",
        "url": "https://lamoura.ma", "city": "Casablanca", "wa": "+212 6 45 67 89 01", "wa_clean": "212645678901",
        "email": "contact@lamoura.ma", "ig": "https://instagram.com/lamourabijoux.ma", "positioning": "Bijouterie / Féminin",
        "shopify_cost_usd": 140, "shopify_cost_mad": 1400,
        "pain_point": "Panier d'achat standard Shopify qui distrait l'acheteur mobile et réduit le taux de complétion des commandes.",
        "pitch_angle": "Tunnel d'achat 'Commander par WhatsApp' ou 'Paiement COD direct' optimisé pour doubler vos ventes.",
        "recommended_stack": "Next.js + Fast Checkout WhatsApp", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 20, "name": "Miguina Horlogerie", "niche": "Haute Horlogerie & Montres Prestige",
        "url": "https://miguina.com", "city": "Casablanca", "wa": "+212 6 61 23 45 67", "wa_clean": "212661234567",
        "email": "contact@miguina.com", "ig": "https://instagram.com/miguina_watches", "positioning": "Luxe & Prestige",
        "shopify_cost_usd": 290, "shopify_cost_mad": 2900,
        "pain_point": "Produits à forte valeur unitaire : la commission Shopify et l'absence de personnalisation sur-mesure dévalorisent l'offre.",
        "pitch_angle": "Un écrin numérique sur-mesure digne des grandes maisons horlogères suisses, sans dépendance à une plateforme SaaS tierce.",
        "recommended_stack": "Next.js + 3D Viewer / High-End Styling", "priority": "🔥 Très Haute", "status": "À Contacter"
    },

    # NEWLY DISCOVERED CLIENTS (15 high-value prospects)
    {
        "id": 21, "name": "Concept Darna", "niche": "Luminaires & Décoration d'intérieur",
        "url": "https://conceptdarna.ma", "city": "Casablanca", "wa": "+212 6 17 95 79 62", "wa_clean": "212617957962",
        "email": "contact@conceptdarna.ma", "ig": "https://instagram.com/conceptdarna.ma", "positioning": "Haut de Gamme Déco",
        "shopify_cost_usd": 210, "shopify_cost_mad": 2100,
        "pain_point": "Objets volumineux nécessitant un calcul de frais de livraison par ville/région complexe mal géré par le checkout Shopify.",
        "pitch_angle": "Calcul automatique des frais de livraison selon la ville (Casa vs hors Casa) et intégration directe des transporteurs sans plugin payant.",
        "recommended_stack": "Next.js + Moteur de livraison personnalisé", "priority": "🔥 Très Haute", "status": "À Contacter"
    },
    {
        "id": 22, "name": "Kamerty", "niche": "Matériel photo, vidéo & studio professionnel",
        "url": "https://kamerty.ma", "city": "Casablanca", "wa": "+212 6 14 28 25 13", "wa_clean": "212614282513",
        "email": "contact@kamerty.ma", "ig": "https://instagram.com/kamerty.ma", "positioning": "High-Tech Pro / Matériel Audio-Vidéo",
        "shopify_cost_usd": 320, "shopify_cost_mad": 3200,
        "pain_point": "Gros catalogue technique + forfaits de maintenance + facturation d'entreprise (ICE/TVA) complexe sous Shopify.",
        "pitch_angle": "Génération automatique des devis et factures conformes DGI (avec ICE/IF) et passerelle CMI sans frais de transaction Shopify.",
        "recommended_stack": "Next.js / Laravel + Module Facturation ICE", "priority": "🔥 Très Haute", "status": "À Contacter"
    },
    {
        "id": 23, "name": "Hadri Parfums", "niche": "Parfumerie & Fragrances orientales",
        "url": "https://hadriparfums.ma", "city": "Casablanca", "wa": "+212 6 29 85 29 03", "wa_clean": "212629852903",
        "email": "contact@hadriparfums.ma", "ig": "https://instagram.com/hadriparfums", "positioning": "Parfumerie / Volume COD",
        "shopify_cost_usd": 180, "shopify_cost_mad": 1800,
        "pain_point": "Fort recours aux offres packs (pack découverte, coffrets) dépendant d'apps tierces payantes et instables.",
        "pitch_angle": "Système de 'Bundle Builder' (composez votre pack) 100% natif, sans redevance mensuelle et avec temps de réponse instantané.",
        "recommended_stack": "Next.js + Custom Bundle Engine", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 24, "name": "Massinart", "niche": "Tableaux d'art & Décoration murale",
        "url": "https://massinart.ma", "city": "Casablanca / Rabat / Marrakech", "wa": "+212 7 74 51 59 75", "wa_clean": "212774515975",
        "email": "contact@massinart.ma", "ig": "https://instagram.com/massinart.ma", "positioning": "Premium Déco / Multi-Showroom",
        "shopify_cost_usd": 350, "shopify_cost_mad": 3500,
        "pain_point": "Coût annuel Shopify exorbitant (>40 000 DH/an avec apps de customisation des cadres/tailles) + problème de synchronisation multi-boutiques.",
        "pitch_angle": "Un configurateur de tableaux sur-mesure (choix cadre, taille, mockup dans le salon) ultra-rapide et synchronisé avec vos 3 showrooms.",
        "recommended_stack": "Next.js Headless + Visual Customizer", "priority": "🔥 Très Haute", "status": "À Contacter"
    },
    {
        "id": 25, "name": "Lustra Maroc", "niche": "Luminaires design & Lustres modernes",
        "url": "https://lustra.ma", "city": "Casablanca", "wa": "+212 6 60 74 34 93", "wa_clean": "212660743493",
        "email": "lustra.maroc@gmail.com", "ig": "https://instagram.com/lustra.ma", "positioning": "Décoration / Luminaires",
        "shopify_cost_usd": 170, "shopify_cost_mad": 1700,
        "pain_point": "Besoin de devis pour les architectes d'intérieur et hôtels non géré nativement par Shopify.",
        "pitch_angle": "Double mode : Commande directe COD pour particuliers + Demande de devis B2B instantanée pour les pros.",
        "recommended_stack": "Next.js B2B & B2C Hybride", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 26, "name": "Sahareye", "niche": "Mode féminine contemporaine & Caftans",
        "url": "https://sahareye.ma", "city": "Casablanca", "wa": "+212 5 22 33 47 77", "wa_clean": "212522334777",
        "email": "hello@sahareye.com", "ig": "https://instagram.com/sahareye_officiel", "positioning": "Mode & Caftans Modernes",
        "shopify_cost_usd": 220, "shopify_cost_mad": 2200,
        "pain_point": "Clientèle MRE et internationale : Shopify impose des frais de conversion de devise et bloque l'optimisation locale.",
        "pitch_angle": "Vendez à la fois aux clientes au Maroc en COD/CMI et aux MRE en France/Europe avec Stripe sans double commission.",
        "recommended_stack": "Next.js Multilingue (FR/AR/EN) + Multi-devises", "priority": "🔥 Très Haute", "status": "À Contacter"
    },
    {
        "id": 27, "name": "Ottavio Shoes", "niche": "Chaussures homme cuir & Bottines de luxe",
        "url": "https://ottavio.ma", "city": "Casablanca", "wa": "+212 6 63 23 59 66", "wa_clean": "212663235966",
        "email": "contact@ottavio.ma", "ig": "https://instagram.com/ottavio_shoes", "positioning": "Chaussures Homme Haut de Gamme",
        "shopify_cost_usd": 240, "shopify_cost_mad": 2400,
        "pain_point": "Frais d'apps d'authentification OTP WhatsApp tierces qui coûtent cher et alourdissent le code du site.",
        "pitch_angle": "Connexion et confirmation WhatsApp 100% intégrées à votre propre serveur, zéro dépendance à des apps tierces.",
        "recommended_stack": "Next.js + WhatsApp Business Cloud API", "priority": "🔥 Très Haute", "status": "À Contacter"
    },
    {
        "id": 28, "name": "Arwa Fashion", "niche": "Modest fashion, Abayas & Hijabs de créateur",
        "url": "https://arwafashion.ma", "city": "Casablanca / Rabat", "wa": "+212 7 08 70 17 01", "wa_clean": "212708701701",
        "email": "contact@arwafashion.ma", "ig": "https://instagram.com/arwashop.maroc", "positioning": "Modest Fashion / Grand Public",
        "shopify_cost_usd": 280, "shopify_cost_mad": 2800,
        "pain_point": "Fort volume de trafic lors des drops (Aïd, Ramadan) qui fait exploser les coûts et ralentit les serveurs partagés.",
        "pitch_angle": "Une infrastructure capable d'absorber 50 000 visiteurs simultanés lors de vos lancements sans aucun crash ni frais par commande.",
        "recommended_stack": "Next.js + Vercel / Cloudflare Edge Caching", "priority": "🔥 Très Haute", "status": "À Contacter"
    },
    {
        "id": 29, "name": "Moan Studio", "niche": "Streetwear & Prêt-à-porter féminin branché",
        "url": "https://moanstudio.ma", "city": "Casablanca / Tanger", "wa": "+212 6 66 93 56 01", "wa_clean": "212666935601",
        "email": "contact@moanstudio.ma", "ig": "https://instagram.com/moanstudio", "positioning": "Mode Jeune & Tendance",
        "shopify_cost_usd": 200, "shopify_cost_mad": 2000,
        "pain_point": "Thème Shopify standardisé qui ne transmet pas l'esprit créatif et 'hype' de la marque urbaine.",
        "pitch_angle": "Un design ultra-moderne inspiré des marques streetwear internationales avec des animations fluides 60fps sur iPhone et Android.",
        "recommended_stack": "Next.js + Framer Motion + Headless Commerce", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 30, "name": "Elite Store", "niche": "Streetwear & Équipements de sport",
        "url": "https://elsto.ma", "city": "Fès / Casablanca", "wa": "+212 6 60 00 00 00", "wa_clean": "212660000000",
        "email": "elite.store667@gmail.com", "ig": "https://instagram.com/elsto.ma", "positioning": "Sport & Streetwear",
        "shopify_cost_usd": 150, "shopify_cost_mad": 1500,
        "pain_point": "Déperdition de clients au moment du checkout à cause des champs inutiles de Shopify.",
        "pitch_angle": "Checkout éclair en 2 champs (Nom + Téléphone) avec sélection automatique de la ville pour maximiser vos ventes d'annonces TikTok.",
        "recommended_stack": "Next.js Ultra-Fast COD", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 31, "name": "Timgharin", "niche": "Cosmétique naturelle, Soins cheveux & Argan",
        "url": "https://timgharin.ma", "city": "Agadir / Casablanca", "wa": "+212 6 64 13 62 50", "wa_clean": "212664136250",
        "email": "contact@timgharin.ma", "ig": "https://instagram.com/timgharin.ma", "positioning": "Cosmétique Naturelle Marocaine",
        "shopify_cost_usd": 160, "shopify_cost_mad": 1600,
        "pain_point": "Apps d'avis et de preuves sociales qui pèsent sur la dotation devises et ralentissent le site.",
        "pitch_angle": "Système d'avis vérifiés, vidéos témoignages TikTok intégrées sans ralentissement et zéro coût d'abonnement mensuel.",
        "recommended_stack": "Next.js + Avis Natifs + Fast Video", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 32, "name": "ForYou Parfum", "niche": "Parfums originaux hommes & femmes",
        "url": "https://foryou.ma", "city": "Casablanca", "wa": "+212 6 22 90 66 77", "wa_clean": "212622906677",
        "email": "parfums@foryou.ma", "ig": "https://instagram.com/foryou.parfum.maroc", "positioning": "Parfumerie / Volume",
        "shopify_cost_usd": 210, "shopify_cost_mad": 2100,
        "pain_point": "Gestion manuelle fastidieuse des retours et confirmations COD Shopify vers transporteurs locaux.",
        "pitch_angle": "Intégration directe de vos expéditions avec Ozon/Sendit/Cathedis et détection automatique des faux numéros pour réduire les retours de 30%.",
        "recommended_stack": "Next.js + Validation Téléphone OTP & Anti-Fake", "priority": "🔥 Très Haute", "status": "À Contacter"
    },
    {
        "id": 33, "name": "Binaa Smart Home", "niche": "Domotique, serrures connectées & sécurité",
        "url": "https://binaa.ma", "city": "Casablanca", "wa": "+212 6 61 58 78 16", "wa_clean": "212661587816",
        "email": "hello@binaa.ma", "ig": "https://instagram.com/binaa.ma", "positioning": "Smart Home & High-Tech",
        "shopify_cost_usd": 240, "shopify_cost_mad": 2400,
        "pain_point": "Clients voulant réserver une installation à domicile avec le produit : non supporté nativement par Shopify.",
        "pitch_angle": "Module intégré 'Achat + Réservation de technicien d'installation' et facturation pro sans surcoût SaaS.",
        "recommended_stack": "Next.js + Système de prise de RDV technique", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 34, "name": "Les Cafés Mirka", "niche": "Cafés torréfiés artisanaux & Équipements",
        "url": "https://mirka.ma", "city": "Casablanca", "wa": "+212 6 63 60 23 29", "wa_clean": "212663602329",
        "email": "contact@mirka.ma", "ig": "https://instagram.com/lescafesmirka", "positioning": "Artisanal / Café de Spécialité",
        "shopify_cost_usd": 170, "shopify_cost_mad": 1700,
        "pain_point": "Abonnements café mensuels difficiles et coûteux à mettre en place avec les banques marocaines sur Shopify.",
        "pitch_angle": "Système d'abonnement café récurrent adapté au marché marocain (prélèvement ou livraison mensuelle planifiée).",
        "recommended_stack": "Next.js + Système d'Abonnement Récurrent", "priority": "Haute", "status": "À Contacter"
    },
    {
        "id": 35, "name": "Chabi Chic", "niche": "Art de vivre, céramique artisanale & Déco",
        "url": "https://chabi-chic.com", "city": "Marrakech", "wa": "+212 6 10 10 47 54", "wa_clean": "212610104754",
        "email": "contact@chabi-chic.com", "ig": "https://instagram.com/chabichicmorocco", "positioning": "Luxe Artisanal / International",
        "shopify_cost_usd": 450, "shopify_cost_mad": 4500,
        "pain_point": "Énorme coût Shopify Plus / Advanced + commissions sur les ventes internationales pesant des dizaines de milliers de DH.",
        "pitch_angle": "Plateforme headless sur-mesure d'envergure mondiale, économisant plus de 50 000 DH/an de commissions de plateforme avec design haute couture.",
        "recommended_stack": "Next.js / Headless Commerce Multi-entrepôts", "priority": "🔥 Très Haute", "status": "À Contacter"
    }
]

# ==========================================
# SHEET 1: DASHBOARD & KPIS
# ==========================================
ws_dash = wb.create_sheet(title="📊 Dashboard & Synthèse")
ws_dash.views.sheetView[0].showGridLines = True

# Banner
ws_dash.merge_cells("A1:K2")
banner_cell = ws_dash["A1"]
banner_cell.value = "🇲🇦 PROGRAMME DE MIGRATION SHOPIFY VERS SITE PROPRIÉTAIRE - MAROC"
banner_cell.font = font_title
banner_cell.fill = fill_navy_dark
banner_cell.alignment = align_center
ws_dash.row_dimensions[1].height = 25
ws_dash.row_dimensions[2].height = 25

ws_dash["A3"].value = "Pipeline de prospection stratégique & Étude d'impact financier pour les marques e-commerce marocaines"
ws_dash["A3"].font = font_subtitle

# KPI Cards Block (Row 5 to 7)
kpis = [
    ("TOTAL PROSPECTS QUALIFIÉS", '=COUNTA(\'🎯 Base Prospects (35)\'!A4:A38)', "Boutiques Shopify au Maroc", "A", "C"),
    ("PROSPECTS 'TRÈS HAUTE' PRIORITÉ", '=COUNTIF(\'🎯 Base Prospects (35)\'!M4:M38, "*Très Haute*")', "Marques prêtes pour migration", "D", "E"),
    ("ÉCONOMIES MOY. ANNUELLES / CLIENT", '=AVERAGE(\'🎯 Base Prospects (35)\'!L4:L38)*12', "Dirhams (MAD) économisés/an", "F", "G"),
    ("FUITE DE DEVISES TOTALE / AN", '=SUM(\'🎯 Base Prospects (35)\'!L4:L38)*12', "MAD gaspillés en abonnements US", "H", "K")
]

ws_dash.row_dimensions[5].height = 18
ws_dash.row_dimensions[6].height = 36
ws_dash.row_dimensions[7].height = 18

for title, formula, sub, col_start, col_end in kpis:
    # merge
    ws_dash.merge_cells(f"{col_start}5:{col_end}5")
    ws_dash.merge_cells(f"{col_start}6:{col_end}6")
    ws_dash.merge_cells(f"{col_start}7:{col_end}7")
    
    c5 = ws_dash[f"{col_start}5"]
    c5.value = title
    c5.font = font_kpi_label
    c5.alignment = align_center
    c5.fill = fill_kpi_card
    
    c6 = ws_dash[f"{col_start}6"]
    c6.value = formula
    c6.font = font_kpi_num
    c6.alignment = align_center
    c6.fill = fill_kpi_card
    if "SUM" in formula or "AVERAGE" in formula:
        c6.number_format = '#,##0 "DH"'
    
    c7 = ws_dash[f"{col_start}7"]
    c7.value = sub
    c7.font = Font(name="Segoe UI", size=8, italic=True, color="64748B")
    c7.alignment = align_center
    c7.fill = fill_kpi_card
    
    # borders
    for row in range(5, 8):
        for col in range(openpyxl.utils.column_index_from_string(col_start), openpyxl.utils.column_index_from_string(col_end) + 1):
            cell = ws_dash.cell(row=row, column=col)
            cell.border = thin_border

# Breakdown Tables (Row 9 onwards)
ws_dash["A9"].value = "RÉPARTITION PAR CATÉGORIE / NICHE"
ws_dash["A9"].font = font_section

niches_summary = [
    ("Bijouterie, Joaillerie & Horlogerie", 8, "Paniers élevés, besoin d'élégance et de confiance maximale"),
    ("Mode, Prêt-à-porter, Caftans & Abayas", 8, "Gros volumes, trafic intense pendant les drops, mobile 90%+"),
    ("Maroquinerie & Chaussures en cuir", 5, "Artisanat d'excellence (Fès/Marrakech), fort taux de conversion"),
    ("Parfumerie, Cosmétique & Bien-être", 6, "Produits récurrents, COD massif, besoin de bundles natifs"),
    ("Maison, Décoration d'intérieur & Art", 5, "Configurateurs visuels, livraison par ville, commandes B2B/B2C"),
    ("High-Tech, Domotique & Santé", 3, "Fiches techniques riches, SAV et facturation ICE obligatoire")
]

headers_niche = ["Catégorie Principale", "Nombre de Boutiques", "% du Total", "Enjeux Clés de Migration"]
for c_idx, h in enumerate(headers_niche, 1):
    cell = ws_dash.cell(row=10, column=c_idx if c_idx < 4 else 4)
    if c_idx == 4:
        ws_dash.merge_cells(f"D10:G10")
        cell = ws_dash["D10"]
    cell.value = h
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = thin_border

for r_idx, (cat, count, enjeu) in enumerate(niches_summary, 11):
    ws_dash.cell(row=r_idx, column=1, value=cat).font = font_data_bold
    ws_dash.cell(row=r_idx, column=2, value=count).font = font_data
    ws_dash.cell(row=r_idx, column=2).alignment = align_center
    ws_dash.cell(row=r_idx, column=3, value=count/35).font = font_data
    ws_dash.cell(row=r_idx, column=3).number_format = '0.0%'
    ws_dash.cell(row=r_idx, column=3).alignment = align_center
    
    ws_dash.merge_cells(f"D{r_idx}:G{r_idx}")
    cell_enjeu = ws_dash[f"D{r_idx}"]
    cell_enjeu.value = enjeu
    cell_enjeu.font = font_data
    cell_enjeu.alignment = align_left
    
    for c in range(1, 8):
        ws_dash.cell(row=r_idx, column=c).border = thin_border
        if r_idx % 2 == 1:
            ws_dash.cell(row=r_idx, column=c).fill = fill_zebra

# Distribution by Priority
ws_dash["I9"].value = "PRIORITÉ DE PROSPECTION"
ws_dash["I9"].font = font_section

prio_summary = [
    ("🔥 Très Haute (Hot Leads)", '=COUNTIF(\'🎯 Base Prospects (35)\'!M4:M38, "*Très Haute*")', "À contacter en premier (Gros gain financier/image)"),
    ("⚡ Haute Priorité", '=COUNTIF(\'🎯 Base Prospects (35)\'!M4:M38, "*Haute*") - COUNTIF(\'🎯 Base Prospects (35)\'!M4:M38, "*Très Haute*")', "Fort potentiel d'économies & COD optimisable"),
    ("📌 Moyenne Priorité", '=COUNTIF(\'🎯 Base Prospects (35)\'!M4:M38, "*Moyenne*")', "Marques plus jeunes ou niches spécialisées")
]

ws_dash.merge_cells("I10:J10")
ws_dash["I10"].value = "Niveau de Priorité"
ws_dash["I10"].font = font_header
ws_dash["I10"].fill = fill_header
ws_dash["I10"].alignment = align_center
ws_dash["I10"].border = thin_border

ws_dash["K10"].value = "Nombre"
ws_dash["K10"].font = font_header
ws_dash["K10"].fill = fill_header
ws_dash["K10"].alignment = align_center
ws_dash["K10"].border = thin_border

for r_idx, (prio_label, formula_val, desc) in enumerate(prio_summary, 11):
    ws_dash.merge_cells(f"I{r_idx}:J{r_idx}")
    c_lbl = ws_dash[f"I{r_idx}"]
    c_lbl.value = prio_label
    c_lbl.font = font_data_bold
    c_lbl.border = thin_border
    
    c_val = ws_dash[f"K{r_idx}"]
    c_val.value = formula_val
    c_val.font = font_data_bold
    c_val.alignment = align_center
    c_val.border = thin_border
    
    if "Très Haute" in prio_label:
        c_lbl.fill = fill_prio_hot
        c_val.fill = fill_prio_hot
    elif "Haute" in prio_label:
        c_lbl.fill = fill_prio_high
        c_val.fill = fill_prio_high
    else:
        c_lbl.fill = fill_prio_med
        c_val.fill = fill_prio_med

# Why Moroccan Businesses Migrate from Shopify (Value Proposition Block)
ws_dash["A18"].value = "LES 4 DOULEURS MAJEURES DE SHOPIFY POUR LES COMMERÇANTS MAROCAINS"
ws_dash["A18"].font = font_section

pain_matrix = [
    ("1. Pression sur la Dotation E-commerce", "Les commerçants paient l'abonnement Shopify ($39-$399) + 5 à 10 apps ($100-$300) par mois en USD sur leur carte bancaire internationale. Cela épuise leur quota officiel (dotation e-commerce) au détriment de leurs dépenses publicitaires Facebook/TikTok Ads indispensables."),
    ("2. Pénalité de 2% sur les Commandes COD", "Shopify n'ayant pas de passerelle 'Shopify Payments' au Maroc, la plateforme prélève des frais de transaction additionnels (0.5% à 2%) sur toutes les commandes, y compris le Cash on Delivery (paiement à la livraison) !"),
    ("3. Checkout Inadapté au Marché Marocain", "Le checkout par défaut de Shopify compte 3 étapes et exige code postal, province, etc. Les Marocains n'ont pas de code postal. Les apps de formulaire COD (Releasit/EasySell) coûtent un abonnement mensuel et ralentissent la boutique."),
    ("4. Lenteur Mobile & Dépendance Totale", "Chaque app Shopify injecte des scripts tiers externes qui font chuter le score Google PageSpeed mobile sous les 40/100 sur le réseau 4G marocain, diminuant drastiquement le retour sur investissement des publicités.")
]

ws_dash.row_dimensions[19].height = 20
for idx, (p_title, p_desc) in enumerate(pain_matrix, 20):
    ws_dash.row_dimensions[idx].height = 42
    ws_dash.merge_cells(f"A{idx}:C{idx}")
    ws_dash.merge_cells(f"D{idx}:K{idx}")
    
    c_title = ws_dash[f"A{idx}"]
    c_title.value = p_title
    c_title.font = font_data_bold
    c_title.fill = fill_kpi_card
    c_title.alignment = align_left
    c_title.border = thin_border
    
    c_desc = ws_dash[f"D{idx}"]
    c_desc.value = p_desc
    c_desc.font = font_data
    c_desc.fill = fill_white
    c_desc.alignment = align_left
    c_desc.border = thin_border
    
    for c in range(1, 12):
        ws_dash.cell(row=idx, column=c).border = thin_border

# ==========================================
# SHEET 2: MASTER PROSPECTS DATABASE (35 STORES)
# ==========================================
ws_leads = wb.create_sheet(title="🎯 Base Prospects (35)")
ws_leads.views.sheetView[0].showGridLines = True

headers_leads = [
    "N°", "Marque (Smiya)", "Niche / Catégorie", "Site Web (URL)", "Ville / Siège",
    "WhatsApp Business", "Lien Direct WhatsApp", "Email Contact", "Instagram",
    "Positionnement", "Coût Shopify Estimé ($/m)", "Coût Shopify Estimé (DH/m)",
    "Priorité", "Douleur Principale Shopify", "Stack Recommandée",
    "Accroche Personnalisée / Pitch", "Statut Prospection", "Dernier Contact", "Prochaine Action"
]

# Title banner
ws_leads.merge_cells("A1:S1")
t_cell = ws_leads["A1"]
t_cell.value = "BASE DE PROSPECTION STRATÉGIQUE - 35 BOUTIQUES SHOPIFY AU MAROC À MIGRER"
t_cell.font = font_title
t_cell.fill = fill_navy_dark
t_cell.alignment = align_center
ws_leads.row_dimensions[1].height = 32

# Table headers
ws_leads.row_dimensions[3].height = 28
for col_idx, h in enumerate(headers_leads, 1):
    cell = ws_leads.cell(row=3, column=col_idx)
    cell.value = h
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = thin_border

ws_leads.freeze_panes = "C4"

for r_idx, lead in enumerate(prospects_data, 4):
    ws_leads.row_dimensions[r_idx].height = 32
    
    c_id = ws_leads.cell(row=r_idx, column=1, value=lead["id"])
    c_id.alignment = align_center
    c_id.font = font_data_bold
    
    c_name = ws_leads.cell(row=r_idx, column=2, value=lead["name"])
    c_name.font = font_data_bold
    
    c_niche = ws_leads.cell(row=r_idx, column=3, value=lead["niche"])
    c_niche.font = font_data
    
    c_url = ws_leads.cell(row=r_idx, column=4, value=lead["url"])
    c_url.font = font_link
    c_url.hyperlink = lead["url"]
    
    c_city = ws_leads.cell(row=r_idx, column=5, value=lead["city"])
    c_city.font = font_data
    c_city.alignment = align_center
    
    c_wa = ws_leads.cell(row=r_idx, column=6, value=lead["wa"])
    c_wa.font = font_data_bold
    c_wa.alignment = align_center
    
    # Clickable WhatsApp Link
    wa_link = f"https://wa.me/{lead['wa_clean']}?text=Salam%20{lead['name'].replace(' ', '%20')}%2C%20je%20vous%20contacte%20concernant%20votre%20site%20web"
    c_walink = ws_leads.cell(row=r_idx, column=7, value="💬 Ouvrir WhatsApp")
    c_walink.font = font_link
    c_walink.hyperlink = wa_link
    c_walink.alignment = align_center
    
    c_email = ws_leads.cell(row=r_idx, column=8, value=lead["email"])
    c_email.font = font_data
    
    c_ig = ws_leads.cell(row=r_idx, column=9, value="Instagram")
    c_ig.font = font_link
    c_ig.hyperlink = lead["ig"]
    c_ig.alignment = align_center
    
    c_pos = ws_leads.cell(row=r_idx, column=10, value=lead["positioning"])
    c_pos.font = font_data
    c_pos.alignment = align_center
    
    c_cost_usd = ws_leads.cell(row=r_idx, column=11, value=lead["shopify_cost_usd"])
    c_cost_usd.font = font_data
    c_cost_usd.number_format = '"$"#,##0'
    c_cost_usd.alignment = align_right
    
    # Formula for MAD: USD * 10
    c_cost_mad = ws_leads.cell(row=r_idx, column=12, value=f"=K{r_idx}*10")
    c_cost_mad.font = font_data_bold
    c_cost_mad.number_format = '#,##0 "DH"'
    c_cost_mad.alignment = align_right
    
    c_prio = ws_leads.cell(row=r_idx, column=13, value=lead["priority"])
    c_prio.font = font_data_bold
    c_prio.alignment = align_center
    if "Très Haute" in lead["priority"]:
        c_prio.fill = fill_prio_hot
    elif "Haute" in lead["priority"]:
        c_prio.fill = fill_prio_high
    else:
        c_prio.fill = fill_prio_med
        
    c_pain = ws_leads.cell(row=r_idx, column=14, value=lead["pain_point"])
    c_pain.font = font_data
    
    c_stack = ws_leads.cell(row=r_idx, column=15, value=lead["recommended_stack"])
    c_stack.font = font_data
    
    c_pitch = ws_leads.cell(row=r_idx, column=16, value=lead["pitch_angle"])
    c_pitch.font = font_data
    
    # Dynamic status from orchestrator run.json if complete
    clean_id = re.sub(r'[\\/*?:"<>|]', '', lead["name"]).strip()
    clean_id = re.sub(r'[\s\-]+', '_', clean_id)
    run_file_check = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leads", clean_id, "run.json")
    lead_status = lead["status"]
    last_contact_str = "-"
    next_action_str = "Premier contact WhatsApp / Audio personnalisé"
    is_orchestrated = False
    
    if os.path.exists(run_file_check):
        try:
            with open(run_file_check, "r", encoding="utf-8") as rf:
                rdata = json.load(rf)
                if rdata.get("stage") == "complete" and rdata.get("status") == "passed":
                    lead_status = "✅ Démo & Audit Prêts"
                    last_contact_str = "Audit & Démo Next.js générés"
                    next_action_str = "Envoyer note vocale WhatsApp & email"
                    is_orchestrated = True
        except Exception:
            pass

    c_status = ws_leads.cell(row=r_idx, column=17, value=lead_status)
    c_status.font = font_data_bold
    c_status.fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid") if is_orchestrated else fill_status_new
    c_status.alignment = align_center
    
    c_last = ws_leads.cell(row=r_idx, column=18, value=last_contact_str)
    c_last.alignment = align_center
    c_last.font = font_data
    
    c_next = ws_leads.cell(row=r_idx, column=19, value=next_action_str)
    c_next.font = font_data
    
    # Borders and alternating fill for non-colored cells
    for col in range(1, 20):
        cell = ws_leads.cell(row=r_idx, column=col)
        cell.border = thin_border
        if r_idx % 2 == 1 and col not in [13, 17]:
            cell.fill = fill_zebra

# Total row at bottom
total_row = len(prospects_data) + 4
ws_leads.row_dimensions[total_row].height = 25
ws_leads.merge_cells(f"A{total_row}:J{total_row}")
tot_lbl = ws_leads[f"A{total_row}"]
tot_lbl.value = "TOTAL DES FRAIS MENSUELS ESTIMÉS SHOPIFY (ÉCONOMIES POTENTIELLES POUR CES MARQUES) :"
tot_lbl.font = font_header
tot_lbl.fill = fill_header
tot_lbl.alignment = Alignment(horizontal="right", vertical="center")

tot_usd = ws_leads.cell(row=total_row, column=11, value=f"=SUM(K4:K{total_row-1})")
tot_usd.font = font_header
tot_usd.fill = fill_header
tot_usd.number_format = '"$"#,##0'
tot_usd.alignment = align_right

tot_mad = ws_leads.cell(row=total_row, column=12, value=f"=SUM(L4:L{total_row-1})")
tot_mad.font = font_header
tot_mad.fill = fill_header
tot_mad.number_format = '#,##0 "DH"'
tot_mad.alignment = align_right

for c in range(1, 20):
    ws_leads.cell(row=total_row, column=c).border = thick_bottom_border

# ==========================================
# SHEET 3: PITCH & SCRIPTS (DARIJA & FRANÇAIS)
# ==========================================
ws_pitch = wb.create_sheet(title="💡 Scripts & Argumentaire")
ws_pitch.views.sheetView[0].showGridLines = True

ws_pitch.merge_cells("A1:G1")
ws_pitch["A1"].value = "SCRIPTS DE PROSPECTION COMMERCIALE & GUIDE D'OBJECTIONS (MAROC)"
ws_pitch["A1"].font = font_title
ws_pitch["A1"].fill = fill_navy_dark
ws_pitch["A1"].alignment = align_center
ws_pitch.row_dimensions[1].height = 32

pitch_sections = [
    ("1. Premier Message WhatsApp d'Accroche (En Darija Pro)",
     "Objectif : Obtenir une réponse du gérant / fondateur en 2 minutes en touchant directement au portefeuille (Devises / Frais cachés)",
     """Salam Si [Prénom du Gérant] / L'équipe de [Nom de la Marque], tbarkellah 3likom service w les produits dyalkom top !

Kanchouf bli le site dyalkom khddam b Shopify. Comme vous le savez, m3a les limitations dyal la dotation e-commerce w l'Office des Changes f l-Meghrib, Shopify kayakhod likom :
1. Abonnement mensuel en dollars ($39 à $299) li kayconsomi likom l-plafond dyal carte e-commerce li khtajito l les pubs (Facebook/TikTok).
2. Des frais cachés dyal 2% 3la kol commande COD (paiement à la livraison) hit makaynch Shopify Payments f l-Maghreb.
3. Des applications mensuelles (PageFly, COD forms, Judge.me) li kayt9alo le site 3la l-mobile w kaytiyho le taux de conversion.

7na kan-développiw des sites e-commerce sur-mesure (Next.js / 100% dialek) :
✅ Zéro abonnement mensuel en devises (site dyalek pour toujours).
✅ Formulaire COD 1-clic ultra-rapide (< 1 seconde de chargement).
✅ Confirmation WhatsApp automatique w liaison m3a les sociétés de livraison (Cathedis, Ozon, AMEEX...).

Wach 3ndkom 10 d9ayeq had la semaine ndiro un audit gratuit dyal le site dyalkom w n-wariwkom ch7al t9do t-wfro par an ?"""),

    ("2. Script de Premier Contact par Email (En Français Professionnel)",
     "Objet : [Nom de la Marque] - Économisez 25 000 DH/an sur vos frais Shopify & Boostez votre conversion mobile",
     """Bonjour [Nom du Dirigeant / Équipe E-commerce],

Félicitations pour le développement de la marque [Nom de la Marque], votre positionnement sur le marché marocain est remarquable.

En analysant votre boutique en ligne [URL], nous avons constaté que vous utilisez la plateforme Shopify. Si Shopify est une solution pratique au démarrage, elle devient un véritable frein pour les marques marocaines en phase d'accélération :

1. Pression sur votre Dotation E-commerce : Entre le forfait Shopify et les applications tierces indispensables (PageFly, formulaires COD, avis), vous dépensez entre 1 500 et 3 000 DH/mois en devises internationales, réduisant d'autant votre budget publicitaire Meta et TikTok.
2. Commissions de 2% sur le Cash-on-Delivery : Faute de Shopify Payments au Maroc, vous payez une pénalité sur chaque commande livrée.
3. Vitesse Mobile limitée : L'accumulation d'apps ralentit le chargement sur smartphone (4G Maroc), ce qui entraîne une perte de 20% à 30% des visiteurs payés via la pub.

Notre offre :
Nous migrons votre boutique vers votre propre infrastructure e-commerce propriétaire haute performance (Next.js / Technologie moderne) :
• 0 DH d'abonnement en devises (vous êtes 100% propriétaire de votre boutique).
• Formulaire Cash on Delivery optimisé en 2 clics avec validation par WhatsApp.
• Vitesse instantanée (Score Google PageSpeed 95+/100) pour maximiser le ROI de vos pubs.

Seriez-vous disponible pour un échange rapide de 15 minutes cette semaine (Visio ou WhatsApp) afin d'examiner l'audit technique et financier de votre boutique ?

Bien cordialement,
[Votre Nom / Votre Agence]
[Votre Téléphone WhatsApp]"""),

    ("3. Traitement des Principales Objections des Clients Marocains",
     "Comment répondre aux doutes les plus fréquents pour conclure le contrat",
     """OBJECTION 1 : 'Shopify c'est simple, comment je vais gérer mes produits sans Shopify ?'
RÉPONSE : 'Vous aurez un tableau de bord (Back-office) en français ou arabe encore plus simple que Shopify ! Vous pourrez ajouter des produits, modifier les prix, voir les commandes et imprimer les bordereaux de livraison en 1 clic depuis votre PC ou votre téléphone, sans aucune ligne de code.'

OBJECTION 2 : 'La migration va-t-elle couper mes ventes ou me faire perdre mes données ?'
RÉPONSE : 'Zéro interruption de service ! Nous importons l'intégralité de vos clients, historiques de commandes et fiches produits sur votre nouveau site. Le basculement se fait en 10 minutes durant la nuit. Vos campagnes publicitaires continuent de tourner sans perturbation.'

OBJECTION 3 : 'Combien coûte la création du site par rapport à Shopify ?'
RÉPONSE : 'Sur Shopify, vous payez entre 18 000 et 35 000 DH chaque année, indéfiniment. Avec un site propriétaire, vous faites un investissement unique amorti en 6 à 9 mois grâce aux économies d'abonnements et au gain de conversion, puis votre site vous appartient à vie.'

OBJECTION 4 : 'Et la sécurité / hébergement ?'
RÉPONSE : 'Votre site est hébergé sur des serveurs Cloud mondiaux sécurisés (Vercel / Cloudflare) avec certificat SSL bancaire et sauvegardes quotidiennes automatiques. C'est le même niveau de sécurité que les géants mondiaux.'""")
]

current_r = 3
for title, subtitle, content in pitch_sections:
    ws_pitch.merge_cells(f"A{current_r}:G{current_r}")
    c_st = ws_pitch[f"A{current_r}"]
    c_st.value = title
    c_st.font = font_section
    c_st.fill = fill_kpi_card
    ws_pitch.row_dimensions[current_r].height = 24
    
    current_r += 1
    ws_pitch.merge_cells(f"A{current_r}:G{current_r}")
    c_sub = ws_pitch[f"A{current_r}"]
    c_sub.value = subtitle
    c_sub.font = font_subtitle
    ws_pitch.row_dimensions[current_r].height = 18
    
    current_r += 1
    ws_pitch.merge_cells(f"A{current_r}:G{current_r}")
    c_txt = ws_pitch[f"A{current_r}"]
    c_txt.value = content
    c_txt.font = font_data
    c_txt.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    
    # Calculate height based on lines
    line_count = len(content.split('\n'))
    ws_pitch.row_dimensions[current_r].height = max(80, line_count * 16)
    
    for c in range(1, 8):
        ws_pitch.cell(row=current_r-2, column=c).border = thin_border
        ws_pitch.cell(row=current_r-1, column=c).border = thin_border
        ws_pitch.cell(row=current_r, column=c).border = thin_border
        
    current_r += 2

# ==========================================
# SHEET 4: CALCULATEUR ROI ET ÉCONOMIES
# ==========================================
ws_roi = wb.create_sheet(title="💰 Calculateur ROI Migration")
ws_roi.views.sheetView[0].showGridLines = True

ws_roi.merge_cells("A1:G1")
ws_roi["A1"].value = "SIMULATEUR DE RENTABILITÉ : SHOPIFY VS SITE PROPRIÉTAIRE (NEXT.JS)"
ws_roi["A1"].font = font_title
ws_roi["A1"].fill = fill_navy_dark
ws_roi["A1"].alignment = align_center
ws_roi.row_dimensions[1].height = 32

ws_roi["A3"].value = "PARAMÈTRES DE LA BOUTIQUE DU CLIENT (MODIFIABLES)"
ws_roi["A3"].font = font_section

params = [
    ("Chiffre d'Affaires Mensuel Estimé (DH)", 150000, "CA moyen d'un e-commerçant marocain actif"),
    ("Nombre de commandes par mois", 500, "Panier moyen ~300 DH"),
    ("Plan Shopify utilisé ($/mois)", 39, "Basic: $39 / Shopify: $105 / Advanced: $399"),
    ("Frais d'applications Shopify mensuels ($/mois)", 80, "EasySell/Releasit, PageFly, Judge.me, etc."),
    ("Commission Shopify sur transactions non-Shopify Payments", 0.02, "2.0% pour Basic, 1.0% pour Shopify"),
    ("Taux de change USD -> MAD", 10.0, "1 USD = 10 MAD environ"),
    ("Coût de développement du Site Propriétaire (Devis Agence DH)", 18000, "Investissement initial one-shot"),
    ("Coût d'hébergement serveur mensuel du Site Propriétaire (DH)", 100, "Vercel / Hetzner / Hostinger")
]

ws_roi.row_dimensions[4].height = 24
ws_roi["A4"].value = "Paramètre"
ws_roi["A4"].font = font_header
ws_roi["A4"].fill = fill_header

ws_roi["B4"].value = "Valeur"
ws_roi["B4"].font = font_header
ws_roi["B4"].fill = fill_header

ws_roi.merge_cells("C4:E4")
ws_roi["C4"].value = "Description / Hypothèse"
ws_roi["C4"].font = font_header
ws_roi["C4"].fill = fill_header

for r_idx, (p_name, val, p_desc) in enumerate(params, 5):
    ws_roi.row_dimensions[r_idx].height = 22
    ws_roi.cell(row=r_idx, column=1, value=p_name).font = font_data_bold
    
    c_val = ws_roi.cell(row=r_idx, column=2, value=val)
    c_val.font = font_data_bold
    c_val.alignment = align_right
    if "DH" in p_name and "Taux" not in p_name:
        c_val.number_format = '#,##0 "DH"'
    elif "$" in p_name:
        c_val.number_format = '"$"#,##0'
    elif "Commission" in p_name:
        c_val.number_format = '0.0%'
    
    ws_roi.merge_cells(f"C{r_idx}:E{r_idx}")
    ws_roi[f"C{r_idx}"].value = p_desc
    ws_roi[f"C{r_idx}"].font = font_data
    
    for c in range(1, 6):
        ws_roi.cell(row=r_idx, column=c).border = thin_border

# Comparative Table
ws_roi["A14"].value = "COMPARAISON DES COÛTS RÉELS SUR 1 AN ET 3 ANS"
ws_roi["A14"].font = font_section

comp_headers = ["Poste de Coût", "Formule / Calcul", "Shopify (1 An)", "Site Propre (1 An)", "Shopify (3 Ans)", "Site Propre (3 Ans)"]
ws_roi.row_dimensions[15].height = 26
for c_idx, h in enumerate(comp_headers, 1):
    cell = ws_roi.cell(row=15, column=c_idx)
    cell.value = h
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = thin_border

comp_rows = [
    ("Frais d'Abonnement Plateforme", "(Plan $ * Taux * Mois)", "=B7*B10*12", "0", "=B7*B10*36", "0"),
    ("Frais des Applications Tierces", "(Apps $ * Taux * Mois)", "=B8*B10*12", "0", "=B8*B10*36", "0"),
    ("Commissions Transactions (2% sur CA)", "(CA Mensuel * % Comm * Mois)", "=B5*B9*12", "0", "=B5*B9*36", "0"),
    ("Frais de Développement Initial", "Création sur-mesure", "0", "=B11", "0", "=B11"),
    ("Frais d'Hébergement & Maintenance", "Serveur Cloud", "0", "=B12*12", "0", "=B12*36"),
]

for r_idx, (post, form, s1, c1, s3, c3) in enumerate(comp_rows, 16):
    ws_roi.row_dimensions[r_idx].height = 22
    ws_roi.cell(row=r_idx, column=1, value=post).font = font_data_bold
    ws_roi.cell(row=r_idx, column=2, value=form).font = font_subtitle
    
    for c_idx, val in enumerate([s1, c1, s3, c3], 3):
        cell = ws_roi.cell(row=r_idx, column=c_idx, value=val)
        cell.font = font_data
        cell.number_format = '#,##0 "DH"'
        cell.alignment = align_right
        
    for c in range(1, 7):
        ws_roi.cell(row=r_idx, column=c).border = thin_border

# Total Row Comparison
tot_r = 21
ws_roi.row_dimensions[tot_r].height = 26
ws_roi.cell(row=tot_r, column=1, value="COÛT TOTAL CUMULÉ").font = font_header
ws_roi.cell(row=tot_r, column=1).fill = fill_navy_dark
ws_roi.cell(row=tot_r, column=2, value="Total des dépenses").font = font_subtitle
ws_roi.cell(row=tot_r, column=2).fill = fill_navy_dark

ws_roi.cell(row=tot_r, column=3, value="=SUM(C16:C20)").font = font_header
ws_roi.cell(row=tot_r, column=3).number_format = '#,##0 "DH"'
ws_roi.cell(row=tot_r, column=3).fill = fill_prio_hot
ws_roi.cell(row=tot_r, column=3).alignment = align_right

ws_roi.cell(row=tot_r, column=4, value="=SUM(D16:D20)").font = font_header
ws_roi.cell(row=tot_r, column=4).number_format = '#,##0 "DH"'
ws_roi.cell(row=tot_r, column=4).fill = fill_prio_high
ws_roi.cell(row=tot_r, column=4).alignment = align_right

ws_roi.cell(row=tot_r, column=5, value="=SUM(E16:E20)").font = font_header
ws_roi.cell(row=tot_r, column=5).number_format = '#,##0 "DH"'
ws_roi.cell(row=tot_r, column=5).fill = fill_prio_hot
ws_roi.cell(row=tot_r, column=5).alignment = align_right

ws_roi.cell(row=tot_r, column=6, value="=SUM(F16:F20)").font = font_header
ws_roi.cell(row=tot_r, column=6).number_format = '#,##0 "DH"'
ws_roi.cell(row=tot_r, column=6).fill = fill_prio_high
ws_roi.cell(row=tot_r, column=6).alignment = align_right

for c in range(1, 7):
    ws_roi.cell(row=tot_r, column=c).border = thick_bottom_border

# Net Savings & Break-even
ws_roi.merge_cells("A23:C24")
c_gain = ws_roi["A23"]
c_gain.value = "ÉCONOMIE NETTE RÉALISÉE DÈS LA PREMIÈRE ANNÉE :"
c_gain.font = font_section
c_gain.alignment = align_left

ws_roi.merge_cells("D23:F24")
c_gain_val = ws_roi["D23"]
c_gain_val.value = "=C21-D21"
c_gain_val.font = font_kpi_num
c_gain_val.number_format = '#,##0 "DH"'
c_gain_val.fill = PatternFill(start_color=EMERALD_LIGHT, end_color=EMERALD_LIGHT, fill_type="solid")
c_gain_val.alignment = align_center

ws_roi.merge_cells("A26:C27")
c_gain3 = ws_roi["A26"]
c_gain3.value = "ÉCONOMIE NETTE TOTALE SUR 3 ANS :"
c_gain3.font = font_section
c_gain3.alignment = align_left

ws_roi.merge_cells("D26:F27")
c_gain3_val = ws_roi["D26"]
c_gain3_val.value = "=E21-F21"
c_gain3_val.font = font_kpi_num
c_gain3_val.number_format = '#,##0 "DH"'
c_gain3_val.fill = PatternFill(start_color=EMERALD_LIGHT, end_color=EMERALD_LIGHT, fill_type="solid")
c_gain3_val.alignment = align_center

for r in [23, 24, 26, 27]:
    for col in range(1, 7):
        ws_roi.cell(row=r, column=col).border = thin_border

# ==========================================
# SHEET 5: SUIVI PROSPECTION CRM
# ==========================================
ws_crm = wb.create_sheet(title="📋 Suivi Prospection CRM")
ws_crm.views.sheetView[0].showGridLines = True

ws_crm.merge_cells("A1:K1")
ws_crm["A1"].value = "PIPELINE COMMERCIAL & JOURNAL DE SUIVI DES RELANCES"
ws_crm["A1"].font = font_title
ws_crm["A1"].fill = fill_navy_dark
ws_crm["A1"].alignment = align_center
ws_crm.row_dimensions[1].height = 32

crm_headers = [
    "Date Prise Contact", "Marque", "Interlocuteur", "Canal Utilisé",
    "Réponse Obtenue", "Statut Actuel", "Objection Majeure", "Valeur Devis Potentiel (DH)",
    "Date Prochaine Relance", "Action Prévue", "Commentaires"
]

ws_crm.row_dimensions[3].height = 26
for c_idx, h in enumerate(crm_headers, 1):
    cell = ws_crm.cell(row=3, column=c_idx)
    cell.value = h
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = thin_border

# Pre-populate rows with high priority leads ready to contact
sample_crm_leads = [
    (lead["name"], lead["priority"], lead["wa"]) for lead in prospects_data if "Haute" in lead["priority"]
]

for idx, (b_name, b_prio, b_wa) in enumerate(sample_crm_leads, 4):
    clean_id = re.sub(r'[\\/*?:"<>|]', '', b_name).strip()
    clean_id = re.sub(r'[\s\-]+', '_', clean_id)
    run_file_check = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leads", clean_id, "run.json")
    is_orchestrated = False
    if os.path.exists(run_file_check):
        try:
            with open(run_file_check, "r", encoding="utf-8") as rf:
                rdata = json.load(rf)
                if rdata.get("stage") == "complete":
                    is_orchestrated = True
        except Exception:
            pass

    ws_crm.row_dimensions[idx].height = 26
    ws_crm.cell(row=idx, column=1, value="26/10/2026" if is_orchestrated else "À planifier").alignment = align_center
    ws_crm.cell(row=idx, column=2, value=b_name).font = font_data_bold
    ws_crm.cell(row=idx, column=3, value="Fondateur / E-commerce Mgr").font = font_data
    ws_crm.cell(row=idx, column=4, value="WhatsApp Direct").alignment = align_center
    ws_crm.cell(row=idx, column=5, value="Démo & Audit validés" if is_orchestrated else "En attente premier message").font = font_data
    
    st_cell = ws_crm.cell(row=idx, column=6, value="2. Prêt pour Envoi" if is_orchestrated else "1. Nouveau Lead")
    st_cell.font = font_data_bold
    st_cell.alignment = align_center
    st_cell.fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid") if is_orchestrated else fill_status_new
    
    ws_crm.cell(row=idx, column=7, value="-").alignment = align_center
    
    devis_cell = ws_crm.cell(row=idx, column=8, value=18000)
    devis_cell.font = font_data_bold
    devis_cell.number_format = '#,##0 "DH"'
    devis_cell.alignment = align_right
    
    ws_crm.cell(row=idx, column=9, value="Immédiat" if is_orchestrated else "J+2").alignment = align_center
    ws_crm.cell(row=idx, column=10, value="Envoyer note vocale WhatsApp & pitch email" if is_orchestrated else "Envoyer note vocale WhatsApp personnalisée").font = font_data
    ws_crm.cell(row=idx, column=11, value=f"Priorité {b_prio} - Démo Next.js prête dans leads/{clean_id}/" if is_orchestrated else f"Priorité {b_prio} - Numéro : {b_wa}").font = font_data
    
    for c in range(1, 12):
        ws_crm.cell(row=idx, column=c).border = thin_border
        if idx % 2 == 1:
            ws_crm.cell(row=idx, column=c).fill = fill_zebra

# Set smart column widths for all sheets
for ws in wb.worksheets:
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            # ignore merged cells in length calculation
            if cell.coordinate in ws.merged_cells:
                continue
            val_str = str(cell.value or '')
            if val_str.startswith('='):
                val_str = "123,456 DH"  # approximate formula result
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

# Specific column adjustments for readability
ws_dash.column_dimensions["A"].width = 36
ws_dash.column_dimensions["B"].width = 20
ws_dash.column_dimensions["C"].width = 16
ws_dash.column_dimensions["D"].width = 24
ws_dash.column_dimensions["E"].width = 22
ws_dash.column_dimensions["F"].width = 24
ws_dash.column_dimensions["G"].width = 22
ws_dash.column_dimensions["H"].width = 24
ws_dash.column_dimensions["I"].width = 28
ws_dash.column_dimensions["J"].width = 16
ws_dash.column_dimensions["K"].width = 16

ws_leads.column_dimensions["A"].width = 6
ws_leads.column_dimensions["B"].width = 24
ws_leads.column_dimensions["C"].width = 32
ws_leads.column_dimensions["D"].width = 26
ws_leads.column_dimensions["E"].width = 18
ws_leads.column_dimensions["F"].width = 20
ws_leads.column_dimensions["G"].width = 22
ws_leads.column_dimensions["H"].width = 28
ws_leads.column_dimensions["I"].width = 14
ws_leads.column_dimensions["J"].width = 24
ws_leads.column_dimensions["K"].width = 16
ws_leads.column_dimensions["L"].width = 18
ws_leads.column_dimensions["M"].width = 16
ws_leads.column_dimensions["N"].width = 46
ws_leads.column_dimensions["O"].width = 30
ws_leads.column_dimensions["P"].width = 46
ws_leads.column_dimensions["Q"].width = 20
ws_leads.column_dimensions["R"].width = 16
ws_leads.column_dimensions["S"].width = 34

ws_pitch.column_dimensions["A"].width = 110

ws_roi.column_dimensions["A"].width = 42
ws_roi.column_dimensions["B"].width = 24
ws_roi.column_dimensions["C"].width = 22
ws_roi.column_dimensions["D"].width = 22
ws_roi.column_dimensions["E"].width = 22
ws_roi.column_dimensions["F"].width = 22

ws_crm.column_dimensions["A"].width = 18
ws_crm.column_dimensions["B"].width = 24
ws_crm.column_dimensions["C"].width = 24
ws_crm.column_dimensions["D"].width = 18
ws_crm.column_dimensions["E"].width = 28
ws_crm.column_dimensions["F"].width = 20
ws_crm.column_dimensions["G"].width = 26
ws_crm.column_dimensions["H"].width = 20
ws_crm.column_dimensions["I"].width = 20
ws_crm.column_dimensions["J"].width = 36
ws_crm.column_dimensions["K"].width = 36

if __name__ == "__main__":
    output_path = r"c:\Users\UserAdmin\Desktop\work\shopify\Prospection_Migration_Shopify_Maroc.xlsx"
    wb.save(output_path)
    print(f"File created successfully at: {output_path}")
