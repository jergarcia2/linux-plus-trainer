# -*- coding: utf-8 -*-
"""Round 2 content cross-check: adds questions confirmed genuinely new after a
stricter re-verification (SequenceMatcher.ratio() + keyword-presence check
instead of the looser quick_ratio() used in the first pass)."""
import json

PATH = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\bank.json"
CH_PATH = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\chapters.json"
bank = json.load(open(PATH, encoding="utf-8"))
chapters = json.load(open(CH_PATH, encoding="utf-8"))

DOMAIN_BY_MODULE = {
    "Module 1: Identifying Basic Linux Concepts": "1.0 System Management",
    "Module 2: Administering Users and Groups": "2.0 Services and User Management",
    "Module 3: Configuring Permissions": "1.0 System Management",
    "Module 4: Implementing File Management": "1.0 System Management",
    "Module 5: Authoring Text Files": "1.0 System Management",
    "Module 6: Deploying Software": "1.0 System Management",
    "Module 7: Administering Storage": "1.0 System Management",
    "Module 8: Managing the Linux Kernel and Devices": "1.0 System Management",
    "Module 9: Maintaining Services": "2.0 Services and User Management",
    "Module 10: Configuring Network Settings": "2.0 Services and User Management",
    "Module 11: Securing a Linux System": "3.0 Security",
    "Module 12: Installing Linux": "1.0 System Management",
    "Module 13: Scripting with Bash and Python": "4.0 Automation, Orchestration, and Scripting",
    "Module 14: Managing Containers in Linux": "2.0 Services and User Management",
    "Module 15: Automating Infrastructure Management": "4.0 Automation, Orchestration, and Scripting",
}

