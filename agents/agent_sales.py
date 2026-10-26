"""
Agent 7: Sales Enablement Writer
Drafts evidence-backed, respectful sales outreach in French and Moroccan Darija
directly referencing the technical audit findings, live demo URL, and financial ROI.
"""

import os
import re
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

def _run_sales_legacy(lead_id: str, workspace: str, brand_name: str, target_url: str):
    raise RuntimeError("Legacy outreach with synthetic claims has been disabled")
    sales_dir = os.path.join(workspace, "sales")
    os.makedirs(sales_dir, exist_ok=True)

    fr_path = os.path.join(sales_dir, "outreach_fr.md")
    darija_path = os.path.join(sales_dir, "outreach_darija.md")

    # Load lead metadata
    lead_file = os.path.join(workspace, "lead.json")
    lead_data = {}
    if os.path.exists(lead_file):
        try:
            with open(lead_file, "r", encoding="utf-8") as lf:
                lead_data = json.load(lf)
        except Exception:
            pass

    contacts = lead_data.get("contacts", {})
    wa_phone = contacts.get("whatsapp") or "+212 6 45 22 20 09"
    wa_clean = re.sub(r'[^0-9]', '', wa_phone)
    contact_email = contacts.get("email") or "mamontre.ma@gmail.com"

    is_watch = "montre" in lead_id.lower() or "montre" in brand_name.lower() or "horloger" in lead_data.get("category", "").lower()
    product_focus = "l'horlogerie et les montres de prestige (Rolex Datejust, Wimbledon, GMT Master II)" if is_watch else "la bijouterie fine et joaillerie en or 18k et argent"
    items_fr = "vos montres" if is_watch else "vos bijoux"
    items_darija = "les montres dyalkom (Wimbledon, GMT Master, Datejust)" if is_watch else "les bijoux dyalkom"

    # Financial figures
    saas_usd = 150 if is_watch else 180
    annual_saas_mad = saas_usd * 10 * 12
    annual_tx_mad = 36000
    total_savings_mad = annual_saas_mad + annual_tx_mad
    three_year_savings = total_savings_mad * 3

    # Load deployment manifest for verified live demo and GitHub repo
    manifest_path = os.path.join(workspace, "deployment", "deployment_manifest.json")
    slug = lead_id.lower().replace('_', '-').replace(' ', '-')
    while '--' in slug:
        slug = slug.replace('--', '-')
    slug = slug.strip('-')
    if not slug.endswith('-demo'):
        slug = f"{slug}-demo"

    demo_url = f"https://{slug}.vercel.app"
    gh_repo = f"https://github.com/e-commerce-refactor/{slug}"

    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as mf:
                mdata = json.load(mf)
                demo_url = mdata.get("vercel", {}).get("production_url") or demo_url
                gh_repo = mdata.get("github", {}).get("repository") or gh_repo
        except Exception:
            pass

    # 1. French Outreach (Executive Email / Formal WhatsApp)
    fr_content = f"""# ✉️ Email d'Approche Exécutive — {brand_name}

**Destinataire :** Fondateur & Direction E-commerce — {brand_name}  
**Email :** {contact_email}  
**Téléphone / WhatsApp :** {wa_phone}  
**Objet :** {brand_name} — Économisez {total_savings_mad:,} DH/an sur Shopify et propulsez vos ventes de montres (Score 98/100)

---

Bonjour [Nom du Dirigeant / Équipe Dirigeante],

Félicitations pour le rayonnement d'**{brand_name}** sur le marché marocain. Vos collections d'exception ({product_focus}) témoignent d'un véritable souci du détail et de la satisfaction client.

En réalisant un audit technique approfondi de votre boutique en ligne ([{target_url.replace('https://', '')}]({target_url})), nous avons identifié **3 freins structurels majeurs liés à Shopify** qui pénalisent directement votre marge nette et vos budgets publicitaires :

### 1. Fuite de devises : {annual_saas_mad:,} DH/an prélevés sur votre Dotation E-commerce
Entre l'abonnement Shopify et vos applications tierces (notamment l'extension **Releasit / EasySell COD Form**), vous réglez environ **${saas_usd} USD par mois** sur votre carte bancaire internationale. Cela épuise inutilement votre quota officiel de dotation e-commerce au détriment de vos campagnes publicitaires Meta et TikTok Ads indispensables pour acquérir de nouveaux clients.

### 2. Pénalité de 2.0% sur le Cash-on-Delivery (environ 36 000 DH/an de perte)
En l'absence de passerelle *Shopify Payments* au Maroc, Shopify prélève une commission de transaction sur chaque commande livrée en espèces. Pour un volume mensuel de 150 000 DH, cela représente **3 000 DH/mois de royalties payées à Shopify sans contrepartie**.

### 3. Lenteur Mobile (Score PageSpeed de 38/100 sur 4G Maroc)
L'accumulation de scripts tiers crée un temps de latence de **4.1 secondes** sur smartphone. Or, 85% de vos acheteurs découvrent {items_fr} via Instagram ou TikTok sur leur mobile. Chaque seconde d'attente vous coûte entre 15% et 25% de vos ventes.

---

### Notre Proposition : Votre Boutique Propriétaire Ultra-Rapide (Next.js 14)

Nous avons développé une démonstration exclusive et déjà déployée en direct sous **technologie Next.js ultra-rapide**, taillée sur-mesure pour votre marque :
- 🔗 **Démonstration en direct** : [{demo_url}]({demo_url})
- 💻 **Code source et architecture vérifiée** : [{gh_repo}]({gh_repo})
- ✅ **0 DH d'abonnement en devises** : Vous êtes 100% propriétaire de votre plateforme à vie.
- ✅ **Formulaire COD 1-Clic Natif** : Remplacement immédiat de Releasit sans script lourd, avec sélecteur de villes marocaines et confirmation WhatsApp instantanée.
- ✅ **Vitesse Maximale (Score 98/100)** : Affichage instantané en moins de 0.8 seconde pour maximiser la rentabilité de vos publicités.
- ✅ **Gain Financier Net** : Un investissement unique amorti en moins de 5 mois, générant **plus de {three_year_savings:,} DH d'économies nettes sur 3 ans**.

Seriez-vous disponible pour un échange visio ou WhatsApp de 10 minutes cette semaine afin de découvrir la démo interactive de votre futur site et les détails de l'audit ?

Bien cordialement,

**[Votre Nom / Votre Agence]**  
Spécialiste de la modernisation e-commerce pour marques marocaines  
WhatsApp direct : [{wa_phone}](https://wa.me/{wa_clean})

*(Si vous ne souhaitez plus recevoir de messages de notre part, répondez simplement "STOP" et nous retirerons immédiatement vos coordonnées de notre fichier).*
"""

    with open(fr_path, "w", encoding="utf-8") as f:
        f.write(fr_content)
    fr_sha = hash_file(fr_path)

    # 2. Moroccan Darija Outreach (WhatsApp Message & Voice Note Script)
    darija_content = f"""# 💬 Script WhatsApp & Note Vocale Darija — {brand_name}

**Numéro WhatsApp Cible :** `{wa_phone}`  
**Lien d'ouverture directe :** [Ouvrir WhatsApp](https://wa.me/{wa_clean}?text=Salam%20{brand_name.replace(' ', '%20')})  
**Ton :** Professionnel, direct, respectueux, orienté rentabilité et fierté marocaine.

---

## Format 1 : Premier Message Texte WhatsApp

Salam Si [Prénom du Gérant] / L'équipe de **{brand_name}**,

Tbarkellah 3likom, {items_darija} w le positionnement f Casablanca top !

Kanchouf bli le site dyalkom **{target_url.replace('https://', '')}** khddam b Shopify w m-installiyin fih l'application **Releasit / EasySell COD** pour le paiement à la livraison.

Derte un audit technique rapide 3la le site dyalkom, w bghit n-werik 3 dyal les points li kaydiyo likom flouss kbiira kol chher :

1️⃣ **Dotation e-commerce** : Katkhellso environ **{saas_usd*10:,} DH/mois b dollars** (${saas_usd}/m) bin l'abonnement Shopify w l'appli COD. Hadchi kay-akol likom le plafond dyal la carte e-commerce li khtajito l les pubs Instagram/TikTok.  
2️⃣ **2% de pénalité 3la le COD** : Hit makaynch Shopify Payments f l-Meghrib, Shopify kayakhod likom 2% 3la kol commande khellasha l-client b l'espèce (environ **36 000 DH par an** dyal les frais zaydin).  
3️⃣ **Le site t9il 3la l-mobile (Score 38/100)** : Kayakhod 4 secondes bach y-t7ell f réseau 4G hit fih 25 scripts d'applications, w hadchi kaytiyyah likom le taux de conversion dyal les annonces.

---

### Chno le hall ?

7na kan-sowbo des sites web e-commerce sur-mesure (b technologie **Next.js** moderne) :
✅ **Zéro abonnement mensuel en devises** (site dyalkom pour toujours).
✅ **Checkout COD 1-clic** natif w khafif (< 1 seconde) bla Releasit w bla bugs.
✅ **Confirmation automatique par WhatsApp** m3a les clients dyalkom.
✅ **Économie de plus de {total_savings_mad:,} DH par an.**

Wجدنا likom une **démo interactive** déjà déployée en ligne spécialement pour {brand_name} :  
👉 **Lien de la démo :** {demo_url}  
👉 **Code source vérifié :** {gh_repo}

Wach 3ndkom 10 d9ayeq had le weekend n-weriwha likom f un appel WhatsApp rapide ?

Merci bzzaf w tbarkellah 3likom !

---

## Format 2 : Script Note Vocale WhatsApp (45 secondes)

> *"Salam Si [Prénom], labas 3lik ? Nchallah tkoun bikhir. Maak [Votre Nom].*  
> *Kanchouf l-khedma nqiyya li kadirou f {brand_name} f Casa, tbarkellah 3likom.*  
> *Gha howa derte un audit technique l-bareh 3la le site dyalkom {target_url.replace('https://', '')}, w ban liya bli Shopify kayakhod likom plus de {total_savings_mad:,} DH f l-3am bin les abonnements en dollars (${saas_usd}/mois) w les commissions dyal 2% 3la le Cash on Delivery.*  
> *Sowebt likom une maquette Next.js khfifa bzzaf, kat-t7ell f 0.5 seconde w فيها formulaire COD 1-clic bla abonnement mensuel avec vos montres Wimbledon et GMT Master.*  
> *L-lien dyalha howa {demo_url}. Si vous êtes disponible, n-sefet lik les détails bach tchoufouha f tlphoune dyalkom ? Lah ywefeq !"*
"""

    with open(darija_path, "w", encoding="utf-8") as f:
        f.write(darija_content)
    darija_sha = hash_file(darija_path)

    handoff = {
        "status": "passed",
        "summary": f"Agent 7 (Sales Writer) drafted hyper-personalized French and Moroccan Darija outreach referencing exact audit evidence for {brand_name}.",
        "artifacts": [
            {"path": f"leads/{lead_id}/sales/outreach_fr.md", "schema_version": "1.0", "sha256": fr_sha},
            {"path": f"leads/{lead_id}/sales/outreach_darija.md", "schema_version": "1.0", "sha256": darija_sha}
        ],
        "evidence": [
            {"source": f"leads/{lead_id}/audit/audit_report.json", "collected_at": utc_now_iso(), "method": "sales_copywriting", "confidence": "high"}
        ],
        "assumptions": [
            f"Outreach addresses business founder/manager on verified WhatsApp channel ({wa_phone})"
        ],
        "risks": [
            "Human in the loop approval required prior to actually transmitting the drafted message"
        ],
        "blockers": [],
        "gate_results": [
            {"criterion": "Strict factual attribution", "result": "pass", "details": f"Claims directly derived from audit report ({annual_saas_mad:,} DH devises + 36,000 DH COD penalty)"},
            {"criterion": "Bilingual enablement", "result": "pass", "details": "Executive French and high-impact Darija WhatsApp script created"},
            {"criterion": "Safety opt-out present", "result": "pass", "details": "Professional STOP opt-out included in French template"}
        ],
        "recommended_next_action": "Workflow complete: Await human approval to schedule client outreach"
    }

    return handoff


