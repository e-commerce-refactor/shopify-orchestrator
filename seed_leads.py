import os
import shutil
import json
import re
from orchestrator import init_workspace, generate_lead_id, normalize_url, LEADS_DIR
from generate_excel import prospects_data

print(f"[*] Reorganizing leads workspace with dedicated Business Name folders...")

# Clean existing leads directory
if os.path.exists(LEADS_DIR):
    shutil.rmtree(LEADS_DIR)
os.makedirs(LEADS_DIR, exist_ok=True)

for p in prospects_data:
    lead_id = generate_lead_id(p["url"], p["name"])
    norm_url = normalize_url(p["url"])
    contacts = {
        "whatsapp": p["wa"],
        "email": p["email"],
        "instagram": p["ig"],
        "verified_owner": False
    }
    permissions = {
        "asset_use": False,
        "data_collection": True,
        "deployment": False,
        "outreach": False
    }
    workspace, lead_data, run_data = init_workspace(
        lead_id=lead_id,
        target_url=norm_url,
        brand_name=p["name"],
        category=p["niche"],
        city=p["city"],
        contacts=contacts,
        permissions=permissions
    )
    print(f"  [OK] Initialized: leads/{lead_id}/ (Brand: {p['name']})")

print("\n[OK] All 35 lead workspaces initialized with lead.json and run.json.")
