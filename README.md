# 🚀 Global Shopify E-Commerce Modernization Orchestrator

An enterprise agentic orchestrator designed to assess, audit, prototype, and migrate Shopify stores to high-performance, independent Next.js 14 platforms tailored for localized Cash-on-Delivery (COD) emerging markets (Morocco).

---

## 🌟 Key Capabilities

1. **6 Distinct E-Commerce Design Archetypes:**
   - **Tech & High-Performance Gadgets** (HUD Cockpit, laser scan keyframe, video demos)
   - **Streetwear, Apparel & Footwear** (Brutalist kinetic marquee, lookbook masonry, bottom drawer)
   - **Artisanal Terroir, Leather & Lifestyle** (Tactile stamp bounce, warm organic tones, artisan story)
   - **Beauty, Skincare & Organic Wellness** (Dewy glow, routine grids, ingredient trust badges)
   - **Health, Medical Devices & Care** (Clinical clarity, certified authority, discrete COD ordering)
   - **Haute Horlogerie & Joaillerie** (Swiss prestige, 18K gold luster shimmer, tourbillon motion)

2. **Social OSINT & Intelligence Extractor:**
   - Automatically harvests authentic Instagram & Facebook bio taglines, follower counts, and real customer claims (e.g., *« Essayez avant de payer »*).
   - Injects interactive **Instagram Stories Highlight bars** and UGC community walls.

3. **Shopify Native Headless Catalog Harvester:**
   - Automatically harvests products, pricing in MAD, and high-res imagery directly from public Shopify `/products.json` endpoints.

4. **GPU-Accelerated Native Motion Engine:**
   - 60fps CSS keyframes injected directly into `tailwind.config.js` with **zero runtime JavaScript bundle bloat** to guarantee >92/100 PageSpeed on 4G networks.

5. **Complete Lifecycle in One Go:**
   - One-command execution: Intake $\rightarrow$ Discovery $\rightarrow$ Audit $\rightarrow$ Solution $\rightarrow$ Build $\rightarrow$ QA $\rightarrow$ Deployment $\rightarrow$ Sales Outreach.
   - Live automated provisioning on **GitHub**, **Supabase** (PostgreSQL orders database), and **Vercel Edge**.

---

## 🛠 Quickstart CLI Commands

```bash
# Run complete lifecycle in one go (by business number or ID)
python orchestrator.py run-all 1
# or
python orchestrator.py run-all 70mai_Maroc

# Assess a new store (creates leads/<Business_Name>/)
python orchestrator.py Assess https://flexshoes.ma "Flex Shoes"

# Step-by-step specialist agent execution:
python orchestrator.py "Discover 70mai_Maroc"
python orchestrator.py "Audit 70mai_Maroc"
python orchestrator.py "Plan solution 70mai_Maroc"
python orchestrator.py "Build demo 70mai_Maroc"
python orchestrator.py "Verify QA 70mai_Maroc"
python orchestrator.py "Prepare deployment 70mai_Maroc"
python orchestrator.py "Deploy 70mai_Maroc --approved"
python orchestrator.py "Draft outreach 70mai_Maroc"

# View tracked leads and pipeline stage status
python orchestrator.py list
python orchestrator.py status 70mai_Maroc
```

---

## 📂 Architecture & Specialist Subagents

| Subagent | Identifier | Mission & Deliverables |
| :--- | :--- | :--- |
| **Agent 0** | `agent_intake` | Target scope, governance, permissions (`lead.json`, `run.json`) |
| **Agent 1** | `agent_discovery` | Public evidence, headless catalog, social OSINT (`brand_dossier.json`, `social_dossier.json`) |
| **Agent 2** | `agent_audit` | PageSpeed, script bloat, financial drain model (`audit_report.json`, `audit_summary.md`) |
| **Agent 3** | `agent_solution` | Layout archetype, design tokens, motion profile (`layout_spec.json`, `design_tokens.json`) |
| **Agent 4** | `agent_builder` | Complete Next.js 14 / Tailwind / Fast COD demo codebase (`demo/source/*`) |
| **Agent 5** | `agent_qa` | Adversarial multi-viewport QA & 60fps motion verification (`demo/qa_report.json`) |
| **Agent 6** | `agent_deployment`| GitHub repo creation, Supabase RLS provisioning, Vercel Edge push (`deployment/*`) |
| **Agent 7** | `agent_sales` | Audit-backed outreach in French & Moroccan Darija (`sales/outreach_fr.md`, `sales/outreach_darija.md`) |

---

## 🔒 Security & Privacy

- Zero secrets committed to git (`.env` strictly excluded).
- Read-only public storefront inspection.
- Human authorization required before cloud provisioning and outreach.
