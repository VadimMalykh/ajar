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

### Step out of the fight (Vadim, 2026-11-17: saved, nothing checked)

An idea for the portal into the past, perhaps for the secret level (MAP10's
secret way out leads to one that is not made yet).

- The player starts a battle. At some point they may leave it through the
  portal.
- Outside they mend (health, whatever else is there), go back, and see that
  same battle from the side, their earlier self in it.
- At the moment the earlier self left, a new portal opens: through it the
  player is in the battle again and carries on.
- It can be done several times. With health low again, out again, and the
  battle is watched from the start with two earlier selves in it, then
  three; each time the player comes in where the last one went out.

**Built: see "MAP31".** What follows was the question then.

Not looked at yet: how it sits with "No real rewind" above (it reads as the
recording played to its end and then handed over, never branched), and what
a trip costs.

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

(Superseded 2026-11-16: see "Playable, and less obvious". The grille is gone;
the brass frame takes BLUE only and the room has no door.)

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

## Look: MAP08 (started 2026-11-16)

Board: https://claude.ai/artifact/WMj8oWyQRb9cwQpwjaPf3N (source
`design/map08-board.html`, images in `build/board8/`: `<look>/view_NN.jpg`
cut from the tour shots, `tex/` swatches). **Chosen 2026-11-17: 3, Festival,
for the whole store**, and it is the default; `AJAR_STORE=1` or `2` are the
other two, `AJAR_STORE=0` the plain textures. The board shows none of what is
under "MAP08: after hours" below.

`AJAR_STORE=1..3` dresses the whole store in one candidate look
(`tools/gfx_store.py`): 1 Emporium (1880s: red brick over green cast iron, oak
panelling, encaustic tile, pressed tin, a deep paper to each department),
2 Grand Magasin (1900s: cream stone, sea-green iron and gilt, ivory panels over
marble, mahogany, coloured glass round the atrium), 3 Festival (1950s: buff
brick, plate glass over turquoise mosaic, teak, lino, one flat colour to a
department). The same in all three: the houses round the arcade (`AJ8XS`), the
goods passage (`XP`), the kiosk (`XN`), the shop window from inside (`XW`), the
lamp store (`XL`), the doors on show (`XD`); the stockroom and the boiler room
wear MAP06's (`AJ6XK`, `XB`). The strongroom keeps its safes; the night room
is not touched.

How the store is built in a look (`map_hinges8.py`, as MAP07's):
- The arcade's wall is the houses; the pieces that are the store are named
  with `front()`, its windows with `pieces()` before it. The dock and the
  roof have the store's back (`K`). Outdoor porches take the foot of the wall
  they stand in (`low(wall=)`: `YP`, `KA`, `AJ8XT`).
- The atrium's wall is one texture 448 high: a clerestory, the gallery's
  wall, the ground floor's. The showroom's is two storeys of 160.
- `shelves(tag, ...)`: 64-long pieces of a department's wall with fitted
  shelves of what it sells, two kinds by turns.
- `over()` carries a wall on above and below an opening, so holes above the
  floor (from the gallery, from the roof, the chute) need nothing else.
- Door faces as in MAP07 (`FACES`; "D" room doors, "Z" bolted, "S" the
  shutter). Both levers stand on the look's own wall (`LV`, `LC`).

Run: the tour in 0 to 3 (66 views, monsters off, no engine warnings).
To shoot again: build with `AJAR_QUICK=1 AJAR_STORE=n`, then `MAP=MAP08 MODE=2
TIMEOUT=400 EXTRA=-nomonsters tools/smoke.sh <dir>`; the board's pictures were
cut to 819 by 512 with the `dpokidov/imagemagick` image.

## MAP08: after hours (2026-11-17)

The options at the foot of the board, all asked for and all built; they are
there in looks 0 to 2 as well (signs and plates only in a look). The walkthrough
reaches the exit and the solver's answer is unchanged (10 door actions). Not
played by hand.

- **Lights out** (`AJAR_DIM`, on by default; `0` is evenly bright). As MAP07:
  `LAMPS` is every indoor lamp, `fit()` is `ajarmap.shaped` with `pools()` and
  `glowing()` (glass counters). The shop window, the kiosk and the caretaker's
  office (`LIT`) are lit. Monsters on the gallery are harder to see.
- **Glass roofs** (`glazed()`, features for `fit()`): panes are sectors with
  the sky 16 above bars of iron (`AJ8XI`). The atrium's lantern stands 48 over
  the ceiling on an upright of small panes (`AJ8XJ`, laid by world position in
  every look: `gfx_store.ALWAYS`). The arcade is roofed in iron with two rows
  of eight panes, kept clear of the porches.
- **The arcade's east end** is a gate (`AJ8XG`, nothing passes) and beyond it
  a street running north and south, darker with distance. Nobody gets there.
- **Signs**: `hung()` hangs one under a porch's edge (the two wings and the
  goods passage, from the atrium); `plates=` on `door()` and `opening()` puts a
  small plate over an inner door, on either side. Letters are gfx.py's 5 by 5.
  `udmf.py`: a wall laid by world position keeps its place over a line that
  is one picture (`exact`); no other level's map changed by it.
- **Things** (`gfx_things.py`, actors 20025 to 20029, `AjarExhibit`): two
  shop's dummies, a rocking horse, a till, rolled carpets. They block nothing.
  The cash office has a desk for its till (new, 64 by 48 at its north wall).
- **The roof's edge**: west and north-west the wall is gone. `ajarmap.beyond`
  lays a parapet 24 high (a blocking line: nothing walks or flies off), the
  roofs next door 128 below, and the town as a cut-out (`AJ8XH`) against the
  sky. South, east and the stair head are still wall.
- The tour has nine more views (66 to 74) for these.

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

**Built: see "MAP09".** Vadim's answers (2026-11-16): the player walks the
chain, but not a full lap: one crossing into the real exit room, and leaving
that room ends the level. The secret exit (the loop of three, PINK) is for
the level after. The place is a telephone exchange. No other new idea.

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

## MAP09 "Putting You Through" (2026-11-16)

Built, solver-proven and walked headlessly. **Not played by hand yet.**
`tools/map_hinges9.py`: a telephone exchange at night. Five doors in the
puzzle (PINK is a sixth, in a secret), four keys, six frames and the two
brass ones, five Stray doors, 12 door actions, 513330 states, none stuck,
nothing losable. 166 monsters, 4 secrets. `MAP=MAP09 ./run.sh`; MAP08's exit
leads here.

Vadim's brief: the way out as a chain (see "Ideas for the next levels", 2);
walked, one crossing; a telephone exchange; otherwise the usual puzzles.

**The chain** (`ajarmap.way_through`, `ajarmap.brass_pair`).
- The line: the night room, with nothing in it but BLUE's far side at its
  west end and VIOLET's at its east end. The trunk room has two brass frames
  (190 and 191) facing each other. With BLUE and VIOLET hung in them, either
  way round, the two rooms open onto each other without end and both doors
  stay for good. Nothing ends yet: the player walks through one of them onto
  the line, and leaving the line again, by either door or by its hole, ends
  the level.
- One of the two in a brass frame is a door like any other and can be taken
  down again.
- Engine: a brass frame's thing has `args[3]`, the other brass frame, and
  `args[1]`, `args[2]`, the two doors' far-side lines (`AjarHandler.Chain`).
  An `AjarLine` thing (editor number 20006) stands in the middle of the line
  with the room's half lengths as its args; `ChainTick` ends the level when
  the player has been inside that box and is then 24 beyond it. Solver:
  `home_chain=dict(frames=, doors=)`.
