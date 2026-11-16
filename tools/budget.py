"""A level's monsters against its ammunition and health, on "Resident" and "Just visiting":
python3 tools/budget.py map_hinges3 ... (in the ajar-tools image, from the project root).
Ammunition is counted as the damage it does; secrets are counted too."""
import importlib, sys
sys.path.insert(0, "tools")
HP = {3004: 20, 9: 30, 3001: 60, 3002: 150, 58: 150, 65: 70, 69: 500, 3003: 1000, 66: 300, 3006: 100,
      3005: 400, 67: 600, 68: 500, 71: 400, 64: 700, 20003: 40, 20004: 80, 20005: 60}
NAME = {3004: "zom", 9: "sgt", 3001: "imp", 3002: "pink", 58: "spec", 65: "cg", 69: "hk", 3003: "baron", 66: "rev",
        3006: "soul", 3005: "caco", 67: "manc", 68: "arach", 71: "PE", 20003: "thief", 20004: "nailer", 20005: "lodger"}
# damage a pickup is worth: shells 70 each, bullets 10, rockets 100, cells 22
AMMO = {2001: ("sh", 8), 82: ("sh", 8), 2008: ("sh", 4), 2049: ("sh", 20), 2002: ("bu", 20), 2007: ("bu", 10),
        2048: ("bu", 50), 2003: ("ro", 2), 2010: ("ro", 1), 2046: ("ro", 5), 2004: ("ce", 40), 17: ("ce", 100),
        2047: ("ce", 20), 8: ("pack", 1)}
DROP = {3004: ("bu", 5), 9: ("sh", 4), 65: ("bu", 10)}
DMG = dict(sh=70, bu=10, ro=100, ce=22)
HEAL = {2011: 10, 2012: 25, 2014: 1, 2013: 100, 2023: 100}
ARM = {2015: 1, 2018: 100, 2019: 200}
WEAP = {2001: "SG", 82: "SSG", 2002: "CG", 2003: "RL", 2004: "PL", 2023: "BERSERK", 8: "BACKPACK"}
for name in sys.argv[1:]:
    mod = importlib.import_module(name)
    m = mod.m
    sk = m._skills()
    for level in (3, 1):
        hp = 0; cnt = {}; am = dict(sh=0, bu=0, ro=0, ce=0); heal = 0; arm = 0; weap = []
        for t, s in zip(m.things, sk):
            if s > level: continue
            ty = t["type"]
            if ty in HP:
                hp += HP[ty]; cnt[NAME[ty]] = cnt.get(NAME[ty], 0) + 1
                if ty in DROP: am[DROP[ty][0]] += DROP[ty][1]
            if ty in AMMO and AMMO[ty][0] != "pack": am[AMMO[ty][0]] += AMMO[ty][1]
            if ty == 8:
                am["sh"] += 4; am["bu"] += 10; am["ro"] += 1; am["ce"] += 20
            heal += HEAL.get(ty, 0); arm += ARM.get(ty, 0)
            if ty in WEAP: weap.append(WEAP[ty])
        dmg = sum(DMG[k] * v for k, v in am.items())
        print(f"{name} skill{level}: {sum(cnt.values())} monsters, hp {hp}; ammo dmg {dmg} (x{dmg/hp:.2f}) "
              f"sh{am['sh']} bu{am['bu']} ro{am['ro']} ce{am['ce']}; heal {heal} armor {arm}; {' '.join(weap)}")
        if level == 3: print("   ", " ".join(f"{k}{v}" for k, v in sorted(cnt.items(), key=lambda x: -x[1])))
