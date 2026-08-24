# -*- coding: utf-8 -*-
import json

PATH = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\pbq_scenarios.json"
scenarios = json.load(open(PATH, encoding="utf-8"))
pbq1 = next(s for s in scenarios if s["id"] == "pbq1")

# keyed "cmdIndex-partIndex" -> explanation of what that blank is asking for
pbq1["blankExpl"] = {
    "0-1": "Names the target disk for the new GPT label. The scenario adds the new drive at /dev/sdc, so any other device name (sdb, /dev/dev1, sdc without /dev/, etc.) points at the wrong device.",
    "0-2": "The parted subcommand that creates a new partition table. mkpart (used in the next command) creates an individual partition, not the table itself.",
    "1-1": "Same device as before: /dev/sdc is the disk that was just labeled and is being partitioned.",
    "1-2": "The parted subcommand that creates a new partition. mklabel (already done in the previous command) creates the partition table, not a partition.",
    "1-3": "The partition type -- \"primary\" is a real, standard partition type; \"secondary\" isn't a valid parted partition type at all.",
    "1-4": "The filesystem-type hint for the new partition -- the task calls for ext4, so any other filesystem name here doesn't match what's being formatted.",
    "2-1": "mkfs.<type> must match the filesystem actually being created -- the task calls for ext4, not ext2/ext3.",
    "2-2": "The partition to format -- note the trailing \"1\" (the first partition on /dev/sdc), not the whole raw disk (/dev/sdc) used in the earlier commands.",
}

json.dump(scenarios, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("added blankExpl to pbq1")