def run_sales(lead_id: str, workspace: str, brand_name: str, target_url: str):
    """Draft outreach using only claims present in the evidence-backed audit."""
    sales_dir = os.path.join(workspace, "sales")
    os.makedirs(sales_dir, exist_ok=True)
    fr_path = os.path.join(sales_dir, "outreach_fr.md")
    darija_path = os.path.join(sales_dir, "outreach_darija.md")

    def load_json(path):
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    lead = load_json(os.path.join(workspace, "lead.json"))
    audit = load_json(os.path.join(workspace, "audit", "audit_report.json"))
    manifest = load_json(os.path.join(workspace, "deployment", "deployment_manifest.json"))
    observations = audit.get("findings", [])
    financial = audit.get("financial_analysis", {})
    measured = audit.get("measured_storefront_facts", {})
    contacts = lead.get("contacts", {})
    recipient = contacts.get("email") or contacts.get("whatsapp") or "À compléter après vérification du contact"

    smoke_verified = any(test.get("verified") for test in manifest.get("smoke_tests", []))
    demo_url = manifest.get("vercel", {}).get("production_url") if smoke_verified else None
    repo_url = manifest.get("github", {}).get("repository") if smoke_verified else None
    observations_md = "\n".join(f"- {item}" for item in observations) or "- Aucun constat suffisamment étayé."
    financial_md = ""
    if financial.get("status") == "calculated_from_user_inputs":
        financial_md = f"\n- Scénario financier calculé à partir des chiffres fournis : **{financial['annual_total_mad']:,.2f} MAD/an**."
    demo_md = f"\n- Démo vérifiée : {demo_url}\n- Dépôt : {repo_url}" if demo_url and repo_url else "\n- Le lien de démonstration sera ajouté après vérification technique."

    fr_content = f"""# Brouillon d'approche — {brand_name}

**Destinataire :** {recipient}
**Objet :** Observations techniques vérifiables sur {brand_name}

Bonjour,

Nous avons examiné les éléments publics de votre boutique {target_url}. Voici uniquement les observations que notre capture permet de vérifier :

{observations_md}{financial_md}

Nous n'avons pas mesuré Lighthouse, les Core Web Vitals, votre chiffre d'affaires ou votre taux de conversion ; ce brouillon ne formule donc aucune promesse sur ces points.

Nous avons préparé une proposition de storefront moderne adaptée au paiement à la livraison.{demo_md}

Si le sujet vous intéresse, seriez-vous disponible pour un échange court afin de valider vos contraintes réelles avant toute recommandation chiffrée ?

Bien cordialement,

[Votre nom / agence]

*(Répondez « STOP » si vous ne souhaitez plus être contacté.)*
"""
    darija_content = f"""# Brouillon WhatsApp Darija — {brand_name}

Salam, derna wahed l'analyse limitée ghir l-ma3loumat publiques dyal {target_url}.

Li tqderna n-verifiw:
{observations_md}

Ma qissnach PageSpeed/Core Web Vitals, chiffre d'affaires, conversion, wala économies; donc ma kan3tiw ta wa3d chiffré bla données dyalkom.{demo_md}

Ila l-mawdo3 kayhemmkom, n9dro ndiro appel qsir bach nefhmou les contraintes dyalkom qbel ay recommandation.

Ila ma bghitouch messages okhrin, jawbou « STOP ».
"""
    with open(fr_path, "w", encoding="utf-8") as f:
        f.write(fr_content)
    with open(darija_path, "w", encoding="utf-8") as f:
        f.write(darija_content)

    evidence_quality = audit.get("evidence_quality")
    status = "passed" if evidence_quality == "verified_live_capture" else "blocked"
    blockers = [] if status == "passed" else ["Sales copy requires a verified live audit"]
    return {
        "status": status,
        "summary": f"Drafted evidence-bounded French and Darija outreach for {brand_name}.",
        "artifacts": [
            {"path": f"leads/{lead_id}/sales/outreach_fr.md", "schema_version": "2.0", "sha256": hash_file(fr_path)},
            {"path": f"leads/{lead_id}/sales/outreach_darija.md", "schema_version": "2.0", "sha256": hash_file(darija_path)},
        ],
        "evidence": [{"source": f"leads/{lead_id}/audit/audit_report.json", "collected_at": utc_now_iso(), "method": "bounded_claim_copywriting", "confidence": "high" if status == "passed" else "low"}],
        "assumptions": [],
        "risks": ["Draft must be reviewed by a human before outreach"],
        "blockers": blockers,
        "gate_results": [
            {"criterion": "Claims trace to audit", "result": "pass" if status == "passed" else "fail", "details": f"audit evidence quality={evidence_quality}"},
            {"criterion": "No synthetic performance or savings claims", "result": "pass", "details": f"script_count={measured.get('external_script_count')}"},
            {"criterion": "Opt-out present", "result": "pass", "details": "STOP instruction included in both drafts"},
        ],
        "recommended_next_action": "Human review required before any outreach" if status == "passed" else "Acquire verified audit evidence before drafting outreach",
    }
