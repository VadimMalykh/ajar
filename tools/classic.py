"""Doom II's own maps joined into one Ajar level, made at build time from the
player's own doom2.wad (PLAN.md, "The joined maps lab").

Nothing of id's is in this file or anywhere in the repository: the maps are
read from the IWAD on the machine that builds, and the joined level is
written to build/ajar-classic.pk3 only (never into build/ajar.pk3). What the
repository holds is code and small numbers: line, sector and thing indices of
id's maps, offsets, and the maps' checksums to guard those numbers.

How a map becomes a piece of the level:
  * Its lumps (THINGS, LINEDEFS, SIDEDEFS, VERTEXES, SECTORS) are found by
    scanning the IWAD's own directory, so that Ajar's maps of the same names
    (MAP01 to MAP20 in ajar.pk3) do not come into it. No nodes are read:
    GZDoom builds them for a UDMF map.
  * Lines: Doom's linedef types are translated by GZDoom's own table
    (xlat/doom.txt and what it includes, read out of gzdoom.pk3 at build
    time) into ZDoom specials, arguments, activation and flags, as GZDoom
    does when it loads a Doom-format map. Specials' numbers: SPECIALS below.
  * Sectors: the special by the same table (9 is a secret).
  * Things: type and angle as they are; Doom's flags: easy -> skill1 and 2,
    medium -> skill3, hard -> skill4 and 5, deaf -> ambush, multiplayer only ->
    not single; Boom's not-deathmatch and not-coop are carried. Player starts
    2 to 4 and deathmatch starts are dropped; player 1's start is kept only in
    the piece the level starts in.
  * Each piece is moved by its offset, and its sector tags (and the line ids
    GZDoom gives Doom-format lines from their tags) are moved into a range of
    its own (TAG_BASE * piece number + tag), except the tags it is told to
    keep (Dead Simple's 666 and 667, which MAPINFO's map07special works on).
  * Exits are made harmless (the special taken off) and listed.
  * Every sector gets UDMF user fields: user_piece (the piece's number) and
    user_music (its map's music), which classic.zs reads.

python3 tools/classic.py builds build/ajar-classic.pk3 (./build.sh calls it
when it finds the IWAD); `survey MAPxx` and `walls MAPxx x y` print what is
needed to choose indices; `check` writes a test package that holds id's maps
converted under other names, to compare them with GZDoom's own loading.
"""
import hashlib
import math
import os
import re
import struct
import sys
import time
import zipfile

sys.path.insert(0, os.path.dirname(__file__))
import ajarmap
from udmf import Map

IWAD = os.environ.get("AJAR_IWAD", "/iwad/doom2.wad")
GZPK3 = os.environ.get("AJAR_GZDOOM_PK3", "/opt/gzdoom/gzdoom.pk3")
TAG_BASE = 10000        # piece n's tags and line ids: n * TAG_BASE + its own
NOTE_T = 20190          # AjarDoomNote (doomlab.zs): a Doom door line's own special, kept while it is made a portal

# GZDoom's checksum of a map (MD5 of THINGS, LINEDEFS, SIDEDEFS and SECTORS, as
# in its compatibility list): the indices used here are those of these maps
CHECKSUMS = {"MAP01": "3C9902E376CCA1E9C3BE8763BDC21DF5", "MAP07": "291F24417FB3DD411339AE82EF9B3597",
             "MAP21": "EBDAC00E9D25D884B2C8F4B1F0390539", "MAP22": "4AA9B3CE449FB614497756E96509F096"}

# ZDoom's line specials by name, the ones GZDoom's Doom table names (its numbers are
# compiled into the engine, not in gzdoom.pk3). `check` compares the result with
# GZDoom's own loading of every map of doom2.wad.
SPECIALS = dict(
    Door_Close=10, Door_Open=11, Door_Raise=12, Door_LockedRaise=13,
    Floor_LowerByValue=20, Floor_LowerToLowest=21, Floor_LowerToNearest=22, Floor_RaiseByValue=23,
    Floor_RaiseToHighest=24, Floor_RaiseToNearest=25, Floor_RaiseAndCrush=28,
    Floor_RaiseByValueTimes8=35, Floor_LowerByValueTimes8=36, Ceiling_LowerByValue=40,
    Ceiling_RaiseByValue=41, Ceiling_CrushAndRaise=42, Ceiling_LowerAndCrush=43, Ceiling_CrushStop=44,
    Ceiling_CrushRaiseAndStay=45, Plat_PerpetualRaise=60, Plat_Stop=61, Plat_DownWaitUpStay=62,
    Plat_UpWaitDownStay=64, Plat_UpByValue=65, Teleport=70, Teleport_NoFog=71,
    Floor_RaiseAndCrushDoom=99, Scroll_Texture_Left=100, Scroll_Texture_Right=101,
    Ceiling_CrushAndRaiseSilentDist=104, Light_ChangeToValue=112, Line_SetPortal=156,
    Ceiling_CrushAndRaiseDist=168, Ceiling_LowerToHighestFloor=192, Generic_Floor=200,
    Generic_Ceiling=201, Plat_DownWaitUpStayLip=206, Plat_PerpetualRaiseLip=207,
    Transfer_Heights=209, Transfer_FloorLight=210, Transfer_CeilingLight=211, Teleport_Line=215,
    Stairs_BuildUpDoom=217, Sector_SetWind=218, Sector_SetFriction=219, Sector_SetCurrent=220,
    Scroll_Texture_Model=222, Scroll_Floor=223, Scroll_Ceiling=224, Scroll_Texture_Offsets=225,
    PointPush_SetForce=227, Plat_RaiseAndStayTx0=228, Plat_UpByValueStayTx=230, Plat_ToggleCeiling=231,
    Light_StrobeDoom=232, Light_MinNeighbor=233, Light_MaxNeighbor=234, Floor_TransferTrigger=235,
    Floor_TransferNumeric=236, Floor_RaiseToLowestCeiling=238, Floor_RaiseByValueTxTy=239,
    Floor_RaiseByTexture=240, Floor_LowerToLowestTxTy=241, Floor_LowerToHighest=242, Exit_Normal=243,
    Exit_Secret=244, Elevator_RaiseToNearest=245, Elevator_MoveToFloor=246, Elevator_LowerToNearest=247,
    Door_CloseWaitOpen=249, Floor_Donut=250, FloorAndCeiling_LowerRaise=251, Ceiling_LowerToLowest=253,
    Ceiling_LowerToFloor=254, Stairs_BuildUpDoomCrush=273,
)
EXITS = {243, 244, 74, 75}      # Exit_Normal, Exit_Secret, Teleport_NewMap, Teleport_EndGame

