# Ajar — plan

A first-person game on the GZDoom engine where your main tool is a door.
Idea 1 from `../IDEAS.md`. Status: playable test level (see "Prototype status").

## Pitch

You carry a door. Hang it in any empty frame and it opens onto the place it
has always opened onto. Take it down and that way is closed again. Every
level is a space you rewire: bring the far room to you, send the thing chasing
you somewhere worse, join two places that were never meant to touch.

## Core rules

1. **A door remembers its far side.** Each door is bound to one fixed place
   (its *far side*). Wherever the door hangs, stepping through arrives there.
2. **Frames are where doors go.** Levels are full of empty door frames. A
   frame with no door is a blank wall recess.
3. **You carry one door at a time** (upgradable later). Unhinging takes a
   moment and leaves you exposed.
4. **Everything uses doors.** Enemies, projectiles, light, sound and physics
   objects pass through a hung door exactly as the player does.
5. **A door works both ways.** Whatever is on the far side can come to you.

These five rules should be enough to generate the whole game. New levels add
situations, not new rules, with a small number of door *types* as the only
exceptions.

## What the player does with it

- **Routing:** hang the door where you need the far side to be (the key room
  is across a chasm; bring its door to your side).
- **Disposal:** hang a door whose far side is a pit, a furnace or the sky in
  the path of a charging enemy.
- **Redirection:** catch a projectile volley in a door and let it come out
  behind the shooters.
- **Escape:** carry your way out with you. Being cornered with a door on your
  back is not being cornered.
- **Denial:** take a door away so reinforcements cannot arrive.
- **Chaining:** two doors, two frames — build a shortcut loop for a fight.

## Door types (introduced gradually)

| Door | Behaviour | Introduced |
|---|---|---|
| Plain | Fixed far side | Act 1 |
| Pair | Two doors that lead to each other; no fixed far side | Act 2 |
| One-way | You can pass, things on the far side cannot | Act 2 |
| Heavy | Slow to carry, cannot be unhinged by enemies | Act 3 |
| Small | Hatch-sized: objects and small enemies only | Act 3 |
| Tilted | Far side is a floor or ceiling: you fall out of it | Act 4 |
| Stray | One shot: opens onto a random place, then vanishes on a timer (see "Stray door") | Level 5 |
| Flip | Two-coloured, two far sides: each hanging opens onto the other one (see "Flip door") | After level 5 |
| Stale | Far side is the same place at an earlier time (see "Time doors") | Act 5 (stretch) |

## Combat

Open decision (see below). Working assumption: **the door is the star, with
a small supporting arsenal** — two or three simple weapons that are
deliberately not enough on their own, so fights are won by placement.

Enemy roster is designed around the door, not around damage numbers:

- **Chargers** — run in straight lines; made to be redirected.
- **Lobbers** — slow arcing projectiles; made to be caught and returned.
- **Hinge-pickers** — unhinge your doors and carry them off.
- **Followers** — come through after you, so escape needs a second step.
- **Wardens** — cannot pass through doors at all; block frames with their bodies.
- **Squatters** — live on a door's far side and come out when it is hung.

## Engine feasibility

To be proven in the prototype before any level design. These are my
expectations of GZDoom, not yet verified:

- **Retargetable portals.** Frames and far sides are pre-authored linedefs
  with line portals (`Line_SetPortal`); hanging a door calls
  `Line_SetPortalTarget` on both lines. An untargeted portal line should
  render as an ordinary wall.
- **Interactive portals** carry actors, projectiles and hitscans. Linked
  (static) portals cannot be retargeted, so sound propagation and some AI
  pathing across a door will need ZScript help.
- **Constraints to design around:** frame and far-side lines must be the same
  length; portal lines should be one-sided; recursion depth when two doors
  face each other is limited; monsters do not path through portals on their
  own and need scripted "see door, use door" behaviour.
- **Tilted doors** (wall-to-floor) are not native. Likely faked with a
  teleport plus momentum change, without a seamless view. Stretch goal.
- **The carried door** is a weapon-slot viewmodel plus a use-action on frames;
  the hung door is an actor (or polyobject) for the swing animation.

If retargeting proves unreliable, the fallback is silent teleport lines with
camera textures for the view through the door. Worse-looking, but it keeps
the game.

## Look and sound

