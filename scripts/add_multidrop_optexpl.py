# -*- coding: utf-8 -*-
import json

PATH = r"C:\Users\Jergarcia\Desktop\linux-plus-trainer\data\pbq_scenarios.json"
scenarios = json.load(open(PATH, encoding="utf-8"))
pbq2 = next(s for s in scenarios if s["id"] == "pbq2")

PART1 = {
    "lvchange -a n /dev/vg01/lv01": "Deactivates an LV -- the opposite of what's needed, and at this point the LV doesn't even exist yet (vgs shows 0 LVs), so there's nothing to activate or deactivate until the metadata is restored first.",
    "lvchange -a y /dev/vg01/lv01": "Activating an LV that doesn't exist yet fails -- the VG metadata has to be restored before any LV can be activated. (This is the right move later, in Part 2 -- not here.)",
    "vgcfgrestore vg01 -f /etc/lvm/archive/vg01_00002-966141411.vg": "Restores the volume group's metadata from the most recent archived backup (_00002 is the higher, more recent sequence number), bringing back the LV definition that was accidentally removed.",
    "pvscan": "Only scans and reports physical volumes -- it doesn't restore removed LV metadata.",
    "lvconvert --type mirror lv01": "Converts an existing LV to mirrored (RAID1) storage -- unrelated to recovering an accidentally removed LV, and there's no LV to convert yet anyway.",
    "vgcfgrestore vg01 -f /etc/lvm/backup/vg01": "/etc/lvm/backup/ holds the current (already-broken, post-mistake) metadata, not a historical snapshot -- restoring from it just reapplies the same broken state. Point-in-time snapshots live in /etc/lvm/archive/ instead.",
    "vgcfgrestore vg01 -t -M /etc/lvm/archive/vg01_00001-810050352.vg": "-t runs vgcfgrestore in test mode -- a dry run that doesn't actually restore anything -- and _00001 is an older archive than _00002, so even without -t this would roll back to a less current state.",
}
PART2 = {
    "mount /dev/vg01/lv01/ /important_data": "Arguments are reversed -- mount expects DEVICE then MOUNTPOINT -- and the LV isn't active yet at this point regardless, so the mount would fail either way.",
    "pvchange -x y /dev/xvdf": "pvchange -x toggles a physical volume's allocation-permission flag; it doesn't activate a logical volume.",
    "lvchange -a n /dev/vg01/lv01": "-a n deactivates the LV -- the opposite of what's needed to continue the recovery.",
    "lvchange -a y /dev/vg01/lv01": "After Part 1 restores the VG metadata, the LV exists again but is inactive. -a y activates it so it can be mounted.",
    "lvextend -L +54 vg01/lv01 /dev/xvdf": "Resizes (grows) an LV -- unrelated to bringing an existing LV online, and premature at this stage of recovery.",
}
PART3 = {
    "mount /important_data /dev/vg01/lv01": "Arguments are reversed -- mount syntax is `mount <device> <mountpoint>`, not the other way around.",
    "xfs_repair /dev/vg01/lv01": "The filesystem isn't corrupted, it was just offline -- running a filesystem repair tool isn't what's needed to bring it back.",
    "mount -a": "Mounts everything listed in /etc/fstab. Since the mount entry for this LV already existed in fstab before the accidental removal, this brings it back online using that existing configuration -- no need to mount it manually.",
    "xfs_mdrestore /dev/vg01 /important_data": "xfs_mdrestore restores XFS metadata from a saved metadump image -- not applicable here, since there's no XFS-level corruption and no metadump was taken.",
    "lvscan -a": "lvscan only lists/scans LVs -- it doesn't mount anything.",
}

pbq2["parts"][0]["optExpl"] = PART1
pbq2["parts"][1]["optExpl"] = PART2
pbq2["parts"][2]["optExpl"] = PART3

json.dump(scenarios, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("added optExpl to pbq2's 3 parts")