MUSIC = {"MAP01": "D_RUNNIN", "MAP02": "D_STALKS", "MAP03": "D_COUNTD", "MAP04": "D_BETWEE", "MAP05": "D_DOOM",
         "MAP06": "D_THE_DA", "MAP07": "D_SHAWN", "MAP08": "D_DDTBLU", "MAP09": "D_IN_CIT", "MAP10": "D_DEAD",
         "MAP21": "D_SHAWN", "MAP22": "D_THE_DA"}


# --- the IWAD ---------------------------------------------------------------------------------------
class Wad:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.data = f.read()
        kind, n, at = struct.unpack_from("<4sii", self.data, 0)
        if kind not in (b"IWAD", b"PWAD"):
            raise ValueError(f"{path} is not a wad")
        self.dir = []
        for i in range(n):
            pos, size, name = struct.unpack_from("<ii8s", self.data, at + 16 * i)
            self.dir.append((name.rstrip(b"\0").decode("latin1").upper(), pos, size))

    def map(self, name):
        """The map's lumps by name, from the first marker `name` in this file's own directory."""
        for i, (n, _, _) in enumerate(self.dir):
            if n == name:
                out = {}
                for n2, pos, size in self.dir[i + 1:i + 12]:
                    if n2 not in ("THINGS", "LINEDEFS", "SIDEDEFS", "VERTEXES", "SEGS", "SSECTORS", "NODES",
                                  "SECTORS", "REJECT", "BLOCKMAP", "BEHAVIOR"):
                        break
                    out[n2] = self.data[pos:pos + size]
                return out
        raise KeyError(f"no map {name} in the wad")


def checksum(lumps):
    h = hashlib.md5()
    for n in ("THINGS", "LINEDEFS", "SIDEDEFS", "SECTORS"):
        h.update(lumps.get(n, b""))
    return h.hexdigest().upper()


def tex(raw):
    return raw.rstrip(b"\0").decode("latin1").upper()


def read_map(lumps):
    """Doom's binary map as plain lists."""
    verts = [struct.unpack_from("<hh", lumps["VERTEXES"], i) for i in range(0, len(lumps["VERTEXES"]), 4)]
    lines = [dict(zip(("v1", "v2", "flags", "special", "tag", "front", "back"), struct.unpack_from("<7H", lumps["LINEDEFS"], i)))
             for i in range(0, len(lumps["LINEDEFS"]), 14)]
    sides = []
    for i in range(0, len(lumps["SIDEDEFS"]), 30):
        ox, oy, up, lo, mid, sec = struct.unpack_from("<hh8s8s8sH", lumps["SIDEDEFS"], i)
        sides.append(dict(ox=ox, oy=oy, top=tex(up), bottom=tex(lo), mid=tex(mid), sector=sec))
    sectors = []
    for i in range(0, len(lumps["SECTORS"]), 26):
        fl, ce, ft, ct, light, special, tag = struct.unpack_from("<hh8s8shhh", lumps["SECTORS"], i)
        sectors.append(dict(floor=fl, ceil=ce, ftex=tex(ft), ctex=tex(ct), light=light, special=special, tag=tag))
    things = [dict(zip(("x", "y", "angle", "type", "flags"), struct.unpack_from("<hhhhH", lumps["THINGS"], i)))
              for i in range(0, len(lumps["THINGS"]), 10)]
    return verts, lines, sides, sectors, things


# --- GZDoom's translation table -----------------------------------------------------------------------
class Xlat:
    """GZDoom's xlat/doom.txt, read from gzdoom.pk3: linedef types, sector types, line flags."""

    def __init__(self, pk3=GZPK3):
        self.z = zipfile.ZipFile(pk3)
        self.names = {}
        self.lines = {}         # type -> (flags, special name, [args: int or "tag"/"lineid"])
        self.sectors = {}       # type -> (value, nobitmask)
        self.bitmasks = []      # (mask, op, amount)
        self.read("xlat/doom.txt")

    def text(self, name):
        t = self.z.read(name).decode("latin1")
        t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
        return re.sub(r"//[^\n]*", "", t)

    def value(self, expr):
        expr = expr.strip()
        if expr in ("tag", "lineid"):
            return expr
        e = re.sub(r"\b([A-Za-z_]\w*)\b", lambda m: str(self.names[m.group(1)]), expr).replace("/", "//")
        return int(eval(e, {"__builtins__": {}}))

    def read(self, name):
        t = self.text(name)
        for inc in re.findall(r'include\s+"([^"]+)"', t):
            self.read(inc)
        for body in re.findall(r"enum\s*\{(.*?)\}", t, flags=re.S):
            n = -1
            for item in body.split(","):
                item = item.strip()
                if not item:
                    continue
                if "=" in item:
                    k, v = item.split("=", 1)
                    n = self.value(v)
                else:
                    k, n = item, n + 1
                self.names[k.strip()] = n
        for k, v in re.findall(r"define\s+(\w+)\s*\(([^)]*)\)", t):
            self.names[k] = self.value(v)
        for num, flags, special, args in re.findall(r"^\s*(\d+)\s*=\s*([\w|\s]+?)\s*,\s*(\w+)\s*\(([^)]*)\)", t, flags=re.M):
            self.lines[int(num)] = (self.value(flags), special, [self.value(a) for a in args.split(",") if a.strip()])
        for num, rest in re.findall(r"^\s*sector\s+(\d+)\s*=\s*([^;]*);", t, flags=re.M):
            nob = "nobitmask" in rest
            self.sectors[int(num)] = (self.value(rest.replace("nobitmask", "")), nob)
        for mask, op, amount in re.findall(r"^\s*sector\s+bitmask\s+(0x[0-9a-fA-F]+|\d+)\s+(clear|<<=|>>=)?\s*(\d*)\s*;", t, flags=re.M):
            self.bitmasks.append((int(mask, 0), op, int(amount or 0)))

    def sector(self, special):
        """A Doom sector type as GZDoom's P_TranslateSectorSpecial makes it."""
        if not special:
            return 0
        mask = 0
        for m, op, amount in self.bitmasks:
            if op == "clear":
                special &= ~m
            elif op == "<<=":
                mask |= (special & m) << amount
                special &= ~m
            elif op == ">>=":
                mask |= (special & m) >> amount
                special &= ~m
        if special in self.sectors:
            v, nob = self.sectors[special]
            return v if nob else v | mask
        return special | mask


