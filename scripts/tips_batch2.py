# -*- coding: utf-8 -*-
import json

PATH = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\bank.json"
bank = json.load(open(PATH, encoding="utf-8"))
byidx = {q["_idx"]: q for q in bank}

TIPS = {
85: "Monitoring thresholds exist to generate alerts once a metric crosses a defined limit \u2014 they trigger notifications, they don't restart services or perform the health checks themselves.",
86: "firewall-cmd changes are runtime-only unless you add --permanent \u2014 and even a permanent rule needs a --reload (or a fresh boot) before it actually takes effect on this run.",
87: "Auditing is the formal term for reviewing process activity and file operations (think auditd) \u2014 logging just records events, it doesn't imply the review itself.",
88: "import is Python's keyword for pulling in a module \u2014 init/name/det aren't real import mechanisms (they're just plausible-looking Python-ish words).",
89: "lm_sensors reads hardware sensor chips for temperature/voltage/fan data \u2014 dmidecode covers static hardware inventory and ipmitool covers out-of-band management, neither reports live thermal readings the same way.",
90: "CIS Benchmarks are the specific, vendor-neutral hardening configuration standards for OS/application security \u2014 ISO 27001 and GDPR are broader compliance/legal frameworks, not step-by-step config guides.",
91: "Kernel messages about hardware errors (ECC, disk, bus errors) point to a hardware problem for the server/facilities team \u2014 they're not something a reboot or reinstall fixes.",
92: "git commit records staged changes into the local repository's history \u2014 git add only stages them, and push/clone deal with the remote, not with recording the change itself.",
93: "A duplex or speed mismatch usually shows as errors/collisions; a throughput ceiling with clean stats on both ends is the classic signature of an MTU mismatch (fragmentation or drops at a size boundary).",
94: "No response to ping alongside working TCP connectivity elsewhere usually means ICMP is being filtered somewhere along the path \u2014 not that the whole server or protocol stack is down.",
95: "Responsible public-AI use means keeping proprietary/sensitive data out of the prompt \u2014 anonymized data is fine to send, but proprietary source code, configs, or real documentation should stay off a public AI service.",
96: "dmesg prints the kernel ring buffer \u2014 hardware/driver events like USB device connections, not login attempts or application-level session messages.",
97: "`w` shows who's logged in, from where, and what they're doing; the -i flag adds IP addresses to that output \u2014 `who`/`cat /etc/hosts` don't show live connection info per user.",
98: "\"Forcefully ignored\" verification errors about trust almost always mean the certificate's issuer isn't in the trusted CA chain (self-signed or internal CA) \u2014 that's different from expiration or algorithm problems.",
99: "Crontab fields are minute hour day month weekday \u2014 \"3:00 PM every Sunday\" is minute=0, hour=15, weekday=0, with day/month left as * (any).",
100: "In shell scripting, an if without an else only handles the true branch \u2014 add else to define what happens when the condition (e.g. file doesn't exist) is false.",
101: "An OS that hasn't been patched in a year is itself the vulnerability \u2014 before blaming a specific service or setting, check how stale the last update actually was.",
102: "PEP 8 is a style/convention guide (naming, formatting, spacing) for writing Python code \u2014 not a module list, a library name, or a data structure.",
103: "nc (netcat) -v host port makes a direct connection attempt and reports whether it succeeded \u2014 the quickest way to confirm a specific remote TCP port is actually reachable.",
104: "getenforce prints SELinux's current mode (Enforcing/Permissive/Disabled) in one word \u2014 the fastest first check whenever SELinux is suspected.",
105: "for username in $VAR; do ...; done word-splits an unquoted variable into a loop automatically \u2014 while/until expect a test condition, not a list, so they're the wrong looping construct here.",
106: "ln -s creates a symbolic link that can point across filesystems and to directories; a hard link (plain `link`/`ln` without -s) can't cross filesystem boundaries.",
107: "Bridged networking gives a VM its own presence directly on the physical network (its own IP/MAC as if it were another physical host) \u2014 NAT and host-only both route through/limit to the host.",
108: "Symbolic links (ln -s) work across different filesystems since they just store a path; hard links cannot cross filesystem boundaries \u2014 that's the deciding detail whenever a question mentions the files are on different filesystems.",
109: "When one user in the same group as another can access something and the other can't, and ordinary group/owner permissions look identical, check for an ACL (getfacl) granting extra access to just that one user.",
110: "dnf --advisory-<CVE/bug-name> upgrade targets only the packages covered by a specific security advisory \u2014 useful for patching one named vulnerability without pulling in an unrelated general update.",
111: "An application that slowly consumes more and more memory over days until it becomes unresponsive is the classic signature of a memory leak, not a quota or allocation-permission issue.",
112: "\"restorecon\" resets a file's SELinux context back to policy default \u2014 reach for it whenever certificates/trust files were replaced or moved and now fail with permission-flavored errors despite correct Unix permissions.",
113: "Ansible playbooks are written in YAML \u2014 human-readable, indentation-based, and the format to recognize on sight for any Ansible question.",
114: "Adding a user to the sudo (or wheel, on RHEL-family systems) group is the standard way to grant privileged/root-equivalent access via usermod -aG, without hand-editing /etc/sudoers or /etc/passwd.",
115: "/etc/resolv.conf is where DNS server IPs are configured \u2014 the same answer whenever a question is about adding, changing, or setting nameservers.",
116: "nc -v host port is the general-purpose way to test whether a specific TCP port is reachable and accepting connections \u2014 works for arbitrary application ports, not just well-known services.",
117: "Resolving short hostnames (not FQDNs) on the same network relies on a configured DNS search domain being appended automatically \u2014 add the search domain rather than more nameservers or per-host DNS records.",
118: "nc (netcat) is the general tool for testing whether a specific port is open on a remote host \u2014 ping only checks basic reachability (ICMP), not any particular port or service.",
119: "Ansible's core job is configuration management \u2014 keeping systems in a defined, consistent state \u2014 not database, process, or asset management.",
120: "sssd.conf configures the System Security Services Daemon, which is what actually joins/authenticates a Linux host against Active Directory \u2014 smb.conf is for file/print sharing (Samba), not domain auth.",
121: "SNMP (Simple Network Management Protocol) is the standard protocol for polling and monitoring network device status/metrics \u2014 DNS/DHCP/SMTP each serve a completely different purpose.",
122: "python -m venv creates an isolated virtual environment \u2014 the conventional first step of any new Python project, done before installing any dependencies into it.",
123: "/usr holds shareable, read-only program data including installed packages' documentation (/usr/share/doc) \u2014 distinct from /var (variable/log data) and /lib (shared libraries).",
124: "A typical feature-branch Git workflow ends with pushing your committed, tested changes to the remote (git push origin <branch>) \u2014 commit/pull/checkout are all steps that happen before that final push.",
125: "Killing processes for a specific user by name reliably means finding their PIDs first (ps -ef | grep <user> | awk '{print $2}') and killing each one \u2014 killall/loops on non-existent conditions in the distractors don't actually target the right processes.",
126: "fuser -mk <mountpoint> both identifies and kills whatever process(es) are holding a filesystem open \u2014 the direct fix for \"target is busy\" on umount, faster than manually cross-referencing lsof.",
127: "chage -M <days> sets the maximum password age (forced expiry interval) for an account \u2014 the tool for enforcing a \"password must be changed every N days\" policy.",
}

applied = 0
for idx, tip in TIPS.items():
    if idx in byidx:
        byidx[idx]["examTip"] = tip
        applied += 1

json.dump(bank, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("applied", applied, "tips; total with tips now:", sum(1 for q in bank if q.get("examTip")))
