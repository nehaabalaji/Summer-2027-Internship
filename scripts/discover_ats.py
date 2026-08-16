#!/usr/bin/env python3
"""Probe public Greenhouse / Lever / Ashby / Workday endpoints for seed companies.

Writes newly verified boards into config/ats_boards.yaml. Never guesses Workday
triples that 404. Does not bypass authentication or bot protection.
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from board.config import sources  # noqa: E402

UA = "Supply-Chain-Internships/1.0 (+https://github.com/nehaabalaji/Summer-2027-Internship; student internship aggregator)"

SEED_COMPANIES = [
    "Qualcomm", "Intuit", "Apple", "Amazon", "ServiceNow", "Sony Electronics",
    "Teradata", "Viasat", "Illumina", "Dexcom", "Solar Turbines", "Caterpillar",
    "Rivian", "Kia", "Mazda", "Hyundai", "Karma Automotive", "Edwards Lifesciences",
    "Masimo", "Blizzard Entertainment", "Ingram Micro", "Broadcom", "Panasonic Avionics",
    "Google", "Pacific Life", "Taco Bell", "Yum Brands", "Experian", "Pacific Dental Services",
    "YouTube", "Electronic Arts", "Belkin", "SpaceX", "NFL", "Mattel", "DIRECTV", "Snap",
    "Disney", "Riot Games", "TikTok", "Oracle", "Activision", "Lionsgate", "Warner Bros",
    "NBCUniversal", "Sony Pictures", "AEG", "Live Nation", "ESPN", "Netflix", "OpenAI",
    "Airbnb", "Uber", "Lyft", "Databricks", "Notion", "Discord", "Cloudflare", "Asana",
    "Figma", "Pinterest", "Flexport", "Stripe", "Brex", "Plaid", "Meta", "NVIDIA", "Cisco",
    "Adobe", "eBay", "PayPal", "Zoom", "Western Digital", "Supermicro", "AMD", "Intel",
    "LinkedIn", "Yahoo", "HP", "SAP", "VMware", "Microsoft", "Applied Materials",
    "Lam Research", "KLA", "Synopsys", "Cadence", "Tesla", "Porsche", "BMW", "Mercedes-Benz",
    "Audi", "Toyota", "Honda", "Nissan", "Ford", "General Motors", "Stellantis", "Volkswagen",
    "Subaru", "Lucid Motors", "Waymo", "Aurora", "Nuro", "Zoox", "Bosch", "Continental",
    "Magna", "Aptiv", "BorgWarner", "Lear", "Denso", "Michelin", "Goodyear", "Pirelli",
    "Redwood Materials", "QuantumScape", "PepsiCo", "Coca-Cola", "Procter & Gamble",
    "Unilever", "Dell", "Walmart", "Home Depot", "UPS", "FedEx", "DHL",
    "Hendrick Motorsports", "Team Penske", "Andretti", "McLaren", "Ferrari", "Haas",
    "Williams Racing", "Formula 1", "Liberty Media", "Salesforce", "IBM", "Visa",
    "American Express", "Mastercard", "Puma", "Adidas", "Lenovo",
]

SLUG_ALIASES = {
    "Electronic Arts": ["ea", "electronicarts"],
    "Taco Bell": ["tacobell", "yum", "yumbrands"],
    "Yum Brands": ["yumbrands", "yum"],
    "Snap": ["snapchat", "snapinc", "snap"],
    "Disney": ["thewaltdisneycompany", "disney"],
    "Warner Bros": ["warnerbrosdiscovery", "wbd", "warnerbros"],
    "NBCUniversal": ["nbcuniversal", "nbcuni"],
    "Live Nation": ["livenationentertainment", "livenation"],
    "Procter & Gamble": ["pg", "proctergamble"],
    "Coca-Cola": ["cocacola", "thecocacolacompany"],
    "Mercedes-Benz": ["mercedesbenz", "mercedes"],
    "General Motors": ["gm", "generalmotors"],
    "Lucid Motors": ["lucidmotors", "lucid"],
    "Western Digital": ["westerndigital", "wd"],
    "Applied Materials": ["appliedmaterials", "amat"],
    "Lam Research": ["lamresearch", "lam"],
    "Pacific Life": ["pacificlife"],
    "Edwards Lifesciences": ["edwardslifesciences", "edwards"],
    "Blizzard Entertainment": ["blizzard", "activisionblizzard"],
    "Riot Games": ["riotgames", "riot"],
    "OpenAI": ["openai"],
    "Notion": ["notion", "notionhq"],
    "Figma": ["figma"],
    "Cloudflare": ["cloudflare"],
    "Plaid": ["plaid"],
    "Brex": ["brex"],
    "Asana": ["asana"],
    "Discord": ["discord"],
    "Pinterest": ["pinterest"],
    "NVIDIA": ["nvidia"],
    "Uber": ["uber"],
    "Lyft": ["lyft"],
    "Airbnb": ["airbnb"],
    "Stripe": ["stripe"],
    "Databricks": ["databricks"],
    "Flexport": ["flexport"],
    "SpaceX": ["spacex"],
    "Rivian": ["rivian"],
    "Nuro": ["nuro"],
    "Waymo": ["waymo"],
    "Zoox": ["zoox"],
    "Intuit": ["intuit"],
    "ServiceNow": ["servicenow"],
    "Adobe": ["adobe"],
    "Cisco": ["cisco"],
    "Zoom": ["zoom"],
    "PayPal": ["paypal"],
    "eBay": ["ebay"],
    "LinkedIn": ["linkedin"],
    "Salesforce": ["salesforce"],
    "IBM": ["ibm"],
    "Visa": ["visa"],
    "Netflix": ["netflix"],
    "Tesla": ["tesla"],
    "TikTok": ["tiktok", "bytedance"],
    "Oracle": ["oracle"],
    "AMD": ["amd"],
    "Qualcomm": ["qualcomm"],
    "Broadcom": ["broadcom"],
    "Illumina": ["illumina"],
    "Dexcom": ["dexcom"],
    "Mattel": ["mattel"],
    "Experian": ["experian"],
    "Ingram Micro": ["ingrammicro"],
    "Caterpillar": ["caterpillar"],
    "Ford": ["ford"],
    "Toyota": ["toyota"],
    "Honda": ["honda"],
    "BMW": ["bmw", "bmwgroup"],
    "Porsche": ["porsche"],
    "Audi": ["audi"],
    "Hyundai": ["hyundai"],
    "Kia": ["kia"],
    "Bosch": ["bosch"],
    "Aptiv": ["aptiv"],
    "Magna": ["magna"],
    "Michelin": ["michelin"],
    "Goodyear": ["goodyear"],
    "Dell": ["dell"],
    "HP": ["hp", "hpinc"],
    "SAP": ["sap"],
    "Walmart": ["walmart"],
    "PepsiCo": ["pepsico"],
    "Unilever": ["unilever"],
    "UPS": ["ups"],
    "FedEx": ["fedex"],
    "DHL": ["dhl"],
    "McLaren": ["mclaren", "mclarenracing"],
    "Ferrari": ["ferrari"],
    "Haas": ["haas", "haasf1team"],
    "Formula 1": ["formula1", "f1"],
    "Liberty Media": ["libertymedia"],
    "Hendrick Motorsports": ["hendrickmotorsports"],
    "Team Penske": ["penske", "teampenske"],
    "Andretti": ["andretti", "andrettiglobal"],
    "Redwood Materials": ["redwoodmaterials"],
    "QuantumScape": ["quantumscape"],
    "Lucid Motors": ["lucidmotors"],
    "Pacific Dental Services": ["pacificdentalservices"],
    "Karma Automotive": ["karmaautomotive"],
    "Masimo": ["masimo"],
    "Teradata": ["teradata"],
    "Viasat": ["viasat"],
    "Supermicro": ["supermicro"],
    "Cadence": ["cadence"],
    "Synopsys": ["synopsys"],
    "KLA": ["kla"],
    "Yahoo": ["yahoo"],
    "VMware": ["vmware"],
    "DIRECTV": ["directv"],
    "Lionsgate": ["lionsgate"],
    "AEG": ["aeg"],
    "NFL": ["nfl"],
    "ESPN": ["espn"],
    "Activision": ["activision"],
    "Belkin": ["belkin"],
    "Panasonic Avionics": ["panasonicavionics", "panasonic"],
    "Sony Electronics": ["sony", "sonyelectronics"],
    "Sony Pictures": ["sonypictures"],
    "American Express": ["americanexpress", "amex"],
    "Mastercard": ["mastercard"],
    "Puma": ["puma"],
    "Adidas": ["adidas"],
    "Lenovo": ["lenovo"],
    "Aurora": ["aurora", "aurorainnovation"],
    "Continental": ["continental"],
    "Lear": ["lear"],
    "Denso": ["denso"],
    "BorgWarner": ["borgwarner"],
    "Stellantis": ["stellantis"],
    "Volkswagen": ["volkswagen", "vw"],
    "Subaru": ["subaru"],
    "Nissan": ["nissan"],
    "Mazda": ["mazda"],
}

WORKDAY_CANDIDATES = [
    ("Nike", "nike", "wd1", "nke"),
    ("Disney", "disney", "wd5", "disneycareers"),
    ("Disney2", "thewaltdisneycompany", "wd5", "disneycareer"),
    ("Oracle", "oracle", "wd5", "External_Career_Site"),
    ("AMD", "amd", "wd1", "External"),
    ("Qualcomm", "qualcomm", "wd5", "External"),
    ("Intuit", "intuit", "wd1", "Intuit"),
    ("Illumina", "illumina", "wd1", "illumina_careers"),
    ("AppliedMaterials", "appliedmaterials", "wd1", "External"),
    ("Lam", "lamresearch", "wd1", "LamResearch"),
    ("KLA", "kla", "wd1", "KLA"),
    ("Synopsys", "synopsys", "wd1", "External"),
    ("Cadence", "cadence", "wd1", "External_Careers"),
    ("WesternDigital", "westerndigital", "wd5", "External"),
    ("HP", "hp", "wd5", "External_Careers"),
    ("LinkedIn", "linkedin", "wd5", "External"),
    ("PayPal", "paypal", "wd1", "jobs"),
    ("eBay", "ebay", "wd5", "eBay_External"),
    ("Adobe", "adobe", "wd5", "external_experienced"),
    ("Cisco", "cisco", "wd5", "cisco_careers"),
    ("Zoom", "zoom", "wd1", "Zoom"),
    ("SAP", "jobs", "wd1", "SAP_Careers"),
    ("Ford", "ford", "wd1", "FordCareerSite"),
    ("Toyota", "toyota", "wd1", "ToyotaMotorNorthAmerica"),
    ("Honda", "honda", "wd1", "Honda_Careers"),
    ("BMW", "bmwgroup", "wd1", "BMW_Group"),
    ("Bosch", "bosch", "wd1", "bosch_career"),
    ("Aptiv", "aptiv", "wd1", "Aptiv"),
    ("Magna", "magna", "wd3", "Magna"),
    ("Michelin", "michelin", "wd3", "Michelin_Careers"),
    ("Goodyear", "goodyear", "wd5", "Goodyear"),
    ("Caterpillar", "cat", "wd5", "CaterpillarCareers"),
    ("Ingram", "ingrammicro", "wd5", "External"),
    ("Mattel", "mattel", "wd5", "Mattel"),
    ("Experian", "experian", "wd5", "Experian_Careers"),
    ("PepsiCo", "pepsico", "wd5", "PepsiCo"),
    ("P&G", "pg", "wd3", "Global_Careers"),
    ("Dell", "dell", "wd1", "External"),
    ("Walmart", "walmart", "wd5", "WalmartExternal"),
    ("HomeDepot", "homedepot", "wd5", "HD_External"),
    ("UPS", "upsjobs", "wd5", "search"),
    ("Lucid", "lucidmotors", "wd1", "Lucid_Motors"),
    ("Rivian", "rivian", "wd1", "Rivian_External"),
    ("Tesla", "tesla", "wd1", "Tesla"),
    ("J&J", "jj", "wd5", "JJ"),
    ("Unilever", "unilever", "wd3", "Unilever_Experienced_Professionals"),
    ("JBHunt", "jbhunt", "wd501", "Careers"),
    ("LiveNation", "livenation", "wd1", "LiveNation"),
    ("Warner", "wbd", "wd5", "External"),
    ("NBCU", "nbcuniversal", "wd5", "External"),
    ("Netflix", "netflix", "wd5", "External"),
    ("Salesforce", "salesforce", "wd1", "External_Career_Site"),
    ("IBM", "ibm", "wd1", "IBM_External"),
    ("Visa", "visa", "wd1", "Visa_Careers"),
    ("Amex", "americanexpress", "wd1", "American_Express"),
]


def slugs_for(name: str) -> list[str]:
    out = list(SLUG_ALIASES.get(name, []))
    compact = re.sub(r"[^a-z0-9]", "", name.lower())
    dashed = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    for item in (compact, dashed):
        if item and item not in out:
            out.append(item)
    return out[:4]


def existing_ids() -> set[str]:
    return {item.get("id") or item.get("source") for item in sources() if item.get("id") or item.get("source")}


def main() -> int:
    found: list[dict] = []
    existing = existing_ids()
    client = httpx.Client(timeout=12.0, headers={"User-Agent": UA, "Accept": "application/json"}, follow_redirects=True)

    print("Probing Greenhouse / Lever / Ashby...")
    for company in SEED_COMPANIES:
        for slug in slugs_for(company):
            checks = [
                ("greenhouse", f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", lambda d: isinstance(d, dict) and "jobs" in d),
                ("lever", f"https://api.lever.co/v0/postings/{slug}?mode=json", lambda d: isinstance(d, list)),
                ("ashby", f"https://api.ashbyhq.com/posting-api/job-board/{slug}", lambda d: isinstance(d, dict) and "jobs" in d),
            ]
            for platform, url, ok in checks:
                source_id = f"{slug}_{platform}" if platform != "greenhouse" else slug
                if source_id in existing or any(b.get("id") == source_id for b in found):
                    continue
                try:
                    time.sleep(0.12)
                    response = client.get(url)
                    if response.status_code != 200:
                        continue
                    data = response.json()
                    if not ok(data):
                        continue
                    count = len(data) if isinstance(data, list) else len(data.get("jobs") or [])
                    print(f"  OK {platform:12} {company:24} slug={slug} jobs={count}")
                    board = {
                        "id": source_id,
                        "company": company,
                        "source": source_id,
                        "platform": platform,
                        "enabled": True,
                        "career_url": url.split("?")[0],
                    }
                    if platform == "greenhouse":
                        board["board_token"] = slug
                    elif platform == "lever":
                        board["board_token"] = slug
                    else:
                        board["board_token"] = slug
                    found.append(board)
                except Exception:
                    continue

    print("Probing Workday CXS...")
    for name, tenant, shard, site in WORKDAY_CANDIDATES:
        source_id = tenant if tenant not in existing else f"{tenant}_{site}"
        if source_id in existing or any(b.get("id") == source_id for b in found):
            continue
        url = f"https://{tenant}.{shard}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
        try:
            time.sleep(0.15)
            response = client.post(
                url,
                json={"limit": 1, "offset": 0, "searchText": "intern"},
                headers={"Content-Type": "application/json"},
            )
            if response.status_code != 200:
                continue
            body = response.json()
            if "jobPostings" not in body and "total" not in body:
                continue
            total = body.get("total")
            print(f"  OK workday      {name:24} {tenant}.{shard}/{site} total={total}")
            found.append(
                {
                    "id": source_id,
                    "company": name,
                    "source": source_id,
                    "platform": "workday",
                    "tenant": tenant,
                    "shard": shard,
                    "site": site,
                    "enabled": True,
                    "career_url": f"https://{tenant}.{shard}.myworkdayjobs.com/{site}",
                }
            )
        except Exception:
            continue

    client.close()
    path = ROOT / "config" / "ats_boards.yaml"
    current = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    boards = list(current.get("boards") or [])
    have = {b.get("id") for b in boards}
    added = 0
    for board in found:
        if board["id"] in have:
            continue
        boards.append(board)
        have.add(board["id"])
        added += 1
    path.write_text(yaml.safe_dump({"boards": boards}, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"Added {added} boards. Total {len(boards)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