# activation of a translated Doom line: GZDoom's 1 << ((flags >> 1) & 7)
SPAC = {0: "playercross", 1: "playeruse", 2: "monstercross", 3: "impact"}
LINEFLAGS = ["blocking", "blockmonsters", "twosided", "dontpegtop", "dontpegbottom", "secret",
             "blocksound", "dontdraw", "mapped", "passuse", "midtex3d", None, "blocklandmonsters", "blockplayers"]


# --- a piece: one of id's maps as UDMF records -------------------------------------------------------
class Piece:
    def __init__(self, wad, xl, mapname, number, dx=0, dy=0, *, keep=(), start=False, exits="off", music=None):
        lumps = wad.map(mapname)
        self.name = mapname
        self.sum = checksum(lumps)
        if mapname in CHECKSUMS and self.sum != CHECKSUMS[mapname]:
            raise ValueError(f"{mapname} in this doom2.wad is not the one the indices were taken from ({self.sum})")
        self.number, self.dx, self.dy = number, dx, dy
        self.keep = set(keep)
        verts, lines, sides, sectors, things = read_map(lumps)
        self.doom = dict(verts=verts, lines=lines, sides=sides, sectors=sectors, things=things)
        self.music = music if music is not None else MUSIC.get(mapname, "")
        self.untranslated = {}       # Doom type -> count, for types the table does not have
        self.exits = []              # (line index, its special) taken off
        self.verts = [(x + dx, y + dy) for x, y in verts]
        self.sides = []
        for s in sides:
            d = dict(sector=s["sector"])
            if s["ox"]:
                d["offsetx"] = s["ox"]
            if s["oy"]:
                d["offsety"] = s["oy"]
            for k, u in (("top", "texturetop"), ("bottom", "texturebottom"), ("mid", "texturemiddle")):
                if s[k] != "-":
                    d[u] = s[k]
            self.sides.append(d)
        self.sectors = []
        for s in sectors:
            d = dict(heightfloor=s["floor"], heightceiling=s["ceil"], texturefloor=s["ftex"], textureceiling=s["ctex"],
                     lightlevel=s["light"])
            sp = xl.sector(s["special"])
            if sp:
                d["special"] = sp
            if s["tag"]:
                d["id"] = self.tag(s["tag"])
            d["user_doom"] = 1            # classic.zs gives it SECF_FLOORDROP, as GZDoom does to a Doom-format map's
            d["user_piece"] = number
            if self.music:
                d["user_music"] = self.music
            self.sectors.append(d)
        self.lines = []
        for i, l in enumerate(lines):
            d = dict(v1=l["v1"], v2=l["v2"], sidefront=l["front"])
            if l["back"] != 0xFFFF:
                d["sideback"] = l["back"]
            fl = l["flags"]
            if fl & 0x800:                       # xlat's "lineflag 11": garbage in the high bits
                fl &= 0x1FF
            for b, n in enumerate(LINEFLAGS):
                if n and fl & (1 << b):
                    d[n] = True
            if l["tag"]:
                d["id"] = self.tag(l["tag"])     # as GZDoom gives a Doom-format line its tag as its id
            if l["special"]:
                tr = xl.lines.get(l["special"])
                if not tr or tr[1] not in SPECIALS:
                    self.untranslated[l["special"]] = self.untranslated.get(l["special"], 0) + 1
                else:
                    flags, name, args = tr
                    sp = SPECIALS[name]
                    if sp in EXITS and exits == "off":
                        self.exits.append((i, sp))
                    else:
                        d["special"] = sp
                        for k, a in enumerate(args):
                            v = self.tag(l["tag"]) if a in ("tag", "lineid") else a
                            if v:
                                d[f"arg{k}"] = v
                        d[SPAC[(flags >> 1) & 7]] = True
                        if (flags >> 1) & 7 == 3:
                            d["missilecross"] = True     # GZDoom gives a Doom gunshot line SPAC_Impact | SPAC_PCross
                        if flags & 1:
                            d["repeatspecial"] = True
                        if flags & 16 and not (fl & 0x20 and (flags >> 1) & 7 == 1):     # (GZDoom: no monster uses a secret line)
                            d["monsteractivate"] = True
                        if flags & 32:
                            d["firstsideonly"] = True
            if l["tag"] and "special" not in d:
                d["arg0"] = self.tag(l["tag"])     # as GZDoom keeps the tag of a line without a special
            self.lines.append(d)
        self.things = []                # thing i is Doom's thing i (None: taken out), for edits by index
        self.notes = []                 # what trim() and the edits did, for the build's summary
        for t in things:
            if t["type"] in (2, 3, 4, 11) or (t["type"] == 1 and not start):
                self.things.append(None)
                continue
            f = t["flags"]
            d = dict(x=float(t["x"] + dx), y=float(t["y"] + dy), type=t["type"], angle=t["angle"])
            for bit, names in ((1, ("skill1", "skill2")), (2, ("skill3",)), (4, ("skill4", "skill5"))):
                if f & bit:
                    for n in names:
                        d[n] = True
            if f & 8:
                d["ambush"] = True
            d["single"] = not f & 16
            d["coop"] = not f & 64
            d["dm"] = not f & 32
            d["class1"] = d["class2"] = d["class3"] = True     # as GZDoom marks a Doom-format thing
            if f & 128:
                d["friend"] = True
            self.things.append(d)

    def tag(self, t):
        return t if not t or t in self.keep else self.number * TAG_BASE + t

    def bounds(self):
        xs = [v[0] for v in self.verts if v is not None]
        ys = [v[1] for v in self.verts if v is not None]
        return min(xs), min(ys), max(xs), max(ys)

    # --- what lies where --------------------------------------------------------------------------
    def side_sector(self, line, k):
        s = self.lines[line].get("sidefront" if k == 0 else "sideback")
        return None if s is None else self.sides[s]["sector"]

    def sector_at(self, p):
        """The sector p is in (by the nearest line a ray to the east meets), or None in the void."""
        best, hit = None, None
        for i, l in enumerate(self.lines):
            if l is None:
                continue
            a, b = self.verts[l["v1"]], self.verts[l["v2"]]
            if (a[1] > p[1]) == (b[1] > p[1]):
                continue
            x = a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x >= p[0] and (best is None or x < best):
                best, hit = x, (i, a, b)
        if hit is None:
            return None
        i, a, b = hit
        # p is on the line's right (its front) if the cross product is negative
        right = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) < 0
        return self.side_sector(i, 0 if right else 1)

    # --- changes, made in code at build time: indices and coordinates are the map's own (as id made it) --
    # Edits come first, then trim(), then Ajar's cuts: nothing is renumbered until textmap() writes the level
    # (what trim() takes out becomes None), so an index means the same thing all along.
    def set_sector(self, i, **fields):
        """A sector's heightfloor, heightceiling, lightlevel, texturefloor, textureceiling, id (a tag: use
        self.tag(n)), special ..."""
        self.sectors[i].update(fields)
        self.notes.append(f"sector {i}: {fields}")

    def set_side(self, line, front=True, **fields):
        """A line's side: texturetop, texturemiddle, texturebottom, offsetx, offsety. (A side id's map
        shares between lines changes on all of them.)"""
        self.sides[self.lines[line]["sidefront" if front else "sideback"]].update(fields)
        self.notes.append(f"line {line} {'front' if front else 'back'}: {fields}")

    ACTIVATION = ("playercross", "playeruse", "monstercross", "impact", "missilecross", "repeatspecial",
                  "monsteractivate", "firstsideonly")

    def set_line(self, i, special=None, *args, on="playeruse", repeat=False):
        """A line's special, by name (SPECIALS), its arguments and how it is set off; None takes it away."""
        l = self.lines[i]
        for k in [k for k in l if k == "special" or k.startswith("arg") or k in self.ACTIVATION]:
            del l[k]
        if special:
            l["special"] = SPECIALS[special]
            for k, a in enumerate(args):
                if a:
                    l[f"arg{k}"] = a
            l[on] = True
            if repeat:
                l["repeatspecial"] = True
        self.notes.append(f"line {i}: {special or 'no special'}{tuple(args) if args else ''}")

    def move_thing(self, i, x, y, angle=None):
        self.things[i].update(x=float(x + self.dx), y=float(y + self.dy), **({"angle": angle} if angle is not None else {}))
        self.notes.append(f"thing {i} moved to ({x}, {y})")

    def remove_thing(self, i):
        self.notes.append(f"thing {i} (type {self.things[i]['type']}) taken out")
        self.things[i] = None

    def add_thing(self, type, x, y, angle=0, **fields):
        d = dict(x=float(x + self.dx), y=float(y + self.dy), type=type, angle=angle, skill1=True, skill2=True,
                 skill3=True, skill4=True, skill5=True, single=True, coop=True, dm=True, **fields)
        self.things.append(d)
        self.notes.append(f"thing {len(self.things) - 1} (type {type}) added at ({x}, {y})")
        return len(self.things) - 1

    DOORS = (10, 11, 12, 13, 249)        # Door_Close, _Open, _Raise, _LockedRaise, _CloseWaitOpen: with no tag
                                         # they move the line's back sector

    def trim(self, box=None, sectors=None, wall=None):
        """Only part of the map: the sectors given, or those wholly in `box` (x1, y1, x2, y2, the map's own
        coordinates). A two-sided line between a kept sector and one that goes becomes a one-sided wall
        facing the kept one (turned round if need be), with `wall` for its texture or else the kept side's
        upper or lower texture, or else that of a wall of the same sector; a door special on it that moves
        its (now gone) back sector is taken off. Lines, sides, vertices and things of what goes are taken
        out (None); a thing goes by the sector it stands in."""
        by_sector = {}
        for i, l in enumerate(self.lines):
            if l is None:
                continue
            for k in ("sidefront", "sideback"):
                if k in l:
                    by_sector.setdefault(self.sides[l[k]]["sector"], []).append(i)
        if sectors is None:
            x1, y1, x2, y2 = box[0] + self.dx, box[1] + self.dy, box[2] + self.dx, box[3] + self.dy
            keep = {sec for sec, ls in by_sector.items()
                    if all(x1 <= self.verts[self.lines[i][k]][0] <= x2 and y1 <= self.verts[self.lines[i][k]][1] <= y2
                           for i in ls for k in ("v1", "v2"))}
        else:
            keep = set(sectors)
        things = 0
        for i, t in enumerate(self.things):          # (while the map is whole)
            if t is not None and self.sector_at((t["x"], t["y"])) not in keep:
                self.things[i] = None
                things += 1

        def plain_wall(sec):
            for i in by_sector.get(sec, []):
                l = self.lines[i]
                if l is not None and "sideback" not in l and self.sides[l["sidefront"]].get("texturemiddle"):
                    return self.sides[l["sidefront"]]["texturemiddle"]
            return "STARTAN2"

        walled, gone, taken = [], 0, []
        for i, l in enumerate(self.lines):
            if l is None:
                continue
            f = self.sides[l["sidefront"]]["sector"]
            b = self.sides[l["sideback"]]["sector"] if "sideback" in l else None
            if f in keep and (b is None or b in keep):
                continue
            if f not in keep and b not in keep:
                self.lines[i] = None
                gone += 1
                continue
            if f not in keep:                          # the kept sector is behind: turn the line round
                l["v1"], l["v2"] = l["v2"], l["v1"]
                l["sidefront"] = l["sideback"]
            del l["sideback"]
            l.pop("twosided", None)
            l["blocking"] = True
            sd = dict(self.sides[l["sidefront"]])
            sd["texturemiddle"] = wall or sd.get("texturetop") or sd.get("texturebottom") or plain_wall(self.sides[l["sidefront"]]["sector"])
            sd.pop("texturetop", None)
            sd.pop("texturebottom", None)
            self.sides.append(sd)                      # a side of its own (id's maps share some)
            l["sidefront"] = len(self.sides) - 1
            if l.get("special") in self.DOORS and not l.get("arg0"):
                taken.append((i, l["special"]))
                for k in [k for k in l if k == "special" or k.startswith("arg") or k in self.ACTIVATION]:
                    del l[k]
            walled.append(i)
        for i in range(len(self.sectors)):
            if i not in keep:
                self.sectors[i] = None
        used_s, used_v = set(), set()
        for l in self.lines:
            if l is not None:
                used_v |= {l["v1"], l["v2"]}
                used_s |= {l[k] for k in ("sidefront", "sideback") if k in l}
        self.sides = [sd if i in used_s else None for i, sd in enumerate(self.sides)]
        self.verts = [v if i in used_v else None for i, v in enumerate(self.verts)]
        self.walled = walled
        self.notes.append(f"trimmed to {len(keep)} of {len(self.sectors)} sectors: {len(walled)} lines made walls, "
                          f"{gone} lines and {things} things taken out, door specials taken off lines {[i for i, _ in taken]}")
        for i in walled:
            self.lines[i]["user_cut"] = 1              # (classic.zs's test finds them so)
        return keep

    # --- Ajar's additions -------------------------------------------------------------------------
    def cut(self, line, at, line_id, target, *, far_colour=None, width=64):
        """Cut a frame (or with `far_colour` that door's far side) into the one-sided wall `line`:
        its mouth runs from `at` units along the line (from its first vertex) for 64,
        and ajarmap.recess's recess and stub lie behind it, in the void. Refuses a wall
        that is two-sided, not straight along x or y, too short, too low, or with
        anything but void behind it. Returns the recess's mouth (m1, m2) and `out`."""
        l = self.lines[line]
        if "sideback" in l:
            raise ValueError(f"{self.name} line {line} is two-sided")
        a, b = self.verts[l["v1"]], self.verts[l["v2"]]
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        if a[0] != b[0] and a[1] != b[1]:
            raise ValueError(f"{self.name} line {line} does not run along x or y")
        if at < 0 or at + width > length:
            raise ValueError(f"{self.name} line {line} is {length:.0f} long: no room for 64 at {at}")
        d = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
        out = (-d[1], d[0])                     # the front (the room) is on the line's right
        m1 = (a[0] + d[0] * at, a[1] + d[1] * at)
        m2 = (a[0] + d[0] * (at + width), a[1] + d[1] * (at + width))
        sec = self.sectors[self.sides[l["sidefront"]]["sector"]]
        floor, ceil = sec["heightfloor"], sec["heightceiling"]
        if ceil - floor < ajarmap.DOOR_H:
            raise ValueError(f"{self.name} line {line}: the room is {ceil - floor} high, a door needs {ajarmap.DOOR_H}")
        deep = ajarmap.DEPTH + ajarmap.STUB
        far1 = (m1[0] + out[0] * deep, m1[1] + out[1] * deep)
        far2 = (m2[0] + out[0] * deep, m2[1] + out[1] * deep)
        xs, ys = [m1[0], m2[0], far1[0], far2[0]], [m1[1], m2[1], far1[1], far2[1]]
        box = (min(xs), min(ys), max(xs), max(ys))
        # nothing but the wall itself may touch the recess's box, edges included, except at the
        # mouth's two ends (the walls that meet this one there); and the box is in no sector
        hit = []
        for i, o in enumerate(self.lines):
            if i == line or o is None:
                continue
            seg = _clip(self.verts[o["v1"]], self.verts[o["v2"]], box)
            if seg and not (_same(seg[0], seg[1]) and (_same(seg[0], m1) or _same(seg[0], m2))):
                hit.append(i)
        mid = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
        if hit or self.sector_at(mid) is not None:
            raise ValueError(f"{self.name} line {line}: behind it is not void (lines {hit[:5]}, sector {self.sector_at(mid)})")
        # the recess as ajarmap makes it, in a map of its own, then sewn in
        m = Map()
        ajarmap.recess(m, m1, m2, out, floor, line_id, target, far_colour=far_colour)
        verts, lines, sides, sectors, things = m.parts()
        secbase = len(self.sectors)
        vmap = {i: self.vertex(v) for i, v in enumerate(verts)}
        # its lines and sides but the mouth's own: the wall's middle piece stands in for that line (GZDoom
        # loses its way in a UDMF map with a sidedef no line uses)
        mouth = next(ld for ld in lines if {verts[ld["v1"]], verts[ld["v2"]]} == {m1, m2})
        dropped = {mouth.get("sidefront"), mouth.get("sideback")}
        smap = {}
        for i, sd in enumerate(sides):
            if i not in dropped:
                smap[i] = len(self.sides)
                self.sides.append(dict(sd, sector=sd["sector"] + secbase))
        for ld in lines:
            if ld is not mouth:
                nd = dict(ld, v1=vmap[ld["v1"]], v2=vmap[ld["v2"]])
                for k in ("sidefront", "sideback"):
                    if k in nd:
                        nd[k] = smap[nd[k]]
                self.lines.append(nd)
        for s in sectors:
            self.sectors.append(dict(s, user_piece=self.number, **({"user_music": self.music} if self.music else {})))
        for t in things:
            self.things.append(t)
        # the wall: split at the mouth; the middle piece is the mouth, two-sided, with the wall's
        # texture above the recess (pegged to the ceiling, as the wall's own is)
        fside = self.sides[l["sidefront"]]
        wall = fside.get("texturemiddle", "-")
        i1, i2 = self.vertex(m1), self.vertex(m2)
        first, last = dict(l), dict(l)
        pieces = []
        if at > 0:
            pieces.append(dict(first, v2=i1))
        mside = dict(fside, offsetx=fside.get("offsetx", 0) + at, texturetop=wall)
        mside.pop("texturemiddle", None)
        if at > 0:
            self.sides.append(mside)
            front = len(self.sides) - 1
        else:                                   # the wall's own side becomes the mouth's: no side left unused
            front = l["sidefront"]
            self.sides[front] = mside
        self.sides.append(dict(sector=secbase))        # the recess (ajarmap.recess's first sector)
        md = dict((k, v) for k, v in l.items() if k not in ("blocking", "dontpegbottom", "special", "id") and not k.startswith("arg"))
        md.update(v1=i1, v2=i2, sidefront=front, sideback=len(self.sides) - 1, twosided=True, dontpegtop=True)
        for k, v in mouth.items():
            if k in ("special", "playeruse", "repeatspecial") or k.startswith("arg"):
                md[k] = v
        pieces.append(md)
        if at + width < length:
            self.sides.append(dict(fside, offsetx=fside.get("offsetx", 0) + at + width))
            pieces.append(dict(last, v1=i2, sidefront=len(self.sides) - 1))
        self.lines[line] = pieces[0]            # the wall's own index stays on its first piece
        self.lines += pieces[1:]
        return m1, m2, out

    def gate(self, line, line_id, target):
        """One of the map's own Doom doors made a frame, as the Doom door lab does it while
        MAP22 loads (doomlab.zs, AjarDoomLabPost), here at build time: the door's face `line`
        gets the id `line_id` (4001..4049: a "gate", which stays a Doom door) and
        Line_SetPortal to `target`; its own special is kept in an AjarDoomNote thing
        (args: the line's index in the level, set by textmap(); its special and arguments 1
        to 3), which AjarDoomLab.WorldLoaded puts back; an AjarFrame stands 8 in front."""
        l = self.lines[line]
        a, b = self.verts[l["v1"]], self.verts[l["v2"]]
        n = math.hypot(b[0] - a[0], b[1] - a[1])
        if "sideback" not in l or not l.get("special"):
            raise ValueError(f"{self.name} line {line} is not a Doom door's face")
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        self.things.append(dict(x=float(mid[0]), y=float(mid[1]), type=NOTE_T, id=line_id, arg0=line,
                                arg1=l["special"], arg2=l.get("arg1", 0), arg3=l.get("arg2", 0), arg4=l.get("arg3", 0),
                                skill1=True, skill2=True, skill3=True, skill4=True, skill5=True, single=True, coop=True, dm=True))
        p = (mid[0] + (b[1] - a[1]) / n * 8, mid[1] - (b[0] - a[0]) / n * 8)
        self.things.append(dict(x=float(p[0]), y=float(p[1]), type=ajarmap.FRAME_T, id=line_id, arg0=line_id,
                                skill1=True, skill2=True, skill3=True, skill4=True, skill5=True, single=True, coop=True, dm=True))
        for k in ("arg0", "arg1", "arg2", "arg3", "arg4"):
            l.pop(k, None)
        l.update(id=line_id, special=156, arg0=target, arg1=line_id, arg2=1, arg3=1)
        return a, b

    def vertex(self, v):
        for i, w in enumerate(self.verts):
            if w is not None and abs(w[0] - v[0]) < 1e-6 and abs(w[1] - v[1]) < 1e-6:
                return i
        self.verts.append(v)
        return len(self.verts) - 1


