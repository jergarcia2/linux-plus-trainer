"""
Backfills two new fields onto every question in data/bank.json:

  domain      - one of CompTIA's 5 official XK0-006 exam domains (1.0-5.0),
                mapped from the existing `chapter` (Module N) field. This is
                the real, official CompTIA taxonomy (extracted from the Exam
                Objectives & Acronyms PDF), used as the coarse "Objective"
                filter in the UI. `chapter` itself remains the fine-grained
                filter (15 modules), same as today.
  difficulty  - "Easy" / "Medium" / "Hard", assigned by a simple, transparent
                heuristic (multi-select answers and long/scenario-heavy stems
                skew harder). This is a best-effort editorial estimate, not a
                certified rating -- it's meant to be hand-correctable later,
                same spirit as the adaptive engine's own weighting.

Run after extract.py.
"""
import json
import os

DATA_DIR = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data"

# Official CompTIA XK0-006 v1.3 domains, confirmed from the Exam Objectives PDF
DOMAINS = {
    "1.0": "1.0 System Management",
    "2.0": "2.0 Services and User Management",
    "3.0": "3.0 Security",
    "4.0": "4.0 Automation, Orchestration, and Scripting",
    "5.0": "5.0 Troubleshooting",
}

# Module -> domain, judged from each module's actual content against the
# domain descriptions in the objectives PDF (containers confirmed under 2.0
# via the PDF's own "manage applications in a container" objective text).
MODULE_DOMAIN = {
    "Module 1: Identifying Basic Linux Concepts": "1.0",
    "Module 2: Administering Users and Groups": "2.0",
    "Module 3: Configuring Permissions": "1.0",
    "Module 4: Implementing File Management": "1.0",
    "Module 5: Authoring Text Files": "1.0",
    "Module 6: Deploying Software": "1.0",
    "Module 7: Administering Storage": "1.0",
    "Module 8: Managing the Linux Kernel and Devices": "1.0",
    "Module 9: Maintaining Services": "2.0",
    "Module 10: Configuring Network Settings": "2.0",
    "Module 11: Securing a Linux System": "3.0",
    "Module 12: Installing Linux": "1.0",
    "Module 13: Scripting with Bash and Python": "4.0",
    "Module 14: Managing Containers in Linux": "2.0",
    "Module 15: Automating Infrastructure Management": "4.0",
}


def assign_difficulties(bank):
    """Terciles on stem length (bumped up a tier for multi-select answers)
    give a usable three-way spread instead of everything collapsing into one
    bucket -- this is a best-effort editorial estimate, not a certified
    rating, and is meant to be hand-correctable later."""
    order = sorted(range(len(bank)), key=lambda i: len(bank[i].get("q", "")))
    n = len(order)
    tier_of_rank = {}
    for rank, i in enumerate(order):
        if rank < n / 3:
            tier_of_rank[i] = "Easy"
        elif rank < 2 * n / 3:
            tier_of_rank[i] = "Medium"
        else:
            tier_of_rank[i] = "Hard"
    bump = {"Easy": "Medium", "Medium": "Hard", "Hard": "Hard"}
    for i, q in enumerate(bank):
        tier = tier_of_rank[i]
        if len(q.get("answer", "")) > 1:
            tier = bump[tier]
        q["difficulty"] = tier


def main():
    path = os.path.join(DATA_DIR, "bank.json")
    with open(path, "r", encoding="utf-8") as f:
        bank = json.load(f)

    counts = {"domain": {}, "difficulty": {}}
    for q in bank:
        code = MODULE_DOMAIN.get(q["chapter"])
        q["domain"] = DOMAINS.get(code, "1.0 System Management")
        counts["domain"][q["domain"]] = counts["domain"].get(q["domain"], 0) + 1

    assign_difficulties(bank)
    for q in bank:
        counts["difficulty"][q["difficulty"]] = counts["difficulty"].get(q["difficulty"], 0) + 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(bank, f, ensure_ascii=False, indent=1)

    with open(os.path.join(DATA_DIR, "domains.json"), "w", encoding="utf-8") as f:
        json.dump(DOMAINS, f, ensure_ascii=False, indent=1)

    print("domain counts:", counts["domain"])
    print("difficulty counts:", counts["difficulty"])


if __name__ == "__main__":
    main()