Open decision. Working assumption: a small, strict, original style that a
script can generate — flat or lightly textured surfaces, strong colour per
far side (each door's colour tells you where it leads), few sprites, heavy
use of lighting and geometry, for everything Ajar adds. Doom's own
monsters and weapons are used as they are (see "Doom II mod").

Readability rule: **the player must always know where a door leads before
stepping through it** — colour, a glyph on the door, and the view through it.

## Campaign structure

About 32 levels in five acts plus a hub. Each act teaches, combines, then
tests.

| Act | Levels | Theme | New ideas |
|---|---|---|---|
| 1. Hinges | 6 | Learning to carry | Plain door, frames, routing, first disposal |
| 2. Company | 6 | Doors work both ways | Enemies use doors, Pair and One-way doors, hinge-pickers |
| 3. Weight | 7 | Physics and scale | Heavy and Small doors, objects, water and light through doors |
| 4. Angles | 6 | Wrong-way-up | Tilted doors, falling as movement, vertical levels |
| 5. Stale air | 6 | Doors that lead to before | Stale doors, levels that fold back on themselves |
| Finale | 1 | One level, every door | — |

The hub is a corridor of frames: each finished act leaves a door there.
Secret levels are reached by hanging a door from one act in a frame in another.

Per-level outlines get written act by act, after the prototype tells us what
is actually fun.

## Project layout

```
ajar/
  PLAN.md
  tools/        map generator and build scripts (Python)
  src/
    zscript/    door, frame, player, enemies
    maps/       generated UDMF maps
    graphics/ sounds/ ...
  build/        ajar.ipk3 (generated, not committed)
```

Maps are generated from scripts rather than drawn in an editor, so frames,
far sides and portal line pairs are declared once and stay consistent. The
build produces `build/ajar.pk3`, run with `gzdoom -iwad doom2.wad -file build/ajar.pk3`.

## Milestones

1. **M0 — Standalone.** Dropped: Ajar is a Doom II mod (see "Doom II mod").
2. **M1 — Portal proof.** One room, two frames, one far side. Retarget at
   runtime by keypress. Answers the feasibility questions above.
3. **M2 — The door as an object.** Pick up, carry, hang, unhinge; viewmodel,
   swing animation, door colour and glyph.
4. **M3 — Things through doors.** One enemy of each of three kinds
   (charger, lobber, follower) with door-aware behaviour; projectiles and
   objects passing through.
5. **M4 — Vertical slice.** Three finished levels from Act 1 with final-ish
   look and sound. Decide here whether the game is fun and what to change.
6. **M5 — Act 1 complete,** then one act per milestone.
7. **Final — Hub, finale, secrets, balance, packaging.**

M1 is the gate: nothing after it starts until retargeting works or the
fallback is chosen. (Passed: retargeting works.)

Order from here: M3, M4, then M5 onwards.

## Doom II mod (decided 2026-11-14)

Ajar is a mod for Doom II: it requires the player's own `doom2.wad` and
uses Doom's monsters, weapons, sounds, palette and menus. This replaces the
earlier plan to go standalone (M0 is dropped) and the "no Doom assets" rule.
Reason (user): the fun is the door ideas on top of familiar monsters and
gunplay. Nothing from `doom2.wad` may be copied into the pk3; it is only
referenced. Freedoom's `freedoom2.wad` remains a possible free host later.

- Doom monsters do not see or chase through a hung door by themselves.
  Every one is given an `AjarSense` item (`src/zscript/enemies.zs`): when it
  can see the player only through a door, it chases an unseen lure standing
  where the player appears to be, which walks it through the door.
  `MAP=TEST MODE=7 ./tools/smoke.sh` checks a zombie waking, following and
  attacking. Limits: it does not shoot through a door, only follows; and a
  monster with no view of the door at all does not look for it.
- The player keeps Doom's weapons; the HUD shows health, ammo and the
  carried door.
- Ajar's own monsters should be about doors, not copies of Doom ones. For
  now there is one, the thief (see "Handoff"). The enemy roster under
  "Combat" predates this decision and is only a list of ideas.

## Open decisions

1. **Guns.** Small supporting arsenal (assumed), or no guns at all?
2. **Tone.** Unsettling, playful, or straight action? Assumed: playful and
   slightly uncanny.
3. **Art source.** Fully generated original style (assumed), or Freedoom
   assets as temporary placeholders during prototyping?
4. **Story.** None, environmental only (assumed), or written narrative?
5. **Crossover with idea 2.** Stale doors in Act 5 borrow from "Thirty
   Moments". Keep, or save for that game?
6. **Time doors.** Is time travel Ajar's Act 5 (a worked-out Stale door), a
   separate game, or dropped? See "Time doors" below; its own questions are
   listed there.

## Time doors (ideas to discuss, 2026-11-14)

Raw ideas, not decisions. Nothing here is prototyped or verified in the
engine. This would replace the one-line "Stale" door in the table above.

**Premise.** A door remembers *when* as well as where: it opens onto the room
as it was when you unhinged it. Through the frame you can watch yourself
fighting; step through and you are in that fight again, beside yourself.

### How it could be built

- **No real rewind.** ZScript cannot snapshot and restore the live world, so
  "this room, earlier" has to be a second copy of the room. The map generator
  builds each time-travel room twice and a door links the copies. Time travel
  is therefore per room, not per level.
- **Recording.** Each tic, store position, angle, frame, health and shots for
  the player and every monster in the room. Cap the length (30–60 s).
- **Replay.** The copy plays the recording with puppet actors. Portals render
  actors on the far side, so the view through the door is the replay.
- **Going live.** When you step through, puppets are swapped for real
  monsters at their recorded state. Your past self keeps replaying its moves
  with real bullets. From there the fight diverges: that is the branch.
- **Costs.** Third-person sprites for the player; every such room built
  twice; puppet-to-monster swap must be invisible.

### The past

- **Fight beside yourself.** Each trip back adds another you.
- **Your past self must survive.** It only replays, so it cannot dodge new
  threats. If it dies, you are erased.
- **Prevented damage is refunded.** Kill the monster that hurt you before it
  lands the hit and you get that health back.
- **Two places at once.** The past you holds the pressure plate while you
  walk through the gate.
- **Kill it differently.** A monster you shot the first time can instead be
  lured somewhere useful (onto a plate, into another door).
- **Paradox rule (proposed): branch and merge.** When the recording reaches
  the moment you left, the outcome of the redone fight becomes the truth.
  Needs a cost, or free retries make every fight trivial.

### The future

The engine cannot compute a real future, so each idea has to say where the
vision comes from and what happens when the real fight goes differently.

- **Your deaths are the future.** When you die you are not reloaded: you are
  back at the door before the fight, looking through it at your corpse and
  the last seconds replaying. The vision is honest because you played it.
  Needs the recording system plus a snapshot of health and inventory at room
  entry.
- **The future is a warning.** An untouched door shows an aftermath scene
  generated from the encounter script: which closets opened, where monsters
  came from, where your body lies. You read it, then fight to make it not
  happen. No recording and no consistency rule needed.
- **The future is a contract.** You may take something from the aftermath (a
  key from the boss's corpse, a weapon on the floor). Then you owe it: the
  real fight must end with it back in place, or you pay a paradox penalty.
  Past is help from yourself; future is debt to yourself.
- **Skip forward.** Step out N seconds later; the world ran without you
  (monsters fought each other, a timed door opened). Easy, only mildly
  interesting.
- **Avoid:** a prophecy that must be reproduced exactly. The game can only
  check coarse facts, so it turns into a challenge list.

The first two combine: the door shows the generated warning until you die,
then shows what really happened to you. The contract needs the most tuning
and can come later.

### Questions to settle

1. Act 5 of Ajar, or its own game (idea 7 in `../IDEAS.md`)? It leans on
   combat far more than the rest of Ajar does, which depends on decision 1.
2. What does a trip back cost? Door used up, a limit on copies of you, or
   something else.
3. What happens to the past self's shots when its target is already dead:
   harmless, or dangerous to you?
4. Deaths-as-future replaces normal death and reload. Everywhere, or only in
   rooms with a time door?
5. How does it meet the readability rule (know where a door leads before
   stepping through) when the answer is a time, not a place?
6. Overlap with "Thirty Moments": the aged-room version of the future
   belongs there, not here.

**First test.** One duplicated room in map `TEST`: record 20 seconds, show
the replay through the door, step in and fight beside yourself. Needs a
weapon and something killable first, so it comes after M3.

## Stray door (designed 2026-11-15, not built)

User's idea, first called the random door.

**Premise.** A door you hang like a coloured one, but it opens onto a random
place. A timer starts at once: go through or do not, and when it runs out the
door is gone either way. Missing a place means reaching it the ordinary way,
with another random door, or the long way round. Some of the places can be
secrets.

Rules the user set:

- A place reached by random door must have a way out once the door is gone.
- A secret reachable by random door must also have a normal way in, for
  players the door did not favour.

Notes (Claude's, to be argued over):

- It breaks core rule 1 on purpose, but can keep the readability rule: you
  see the place through the frame before you step. The timer turns "know
  where it leads" into "read the room in five seconds", which is the fun.
  Places in the pool should therefore be readable at a glance.
- "Random" should be a draw from a pool authored per level, without repeats
  until the pool is used up, not a free dice roll: no streaks of the same
  room, and the secret comes up eventually.
- It works both ways while it is open (rule 5): whatever is there can come
  out, so a bad draw costs something even if you stay put.
- Cheap to build: a pool place is an ordinary far-side stub; the door picks
  its target when hung and unhangs itself on a timer. Nothing new in the
  engine.
- Solver: the level must be winnable without any random door, and every
  pool place must pass the no-stuck-states check, including with a carried
  coloured door taken through.

Answers from the user (2026-11-15):

- **Shortcuts are allowed.** A draw may skip part of the level, later even
  put you behind a lock you have no key for. But there is always a way
  back: a player after 100% kills, items and secrets must be able to reach
  everything they skipped, by the long way. For the solver this is stronger
  than "can still win": from every state, every place must stay reachable.
- **Bad draws are pretty dangerous,** more so on later levels.
- **Timer:** start at 5 seconds and see. Possibly random per hanging, 3 to
  10 seconds.
- **Caught in it when it closes: telefrag** (to be tried). These portals
  move a thing when its centre crosses the line, so nothing is ever really
  half-way; the script would kill whatever overlaps the line at closing.
- **Look: multicoloured.** No clock on it: the clock sign is kept for the
  time doors.

- **One shot.** Once hung it is used up and disappears with its opening. A
  level can have several.
- **The time left is always shown** to the player.
- **The telefrag kills the player too.**
- **Introduced in level 5** (decided 2026-11-15; level 4 has the thief).

- **Name: the Stray door** (a door that has forgotten where it belongs).

Nothing is left open; it is ready to build when its turn comes.

## Prototype status (2026-11-14)

A test level exists (now map `TEST`): `./build.sh` (docker) builds `build/ajar.pk3`,
`./run.sh` plays it, `./tools/smoke.sh` runs a scripted walkthrough headlessly
in docker (`MODE=2` uses real USE key presses). It covers most of M1 and M2:
three plain doors, six frames, carry / hang / unhinge / swap.

Verified on GZDoom 4.12.2:

- Retargeting works with `Line_SetPortal` type 1 (teleporter) plus
  `Line_SetPortalTarget`, including a frame at a different floor height.
- **Portal lines cannot be one-sided.** A walkable portal needs a real sector
  behind the line, so every frame and far side has a small stub sector at its
  back. This replaces the "portal lines should be one-sided" assumption above.
- An untargeted portal line does not render or block as a wall by itself: the
  script sets blocking flags and a middle texture while the frame is empty,
  and clears both while a door hangs there.
- Portal lines are authored with a valid dummy target and emptied at map load.

Not done yet: no git repo; no door swing
animation or carry delay; nothing but the player has been sent through a door.

## First level (2026-11-14)

`MAP01` "Borrowed Rooms" (`tools/map_hinges1.py`) is the first real level:
five plain doors, four frames, a cell, a hall cut by a pit, a ledge, a gallery,
a vault and the exit. The test box is still there as map `TEST`
(`MAP=TEST ./run.sh`).

- Each level module also declares itself as a graph (`PUZZLE`). `tools/solve.py`
  runs at build time, prints the shortest solution and fails the build if the
  level is unsolvable or has any state the player cannot win from. MAP01:
  9 door actions, 253 states, none stuck.
- `./tools/smoke.sh` plays that solution in the engine (10 checks);
  `MAP=TEST ./tools/smoke.sh` runs the old test-box walkthrough.
- Design rules that fell out of it: a place you can only leave by door needs
  a door hung there from the start (then it can only ever be swapped, never
  emptied); leaning doors only go in places that stay reachable; swapping
  means frames are never scarce, so difficulty has to come from one-way drops
  and from a door being your only way out.

Still no door swing or carry delay.

Company and decoration (2026-11-14): MAP01 has eight Doom monsters and none
of Ajar's own — two zombies in the hall, a demon in the pit, an imp on the
ledge, an imp on the gallery, two imps in the vault, a zombie by the exit —
with a shotgun in the hall, shells, stimpacks and a medikit. Each far side
is lit in its door's colour (red, blue and green torches, candelabra on the
gold ledge, tech lamps by the exit); the hall has two candle niches and two
barrels, the pit has remains. Blocking lights stand in corners and beside
recesses, never on a line the player walks. `MAP=MAP01 MODE=2
./tools/smoke.sh` is a tour: it keeps the monsters, stands unseen in each
room and takes a screenshot. The walkthrough (mode 1) removes the monsters,
so it still only proves the doors. Not played by hand yet: whether the
fights are too hard or too easy for a first level is unknown.

Surfaces (2026-11-14): rooms are cut into grids (`ajarmap.room`) so a pale
carpet runner under a raised row of ceiling lights leads from door to door;
the cell is brick, the vault is walls of small locked doors, and framed
pictures of doors hang in the hall and on the gallery (`ajarmap.picture`,
which uses the new `Map.cut` to split a wall). All textures are generated in
`tools/gfx.py`.

Shooting through doors (2026-11-14): it works. `MAP=TEST MODE=8` fires the
real pistol by key press through the RED door and kills a zombie, then
checks scripted shots backwards, at a slant and through the pit frame;
`MAP=MAP01 MODE=3` checks cell/hall and pit/ledge both ways. Two limits:

- The engine never lets a shot hit whoever fired it (a rocket jump is
  splash damage, not the rocket hitting you), so by itself you could not
  shoot your own back through a door. Script now makes that work (user
  asked): `AjarHandler.SelfShots` re-traces each bullet when the pistol,
  chaingun or either shotgun uses ammo and hurts the player if it came
  through a door and then through them; `AjarShotWatch` follows every
  projectile and, once it has been through a door, lets it hit its sender
  (monsters' own shots too). `MAP=TEST MODE=9` checks pistol and plasma.
  Other mods' bullet weapons are not covered. A projectile needs a fairly
  straight line: at a steep slant it hits the side of the frame.
- Autoaim does not find a target through a door whose two ends are at
  different floor heights (pit/ledge). The shot still flies level and
  arrives at the matching height, so it hits what is straight ahead.

## Second and third levels (2026-11-15)

Both are built, solver-proven and walked headlessly. MAP02's first version
was played and liked by the user; the reworked MAP02 and MAP03 were played
on 2026-11-15 too (see "Less linear levels"). `MAP=MAP02 ./run.sh`, `MAP=MAP03 ./run.sh`; each
level's exit leads to the next, MAP03's loops back to itself.
`MAP=MAP0x ./tools/smoke.sh` is the walkthrough, `MODE=2` the tour.

**Fixed doorways** (user, 2026-11-15: "usual doors" instead of nailing a
coloured one). `ajarmap.doorway(m, n, ...)` joins two places for the whole
level with a plain pale stone opening: no colour, no leaf, no glow, and
USE says it is part of the building. Underneath it is a leafless door
fixed in its frame (door thing `args[3]`), so monsters, shots and lodgers
treat it as a hung door. In a `PUZZLE` graph it is one walk link each way.
Every coloured door stays one the player can take.

`MAP02` "No Vacancy": that version (five doors in a chain) was played and
called too obvious; it is replaced, see "Less linear levels" below.

`MAP03` "Stage Door" (`tools/map_hinges3.py`), a theatre: 9 door actions,
460 states, none stuck.

- Foyer (start; VIOLET) joined by a doorway to the stalls (two frames).
  Dressing room (VIOLET's far side, BLUE), a dead end. Box (BLUE's, GREEN),
  gods (YELLOW's, RED: the way out, visible from the stalls) and flies
  (GREEN's) are ledges: you step out onto them and can only drop. The
  stage (one frame) is too high to climb from the stalls; the trap at the
  back of it is a pit whose way out is YELLOW, hanging there. The alley
  (RED's) has the exit.
- New for the player: doors that are one-way trips, and needing free hands
  at the bottom of a drop (the swapped-out door is left on the stage).
- Company: one lodger (wakes in the stalls), imps and former humans in the
  stalls, a hell knight on the stage, a spectre in the trap, a chaingunner
  in the gods, lost souls on the flies, sergeants in the dressing room, a
  revenant in the alley. Super shotgun on the box. None of Ajar's own
  monsters are new here (user: none yet).
- Ledges must be at least 192 deep, or a running player goes straight off.

Puzzle length: searches over variants of both layouts found nothing much
longer with five doors and no stuck states. More length needs a sixth
door colour or more doors that start hung and have to be displaced.

## Less linear levels (2026-11-15)

User, after playing MAP02 and MAP03: all works, but MAP02 is obvious ("I
take the next door, it moves me to the proper place, then I see the next
one"). Wanted: a puzzle, where using a door at the wrong time costs you a
long way back; bigger maps; rooms behind normal doors; doors you have to
look for. The theatre is liked but should be much bigger, with keys and
perhaps secrets.

**Finding: plain doors alone always give a chain.** Any door can hang in
any frame and works both ways, so reaching a place never needs more than
one door, and that door lies in one place. Random and hill-climbing
searches over hotel layouts (several hundred thousand) found nothing else.
Two things break the chain:

- **Something that asks for two things at once**: keys, above all a lock
  that needs two. (Later: nailed doors, one-way doors.)
- **Running out of frames.** A door cannot be put down, only hung. To pick
  one up you need empty hands, so with as many frames as doors every frame
  matters, and a frame somewhere awkward becomes the puzzle.

Also: the solver counts door actions, but what a mistake costs the player
is walking. Rating a level with every move costing one shows it (old MAP02:
no move ever set you back).

Two rules that came out of it:

- No frame in a place that is only reached through one door: hang that
  door there and the place is lost for good. (The terrace frame did this
  as soon as the balcony could be left by dropping.)
- A level should stay fully reachable from every state, for players who
  want everything; `rate.py` in the search checked this, `tools/solve.py`
  does not yet.

**Built for it:**

- `ajarmap.roomdoor`: an ordinary Doom door (USE opens it, it shuts by
  itself, monsters open it), plain wood, texture `AJHDOR`. Rooms beside it
  should be at most 128 high.
- Room keys (user chose these over Doom's keycards, and to have them in
  MAP02 already): `AjarKey1`..`AjarKey4`, editor numbers 20011-20014,
  numbered brass keys, shown top right on the HUD, taken away at the end
  of the level like Doom's. `roomdoor(keys="1")` locks a door; `keys="23"`
  gives it two locks that need both. Lock plates on the door show the
  numbers. Locks are in `src/lockdefs.txt` (41-47), `ajarmap.key` places a
  key.
- `tools/solve.py` knows keys: `keys={name: region}` and walk links
  `(from, to, "23")`.

`MAP02` "No Vacancy" (`tools/map_hinges2.py`), rebuilt: 10 door actions,
3 keys, 2590 states, none stuck. **Not played by hand yet.**

- Ground floor to walk about in: lobby, a hall with six guest rooms
  (101-106), dining room, kitchen. Upstairs a hall with four rooms
  (201-204), reached by RED and left by dropping into the lobby. Attic
  (drops into the upstairs hall), cellar (a dead end), terrace over a
  garden, stone doorway from the garden to the balcony, and a gap in the
  balcony rail to drop back into the lobby. The street is the way out.
- Four frames: lobby, kitchen, upstairs hall, cellar. None beyond the
  terrace.
- RED is in room 104. Upstairs: key 1 (room 201) and YELLOW (room 204),
  which leads to the attic and key 3. Key 1 opens room 106: BLUE, which
  leads to the cellar and key 2. Keys 2 and 3 open room 203: GREEN, which
  leads to the terrace. VIOLET leans on the balcony. Attic and cellar can
  be done in either order.
- The catch: VIOLET needs empty hands, and nothing can be hung beyond the
  terrace, so GREEN has to go into an empty frame, never a swap. With RED,
  YELLOW and BLUE hung, the only empty frame is the cellar's. Go through
  with a door in hand and it is the long way round: garden, balcony, drop,
  and all the way back.
- Company: 32 monsters. One lodger, in the kitchen. Spectres in the
  cellar, a demon shut in 106, imps and a sergeant with GREEN.
- `MAP=MAP02 ./tools/smoke.sh`: 28 checks, including both locks refusing
  without keys. `MODE=2` is the tour (15 views).

**Second pass (2026-11-15)**, after the user played it: much better, but
each key lay close to its lock, the colours are still used one after
another, the rooms did not look like rooms, and "where is the lobby?".

- Keys: four now, and none is used on the floor where it is found. Key 4
  (bathroom of 201, upstairs) opens suite 105 at the far end of the ground
  floor, where key 3 lies in the bath. Key 1 (attic) opens 106 next to it
  (BLUE). Key 2 (cellar) and key 3 open suite 203 upstairs (GREEN). All
  three locks can be seen long before their keys. 10 door actions, 3434
  states, none stuck; the description of the rebuilt level above is
  otherwise still right.
- Rooms: `guest()` in `map_hinges2.py` gives every room a bed, a tiled
  bathroom (bath, basin; behind a door or an open way) and windows; 105
  and 203 are suites (sitting room, then bedroom). Dining room has tables
  and windows, the kitchen a counter. New helpers in `ajarmap`: `fitted`
  (a room with furniture: rectangles with their own floor), `window`
  (glazing bars over a `Line_Horizon` sky), `opening`. `udmf` sectors have
  `side` (texture of a step up to them), lines `lower`. A wall piece with
  its own picture must not be crossed by a furniture edge of `fitted`.
- Lobby: reception desk with a key rack under the balcony, a sofa, and
  the hotel's front doors, boarded up, under a NO VACANCY sign.
- The colour order is unchanged and still a chain. Ideas put to the user,
  nothing chosen yet: a hub of two or three doors open at once; a door
  that starts hung and is first met from its far side; a place that needs
  two doors hung at the same time; a door with two jobs; a spare door
  that is a trap or a secret.
- `MAP=MAP02 ./tools/smoke.sh`: 23 checks. `MODE=2`: 25 views. Not played
  by hand yet.

## MAP03 rebuilt (2026-11-15)

User: MAP02 stays as it is; all the non-linear ideas go into a new MAP03,
much bigger, with other rooms, keys and more enemies. The MAP03 described
under "Second and third levels" is gone. **Not played by hand yet.**

`MAP03` "Stage Door" (`tools/map_hinges3.py`): six doors, three keys, five
frames, 8 door actions, 60620 states, none stuck, nothing losable. 56
monsters, 2 secrets.

- Front of house, all walkable: foyer (start, frame), cloakroom (VIOLET),
  bar (BLUE), stalls with rows of seats (frame), orchestra pit. Above:
  dress circle (BLUE's far side, key 2), gods (YELLOW's far side) with the
  lighting booth behind them, flies (GREEN's far side) and a lighting
  bridge from them along the south wall to a landing over the gods. The
  stage is too high to climb; backstage are two dressing rooms (key 1),
  the star's room (keys 2 and 3: RED) and a green room. The room under
  the stage (VIOLET's far side, GREEN, a frame) is open from above.
- Hub: BLUE and VIOLET from the start, circle and under-stage in either
  order.
- Bolted doors (`ajarmap.bolted`, `unbolt`): shut from one side, they open
  for good when the player first arrives on the other: the circle's
  stairs down to the bar, the grate between pit and under-stage (a block
  of the stage front that sinks), the booth's door to the gods.
- GREEN has two jobs: the flies are the only way onto the stage (a drop)
  and the only way to the gods (the bridge), each one-way.
- YELLOW is first met from its far side: it hangs in the booth, and its
  far side in the gods stands open onto the booth and key 3.
- PINK, the sixth colour (ring glyph), is a spare: it hangs in the
  manager's office (key 1) and opens onto the property store (rocket
  launcher, armour, revenants), a secret. The other secret is a nook off
  the bridge.
- RED needs empty hands, so every door taken has to hang somewhere.
- `MAP=MAP03 ./tools/smoke.sh`: 18 checks. `MODE=2`: 27 views.

What the searches showed, to keep:

- A frame in a place reached only through one door makes an island as
  soon as that door is hung there and the place left by a drop. Either no
  frame there (stage, circle, flies, gods), or a bolted door that opens
  on first arrival (booth, under-stage).
- A door once picked up can never be put down, so with RED needing empty
  hands there must be a frame for every other door that can be taken. A
  spare door therefore starts hung, in a frame of its own.
- `tools/solve.py`: `auto` (things that happen by themselves on arriving
  somewhere, i.e. bolts) and `lost()` (places and keys that can become
  unreachable for good). A `PUZZLE` with `complete=True` fails the build
  if anything can be lost; MAP02 and MAP03 lose nothing, MAP01 can lose
  the cell and the ledge (it has no `complete`).
- Ordinary doors now fit rooms up to 256 high (the texture carries wall
  above the leaf).

Door colours: five now, and the limit is the player's memory, not the
solver (MAP02's 2590 states take well under a second; even eight doors
would be fine). Adding one is a colour and a glyph in `tools/gfx.py`, a
sprite state and three table entries in `AjarDoor`. Suggested ceiling:
six or seven per level, and not all new at once. Not added yet.

Next for this: the user plays the new MAP02; then MAP03 gets the same
treatment (much bigger, keys, secrets).

## MAP04 "Party Wall" (2026-11-15)

Built, solver-proven and walked headlessly. **Not played by hand yet.**
`tools/map_hinges4.py`: houses round an open yard. Six doors, four keys,
six frames, 10 door actions, 38158 states, none stuck, nothing losable.
87 monsters, 4 secrets. `MAP=MAP04 ./run.sh`; MAP03's exit now leads here.

User's brief: much bigger, open space as well as closed, multi-level,
puzzles out of carrying only one door (which door, or none), the thief,
secrets. All agreed 2026-11-15, with the Stray door moved to MAP05.

- **Places.** The yard (start in the gate passage; three frames; wash
  house) is the one place to walk about in. Above it: balcony (BLUE's far
  side; key 1, GREEN), roof (GREEN's; key 2), loft (YELLOW's) with a suite
  behind keys 1 and 2 (VIOLET). In the middle of the roof a light well with
  the boiler: a frame and key 4. North of it the cellar (YELLOW), whose
  door to the yard is bolted on the cellar side, and the kennel (VIOLET's
  far side; key 3). East: the landlord's office (keys 3 and 4, two barons)
  and behind it the strongroom: RED and a frame; RED opens onto the street.
- **Squeezes** (new rule; `ajarmap.squeeze`, line id 500): a hole a door
  does not fit through. The player passes with empty hands only
  (`AjarHandler.Squeeze` sets `ML_BLOCK_PLAYERS` while a door is carried
  and says so when they push at it); monsters never (`blockmonsters`).
  Four: well to cellar (the coal hole), kennel to cellar (a hatch with a
  drop: one way), wash house to pantry, office to strongroom.
- **The catch.** RED is behind a squeeze, so every other door must hang
  somewhere: four doors, three frames in the yard, and the fourth frame is
  down the well, where a door can only be brought by jumping in from the
  roof with it. Which door goes down is the player's choice.
- **Sending something somewhere worse.** VIOLET's far side, the kennel,
  has no way out for a monster. Let the barons follow you in, leave by the
  hatch, take the door down; the door with barons behind it is the one to
  put down the well. Optional: they can be fought, and shot through the
  kennel's bars from the cellar. `MAP=MAP04 MODE=3 ./tools/smoke.sh`
  proves it with one baron.
- **The thief** starts with BLUE on its back, the only door there is
  (thing `args[0]` = colour; the door thing stands where the thief does),
  and stays in the yard (`args[1]` = 1: it never walks through a door, and
  a step through one by accident is undone in `AjarThief.Tick`). It also no
  longer tries to reach anything through a squeeze.
- **Secrets.** PINK hangs in the pantry behind a squeeze, cannot be carried
  out, and opens onto a store (both count). A target in a hole high in the
  south wall can only be seen from the edge of the roof (two bonuses mark
  the spot); shooting it opens a closet in the yard. A nook off the roof.
  Not done, though proposed: a hidden frame (it would undo the catch) and
  a secret for disposing of the barons.
- `MAP=MAP04 ./tools/smoke.sh`: 24 checks, including a squeeze refusing a
  door. `MODE=2`: tour, 31 views.

`tools/solve.py` now knows:

- Squeezes: a walk link `(from, to, keys, "squeeze")` needs empty hands.
- The thief: `thief=dict(zone=region, sees=[regions])` and a door with
  `thief=True`. It may at any time pick up a door leaning in its zone,
  hang its door in an empty frame there, and, while the player is in the
  zone or a region in `sees`, take a hung door down or swap it. The player
  can kill it in its zone. Every arrangement the two can produce is
  explored, and from each the player must be able to win, and reach
  everything, by their own moves alone. One thief, one zone, and it must
  be one that stays there.

Found on the way:

- A door that must be picked up with empty hands and then carried about
  makes places losable once there are more doors than frames. Putting it
  behind a squeeze with a frame of its own avoids that.
- A door on a tall outdoor wall is drawn again higher up; give it a low
  porch on the yard side (`porch()` in the map).
- One ZScript function does not hold three large constant tables: the
  third came out empty (hence `PartyWallViews`).
- Doom monsters stray through hung doors just by running about.

Not known until it is played: whether the yard is too hard at the start
(a thief, 30 monsters, snipers on three sides), whether the well reads as
"a door has to come down here", and whether the squeeze message is enough
or the holes need a sign.

## Flip door (designed 2026-11-15, not built)

User agreed. A special door, not a property of every door: two-coloured,
with two far sides. Hung, it opens onto one of them and stays so for as
long as it hangs, so the view through it is always true. Each time it is
taken down and hung again it opens onto the other. The leaf shows both
colours and which comes next. Getting "the same side again" costs a
re-hang, i.e. a frame and empty hands. Turned down: a dial set in the
hand (no cost) and a far side that depends on the frame (a second thing
to remember). Not for MAP05, which has the Stray door.

## Handoff (2026-11-14)

State (end of 2026-11-14): MAP01 builds, passes the solver and the headless
walkthrough, and was played and accepted by hand. Ajar is a Doom II mod
with Doom's monsters and weapons. Three monsters of its own exist (thief,
nailer, lodger); the user played all three in the test box and is happy
with them. All smoke tests pass. There is no git repo: everything is only
in this directory.

How to work on it (everything but GZDoom itself runs in docker):

- `./build.sh` — solver check, then `build/ajar.pk3`. It prints the MAP01
  solution.
- `./run.sh` — play MAP01; `MAP=TEST ./run.sh` for the mechanics test box.
- `./tools/smoke.sh` — headless MAP01 walkthrough, screenshots and log in
  `build/smoke`. `MAP=TEST` (and `MODE=2`) for the test box; a custom output
  directory must be an absolute path.
- A new level is a `tools/map_*.py` module with a `Map` called `m` and a
  `PUZZLE` graph, registered in `MAPS` in `tools/build.py` and in
  `src/mapinfo.txt`. `tools/ajarmap.py` has the frame, far-side and door
  helpers; far-side line ids are 200 + colour.

Playtest of MAP01 (2026-11-14, by hand): accepted as the first level. The pit
reads as a pit, the start message is fine, and the 9-action flow is
interesting and enough for a first level; later levels can be more
complicated. One bug found and fixed: room tints coloured door sprites too
(BLUE looked grey on the gold ledge), so rooms now tint surfaces only
(`color_floor` etc. instead of `lightcolor` in `tools/udmf.py`); confirmed
fixed by hand. The coloured stripes above recesses are fine.

M3 proof (2026-11-14): `MAP=TEST MODE=3 ./tools/smoke.sh` sends a projectile,
a monster-like actor and a hitscan from the hall through the hung RED door;
all three arrive in the red room.

Own monsters (2026-11-14): the charger and the lobber were built, tried by
hand and removed (user: not clearly fun; the charger is a lost soul). Two
findings from them remain in use: `CheckSight` does not look through these
portals (`AjarSight.DoorImage` does that job), and a shot's sender must be
cleared for it to hurt its own kind.

Thief (2026-11-14): `AjarThief` (editor number 20003, sprites `AJTH`, 40
health). It does what the player does: takes a hung door (35 tics at the hinges) or
picks up a leaning one, carries it to another frame and hangs or swaps it
there, rests a moment, and repeats until killed. Now and then (about one
look in three, at most every 250 tics) it instead walks through a hung
door, from either end, and carries on from the other side. It picks among
the jobs open to it at random. What it carries drops where it dies; what it
rearranged stays rearranged. It moves at about 8 units a tic (user: the
first version, 3.3, was very slow). Limits, on purpose:

- It only goes for things it can see and reach by a straight walk with no
  step over 24 on the way (it cannot plan a way down a drop, across a pit
  or round by stairs — earlier versions went for a door in the pit, then
  for an opening across the pit, and paced the edge).
- Taking a hung door down, or swapping it out, it does only while it can
  see the player: that is the one job that can close a way behind someone's
  back. Picking up a leaning door, hanging into an empty frame and walking
  through doors it does unwatched.
- It leaves the frame it last used alone for 350 tics and gives a job up
  after 150 walk steps.
- Doom's chase code overshoots a 64-wide doorway at this speed, so the last
  steps through an opening are walked straight by velocity.

`MAP=TEST MODE=5 ./tools/smoke.sh` (random choices off) checks take, hang
elsewhere, take again, drop, recovery, and a walk through a door and back.
One stands in the test box hall. `tools/solve.py` does not model the thief
yet, so a level with one is not proven winnable.

Nailer (2026-11-14): `AjarNailer` (editor number 20004, sprites `AJNL`, 80
health). It walks to the nearest hung door without nails and nails it to
its frame (34 tics of hammering). A nailed door still works as a door, but
neither the player nor a thief can take it down or swap it until the
nailer is dead; then the nails fall out of every door it nailed. Nailed
doors show two planks (`AJN1`..`AJN5`). With nothing left to nail it goes
for the player with the hammer (8-20 damage). `MODE=6` tests it.

Lodger (2026-11-14): `AjarLodger` (editor number 20005, sprites `AJLG`, 60
health), the user's "monster for empty frames". It lives inside the empty
frames, where it cannot be seen or hurt. It picks an
empty frame the player can see (96 to 1024 units away); the frame glows
and knocks for 36 tics, then the lodger steps out and attacks (4-10
damage a hit, 7.5 units a tic). After 220 tics, or 20 damage, it walks
back into the nearest empty frame and waits 60-130 tics. (User: the first
version, 4 units a tic, never reached a moving player.) A frame with a
door in it is shut to it: hanging a door plugs the frame, even during the knocking. With every reachable frame plugged
while it is out, it is shut out and fights on. `MODE=7` tests it.

Shared code: `AjarWorker` (reach test, marker, walking) under `AjarEnemy`.

Order of appearance (user, 2026-11-14, revised the same day): none of
Ajar's own monsters in level 1. Then the lodger first, then the thief, then
the nailer; the repainter (swaps where two doors lead, irreversible, not
built) comes last. Which level each one first appears in is still open.

Test box: `MAP=TEST ./run.sh` has all three plus an imp, a zombie and a
shotgun. `MAP=TEST ./run.sh +set ajar_only N` keeps one of Ajar's own:
1 thief, 2 nailer, 3 lodger. Smoke modes: 1 and 2 walkthrough, 3 things
through doors, 4 Doom monster follows through a door, 5 thief, 6 nailer,
7 lodger, 8 shooting through doors, 9 shooting yourself. `tools/solve.py` models the
thief (see "MAP04") and no other monster.

Next, in order:

1. Play MAP04 by hand (see "MAP04").
2. Decoration of MAP01-MAP04 (user: a separate task).
3. MAP05 with the Stray door.
4. Teach `tools/solve.py` about the nailer before a level uses it.
5. Door swing animation and carry delay (left over from M2).
6. The flip door; the repainter, last.

## Look: MAP01 (started 2026-11-15)

Decoration is done room by room: candidates are generated in
`tools/gfx.py`, built behind a switch, photographed in the engine from fixed
cameras and chosen by the user on the look board
(https://claude.ai/artifact/LqAibHAuoDo3ANyVetwAXf, source
`design/map01-board.html`, images from `build/board/`).

Tools: `tools/trial.sh AJAR_HALL 1 2 3` builds MAP01 once per value and
shoots the 22-view tour (`MAP=MAP01 MODE=2`) into `build/trial/`;
`tools/cfgtest.sh` checks a GZDoom config headless.

Decided for MAP01 (user):
- The cell stays as it is.
- The hall, the ledge and the gallery are one room and are dressed alike:
  terracotta over a navy dado (`AJHW2`; `AJHS2` is the 176-high cut for the
  gallery), slate flags with a plain navy runner (`AJHG4`, `AJHR3`), the
  warm tint. No blue or gold room tint any more: the trim column over a far
  side, the torches and the doors carry the colour.
- The pit is a stone cellar (`AJPW1`, end walls `AJPE1`), dark floor.
- The shotgun lies on the ledge, after the pit. The hall is pistol only.
- The game is designed for the hardware renderer. `run.sh` starts GZDoom
  with its own `ajar.ini` and the GLES backend (the OpenGL backend draws
  black in hardware mode on this machine).

The losing candidates are still in `gfx.py` behind `AJAR_HALL`, `AJAR_PIT`
and `AJAR_FLOOR` (two digits mix a floor with another's runner). They can
go once MAP01 is settled.

Rules that fell out of it: walls are cut at multiples of 32, so wall
patterns repeat every 32 across; a full-height wall is one texture from
skirting to cornice (336 in the hall); `m.line(..., upper=, lower=,
dontpegtop=, dontpegbottom=)` carries a wall on above and below an opening;
`sector(raw=...)` passes UDMF properties such as `lightfloor`.

Monsters through doors (2026-11-15): `AjarSense` used to drop its lure as
soon as the monster lost its straight view through the opening, and the
monster then walked at the wall nearest the player. Now it keeps making for
that door for 30 seconds: to a spot square in front of the opening, then
through. `MAP=MAP01 MODE=4` checks a hall zombie following into the cell,
and the pistol hitting yourself in the hall.

The vault has the hall's navy runner (user, 2026-11-15).

The way out is on trial behind `AJAR_EXIT` (`AJAR_EXIT=2 ./build.sh`, or
`tools/trial.sh AJAR_EXIT 1 2`; the tour has 22 views now, the last two of
the exit door). The idea for exit rooms in every level: far sides have a
colour, the way out has none.
- 1 (built by default until the user chooses): a dim white room whose
  white door stands ajar, light behind it and a wedge of light across the
  runner. Push the door (USE) to leave.
- 2: the white room with a fixed doorway between its two end walls, so
  that through either end you see the room again and your own back in it.
  Walking into either end is the way out. VIOLET's far side moves to the
  south wall.
- 0: as first built (plum room, arrow switch).
The user chose the doorway of 2 (2026-11-15), but not the bare white room
("looks unfinished"): it needs decoration and colour. Three dressed rooms
around that doorway, with a brass surround and candelabra at both ends:
- 3: ivory panels over a charcoal dado, black-and-white marble floor,
  black runner.
- 4 (**chosen by the user**, the default): a night room, ink walls and
  ceiling with gold stars, dark floor with brass inlay, gold runner.
- 5: the hall turned inside out, ivory over a terracotta dado, encaustic
  tile floor, navy runner.
Not built: the exit glyph (an architect's door symbol), a door onto the
next level, a free-standing door.

Wide monsters and doors (2026-11-15): the demon in MAP01's pit could not
use the YELLOW door. A thing crosses a portal line when its centre does,
and its whole box must then fit in front of the back wall of the stub
behind the line. With a 32 stub a demon (radius 30, step 10) had 2 units
to land in. `ajarmap.STUB` is now 48 (64 runs into a room in MAP03), enough
for anything that fits a 64 opening. `MAP=MAP01 MODE=5` checks it.
The user saw the demon come through and then hang about on the ledge side;
left as it is for now.
`MAP=MAP01 MODE=4` (`monsterComesIntoCell`) passes on some runs and not on
others: the zombie sometimes needs longer than the test allows to line up
with the opening.

Next for the look, in order:
1. The user reported not being able to shoot themself in MAP01; it could
   not be reproduced. Ask which door, which frame, where they stood and
   which weapon.
2. The same way out (night room, doorway onto itself) in MAP02-MAP04, and
   an exit glyph if one is still wanted.
3. Ceilings and lighting of the hall block: everything is evenly bright,
   lamps light nothing, and thin dark beams show where ceilings step by 16
   at the light strips.
4. Doom's props (torches, candelabra, barrels) against the new surfaces.
5. Update the board's lower "before" section, then MAP02-MAP04.