def _same(p, q):
    return abs(p[0] - q[0]) < 1e-6 and abs(p[1] - q[1]) < 1e-6


def _clip(a, b, box):
    """The part of the segment a-b in the closed box, or None."""
    x1, y1, x2, y2 = box
    t0, t1 = 0.0, 1.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    for p, q in ((-dx, a[0] - x1), (dx, x2 - a[0]), (-dy, a[1] - y1), (dy, y2 - a[1])):
        if p == 0:
            if q < 0:
                return None
        else:
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
    if t0 > t1 + 1e-9:
        return None
    return (a[0] + dx * t0, a[1] + dy * t0), (a[0] + dx * t1, a[1] + dy * t1)


# --- the joined level -----------------------------------------------------------------------------------
def textmap(pieces, own=None):
    """The level: the pieces in order, then Ajar's own map (a udmf.Map) after them."""
    def val(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, str):
            return '"%s"' % v
        if isinstance(v, float):
            return repr(v) if v != int(v) else f"{v:.1f}"
        return str(v)

    def block(kind, d):
        return kind + "{" + "".join(f"{k}={val(v)};" for k, v in d.items()) + "}\n"

    verts, lines, sides, sectors, things = [], [], [], [], []
    parts = [(p.verts, p.lines, p.sides, p.sectors, p.things) for p in pieces]
    if own is not None:
        parts.append(own.parts())
    def index(items, base):          # old index -> new, what is None (taken out by Piece.trim) left out
        out = {}
        for i, x in enumerate(items):
            if x is not None:
                out[i] = base + len(out)
        return out

    for cv, cl, cs, csec, cth in parts:
        vi, si, seci, li = index(cv, len(verts)), index(cs, len(sides)), index(csec, len(sectors)), index(cl, len(lines))
        verts += [v for v in cv if v is not None]
        for ld in cl:
            if ld is None:
                continue
            ld = dict(ld, v1=vi[ld["v1"]], v2=vi[ld["v2"]])
            for k in ("sidefront", "sideback"):
                if k in ld:
                    ld[k] = si[ld[k]]
            lines.append(ld)
        sides += [dict(sd, sector=seci[sd["sector"]]) for sd in cs if sd is not None]
        sectors += [d for d in csec if d is not None]
        things += [dict(t, arg0=li[t["arg0"]]) if t["type"] == NOTE_T else t for t in cth if t is not None]     # see Piece.gate
    out = ['namespace="zdoom";\n']
    for x, y in verts:
        out.append(block("vertex", dict(x=float(x), y=float(y))))
    for ld in lines:
        out.append(block("linedef", ld))
    for sd in sides:
        out.append(block("sidedef", sd))
    for d in sectors:
        out.append(block("sector", d))
    for d in things:
        out.append(block("thing", d))
    return "".join(out)