- `MAP=MAP09 MODE=3 ./tools/smoke.sh` checks it by itself (9 checks). There
  is no chain in the test box: it has no two colours to spare.
- The line is a way between any two frames BLUE and VIOLET hang in, for
  whatever is carried. The level is built on that.
- A Stray door may open onto either end of the line, so it needs a way out
  on foot. It stands 96 above the forecourt and a hole in its south wall
  lets you drop out: never in. From the start you see the hole and a starry
  ceiling behind it.

**The level.**
- One place to walk about in ("main"): the forecourt (start, nobody), the
  call office (RED, a frame), the switchroom (a frame), the cable passage,
  and under it the battery room (a frame).
- Up: the supervisor's gallery over the switchroom's west side, with the
  cable loft as its north end (RED's far side; key 1); the roof (GREEN's;
  key 2), with a hole down onto the gallery; the monitor's balcony over the
  switchroom's north-east corner (YELLOW's; key 4).
- The trunk room is a place doors come into from above only: a hole in the
  loft's floor. Its way in from the switchroom is a hatch (a squeeze); a
  chute lets a door out again into the battery room.
- West wing (key 1): canteen, cloakroom, rest room (GREEN, a frame). East
  wing (key 2): apparatus room (key 3), relay room (YELLOW, a frame), and
  off the apparatus room the test room. Manager's office (keys 3 and 4):
  BLUE.
- **The catch.** VIOLET leans in the test room, whose only way in or out is
  a hatch no door fits through; the test room has a frame. Hung there,
  VIOLET takes you onto the line without it. Another door has to hang in
  that frame instead, and a door comes into the test room only along the
  line: through BLUE, hung somewhere, and out by VIOLET's far side. Then
  VIOLET leaves through the door it was swapped for. Any of RED, GREEN and
  YELLOW will do; the solver's own answer hangs BLUE in a brass frame for
  it, so the first trip along the line starts in the trunk room.
- Stray pool: the generator room off the passage (a mancubus; bolted inside)
  and the kiosk (secret), and the far side of whatever is not hung.
- Secrets: the kiosk in the forecourt (shoot its bell through the bars, or a
  Stray door); the stationery store behind the relay room (a squeeze; PINK
  and a frame) and beyond its bars the strongroom (PINK's far side); an
  alcove off the battery room.
- One lodger, in the trunk room, whose brass frames are empty until the end.
- `MAP=MAP09 ./tools/smoke.sh`: 34 checks, to the exit. `MODE=2`: tour, 41
  views (`TIMEOUT=400`). No test of the chute, the level's Stray doors, the
  bell or the PINK secret.

Found on the way (the solver):
- YELLOW's far side was first on a mezzanine inside the east wing. A Stray
  door could open onto it before the wing was unlocked, with RED in hand;
  RED hung in the wing's frame and the player out through it, and the wing's
  key was out of reach for good. A far side must not be behind a lock.

Open, Vadim's call: whether leaving the line by its hole should end the
level too (it does now); the two switchboards under the gallery's gap, which
a jump down lands on. The level wears stock textures; its look is for a
design session. Next: the level after has the secret exit, the loop of three
with PINK.

## Fights, MAP03 to MAP09 (2026-11-16)

Asked for by Vadim: a backpack (there was none), and the monsters of MAP03
to MAP09 placed for livelier fights, judged as a Doom II player would.
Only things moved: no wall, door, key or frame, and the solver's graphs are
as they were.

What was wrong, by the numbers (`tools/budget.py`, `tools/thingcheck.py`):

- No backpack anywhere, with 150 to 230 shells lying about a level and room
  for 50.
- From MAP04 on the rocket launcher was only in PINK's secret, from MAP08 the
  plasma rifle only in the kiosk, while rockets and cells lay on the main
  way.
- MAP07 to MAP09: ammunition worth 1.3 to 1.5 times the monsters' health,
  secrets included, and about 400 health on the way for 25000 to 28000 of
  theirs.
- About 70 monsters stood inside another monster or a lamp (MAP05 2, MAP06 7,
  MAP07 17, MAP08 23, MAP09 21, MAP03 1), and one imp on a crate under a
  ceiling too low for it.
- The berserk pack was behind the fight it is for (MAP05: the far corner of
  the yard; MAP06 to MAP09: in the boiler room, behind a mancubus).

What changed:

- A backpack in every level from MAP03, early and in plain sight: cloakroom,
  wash house, waiting room, gift shop, the hall, the enquiry desk, the call
  office.
- Berserk before the teeth: MAP03 at the mouth of the stalls (the pit now
  has four demons and a spectre), MAP05 at the head of platform 1 over the
  tracks, MAP06 by GREEN in the cafe (the cellar), MAP07 by the library's
  door, MAP08 and MAP09 at the head of the stairs down. MAP04's was right.
  The boiler rooms have a soul sphere and rocket boxes instead.
- Weapons on the way: launcher in MAP05's signal box, at the head of MAP06's
  court steps, on MAP07's stacks and MAP08's and MAP09's gallery (each over a
  crowd); plasma on MAP06's mezzanine, in MAP08's office, on MAP09's balcony.
- Monsters that fight each other: guns behind fireballs and teeth as seen
  from where the player comes in (MAP05 concourse, MAP06 great hall and
  court, MAP03 bar and stage, PINK's store), the mancubus at the far end of
  MAP05's shed behind the spectres, men round barrels by the way in (MAP04
  yard, MAP05 platform 1).
- Shell boxes, rocket boxes and medikits until every level has ammunition
  worth 1.8 to 2.7 times its monsters and 360 to 900 health.
- Every monster stands clear.

Not done, Vadim's call: the numbers of monsters are as they were (MAP07 to
MAP09 have 166 to 184, fifteen hell knights each); the crossfire from the
galleries over MAP06's court and the 30 monsters of MAP08's atrium and
MAP09's switchroom are still what a pistol start meets. None of it has been
played by hand.

## Playable, and less obvious (2026-11-16)

Vadim, after playing MAP08: the grille across the night room spoils the
endless room; the fights of MAP06 to MAP09 may be thinned; the targets that
open secrets are too easy to see.

**MAP08's night room has no grille.** What the grille was for: any door hung
in the brass frame was a way to carry BLUE in, without the shutter. Now the
brass frame takes no door but BLUE (`way_home(only=True)`, AjarFrame
`args[4]`, in a PUZZLE `only={HOME: BLUE}`; it says so when another is
tried), and the room's bolted door to the dock is gone: you come in through
BLUE and leave through it, or push the shutter from inside, and BLUE comes in
under the shutter or not at all. "night" and "home" are one region again and
`home_door` is not used by any level (the solver still knows it, and
`way_home(grille=True)` still builds). This is one more exception to "a
frame takes any door": only this frame, only in MAP08.

**A bell, not a target.** `AJTARG` was a red and white bullseye. It is now
the secret room's own wall with a small brass bell on it (`gfx.bell`):
`AJTARG` on the vault wall (MAP05, MAP08, MAP09), `AJTARG4` in the hole over
MAP04's yard (no longer floodlit), `AJTARG6` among the tools on the shed's
wall (MAP06, MAP07). MAP04's two bonuses on the roof still mark where to
stand.

**Thinner.** MAP06: one chaingunner on each gallery over the court instead
of two, one cacodemon in it, one knight in the night room. MAP07 155 monsters
(170), MAP08 164 (184), MAP09 152 (166): eight or nine hell knights each
instead of fifteen, and about a quarter fewer in MAP08's atrium and MAP09's
switchroom, with one chaingunner on the gallery over each.

