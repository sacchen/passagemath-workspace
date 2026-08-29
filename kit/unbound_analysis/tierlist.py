import json
from datetime import datetime

with open('issues.json') as f:
    issues = json.load(f)

with open('prs.json') as f:
    prs = json.load(f)

items = []
for i in issues:
    items.append({"type": "Issue", "number": i["number"], "title": i["title"], "updatedAt": i["updatedAt"], "labels": [l["name"] for l in i.get("labels", [])]})

for p in prs:
    items.append({"type": "PR", "number": p["number"], "title": p["title"], "updatedAt": p["updatedAt"], "labels": [l["name"] for l in p.get("labels", [])]})

S_Tier = []
A_Tier = []
B_Tier = []
C_Tier = []
D_Tier = []

now = datetime.fromisoformat("2026-03-06T00:00:00Z")

for item in items:
    title = item["title"].lower()
    updated = datetime.fromisoformat(item["updatedAt"].replace("Z", "+00:00"))
    days_old = (now - updated).days
    labels = item["labels"]
    
    score = 0
    
    # Scale & Leverage (High impact, structural)
    if "wheel" in title or "windows" in title or "macos" in title or "ci" in title or "packaging" in title or "curation" in title or "wasm" in title or "webassembly" in title:
        score += 3
        
    if "bug" in labels:
        score += 1
        
    if "help wanted" in labels:
        score += 2 # Highly tractable for new contributors / clear need
        
    if days_old > 100:
        score += 2 # Neglected
    elif days_old > 30:
        score += 1
        
    # Categorization based on score
    if score >= 5:
        S_Tier.append(item)
    elif score == 4:
        A_Tier.append(item)
    elif score == 3:
        B_Tier.append(item)
    elif score == 2:
        C_Tier.append(item)
    else:
        D_Tier.append(item)

def print_tier(name, tier_items):
    print(f"## {name} Tier ({len(tier_items)} items)\n")
    for it in tier_items:
        print(f"- **{it['type']} #{it['number']}**: {it['title']} *(Updated: {it['updatedAt'][:10]}, Labels: {', '.join(it['labels']) if it['labels'] else 'None'})*")
    print("\n")

print("# PassageMath Issues and PRs Tier List")
print("> Ranked based on Leverage, Scale, Neglectedness, and Tractability.\n")

print_tier("S (Highest Impact, High Need/Neglected)", S_Tier)
print_tier("A (High Impact or Significant Bugs)", A_Tier)
print_tier("B (Moderate Impact/Maintenance)", B_Tier)
print_tier("C (Standard Updates/Bugs)", C_Tier)
print_tier("D (Recent/Lower Priority)", D_Tier)