def wad(name, text):
    lumps = [(name, b""), ("TEXTMAP", text.encode()), ("ENDMAP", b"")]
    data, direc, pos = b"", b"", 12
    for n, d in lumps:
        direc += struct.pack("<ii8s", pos, len(d), n.encode())
        data += d
        pos += len(d)
    return b"PWAD" + struct.pack("<ii", len(lumps), pos) + data + direc


# --- the lab levels ---------------------------------------------------------------------------------------
# Frames 101 (Entryway, the first room), 102 (Entryway, by its exit), 103 (Dead Simple), 104 (the Ajar room);
# far sides 201 (RED: Dead Simple, by its start) and 202 (BLUE: the Ajar room); 4001 Entryway's exit door
# (line 166, door sector 37, 64 wide) made a frame that stays a Doom door. Piece n's tags are 10000 n + its own.
E_DX, E_DY = 0, 0                   # Entryway as it is
D_DX, D_DY = 6144, 0                # Dead Simple, east of it (Entryway ends at x 2072, Dead Simple begins at 4224)
ROOM = (-256, 3200, 256, 3584)      # the Ajar room, north of Entryway (which ends at y 2688)


def entryway(wadf, xl, n=1):
    p = Piece(wadf, xl, "MAP01", n, E_DX, E_DY, start=True)
    p.cut(16, 0, 101, 201)            # the first room's north wall, west of the steps: (-320, 1280)-(-256, 1280)
    p.cut(128, 384, 102, 201)         # the big room's north wall by the exit door: (832, 960)-(896, 960)
    p.gate(166, 4001, 201)            # the exit door's south face: (960, 1048)-(1024, 1048)
    return p