## Doors drawn as two left halves (2026-11-16)

Seen by Vadim in MAP06 (the boiler room's door, the gift shop's). Where a
room's floor pattern puts a vertex in the middle of a door's line, the line
is built in pieces and each piece drew the door's face from its own left
edge. 21 doors in MAP04 to MAP09 had it. `roomdoor()` and `bolted()` now mark
their mouth lines `exact`, and `udmf.py` carries a cut line's offset to the
wall over the opening as well as to its middle texture.

## Levers that look like levers; ambushes (2026-11-16)

**Levers.** Vadim, in MAP06's office: the lever does not look like a switch
and nothing happens when it is pulled. It worked (the grotto opened, out of
sight). Now:
- `gfx.lever` / `gfx.levers`: a brass-rimmed switch box at hand height on the
  room's own wall, lamp red and lever up, lamp green and lever down once
  pulled: `AJ5LV` (signal box), `AJ6LV<look>` (museum office), `AJ7LV<look>`
  (transit house), `AJLEVR` (plain wall, MAP08's cash office), `AJLEVB`
  (brick, the shutter's lever), each with an `N` twin. `animdefs.txt` is
  generated and names every pair as a switch, so Doom moves it and gives it
  its sound.
- `AjarHandler.WorldLinePreActivated` says what a lever or a bell did
  ("Somewhere in the building a bolt is drawn").

**Ambushes** (`ajarmap.ambush`, thing 20030 `AjarAmbush`,
`AjarHandler.AmbushTick`). There were none: every monster stood in its place
from the start. An ambusher is a monster that comes in a teleport flash when
the player takes a room key (cause 1..4) or first takes a door (10 + colour;
not used yet). No closets, no geometry: the thing is a marker and the script
spawns the monster there, awake, once the place is free. Thinned on the
easier difficulties like placed monsters. Two or three per level from MAP03
to MAP09, five to eight monsters a level; the list is at the foot of each
map's things. `tools/budget.py` and `tools/thingcheck.py` count an ambusher
as the monster it will be.

## MAP09 rebuilt (2026-11-16)

Vadim, after playing MAP08 and starting MAP09: the two begin alike. They
did: MAP09 had been laid out on MAP08's plan with the rooms renamed, down to
the monster lists. The puzzle (the chain, VIOLET in the test room, the trunk
room entered from above only) is kept; the building and the way into it are
new (`tools/map_hinges9.py`, its docstring has the plan).

- The switchroom is a long hall, east to west, with the gallery along its
  north wall and the balcony in its south-west corner. The line hangs over
  the east end of the forecourt; the kiosk is at the west end.
- RED opens onto the roof now and GREEN onto the gallery: the first trip is
  out under the sky, key 2 is in the roof's far corner, and the hole down
  onto the gallery leads to key 1. Both wings can then be opened in either
  order. Key 3 moved to the west wing (the cloakroom), so that wing is still
  needed.
- The thief is back, in the east wing, with YELLOW on its back
  (`thief=dict(zone="east")`). The east wing has no frame: with one, the
  thief hangs YELLOW in it, a Stray door can put the player on the balcony,
  and from there the wing is entered without its key; the solver then found
  the player shut out for good (RED left inside, key 2 on the roof). So the
  thief is to be caught, and has nowhere to hang what it carries.
- The battery room, the cable passage and the generator room are north-east,
  under the trunk room's chute.
- 10 door actions, 312528 states, none stuck, nothing losable. 145 monsters
  with the ambushers. `MODE=1` (58 checks, the thief killed first), `MODE=3`
  and the tour (`MODE=2`) are rewritten for the new plan; `smoke_MAP09_1.cfg`
  waits longer.
- `roomdoor(free_inside=True)` exists (a locked door that needs no key from
  inside) and is not used: it did not cure the above.

Not done: a look for MAP08 and MAP09; neither has been played by hand as
rebuilt.

## The repainter (built 2026-11-16)

In the plan since 2026-11-14 as one line ("swaps where two doors lead,
irreversible, not built"); Vadim asked for it in MAP09. `AjarRepainter`
(`src/zscript/enemies.zs`, editor number 20007, 70 health, does not fight):

- A door's colour is where it leads. The repainter walks to a door, hung or
  leaning, and takes its colour: its shadow turns that colour and a line says
  which door it touched. That is the warning. Then it walks to a second door
  and the two change places (`AjarHandler.Repaint`: the two doors trade
  colour and far-side line; what hangs is linked again). It does not put them
  back and paints no door twice. Killed with a colour on its brush it has
  changed nothing.
- It leaves alone a door in somebody's hands, a nailed door, a Stray door and
  whatever hangs in a brass frame. With nothing to do it wanders.
- `tools/solve.py`: `repainter=dict(zone=[regions])`: while it lives any two
  doors hanging or leaning in its zone may change places; the player can kill
  it there. Its life is the second bit of the state's thief flag.
- MAP09 has one, in the switchroom (zone: main and the west wing): 10 door
  actions, none stuck, nothing losable with it. `MAP=MAP09 MODE=4` tests it
  (GREEN in a frame, BLUE leaning: they change places and the frame opens
  onto the line).
- Open, Vadim's call: its look is provisional (the shadow of an imp, no
  eyes; the other three were chosen from boards); its sounds are the imp's;
  whether it should be seen at work before it may swap, as the thief must be
  seen to take a door down. In MAP09 it only bites when two doors are left
  about the switchroom at once (a second door hung in 102 as a shortcut).

## Look: MAP09 and the repainter (started 2026-11-17)

Board: https://claude.ai/artifact/EzEwGjnDYZv6be3jTcPKyr (source
`design/map09-board.html`, images in `build/board9/`: `<look>/view_NN.jpg`,
`tex/` swatches, `rp/<look>/pose_N.jpg`). **Chosen by Vadim, 2026-11-17:
look 1, Central, for the exchange; candidate 2, Family, for the repainter.**
Both are built and are what the game now is. Branch `look9`, not committed.
Not played by hand.

`AJAR_EXCHANGE` picks the exchange's look (`tools/gfx_exchange.py`); the
default is 1, 2 and 3 build the two that lost, 0 the plain level (whose map
was byte for byte what it had been before the looks, checked). 1 Central (1900s: red brick and
terracotta, cream over mahogany and brown glazed brick, bottle-green iron,
brass, mahogany cord boards), 2 Trunk (1930s: brown brick over Portland
stone, cream over green gloss paint, oak, lino, black cord boards), 3 Crossbar
(1960s: a concrete frame and blue panels, white and grey with one colour to a
room, teak, vinyl tile, grey desks of keys). The same in all three: the
houses across the road (`AJ9XS`), the kiosk (`XN`), the stationery store
(`XL`), the cable loft and its drums (`XC`, `XD`), the shaft from it (`XH`),
the battery room and its cells (`XB`, `XJ`), the cable passage (`XP`), the
generator room (`XG`), coats (`XK`). The strongroom keeps its safes; the line
is not touched.

How it is built (`map_hinges9.py`, as MAP08's): `fit()`, `low()`, `over()`,
`pieces()`, `front()`, `door()`, `bolted()`, `opening()`, `squeeze()`,
`bars()`, `hall()`; door faces in `FACES`. New here: a call box's front is
one picture on its north line (`lower=`), switchboards repeat every 32 and
have a face on both long sides, the trunk room's wall under the hole from the
loft is its own 288-high texture (`TRH`).

The tour has six more views (42 to 47: the gallery and the balcony from the
hall, the loft past its drums, the call boxes, the front, the battery room's
cells), because 10 and 17 look into furniture; 48 in all, and
`smoke_MAP09_2.cfg` takes 48 shots. `tools/board9_shots.sh` builds and shoots
all four (about 15 minutes), look 1 last, so the pk3 is left as the game is.

**The repainter** (`AjarRepainter.Dress`): the imp's shadow with the lodger's
brass eyes at 0.7 (`EYE_Z` 45), shown while it faces you as the thief's are.
The shadow no longer turns the colour: while a colour is on its brush only
its eyes are that colour. `MAP=MAP09 MODE=5` photographs it at work before
the switchroom's frame (six shots); `MODE=4`, its test, passes, and so does
MAP09's walkthrough in look 1. The candidates that lost (a mancubus' shadow,
the marine in overalls, an imp in whitewash, a chaingunner's shadow) and
their portrait mode, cvar and translations are deleted; the board's
photographs of them remain in `build/board9/rp/`. With a colour on its brush
it walks to the second door, so the coloured eyes are seen only when that
walk is towards you.

Put to Vadim at the foot of the board, none built: lights out, signs,
things on the floor, the forecourt as a street, the roof's edge, sound, the
switchboards under the gallery's gap; for the repainter: a sound or drips
with the warning, whether it must be seen at work, its voice, its size.

## MAP10 "All Change" (2026-11-17)

Built, solver-proven, its two ways out walked headlessly. **Not played by
hand, and no walkthrough test of the whole level yet.** `tools/map_hinges10.py`:
a town square at night and a bus at its stop. Six doors, all in the puzzle,
two keys, seven frames (three of them brass), four Stray doors, 9 door actions
(the secret way out: 11), 1920764 states, none stuck, nothing losable, the
secret way out included. 142 monsters and 17 that come by ambush, 4 secrets.
`MAP=MAP10 ./run.sh`; MAP09's exit leads here.

Vadim's brief (2026-11-17): the bus; a secret exit in the same place as the
plain one, built of other colours, PINK one of them, and counted as a secret;
districts that are the earlier levels; a route board; the square as an arena;
ambushes; the repainter; lodgers in the bus.

**The repainter comes when it has work** (Vadim, 2026-11-17: standing in the
square at the start with nothing to paint, it was shot before it did
anything). It is an ambusher now, cause 20 (`AjarHandler.WorkNear`): it comes
in a flash once a door it may paint hangs or leans within 700 of its place at
the stop, and goes to it. Not built: another that comes after the first is
killed.

**The bus** (`ajarmap.bus`, `tools/gfx_bus.py`). See "Ideas for the next
levels", 1; the engine questions there are answered.
- **It stands free in the square and you walk round it** (Vadim, 2026-11-17:
  "more really like the bus in the movie"; before that it stood in the
  depot's gateway, a face each side). Two faces, a front and a back
  (`ajarmap.bus(free=True)`, `bus_ends`). Doors 1 to 6 face the stop: 1 the
  hotel and 5 the station (lines that always run: fixed doorways), 2 a frame,
  3 GREEN's far side, 4 no number (a place Stray doors open onto), 6 a brass
  frame. In its back, from the lane: 7 a second frame, 8 the observatory
  (always runs). The depot is a yard beyond the lane; nothing on the bus goes
  there, YELLOW's far side is in its wall, and its gate lets out into the lane.
- How it is drawn: the bus is a solid block 144 high with the sky over it.
  The engine cannot show anything over a solid block but sky, as far up as
  the sky goes (a pocket with a ceiling, such as a door's recess, shuts off
  whatever is behind it in plan). So **nothing that can be seen behind the
  bus may be taller than the bus**: the square's walls are 144 high, sky at
  144, with porches at 128 where a door or a hole comes out high (the stage
  door, the depot's gate, the hole from the line, whose floor came down to
  64). A bus with taller houses behind it would want 3D floors; not tried.
  The faces are 144 apart, the recesses back to back. Six portals in one view
  draw without trouble (GLES, headless).
- **The places are the earlier levels as they stand** (Vadim, 2026-11-17:
  door 1 was "just a room"; "bigger parts of other maps"; and let them have
  doors of their own that lead to other levels or to the stop).
  `ajarmap.excerpt(m, src, at, dx, dy)` lifts out of another level's Map all
  that can be walked to and back from a point without a carried door, with
  its furniture, windows, ordinary doors, monsters and pick-ups; frames, far
  sides, locked and bolted doors, keys, exits and secrets stay behind, and it
  returns the places where recesses were, for this level's own. So: line 1
  arrives where MAP02 began (its whole ground floor, 12 monsters), line 5
  where MAP05 did (concourse, platforms, tracks, 52), RED's far side is in
  MAP03's foyer (foyer, house, rooms behind). RED leans in a hotel room,
  YELLOW on the station's far platform, GREEN behind the theatre's foyer.
  The museum, the depot and the observatory are still my own small rooms:
  MAP06 and MAP07 lift out as well (MAP07: 646 sectors, 84 monsters), not
  done. More frames in the districts are possible but each multiplies the
  solver's states (seven frames: 1.9 million).
- **The other stop** (Vadim, 2026-11-17: a door to another part of the level
  with a similar bus and other doors). Door 8 of the 10 is door 1 of the 20,
  an amber bus (`gfx_bus.LIVERIES`, `bus(livery=)`) in a square of its own:
  2 the pit under the theatre's stage door (the theatre's way out on foot),
  a door with no number, and in its back 4 the observatory. All of it is
  "main" in the PUZZLE, which did not change.
- The route board in the shelter (`ajarmap.route_board`,
  `AjarHandler.BoardTick`): a lamp for each door of the bus, in the colour of
  what hangs there or, for a far side, lit while that door hangs anywhere.
- Districts wear the looks chosen for their levels: hotel (MAP02), station
  (MAP05), theatre (MAP03), museum (MAP06), observatory (MAP07). The square,
  the depot and the bus are provisional: a look board is still to come.

**The two ways out.**
- Plain: MAP09's chain. The brass frames are door 6 of the bus and the one in
  the shelter facing it; the line hangs over the shelter (BLUE, VIOLET).
- Secret (`ajarmap.way_longer`, `AjarHandler.LoopLen`): PINK opens onto a room
  with a brass frame of its own. PINK and one of BLUE and VIOLET at the stop,
  the other of them in PINK's room: a loop of three rooms. Closing it gives a
  secret at once (the level counts one more than it has secret sectors), and
  leaving the line by it is `Exit_Secret`, which leads to MAP31 (see "MAP31").
- PINK's store (ring its bell from the museum's gallery) and PINK's room are
  secrets as before, so finding the long way round is the level's fourth.
- **Nothing is fixed when a chain closes** (Vadim, 2026-11-17; MAP09 too). A
  brass frame is a frame like any other. The loop's doors stay only once the
  player has walked onto the line through it; leaving the line ends the level.
- PINK's room's frame takes BLUE and VIOLET only (AjarFrame `args[4]` = 2, in
  a PUZZLE `only={HOME3: (BLUE, VIOLET)}`). The third exception to "a frame
  takes any door", after MAP08's.
- `MAP=MAP10 MODE=3 ./tools/smoke.sh`: 18 checks, both loops, out by the
  secret one. `MODE=2`: tour, 42 views (`TIMEOUT=400`).

**The level.** "main" is the square, the hotel, the station and the
observatory's library. RED (hotel) opens onto the theatre: GREEN, key 1.
YELLOW (station) onto the depot: key 2, which opens the dome off the
library, BLUE under it. The solver was run on three ways of standing the
bus free (the library on line 8 or behind the depot, a second frame or
none): 9 and 11 door actions every time, nothing stuck. The dome's floor
is sunk (Vadim, 2026-11-17: a longer puzzle if the solver can bear it; it
was 8 door actions): a ledge, a drop, stairs up to a hole no door fits, and
a frame, as in the museum's cellar. So two doors are spared for BLUE and
VIOLET while a third keeps a line running. The museum is on
the square (key 1): VIOLET in its cellar, which you drop into with what you
carry and leave by a hole no door fits, so VIOLET leaves through another
door hung in the cellar's frame; PINK in its store.

Found on the way (the solver):
- The theatre had no way out but RED. The repainter, or a Stray door, shut
  the player in. It now stands on the square's south side, a step up, and its
  stage door lets out and never in.
- A Stray door can open onto PINK's room with any door in hand. RED or YELLOW
  hung in that room's frame was gone for good, and the level with it: hence
  the frame that takes two doors only.
- The depot's way out was a hole for empty hands. Whoever carried YELLOW in
  (through PINK's room) had shut the depot, BLUE inside. It is a gate now, a
  step down, and takes a door through.
- The depot's face of the bus had a frame (door 8 of three). With that and
  the dome's, RED and YELLOW could both be left hanging on the depot's side,
  and nothing led to the theatre or the depot any more. That face has no
  frame now.
- With six doors the first draft (seven frames, three keys, a locked office)
  took the solver past ten minutes and 2.5 GB. This one takes two minutes.
  `tools/build.py` now keeps each level's proof (`build/proofs.json`) until
  its puzzle or the solver changes.

Settled (Vadim, 2026-11-17): the square is empty until a key or a door brings
company to it. Open: GREEN is in no shortest solution (the solver hangs
YELLOW in the cellar and has a line from there to the depot); nothing of
this level's fights has been played.

## Look: MAP10, the film's bus forty years on (started 2026-11-17)

Vadim, 2026-11-17: the bus is to be known for the film's by somebody who has
seen "Гостья из будущего", not copied from it, and forty years older than it
was there; and the parts of other levels are to be dressed as they are in
those levels. Branch `look10`, not committed. **Not played by hand.** No
board of three: the brief was the look.

**The bus** (`tools/gfx_bus.py`, `ajarmap.bus`). The film's is a flat plywood
bus painted red with a row of numbered doors. Ours: solid red gone chalky, a
yellowed cream roof edge and waist stripe, windows in black rubber, painted-on
wheels at its two ends, and over each door a white route plate with the
number in black. Russian on the bus and nowhere else in the game: `АВТОБУС 10`
on its front, and on the plates of the lines that always run where they go
(`ГОСТИНИЦА`, `ВОКЗАЛ`, `ПЕРЕСАДКА`; on the 20: `ПЕРЕСАДКА`, `ТЕАТР`,
`ПЛАНЕТАРИЙ`). The door with no number has lost its plate: the red it kept the
sun off, two screw holes. Forty years: rust from the gutter and from under
the windows, paint gone in patches with the plywood's plies under it, a
cracked window, one boarded with a sheet of ply, a dead headlamp, road dirt
and moss along the foot. Five panels (`AJ?US`, `AJ?US1..4`) laid by turns so
that no two alike stand side by side; the ends are `AJ?USZ`/`AJ?USY` (the
corner on the left, on the right). The 20 is the same in faded amber. The
depot's buses that are only buses wear the same side, and a roof (`AJQRF`).

**The square** (`tools/gfx_square.py`, `AJAR_SQUARE=0` for the plain
textures). One look. The fence is the cast-concrete panel with lozenges that
every Soviet yard had (`AJQF`; with posters, with a corner knocked out); it
is the right height for walls that may not be taller than the bus. Asphalt
with patches and cracks, slabs under the stops, a sheet-steel shelter with
the stop's yellow sign and what is left of a timetable, a blue sheet-steel
kiosk, slatted benches. The museum's side of the square is terracotta and
stone (MAP06's colours) and its door has a face of its own there. The depot
is sand-lime brick and oiled concrete. Canopy edges say BUS STOP, PRESS,
MUSEUM, DEPOT (English, as every sign of the town). The line, PINK's room
and the two secret rooms are not touched.

**The other levels' pieces, checked** (`tools/excerptcheck.py`: every line
MAP10 has in common with MAP02, MAP05 and MAP03 compared, both sides'
textures, offsets, flags, the sectors behind; `-v` lists each difference).
What it found, and what was done in `ajarmap.excerpt`:
- Where a level went on beyond the piece taken, the wall kept what hung on
  the line: a railing's texture over the whole wall (the station's gallery,
  the theatre's circle and gods), and the stage was a blank wall. Now what is
  seen from the ground and out of reach comes along as **scenery**: the
  station's gallery, bridge and carriages, the theatre's stage, curtain,
  circle and gods, the hotel's upper hall. Nobody gets there: every step
  from the ground to scenery is more than 24 (checked in the code), nothing
  that can be dropped into is taken, monsters and pick-ups stay behind;
  lamps and exhibits come.
- Locked and bolted doors were plain wall. They are the same doors **nailed
  up** (`ajarmap.boarded`, `gfx.boarded`: three boards across the leaf), so
  that a lock plate with a 1 on it does not ask for this level's key 1.
  Doors up in the scenery are shut and not boarded.
- The theatre's north circle is where this level's stage-door pit is. It
  comes along with the pit cut out of it (`without=`), 16 deep over the pit.
- What still differs, on purpose: this level's own recesses where the
  source had its own; frames and far sides are wall; the bell targets of the
  sources' secrets are gone with the secrets.
- The museum and the observatory are this level's own small rooms, not
  excerpts. They now use MAP06's and MAP07's own dictionaries and rules
  (imported, so a change of look there arrives here): the great hall 384
  high with porches and the wall over them, the wing's gallery 160 with its
  pictures, the cellar 128 with a tall bay under the hole; the library 320
  and the dome 448, dim with pools of light at lamps and torches as MAP07
  is, doors and frames under porches with faces made for their walls, the
  telescope on the pier. Before, the walls hung from the wrong heights (a
  384 wall on a 256 room) and nothing was laid by world position. The dome
  is square, not eight-sided, and has no slit: MAP10's sky is not MAP07's.

**MAP09: the switchroom's porches** (Vadim, playing, 2026-11-17: "wall
texture near the door is broken"). Every indoor porch of MAP09 is in the
switchroom, and wore the generic porch wall (`A`), whose dado is 8 lower
than the switchroom's and which has no pilasters: the panelling stepped at
each porch. They wear the switchroom's own wall now (`HP`: the lowest 128 of
its ground floor's; `HQ`: of its gallery's), and the door faces there are
made on it.

## MAP09 shuffled (2026-11-17)

Vadim, playing through: MAP09 was still too like MAP08 (the start outside
the front door, a wing on key 1 and a wing on key 2, the office on keys 3
and 4, the same secrets in the same places, a cellar of demons). The puzzle
(the chain, the test room's catch, the trunk room from above, the thief, the
repainter) and the rooms stayed. What moved:

- **Start**: on the roof, a shotgun to hand and a few imps. The hole lets
  down onto the gallery, over the switchroom and its night shift, with the
  rocket launcher there. RED (call office) is the only way back up. The
  forecourt is come to last, by the front door: what was on the roof
  (cacodemons, a revenant, a hell knight) is there now.
- **Keys and locks**: key 1 on the roof; the west wing is open, and key 1
  opens the cloakroom in it, where key 2 is; key 3 is in the far corner of
  the battery room; keys 2 and 3 open the east wing; key 4 (the balcony,
  YELLOW's far side) alone opens the manager's office.
- **Secrets**: the kiosk has no bell: a lever between the trunk positions
  draws its bolt (line 307). The stationery store and the strongroom are
  behind the cloakroom's coats, not behind the relay room. The alcove is
  behind the cable drums in the loft, not off the battery room.
- **The battery room**: hell knights, a revenant and a cacodemon for the
  demons and spectres; the berserk lies before the canteen's door.
- Kept on purpose: the seat across the rest room's doorway (Vadim).
- Solver: 10 door actions, 1304192 states, 0 stuck, nothing losable.
  `MAP=MAP09 ./tools/smoke.sh`: 35 checks. Not played by hand.

## Levels 11 to 30: the institute (2026-11-17, to discuss)

Vadim and Claude, brainstorming while MAP01 to MAP10 are polished. **Nothing
here is built and nothing has been tried in the engine**; every engine claim
below is an expectation. Vadim's answers so far: the institute for 11 to 20,
yes; 21 to 30 carry it on to the reveal; the Pair door to be discussed and
shown in a demo; all the effects, geometries and time ideas below go on the
list.

### The place

Not fantasy and not clean science fiction: in a wizard's tower or on a
starship a portal is expected, and the paradoxes of 1 to 10 work because the
places are ordinary. So: **a research institute that studies the doors**, in
the line of the film's Institute of Time (MAP10's bus already points there)
and of Soviet "institute of magic" fiction. Ordinary corridors, a canteen, a
pass office, a cloakroom; and labs where the geometry was bent on purpose.
It gives a reason for machinery (lifts, conveyors, pumps, clocks) and for
the time doors. Original place and people: nothing lifted from the film or
the books but the kind of building.

**11 to 20: the institute as it was left.** The player goes through the
departments, each one a lab for one idea below. What they see is the
apparatus, not yet the cause.

**21 to 30: how it happened** (Vadim: the paradoxes, the monsters and the
rest were scientific experiments that went wrong). Claude's suggestions for
how the reveal can be played and not told, to argue over:
- The time doors are how the player sees it: a Stale door onto a lab on the
  day of the experiment, the staff still there.
- The monsters are what was on the far side of the first door that was ever
  hung (the plan's Squatters, at the scale of a world).
- The doors of 1 to 10 (the hotel's, the theatre's, the station's) are found
  here as specimens, with the frames they were cut from: the town was the
  field trial.
- The last levels are the experiment itself, the first frame and the first
  door, and the player's choice is what hangs in it.

### The Pair door

In the type table since the first day, not built. A plain door has one fixed
end, so the player chooses half of every link. A Pair is two leaves that lead
to each other: **the player joins any two frames.** Core rule 1 still holds:
what a Pair leaf remembers is its twin.

How Claude thinks it should work (proposed, each point open):
- **Two leaves, one colour**, carried one at a time like any door (decided). Both hung:
  each frame opens onto the other. One hung, the other leaning, carried or
  stolen: the hung one is a shut door.
- **The rope** is its basic move (corrected 2026-11-17: a leaf can only be
  hung where the player stands, so a Pair never reaches a place for them; it
  keeps a place they have been). Hang one leaf, carry the other down a drop,
  through a plain door or past a timed shutter, hang it there: the way back
  is open and stays. Go through, take down the leaf you came out of, hang it
  further on: the same rope paid out. It also sets a plain door free: go up
  by RED, hang a leaf, and RED is not needed for that place any more.
- **Both leaves in one room** make the sights: opposite walls, the endless
  corridor; walls at a right angle, the pinwheel; side by side, the U-turn.
  So the Pair is also the player's tool for every effect listed below.
- **With plain doors** it makes chains whose middle link the player moves.
- **Company**: a thief with one leaf shuts the link from anywhere; a lodger
  comes out of either end.
- Frames only: a leaf does not go in a far side's recess.
- Engine: the two frame lines target each other (`Line_SetPortalTarget`
  both ways). To check in the code: that a frame's recess can be the arriving
  side as a far side's stub is. Solver: a second free end in the state.

Vadim's answers (2026-11-17): one leaf at a time; several Pairs in a level,
certainly; what a leaf hung alone shows, to be seen both ways in the demo.
Still open: whether a brass frame takes a Pair leaf (brass frames are the
ones that take only certain doors: MAP07's way out, MAP09's trunk room).

**Built: the lab** (`tools/map_lab.py`; `MAP=LAB ./run.sh`). Vadim played it
(2026-11-17): "all looks great", and the Pair goes into the levels to come.
**A leaf hung alone is a shut door** (Vadim, 2026-11-17, having tried both:
"shut door was ok"). The other thing tried was a picture of what the twin
looks out on from where
it leans (a camera texture, by a lever in the lab): taken out again, lever
and all, the same day. Both TEAL leaves and a plain RED door in a hall with
frames 111 west and 112 east (opposite: the endless corridor), 113 south
(round the corner from 112: the room repeats turned), 114 and 115 south
(side by side: each turns you round) and 117 (a spare). A gallery too high
to climb has RED's far side, frame 116, both ORANGE leaves and the way out:
the rope.
- How it is made: a leaf is an `AjarDoor` with `args[4]` the pair's number
  and colour 8 (TEAL) or 9 (ORANGE). Its `args[0]` is 0 until both hang and
  then the line of the twin's frame, so `Hang` and `Unhang` link frame to
  frame with the code plain doors use, and whatever asks where a hung door
  leads is told the truth. A frame's recess does serve as the arriving side.
  `ajarmap.pair`.
- Left out of Stray doors' and the repainter's reckoning. **Not tried with a
  thief, a nailer or a lodger**, and the solver does not know Pairs.
- `MAP=LAB tools/smoke.sh`: 13 checks (`LabScript`), all pass, and TEST modes
  1 and 13 and MAP09's chain still do (those three on the host's GZDoom
  with SDL's offscreen video driver, while docker was down; the lab's
  in the `ajar-tools` image as well). Built with `AJAR_QUICK=1`: the solver
  was not run on the branch.

Supporting types from the table, for the same levels: One-way (loops that
run one way round) and Small (a hatch: shots and sight, no walking).

### Effects (what doors that see their own room can show)

MAP07's way out (`ajarmap.way_round`: four mouths in one room, where every
other level has two) is hard to read although it is simple, because every
opening shows the room you are in from another side, with you in every
second copy, and the eye has no outside to hold on to. The same family:
- **Inside-out room.** A thin booth in a square, a far side in each of its
  four faces; the four frames on the four walls of a hall. From the hall you
  see the square looking north, east, south and west from one point: the
  hall has no size. The bus is half of this already.
- **Pinwheel.** A door on the wall at a right angle to its own far side: the
  room repeats turned, and you see yourself from the side.
- **Jigsaw wall.** Six far sides side by side in one place, six frames in a
  row elsewhere. In order, the wall is one wide window; out of order, a
  scrambled picture. The order can be the lock. To test: whether something
  wider than one door can pass two neighbouring openings.
- **Honeycomb and triangle rooms**, and mirrors: in "Ideas for the next
  levels", 3; still waiting for the slanted-recess and `Line_Mirror` tests.
- **The model room** (weakest, kept as a note): the generator builds a room
  a second time at four times the size; a door into it makes you small.

### Geometries the player builds

- **Moving room.** A far side inside a lift car: the door opens onto the car
  wherever the car is, so the same door leads to another floor after a ride.
  The other way, a frame in the car carries a far side from floor to floor.
  To test: a portal line on a sector whose floor moves, and which height
  alignment `Line_SetPortal` wants for it.
- **Sight lines.** A switch that can only be shot through a chain of doors
  the player lines up (shots already cross). The same for monsters: let two
  groups see each other and they fight.
- **Bottle.** Lead followers into a loop, step out sideways, take the door:
  they are shut in a pocket.
- **Conveyors.** A belt (Doom's scrolling floor) that ends at a frame
  delivers what it carries, barrels or a weight for a plate, to wherever
  that door's far side is.
- **Canal lock.** The door to the reservoir floods the room it is hung in
  (scripted water level, not real flow); the player floats up to a high
  frame, and chooses which room.
- **Train of rooms.** Modules with a far side at one end and a frame at the
  other: the order of hanging is the order of the rooms along the corridor.
- **Roundabout.** An ordinary teleporter is a fixed one-way line; with doors
  for the way back the player closes a circuit that runs one way only.
- **The arrangement is the map**: in "Ideas for the next levels", 3.

### Time

- **Relay run.** MAP08's 8 seconds, but the way out is too far to run: lay
  the track of doors first, then pull the lever and run it. Several layouts
  work, none is the right one.
- **Metronome.** A fireball going round a closed loop strikes a shoot-switch
  every lap and holds a timed shutter up; the length of the loop is the
  beat. To test: a projectile that keeps going round.
- **Timetable.** Frames behind shutters that open by the clock: a link
  exists for part of the time, and a route is a set of connections to make.
- **Step out of the fight**: under "Time doors"; the late or the secret
  level (MAP10's secret way out still leads to a level that is not made).

### First tests (test box, before any level counts on them)

1. A portal line on a lift's sector.
2. A projectile circulating in a closed loop.
3. The inside-out room: how deep the engine draws four doors that see each
   other.
4. The Pair demo above.

## MAP09: the start is back on the street (2026-11-17)

Vadim, the same day: the roof is not a place to start, and it is very hard
at once. The rest of the shuffle stays (the keys, the locks, the secrets,
the cellar).

- **Start**: the forecourt again, at the front door, with nobody about. The
  call office is the first room and has the shotgun; RED leans there and
  its far side is on the roof, as before the shuffle.
- **The roof**: key 1 stays in its corner (the far one from the hole). Who
  was there before the shuffle is back (imps, sergeants, a chaingunner, two
  cacodemons, a revenant, a hell knight, lost souls) with the super
  shotgun, and taking key 1 brings a cacodemon and two imps again. The
  forecourt's watchers are gone.
- Solver graph: `start="main"`. The autotest takes RED to the call office's
  frame first (`startsInForecourt`, `onRoof`), and `redHung` is gone.
- Solver: 10 door actions, 1304192 states, 0 stuck, nothing losable.
  `MAP=MAP09 ./tools/smoke.sh`: 36 checks. Not played by hand. (Built late:
  docker's store on /data was lost with the failing disk, and docker now
  keeps its data in /var/lib/docker.)
- **More to shoot with at the start** (Vadim: the kiosk's bell went with the
  shuffle, and with it the plasma rifle you could have at once): a shotgun,
  shells and clips on the forecourt's path; the call office's gun is a
  chaingun, with a box of shells and a box of bullets by the counter; a
  box of each at the way into the switchroom. Thingcheck 0 problems, smoke
  36 checks. Not played by hand.

## The line ends the level only by its doors (2026-11-17)

Vadim, playing MAP09: walking onto the line through the closed loop does not
end the level, and that is right; but leaving it by its third way out (the
drop, MAP09's hole over the forecourt) did. Now only leaving by one of the
line's two doors ends the level. Out by the drop, nothing ends: the loop's
doors stay hung (they were fixed when the line was walked onto), and the
line can be walked again.

- `ChainTick` keeps where on the line the player last was (`lineAt`); a
  leaving from anywhere but the middle 128 of an end wall is on foot. So a
  way out on foot must not be there (ajarmap.way_through says so).
- MAP10's line is the same room: its secret way out is still by a door.
- `MAP=MAP09 MODE=3`: `theHoleEndsNothing`, `backOnTheLine`, then out by
  VIOLET's end (18 checks). MAP09 mode 1: 36; MAP10 mode 3: 18, the secret
  way out. Not played by hand.

## Ambushes: no two alike (2026-11-17)

Vadim: every ambush was two imps and somebody, on the way back. MAP05 to
MAP10 are changed; MAP03 and MAP04, the first that have any, are left.

- `ajarmap.ambush(..., after=N)`: a wave that holds back N seconds after the
  thing is taken (AjarAmbush args[2]), for when the first looked like all.
- Some now come in the room with you, round the key, not on the way back.
- **MAP05**: key 1, demons in the signal box with you, then the bridge
  (revenant, imps) 4 s later; key 3, spectres for the demons, the
  chaingunner late.
- **MAP06**: key 1, lost souls round you, then the gallery behind 4 s later.
- **MAP07**: key 4, the clocks strike in turn: an imp, a sergeant at 2 s, a
  chaingunner at 4, a revenant at 6.
- **MAP08**: key 3, lost souls from under the linen, then the way back.
- **MAP09**: key 1, four lost souls round you on the roof, a cacodemon at
  4 s; key 2, three spectres among the coats, one in the door, then
  chaingunners in the canteen at 6 s; key 3, nothing until the stairs: a
  mancubus fills the passage at 3 s, demons come up behind at 6; key 4,
  revenants on the gallery across the hall, the hell knight below at 5 s.
- **MAP10**: GREEN, the revenant 5 s after the imps; key 1, spectres either
  side of you (an imp fewer in the square); key 2, demons in the depot's
  corner for the square's revenant.
- Every ambusher was seen to come in the game: the walkthroughs of MAP05 to
  MAP09 (8, 11, 7, 11, 16), and for MAP10 a new `MAP=MAP10 MODE=1`, which
  only hands over both keys (12). Thingcheck: 0 problems. How hard they
  are now is not tested: not played by hand.

## MAP31 "This Is Where We Came In" (2026-11-17)

The first secret level, from MAP10's secret way out. Built; its mechanic
and a walk through all three halls pass headless. **Not played by hand: no
fight has been fought, and the numbers of monsters and supplies are a first
guess.** `tools/map_secret1.py`; `MAP=MAP31 ./run.sh`. Its own way out starts
it again until there is a MAP11. No door to carry, no solver.

Vadim's brief (2026-11-17): the secret level uses "Step out of the fight"
(under "Time doors"); the Pair is kept for 11 to 20. Settled the same day:
- A cinema, as a building only. **The fights are not films**: the player
  really is back before the fight, and nothing is wound, sped up or tinted.
  The earlier self looks as the player does.
- The way out of a fight is a fixed door of the game's kind (a clock on it),
  not one that is carried: two or three round a hall. A carried time door
  can wait for 21 to 30.
- Each trip lands in a box of its own, behind glass, with its own supplies:
  the boxes are the limit (three to a hall), and no earlier self is ever met
  in the same room. The shared buffet was dropped for that reason.
- Watching runs at the fight's own speed. The price of the third trip is
  watching the whole fight so far.
- Three fights; a trip goes back to the beginning of the fight that is on.

**What the player sees.** Through a time door: the next box, and through
its glass this hall. Step through and it is before the fight: behind the
glass the hall is as it was, the earlier self comes in and fights, and the
earlier watchers stand in their boxes. Top of the screen: how far the fight
has got and when it was left. At that moment the earlier self goes into the
door, the box's door opens onto it, and the fight is real again whether the
player comes or not (monsters that have lost them wander). Back in the hall
the door shuts, and the hall's doors lead to the next box. After the last
box they are shut.
- Where you leave is where you return, with what was after you a step away.
- What was right behind you (within 150 of the door, after you, small enough
  for a door, two at most) comes out into the box with you, and is gone from
  the fight from then on.
- From a box the hall is seen from above: who comes in later and where, and
  the tops of the tall blocks (80 high). In the great hall one has an arrow
  on it, at a piece of the south wall that opens with USE: the secret (BFG).
- A room key lies at the far end of halls 2 and 3; cupboards in their first
  two boxes want it (rocket launcher; cells, soulsphere, armour). A box is
  visited once: no key, no cupboard.

**How it is made** (`src/zscript/time.zs`, `tools/ajartime.py`; the map
contract is at the top of time.zs). Nothing is rewound, as "No real rewind"
said, and no room is built twice:
- While a fight is on, every thing in its zones is recorded each tic it
  changes: place, angle, sprite, frame (`AjarTrack`).
- When the player leaves, the real things in the hall are stopped where
  they are (`tics` -1, no speed, held in place each tic) and hidden, and
  puppets (`AjarEcho`) play the record from its first tic. At the last tic
  the puppets stand where the real things do; they are removed and the real
  ones go on. So the past cannot be changed and there is nothing to merge.
- What happens in a box while it is watched from is recorded too, as that
  box's own track from tic 0, and played in later trips: hence the earlier
  watchers, and a monster that followed someone out.
- The doors are portal lines as a door's far side is (`AjarHandler.Link`):
  the hall's lead one way to the next box; after the replay the box's door
  and the door that was used are joined both ways.
- The glass stops walkers, shots and monsters' sight.
- Later monsters are `AjarCue` things in waves: a wave comes when no more
  than so many are left. The fight is won when no wave and no monster is
  left; then sector 3090 + 100 x fight opens (a steel door).
- **Everything that changes in a fight's zones must be a thing.** A door or
  lift that moved would not be played back. Hence a hall is entered by a
  step down (32) and its cupboards are things (`AjarLocker`). Known gaps:
  the secret wall in the great hall is a real door and is seen open in a
  replay from the start if it was opened; bullet marks on walls are there
  from the start of a replay; a replay has no sound (the glass).
- Monsters do not walk through an open time door by themselves (they know
  only the doors of `AjarSense`); shots do.

**The level.** A foyer (shotgun, chaingun) and three halls joined by fixed
doorways: 768 x 704 (10 monsters and 9 in two waves), 1024 x 896 (17 and 15
in two waves, an arch-vile in the second; the super shotgun before it),
1280 x 1024 (25 and 27 in three waves, a cyberdemon the last; the plasma
rifle before it). One secret. Plain walls: its look is still to come.

Tests: `MAP=TIME MODE=3 tools/smoke.sh` (the time box, `tools/map_time.py`:
14 checks, two trips, two earlier selves at once) and `MAP=MAP31 MODE=3
TIMEOUT=250 tools/smoke.sh` (21 checks: each hall begun, left, watched,
handed over, come back to, won; both cupboards), and `MAP=TIME MODE=4
TIMEOUT=60 tools/smoke.sh` (3 checks: a demon on the player's heels comes
out into the box and stays out of the fight). Not tested: a save and load
in the middle of a fight, dying in a box.

## Look: MAP31 (started 2026-11-17)

Board: not published yet (source `design/secret1-board.html`, images in
`build/board31/`: `<look>/view_NN.jpg`, `tex/` swatches, `sheet_<look>.jpg`
contact sheets). **Vadim has not chosen.** Look 1 is what the game wears
meanwhile, so that the level is dressed when it is played. Branch `look31`,
not merged. Not played by hand.

`AJAR_CINEMA` picks the cinema's look (`tools/gfx_cinema.py`, names
`AJY<part><look>`); unset is 1, and 0 is the plain level (whose map is byte
for byte what it was before the looks, checked). Three periods of one town
cinema:
1. **Palace** (1930s): halls in burgundy damask between fluted gilt
   pilasters with a gilt sunburst to a bay, walnut below, a carpet of gold
   scales, cream coffers with round lamps; the foyer cream over black marble
   on black and cream marble; curtains in the ways in; buttoned velvet in the
   boxes; the tall blocks are plinths of black marble; brass round the glass.
2. **Kino** (1960s): halls in white perforated panels over ash slats under a
   blue band, boards in red-brown floor paint, a flat white ceiling with
   square lamps; the foyer whitewash over small blue mosaic on terrazzo, a
   red runner with green edges; veneer in the ways in; pegboard over ash in
   the boxes; whitewash over green oil paint in the lobbies; the tall blocks
   are loudspeaker cabinets; white frames.
3. **Fleapit** (1980s, run down): halls in hessian gone orange over scuffed
   brown gloss with water marks, a swirl carpet with gum on it, stained
   ceiling tiles, strip lights; the foyer yellowed woodchip over
   wood-effect boards on lino squares, a rubber mat; three stripes in the
   ways in; cork tiles in the boxes; painted blockwork in the lobbies; the
   tall blocks are banks of orange plastic seats; brown frames, one pane
   cracked and taped.

The same in all three, drawn per look: the screen, which hangs over the way
into each hall (the north box is where a projection box would be) and is
blank, as the fights are not films; six posters in the foyer of the town's
other places as films (All Change, Small Hours, Lost Property, After Hours,
Putting You Through, Party Wall); the box office on the foyer's west wall,
shut; the street doors behind the start; HALL 1 over the way in and HALL 2,
HALL 3 over the arches in the lobbies; shelves of film cans in the closet;
the steel doors let into the wall of each side. The arches keep their stone,
the way out its sign.

How it is built (`map_secret1.py`): `dress()` gives a sector the look's
textures, `over()` carries a wall on over an opening. A look changes
textures, flats and the halls' light (180, 200, 176; it was 190). The foyer
becomes a `fitted` room with a runner, four lamps, a counter (40 high) and a
bench (16): the only new shapes, both outside every fight. **Nothing is
added to a hall or a box and nothing there moves.** The glass has a middle
texture on its box side (`GL`: a frame, clear inside it; the line's flags are
as they were) and its own trim (`ajartime.glass(trim=)`). The wall over a
time door and over and under the glass is the room's own. The piece of the
great hall's wall that opens wears the wall itself, as before. Hall
ceilings and look 3's carpet are 128-square flats. The capitals K, W and X
were added to the lettering.

Touched for every look and for the time box too (`gfx_time.py`): the
quarters and hours on the time door's clock, louvres on the cupboard. The
door's ivory, its trim and the arrow flat are as they were; in the looks the
arrow is on that look's block top (`BA`).

The tour (`SecretOneViews`, `MAP=MAP31 MODE=2`, `smoke_MAP31_2.cfg`) has 25
views: the foyer, each hall from its floor and from a box, a box, a time
door, two lobbies, the closet. `tools/board31_shots.sh` builds and shoots
all four (about 15 minutes), look 1 last, so the pk3 is left as the game is.
With monsters off the later waves still come (a hall that starts empty has
already let them in), so some pictures have monsters in them.

Provisional, all of it: what the tall blocks are, the blank screen, the
posters, the halls' light, whether the time door wants a darker surround in
look 2. Put to Vadim at the foot of the board, none built: seats, lights
down, a picture on the screen.

Found while shooting: the closet and the great hall's way in overlapped by
32 on the map. The arrow's block and the closet behind the wall it points at
are now 64 further west (the block at 384 to 448 of the hall).
