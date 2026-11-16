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
| Stray | One shot: opens onto a random place, then vanishes on a timer (see "Stray door") | Level 5 (built) |
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

## MAP05 "Lost Property" (2026-11-15)

Built, solver-proven and walked headlessly. **Not played by hand yet.**
`tools/map_hinges5.py`: a railway terminus. Five doors in the puzzle (PINK
is a sixth, in a secret), four keys, five frames, four Stray doors, 10 door
actions, 322864 states, none stuck, nothing losable. 133 monsters, 5
secrets. `MAP=MAP05 ./run.sh`; MAP04's exit leads here. The user played
MAP04 and confirmed it ("looks great, we can go next").

User's brief: bigger again, more puzzles and secrets, the player builds the
way out, perhaps the next monster. The Stray door was already due here.

**The way out is built by the player** (user's idea; `ajarmap.way_home`).
The night room of the earlier levels, but its two ends are not joined: the
far side of an ordinary coloured door is in one end and an empty brass
frame in the other. Hang that door in that frame and the room opens onto
itself: the door loses its leaf and becomes the doorway of `way_out()`, for
good, and walking into either end ends the level. No new rule: it is rule 1.
- The user chose an ordinary colour over a special "night door" (Claude's
  first suggestion): the player may reach the room by chance, and then has
  to work out that the door must be carried there another way.
- The puzzle it makes: that door, hung anywhere, takes you to the night
  room, and then it is behind you. So the room needs a second way in by
  which a door can be carried. How hard that way is, is the knob per level.
- Meant for every level from here on; MAP01-04 keep the ready-made room.
- Engine: the frame thing's `args[1]` is the far-side line id of the door
  that belongs there; both mouths have line id 590 and become `Exit_Normal`
  when it is hung (`AjarHandler.ComeHome`). Solver: `home_frame`.
  `MAP=TEST MODE=12` checks it.

**Stray doors** are built as designed (see "Stray door"): colour 7,
`ajarmap.stray` and `ajarmap.stray_place` (line ids 270-289), drawn without
repeats, 2 to 5 seconds, the time left always on the HUD, telefrag at closing.
A thief ignores them. `MAP=TEST MODE=11`, `MAP=MAP05 MODE=3`.
- **Not agreed yet, built as Claude proposed it:** a Stray door that a
  nailer has nailed stays open until the nails fall out (the HUD says
  NAILED). To turn it off: the `if (d.nailer) continue;` in `StrayTick`.
- Timer: random per hanging, 2 to 5 whole seconds, the short ones
  likelier (2 s 35%, 3 s 35%, 4 s 20%, 5 s 10%; `StrayTics`). Vadim,
  2026-11-15, after playing: a fixed 5 seconds was too long. The headless
  tests always get 5.
- **The pool is mixed** (agreed 2026-11-15, after playing): a Stray door
  opens onto one of the level's own stray places or onto the far side of
  any coloured door that hangs nowhere at that moment (`StrayPool`). So
  the pool shrinks as doors are hung, and a draw can show where a colour
  leads before its door is found. Stray places are now only for somewhere
  no coloured door leads: MAP05 keeps three (lamp room, kiosk, engine
  shed). If a coloured door is hung while a Stray door is open onto its
  far side, the Stray door shuts at once (telefrag and all); no test
  covers that. The solver adds the home of every unhung door to `pool`.

**The level.**
- Concourse (start), platform 1 and the tracks are one place to walk in.
  Off platform 1: waiting room (RED), lost property office (keys 1 and 2:
  key 3, two Stray doors), lockers behind a squeeze (PINK, secret), lamp
  room (secret). A train stands at platform 2: a solid block whose roof is
  a way along from the bridge. The bridge (RED's far side) crosses the
  east end with gaps in its rail over platform 1, the train, platform 2
  and the yard; the signal box off it has key 1, GREEN and a lever. The
  gallery (GREEN's far side; key 2) looks into the concourse. Off platform
  2: parcels office (BLUE's far side; key 4) and the night room, both
  bolted inside. North: goods yard, engine shed, loft (YELLOW's far side,
  a Stray door), station master's office (keys 3 and 4: VIOLET).
- **A turnstile is a squeeze.** Platform 2 is two steps from the concourse
  with empty hands; BLUE leans just beyond it. With a door the only way
  there is RED, the bridge and down. That is how VIOLET gets home.
- **The nailer** is in the engine shed, where YELLOW hangs: it is nailed
  before you get there. The yard gate is bolted on the yard side (first
  way in: off the bridge); once open, the nailer can come out to work.
- **Stray pool:** night room (an early look at the goal, and it draws the
  bolt), gallery, lamp room, parcels office, engine shed (the nasty one),
  kiosk (secret; otherwise opened by shooting its bell through the bars).
- `MAP=MAP05 ./tools/smoke.sh`: 28 checks. `MODE=2`: tour, 50 views.
  `MODE=3`: the four Stray doors.

`tools/solve.py` now knows:
- `home_frame`: hanging the right door there wins.
- `nailer=dict(zone=[regions, (region, key)])`. Which doors are nailed is
  not kept (every subset of doors multiplied the states past two million):
  while the nailer lives, taking down or swapping a door in its zone is
  luck, never something a win may depend on. The player kills it in its
  zone.
- `pool=[regions]`: Stray doors are not counted. With empty hands in a
  place with a frame the player may find themselves in any pool place,
  with empty hands, a door that leant nearby, or the door that hung in
  that frame. No win may depend on it; the printed solution uses none.
- MAP05 takes the solver about a minute; the whole build about two.

Limits of 2.5D met here: nothing can be under anything, so the train is
solid (no carriages to walk through), nothing runs under the bridge, and a
frame cannot be cut into a platform edge or the foot of the bridge.

The night room's far side wears its own colour's surround, not the room's
brass (Vadim, after playing: arriving there by Stray door, the brass read
as yellow and did not say which door belongs in the frame). The frame end
stays brass. No stray place in the night room: VIOLET's far side is in the
pool until VIOLET is hung.

**Played by Vadim, 2026-11-15: "looks great".** What he liked most, and
wants more of in later levels: the twist at the end. You see that VIOLET
has to be carried round to the other end of the night room, and then that
this cannot be done without going through RED to get up to the bridge: one
door's errand needs another door's far side. Build later puzzles on that.

### Handoff for the levels (2026-11-15, night)

State: MAP05 and everything in this section is committed on `main` and
pushed; the `map05` branch and worktree are gone. MAP01-05 build and pass
the solver (MAP05: 10 door actions, 450927 states, nothing stuck or
losable; the build takes about two minutes, most of it this). Passing:
`MAP=MAP05 MODE=1` (walkthrough to the exit), `MODE=3` (Stray doors),
`MODE=2` (tour, give it `TIMEOUT=400`), `MAP=TEST MODE=11` and `12`.
Vadim has played MAP05 through and likes it. He has not yet played the
three changes made after that: the 2 to 5 second timer, the mixed pool,
and the violet surround in the night room. Ask how they played.

Still open:
- A nailed Stray door stays open: Claude's proposal, built, never agreed
  or refused. Ask.
- Offered and not taken up: rigging the first Stray draw of a level to
  open onto the night room, so that every player gets the glimpse. Vadim
  preferred fixing the surround; raise it again only if the glimpse
  turns out too rare (about 57% over the level's four Stray doors).
- No test for a Stray door shutting when a coloured door is hung onto the
  far side it is open on, for the random timer (tests always get 5 s), for
  a nailed Stray door, or for the kiosk's bell.
- MAP05 wears stock textures; its look is for the design session.
- Careful: the design session works in this same checkout. Stage your own
  files or hunks only (`tools/ajarmap.py`, `gfx.py`, `ajar.zs` and this
  file are shared), and its smoke runs write to `build/smoke` too: give
  `tools/smoke.sh` a directory of your own.

Next: MAP06. Ideas on the table, all Vadim's: the player builds the exit
on every level from now on; the two ideas below (set-up-and-swap; the
timed exit); the Flip door is the next door in the table; lodger is the
monster MAP05 did not use.

**Idea for later levels** (Vadim, 2026-11-15): the same twist one step
deeper. To bring the right door where it is needed you must first hang
another door in place, then carry a second one there and swap, and only
through that swap does the route open; a third door (as RED here) is the
one you have to remember exists and where it hangs. So the player holds
two colours in mind, works out how to set them up, and recalls the third.

**Idea for a later level** (user, 2026-11-15, not for MAP05): the exit
room's door is opened by a switch and shuts again on a timer, so the player
first has to lay a fast route of doors from the switch to it.

## MAP06 "After Hours" (2026-11-16)

Built, solver-proven and walked headlessly. **Not played by hand yet.**
`tools/map_hinges6.py`: a museum at night. Five doors in the puzzle (PINK is
a sixth, in a secret), four keys, six frames, four Stray doors, 13 door
actions, 271787 states, none stuck, nothing losable. 149 monsters, 5
secrets. `MAP=MAP06 ./run.sh`; MAP05's exit leads here.

Vadim's brief: no new ideas (there was one in each of the first five
levels); a big map with puzzles like MAP05's, more of a classic Doom II
level where you go between places and find your way; the way out built as in
MAP05. So nothing here is new to the engine or the solver, and none of
Ajar's own monsters but two lodgers.

**The level.**
- One floor to walk about in: lobby (start, frame), great hall (frame),
  cloakroom (RED), gift shop, cafe (GREEN) and, down steps, a sunken court
  under the sky. Round the court: the upper gallery over its west side
  (RED's far side; key 1), the roof over its east side (YELLOW's; key 3),
  the terrace north of it with the night room off it, bolted inside. A
  mezzanine over the great hall (VIOLET's; key 4). The cellar (GREEN's; key
  2, a frame), whose door up to the cafe is bolted on the cellar side.
- West wing (key 1): four rooms in a ring, YELLOW, a frame, and the office
  (keys 3 and 4). East wing (key 2): four rooms in a ring, VIOLET, and the
  archive (keys 2 and 3): two Stray doors and a super shotgun, optional.
- Two doors from the start, in either order (RED and GREEN); then the two
  wings in either order; the office needs both.
- **The catch** is Vadim's set-up-and-swap idea (see "Idea for later
  levels"). BLUE, the door that belongs in the night room, leans in the
  strongroom behind the office, and the only way in or out of there is a
  hole no door fits through. The strongroom has a frame. Hang BLUE in it
  and you are in the night room without it. To get BLUE out, another door
  must hang in the strongroom's frame instead, and it can only be brought
  there through the night room and BLUE's far side. A door reaches the
  terrace only from above: off the upper gallery (RED) or the roof
  (YELLOW). Then BLUE goes out through the door it was swapped for, and
  round to the terrace the same way.
- The terrace can also be reached from the court with empty hands: steps up
  to a gap by a gatepost (a squeeze: a bare line with id 500, no hole built
  round it). Without it a door hung in the night room by a Stray door's
  luck left the terrace unreachable (the solver found it).
- Why two ways down to the terrace: with only one, that door could end up in
  the strongroom's frame after BLUE is out, and nothing could be carried to
  the night room again.
- Stray pool: the grotto (secret) and the boiler room (a mancubus), and the
  far side of whatever is not hung.
- Secrets: stockroom behind the gift shop (squeeze) and PINK's store; the
  grotto off the court (the office's lever, or a Stray door); the gardener's
  shed (shoot its bell through the bars); a nook off the roof.
- `MAP=MAP06 ./tools/smoke.sh`: 38 checks, to the exit. `MODE=2`: tour, 58
  views (`TIMEOUT=400`). No test of the level's Stray doors or of the bell.

Tried and dropped: a thief in the west wing with YELLOW on its back. With
a wing behind a lock the solver found the player locked out of their own
key (RED swapped into the wing's frame from the far side, key 1 not yet
taken), and it took the state count from 270 thousand to 1.7 million.

`tools/mapcheck.py map_hinges6 out.png` (new; run it in the `ajar-tools`
image) reports overlapping sectors and things standing in walls, and draws
the level's plan.

The level wears stock textures; its look is for a design session.

## MAP07 "Small Hours" (2026-11-16)

Built, solver-proven and walked headlessly. **Not played by hand yet.**
`tools/map_hinges7.py`: an observatory on a hill at night. Five doors in the
puzzle (PINK is a sixth, in a secret), four keys, six frames, five Stray
doors, 12 door actions, 268139 states, none stuck, nothing losable. 170
monsters, 5 secrets. `MAP=MAP07 ./run.sh`; MAP06's exit leads here.

Vadim's brief: the new exit; "side by side" as the level's motif; an
observatory; bigger than MAP06; a calm beginning, monsters a little later;
ways to make the monsters easier by choosing doors well (left to Claude).

**The way out turns you round** (Vadim's idea; `ajarmap.way_round`). The
night room, but nothing in it faces anything. Its west wall has a ready-made
pair of brass openings that are one fixed doorway: into one, out of the
other, back into the room. Its east wall has the far side of an ordinary door
and beside it an empty brass frame. Hang that door there and the east wall
turns you round too: the room repeats through every opening, with you in
every second copy, seen from behind. All four mouths then end the level
(line id 590, `ComeHome`, as in MAP05). No change to the engine or solver.
- One pair alone never shows you yourself: the room seen through it is the
  room turned half round about the pier between the two openings, and the
  pier hides where you would be. So the sight is saved for the end.
- You are small in it: the nearest you is two room lengths away. A shorter
  room would bring it closer. Not tried.
- Open, Vadim's call: once built, should the player be able to walk the loop
  before leaving (the exit somewhere else), instead of every mouth ending
  the level?
- `MAP=TEST MODE=13` checks the room (VIOLET, frame 191, at 4000, 2000 in the
  test box: `warp 4160 2128`).

**Side by side.** Every far side has an empty frame next to it with
something between that cannot be walked: the gate's bars (RED), the height
of the stacks over the library (GREEN) and of the gallery in the dome
(YELLOW), the ravine (VIOLET), bars again in a secret (PINK). The exit is
the same step with nothing to cross. Only RED's and VIOLET's are forced; the
others are where the frames happen to be.

**The level.**
- Quiet start: the road (start), the gate, the forecourt, the hall and the
  west yard have nobody in them. RED leans by the gate, which is bolted
  inside; the frame is beside it and RED's far side three steps beyond the
  bars. Coming through draws the bolt.
- One place to walk about in ("grounds"): gate passage, forecourt, hall
  (GREEN, a frame), library (a frame), dome (a frame), west yard, lane.
- Up: the stacks over the library (GREEN's far side; key 1), the dome's
  gallery (YELLOW's; key 2), the roof between them and the lane, and the
  night room off the gallery, bolted inside.
- North: the hillside (VIOLET leans there; one frame, in the stump of a
  bridge tower), the ravine, the knoll (VIOLET's far side), the transit
  house (keys 3 and 4: BLUE, and the cave's lever).
- The hillside is reached from the lane by a stile (a squeeze), and the roof
  from the hillside by steps and a gatepost (a squeeze: bare line 500, as
  MAP06's). With a door the only ways onto the hillside are off the roof (a
  gap in its rail) and off the knoll.
- West wing (key 1, off the lane): workshop, instrument room (YELLOW), clock
  room (key 4). East wing (key 2, off the hall): lecture room, planetarium,
  orrery, steps down to the cellar (key 3).
- **The catch.** VIOLET cannot leave the hillside by the stile, so it hangs
  in the hillside's one frame: the real step across the ravine. BLUE comes
  down off the knoll to that frame and no further. Swapped in, it takes you
  to the night room (the bolt) with VIOLET in hand. What must hang on the
  hillside instead is YELLOW, and YELLOW gets there only over the knoll:
  through VIOLET, hung somewhere in the grounds by then. Then BLUE goes up
  through YELLOW. (Or RED instead of YELLOW on the hillside, and YELLOW in
  the grounds: the solver allows both.)
- **Monsters made easier by doors.** The library and the dome are the two
  big fights, and both can be had from above. GREEN leans in the quiet hall
  beside a frame: hung there, it puts you on the stacks over the library
  before anything in it has seen you; the frame "beside its far side" is
  down among them. The gallery is reached over the roof with empty hands, or
  through YELLOW later; the dome's own frame is on its floor. Also there for
  whoever thinks of it: nothing that follows you onto the knoll can get off
  it (monsters do not jump into the ravine), and the gate's bars can be shot
  through. None of this is tested or required.
- Stray pool: the boiler house off the yard (a mancubus; bolted inside) and
  the cave in the ravine (secret), and the far side of whatever is not hung.
  No Stray door in the quiet part.
- Secrets: the lens store behind the instrument room (a squeeze; PINK and a
  frame) and, beyond its bars, the armoury (PINK's far side; its own door is
  bolted inside, so a Stray door cannot strand anyone there); the cave (the
  transit house's lever, or a Stray door); the shed in the lane (shoot its
  bell through the bars); an alcove past the cistern (a squeeze).
- `MAP=MAP07 ./tools/smoke.sh`: 36 checks, to the exit. `MODE=2`: tour, 63
  views (`TIMEOUT=400`). No test of the level's Stray doors, the bell, the
  PINK secret, or the fights from above.

Found on the way (the solver):
- A door that only one door leads to (the gallery, by YELLOW) is lost if
  that door ends up in the night room's frame by a Stray door's luck. Hence
  the steps and gatepost: the gallery is always reachable with empty hands.
- A frame in the transit house made the knoll losable (VIOLET hung in it).
- With VIOLET leaning anywhere a door can walk from, the hillside's frame
  is not needed for VIOLET at all: any frame leads to the knoll.

The level wears stock textures; its look is for a design session. The
planetarium borrows the night room's walls and ceiling.

## MAP08 "Closing Time" (2026-11-16)

Built, solver-proven and walked headlessly. **Not played by hand yet.**
`tools/map_hinges8.py`: a department store after the doors are locked. Five
doors in the puzzle (PINK is a sixth, in a secret), four keys, five frames
and the brass one, five Stray doors, 10 door actions, 547056 states, none
stuck, nothing losable. 184 monsters, 5 secrets. `MAP=MAP08 ./run.sh`;
MAP07's exit leads here.

Vadim's brief: the timed exit (see "Idea for a later level"), chosen from
four options put to him on 2026-11-16. The other three, for later: "Deep End"
(public baths, the Flip door, counting your hangings), "Wrong Number" (a
telephone exchange, the Pair door), "Night Shift" (a foundry, no new rule,
disposal as the whole level).

**The shutter** (`ajarmap.shutter`, `ajarmap.lever`; sector tag 600). A
lever sends a rolling shutter up and it comes down by itself 8 seconds later
(`SECONDS` in the map; Doom's own `Door_Raise`). The time left is on the HUD
(`AjarHandler.ShutterTick`), and pulling the lever says what went up and for
how long. From the far side it can be pushed up with USE, for one second: a
way out, not a way to fetch anything. Porch lines keep monsters from under
it, because a shutter that meets something goes up again; the player can hold
it up by standing in it, which only helps someone who is already there.

**A grille across the night room** (`way_home(grille=True)`). Without it the
shutter would be for nothing: any door hung in the brass frame is a way to
carry BLUE in (MAP06's trick). BLUE's far side is in the west half, the frame
in the east half, and the gap in the grille is a squeeze. The east half is
entered with a door only under the shutter. The west half's door to the dock
is bolted inside, as in MAP05 to MAP07; arriving in either half draws it.

**The level.**
- One place to walk about in ("store"): the arcade (start), the lobby (RED, a
  frame), the atrium, the goods passage, and under it the stockroom (a
  frame). The gallery over the atrium's west side (RED's far side; key 1)
  has a gap over the atrium and a hole into the showroom. The roof (GREEN's;
  key 2) has a hole down onto the gallery.
- The door showroom (two frames) is a place doors do not leave: a turnstile
  from the atrium, a hatch to the dock. A door comes in from above only. The
  caretaker's office is a balcony over it (YELLOW's far side; key 4; the
  lever; a window on the dock): its stairs end at a gatepost, so a door comes
  into the office only through YELLOW, and leaves by a gap in the rail.
- The loading dock (VIOLET leans there; VIOLET's far side faces the shutter)
  has a chute down into the stockroom: the way out with VIOLET.
- West wing (key 1): toys, haberdashery, furniture (GREEN, a frame). East
  wing (key 2): china, linen (key 3), carpets (YELLOW). Cash office (keys 3
  and 4): BLUE, and the lever of the shop window.
- **The catch.** VIOLET has to hang in the showroom, and BLUE has to be in
  hand at the lever. Both come into the showroom from above: over the
  gallery (through RED, or GREEN and the roof) or off the balcony (through
  YELLOW, hung in the store). Then: through YELLOW into the office, the
  lever, off the balcony, through VIOLET, across the dock, under the
  shutter. The script's walk does it in 124 tics of the 280.
- The frames the dash can use are the showroom's two. The others are too far
  apart for a runner by the solver's count (the lobby's and the stockroom's:
  2500 units and two ordinary doors; the furniture's: three doors), which is
  why the stockroom's frame is at the far end and why ordinary doors stand
  on those ways. A strafe-runner may beat that. Nothing breaks if so.
- Stray pool: the boiler room off the passage (a mancubus; bolted inside)
  and the shop window (secret), and the far side of whatever is not hung.
- Secrets: the shop window, seen from the start (the cash office's lever, or
  a Stray door); the kiosk in the arcade (shoot its bell through the bars);
  the lamp store behind the carpets (a squeeze; PINK and a frame) and beyond
  its bars the strongroom (PINK's far side); an alcove off the stockroom.
- One lodger, in the showroom, whose two frames are empty until you fill
  them. No thief (proposed as an extra, not built).
- `MAP=MAP08 ./tools/smoke.sh`: 36 checks, to the exit, the dash on foot.
  `MODE=2`: tour, 66 views (`TIMEOUT=400`). No test of the push from inside
  the shutter, the level's Stray doors, the bell or the PINK secret.

`tools/solve.py` now knows:
- `dash=dict(at=, to=, limit=, legs={(a, b): units})`: from region `at` the
  player gets to `to` with whatever they carry if the legs and the doors
  that hang make a route from "lever" to "shutter" within `limit`. A quicker
  runner is luck: allowed for, never relied on.
- `home_door`: the door that makes `home_frame` the way out when its far
  side is in another region (the grille). With it the search goes on past a
  built way out, the door fixed in its frame: having had to build it to get
  out of somewhere loses nothing.
- `AJAR_QUICK=1 ./build.sh` builds without the solver, which now takes about
  three minutes for the eight levels.

Found on the way (the solver):
- A door-island (the showroom) needs two ways in for doors. With the office
  the only one, YELLOW carried into the showroom by a Stray door's luck was
  there for good, and BLUE could never reach the lever.
- With one frame in the store the hands are never empty again after the
  second door. Hence the stockroom's.
- A wrong door run in under the shutter and hung in the brass frame has to
  be able to come out again: hence the push from inside.

Open, Vadim's call: the 8 seconds (one number); whether the lobby and
stockroom frames should be closer, so that a second, harder route exists on
purpose; a thief in the showroom. The level wears stock textures; its look
is for a design session.

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

Lodger (2026-11-14): `AjarLodger` (editor number 20005, 60
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

(Superseded, see "The way out in every level" below.) The way out was on trial behind `AJAR_EXIT` (`AJAR_EXIT=2 ./build.sh`, or
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

The way out in every level (2026-11-15): `ajarmap.way_out(m, x, y, colour)`
builds the night room with the doorway onto itself; MAP01-MAP04 use it and
every new level should. It takes doorway number 9. The streets and the
alley are gone, the graph's goal is called "exit" everywhere, and the
walkthroughs walk into the doorway instead of pressing a switch. The
`AJAR_EXIT` switch and the losing candidates are deleted.

The vault's two imps stand flat against the wall you come in by, one each
side of GREEN's far side (user: "once you enter they're behind you"; the
existing imps, not extra monsters).

Monsters and doors, second fix (2026-11-15). The user saw monsters by a
door attacking "something on the side of the door", and not always coming
through. Cause: the lure is the monster's target, and Doom's monsters
attack what they chase, so they bit or shot the lure standing in front of
the opening, and a monster in biting range of it never walked on. Now,
in `AjarSense`:
- While it is after a lure a monster cannot attack (melee range and
  reaction time are switched off, and given back afterwards).
- In front of the opening it is slid sideways onto the middle line, 2
  units a tic, because the chase walks in whole steps and a demon needs
  to be within 2 units.
- When the player goes through a door, every monster that was after them
  and can see that door follows through it, seen through the door or not
  (`AjarHandler.Followers`).
- A monster too wide or tall for an opening no longer tries.
`MAP=TEST MODE=10` checks it: an imp, a demon and a zombie, none in front
of the door, all follow, and none attacks its lure (before: 2 of 3, and
115 tics of attacking the lure). Still true: a monster does not shoot at
you through a door.

## Look: MAP02 (started 2026-11-15)

Board: https://claude.ai/artifact/VfdHfuaa96vbRtnCW4PUxU (source
`design/map02-board.html`, images in `build/board2/`: `<look>/view_NN.jpg`
cut from the tour shots with ImageMagick, `tex/` swatches).

`AJAR_HOTEL=1..3` dresses the whole hotel in one candidate look
(`tools/gfx_hotel.py`): 1 Grand (bottle green, cream damask, crimson), 2
Seaside (aqua, white beadboard, coral), 3 Deco (teal, black, gold). Kitchen
(white tile, quarry floor), attic (boards) and cellar (MAP01's stone) are
the same in all three. `MAP=MAP02 tools/trial.sh AJAR_HOTEL 0 1 2 3` shoots
them.

**The user chose look 1, Grand, for the whole hotel (2026-11-15)**; it is
the default now. `AJAR_HOTEL=0` is the hotel as first built, 2 and 3 the
losers. The board still shows the choice as open.

**MAP02's look is settled (user, 2026-11-15, after seeing it built): "looking
good as it's built now. Keep it this way."** Do not go on dressing the hotel
unasked: the terrace and garden, the ceilings and the other points at the
foot of the board stay as they are unless the user brings them up. Open
for tidying only: looks 2 and 3 and `AJAR_HOTEL=0` can be deleted from
`gfx_hotel.py` and `map_hinges2.py`, and the board could be marked decided.

## Handoff (2026-11-15, evening)

State: everything above is committed and pushed (`main`). All of MAP01-04
build, pass the solver and their walkthroughs; `MAP=TEST MODE=10`,
`MAP=MAP01 MODE=4` and `5`, `MAP=TEST MODE=4` and `7`, `MAP=MAP04 MODE=3`
passed after the monster fix. Nothing from this session was played by
hand by me. The user has seen the Grand hotel and accepted it. Not yet
reported on by the user: the vault ambush, the way out in MAP02-04, and
the monsters' new door behaviour (they now follow you through a door you
left by, which makes retreating less safe). Ask how those played.

Where to pick up: MAP01 and MAP02 are both settled in look. Next is the
user's call; the candidates are the list below, MAP03's look (same method:
candidates behind a switch, `MAP=MAP03 tools/trial.sh`, a board), and
MAP05 with the Stray door (see the earlier "Next, in order" list).

Next for the look, in order:
1. The user reported not being able to shoot themself in MAP01; it could
   not be reproduced. Ask which door, which frame, where they stood and
   which weapon.
2. MAP03's and MAP04's look, if the user wants them next.
3. Ceilings and lighting of the hall block: everything is evenly bright,
   lamps light nothing, and thin dark beams show where ceilings step by 16
   at the light strips.
4. Doom's props (torches, candelabra, barrels) against the new surfaces.
5. Update the board's lower "before" section, then MAP02-MAP04.

## Look: the lodger (started 2026-11-15)

Board: https://claude.ai/artifact/3Z9UPJgafVasVmHJZfAEXp (source
`design/lodger-board.html`, images in `build/board_lodger/`). Six candidate
looks in `tools/gfx_lodger.py`, each with seven frames (A/B walk, C arm up,
D strike, E dead, F/G coming out of a frame): 1 Shadow, 2 Guest, 3 Missing
door, 4 Knocker, 5 Reach, 6 Shadow guest (my suggestion). `AJAR_LODGER=1..6
./build.sh` puts one into the game; unset is the slab as first built.
`tools/lodger_shots.sh` rebuilds the board's images: sprites, and five posed
photographs per look in MAP02's kitchen (`MAP=MAP02 MODE=3`,
`LodgerPortrait` in `ajar.zs`). None of the six was liked.

Second round (same day; the user found all six of the first "pretty bad"):
the board now shows the lodger as the shadow of a Doom monster (its sprites
drawn with the stencil style in near-black: revenant, arch-vile, zombie,
imp; solid or see-through) and a soft smoke figure (`gfx_lodger.py` look 7,
four times as fine, shown at quarter scale). `tools/lodger_shots2.sh`
photographs them: `ajar_lodger_look 1..7` picks the look in `MAP=MAP02
MODE=3`, passed through `EXTRA` in `tools/smoke.sh`. The headless renderer
shows Doom's fuzz style as plain translucent black, so the shimmer is not
photographed.

**Chosen (user, 2026-11-15): the revenant's shadow, seen through, with brass
eyes.** Built: `AjarLodger` draws Doom's `SKEL` sprites with the
translucent stencil style (near-black, alpha 0.6; set in `PostBeginPlay`
because the style has no name as a property). `AjarLodgerEyes` (`AJLE`, two
brass hinge plates, bright) is carried at its head by the lodger's `Tick`
and shown only while it faces the camera within 50 degrees. While it knocks
the eyes show in the mouth of the frame; it fades in as it steps out and
fades into the frame over a few tics (`Enter` state) instead of vanishing.
`MAP=TEST MODE=7` passes. `EXTRA="+set ajar_lodger_look 0" MAP=MAP02 MODE=3
./tools/smoke.sh DIR` photographs it posed (9: turned aside). Not played by
hand yet. Open: the eyes' height (`EYE_Z` 70) is one number for every
frame, so they drift a little off the head in the punch; the looks that
lost (`gfx_lodger.py`, both `lodger_shots` scripts, looks 1..8 in
`LodgerPortrait`) can be deleted.

## Look: MAP03 (started 2026-11-15)

Board: https://claude.ai/artifact/XvjBbHN3d9YvRAaJfWZNNz (source
`design/map03-board.html`, images in `build/board3/`: `<look>/view_NN.jpg`
cut from the tour shots, `tex/` swatches unzipped from the pk3).

`AJAR_THEATRE=1..3` dresses the whole theatre in one candidate look
(`tools/gfx_theatre.py`): 1 Opera (crimson damask, ivory, gilt), 2 Playhouse
(whitewash, oak, green baize), 3 Civic (teak slats, concrete, orange seats).
The back of the house (corridor, dressing rooms with mirrors, the star's
room, green room, booth, flies, under the stage, back stairs) is the same in
all three. **The user chose look 1, Opera, for every part (2026-11-15)**; it
is the default now. `AJAR_THEATRE=0` is the theatre as first built, 2 and 3
the losers. The board still shows the choice as open.
`EXTRA=-nomonsters MAP=MAP03 tools/trial.sh AJAR_THEATRE 0 1 2 3` shoots
them (monsters off: they walk into the cameras). The property store is not
dressed. The board also lists options that change the level's shape, none
built: a proscenium arch, seats with backs, a chandelier and dim house
lights, boxes.

Built for it:
- `Map.align` (`udmf.py`): a set of wall textures laid by world position
  instead of from each line's start, so a wall cut into pieces by furniture
  shows no seams. Such textures are 64 wide and symmetric. Only MAP03's
  looks use it.
- `fitted`/`room`: `lite` (ceiling flat over a runner) and `lift` (how far
  that ceiling is raised; the theatre's looks use 0). `roomdoor(skin=)`.
- A tier's front is its sector's `side`: a parapet over the house wall,
  one texture per face height.

Bug fixed on the way (user's screenshot of MAP02's lobby, the wall under
the mouth of the upstairs hall drawn 16 too high): a wall hung from the
ceiling (`dontpegtop` upper, `dontpegbottom` lower, any one-sided wall) was
hung from the raised ceiling of a runner's light strip. Runner cells are
now sectors with `lift`, and `udmf.py` draws their hung walls that much
lower. It applies to every level.

## Look: MAP04 (started 2026-11-16)

Board: https://claude.ai/artifact/8RxUXmRfDd8t9npDvAw7K5 (source
`design/map04-board.html`, images in `build/board4/`: `<look>/view_NN.jpg`
cut from the tour shots, `tex/` swatches cut from the pk3's textures).
**The user chose look 1, Tenement, for every part (2026-11-16)**; it is the
default now. `AJAR_YARD=0` is the block as first built, 2 and 3 the losers.
The board still shows the choice as open. Not played by hand in this look yet.

`AJAR_YARD=1..3` dresses the whole block in one candidate look
(`tools/gfx_yard.py`): 1 Tenement (brick, stone bands, sash windows, slate
and iron), 2 Patio (lime wash, painted dados, shutters, pantiles), 3 Inn
yard (timber frames over rubble stone, lattice windows, thatch). Below
ground (cellar, stairs, kennel) and the pantry's shelves are the same in all
three. The strongroom keeps its safes; the closet and the store (PINK's far
side) are not dressed. `EXTRA=-nomonsters MAP=MAP04 tools/trial.sh AJAR_YARD
0 1 2 3` shoots them.

How the yard is built in a look:
- Each side of the yard is a house (W, N, E, S) with its own colour. A
  16-wide strip of yard along each wall carries that house's front as its
  `wall` (`EDGES` in `map_hinges4.py`).
- A front is one texture, 64 by 512, hung from the sky's edge: three
  storeys of 160 (the balcony stands on the first, the roof on the second)
  under 32 rows of eaves. One-sided walls, and the wall over or under any
  opening (`front()`: upper unpegged, lower unpegged), all show the same
  rows at the same height. The fronts of balcony, roof and loft are cuts of
  the same texture with an edge on top.
- Windows are 64-long pieces of wall with their own texture (`windows()`,
  `along()`), placed by hand clear of every opening; they must start at a
  multiple of 64. Under the roof they are a `lower`.
- The roof is two sectors in a look: a strip along the yard whose `side` is
  the house front, and the rest, whose `side` is the light well's lining.
- Railings (user's screenshots, 2026-11-16: the fronts under the balcony
  and the loft stepped up and down, and a column of loft wall stood over
  the loft). Two faults, both fixed for every level:
  - A railing makes its whole line lower-unpegged, so the wall below it
    was drawn from the ceiling instead of from the raised floor. The line
    property `floorpeg` (`udmf.py`) puts it back; the `RAIL` of MAP03's
    and MAP04's looks has it. MAP03's tier fronts had the same fault.
  - A piece of wall that ran past the end of a declared line got none of
    its properties, so railings had holes wider than drawn (MAP03: none at
    all along the flies; MAP04 balcony and loft; MAP05 bridge and
    elsewhere). `rail()` now cuts the wall at its ends in every map, and
    `Map.textmap` refuses to build a map where any declared line ends
    inside a piece of wall. The gaps are now as drawn, i.e. narrower than
    what was played; all walkthroughs pass.
- MAP04's berserk pack lies in the light well in front of the coal hole
  (user: it lay at the far end of the cellar, behind all the demons it is
  meant for).
- The dark column over the yard's two frames is replaced by the front.
  Far sides keep their coloured column.

Options that change shape, light or play are listed at the foot of the
board, none built: real eaves against the sky, marking the frames, evening
light, things in the yard.

## Look: the thief (started 2026-11-16)

Board: https://claude.ai/artifact/5NfE9vX2kBz5K83jy8Bm2i (source
`design/thief-board.html`, images in `build/board_thief/<look>/pose_N.jpg`).
Six looks were shown: the prototype sprite and five of Doom's sprites made
small and recoloured (arch-vile in soot, Wolfenstein guard in black, imp in
ash, arachnotron in brass, arch-vile as a shadow).

**Chosen (user, 2026-11-16): the Shadow.** Built: `AjarThief` draws Doom's
`VILE` sprites at 0.6 with the translucent stencil style (near-black, alpha
0.7), walks on the arch-vile's six frames, raises its arms for the 35 tics
at the hinges and dies with the arch-vile's death. `Dress()` carries its
eyes (`AjarLodgerEyes` at 0.7, shown only while it faces the camera) and
the door on its back: `AjarThiefPack`, the carried door's own sprite in its
colour at 0.72, so that which door it has can be read across the yard.
`MAP=TEST MODE=5`, `MAP=MAP04 MODE=1` and `MODE=3` pass. Not played by hand.
The portrait mode and the board's tooling are gone again (commit 8e2be80
has them); the board's images are in `build/board_thief/`. The `AJTH`
sprites in `gfx.py` are no longer used and can be deleted.
Put to the user and not answered: a sound while it works at the hinges, its
voice (still the revenant's, as the lodger's), what it does when hurt.

## Look: MAP05 and the nailer (started 2026-11-16)

Board: https://claude.ai/artifact/NPE1NJydqajQ3AfFL61K3v (source
`design/map05-board.html`, images in `build/board5/`: `<look>/view_NN.jpg`
cut from the tour shots, `tex/` swatches, `nailer/<look>/pose_N.jpg`). One
page for both. **The user chose look 1, Terminus, for every part, and the
knight's shadow for the nailer (2026-11-16)**; both are the default now.
`AJAR_STATION=0` is the station as first built (its map is byte for byte
the one before this work), 2 and 3 the losers. The board still shows the
choice as open. Not played by hand in this look yet.

`AJAR_STATION=1..3` dresses the whole station in one candidate look
(`tools/gfx_station.py`): 1 Terminus (red brick and stone, iron and glass,
a brick viaduct under the bridge), 2 Metropolitan (cream faience with green
and black bands, steel windows, concrete), 3 Branch line (cream weatherboard
over chocolate, timber trestle, tarred goods side). The signal box, the
engine's painted side and ends, the shed's roof and the benches are the same
in all three. Lockers, lamp room, kiosk and store are not dressed.
`TIMEOUT=500 EXTRA=-nomonsters MAP=MAP05 tools/trial.sh AJAR_STATION 0 1 2 3`
shoots them (50 views each).

How the station is built in a look (`map_hinges5.py`):
- Outdoor walls are 576 high and count down from the sky's edge at 512:
  three storeys of 160 under eaves, 64 more rows below platform level. The
  station's front (`AJ5Y`) stands round the platforms and along the bridge,
  the goods wall (`AJ5G`) round the yard and the loft.
- A canopy, the vestibule and the porches are low pieces (`LOW`) of a taller
  place with their own 128 wall; the wall over their open sides is set with
  `over()` / `low()` (upper, unpegged at the top) so that it carries on as
  the wall beside it. `low()` names the open sides: a bolted door in a
  closed side has no line of its own and would be painted over.
- Windows are 64-long pieces as in MAP04 (`windows()`), also in the wall
  over a canopy's edge.
- Bridge, gallery and loft have a `side`: their front from the deck down
  (the bridge's goes on past the platforms to the rails), with `floorpeg`
  railings as in MAP04. Where a canopy ends against the bridge the line has
  the canopy's wall below and the front above.
- Checked by script: in every look the railings, the sectors' heights,
  lights and tags, and the things are the same as in the stock level. In
  look 1 `MAP=MAP05 MODE=1` (28 checks) and `MODE=3` (8) pass.

The nailer. Six looks were shown: the prototype sprite, the shadows of a
hell knight, a mancubus and a chaingunner, a hell knight in iron grey, and
the knight's shadow with nails in its shoulders. **Chosen: the knight's
shadow.** Built: `AjarNailer` draws Doom's `BOS2` sprites at 0.8 with the
translucent stencil style (near-black, alpha 0.7), walks on the knight's
four frames, nails and strikes with its throwing arm (E back, G down) and
dies with the knight's death. `AjarNailerEyes` (`AJNE`, two nail heads,
bright) is carried at its head by `Tick` and shown only while it faces the
camera, 5 lower while the arm is down. `MAP=TEST MODE=6` passes (4 checks).
Not played by hand. The portrait mode, its tooling and the `AJNL` sprites
are gone; the board's images are in `build/board5/nailer/`.
Put to the user on the board and not answered: a hammering sound that
carries across the station, its voice (still the revenant's), whether the
shed is too dark to find a shadow in, and the "beyond paint" list (light,
sky beside the bridge, a platform edge, the train, station things, marking
the frames).

## Look: MAP06 (started 2026-11-16)

Board: https://claude.ai/artifact/TjZtXwZGefUcSF8V4twLmG (source
`design/map06-board.html`, images in `build/board6/`: `<look>/view_NN.jpg`
cut from the tour shots, `tex/` swatches). **The user chose look 2, Cabinet,
for every part (2026-11-16)**; it is the default now, with the dressed cellar,
boiler room, stockroom, grotto and shed (the user did not pick those
separately: ask if they should go back to safes). `AJAR_MUSEUM=0` is the
museum as first built (its map is byte for byte the one before this work), 1
and 3 the losers. The board still shows the choice as open. Not played by
hand in this look yet.

`AJAR_MUSEUM=1..3` dresses the whole museum in one candidate look
(`tools/gfx_museum.py`): 1 Athenaeum (Portland stone, marble, antiquities on
Pompeian red and ochre, paintings on damask), 2 Cabinet (buff terracotta
banded in slate, glazed tile, mahogany, specimens), 3 Kunsthalle (white
render over concrete, black steel, abstracts). The same in all three, and
dressed for the first time in any level: cellar, boiler room, stockroom,
grotto, gardener's shed. The strongroom keeps its safes; the store (PINK's
far side) and the night room are not touched. In looks 1 and 2 `MAP=MAP06
MODE=1` passes to the exit; the tour was shot in 0 to 3 (58 views, monsters off),
no engine warnings.

How the museum is built in a look (`map_hinges6.py`):
- One front (`AJ6Y`), 640 high, stands round the court and the terrace,
  counted down from the sky's edge at 512: attic to 336, upper floor to 160,
  ground floor to 0, 128 rows below ground for the sunk court. What stands in
  front of it is a cut of it: under the upper gallery an arcade (`AJ6YG`),
  under the roof the east front (`AJ6YS`), the terrace's edge (`AJ6YE`), the
  wall round the roof (`AJ6YU`).
- The upper gallery has a ceiling, so its railings also carry the wall over
  it (`rail(..., upper=, dontpegtop=)`), and a 16-deep strip of it at the
  great hall has its own `side`, the hall's wall.
- `pieces()` / `pictures()`: 64-long wall pieces with windows or exhibits,
  each starting at a multiple of 64. Those over an opening are declared
  before the `porch()` / `over()` of the whole opening: a piece of wall takes
  the first declared line that contains it.
- Room and bolted doors have a face per side (`door()`, `bolted()`;
  `FACES`, `BOLTS` in `gfx_museum.py`): the wall of the room it is seen from
  carries on over the leaf, drawn for the door's own place in that wall's 64.
- The rooms of each wing take two wall colours by turns round the ring.
- Cases, desks, benches and railings repeat every 16, so they need no
  aligning; walls are in `Map.align` (`gfx_museum.aligned`).

Options that change shape, light or play are at the foot of the board, none
built: dim rooms with lit exhibits, statues on the hall's plinths, a parapet
and sky at the roof's edge, marking the frames, fewer exhibits, dressing the
earlier levels' secrets the same way.

## Handoff (2026-11-16, night)

State: `main` has MAP01-MAP06; all build and pass the solver. Every level
up to MAP05 is settled in look (MAP05: Terminus, chosen from the board on
2026-11-16), and all three of Ajar's own monsters have their looks: lodger
(revenant's shadow), thief (arch-vile's shadow), nailer (hell knight's
shadow). No branches or worktrees are left besides `main`.

Run after the last change (MAP05's look and the nailer): the full build,
`MAP=MAP05 MODE=1` and `MODE=3`, `MAP=TEST MODE=6`. Not rerun: the other
levels' walkthroughs (their maps did not change; `gfx.py` only gained
textures and lost the `AJNL` sprites), MAP05's tour as built by default.

Open, the user's call:
1. Play MAP05 in the Terminus look and meet the new nailer; neither has
   been played by hand. In the dark engine shed the shadow is hard to see:
   ask whether that is right.
2. MAP05 beyond paint and the nailer's sound (foot of the board, see
   "Look: MAP05 and the nailer").
3. MAP06 has no look yet: same method (candidates behind a switch,
   `tools/trial.sh`, a board; shoot with `EXTRA=-nomonsters`).
4. Still unanswered from before: MAP03 beyond paint, the undressed stores
   and secrets (MAP03's property store, MAP04's closet and store, MAP05's
   lockers, lamp room, kiosk and store: one direction could do for all),
   the thief's sound and what it does when hurt, a nailed Stray door
   staying open.
5. Tidying when wanted: the losing looks (`AJAR_HOTEL` 0, 2, 3;
   `AJAR_THEATRE` 0, 2, 3; `AJAR_YARD` 0, 2, 3; `AJAR_STATION` 0, 2, 3;
   `gfx_lodger.py`; the `AJTH` sprites), and the boards could be marked
   decided.

Working notes for the next session:
- The user plays from the main checkout's `build/ajar.pk3`. Do design work
  in a worktree so that builds and smoke runs do not replace it under a
  running game, and give `tools/smoke.sh` an output directory of its own.
- A build without the solver is enough while only textures change (the
  solver is most of the two minutes); run the real `./build.sh` at the end.
- `Map.textmap` refuses a line that ends inside a piece of wall: `m.cut()`
  its ends. A line given for a whole edge also applies to every piece of
  that edge without a line of its own, a bolted door's face among them.

## Handoff (2026-11-16)

State: MAP01-MAP05 build and pass the solver. MAP01, MAP02 and MAP03 are
settled in look (MAP03: Opera, chosen from the board, not yet played by
hand in that look). After the look and the wall fix only MAP03's
walkthrough was rerun (17 checks pass) and MAP02's lobby was photographed;
the other levels' smoke tests were not rerun since `udmf.py` changed
(`lift`), so run them first: `MAP=MAP0x ./tools/smoke.sh` for 1, 2, 4, 5.

Open, the user's call:
1. MAP03 beyond paint (foot of the board): a proscenium arch, seats with
   backs, a chandelier with dim house lights, boxes beside the stage; and
   whether the room tints are missed as a guide to the six doors.
2. The property store (PINK's far side) is not dressed; no direction given.
3. MAP04's and MAP05's look, same method (candidates behind a switch,
   `tools/trial.sh`, a board). Shoot with `EXTRA=-nomonsters`.
4. Not played by hand yet: MAP03 as rebuilt, MAP05, the lodger's new look.
5. Tidying when wanted: the losing looks (`AJAR_HOTEL` 0, 2, 3;
   `AJAR_THEATRE` 0, 2, 3; `gfx_lodger.py`), and the three boards could be
   marked decided.

## Difficulty (2026-11-16)

Asked for after MAP05 by hand: too hard for the user, who does not want the
level itself made easier. Four levels, `src/mapinfo.txt`:

| `SKILL` | name | Doom's monsters | damage taken | ammo |
|---|---|---|---|---|
| 1 | Just visiting | about half | x0.5 | x1.5 |
| 2 | Short stay | about three in four | x0.75 | x1.25 |
| 3 | Resident | all (the levels as designed) | x1 | x1 |
| 4 | Night shift | all, and quicker to attack | x1.5 | x1 |

- "Resident" is the default in the menu and what `+map` starts, so the smoke
  tests play it as before.
- The thinning is automatic (`Map._skills` in `tools/udmf.py`): of each kind
  of monster, in the order placed, every second one stays on 1 and three in
  four on 2; the first of a kind always stays. `m.thing(..., skill=N)` pins
  one thing to "from N up" by hand. Nothing is pinned yet.
- Doors, keys, pickups, the thief, the nailer and the lodger are the same on
  all four: the puzzle and the solver do not know about difficulty.
- To try one: `SKILL=1 MAP=MAP05 ./run.sh`. A new game from the menu asks.
- Not known: whether the numbers are right. None of the four has been played
  by hand.

## Look: MAP07 (started 2026-11-16)

Board: https://claude.ai/artifact/8JZuyVeqzcCYRmVED2SNbu (source
`design/map07-board.html`, images in `build/board7/`: `<look>/view_NN.jpg`
cut from the tour shots, `tex/` swatches). **The user chose look 3, Star
Palace, for every part (2026-11-16)**; it is the default now. The board still
shows the choice as open. Not played by hand in this look yet.

`AJAR_OBSERVATORY=1..3` dresses the whole observatory in one candidate look
(`tools/gfx_observatory.py`): 1 Royal (brick and Portland stone, sashes,
cream panelling, oak, brass), 2 Mountain (granite, shutters, limewash and
pine, a riveted iron dome), 3 Star Palace (fluted concrete, bronze, midnight
blue and gold, travertine). `AJAR_OBSERVATORY=0` is the level as first built
(until the next section's changes: its map was byte for byte the one before
this work); 1 and 2 are the losers. The same in all three:
the wood round the hill (`AJ7XN`), rock in the ravine, the lens store, the
armoury; the cellar, boiler house, cave and shed wear MAP06's (`AJ6XC`,
`XB`, `XG`, `XS`). The night room is not touched.

How the observatory is built in a look (`map_hinges7.py`):
- Three kinds of open air: the grounds (`OPEN`: a garden wall with trees
  over it, `G`), between the building's own walls (`BUILT`: the front, `Y`)
  and the hill (`WILD`). Pieces of a place's wall that are the building's
  are named with `front()`, windows with `windows()` before it.
- `fit()` is `ajarmap.fitted` and also carries the wall on over the open
  sides of every porch in the room; a porch at the room's edge that faces
  another place needs its own `over()` (the tower's stump, from the ravine).
- A door's face is drawn for its own place in its wall. The map works out
  the shift, names the texture and lists it in `FACES`; `gfx.make_all` hands
  that to `gfx_observatory.make`, so only the look being built has doors.
  Texture names stop at 8 letters: hence numbered faces.
- Library: two tiers of books, the stacks' floor carried round as a rail;
  `LS`, `LV`, `LB` are cuts of the same wall. Dome: shell, ring and wall in
  one texture 448 high.

Run: the tour in 0 to 3 (63 views, monsters off, no engine warnings);
`MAP=MAP07 MODE=1` in looks 1 and 3 to the exit; the full build. Not run: the
walkthrough in look 2, and nothing played by hand.

Options that change shape, light or play were at the foot of the board: a
telescope on the pier, an octagonal dome, dim rooms, a horizon instead of the
wood, the planetarium's own look, an orrery and a globe. The user said yes to
all six (2026-11-16, "let's try" for the dome and the dim rooms): see the
next section.

## MAP07: the dome, the dark, the hill (2026-11-16)

Built on top of the Star Palace look; all of it is there in looks 0 to 2 as
well (`AJAR_OBSERVATORY=0` is no longer the level as first built). The board
does not show any of this. Not played by hand.

- **The dome is eight-sided**: the square 768 with 192 cut off each corner.
  The gallery follows it round the west, north and east. The frame on the
  floor and YELLOW's far side on the gallery are where they were, each now in
  a low bay that opens out of a slanting wall (a frame cannot stand in a
  slanting wall: its recess would run into the hall or the night room, and
  portals are only tried square to the grid). The gaps in the gallery's rail
  moved 64 south (west and east) and to x 64..128 (north). The middle of the
  roof is stepped up 64 (`LANTERN`); the slit runs through it. On the roof
  outside, the floor runs into the two cut corners, so the dome shows three
  faces. The puzzle graph is unchanged.
- **The telescope** stands on the pier (`AjarTelescope`, sprite `AJTE`, 16
  sides), pointing north out of the slit. It is a sprite and stops nothing:
  no shot, no monster. `tools/gfx_things.py` draws it, the planetarium's
  projector (`AJPJ`), the orrery (`AJOY`) and the hall's globe (`AJGB`) from
  solids (tubes, balls, rings), once from each side. The orrery and the globe
  stand on plinths where glass cases were.
- **The planetarium** has its own look: eight-sided, a dome in three steps
  with the sky on it (`CS`, `ES`), a town's roofs round the wall (`EP`), a
  carpet (`FE`), the projector in the middle. It no longer wears the night
  room's walls.
- **Small hours**: indoors is dim (hall 140, library and stacks 120, dome
  120, rooms 125, planetarium 100) with a pool of light in three steps round
  every lamp (`LAMPS`, which also places them) and a lit top and a ring round
  every glass case, plinth and the pier. `AJAR_DIM=0` builds it evenly bright
  as before. New lamps: one on the stacks, two on the gallery's corners.
- **The hill is open** on the east and west of the hillside and the ravine
  and round the knoll (`horizon()`, `ajarmap.beyond`): a bank of rock 32
  high that nothing walks or flies over, the tops of the wood below
  (`AJ7XT`), and the country beyond under the sky. The ravine's far bank
  west of the knoll has the cave behind it, so there the sky comes down to
  48 along its foot (`SHELF`) and the bank ends at that height. The level has
  its own sky, `AJ7SKY`: stars, the Milky Way, a moon. The walls round the
  grounds are as they were.

In the tools:
- `ajarmap.shaped` is `fitted` for rooms with slanting walls and many small
  changes: features may be convex polygons, the room an `outline`, and
  pieces alike are joined (MAP07 is 1215 sectors with all its pools).
  `ajarmap.octagon`, `ajarmap.beyond` (strips along the outside of an edge).
- `udmf.py`: `fit=(point, stretch)` on a line lays aligned textures along a
  slanting wall, stretched to a whole number of 64s (`slant()` in the map);
  `midraise` lifts a middle texture; `upper="-"` leaves the wall over a line
  bare, which is what lets a middle texture stand above a lowered sky. A
  line marked `exact` that something else cuts (a pool's edge through the
  transit house's lever) now keeps its special and shows its part of the
  picture on each piece; before, it silently lost both.
- A thing by a slanting wall needs its whole square clear of it, not its
  radius: `tools/mapcheck.py` says so.

Run: the tour (77 views, monsters off, no engine warnings); `MAP=MAP07
MODE=1`, 38 checks to the exit; `mapcheck`; the full build with the solver.
Looks 0 to 2 and `AJAR_DIM=0` were built and loaded, not toured.

## Ideas for the next levels (2026-11-16, to discuss)

Vadim's three ideas, with Claude's notes. Nothing here is built, and nothing
marked "to test" has been tried in the engine.

### 1. The bus stop

Vadim: the teleporter bus of "Гостья из будущего" (1984). In the film it is
the flat red outline of a bus standing at a stop, with six numbered doors;
each door opens onto another part of Moscow, and which doors you get depends
on which side you come at it from. Ours has empty frames and far sides of
coloured doors mixed along it.

Notes:
- **No new rule.** It is a slab with recesses in it: far sides, frames, and
  perhaps fixed doorways (`ajarmap.doorway`) as lines that always run. A
  helper `ajarmap.bus()` and a look (red outline, a number over each door, a
  destination board in the door's colour) is all it needs.
- **It turns the levels inside out.** Until now doors lie near the middle and
  their far sides are far away. With the far sides on the bus, every coloured
  door is a ticket back to the stop, and it is found out in a district. Hang
  it there and that district has a line; the player builds the network.
  With frames on the bus too, a door whose far side is in a district makes an
  outbound line. Fewer bus frames than doors that want one is the puzzle:
  which lines run at the same time.
- **Two faces.** The slab can stand in a wall between two places that do not
  otherwise meet (the square and a fenced depot): the same bus, other doors,
  as in the film.
- **Company fits.** A thief whose zone is the stop is a dispatcher changing
  the routes (the solver has this already). Lodgers live in the bus's empty
  frames. A Stray door in a bus frame is the bus with no number on it.
- **How flat.** A portal line needs its 48 stub behind it, so the slab is
  about 64 thick with the recesses flush in its face, and doors of the two
  faces have to alternate along it instead of standing back to back. On a
  slab 500 long that should still read as flat. To test.
- **To test:** six openings in view at once, each drawing another place
  (MAP04's yard shows three). Doors in one flat wall never face each other,
  so there is no hall-of-mirrors depth to pay for.
- Several buses, one per district, would be the film's network, but the far
  sides can only be in one place: the other stops would be frames and fixed
  doorways only.

### 2. The way out as a chain

Vadim: the exit room has the far sides of two doors of different colours.
Another room has two frames on opposite walls. Hang the two doors there and
the chain closes: the endless way.

Notes:
- **It works, and both ways round.** Say BLUE's far side is in the exit
  room's east wall and VIOLET's in its west wall, and the other room has a
  west and an east frame. BLUE west and VIOLET east gives a straight endless
  corridor in which the two rooms alternate. The other way round, each door
  turns you about (as MAP07's does) and the loop still closes. So there is no
  wrong way to hang them, only two different sights.
- **The exit room needs no other entrance** and no bolted door: it is reached
  through BLUE or VIOLET only, from wherever they hang. Seen early it is a
  room with two door backs in it and nothing else, which is the hint.
- **Where the puzzle is.** Two doors have to end up in one room, each carried
  there with the other one's errands already done, and both are then spent.
  The frame room is where a door is hard to bring (MAP05's turnstile, MAP06's
  strongroom, MAP08's shutter all carry over).
- **It grows.** A loop of n rooms needs n doors: each room has a way in and a
  way on, each a frame or a far side. Three rooms and three colours is the
  secret exit, below.
- Engine: `ComeHome` checks one frame for one door; it would check that a
  loop of hung doors runs through the exit room. Solver: `home_frame` becomes
  a set of (frame, door) choices. Both small. The view is the one
  `way_out()` already draws.
- Open, as since MAP07: when the chain closes, does every mouth end the
  level, or may the player walk the loop first?

### 3. More colours, other shapes

**Secret exit by the longer loop (three colours; Claude's suggestion for
PINK).** The exit room has BLUE's and VIOLET's far sides; the brass room has
two frames; PINK's far side is in a third room that has one frame. The plain
way out is the loop of two: BLUE and VIOLET in the brass room. The secret one
is the loop of three: BLUE in the brass room, PINK in its other frame, VIOLET
in the pink room's frame. Which loop was closed decides the exit. Nothing new
to learn: a player who understood the chain can find it, and sees a pink room
in the corridor where no pink room was.

**Rooms that are not square.**
- A door joining two walls that are not opposite turns you. In a six-sided
  room with three far sides and three frames, all walls open, the room
  repeats in every direction like a honeycomb; in a three-sided one, three
  colours tile the floor with triangles. Which door hangs in which frame
  changes the pattern, so one arrangement can be the secret. To test:
  recesses on slanted walls (every opening must stay 64 wide, so the corners
  fall off the grid; `recess()` is written for straight walls only), and how
  deep the engine draws when every wall is a door.
- A round room (a dome) with frames all round its wall and a thing in the
  middle to fight round: which far side is behind you matters.

**Mirrors.** GZDoom has real wall mirrors (`Line_Mirror`). To test: with
these portals in view, and in the GLES backend.
- For reading a room: a mirror at a corner shows a frame, a far side or a
  monster before you are in front of it.
- Things only a mirror shows (the engine has a flag for it, to test in
  4.12): the lodger's eyes in the frame it is waiting in. A mirror then tells
  you which frame to plug.
- A door hung beside its own far side is already a kind of mirror that shows
  your back (MAP07). A hall with one of each makes the difference a joke.
- Not proposed: a mirror door with a rule of its own. The plan's rule is new
  situations, not new rules.

**The arrangement is the map (three or more colours, no new rule).** Three
frames in three places that can only be reached through the doors hanging in
them, and a lock that wants a certain door in a certain frame (the frame's
surround in the door's colour says which). With one hand, moving a door
changes what you can reach next. The solver can search for arrangements that
take many moves; the limit on colours is still the player's memory (six or
seven a level).

### Decided

**MAP09's way out is the chain** (Vadim, 2026-11-16). The rest of the level's
brief is open: see "Questions for Vadim", 3 and 4, and the place.

What the chain needs before the level (checked in the code, not built):
- `AjarHandler.Hang` calls `ComeHome` when one frame gets its one door
  (`f.args[1] == d.args[0]`). The chain calls it when the loop through the
  exit room is closed, from whichever of the two doors is hung last, and
  fixes both doors. Taking either down before that must stay possible.
- `tools/solve.py`: `_won` and the "it stays" test know one `home_frame`.
  They become a set of frames, each with the doors that count there.
- `ajarmap`: a helper for the two rooms (far sides at the ends of one,
  brass frames at the ends of the other), and a `MAP=TEST` mode for it.
- `src/mapinfo.txt`: MAP08's `next` is still MAP08.

### Claude's view

- The chain (2) is the smallest step and the surest: build it next, with the
  loop of three as the secret exit of the same level.
- The bus (1) deserves a level of its own, a town square with districts; it
  changes how a level is laid out more than it changes any rule.
- Mirrors and slanted rooms need an engine test in the test box before any
  level counts on them.

### Questions for Vadim

1. Bus: are its fixed lines two-way doorways, or one-way (you step out at a
   stop and need the district's door to come back)?
2. Bus: one face or two?
3. Chain: walk the loop, or leave at once?
4. Secret exit: where does it lead? There are no secret levels yet.
5. Same level for the chain and the bus, or one each?
