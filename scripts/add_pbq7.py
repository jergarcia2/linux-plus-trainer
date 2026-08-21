# -*- coding: utf-8 -*-
import json

PATH = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\pbq_scenarios.json"
scenarios = json.load(open(PATH, encoding="utf-8"))

new_scenario = {
    "id": "pbq7",
    "title": "PBQ 7 \u2014 SSH Key Setup",
    "type": "tiles",
    "badge": "SIMULATION",
    "desc": "A senior administrator has placed a private key for user admin in your home directory. "
            "The server you need to remotely access is server1, and SSH is listening on port 2222.",
    "inst": "Click tokens to build each command. Click a token in the command bar to remove it. "
            "Complete all four tabs.",
    "tabs": [
        {
            "name": "Move Key",
            "pfx": "",
            "toks": ["mv", "cp", "~/server1", "~/.ssh/id_rsa", "~/.ssh/id_rsa.pub",
                     "/etc/ssh/id_rsa", "~/.ssh/authorized_keys", "-r"],
            "ok": ["mv", "~/server1", "~/.ssh/id_rsa"],
            "expl": "mv ~/server1 ~/.ssh/id_rsa\n  \u2192 Moves the private key into the .ssh directory and "
                    "renames it to the conventional id_rsa filename SSH expects by default."
        },
        {
            "name": "Set Permissions",
            "pfx": "",
            "toks": ["chmod", "600", "644", "700", "755", "~/.ssh/id_rsa", "~/.ssh", "-R"],
            "ok": ["chmod", "600", "~/.ssh/id_rsa"],
            "expl": "chmod 600 ~/.ssh/id_rsa\n  \u2192 Private keys must be readable/writable by the owner "
                    "only \u2014 SSH refuses to use a key with group/world permissions set (644 or 755 "
                    "would be rejected)."
        },
        {
            "name": "Set Ownership",
            "pfx": "",
            "toks": ["chown", "admin:admin", "root:root", "comptia:comptia", "~/.ssh/id_rsa", "-R"],
            "ok": ["chown", "admin:admin", "~/.ssh/id_rsa"],
            "expl": "chown admin:admin ~/.ssh/id_rsa\n  \u2192 The key should be owned by the user connecting "
                    "with it (admin, per the scenario) so SSH's ownership check passes."
        },
        {
            "name": "Connect",
            "pfx": "",
            "toks": ["ssh", "-i", "-p", "2222", "22", "~/.ssh/id_rsa", "admin@server1",
                     "root@server1", "server1"],
            "ok": ["ssh", "-i", "~/.ssh/id_rsa", "-p", "2222", "admin@server1"],
            "expl": "ssh -i ~/.ssh/id_rsa -p 2222 admin@server1\n  \u2192 -i selects the private key, -p "
                    "targets the non-default port (2222) the scenario specifies, and admin@server1 is the "
                    "user/host pair. Note: the same options could instead be saved permanently in "
                    "~/.ssh/config as a Host block, so you don't have to type them every time."
        }
    ]
}

scenarios.append(new_scenario)
json.dump(scenarios, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("added pbq7, total scenarios:", len(scenarios))
