import json

PATH = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\bank.json"
CH_PATH = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\chapters.json"
bank = json.load(open(PATH, encoding="utf-8"))
chapters = json.load(open(CH_PATH, encoding="utf-8"))

new_idx = len(bank)
new_q = {
    "q": "Users report that they are unable to reach the company website https://www.comptia.org. "
         "A systems administrator confirms the issue: `curl https://www.comptia.org` returns "
         "\"curl: (7) Failed to connect to www.comptia.org port 443: No route to host\". "
         "On the web server, `firewall-cmd --list-all` shows the active zone's services as "
         "\"cockpit dhcpv6-client http ssh\" (no https), and `ip route` shows a correct default "
         "route via eth0. Which of the following is causing the issue?",
    "options": {
        "A": "The web server's interface has no link.",
        "B": "The default route on the web server is incorrect.",
        "C": "HTTPS traffic is not allowed through the web server firewall.",
        "D": "User IP addresses are rejected by the firewall.",
    },
    "answer": "C",
    "images": [],
    "hasImage": False,
    "chapter": "Module 11: Securing a Linux System",
    "explanation": "firewall-cmd --list-all shows the active zone permits http and ssh but not "
                   "https, so the host firewall is dropping port 443/tcp before it ever reaches "
                   "the web server process -- matching curl's \"No route to host\" (firewalld's "
                   "reject behavior). Fix: `firewall-cmd --add-service=https --permanent && "
                   "firewall-cmd --reload`.",
    "optExpl": {
        "A": "eth0 shows an active default route (`default via ... dev eth0`) in the ip route "
             "output, so the interface has link and is configured -- this isn't a down-interface problem.",
        "B": "The routing table already has a correct default route. A bad default route would "
             "break most outbound traffic, not selectively block just HTTPS.",
        "C": "The firewalld zone's service list is \"cockpit dhcpv6-client http ssh\" -- https "
             "is missing, so port 443/tcp is blocked at the host firewall. Adding the https "
             "service (or opening 443/tcp directly) resolves it.",
        "D": "The zone's rich rules only reject SSH traffic from specific source IPs -- they "
             "don't touch HTTPS, and nothing here points to the affected users being on that list.",
    },
    "domain": "3.0 Security",
    "difficulty": "Hard",
    "examTip": "When a service is unreachable but routing and the interface both check out, check "
               "the host firewall's service/port list (`firewall-cmd --list-all`) before assuming "
               "a network-layer problem -- a missing service entry is a common, easy-to-miss cause.",
    "_idx": new_idx,
    "source": "vcehome-2026-08 (new, not in original 185)",
}

bank.append(new_q)
json.dump(bank, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

ch = "Module 11: Securing a Linux System"
chapters["counts"][ch] = chapters["counts"].get(ch, 0) + 1
json.dump(chapters, open(CH_PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

print("added question at _idx", new_idx, "-- bank now has", len(bank), "questions")