def dead_simple(wadf, xl, n=2):
    p = Piece(wadf, xl, "MAP07", n, D_DX, D_DY, keep=(666, 667))
    p.cut(62, 944, 201, 101, far_colour=ajarmap.RED)      # the yard's east wall, facing the start: y -176..-240
    p.cut(61, 1856, 103, 201)                             # the yard's north wall: x 128..192
    return p


def ajar_room():
    m = Map()
    x1, y1, x2, y2 = ROOM
    m.sector([(x1, y1), (x1, y2), (x2, y2), (x2, y1)], ceil=160, light=200, color=0xE8F0FF)
    ajarmap.recess(m, (-32, y2), (32, y2), (0, 1), 0, ajarmap.far_id(ajarmap.BLUE), 101, far_colour=ajarmap.BLUE)
    ajarmap.recess(m, (x1, 3360), (x1, 3424), (-1, 0), 0, 104, 201)
    # RED and BLUE lean in Entryway's first room, north of the start
    ajarmap.door(m, ajarmap.RED, -176, 1100, angle=270)
    ajarmap.door(m, ajarmap.BLUE, -16, 1100, angle=270)
    return m


# CLASSIC4: two further pieces far out, to see what large coordinates do. Nirvana (MAP21) at (16384, 0)
# with frame 105 in its start room, The Catacombs (MAP22) at (24576, 16384) with GREEN's far side (203) in
# its start room; GREEN leans in Entryway's first room beside RED and BLUE.
FAR = {"MAP21": (16384, 0), "MAP22": (24576, 16384)}
# AJAR_CLASSIC_FAR22=40960,16384 puts The Catacombs elsewhere (the lab's test of coordinates past 32767)
if os.environ.get("AJAR_CLASSIC_FAR22"):
    FAR["MAP22"] = tuple(int(v) for v in os.environ["AJAR_CLASSIC_FAR22"].split(","))


