# DL1 Main Path Walkthrough

Run the complete v0.2 main path:

```bash
python -S -m trapspringer.adapters.cli.main --campaign dl1 --demo-main-path --status --no-recap
```

Expected spine:

1. Event 1: Toede ambush
2. Goldmoon and Riverwind join
3. Xak Tsaroth arrival
4. Temple of Baaz / wicker dragon discovery
5. Plaza of Death / Khisanth surface encounter
6. Temple of Mishakal / staff recharge
7. Descent into Xak Tsaroth
8. Lower city route discovery
9. Khisanth's lair at 70k
10. Staff shatter and Disks recovery
11. Collapse escape
12. Epilogue and Medallion of Faith

The `--status` output should end at `epilogue_complete` with the staff shattered, Khisanth defeated, Disks recovered, and the Medallion created.
