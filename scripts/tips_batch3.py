# -*- coding: utf-8 -*-
import json

PATH = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\bank.json"
bank = json.load(open(PATH, encoding="utf-8"))
byidx = {q["_idx"]: q for q in bank}

TIPS = {
128: "Identify a file by its actual content (`file` reporting \"7-zip archive data\"), not its filename \u2014 the matching extraction tool (7za e/x) is the one built for that specific archive format, regardless of what extension the file was given.",
129: "iptables direction matters: -A INPUT with -s <source network> --dport <service port> is how you restrict who's allowed to *connect in*; OUTPUT rules and --sport target the wrong direction/field entirely.",
130: "A negotiated link speed lower than the interface's rated capability (visible in ethtool output) caps real-world throughput well below what the hardware should support \u2014 check negotiated Speed before suspecting MTU, duplex, or FEC.",
131: "A server with an active link but no IP address, that only responds on the local console, is almost always failing to get a lease from DHCP \u2014 not a cabling or NIC hardware failure.",
132: "dd captures a raw, byte-for-byte image of a whole disk including the partition table itself \u2014 exactly what you need to back up or restore partition table structure, unlike file-oriented tools (tar/cpio/gzip).",
133: "A non-interactive/service account should have its shell set to /sbin/nologin so no one can get an interactive session from it, even with valid credentials.",
134: "\"Command not found\" for a script that clearly exists and is executable usually means its directory isn't in $PATH \u2014 fix that in a shell startup file like .bash_profile rather than chasing ownership or permissions.",
135: "journalctl -u <unit> filters the systemd journal down to just that one service's log entries \u2014 the direct way to see \"all logs\" for a specific unit, unlike grepping a shared log file.",
136: "Responsible AI use means scrubbing sensitive/identifying data before it ever reaches the model \u2014 sanitizing input, not blind copy-paste or lint-everything-automatically habits.",
137: "Random disconnects with otherwise-normal configuration (routing/MTU/TTL fine) point at a flaky physical NIC \u2014 hardware replacement, not a settings tweak.",
138: "Watch for the specific phrase \"memory usage climbing over time\" in a still-running process \u2014 that's a memory leak, distinct from swap exhaustion or cache growth (which self-manages and isn't a leak).",
139: "OOM-killer terminations that take *longer* to trigger after adding more RAM (rather than never happening) confirm a genuine memory leak \u2014 more memory just buys time before the same leak eventually exhausts it again.",
140: "chmod g+s on a directory (setgid) makes every new file/subdirectory created inside automatically inherit the directory's group \u2014 the standard fix for shared-directory group-ownership headaches.",
141: "Certificate trust errors for a server you actually intend to trust are fixed by importing that certificate into your local trusted store \u2014 not by disabling cert checking or minting a new self-signed cert.",
142: "Granting a few specific privileged commands to a small group means scoping sudo rules to exactly those utilities \u2014 not sharing the root password, not blanket full-root sudo access, and not sticky bits (which do something unrelated).",
143: "docker run -it <image> starts a new container and attaches an interactive terminal to it in one step \u2014 the standard way to \"start a terminal in a container.\"",
144: "export PATH=$PATH:<newdir> appends to the existing PATH by referencing the current value with $PATH \u2014 forgetting the leading $ (just \"PATH:...\") breaks the assignment entirely.",
145: "Editing a systemd unit file only changes it on disk \u2014 systemctl daemon-reload is required before systemd notices the edit; restart/start/enable act on the old, cached unit definition until then.",
146: "Ansible's Inventory defines which hosts/groups exist and can carry per-host or per-group variables \u2014 Playbooks define what to *do* to them, a different concept entirely.",
147: "dmesg surfaces kernel-level messages including boot-time errors \u2014 the first place to check for hardware/driver problems that happened during startup.",
148: "rpm -qa | grep kernel (or dnf list installed kernel*) shows exactly which kernel package/version is installed, and uname -a confirms what's currently running \u2014 the safe way to identify the right vmlinuz to restore before ever risking a reboot.",
149: "Port is a Port keyword inside /etc/ssh/sshd_config \u2014 the only file of these four that actually controls which port sshd listens on.",
150: "git pull fetches new commits from the remote and merges them into your local branch in one step \u2014 exactly \"synchronize local copy with the main repo's contents.\"",
151: "iptables -t nat -A PREROUTING ... --dport 80 -j DNAT --to-destination redirects *incoming* traffic on port 80 to a new destination \u2014 matching source port (--sport) or the wrong chain/table would target different traffic entirely.",
152: "ip route add <destination>/<mask> via <gateway> dev <iface> is the modern syntax for a static route \u2014 the older `route` command and made-up flags in the distractors aren't valid ways to add a persistent route.",
153: "Test for a file's existence with [ -f \"$var\" ] \u2014 quoting the variable protects against spaces/empty values, and -f specifically checks \"regular file exists,\" not -d (directory).",
154: "dd if=<source> of=<destination> \u2014 if (input file) always names what you're reading FROM, of (output file) names what you're writing TO; swapping them would overwrite your source disk instead of imaging it.",
155: "Code that declares desired end-state infrastructure (servers, networking) for cloud providers, applied declaratively rather than as an imperative script, is Terraform's signature \u2014 distinguish it from configuration-management tools (Ansible/Puppet/Chef) that manage software *on* already-provisioned machines.",
156: "LDAP is the standard centralized directory service for storing and querying users/groups across a network \u2014 MFA/SSO/PAM are authentication mechanisms, not user-data repositories themselves.",
157: "A network interface that's administratively up but shows NO-CARRIER (or similar) almost always means the cable isn't actually connected to a switch/port \u2014 check physical link state before suspecting addressing or drivers.",
158: "podman/docker run -p <host-port>:<container-port> \u2014 host port always comes first, container's internal port second; getting the order backwards exposes the wrong port entirely.",
159: "podman/docker exec -it <container> <shell> opens an interactive shell inside an *already-running* container to inspect logs/state live \u2014 `run` would start a brand-new container instead of entering the existing one.",
160: "Getting a public key onto a remote host can be done with the purpose-built ssh-copy-id, or generically with any file-copy tool like scp \u2014 ssh-keygen/ssh-keyscan only generate/collect keys, they don't transfer files.",
161: "sysctl -w net.ipv4.ip_forward=1 sets the live kernel parameter immediately (add it to /etc/sysctl.conf separately to make it persist across reboots) \u2014 that's the standard runtime way to enable IP forwarding, not a raw /proc echo or a firewall/service command.",
162: "After changing a systemd timer/service definition, systemctl daemon-reload must run before systemd picks up the new schedule \u2014 a plain reboot alone can still leave stale cached unit state in some setups, so make reloading part of the habit.",
163: "A proper Git change workflow branches off before editing (git checkout -b <branch>) so changes stay isolated and reviewable \u2014 that's the version-control best practice being tested here, not just cloning and pushing straight to the main branch.",
164: "chmod -t removes the sticky bit from a directory \u2014 with it set, only a file's owner (or root) can rename/delete it even with group write access; removing it lets any user with write access rename files.",
165: "uname's flags each report something different: -s = kernel name, -n = hostname, -o = operating system, -m = machine hardware (architecture) \u2014 memorize which letter maps to which field.",
166: "Building a filesystem on LVM is a multi-step chain: lvcreate (carve the logical volume from a volume group) \u2192 mkfs (format it) \u2192 mount \u2014 skipping straight to a raw partition (parted) or inventing non-existent commands (\"lvs --create\") breaks the LVM abstraction the question is testing.",
167: "Match the tool to the actual compression format \u2014 unzip handles .zip archives specifically; gzip/bzip2 handle single-file .gz/.bz2 streams, not zip containers.",
168: "SSH connection failures that get no response at all (timeout, not \"connection refused\") from an otherwise-reachable IP usually mean a firewall is silently dropping the traffic \u2014 refused connections would point to the service itself instead.",
169: "/etc/systemd/journald.conf is journald's own config file \u2014 don't confuse it with the similarly-named but non-existent \"systemd-journald.conf\"/\"systemd-journalctl.conf\" distractors.",
170: "When a scenario explicitly calls out portability + high availability + scalability *in production* for containers, that's describing container orchestration \u2014 Kubernetes, not just Docker (which runs containers but doesn't orchestrate a production cluster by itself).",
171: "Jenkins is the classic dedicated CI/CD pipeline automation server \u2014 Chef/Puppet/Ansible are configuration-management tools, a related but different job.",
172: "umask sets the *default* permission mask applied to every newly created file automatically \u2014 the right tool when the requirement is about all *future* files, not a one-time chmod on files that already exist.",
173: "pam_nologin.so is the PAM module that checks for /etc/nologin and blocks all non-root logins while that file exists \u2014 purpose-built for exactly this maintenance-mode scenario.",
174: "systemctl mask makes a service impossible to start either automatically or manually (it symlinks the unit to /dev/null) \u2014 stronger than disable, which only prevents automatic/boot-time starts but still allows a manual start.",
175: "A service repeatedly failing with a timeout during startup often just needs more time \u2014 raise TimeoutStartUSec in the unit file rather than changing scheduling, kill signals, or enablement, none of which address a slow-starting process being killed too early.",
176: "systemd's Requires= creates a hard dependency \u2014 the unit won't start (and stops if the dependency fails) until the required service is up, which is exactly \"ensure the database is available before the web app starts.\" Wants= is only a soft/best-effort hint, not a real prerequisite.",
177: "\"No space left\" errors with plenty of visible disk capacity free are often an inode exhaustion problem, not a block/byte-space problem \u2014 df -i checks inode usage specifically, separate from the default df (which reports block/byte usage).",
178: "Match the package manager to the distro family: dnf/yum for RPM-based systems, apt/apt-get for Debian-based \u2014 using rpm -i to install (not remove) or the wrong family's tool won't accomplish an RPM removal.",
179: "tail -n <N> prints just the last N lines of a file \u2014 the flag to reach for whenever a question specifies an exact line count.",
180: "iowait rising while a workload sits at (or near) a cloud disk's documented max throughput/IOPS ceiling means the storage tier itself is the bottleneck \u2014 not CPU, not an idle system, and not partitioning.",
181: "ip route get <dest> from <source> asks the kernel's routing table which path it would actually use between two specific addresses \u2014 the direct way to \"test the route\" without sending real traffic.",
182: "cat <file> | xargs rm -rf feeds each line of a text file as an argument to rm, deleting everything listed \u2014 the standard pattern for turning a list-of-names file into a bulk delete.",
183: "kill -9 sends an unblockable, unignorable termination signal that immediately ends a runaway process \u2014 renice only lowers its priority (doesn't stop it), and pstree/iostat are just diagnostic, not corrective.",
184: "chmod's numeric mode encodes special bits as a leading digit: 4 = SUID, 2 = SGID, 1 = sticky \u2014 so SUID + rwxr--r-- (744) is written as 4744, prefixed onto the normal three-digit permission set.",
}

applied = 0
for idx, tip in TIPS.items():
    if idx in byidx:
        byidx[idx]["examTip"] = tip
        applied += 1

json.dump(bank, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
missing = [q["_idx"] for q in bank if not q.get("examTip")]
print("applied", applied, "tips; total with tips now:", sum(1 for q in bank if q.get("examTip")))
print("still missing:", missing)