# Nirvana is also the lab's try at changing a map (Vadim, 2026-11-26: the Doom maps are raw material, "modified
# in different ways anyway"): a few edits by index, then only its south strip kept (TRIM21, in its own
# coordinates: the start room and the east half of the long rooms west of it, which are cut through), then the
# frame cut in.
TRIM21 = (3000, 3000, 4700, 3870)


def nirvana(wadf, xl, n=3):
    p = Piece(wadf, xl, "MAP21", n, *FAR["MAP21"])
    p.set_sector(17, lightlevel=208, texturefloor="FLOOR1_6")      # the start room: lighter, a red floor
    p.set_sector(20, heightfloor=40, id=p.tag(900))                 # its middle square: 24 higher, and a tag of its own
    p.set_side(29, texturemiddle="MARBFACE")                        # the start room's east wall
    p.set_line(29, "Light_ChangeToValue", p.tag(900), 64, repeat=True)   # which now darkens the square, by USE
    p.remove_thing(70)                                              # the super shotgun on the square
    p.move_thing(50, 4224, 3200)                                    # a medikit, to the frame's front
    p.add_thing(2019, 4480, 3200)                                   # a blue armour beside it
    p.trim(box=TRIM21)
    p.cut(30, 320, 105, 201)                            # the start room's south wall: x 4288..4224 of MAP21
    return p


def far_pieces(wadf, xl):
    n21 = nirvana(wadf, xl)
    n22 = Piece(wadf, xl, "MAP22", 4, *FAR["MAP22"])
    n22.cut(582, 128, 203, 101, far_colour=ajarmap.GREEN)  # the start room's south wall: x -520..-584 of MAP22
    return [n21, n22]


def levels(wadf, xl):
    """name -> (pieces, Ajar's own map)"""
    out = {"CLASSIC": ([entryway(wadf, xl), dead_simple(wadf, xl)], ajar_room())}
    room = ajar_room()
    ajarmap.door(room, ajarmap.GREEN, -96, 1150, angle=270)
    out["CLASSIC4"] = ([entryway(wadf, xl), dead_simple(wadf, xl)] + far_pieces(wadf, xl), room)
    return out


def build(out=os.environ.get("AJAR_CLASSIC_OUT") or "build/ajar-classic.pk3"):
    """build/ajar-classic.pk3: the joined levels, and nothing else (their MAPINFO and ZScript are in ajar.pk3)."""
    t0 = time.time()
    wadf, xl = Wad(IWAD), Xlat()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, (pieces, own) in levels(wadf, xl).items():
            text = textmap(pieces, own)
            z.writestr(f"maps/{name}.wad", wad(name, text))
            print(f"{name}: {len(text) // 1024} KB of TEXTMAP; " + "; ".join(
                f"{p.name} at ({p.dx}, {p.dy}) spans {p.bounds()}, tags {p.number * TAG_BASE}+"
                + (f" (kept {sorted(p.keep)})" if p.keep else "")
                + (f", exits off: lines {[i for i, _ in p.exits]}" if p.exits else "")
                + (f", UNTRANSLATED {p.untranslated}" if p.untranslated else "")
                + (f", changed: {'; '.join(p.notes)}" if p.notes else "") for p in pieces))
    print(f"built {out} from {IWAD} in {time.time() - t0:.1f} s")


# --- tools to choose indices ---------------------------------------------------------------------------
def survey(wadf, xl, name):
    p = Piece(wadf, xl, name, 0, start=True, exits="keep")
    print(name, "checksum", p.sum, "bounds", p.bounds(), "lines", len(p.lines), "sides", len(p.sides),
          "sectors", len(p.sectors), "things", len(p.things))
    print("untranslated types", p.untranslated)
    sp = {}
    for l in p.doom["lines"]:
        sp[l["special"]] = sp.get(l["special"], 0) + 1
    print("linedef types", dict(sorted(sp.items())))
    print("sector types", sorted({s["special"] for s in p.doom["sectors"]}), "tags", sorted({s["tag"] for s in p.doom["sectors"]}))
    for t in p.doom["things"]:
        if t["type"] in (1,):
            print("start", t)


def walls(wadf, xl, name, x, y, r=512):
    """One-sided walls near (x, y) along x or y, long enough, with void behind and a tall enough room."""
    p = Piece(wadf, xl, name, 0, start=True, exits="keep")
    for i, l in enumerate(p.lines):
        if "sideback" in l:
            continue
        a, b = p.verts[l["v1"]], p.verts[l["v2"]]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if math.hypot(mx - x, my - y) > r:
            continue
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        sec = p.sides[l["sidefront"]]["sector"]
        s = p.sectors[sec]
        ok = []
        for at in range(0, int(length) - 63, 16):
            try:
                q = Piece(wadf, xl, name, 0, start=True, exits="keep")
                q.cut(i, at, 101, 201)
                ok.append(at)
            except ValueError:
                pass
        print(f"line {i} {a}->{b} len {length:.0f} sector {sec} floor {s['heightfloor']} ceil {s['heightceiling']} "
              f"tex {p.sides[l['sidefront']].get('texturemiddle')} cut at {ok[:3]}{'...' if len(ok) > 3 else ''}{ok[-1:] if len(ok) > 3 else ''}")