NEW = [
{
  "q": "A systems administrator needs to integrate a new storage array into the company's existing storage pool and wants to confirm the operating system detects the new array. Which of the following commands should the administrator use?",
  "options": {"A": "lsscsi", "B": "lsusb", "C": "lsipc", "D": "lshw"},
  "answer": "A", "chapter": "Module 7: Administering Storage", "difficulty": "Easy",
  "explanation": "lsscsi lists SCSI-layer devices (which includes most enterprise storage arrays), making it the direct way to confirm the OS sees a newly attached array.",
  "optExpl": {
    "A": "lsscsi lists recognized SCSI devices and their device nodes -- the tool built specifically for verifying storage-array detection at the SCSI layer.",
    "B": "lsusb only enumerates USB devices, not SCSI/SATA/SAS storage arrays.",
    "C": "lsipc reports on inter-process communication facilities (shared memory, semaphores) -- unrelated to hardware detection.",
    "D": "lshw shows broad hardware details and could include storage, but lsscsi is the purpose-built, more direct tool for this specific check.",
  },
  "examTip": "lsscsi is the go-to command whenever a question is specifically about confirming a storage array/SCSI device was detected -- lshw is the generic \"show me everything\" fallback, not the first choice.",
},
{
  "q": "Users report that they cannot access some files located in the /opt/finapp directory after a power outage caused an unexpected server restart. The administrator finds /opt/finapp is an XFS filesystem, and /var/log/messages shows \"XFS (opt_finapp): Corruption detected in inode 3645, extent tree.\" Which of the following commands should the administrator run in an attempt to fix the filesystem?",
  "options": {"A": "fdisk /dev/mapper/rhel-opt_finapp", "B": "xfs_repair /dev/mapper/rhel-opt_finapp", "C": "lvcreate -L900G -n opt_finapp rhel fsck.ext4 /dev/mapper/rhel-opt_finapp", "D": "fsck.ext4 /dev/mapper/rhel-opt_finapp"},
  "answer": "B", "chapter": "Module 7: Administering Storage", "difficulty": "Hard",
  "explanation": "XFS has its own dedicated repair tool -- xfs_repair -- and does not use fsck; fsck.ext4 only works on ext-family filesystems, and the corruption message explicitly names XFS.",
  "optExpl": {
    "A": "fdisk edits partition tables, not filesystem structures -- it can't repair corruption inside an already-created filesystem.",
    "B": "xfs_repair is XFS's dedicated consistency-check-and-repair tool, built specifically for the \"corruption detected in inode/extent tree\" scenario described here.",
    "C": "This mixes lvcreate (which makes a brand-new logical volume, destroying data) with an ext4 tool -- neither belongs in an XFS repair, and running it would make things worse.",
    "D": "fsck.ext4 only understands ext2/3/4 filesystems; running it against an XFS filesystem does nothing useful.",
  },
  "examTip": "Match the repair tool to the filesystem type: XFS uses xfs_repair, ext2/3/4 uses fsck.ext4/e2fsck -- mixing them up is a common distractor.",
},
{
  "q": "An administrator logs in to a Linux server and notices the clock is 37 minutes fast. Which of the following commands will fix the issue?",
  "options": {"A": "hwclock", "B": "ntpdate", "C": "timedatectl", "D": "ntpd -q"},
  "answer": "B", "chapter": "Module 9: Maintaining Services", "difficulty": "Easy",
  "explanation": "ntpdate performs an immediate, one-shot time correction against an NTP server -- the direct fix for a clock that's already drifted noticeably out of sync.",
  "optExpl": {
    "A": "hwclock reads/sets the hardware (RTC) clock directly, but doesn't sync against a time server to correct drift.",
    "B": "ntpdate immediately queries an NTP server and steps the system clock to match -- the quickest way to correct a clock that's already 37 minutes off.",
    "C": "timedatectl manages systemd's time settings (timezone, NTP on/off) but doesn't itself force an immediate one-shot correction the way ntpdate does.",
    "D": "ntpd -q performs a one-time sync-and-exit similar to ntpdate, but ntpdate is the more direct, purpose-built command for this exact scenario.",
  },
  "examTip": "For a clock that's already drifted out of sync, reach for a one-shot correction tool (ntpdate/ntpd -q) -- timedatectl and hwclock manage settings and hardware time, not an active resync.",
},
{
  "q": "A Linux administrator is working with a CPU-intensive program called data-analysis1 and needs to prevent it from monopolizing CPU resources when it's launched. Which of the following commands accomplishes this?",
  "options": {"A": "data-analysis1 --nice 15", "B": "nice data-analysis1", "C": "nice -15 data-analysis1", "D": "data-analysis1 & nice +5"},
  "answer": "B", "chapter": "Module 8: Managing the Linux Kernel and Devices", "difficulty": "Medium",
  "explanation": "nice <command> launches a program with a lower (less favorable) default scheduling priority, exactly what's needed to keep a CPU-heavy program from crowding out everything else.",
  "optExpl": {
    "A": "--nice isn't a flag the program itself understands -- nice has to be the command that launches the program, not an argument passed to the program.",
    "B": "nice data-analysis1 starts the program with a raised (less favorable) niceness value by default, reducing its scheduling priority relative to other processes.",
    "C": "nice -15 actually *increases* priority (negative-style adjustment via -N syntax needs care; -15 here is ambiguous/incorrect usage) and isn't the safe default way to de-prioritize a new process.",
    "D": "Launching in the background with & and then running nice afterward as a separate, unrelated command doesn't apply niceness to data-analysis1 at all.",
  },
  "examTip": "nice <command> (no dash, plain launch) applies a sane, safer default de-prioritization; renice is the tool for adjusting a process that's already running.",
},
{
  "q": "A systems administrator engineer wants to configure a Linux server's time zone to America/Chicago. Which of the following commands should the engineer use?",
  "options": {"A": "date configure -set-timezone America/Chicago", "B": "set-timezone -config America/Chicago", "C": "time date set America/Chicago", "D": "timedatectl set-timezone America/Chicago"},
  "answer": "D", "chapter": "Module 9: Maintaining Services", "difficulty": "Easy",
  "explanation": "timedatectl set-timezone <zone> is systemd's standard command for changing a system's configured time zone.",
  "optExpl": {
    "A": "date only displays/sets the current date and time -- it has no timezone-configuration subcommand.",
    "B": "set-timezone isn't a standalone command on its own; timezone changes go through timedatectl.",
    "C": "\"time date set\" isn't a real command sequence on Linux.",
    "D": "timedatectl set-timezone America/Chicago is the correct, standard systemd command for changing the configured time zone.",
  },
  "examTip": "timedatectl is the modern systemd tool for anything involving date, time, timezone, and NTP sync state -- memorize it as your first guess for time-configuration questions.",
},
{
  "q": "A Linux administrator is updating the file that contains the addresses of the software and update repositories on an Ubuntu system. Which of the following files should the administrator edit?",
  "options": {"A": "/etc/apt/sources.list", "B": "/etc/apt/listchanges.conf", "C": "/etc/yum/yum.conf", "D": "/etc/dnf/dnf.conf"},
  "answer": "A", "chapter": "Module 6: Deploying Software", "difficulty": "Easy",
  "explanation": "/etc/apt/sources.list is Debian/Ubuntu's list of package repository sources -- yum.conf and dnf.conf are the RPM-family equivalents, not applicable on Ubuntu.",
  "optExpl": {
    "A": "/etc/apt/sources.list is exactly where apt-based systems (Debian/Ubuntu) list their repository sources.",
    "B": "listchanges.conf configures the apt-listchanges notification tool, not repository locations.",
    "C": "yum.conf is the repository/config file for yum -- a RPM-family (RHEL/CentOS/Fedora) tool, not used on Ubuntu.",
    "D": "dnf.conf is dnf's config file -- again RPM-family, not Ubuntu's package manager.",
  },
  "examTip": "Match the config file family to the distro: apt/sources.list for Debian-based systems, yum.conf/dnf.conf (and /etc/yum.repos.d/) for RPM-based systems -- a fast way to eliminate half the options on any package-manager question.",
},
{
  "q": "A Linux administrator needs to replace the entire content of the test1.sh file with the content of the test2.sh file. Which of the following commands will achieve this goal?",
  "options": {"A": "cat test2.sh >> test1.sh", "B": "cat test2.sh > test1.sh", "C": "cat test2.sh < test1.sh", "D": "cat test2.sh ? test1.sh"},
  "answer": "B", "chapter": "Module 4: Implementing File Management", "difficulty": "Easy",
  "explanation": "A single > redirect overwrites the destination file's existing content; >> would append instead of replace.",
  "optExpl": {
    "A": ">> appends to the end of test1.sh, keeping its old content alongside the new -- not a full replacement.",
    "B": "A single > redirects and overwrites test1.sh's content entirely with test2.sh's content, exactly \"replace.\"",
    "C": "< redirects input *into* the cat command rather than writing output to a file -- it doesn't write to test1.sh at all.",
    "D": "\"?\" isn't a valid redirection operator.",
  },
  "examTip": "Redirection operators: > overwrites, >> appends -- mixing these up is one of the most common shell scripting exam traps.",
},
{
  "q": "A Linux administrator attempts to log in to a server over SSH as root and receives the error \"Permission denied, please try again.\" The administrator can log in to the console directly as root and confirms the password is correct. Reviewing the SSH configuration shows PermitRootLogin is set to prohibit-password. Which of the following will most likely allow the administrator to log in over SSH as root?",
  "options": {"A": "Log out other user sessions because only one is allowed at a time.", "B": "Enable PAM and configure the SSH module.", "C": "Modify the SSH port to use 2222.", "D": "Use a key to log in as root over SSH."},
  "answer": "D", "chapter": "Module 11: Securing a Linux System", "difficulty": "Medium",
  "explanation": "PermitRootLogin prohibit-password (a common hardening default) allows root to log in over SSH only via key-based authentication -- password auth for root is deliberately rejected even though the password itself is correct.",
  "optExpl": {
    "A": "Concurrent-session limits aren't what prohibit-password controls -- this doesn't address the actual restriction in effect.",
    "B": "PAM is likely already enabled by default; the SSH daemon's PermitRootLogin setting, not a missing PAM module, is what's blocking password-based root login here.",
    "C": "Changing the port affects which port sshd listens on, not which authentication methods are accepted for root.",
    "D": "With PermitRootLogin prohibit-password, root can still log in over SSH -- but only using a key, never a password. Setting up key-based auth resolves it.",
  },
  "examTip": "\"Permission denied\" for root over SSH with a *confirmed-correct* password almost always means PermitRootLogin is set to prohibit-password (or without-password) -- the fix is a key, not a password reset.",
},
{
  "q": "An organization's business office needs to collaborate on quarterly reports and asks the systems administrator to create a finance group. The administrator creates a directory (currently drwxrwxr-x, group \"Business\") for this purpose. Which of the following commands will allow all members of the finance group to have group ownership of all files created in the directory, while ensuring members of the business group preserve access? (Select two).",
  "options": {"A": "chgrp Finance Q1/", "B": "chmod g+s Q1/", "C": "chmod u+s Q1/", "D": "chmod a+x Q1/", "E": "chown Finance Q1/", "F": "chmod g+x Q1/"},
  "answer": "AB", "chapter": "Module 3: Configuring Permissions", "difficulty": "Hard",
  "explanation": "Changing the directory's group to Finance (chgrp) and setting the setgid bit (chmod g+s) together make every new file created inside automatically group-owned by Finance -- the standard combination for shared-directory group inheritance.",
  "optExpl": {
    "A": "chgrp Finance Q1/ changes the directory's own group to Finance, the group new files should inherit.",
    "B": "chmod g+s Q1/ (setgid) makes every new file/subdirectory created inside automatically take on the directory's group -- without this, chgrp alone only affects the directory itself, not future files.",
    "C": "setuid (u+s) on a directory has no effect on group-ownership inheritance -- it's a different, unrelated bit.",
    "D": "a+x only affects execute (traverse) permission for everyone; it doesn't touch group ownership or inheritance.",
    "E": "chown changes the *owner*, not the group -- the requirement here is about group ownership, so chgrp is the correct tool, not chown.",
    "F": "g+x only affects execute permission for the existing group; it doesn't change which group a new file inherits.",
  },
  "examTip": "\"New files should automatically belong to the shared group\" is the signature phrase for setgid (chmod g+s) on a directory -- almost always paired with chgrp to first set the group you want inherited.",
  "source": "VCE dump, answer independently determined (source PDF did not include an extractable answer key for this question).",
},
{
  "q": "A systems administrator updates a DNS zone file to point www.abc.com to a new IP address, but querying it still returns the old IP mapping. Which of the following should the administrator run on the client to retrieve the updated IP mapping?",
  "options": {"A": "systemd-resolve query www.abc.com", "B": "systemd-resolve status", "C": "service nslcd reload", "D": "resolvectl flush-caches"},
  "answer": "D", "chapter": "Module 10: Configuring Network Settings", "difficulty": "Medium",
  "explanation": "A stale DNS answer after the authoritative record has already changed points to a local resolver cache still holding the old value -- resolvectl flush-caches clears systemd-resolved's cache so the next query re-fetches fresh data.",
  "optExpl": {
    "A": "\"systemd-resolve query\" isn't valid syntax for the modern resolvectl-based tool, and querying again would still hit the same stale cache anyway.",
    "B": "systemd-resolve status reports resolver configuration/state -- it's informational and doesn't clear any cached records.",
    "C": "nslcd is for LDAP-based name service lookups, unrelated to DNS resolver caching.",
    "D": "resolvectl flush-caches clears systemd-resolved's local DNS cache, forcing the next lookup to fetch the current (updated) record instead of a stale cached one.",
  },
  "examTip": "When an authoritative DNS record was already changed but clients still see the old value, suspect a local resolver *cache*, not the zone file -- flushing the cache (resolvectl flush-caches) is the fix, not editing DNS again.",
},
{
  "q": "A Linux server is not starting up because files in the /boot/ partition are corrupt. After the initial GRUB screen, the message \"Uncompression error -- System halted\" is displayed. Which of the following steps should the administrator take to recover the system without destroying the existing installation? (Select two).",
  "options": {"A": "Replace the hard drive.", "B": "Increase the amount of swap memory.", "C": "Start up in single-user mode.", "D": "Start up the system using rescue boot media.", "E": "Reinstall the kernel packages.", "F": "Reinstall the OS."},
  "answer": "DE", "chapter": "Module 12: Installing Linux", "difficulty": "Hard",
  "explanation": "With /boot itself corrupt, the system can't reach any normal boot target (including single-user mode) -- recovery means booting external rescue media first, then reinstalling/regenerating the kernel files that live in /boot.",
  "optExpl": {
    "A": "The hard drive isn't reported as failed, just the boot files -- replacing hardware is a drastic, unnecessary step.",
    "B": "Swap size has nothing to do with a GRUB-stage uncompression error reading corrupted /boot files.",
    "C": "Single-user mode is still a normal boot target reached *after* the kernel/initrd load successfully -- if /boot itself is corrupt, the system can't get that far.",
    "D": "Booting from rescue media gives you a working environment to mount the broken system's filesystems and repair /boot without needing the (currently unbootable) installed OS.",
    "E": "From the rescue environment, reinstalling the kernel package regenerates the corrupted vmlinuz/initrd files in /boot, restoring a bootable state.",
    "F": "A full OS reinstall would work but destroys the existing installation and all its configuration/data -- the question specifically asks to avoid that.",
  },
  "examTip": "\"Recover without destroying the existing installation\" is the tell to reach for rescue/live boot media plus a targeted repair (like reinstalling just the kernel package) -- not a full reinstall, and not a boot mode that itself depends on the broken files.",
  "source": "VCE dump, answer independently determined (source PDF did not include an extractable answer key for this question).",
},
{
  "q": "An administrator has generated an RSA SSH key pair to log in to a remote server. After copying the public key and attempting to log in, the administrator sees \"Permission denied (publickey,password)\" and debug output showing \"send_pubkey_test: no mutual signature algorithm.\" Which of the following actions should the administrator take first to remediate this issue?",
  "options": {"A": "Issue systemctl restart sshd on the local server.", "B": "Create a new key pair by running ssh-keygen -t ecdsa.", "C": "Set PermitRootLogin yes in the /etc/ssh/sshd_config file.", "D": "Update permissions on the /home/admin/.ssh directory to 700 on the remote server."},
  "answer": "B", "chapter": "Module 11: Securing a Linux System", "difficulty": "Hard",
  "explanation": "\"No mutual signature algorithm\" means the client and server don't share a compatible key-signing algorithm -- modern OpenSSH versions disable the older ssh-rsa signature scheme by default, so switching to a modern key type (ecdsa/ed25519) resolves the mismatch.",
  "optExpl": {
    "A": "Restarting sshd on the local machine doesn't change which signature algorithms either side is willing to negotiate.",
    "B": "Generating a key with a currently-accepted signature algorithm (ecdsa) sidesteps the deprecated-ssh-rsa mismatch causing the negotiation failure.",
    "C": "PermitRootLogin controls whether root specifically can log in -- it's unrelated to a signature-algorithm negotiation failure, and this scenario doesn't even mention the root account.",
    "D": "Loose .ssh directory permissions cause SSH to silently ignore authorized_keys, not this specific \"no mutual signature algorithm\" negotiation error.",
  },
  "examTip": "\"No mutual signature algorithm\" is a specific, recognizable phrase pointing at an incompatible/deprecated key type (classic ssh-rsa) -- not a permissions or config problem; regenerating with a modern algorithm (ecdsa/ed25519) is the fix.",
},
{
  "q": "A systems administrator is compressing old log files to save as much disk space as possible, and compression time is not a concern. Which of the following commands will achieve the best compression ratio?",
  "options": {"A": "bzip2", "B": "xz", "C": "tar", "D": "gzip"},
  "answer": "B", "chapter": "Module 4: Implementing File Management", "difficulty": "Medium",
  "explanation": "Of the common Linux compressors, xz (LZMA2-based) typically achieves the best compression ratio at the cost of being the slowest -- the right tradeoff when space matters more than speed.",
  "optExpl": {
    "A": "bzip2 generally compresses better than gzip but not as well as xz.",
    "B": "xz achieves the highest compression ratio of these options, trading extra CPU time/speed for smaller output -- ideal when \"time is not a concern.\"",
    "C": "tar only bundles files together (archiving); it doesn't compress on its own without a compression flag/pipe.",
    "D": "gzip is fast but has the weakest compression ratio of the three actual compressors listed here.",
  },
  "examTip": "Rank of compression ratio (best to fastest) among gzip/bzip2/xz: xz compresses smallest but slowest, gzip is fastest but compresses least -- pick based on which the question says matters more, space or time.",
},
{
  "q": "An application requires a configuration file to be placed in each user's home directory automatically whenever a new account is created. In which of the following locations should the administrator place this file?",
  "options": {"A": "/etc/skel", "B": "/etc/sysconfig", "C": "/etc/ssh", "D": "/etc/rc.local"},
  "answer": "A", "chapter": "Module 2: Administering Users and Groups", "difficulty": "Easy",
  "explanation": "Anything placed in /etc/skel is automatically copied into a new user's home directory when useradd -m creates it -- the standard mechanism for seeding default per-user files.",
  "optExpl": {
    "A": "/etc/skel is the \"skeleton\" directory whose contents are copied into every newly created user's home directory -- exactly the mechanism this scenario needs.",
    "B": "/etc/sysconfig holds system-wide service/network configuration, not per-user home directory templates.",
    "C": "/etc/ssh holds SSH daemon/client configuration, unrelated to new-user home directory content.",
    "D": "/etc/rc.local (where still used) runs commands at boot -- it's not a per-user file template location.",
  },
  "examTip": "/etc/skel is the exam's standard answer whenever a question is about files that should automatically appear in every new user's home directory.",
},
{
  "q": "An administrator thinks the user Joe may be running an unauthorized process on a Linux server. Which of the following commands should the administrator use to view Joe's running processes and their live resource usage?",
  "options": {"A": "lsof -p 'Joe'", "B": "top -u 'Joe'", "C": "jobs -n 'Joe'", "D": "ps -ax 'Joe'"},
  "answer": "B", "chapter": "Module 8: Managing the Linux Kernel and Devices", "difficulty": "Easy",
  "explanation": "top -u <user> filters the live, continuously-updating process view down to just that user's processes -- the right tool for actively watching what a specific user is running.",
  "optExpl": {
    "A": "lsof -p expects a PID, not a username, and lists open files rather than giving a live resource-usage view.",
    "B": "top -u 'Joe' filters top's live, auto-refreshing display to only Joe's processes -- exactly what's needed to watch what a specific user is currently running.",
    "C": "jobs lists background jobs of the *current shell session*, not another user's processes system-wide, and doesn't take a username filter this way.",
    "D": "ps -ax lists all processes system-wide but doesn't filter by username with that syntax, and it's a static snapshot rather than a live view.",
  },
  "examTip": "top -u <user> is the quick way to watch one user's processes live; ps -u <user> would give a similar filtered *snapshot* instead of a continuously refreshing view -- know the distinction between live monitoring and a one-time listing.",
},
{
  "q": "A systems administrator is writing a script to report the number of files in a given directory. Which of the following commands, piped from an `ls` listing, will produce a simple count?",
  "options": {"A": "less", "B": "tail -f", "C": "tr -c", "D": "wc -l"},
  "answer": "D", "chapter": "Module 4: Implementing File Management", "difficulty": "Easy",
  "explanation": "wc -l counts lines in its input -- piping a one-file-per-line `ls` listing into wc -l is the standard way to count files in a directory from a script.",
  "optExpl": {
    "A": "less is a pager for viewing output interactively; it doesn't produce a count.",
    "B": "tail -f follows a growing file/stream for new lines -- it's for watching live output, not counting existing entries.",
    "C": "tr translates or deletes characters; it isn't a counting tool on its own.",
    "D": "wc -l counts the number of lines in its input -- piping ls (one entry per line) into wc -l gives a simple file count.",
  },
  "examTip": "wc -l is the standard \"count lines/items\" tool in a pipeline -- reach for it whenever a script needs to turn a line-per-item listing into a number.",
},
{
  "q": "A systems administrator is deploying a web server using the following code snippet: `name \"Web Server\" description \"The role contains nodes, which act as a web server\"`. Which of the following technologies is the administrator using?",
  "options": {"A": "Chef", "B": "Ansible", "C": "Puppet", "D": "Terraform"},
  "answer": "A", "chapter": "Module 15: Automating Infrastructure Management", "difficulty": "Medium",
  "explanation": "\"Roles\" defined with name/description attributes in a Ruby-flavored DSL is Chef's distinctive syntax style -- Ansible uses YAML playbooks, Puppet uses its own declarative manifest language, and Terraform uses HCL.",
  "optExpl": {
    "A": "Chef defines roles using exactly this kind of Ruby-based DSL block (name/description/run_list) -- the syntax shown is characteristic of a Chef role definition.",
    "B": "Ansible's playbooks are written in YAML, not this Ruby-style attribute block.",
    "C": "Puppet manifests use their own declarative resource syntax, visually distinct from this Chef-style role block.",
    "D": "Terraform uses HCL (HashiCorp Configuration Language) for declaring infrastructure resources -- a different syntax entirely.",
  },
  "examTip": "Recognize each config-management tool by its file syntax on sight: Ansible = YAML playbooks, Chef = Ruby-based DSL (recipes/roles/cookbooks), Puppet = its own declarative manifest language, Terraform = HCL.",
},
{
  "q": "Which of the following RAID levels represents disk mirroring?",
  "options": {"A": "RAID 0", "B": "RAID 1", "C": "RAID 5", "D": "RAID 6"},
  "answer": "B", "chapter": "Module 7: Administering Storage", "difficulty": "Easy",
  "explanation": "RAID 1 writes an identical copy of all data to two (or more) disks -- the definition of mirroring.",
  "optExpl": {
    "A": "RAID 0 is striping for performance, with no redundancy at all -- the opposite of mirroring.",
    "B": "RAID 1 duplicates all data across two or more drives in real time -- exactly what \"mirroring\" means.",
    "C": "RAID 5 uses striping with distributed parity, not a full duplicate copy.",
    "D": "RAID 6 is like RAID 5 with an extra parity block for additional fault tolerance, still parity-based rather than a mirror.",
  },
  "examTip": "Memorize the core RAID identities: 0 = striping (speed, no redundancy), 1 = mirroring (full duplicate), 5/6 = striping with (single/double) parity.",
},
{
  "q": "A Linux systems administrator wants to validate the network interface configuration and status for the interface eth3 on a server. Which of the following commands should the administrator use?",
  "options": {"A": "ip list interface eth3", "B": "ip addr show dev eth3", "C": "ip show eth3", "D": "ip config eth3"},
  "answer": "B", "chapter": "Module 10: Configuring Network Settings", "difficulty": "Easy",
  "explanation": "ip addr show dev <iface> is the correct modern-iproute2 syntax for displaying one interface's address/status details.",
  "optExpl": {
    "A": "\"ip list interface\" isn't valid ip command syntax.",
    "B": "ip addr show dev eth3 is the correct syntax to display address and status information for a specific interface.",
    "C": "\"ip show\" without the addr/link object keyword isn't valid syntax.",
    "D": "\"ip config\" isn't a real ip subcommand (that's the older, separate ifconfig tool's naming, not ip's).",
  },
  "examTip": "The ip command's syntax pattern is `ip <object> <command> [dev <interface>]` -- e.g. ip addr show dev eth3, ip link show dev eth3 -- memorizing that object-first structure rules out most made-up-looking distractor syntax.",
},
{
  "q": "A systems administrator needs to check the size of the filesystem on the current application servers, including how much space is used and available on each mounted filesystem. Which of the following commands should the administrator use?",
  "options": {"A": "fdisk", "B": "df", "C": "du", "D": "lsblk"},
  "answer": "B", "chapter": "Module 7: Administering Storage", "difficulty": "Easy",
  "explanation": "df reports space usage and availability per mounted filesystem -- du instead reports space used by specific files/directories, a different (and commonly confused) tool.",
  "optExpl": {
    "A": "fdisk manages partition tables; it doesn't report filesystem space usage.",
    "B": "df reports total/used/available space for each mounted filesystem -- exactly what's asked for here.",
    "C": "du reports disk usage of files and directories (a bottom-up sum), not overall filesystem-level free space -- a frequently confused pair with df.",
    "D": "lsblk lists block devices and their mount points/sizes, but not live used/available space the way df does.",
  },
  "examTip": "df = filesystem-level free/used space (top-down); du = space consumed by specific files/directories (bottom-up) -- confusing the two is one of the most common exam traps.",
},
]

next_idx = len(bank)
added = 0
for q in NEW:
    q["images"] = []
    q["hasImage"] = False
    q["domain"] = DOMAIN_BY_MODULE[q["chapter"]]
    q["_idx"] = next_idx
    bank.append(q)
    chapters["counts"][q["chapter"]] = chapters["counts"].get(q["chapter"], 0) + 1
    next_idx += 1
    added += 1

json.dump(bank, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(chapters, open(CH_PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("added", added, "questions; bank now has", len(bank))
