"""
Skill: Shopify Headless Catalog Harvester
Extracts real product data, high-resolution imagery, and pricing from
the merchant's public Shopify endpoints (/products.json) with intelligent
niche-tailored fallbacks.
"""

import json
import re
import urllib.request
import urllib.error

def harvest_shopify_catalog(target_url: str, brand_name: str, archetype: str, niche: str) -> dict:
    """Harvests real products from public Shopify endpoints or generates archetype-tailored inventory."""
    catalog_products = []
    
    # 1. Attempt live /products.json retrieval
    clean_url = target_url.rstrip("/")
    api_url = f"{clean_url}/products.json?limit=12"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                raw_products = data.get("products", [])
                for idx, p in enumerate(raw_products[:8]):
                    variants = p.get("variants", [{}])
                    first_var = variants[0] if variants else {}
                    raw_price = first_var.get("price", "499")
                    price_mad = int(float(raw_price))
                    compare_price = first_var.get("compare_at_price")
                    orig_mad = int(float(compare_price)) if compare_price else None
                    
                    images = p.get("images", [])
                    img_src = images[0].get("src") if images else "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80"
                    
                    # Clean html from description
                    raw_desc = p.get("body_html", "") or p.get("title", "")
                    clean_desc = re.sub(r'<[^>]+>', ' ', raw_desc).strip()
                    clean_desc = re.sub(r'\s+', ' ', clean_desc)[:160] + "..." if len(clean_desc) > 160 else clean_desc
                    
                    catalog_products.append({
                        "id": p.get("handle") or f"product-{idx+1}",
                        "name": p.get("title", f"Produit {idx+1}"),
                        "subtitle": p.get("product_type") or brand_name,
                        "category": p.get("product_type") or "Collection Signature",
                        "priceMad": price_mad,
                        "originalPriceMad": orig_mad,
                        "image": img_src,
                        "badge": "BESTSELLER" if idx == 0 else "LIVRAISON 24H",
                        "description": clean_desc or p.get("title", ""),
                        "stockLeft": None
                    })
    except Exception:
        pass # Fall through to archetype-curated catalog

    if not catalog_products:
        catalog_products = get_archetype_catalog(archetype, brand_name)
        source = "niche_curated_fallback"
    else:
        source = "live_shopify_api"

    return {
        "count": len(catalog_products),
        "products": catalog_products,
        "categories": list(set(p.get("category", "Général") for p in catalog_products)),
        "source": source
    }