# --- the check: id's maps converted, beside GZDoom's own loading of them ----------------------------------
# build/classic-check.pk3 holds every map of doom2.wad converted as a piece (number 0: tags as they are,
# exits kept) under the name CVxx, and a handler that prints what the engine loaded, line by line, for
# whichever map is loaded; build/classic-check.cfg loads MAPxx and CVxx in turn. `compare LOG` reads the
# printout and lists every difference. (In build/ only: it holds id's maps.)
DUMPER = """
class ClassicDump : EventHandler
{
	override void WorldLoaded(WorldEvent e)
	{
		string m = level.mapname;
		// what classic.zs does at load (AjarClassic.WorldLoaded)
		for (int i = 0; i < level.sectors.Size(); i++) if (level.sectors[i].GetUDMFInt('user_doom')) level.sectors[i].Flags |= Sector.SECF_FLOORDROP;
		for (int i = 0; i < level.lines.Size(); i++)
		{
			Line l = level.lines[i];
			string ids = "";
			for (int k = 0; k < l.CountIDs(); k++) ids = ids .. " " .. l.GetID(k);
			Console.Printf("CDUMP %s L %d %d %d %d %d %d %d act %d flags %x ids%s", m, i, l.special, l.args[0], l.args[1], l.args[2], l.args[3], l.args[4],
				l.activation, l.flags, ids);
			for (int k = 0; k < 2; k++)
			{
				Side s = l.sidedef[k];
				if (!s) continue;
				Console.Printf("CDUMP %s D %d %d %s %s %s %.1f %.1f %.1f %.1f sec %d", m, i, k, TexMan.GetName(s.GetTexture(Side.top)),
					TexMan.GetName(s.GetTexture(Side.mid)), TexMan.GetName(s.GetTexture(Side.bottom)),
					s.GetTextureXOffset(Side.mid), s.GetTextureYOffset(Side.mid), s.GetTextureXOffset(Side.top), s.GetTextureYOffset(Side.bottom), s.sector.Index());
			}
		}
		for (int i = 0; i < level.sectors.Size(); i++)
		{
			Sector s = level.sectors[i];
			string tags = "";
			for (int k = 0; k < s.CountTags(); k++) tags = tags .. " " .. s.GetTag(k);
			Console.Printf("CDUMP %s S %d %.1f %.1f %s %s light %d special %d damage %d flags %x tags%s", m, i, s.CenterFloor(), s.CenterCeiling(),
				TexMan.GetName(s.GetTexture(Sector.floor)), TexMan.GetName(s.GetTexture(Sector.ceiling)), s.lightlevel, s.special,
				s.damageamount, s.Flags, tags);
		}
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
			Console.Printf("CDUMP %s T %s %.0f %.0f %d sf %x amb %d", m, a.GetClassName(), a.SpawnPoint.x, a.SpawnPoint.y, a.SpawnAngle,
				a.SpawnFlags, a.bAmbush);
		Console.Printf("CDUMP %s END secrets %d monsters %d items %d", m, level.total_secrets, level.total_monsters, level.total_items);
	}
}
"""


def check(wadf, xl, out):
    names = [f"MAP{i:02d}" for i in range(1, 33)]
    cfg = []
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("zscript.zs", 'version "4.12"\n' + DUMPER)
        z.writestr("mapinfo.txt", 'gameinfo { AddEventHandlers = "ClassicDump" }\n')
        for n in names:
            p = Piece(wadf, xl, n, 0, start=True, exits="keep")
            z.writestr(f"maps/CV{n[3:]}.wad", wad(f"CV{n[3:]}", textmap([p])))
            cfg.append(f"map {n}; wait 3; map CV{n[3:]}; wait 3")
    with open(os.path.splitext(out)[0] + ".cfg", "w") as f:
        f.write("wait 5; " + "; ".join(cfg) + "; quit\n")


def compare(log):
    maps = {}
    for line in open(log, encoding="latin1"):
        if not line.startswith("CDUMP "):
            continue
        _, m, rest = line.rstrip("\n").split(" ", 2)
        maps.setdefault(m, []).append(rest)
    total = 0
    for i in range(1, 33):
        a, b = maps.get(f"MAP{i:02d}", []), maps.get(f"CV{i:02d}", [])
        if not a or not b:
            print(f"MAP{i:02d}: not loaded ({len(a)}, {len(b)} lines)")
            continue
        ta = sorted(re.sub(r"sf 7e(.)", r"sf 70\1", x) for x in a if x.startswith("T ") and not x.startswith(("T DoomPlayer", "T Player")))
        tb = sorted(re.sub(r"sf 7e(.)", r"sf 70\1", x) for x in b if x.startswith("T ") and not x.startswith(("T DoomPlayer", "T Player")))
        # GZDoom keeps bit 0x800 of a Doom-format line's flags where it was set (MAP14); it means nothing once loaded
        ra = [re.sub(r" ids 0$", " ids", re.sub(r"flags (\w*)", lambda m: "flags %x" % (int(m.group(1), 16) & ~0x800), x) if x.startswith("L ") else x)
              for x in a if not x.startswith("T ")]
        rb = [x for x in b if not x.startswith("T ")]
        diffs = [(x, y) for x, y in zip(ra, rb) if x != y]
        if len(ra) != len(rb):
            diffs.append((f"{len(ra)} records", f"{len(rb)} records"))
        sa, sb = set(ta), set(tb)
        tdiff = sorted(sa - sb)[:6] + ["/"] + sorted(sb - sa)[:6] if sa != sb or len(ta) != len(tb) else []
        total += len(diffs) + (1 if tdiff else 0)
        print(f"MAP{i:02d}: {len(ra)} records, {len(ta)} things: {len(diffs)} differences{', things differ' if tdiff else ''}")
        for x, y in diffs[:12]:
            print(f"    id's: {x}\n    ours: {y}")
        if tdiff:
            print("    things (id's only / ours only):", tdiff)
    print("differences in all:", total)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "build":
        if not os.path.exists(IWAD) or not os.path.exists(GZPK3):
            print(f"no {'doom2.wad' if not os.path.exists(IWAD) else 'gzdoom.pk3'} found: build/ajar-classic.pk3 (the joined Doom II maps) not built")
            sys.exit(0)
        build()
    elif args[0] == "survey":
        w, x = Wad(IWAD), Xlat()
        for n in args[1:]:
            survey(w, x, n)
    elif args and args[0] == "walls":
        walls(Wad(IWAD), Xlat(), args[1], float(args[2]), float(args[3]), float(args[4]) if len(args) > 4 else 512)
    elif args and args[0] == "check":
        check(Wad(IWAD), Xlat(), "build/classic-check.pk3")
    elif args and args[0] == "compare":
        compare(args[1])