def get_archetype_catalog(archetype: str, brand_name: str) -> list:
    """Provides authentic, category-specific curated inventory with real imagery and realistic Moroccan MAD prices."""
    if archetype == "tech_gadgets":
        return [
            {
                "id": "dashcam-omni-4k-360",
                "name": f"{brand_name} Dashcam Omni 360° 4K HDR",
                "subtitle": "Capteur Sony Starvis 2 • Surveillance Parking 24/7 & IA Détection",
                "category": "Dashcams 4K",
                "priceMad": 1490,
                "originalPriceMad": 1890,
                "badge": "BESTSELLER CASABLANCA",
                "image": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=800&q=80",
                "description": "La référence absolue des caméras embarquées au Maroc. Rotation motorisée à 360°, vision nocturne HDR exceptionnelle et enregistrement automatique en cas de choc en stationnement.",
                "stockLeft": 4
            },
            {
                "id": "dashcam-a810-dual-vision",
                "name": f"{brand_name} Dual Vision Avant & Arrière 4K",
                "subtitle": "Pack Caméra Avant 4K + Caméra Arrière 1080P & GPS Intégré",
                "category": "Packs Sécurité",
                "priceMad": 1850,
                "originalPriceMad": 2200,
                "badge": "PACK DUO AVANT/ARRIÈRE",
                "image": "https://images.unsplash.com/photo-1508974239320-0a029497e820?auto=format&fit=crop&w=800&q=80",
                "description": "Protection intégrale à l'avant et à l'arrière de votre véhicule. Angle ultra-large 170°, alerte franchissement de ligne et sauvegarde cloud d'urgence.",
                "stockLeft": 2
            },
            {
                "id": "hardwire-kit-parking-24h",
                "name": "Kit Câblage Parking 24/7 Hardwire Kit",
                "subtitle": "Câblage direct boîte à fusibles avec protection anti-décharge batterie",
                "category": "Accessoires & Câblage",
                "priceMad": 249,
                "originalPriceMad": 350,
                "badge": "INSTALLATION DISPO",
                "image": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80",
                "description": "Permet à votre dashcam de filmer en continu lorsque le moteur est éteint sans jamais vider la batterie de votre voiture.",
                "stockLeft": 7
            }
        ]
    elif archetype == "fashion_streetwear":
        return [
            {
                "id": "mocassin-cuir-artisan-cognac",
                "name": f"{brand_name} Mocassin Cuir Souple Cognac",
                "subtitle": "Cuir de Vachette Pleine Fleur & Semelle Ergonomique Cousue",
                "category": "Chaussures Cuir",
                "priceMad": 480,
                "originalPriceMad": 650,
                "badge": "ESSAYEZ AVANT DE PAYER",
                "image": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?auto=format&fit=crop&w=800&q=80",
                "description": "Le mocassin signature façonné à la main. Cuir ultra-souple qui épouse la forme du pied, semelle intérieure en mousse mémoire de forme.",
                "stockLeft": 5
            },
            {
                "id": "sneaker-cuir-blanc-minimal",
                "name": f"{brand_name} Sneaker Classic Cuir Blanc",
                "subtitle": "Baskets Urbaines Finition Nubuck & Doublure Respirante",
                "category": "Baskets Urbaines",
                "priceMad": 520,
                "originalPriceMad": 690,
                "badge": "LIVRAISON 24H",
                "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=800&q=80",
                "description": "L'indispensable du vestiaire contemporain. Lignes épurées, cuir résistant aux intempéries et semelle cousue 360° pour une durabilité maximale.",
                "stockLeft": 3
            },
            {
                "id": "derbies-cuir-noir-prestige",
                "name": f"{brand_name} Soulier Derby Cuir Noir Mat",
                "subtitle": "Souliers de Cérémonie & Travail • Montage Cousu Goodyear",
                "category": "Souliers Habillés",
                "priceMad": 550,
                "originalPriceMad": 720,
                "badge": "ÉLÉGANCE CASABLANCA",
                "image": "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?auto=format&fit=crop&w=800&q=80",
                "description": "L'élégance formelle à son apogée. Cuir noir lustré à la cire d'abeille naturelle, parfait pour les réunions d'affaires et grandes occasions.",
                "stockLeft": 4
            }
        ]
    elif archetype == "artisanal_craft":
        return [
            {
                "id": "plat-service-ceramique-or",
                "name": f"{brand_name} Plat de Service Céramique & Rayures Or",
                "subtitle": "Argile Rouge Façonnée au Tour & Peinte à la Main à Marrakech",
                "category": "Art de la Table",
                "priceMad": 390,
                "originalPriceMad": 490,
                "badge": "PIÈCE UNIQUE FAIT MAIN",
                "image": "https://images.unsplash.com/photo-1615529182904-14819c35db37?auto=format&fit=crop&w=800&q=80",
                "description": "Une création artisanale d'exception. Émail sans plomb alimentaire rehaussé d'or 12 carats déposé au pinceau fin.",
                "stockLeft": 3
            },
            {
                "id": "service-tasses-cafe-beldi",
                "name": f"{brand_name} Set de 6 Tasses Beldi & Soucoupes",
                "subtitle": "Céramique Artisanale Finition Mate & Liseré Or",
                "category": "Café & Thé",
                "priceMad": 320,
                "originalPriceMad": 420,
                "badge": "COFFRET CADEAU",
                "image": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80",
                "description": "Sublimez votre rituel du café marocain. Chaque tasse est tournée à la main et présente de subtiles variations qui en font le charme authentique.",
                "stockLeft": 6
            }
        ]
    elif archetype == "beauty_cosmetics":
        return [
            {
                "id": "serum-argan-figue-barbarie",
                "name": f"{brand_name} Sérum Précieux Argan & Figue de Barbarie",
                "subtitle": "100% Pur Bio Pressé à Froid • Anti-Âge & Éclat Instantané",
                "category": "Soins Visage",
                "priceMad": 280,
                "originalPriceMad": 380,
                "badge": "RÉSULTATS 14 JOURS",
                "image": "https://images.unsplash.com/photo-1608248597359-299e5a52233f?auto=format&fit=crop&w=800&q=80",
                "description": "Concentré botanique d'exception riche en vitamine E et stérols naturels. Régénère la peau pendant la nuit et lisse les ridules d'expression.",
                "stockLeft": 5
            },
            {
                "id": "masque-cheveux-botanique",
                "name": f"{brand_name} Masque Réparateur Intense Romarin & Argan",
                "subtitle": "Soin Fortifiant Sans Sulfate pour Cheveux Abîmés",
                "category": "Soins Cheveux",
                "priceMad": 190,
                "originalPriceMad": 260,
                "badge": "98% SATISFACTION",
                "image": "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=800&q=80",
                "description": "Nourrit la fibre capillaire en profondeur dès la première application. Stimule la pousse et prévient la casse.",
                "stockLeft": 8
            }
        ]
    elif archetype == "health_medical":
        return [
            {
                "id": "glucometre-connecte-smart",
                "name": f"{brand_name} Kit Lecteur Glycémie Sans Piqûre Continue",
                "subtitle": "Capteur Connecté Bluetooth • Alerte Hypoglycémie & Suivi Smartphone",
                "category": "Surveillance Diabète",
                "priceMad": 850,
                "originalPriceMad": 1100,
                "badge": "NORME CE CERTIFIÉE",
                "image": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=800&q=80",
                "description": "Suivi du taux de glucose en temps réel 24h/24 sans piqûre au bout du doigt. Application mobile en français et assistance téléphonique.",
                "stockLeft": 3
            }
        ]
    elif archetype == "luxury_horlogerie":
        return [
            {
                "id": "chronographe-automatique-calibre16",
                "name": f"{brand_name} Chronographe Automatique Calibre 16",
                "subtitle": "Boîtier Acier 904L 42mm • Verre Saphir Antireflet Double Face",
                "category": "Chronomètres de Précision",
                "priceMad": 3200,
                "originalPriceMad": 3900,
                "badge": "BESTSELLER EXÉCUTIF",
                "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
                "description": "Chronomètre de haute précision avec mouvement automatique calibre 16 suisse. Étanche 100 mètres, cadran ardoise brossé soleil et compteurs azurés.",
                "specs": {"calibre": "Automatique 28,800 vph", "boitier": "Acier Noble 904L 42mm", "verre": "Saphir Inrayable", "etancheite": "10 ATM / 100M"},
                "stockLeft": 3
            },
            {
                "id": "montre-squelette-titane-tourbillon",
                "name": f"{brand_name} Squelette Titane Tourbillon Grade 5",
                "subtitle": "Architecture Squelette Aérienne & Réserve de Marche 72h",
                "category": "Grandes Complications",
                "priceMad": 4800,
                "originalPriceMad": 5800,
                "badge": "ÉDITION LIMITÉE 50 PCS",
                "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=800&q=80",
                "description": "Chef-d'œuvre d'ingénierie contemporaine. Platine et ponts en titane grade 5 évidés au micron, balancier visible et fond transparent en verre saphir.",
                "specs": {"calibre": "Squelette Manuel 72h", "boitier": "Titane Satiné 43mm", "verre": "Double Saphir Traité", "etancheite": "5 ATM / 50M"},
                "stockLeft": 1
            },
            {
                "id": "plongeuse-pro-lunette-ceramique",
                "name": f"{brand_name} Plongeuse Professionnelle 300M Céramique",
                "subtitle": "Lunette Tournante Unidirectionnelle Cerachrom & Valve Hélium",
                "category": "Plongeuses Professionnelles",
                "priceMad": 2400,
                "originalPriceMad": 2900,
                "badge": "GARANTIE 2 ANS",
                "image": "https://images.unsplash.com/photo-1547996160-71dfabb1a7b1?auto=format&fit=crop&w=800&q=80",
                "description": "Instrument de plongée par excellence. Lunette céramique inaltérable, index luminescents Super-LumiNova BGW9 haute visibilité sous-marine.",
                "specs": {"calibre": "Automatique 4Hz", "boitier": "Acier Brossé 41mm", "verre": "Saphir 3.5mm", "etancheite": "30 ATM / 300M"},
                "stockLeft": 4
            },
            {
                "id": "classic-dress-watch-sunray",
                "name": f"{brand_name} Classic Elegance Cadran Bleu Sunray",
                "subtitle": "Profil Ultra-Fin 8.5mm & Bracelet Cuir d'Alligator Cousu Main",
                "category": "Classiques Éléganz",
                "priceMad": 1850,
                "originalPriceMad": 2250,
                "badge": "LIVRAISON 24H",
                "image": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=800&q=80",
                "description": "Le raffinement discret sous la chemise de costume. Aiguilles dauphines polies miroir, guichet dateur biseauté et boucle ardillon siglée.",
                "specs": {"calibre": "Automatique Ultra-Fin", "boitier": "Acier 316L 39mm", "verre": "Saphir Bombé", "etancheite": "5 ATM / 50M"},
                "stockLeft": 5
            }
        ]
    else: # luxury_joaillerie / luxury_prestige
        return [
            {
                "id": "solitaire-diamant-eternel-or18k",
                "name": f"{brand_name} Bague Solitaire Diamant Éternel Or 18K",
                "subtitle": "Diamant Brillant Naturel 0.70 Ct Certifié GIA & Poinçon d'État",
                "category": "Haute Joaillerie & Solitaires",
                "priceMad": 3400,
                "originalPriceMad": 4200,
                "badge": "CERTIFICAT GIA INCLUS",
                "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&q=80",
                "description": "L'incarnation de la promesse éternelle. Or blanc 750 millièmes rhodié, serti 4 griffes mettant en valeur un diamant de pureté exceptionnelle.",
                "specs": {"or": "18 Carats / 750‰", "pierre": "Diamant Naturel 0.70 Ct", "taille": "Brillant Rond", "ecrin": "Velours Royal Offert"},
                "stockLeft": 2
            },
            {
                "id": "bracelet-riviere-diamants-or-blanc",
                "name": f"{brand_name} Bracelet Rivière Tennis Or Blanc 18K",
                "subtitle": "Pavage Continu 55 Diamants Taille Brillant & Fermoir Sécurité",
                "category": "Bracelets Haute Joaillerie",
                "priceMad": 4800,
                "originalPriceMad": 5900,
                "badge": "PIÈCE MAÎTRESSE",
                "image": "https://images.unsplash.com/photo-1611591475152-47eac9407db5?auto=format&fit=crop&w=800&q=80",
                "description": "Un ruban de lumière fluide au poignet. Confectionné à la main avec fermoir cliquet à double huit de sécurité pour une tenue parfaite.",
                "specs": {"or": "18 Carats / 750‰", "pavage": "55 Diamants 2.5 Ct Total", "fermoir": "Double Sécurité", "ecrin": "Coffret Prestige"},
                "stockLeft": 1
            },
            {
                "id": "collier-pendentif-emeraude-royale",
                "name": f"{brand_name} Collier Pendentif Émeraude Royale & Or Jaune",
                "subtitle": "Émeraude Ovale Poire Naturelle & Chaîne Maille Forçat Or 18K",
                "category": "Colliers & Pierres Précieuses",
                "priceMad": 2650,
                "originalPriceMad": 3200,
                "badge": "COUP DE CŒUR",
                "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80",
                "description": "Le vert impérial d'une émeraude de Colombie entourée d'un délicat halo de diamants taille brillant sur or jaune 18 carats.",
                "specs": {"or": "Or Jaune 18 Carats", "pierre": "Émeraude Naturelle 1.2 Ct", "chaine": "42cm Réglable", "ecrin": "Velours Vert Forêt"},
                "stockLeft": 3
            },
            {
                "id": "bague-saphir-ceylan-pavage",
                "name": f"{brand_name} Bague Saphir Bleu Ceylan & Pavage Diamants",
                "subtitle": "Saphir Ovale Bleu Intense 1.5 Ct & Corps de Bague Or Blanc",
                "category": "Bagues Cocktail & Cadeaux",
                "priceMad": 1950,
                "originalPriceMad": 2500,
                "badge": "ESSAYAGE À DOMICILE",
                "image": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&w=800&q=80",
                "description": "L'éclat royal du saphir de Ceylan mis en majesté par un pavage latéral en diamants étincelants. Un présent inoubliable.",
                "specs": {"or": "18 Carats / 750‰", "pierre": "Saphir Ceylan 1.5 Ct", "poids": "3.8g", "ecrin": "Écrin Cadeau Offert"},
                "stockLeft": 4
            }
        ]
