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

- **A harder start** (2026-11-20, Vadim: the start is "over simplified",
  meaning the fight). The lobby: two sergeants, two more imps and a demon
  (it had two zombies and an imp). The great hall: two demons at its mouth,
  a hell knight in the middle, two chaingunners under the porch at the
  back. Taking a Stray door (the lobby's is the first to hand) brings two
  imps and a spectre into the lobby and two sergeants to the hall's mouth.
  Shells, a shell box, a stimpack and a medikit for it. Not played by hand.

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

**Retired 2026-11-19 (Vadim): not useful after all, especially once there
are Pair doors.** Taken out of MAP09 and MAP10, the only levels that had
one, and out of the code: the `AjarRepainter` class, `AjarHandler.Repaint`,
the ambush cause 20 (`WorkNear`), the solver's `repainter=`, MAP09's test
modes 4 and 5, editor number 20007. What follows, and every later mention
of it in this plan, is history. Its look is still on
`design/map09-board.html`.

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
- PINK's room's frame took BLUE and VIOLET only at first. **It takes any door
  now** (Vadim, 2026-11-18, after playing: why not any door?). What was lost
  without the rule was one thing: RED, before key 1, brought there by a Stray
  door and hung. So no Stray door opens onto PINK's room (`StrayPool`, and
  the solver): a door comes there only through PINK, hung where the player
  can walk to, and can be fetched again. Only PINK itself is refused there
  (the room would open onto itself and, left by the hole, be shut for good).
  Solver: 0 stuck, nothing lost. AjarFrame `args[4]` = 2 only marks the frame.
- MAP08's brass frame, which still takes BLUE only (it keeps the shutter the
  only way in for BLUE), is marked: its brass is inlaid with blue enamel
  (`AJXA2`/`AJXF2`; `way_home(only=True)` picks the door's colour).
- **Leaving the line on foot frees the loop's doors** (Vadim, 2026-11-18): he
  built the plain loop, walked onto the line, left by the hole, and could not
  take BLUE or VIOLET down to build the secret one. They are nailed while he
  is on the line, and again each time he walks onto it.
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

### The first tests, run (2026-11-18)

Map ENG (`tools/map_eng.py`, `src/zscript/engtest.zs`; `MAP=ENG ./run.sh`,
`MAP=ENG MODE=1..5 tools/smoke.sh`): five bays off one corridor, portals
joined at load, no carried doors. Run headless only (docker, software GL);
**not played by hand, and no frame rate was measured.**

1. **A portal in a lift car: works.** The car, the recess and its stub share
   a tag and move by `FloorAndCeiling_RaiseByValue`. Walking through either
   way puts you on the floor of the far side wherever the car is (down, up,
   and half-way down while it moves); a fireball goes through the same way;
   the view is level from both sides during the ride; the same after the
   link is cut and made again with `Line_SetPortalTarget`. Not tried: a
   monster through it, a carried door hung in the car.
2. **A missile going round: works.** An imp's fireball, a plasma ball and a
   rocket each kept going round a corridor 544 long for as long as they were
   watched (10, 13 and 10 laps); a lap is the length over the speed (54 or
   55 tics for the fireball). A line with `missilecross` is set off every
   lap. `Door_Raise` on it does not hold a shutter up: a crossing while the
   shutter is still moving or waiting is ignored (the plasma ball raised it
   5 times in 13 laps), so the metronome needs a few lines of script.
3. **The inside-out room: works.** Four frames in a hall's four walls, each
   out of the same face of a booth 192 square (a recess and stub from each
   face do not fit in less). Walking out of each lands where it should,
   facing the same way; from the square the booth's faces show the hall and
   the square again beyond it.
4. **Mirrors: work**, with `Line_Mirror` on a one-sided wall: a mirror shows
   a portal and what is behind it, a portal shows a mirror, and a mirror
   facing a portal repeats. `+ONLYVISIBLEINMIRRORS` does what the lodger's
   eyes need: the thing is not drawn seen directly or through a plain door,
   and is drawn in a mirror, also in a mirror seen through a door.
5. **Slanted recesses: work.** A six-sided room, each wall onto the one
   opposite, is a honeycomb, and walking on through a wall is a straight
   line; joined to its neighbour instead, a wall turns you 60 degrees. A
   three-sided room with two doors a wall, each onto its neighbour round the
   corner, tiles into triangles. The corners are off the grid (coordinates
   to three decimals), which the engine takes; `udmf.py` does not split a
   slanting wall at such points, so the room's outline names every corner
   itself (`many_sided`). `ajarmap.recess` is still for straight walls.

### Where 11 to 20 stand (2026-11-18)

A summary made while Vadim tested MAP31; the details are in the sections it
names.

- **Decided**: the institute, 11 to 20 as it was left and 21 to 30 the
  reveal ("The place"). The Pair door goes into these levels ("The Pair
  door"). Not every idea on the lists has to be used (Vadim, 2026-11-18).
- **Built and ready**: the Pair (lab only: not tried with a thief, a nailer
  or a lodger, and the solver does not know it; open: whether a brass frame
  takes a leaf); the time door (MAP31); everything of 1 to 10 (Stray door,
  thief, lodger, nailer, repainter, the bus, the chain and its longer loop,
  the timed exit).
- **Designed, not built**: the Flip door ("Flip door"); One-way and Small
  doors (the type table); set-up-and-swap one step deeper ("Idea for later
  levels").
- **On the list, the engine allows them** ("The first tests, run"): the
  inside-out room, the pinwheel, honeycomb and triangle rooms, the round
  room, mirrors and things only a mirror shows, the moving room, the
  metronome (with a script for its shutter), sight lines, the bottle,
  conveyors, the canal lock, the train of rooms, the roundabout, the
  arrangement as the map, the relay run, the timetable. Still to test: the
  jigsaw wall (something wider than one door through two openings). The
  model room is the weakest and only a note.
- **From "Time doors", not used by MAP31**: two places at once (the earlier
  self holds the plate), the future as a warning, the future as a contract.

### MAP11 (2026-11-18, agreed in outline; built: see the first build, below)

Vadim: no heap of ideas; 11 brings in the Pair, beside plain coloured doors,
and lets the player get used to it before the puzzles begin.

Claude's outline, to argue over:
- **The place**: the way into the institute: the lobby, the pass office and
  its turnstile, the cloakroom, the first corridor of labs. Where MAP10's
  bus let the player off.
- **Three steps, each a thing to do and not a riddle.**
  1. Both leaves lean by two frames that face each other across the lobby.
     One hung: a shut door. Both: the endless corridor. Nothing depends on
     it; it shows what a Pair is.
  2. The rope. The turnstile lets you in and not out (MAP05's). Hang a leaf
     in the lobby, carry the twin through, hang it inside: the way back is
     open and stays.
  3. With a plain door. RED's far side is up on a gallery, as in the lab.
     Go up by RED with a leaf, hang it there, come down and hang its twin:
     the gallery is joined to the floor, and RED is free for the errand the
     way out needs.
- **The way out** is built by the player as since MAP05, with the plain
  door, so that the brass frame question can wait.
- **Company**: Doom's own monsters, few. No thief, nailer, lodger or
  repainter: none has been tried with a Pair, and the level is for learning
  one thing.
- **One secret**, found by a sight and not a puzzle: two frames side by side
  (the U-turn) or round a corner (the pinwheel) in the cloakroom.
- **Before it can be built**: the solver has to know Pairs (a second free
  end in the state), since every level is proved by it.

### MAP11 "By Appointment" (2026-11-18, built twice)

`tools/map_institute1.py`; `MAP=MAP11 ./run.sh`. Its look: see "Look:
MAP11". **Not played by hand.** The name is Claude's, to be changed freely.
MAP10's plain way out and MAP31's lead here; its own starts it again.

The first build was six rooms and six monsters. Vadim: far too simple for an
eleventh level; not more puzzle, more action. Rebuilt the same day at the
size of MAP08 to MAP10's fights, the puzzle kept light.

- **Places.** One place to walk about in: the lobby (start; both TEAL
  leaves, RED; two frames facing each other; the reception desk), the
  cloakroom (backpack, chaingun), the corridor north (a frame), the optics
  lab west (super shotgun; a frame) and the canteen east (GREEN, berserk).
  Over the canteen's north side the gallery (RED's far side, key 1, rocket
  launcher), with a balcony down the canteen's east side; from it a drop
  into the canteen and one into the archive. The archive (VIOLET; three
  frames; stacks) is entered from the corridor only by a hole for empty
  hands. The pump room (GREEN's far side, key 2, plasma rifle; dark) has a
  hatch out into the corridor, a hole too and a step too high to climb back:
  the way in is GREEN. At the corridor's end a door with locks 1 and 2 (no
  key needed from inside): the experiment hall, and beyond it the night
  room, whose brass frame takes VIOLET only.
- **The puzzle.** GREEN for key 2, RED for key 1, and VIOLET out of the
  archive in hand, which the hole will not have: a leaf in the hall, its
  twin up by RED and down the drop. 10 door actions that way. The turnstile
  of the outline is this hole (the game's turnstile is a squeeze, which a
  leaf does not pass either).
- **The Pair is the only way** (Vadim, 2026-11-19: otherwise the Pair is
  not needed in the level at all). The archive's three frames take any door
  but RED (`ajarmap.recess(only=4, home=RED)`, AjarFrame args[4] = 4; their
  trim carries a red plate struck through, `AJNO1`; "This frame is barred to
  the RED door. Any other will hang in it."). What it shuts was the solver's
  shortest, 8 actions: VIOLET hung in the archive, into the night room with
  RED, back through VIOLET with it, swap, and VIOLET out by RED over the
  gallery. Tried in the solver first: frames for VIOLET only (the plan's
  first thought) leave whoever drops in with GREEN stuck; frames for
  anything but VIOLET leave whoever takes VIOLET stuck. Without the leaves
  the level now has no solution.
- **The fights**: 86 monsters on "Resident" (47 on "Just visiting"), 15030
  health of them, ammunition worth 2.26 times that, 520 health, 300 armour.
  Lobby: zombies, sergeants behind the desk, imps. Corridor: imps, two
  chaingunners at its far end. Lab: demons, imps on the crates, a revenant.
  Canteen: imps, sergeants, two knights; an imp and a chaingunner over it on
  the gallery. Pump room: spectres and demons in the dark, a knight by the
  hatch. Archive: imps, knights, lost souls among the stacks. Experiment
  hall: two mancubi, three knights, revenants and imps on platforms, two
  cacodemons, a baron before the way to the night room.
- **Ambushes**, none like another: a leaf taken, sergeants behind you in the
  lobby and imps 3 s later; key 1, cacodemons up from the canteen, demons
  along the gallery at 3 s; key 2, revenants by the pump room's hatch, imps
  in the corridor at 3 s; VIOLET taken, spectres round you in the archive,
  revenants between the stacks at 4 s.
- **The secret**: the south end of the balcony (a soul sphere), seen from
  the canteen's floor, reached along the balcony from the gallery.

The solver knows Pairs (`solve.py`: a leaf is `dict(pair=its twin's key,
lean= or frame=)`, `ajarmap.leaves`): both hung, each frame leads to the
other; one alone leads nowhere. Two frames are there because of it: a fourth
in the hall (the lab) and a third in the archive, so that hands can always
be emptied (640 stuck states without them). Now 122867 states, 0 stuck,
nothing can be lost. Not in the solver: a Pair with a thief, a nailer, a
repainter or a Stray door.

`MAP=MAP11 tools/smoke.sh`: 18 checks (the first: RED is refused in the archive) (`ByAppointmentScript` in
`src/zscript/map11.zs`, the Pair's way), all pass, out by the way out; every
ambusher was seen to come but key 2's imps, which are due after the walk has
left. `mapcheck` and `thingcheck`: 0 problems. Not known: how hard any of
it is.

### MAP12 "Going Up" (2026-11-19, outline; not built)

Claude's proposal, to which Vadim said "let's go"; his answers to the three
questions at the end are still owed. The name is Claude's, to be changed
freely.

- **One idea: the moving room.** The goods wing: three floors round one
  lift shaft, the stairs sealed. Ground the loading hall, first the
  workshops, top the winding room with the way out.
- **Three steps, as in MAP11.**
  1. See it. A plain door has its far side in the car. Hung in the loading
     hall it opens onto the car; press the button and the same door opens
     onto another floor.
  2. Use it. The top landing has no working button and the car's own panel
     does not reach it: the car gets there only when sent from below. Send
     it, and go through the door.
  3. With the Pair. The car has a frame: a leaf there, its twin anywhere,
     and that place rides with the lift. That brings the way-out door down
     from the top.
- **The puzzle** about 10 to 12 door actions, the Pair needed this time
  (MAP11's shortest way does without it).
- **The fights** MAP11's size or a little over, 90 to 100 monsters on
  "Resident", one fight a floor, cacodemons and lost souls up the shaft, the
  big one in the winding room. **The ambush only this level can have**: the
  car arrives with monsters in it, and they come out of the hung door
  wherever it is.
- **Company**: Doom's monsters only. A thief, nailer or lodger with a Pair
  is still untried; one of them back in MAP13.
- **MAP13**, as proposed: the optics department (switches shot through a
  line of doors, monsters set on each other through them, mirrors).
- **Asked, not answered**: lift for 12 and optics for 13, or the other way
  round; whether the Pair is to be the only way in 12 (and MAP11's 8-action
  way round shut); whether MAP11's size is right (it has not been played).

### MAP12 "Going Up", built (2026-11-19)

`tools/map_institute2.py`, `src/zscript/map12.zs`; `MAP=MAP12 ./run.sh`,
`MAP=MAP12 MODE=1 EXTRA=-nomonsters tools/smoke.sh`. **Not played by hand.**
Vadim's answers: the lift for MAP12 and optics later; a bit larger than
MAP11. MAP11's way round the Pair was to stay (Vadim, 2026-11-19: "it's
ok"), and was shut the same day after he had played it: see MAP11. What differs from
the outline above is Claude's choice, to be changed freely.

- **The building.** Ground: the loading hall (start, RED, one frame). First
  floor, west of the shaft: the workshops (GREEN, a TEAL leaf; no frame). Top,
  north: the winding room (key 1; no frame), and behind locks 1 and 2 the
  night room, whose brass frame takes VIOLET only. Off the hall behind lock
  1, the store, sunk 64 (VIOLET; two frames): a drop in, a hole and steps
  out that no door fits. The battery room (key 2, plasma rifle) has no way
  in but GREEN. Gaps drop from the top to the workshops and from the
  workshops to the hall: the only way up is the lift.
- **The lift's rules.** The car's own panel is torn out. The hall and the
  workshops each have buttons 0 and 1. Only the dispatcher's booth has
  button 2, and the booth is walled up behind glass on the first floor: the
  other TEAL leaf hangs in its frame, which takes a TEAL leaf and nothing
  else (new: AjarFrame args[4] = 3, `recess(home=TEAL, only=3)`; without it
  the solver found VIOLET swapped into the booth and the top lost for good).
- **The puzzle**, 9 door actions, no stuck states, nothing losable: RED in
  the hall's frame, button 1, through RED (the first floor); the leaf in the
  car's frame (the booth opens onto the car), button 2 and back (the top,
  key 1); GREEN for key 2; RED taken down and hung in the store, VIOLET
  through it into the car, by the leaf to the booth, button 2, and back: the
  top with VIOLET. The Pair is needed, and so is the car's frame for the
  first trip to the top (the workshops have no frame for the leaf).
- **The fights**: 100 monsters on "Resident" (54 on "Just visiting"), 18400
  health of them (MAP11: 86 and 15030), ammunition worth 2.29 times that,
  595 health, 300 armour; every weapon up to the plasma rifle. Five
  ambushes; the one only this level can have comes with key 2: demons
  appear in the car, wherever it is, and come out by whatever door opens
  onto it.
- **Its look** is MAP11's Post Box, from MAP11's parts (the hall wears the
  experiment hall, the workshops the lab, the winding room the lobby with
  the machine for its engine). New: the lift's buttons (`tools/gfx_lift.py`,
  AJLB0..2 and the torn-out AJLBX). Nothing else was drawn for it: no look
  board, no secret, no tour of views yet.
- **MAP11 now leads to MAP12**, and MAP12 to MAP13.

### MAP13 (2026-11-19, Claude's outline; Vadim: "go with map13 as proposed"; built: see below)

Vadim asked for the planning to start once MAP12 was seen to be dressed
(it wears MAP11's Post Box). Everything below is Claude's proposal.

- **One idea: sight lines.** The optics department, as proposed with
  MAP12: what a hung door lets through besides the player. Shots and sight
  cross a door already; no level has asked for it yet.
- **The place**: the optics wing, on from MAP11's optics lab: the long
  range (a firing gallery for light, 1500 or so from end to end), the
  darkroom, the lens store, and two test cells behind armoured glass.
- **Three steps, each a thing to do, as in 11 and 12.**
  1. See it. A switch on a ledge nobody can reach, across a pit, and too
     far round a corner to be shot from the floor. A plain door's far side
     looks straight at it: hang the door anywhere and shoot the switch
     through it.
  2. Line two up. A switch that no far side looks at. A leaf hung in the
     cell that faces it, its twin where a plain door's far side looks at
     that leaf: the shot goes through two openings. Here the player picks
     the frames for the angle, and a wrong pair shows the wall beside it.
  3. Set them on each other. The two test cells hold what was being
     measured: barons in one, mancubi or cacodemons in the other, and the
     way on leads through both. A door in the frame of one and a leaf
     looking out of the other: they see each other and fight, and the
     player comes in after. Skipping it is allowed, and costs the whole
     fight.
- **The puzzle** about 10 door actions; the Pair needed (step 2). The way
  out by VIOLET into a night room, as in 11 and 12, unless it is time for
  another.
- **The fights** a little over MAP12: about 110 on "Resident". Snipers
  down the range (chaingunners, revenants) who shoot through whatever door
  faces them, so a door hung carelessly is a hole in the player's cover.
  Step 3's cells are the big fight, or what is left of it.
- **Mirrors: not here.** They work (the first tests, 4), and belong to the
  same department, but Vadim's rule for 11 was one idea a level. MAP14.
- **Company**: Doom's monsters only once more, since the level's own trick
  is making them fight; a thief or a lodger with a Pair is still untried
  and would want its test first.
- **Before it can be built** (a test box, as the lift had):
  1. A shoot switch set off through one door and through two (bullets,
     and a rocket or plasma ball).
  2. Two kinds of monster in sealed rooms joined only by a hung door: do
     they wake, aim and hit through it, and does the fight start with no
     help; the same through door and leaf together.
  3. The solver: a gate that opens once a switch has been shot, with the
     switch tied to the frames that give the line ("shot from region R
     while door D hangs in one of these frames").
- **Asked**: sight lines for 13 and mirrors for 14, or both in one; whether
  step 3 may be skipped or the cells are sealed until the monsters have
  thinned each other; the same way out again or something new; the name.

### MAP13 "Sight Unseen", built (2026-11-19)

`tools/map_institute3.py`, `src/zscript/map13.zs`, `src/zscript/optics.zs`;
`MAP=MAP13 ./run.sh`, `MAP=MAP13 MODE=1 EXTRA=-nomonsters tools/smoke.sh`
(25 checks, all pass, out by the way out). **Not played by hand.** The name
and everything that differs from the outline are Claude's, to be changed
freely. The four questions were answered by "as proposed": mirrors wait for
14, step 3 may be skipped, the same way out, Doom's monsters only.

- **What changed from the outline, and why.** Step 2 as written could not
  be forced: a leaf is hung where the player stands, so a switch that a
  line of two doors shows is also shown by one. So the shooter is fixed:
  **an emitter** at the west end of the range fires a beam east into RED's
  far side, and the beam comes out of whichever frame RED hangs in, square
  to it. The player aims it by choosing frames. Bullets do nothing to the
  sensor it is meant for.
- **Places.** The optics hall (start; GREEN, both TEAL leaves; frames 101
  west and 102 east, facing each other, 103 north, facing a wall). West,
  the darkroom: frame 104, which takes a TEAL leaf only, and across from it
  the sensor. North, behind a steel door, the range (1664 long; the
  emitter and its button; RED, BLUE; frame 105; a pit, and beyond it RED's
  far side and key 1, with a drop into the pit and steps out west). North
  of the range two test cells behind steel doors: GREEN's far side (2
  barons, 4 knights, key 2, a target on the far wall) and BLUE's (3
  mancubi, 2 cacodemons; beyond it the lens store, VIOLET, the plasma
  rifle). A grille stands before both far sides: shots and sight, no
  walking, either way. Off the hall behind locks 1 and 2 the night room,
  brass frame for VIOLET only.
- **The puzzle**, 10 door actions, 41675 states, 0 stuck, nothing losable:
  GREEN hung in the hall and the target shot through it (the range opens);
  RED in 101 or 102, a leaf in the frame facing it, its twin in 104, the
  emitter (the cells open); key 1 by RED, key 2 and VIOLET from the cells.
  The Pair is needed: 104 takes nothing else, and without that RED hung in
  104 put the beam on the sensor by itself. Frame 105 is there because
  five doors and three hall frames left hands that could not be emptied
  (2880 stuck states without it).
- **Step 3, not needed**: GREEN and BLUE in 101 and 102 before the cells
  are opened, and what lives in them fights through the two doors.
- **The fights**: 106 monsters on "Resident" (57 on "Just visiting"), 21260
  health of them, ammunition worth 2.34 times that, 645 health, 300
  armour, every weapon up to the plasma rifle. Six ambushes (GREEN, a
  leaf, RED, key 1, key 2, VIOLET). Chaingunners and imps beyond the pit
  fire through RED at whoever stands before its frame.
- **Its look** is MAP11's Post Box from MAP11's parts (hall: the lab;
  darkroom: the pump room; range: the experiment hall; cells: the
  cloakroom; store: the archive). **Nothing was drawn for it**: the
  emitter is a button with the way out's sign and no lamp to see, the
  targets are two plain discs (`AJTG`), the grille is the night room's. No
  secret, no tour of views, no look board.
- **MAP12 leads to MAP13**, and MAP13 to MAP14.
- Since then (2026-11-19, after Vadim played it): the emitter's button has
  a plate of its own (`AJLBF`, a lamp and its beam, on the lift buttons'
  trunking) in place of the way out's sign.
- Not known: how hard it is; whether the beam's line reads without a lamp
  to see; whether monsters walking to their posts look right.

### Nothing to pick up out of reach (2026-11-19)

Vadim found MAP12's backpack on a 96-high block: nothing gets up there
(no jumping, a step is 24 at most). His rule: **there are no items the
player cannot take.** `tools/itemcheck.py map_... ` walks each level from
the start, from every frame, far side and room door and from every tagged
sector, up 24 and down any drop, and reports a pickup in a sector never
walked into. One on furniture counts as within reach only if it is no more
than 48 up and less than 20 in from an edge the player can stand at (their
middle stays 16 short of the step, and they touch what is within 36). It is
not part of `build.sh`; run it with mapcheck and thingcheck on a new level.

It found 14, all moved: MAP07 two boxes of shells in the middle of the
shed's tables; MAP11 the super shotgun on a 64 crate; MAP12 **key 1** on the
winding room's far platform (the level could not be finished), a soul
sphere, rockets and cells on another, the super shotgun on a 64 bench, the
berserk 20 in on a bench, the backpack (now on the low crate under the gap
from the workshops, where Vadim stood); MAP13 the chaingun on a 96 bench,
rockets on a 64 crate, the rocket launcher and the backpack in the middle
of 48 furniture. Things on platforms went to the floor at their foot;
steps up to the platforms would be the other way. Also MAP13: two imps in
the darkroom stood in each other.

### MAP14 "On the Level" (2026-11-19; Vadim's idea, built the same day)

`tools/map_institute4.py`, `src/zscript/map14.zs`; `MAP=MAP14 ./run.sh`,
`MAP=MAP14 MODE=1 EXTRA=-nomonsters tools/smoke.sh "$PWD/build/smoke14"`
(34 checks, all pass, out by the loop). **Not played by hand.** The idea
is Vadim's: "combine the lift with a frame and the two-door exit: set the
proper door in the lift and on one of the floors where it is properly
aligned; then you need to send the lift to the proper floor and it will
build the exit way". The name, the building and the puzzle are Claude's, to
be changed freely. Mirrors, which the MAP13 outline kept for 14, wait again.

- **One idea: the way out is a chain with one end in the lift.** MAP09's
  chain (`way_through`: two brass frames, two doors whose far sides are
  the two ends of the line), but one brass frame is in the car's east wall
  and the other in the west wall of the first floor, across the room and
  the landing from it. They face each other only while the car stands at
  the first floor, and only then is the loop closed.
- **The rule** (`AjarHandler.BrassLevel`, in `LoopLen`): with a brass frame
  in a lift sector, the loop needs the car standing still with its floor
  at the other frame's. Nothing is fixed by it, as in MAP09: send the car
  away and the loop is open again, and the two doors are then a way between
  that floor and the car, wherever it is, by the line. Walking onto the line
  through the closed loop makes its doors stay, as before. (Claude had
  proposed that it stay built once it had lined up; this follows the
  chain's own rule of 2026-11-17 instead. To be argued.) What is said:
  hanging the second door with the car elsewhere, "they do not face each
  other: the lift is at another floor"; the car arriving, "the lift stops
  level with the other brass frame"; the car leaving, that they no longer
  face each other.
- **Found on the way**: the engine pushes a frame that rides in a car down
  under the ceiling its recess had when the level began, each tic, and
  `LiftTick` puts it back later in the same tic. So the two frames are
  compared by their sectors' floors, not their own heights.
- **The building**, the staff wing, three floors round one lift, no stairs.
  Ground: the canteen (start; RED; frame 101) and its kitchen (the super
  shotgun). First, west of the shaft: accounts (GREEN; the brass frame;
  nothing stands between it and the landing), and behind lock 1 the
  cashier's office (BLUE, the rocket launcher). Top, north: the director's
  floor (key 1), and behind lock 2 the safe room (VIOLET). The cold store
  (GREEN's far side; key 2, the plasma rifle) has no way in but GREEN. The
  line is MAP09's night room. Gaps drop from the top to accounts and from
  accounts to the canteen.
- **The buttons are the puzzle.** The car's own panel is torn out. The
  canteen sends it to the ground and to the top; the top sends it to the
  first floor; accounts has no button. So the car comes level with the
  brass frame only when sent from the top, and whoever sent it gets down
  by the gap. RED's far side is in the car, as in MAP12.
- **The puzzle**, 8 door actions, 1427 states, 0 stuck, nothing losable
  (`home_chain=dict(..., level=1)` in the solver: the loop counts only with
  the lift at that floor): RED in 101, the car to the top, through RED (key
  1); the car to the first floor and down the gap; GREEN in the brass frame
  there, which is a frame like any other (key 2); down to the canteen, the
  car to the top, VIOLET out of the safe room into the car's brass frame;
  the car to the first floor, the gap, BLUE out of the cashier's office
  swapped in for GREEN. Shorter than 11 to 13 (10, 9, 10): to be made
  longer if it plays too easy.
- **The fights**: 109 monsters on "Resident" (58 on "Just visiting"),
  22790 health of them, every weapon up to the plasma rifle, a backpack on
  a canteen table. Six ambushes (RED, key 1, GREEN, key 2, VIOLET, BLUE);
  BLUE's puts demons in the car, and they come out of whatever opens onto
  it. A player dropping from the top lands on or by a desk.
- **Its look** is MAP11's Post Box from MAP11's parts (canteen: the
  experiment hall; kitchen: the archive; accounts: the lab; cashier: the
  cloakroom; cold store: the pump room; the top: the lobby; safe room: the
  lift's steel). The buttons are MAP12's. Its own props and pictures came
  the same day: see "MAP13 and MAP14: props and pictures of their own". No
  floor indicator, no secret, no look board.
- **MAP13 leads to MAP14**; MAP14's way out starts it again until there is
  a MAP15.
- Not known: whether the two frames read as a pair across 770 units of
  office; whether "sent from the top, met by the gap" is found or stumbled
  on; how the closed loop looks from inside the car; a monster standing in
  the landing when the car is sent holds it, and with it the way out.

### MAP13 and MAP14: props and pictures of their own (2026-11-19)

Vadim: "rework decoration for 13 and 14 a bit"; asked how far, "props and
pictures only", and "they look ok. Just to introduce something new, not make
them all absolutely the same". So walls, floors and ceilings stay MAP11's
Post Box, and each level gets things of its own: `tools/gfx_institute2.py`
(names `AJI<part><look>` as before, drawn in all three looks; a contact
sheet: `python3 tools/gfx_institute2.py <dir>`). All Claude's invention.

- **MAP13**: optical benches in the hall and the range (a slab on a steel
  frame, a rail with lenses in their holders, `OS`/`OT`); a chart of how the
  beam goes, in at a door and out of its frame (`RD`, in place of one of the
  hall's two lens cabinets); in the darkroom a safelight and prints pegged
  on a line (`SL`, in place of the gauges); the range's marks 100, 200, 400
  stencilled along its south wall (`R1..R3`); racks of lenses in the lens
  store (`LS`). **The emitter can be seen**: a lamp on a stand (`AJEMA0`;
  `AjarEmitter` is no longer invisible, in the test map OPT too).
- **MAP14**: the canteen's tables are MAP11's (`TS`/`TT`, 32 high, oilcloth)
  and its east wall has the kitchen's hatch, shut, and a menu (`HT`); the
  kitchen has a range 48 high where a stack stood to the ceiling (`RS`/`RT`)
  and pans on a rail (`PN`); accounts has MAP11's desks, 40 high, with a
  ledger and an adding machine on top (`AT`), the plan and how it was met
  (`PF`: in look 3 the line turns down and stops) and filing cabinets
  (`FG`); the cashier's office has the window, CLOSED (`CW`); the safe room
  the safe's door (`SF`); the director's floor MAP11's desk and counters, a
  bookcase (`BC`) and the pale square where a portrait hung (`PR`).
- **Tours**: `MAP=MAP13 MODE=2` (7 views) and `MAP=MAP14 MODE=2` (15),
  `SightUnseenViews` and `OnTheLevelViews`. Seen in look 3 only, headless.
- Not done: a look board; anything for the cold store, the cells or the
  lift car; the darkroom's lamp is a picture and lights nothing.

### MAP13: monsters that could not move (2026-11-19)

Vadim, playing: "some monsters appear in stale positions, where they
cannot move". Four ambush spots overlapped furniture (a sergeant's and two
demons' in the hall, a knight's in the range: the checks took an ambusher
for a thing of radius 16), so those came in wedged into a bench or crate.
Moved clear. Three sergeants placed on benches and a crate could not come
down either (a monster does not step off more than 24) and now stand
beside them; MAP14's four on tables and desks likewise. **MAP11 and MAP12
still have monsters placed on crates and platforms on purpose** (snipers);
to be taken down too if Vadim reads them as stuck. No other level had an
ambush spot in furniture.

### Two sessions, one checkout (2026-11-19)

Several sessions were building in this checkout at once and wrote over each
other's `build/ajar.pk3` (seen as "ZIP file corrupt", and as Doom's own
MAP13). `AJAR_OUT=build/mine.pk3 ./build.sh` builds to another file and
`PK3=build/mine.pk3 tools/smoke.sh` tests it.

### MAP13 made harder, MAP14 given a boss (2026-11-19, branch `map13-harder`)

Vadim, having played both: in MAP13 "the main puzzle is the beam; the exit
door itself is very easy, and the blue door is not needed at all. Maybe we
could make it more challenging too"; "the backpack in both 13 and 14 is too
easy to obtain"; in MAP14, on the director's floor once VIOLET is taken,
"more enemies and the main boss, as an ambush" and "a couple of
arch-viles", one arch-vile in the safe room, and for the PLAN chart
"something scientifically more interesting". What was built is Claude's.

- **MAP13: BLUE is needed.** The lens store (VIOLET) has a steel door, and
  its sensor is on the east wall of BLUE's cell in line with BLUE's far
  side: BLUE goes where the leaf hung and the emitter is fired again.
- **MAP13: the way out is a step more.** Past locks 1 and 2 there is a
  steel door; its target is in the night room beside the brass frame and
  is shot through VIOLET hung in the hall, which then comes down again to
  be carried in. 15 door actions (were 10), no stuck states, nothing
  losable; the walkthrough has 44 checks.
- **Backpacks**: MAP13's beyond the pit (by RED only), MAP14's in the cold
  store (by GREEN only).
- **MAP14**: VIOLET taken brings three revenants, then the cyberdemon (on
  every difficulty) and three cacodemons, then two mancubi and three
  knights, then two arch-viles; an arch-vile stands in the safe room; cells
  and rockets added there and on the floor (ammo x1.97 on Resident before
  the last of it). Ambushes can bring a cyberdemon (16).
- **MAP14's chart** `PF` is THROAT: two funnels joined at the neck, R0, the
  path through; in look 3 the neck is ringed in red and the path stops.
- Not played by hand; the boss fight's balance is a guess.


`tools/map_optics.py`, `src/zscript/optics.zs`; `MAP=OPT ./run.sh`,
`MAP=OPT MODE=1..3 tools/smoke.sh`. Run headless only.

- **A bullet through a door hits what is there** (the engine's doing).
  `ajarmap.target(m, x, y, tag)` is a thing to shoot (`AjarTarget`, 20060)
  that opens every `ajarmap.steel(..., tag)` door; with `beam=True` it is a
  sensor and only a beam sets it off.
- **The emitter** (`ajarmap.emitter`, `AjarEmitter`, 20061): its button
  fires an `AjarBeam`, a missile (speed 25, it hurts what it hits). Through
  RED in the frame facing a wall: nothing. Through RED in 101, across the
  hall into a leaf in 102 and out of its twin: on the sensor (MODE=1).
- **Monsters do not see or aim through a door** (the engine's sight stops
  at one; `AjarSense` only makes them follow). `ajarmap.watch(m, box,
  colour)` marks a room that is a door's far side (`AjarWatch`, 20062), and
  `OpticsTick` does it for those in it: while that door hangs they fire at
  the player before its frame, or, where its frame faces the frame of
  another watched room's door, at what is in that room. A monster fires
  its own attack at an `AjarAim` put where the victim would be if the door
  were a hole in the wall (`PortalMap`, `AimThrough`: the straight line has
  to pass each opening, with sight on each stretch). It only has that line
  from where door and victim are in one line, so it walks there first
  (`TakePost`, as to a patrol point). Not revenants (a homing missile turns
  back), arch-viles, pain elementals or lost souls.
  MODE=2: a baron behind GREEN hit the standing player three times in 15
  seconds. MODE=3: a baron and a mancubus, GREEN in 101 and BLUE in 102,
  hurt each other (4 volleys in 20 seconds: slow; in MAP13 there are 6 and
  5 of them).
- Found on the way: the engine all but hides an invisible thing from
  `CheckSight` (it wants `SF_IGNOREVISIBILITY`).
- **The solver** (`solve.py`): `sights={key: ...}`, a target shot through a
  door or an emitter's button with the arrangements that put its beam on
  the sensor, each giving a key that steel doors need; `barred=True` on a
  door that is never walked through.

### The lift, built and tested (2026-11-19)

`tools/map_lift.py`, `src/zscript/lift.zs`; `MAP=LIFT ./run.sh`,
`MAP=LIFT MODE=1 tools/smoke.sh` (the doors), `MODE=2` (company). On the
branch `map12` (worktree `../ajar-map12`). Run headless only: **not played
by hand.**

- **How it is made.** The car is every sector with tag 700
  (`ajarmap.LIFT`): the car itself and the door recesses in its walls
  (`ajarmap.recess(tag=)`), moved together by
  `FloorAndCeiling_RaiseByValue`, 4 units a tic. A landing is a sector
  beside the car with its floor at a stop's height and a low lintel: at any
  other stop it is a wall, with no script. `ajarmap.lift_button(m, a, b, z,
  tid, at)` is a button that sends the car to height z (an `AjarLiftButton`
  thing, 20050; `AjarHandler.LiftSend`). A press while it moves is refused
  ("The lift is on its way."). Frames and doors have no gravity and are
  kept on the car's floor by `LiftTick`.
- **The test map**: a hall, a first floor 192 up and a top 384 up round one
  car. In the car frame 110, RED's far side and both ORANGE leaves; RED and
  both TEAL leaves in the hall. Buttons: in the car for the ground and the
  first floor; in the hall to call it and to send it to the top; on the
  first floor to call it; none at the top, where the way out is.
- **The solver** (`solve.py`, `lift=`): the car's floor is in the state.
  The car is a region joined on foot to the landing it stands at; sending
  it costs nothing; a door rides in it. The test map's proof: 2 door
  actions (send the lift to the top, take RED, hang it, through it, out),
  12067 states, 0 stuck, nothing lost.
- **The four tests.**
  1. A monster through the car's door: works both ways. A demon in the
     hall came up through RED to the player in the car at the top; a demon
     in the car at the top came down through RED to the player in the hall
     (the door sense of 1 to 10, unchanged). A zombie in the car rides.
  2. A carried door hung in the car: works. The frame, a leaf hung alone, a
     leaf hung open and leaning leaves all ride; with the twin on the first
     floor, that frame leads to the car wherever it is, and stepping
     through while the car is on its way down lands in the car; taken down
     and hung again at the top, it stands on the car's floor.
  3. What is in the car's way. Nothing can be under the car: with the car
     elsewhere its opening is a wall. What stands in the opening when the
     car is sent holds it (the player at the top: the car stopped 72 down,
     its ceiling on their head, and went on when they left). A body holds
     nothing and stays on the landing. Not seen: a live monster standing
     there (the test's demon would not stand still: it walked into the
     car); the engine makes no difference between it and the player.
  4. The solver: above.
- **Not done**: a look for the car and its buttons (the button is the way
  out's sign for now); a sound while it moves; anything on the HUD; a
  thief, nailer, lodger or Stray door with a lift (the solver's
  thief does not ride or press); more than one lift in a level (the tag is
  an argument everywhere but in the test's script).

### MAP15 and MAP16 (2026-11-19, agreed in outline)

Vadim chose from five proposals: **mirrors for 15, the thief with a Pair
leaf for 16**; the other three are kept for the rounds after (below).
Everything not marked as his is Claude's proposal. (This section and the
two after it were written, lost when the file was put back to the last
commit by another session, and written again the same evening.)

- **MAP15: mirrors, the optics wing's other half.** As outlined: things
  seen only in the glass; the emitter's beam aimed by door and mirror; a
  fight with monsters only the mirrors show. Built: see below.
- **Size** (Vadim): considerably bigger than MAP13 (he had not seen 14).
- **A secret way out** (Vadim: yes), and **the secret** (Vadim, from four
  proposals: "let's try"): a door only the glass shows. It leans in a room
  that looks empty; the mirror shows it; the player walks to where the
  reflection says it is and takes it by feel, and its far side is the
  secret way out. The other three, not used: a mirror that is not one (a
  leaf onto a room built as the mirror image: you are not in it); a target
  hit only by the beam off a mirror the puzzle never uses; a switch that is
  only in the third copy of a room between a leaf and a mirror.
- **MAP16: company comes back.** A thief that takes a Pair leaf shuts the
  link from anywhere; the level is about guarding the rope the player has
  paid out. To test first: thief and nailer with a Pair; the solver's thief
  with a lift, and with Pairs at all.

**Secret levels** (Vadim, 2026-11-19): secret ways out in 15, 20 and 30 as
well as MAP10's. Four secret levels are possible: GZDoom's `secretnext`
names any map, and nothing limits their number. Not decided: where a
secret level reached from MAP30, the last, leads back to.

**Kept for later rounds** (Vadim: all three sound interesting):
- **Conveyors, the goods dispatch.** A belt that ends at a frame delivers
  what it carries to that door's far side: a weight onto a plate, barrels
  into a sealed cell, monsters to the player. With a Pair both ends are the
  player's. To test: a scrolled thing crossing a hung door.
- **Timetable and relay run, the clock room.** Frames behind shutters that
  open by the clock; lay the track of doors, pull the lever, run it. The
  metronome (a fireball lapping a loop the player builds) as the clock. The
  solver needs time in its state: the heaviest. Claude: 17 or so.
- **The inside-out room and the honeycomb, the geometry department.** The
  strongest to look at, the thinnest puzzle ("the arrangement is the map").

### MAP16, 17, 18 and MAP20's secret: the second round (2026-11-19, evening)

Vadim and Claude, before MAP16 is begun. **Nothing here is built or tested.**
Decided by Vadim: MAP16 stays what was agreed above (the thief with a Pair
leaf, the rope guarded); the endless stair goes into it if a good use is
found; the proposal for 17 and 18 and the secret for MAP20 are written down
to come back to. Everything else is Claude's proposal.

**The endless stair** (Vadim: "I like endless stair actually"). A Pair from
the foot of a stair to its head: the stair only goes down and never ends.
Doors hang in walls, so this is a stair or a run of drops that is walked,
with a door at the foot; nothing falls freely through it (that would be the
Tilted door, not built). Uses, Claude's, strongest first:
- **The way up is down.** A stairwell whose flights are gone: each is a drop
  too high to climb, with the floors off the landings. One leaf at the foot
  and one at the head, and every floor is reached by going down. This Pair
  is the rope of the agreed level: the thief that takes a leaf leaves the
  player at the bottom of a well. Proposed as MAP16's spine.
- **What follows you comes from above.** Monsters that chase go round too:
  wait on a landing and they arrive one at a time down the flight above.
  A rocket fired down the well comes out at the top: something above the
  player is shot by aiming down.
- **The thief in the well.** A thief that runs down the stair with a door
  passes the same landing every lap. To check: how the thief chooses where
  to run, and that it will take a door through a Pair at all.
- Not proposed: a stair that is different each lap (a counter in a script,
  a new rule and not a situation).

**Other paradoxes listed the same evening**, not placed in any level:
- Round the pillar: a stub of wall from a pillar to the room's edge, a frame
  in each face. Clockwise you meet one door, anticlockwise the other: one
  corner leads to two rooms.
- A corridor of chosen length: two Pair leaves in a long corridor cut its
  middle out or close it on itself. For a timed shutter, a charging monster,
  a rocket to outrun.
- The room that is its own neighbour: a Pair east to west and a plain door
  north onto its own far side south. Shots come back, theirs as well.

**MAP17 and MAP18: a kit of rooms and orders to fill** (Vadim's idea: from a
set of places already joined by doorways, lifts, halls and fixed portals,
the player makes maps of their own with the coloured doors and the Pairs,
and different combinations give different geometries; Claude's development
of it). It gives the geometry department, "the thinnest puzzle" above, its
puzzle.
- The difficulty: if only what can be reached counts, building a geometry is
  routing again. So the shape has to be measured by something in the game:

  | Property of the shape | What reads it |
  |---|---|
  | Straightness | the emitter's beam, shots, what monsters see |
  | Length of a loop | a fireball's lap, the metronome's beat |
  | Direction | drops, teleporters and belts: a circuit one way round |
  | Order of rooms | a crate on a belt passes the stations in the order hung |
  | Height | the frame in the lift car, drops |

- **The kit**: six to eight modules, each with one fixed feature (a stair, a
  lift, a belt, a window, a teleporter) and two or three frames or far
  sides.
- **The orders**: three or four briefs that each ask for a shape and not for
  a place: a loop the fireball laps in a given time, a straight line from
  emitter to sensor, a circuit that runs one way, a crate through the press
  before the kiln. Each has several answers; no one arrangement fills two,
  so the player builds again.
- **The plan table**: a board in the hub with a lamp for each frame, showing
  what leads where now. Without it the limit is the player's memory.
- **The fight**: the arena is what was built before the lever was pulled (a
  killing loop, a bottle, the room that is its own neighbour).
- Two levels, split not decided. Claude: 17 the kit with the orders that
  need no clock (beam, one-way circuit, order of rooms); 18 the ones that
  do (the metronome, the relay run), since the solver needs time in its
  state for them. The conveyor and timetable ideas kept above fold into
  these as features of modules.
- To test first: a scrolled thing crossing a hung door; the script that lets
  the metronome hold a shutter; the solver with Pairs.

**MAP20's secret way out: the left-handed copy** (Vadim: for MAP20's secret
exit; it is the first of the three secrets not used in MAP15, "a mirror
that is not one"). A room has a wall of glass that shows the room
reflected, as MAP15's mirrors do, among real mirrors. One pane is not a
mirror: it is an opening, hung or fixed, onto a room built as the mirror
image of this one. The tell is that the player is not in it, nor their
shots. Walk into the glass and you are in the copy, where one thing is not
as it was on the right-handed side: the secret way out.
- How Claude would make it: the generator builds the room a second time
  reflected in the plane of the wall, so a plain opening onto it looks like
  a mirror with no trick of the engine. Only things that stand still may be
  in view (props are made twice; a monster would be missing from the
  glass, which could be a second tell or a fault).
- Open: whether the pane is a carried door (a leaf hung in a frame among
  the mirrors) or fixed; what the level's own idea is (MAP20 is not
  outlined).

### Company with a Pair, tested (2026-11-19, before MAP16)

The tests MAP16 was waiting for, in the lab: `MAP=LAB MODE=2 tools/smoke.sh`
(`LabThiefScript`, 9 checks) and `MODE=3` (`LabNailerScript`, 8 checks). All
pass, headless in docker; **not played by hand**. `PairOk` is checked every
tic of both: both leaves hung, each leads to the other's frame and both
frames are open; otherwise neither leads anywhere and a hung leaf is a wall.
- **Thief.** It takes a hung leaf while watched: the link is cut and both
  frames are walls. It hangs the leaf in another frame and the link is made
  again from there. It walks through a Pair with both leaves hung and comes
  out at the twin (hall to gallery).
- **Fixed** (found by reading, `enemies.zs`): a leaf hung alone counted as a
  door to walk through, and the thief would have walked at a wall until its
  patience ran out. A shut leaf is no way now, and a way stops being one
  when the twin is taken mid-walk. Not run without the fix.
- **Nailer.** It nails a hung leaf: that leaf cannot be taken, by the player
  or (by the thief's own rule for nailed doors) a thief. Its twin can be:
  the nailed leaf is then a shut door, still nailed, and leads to wherever
  the twin is hung next. So a nailer holds one end of the rope fast: it can
  be the player's friend. Not drawn: nails on a leaf that is shut (a shut
  leaf is a texture on its line, the nailed look is a sprite).
- **Solver.** A thief, a Pair and a lift together run (a made-up well of
  three floors, not kept). Its thief still stays in one zone: one that
  walks through doors is not modelled, as before. What the well shows: a
  drop taken with the rope not paid out is the end, so a level of drops
  needs a fixed slow way back, or the solver calls nearly every state stuck.
- Not tried: a lodger and a Pair beyond what MAP15 does (it takes a leaf
  for a plug); a thief in a lift car.

### MAP16 "Watch Your Step", built (2026-11-19)

Vadim: "Yes go and build", to the outline of the stairwell with the thief
and the nailer. `tools/map_institute6.py`, `src/zscript/map16.zs`; on the
branch `map16` (worktree `../ajar-map16`). **Not played by hand**; how hard
it is, is not known. It wears MAP11's look and has no props of its own.

- **The well.** Four landings round a solid shaft, each 128 below the last
  (top 384, second 256, first 128, the foot 0); the foot lies under the
  head, a cliff of three floors. A room off each: the reading room (the
  start), the labs, the canteen; the foot is open to the boiler room, with
  the stores beyond.
- **The endless stair, and what was changed from the outline.** The head's
  TEAL leaf is part of the building (a door thing with `args[3]`, as a
  fixed doorway has: nobody takes it, it has no leaf to show, and alone it
  is a shut door). The player has the other leaf only. Reason: with both
  leaves free, both can be carried down the drops, and then no door ever
  comes up again; the solver called most of such a well stuck. Fixed at
  the head, the leaf is always worth hanging wherever it is. In the PUZZLE
  graph it is a plain door whose far side is the top.
- **Nobody is left at the bottom.** A hole in the boiler room (empty hands)
  leads to a cubby with a doorway of the building's up to the reading
  room. No door goes up that way. The cubby is the secret (blue armour).
- **The puzzle.** VIOLET leans in the stores and belongs in the brass frame
  of the night room at the top, behind locks 1 and 2: it comes up by the
  stair or not at all. RED (the canteen) opens onto the strongroom, key 1;
  GREEN (the labs) onto the cold store, key 2. Frames: 103 top, 102
  second, 101 first, 104 the foot, 105 the stores. Solver: 8 door actions,
  104358 states, none stuck, nothing can be lost for good.
- **The thief** stays at the base and starts in sight of the foot's frame.
  It has nothing to carry off down there but what the player brings: RED
  was in the boiler room in the first build, and the thief picked it up,
  ran into the stores and stood behind the shelves for good, since it only
  goes for what it can see and walk straight to. In the graph it sees the
  player on every landing (the well is open).
- **The nailer** comes to the foot when VIOLET is first taken (the level's
  first ambusher, so there on every difficulty; `AmbushClass` knows 20004
  now). It nails the leaf at the foot, and a thief leaves a nailed leaf
  alone: the player's friend until they kill it.
- **Dropped from the outline**: the ORANGE Pair (six doors made the search
  too big), the second thief (the solver knows one), and the goods lift
  (the hole and the cubby do its work, and a lift that carries doors would
  have made the stair unnecessary).
- 103 monsters on "Resident" (55 on "Just visiting"), ammunition 1.5 times
  their health (`budget.py`). `mapcheck`, `thingcheck`, `itemcheck`: 0
  problems.
- Tests, headless: `MAP=MAP16 tools/smoke.sh`, the walkthrough, 19 checks
  to the way out; `MODE=2` with `EXTRA=-nomonsters`, a tour of 13 views;
  `MODE=3`, the company where it lives, 5 checks: the level's thief has
  the leaf out of the foot's frame and stays at the base, the nailer nails
  it, a second thief leaves it alone.
- MAP15 and MAP32 lead on to it; its own way out starts it again until
  there is a MAP17.
- Not done: monsters that chase do not come down the drops (Doom's do not
  step off a high ledge), so "what follows you comes from above" is only
  the cacodemons that rise up the well when the leaf is taken. No nails
  are drawn on the fixed head. No look board.

### Mirrors, built and tested (2026-11-19)

`tools/map_mirror.py`, `src/zscript/mirror.zs`; `MAP=MIR ./run.sh`,
`MAP=MIR MODE=1..3 tools/smoke.sh`. Run headless only; **not played by
hand.** Three rooms with no way between them.

- **Nothing comes back off a mirror by itself**: not a bullet, not a
  plasma ball. A mirror is a wall to every shot.
- **The beam does, by script** (`AjarBeam.A_Glance`, `optics.zs`): a beam
  that strikes a `Line_Mirror` wall goes on from it at the mirrored angle,
  from the very point its middle was flying at, a new beam with the same
  sender. MODE=1: fired at a mirror at 153 degrees it lands on a sensor on
  the wall opposite. The player's own shots are not turned.
- **The door only the glass shows** (`ajarmap.door(..., unseen=True)`, the
  door thing's `args[3]` = 2): leaning, it is drawn in mirrors only and has
  no glow; USE where it stands takes it ("Your hands find the GREEN door
  that only the glass showed."), and from then on it is a door like any
  other. Taken by a script call in the test, not by a key press. Open:
  whether it should keep a faint glow as a hint.
- **A monster only the glass shows** (`AjarUnseenImp`, 20092): drawn in the
  mirror only, blocks the player, is hit by a bullet, hurts the player. Its
  fireballs are drawn as usual.
- **The lodger and a Pair**: MODE=3: a leaf hung alone plugs its frame, and
  so do both leaves joined (500 tics each, the lodger stayed in). "A lodger
  comes out of either end" (the Pair's notes) is not built.
- A mirror has no frame or look of its own: on a wall it reads as an
  opening onto another room until something is seen to be doubled.

### MAP15 "On Reflection", built (2026-11-19)

`tools/map_institute5.py`, `src/zscript/map15.zs`; `MAP=MAP15 ./run.sh`,
`MAP=MAP15 MODE=1 tools/smoke.sh` (26 checks, all pass, out by the way
out; the secret door and its room on the way), `MODE=2` the tour of its
mirrors. Vadim: "just build it, I'll check in game". **Not played by
hand.** The name, the building and the puzzle are Claude's, to be changed
freely. MAP14 leads to it; its way out starts it again until there is a
MAP16, and its secret one leads to MAP32.

- **What changed from the outline.** One Pair, not two: every way Claude
  found to need two in one beam had a shorter way round with one. No
  lodger in the glass (with a Pair it plugs like any door, and adds
  nothing here). The player's own shots are not turned.
- **Places.** The mirror hall (start; both TEAL leaves; frames 101 west,
  102 east, 103 north): a mirror stands aslant in its middle, facing
  north-west, so that 103 and 101 look at each other in it and 102 looks at
  its back. On the north wall a target only the mirror shows: shot, it
  opens the steel door north. West, the darkroom (frame 106, a TEAL leaf
  only; sensor B). North, the gallery: empty to look at, four mirror panes
  down its north wall, and 18 monsters only they show (seen once dead);
  RED; frame 105; PINK. North of that the beam lab (the emitter, RED's far
  side at the other end, frame 107) and two cells behind steel doors: the
  first (sensor B opens it) has key 1, BLUE and the plasma rifle, the
  second (sensor C) key 2, and beyond it the store with VIOLET. The
  periscope room is BLUE's far side and has no other way in: frame 104,
  and two mirrors across its east corners that carry what comes out of 104
  round three walls to sensor C. Off the hall behind locks 1 and 2 the
  night room, brass frame for VIOLET only.
- **The puzzle**, 11 door actions, 480336 states, 0 stuck, nothing losable
  (the proof takes some minutes): a leaf in 101, its twin in 106, RED in
  103, the emitter (the beam goes by RED, the hall's mirror and the Pair to
  sensor B); BLUE swapped in for RED, through it with RED, which goes in
  104, the emitter (sensor C); key 2, VIOLET. The other way: the twin out
  of 106 into 104, and RED stays. The Pair is needed (106 takes nothing
  else).
- **The secret**: PINK leans by the gallery's south wall and only the glass
  shows it. Its far side is a room (a megasphere, cells, rockets) with the
  secret way out, a switch with the way out's sign (`Exit_Secret`). It is
  in the solver's proof as a door like any other. One secret sector.
- **The fights**: 158 monsters on "Resident" (81 on "Just visiting"), 32630
  health of them (MAP13: 106 and 21260), ammunition worth 2.41 times that,
  920 health, 500 armour, every weapon up to the plasma rifle, a backpack.
  Six ambushes (a leaf, RED, key 1, BLUE, key 2, VIOLET); RED's fills the
  gallery again, with monsters that are seen.
- **Made for it**: `ajarmap.unseen(m, box)` (every monster in the box at
  the start is drawn in mirrors only until it dies; `AjarUnseen`, 20093),
  `target(unseen=True)`, and the beam's reflection from the exact point of
  the glass (it was off by up to 18, enough to miss a sensor beyond a Pair).
- **Its look** is MAP11's Post Box from MAP11's parts (hall: the lab;
  darkroom: the pump room; gallery: the lobby; beam lab: the experiment
  hall; cells: the cloakroom; store: the archive; periscope room: the
  corridor). **Nothing was drawn for it**: a mirror has no frame, and in
  the gallery it is told from a doorway only by the strips of wall between
  the panes and by yourself in it.
- Since then (2026-11-19, Vadim played it: "there are invisible monsters?
  is this intended?"): a monster of the gallery is unseen only while it is
  in the gallery; one that walks out into the hall is seen like any other
  (`UnseenTick`). He also met the steel door already open after dying: a
  plain restart was tried headless and starts with it shut, so most likely
  a save made after the target was shot. For the gallery to explain
  itself (Vadim: "let's try to make the gallery more readable"): each
  pane stands in a frame of trim, set 8 back with a sill 24 high and a
  head at 200, and the first time the player stands in the room with any
  of them alive it says "This room is not as empty as it looks. The glass
  shows who is here." Seen headless only.
- **The secret way out, built with PINK** (2026-11-19, Vadim disliked the
  switch with the arrow). PINK's far side is now a night room in PINK's
  rose (`way_home(only=True, frame=SECRET_HOME, mouth=SECRET_MOUTH,
  rose=True)`: frame 193, mouths 591, the carpet strip one secret sector),
  with a brass frame inlaid with PINK that takes PINK only. Hung there,
  PINK stays and the mouths become `Exit_Secret` (`ComeHome` tells the
  frame by its id; `wayOutBuilt`, frame 190 and lines 590 are not touched;
  `secretOutBuilt`). In the back of that frame's empty recess sensor D
  (tag 4): it opens a steel door (line 314) at the north end of a passage
  from the periscope room's north wall (x 1664-1728, signed STAFF ONLY) to
  the middle of the night room's south wall. So: RED in 103 and PINK in
  101 (or the other way round), the emitter; the beam goes by RED and the
  mirror into PINK, out of its far side down the room onto sensor D. Then
  PINK through BLUE into the periscope room, through the steel door, into
  the brass frame. In the solver: region "secret", sight "d", and
  `stays={193: PINK}` (new in solve.py: a door hung there is not taken
  down again); nothing losable. `MAP=MAP15 MODE=3 tools/smoke.sh` plays it
  and leaves by it to MAP32.
- **RED's ambush is unseen too** (2026-11-19): an ambusher that comes in
  an `AjarUnseen` box joins the unseen ones (`UnseenJoin`), unseen while
  alive and in the box, as those placed there. The flash is seen.
- **The gallery's pillars stand before the strips of wall** between the
  panes (2026-11-19, Vadim: the one at 128..192 stood straight before the
  way in and hid the glass): x -64..0, 192..256 and 448..512. From the way
  in the pane 0..192 is clear. A demon and a spot of RED's ambush moved.
- **Two ambushes after the second beam** (2026-11-20, Vadim: after both
  beam experiments the gallery and the periscope room are walked again,
  empty). `ajarmap.ambush` has a new cause, 20 plus a target's or sensor's
  tag (set off), and `near=`: the ambusher holds back until the player is
  within that distance of its spot and in sight of it. Sensor C (cause 23):
  the gallery a third time, unseen (3 spectres, 2 revenants, 2 knights, then
  a cacodemon and a baron; near 700, so the far end comes as he walks in),
  and the periscope room, seen (4 imps, 2 chaingunners, a revenant, then a
  knight and a mancubus; near 640, all of the room from BLUE's far side).
  One who never goes back never meets them, and they are not in the kill
  count until they come. Checks `periAmbushSeen`, `galleryAmbushUnseen`.
- Not known: how hard the gallery is (monsters that are not seen, knights
  and cacodemons among them); whether the target in the glass is found;
  whether the beam's way round the periscope room reads; the frame rate
  with mirrors and hung doors in one view (headless only so far).

## Look: MAP11 (started 2026-11-19)

Board: https://claude.ai/artifact/Au3vTbXEAfHzH9bbVMmALm (source `design/map11-board.html`, images in
`build/board11/`: `<look>/view_NN.jpg`, `tex/` swatches, `sheet_<look>.jpg`
contact sheets). **Vadim chose 3, Post Box, for the whole level
(2026-11-19)**, and it is the default; `AJAR_INSTITUTE=1` or `2` are the
other two. The board shows the choice as open. Not played by hand.

`AJAR_INSTITUTE` picks the institute's look (`tools/gfx_institute.py`, names
`AJI<part><look>`); unset is 3, and 0 is the plain level (whose map is byte
for byte what it was before the looks, checked). Three institutes:
1. **Academy** (1950s): cream plaster under a cornice, oak panelling, red
   marble pillars and chequered stone in the lobby; parquet and olive oil
   paint in the corridor; white tile in the lab and the hall; globes.
2. **Thaw** (1960s, a science town): white perforated panels over ash slats,
   aluminium, terrazzo, a mosaic; pale blue in the corridor, green enamel in
   the lab, glass blocks and yellow mosaic in the canteen, concrete with a
   hazard stripe in the hall.
3. **Post Box** (a closed establishment, some years on): green or blue oil
   paint over yellowed whitewash, flaking; brown lino, khaki steel, tiles
   gone from the walls, red stencils.

The same idea in all three, drawn per look: the street doors behind the
start; on the lobby's long wall what the institute says of itself (a
painting of the first door; a mosaic of an atom with a door on one orbit; a
board of honour with two photographs taken down); a clock at a quarter to
and VISITORS BY APPOINTMENT ONLY; coats behind the cloakroom's counter; a
blackboard with the Pair drawn on it and cabinets of lenses in the lab; the
gallery's front as the kitchen's hatch, a menu; stacks and a card index in
the archive; tanks and gauges in the pump room; the machine (a door's
outline within itself on each face), the desk it was run from and a warning
in the hall. A plate over each way off the corridor (CLOAKROOM, OPTICS,
CANTEEN, PUMPS, ARCHIVE; TEST HALL on the locked door). The trim over frames
and far sides and the night room are not touched. All of it is Claude's
invention; Vadim, 2026-11-19: "your inventions are all good" (the machine,
the painting of the first door, the Pair on the blackboard, DO NOT OPEN
ANYTHING among them), so they stand.

How it is built (`map_institute1.py`): `dress()` gives a sector the look's
textures, `tint()` drops the room tints, `box()` and `pillar()` name a piece
of furniture's top and side, `over()` carries a wall on over and under an
opening, `opening()` and `squeeze()` do that for both sides, `named()` puts
a plate over a way (the map lists what it needs in `SIGNS`, and the locked
door's two faces in `FACES`; `gfx.make_all` hands both to
`gfx_institute.make`), `hang()` puts a picture on a piece of wall. The
canteen's wall is two storeys of 128, so the gallery and the balcony stand
in the upper one. Light is as it was, but for the pump room's lamp
(Vadim, 2026-11-19: "add a lamp in the pump room"): in a look a caged lamp
is on its ceiling over the gauges (`KQ`, drawn round the flat's corners,
since its square is 32 off the grid), and its light falls off in three
steps (200, 164, 136) to the room's 110, which is as it was. The spectre
that stood under it stands in the dark south-west corner instead. The
board's photographs are from before the lamp.

The tour (`ByAppointmentViews` in `map11.zs`, `MAP=MAP11 MODE=2`,
`smoke_MAP11_2.cfg`) has 37 views. `tools/board11_shots.sh` builds and
shoots all four (about 20 minutes), look 3 last, so the pk3 is left as the
game is.

Run: the tour in 0 to 3; `MAP=MAP11 tools/smoke.sh` in looks 1 and 3. Not run: the
solver (the puzzle is untouched, and the builds were `AJAR_QUICK=1`).

Put to Vadim at the foot of the board, none built: light (and a lamp in the
pump room, since built), windows, things on the floor, the machine as a free-standing
frame, whether the staff left in a hurry or long ago, room numbers on the
plates, a railing with gaps at the drops.

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
line's two doors ends the level. Out by the drop, nothing ends, and the line can be walked again. (The loop's
doors, fixed when the line was walked onto, stayed fixed at first; since
2026-11-18 they are free again once he is out: see MAP10, "The two ways out".)

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
  corner for the square's revenant; VIOLET (2026-11-18, Vadim), a spectre,
  and 3 s later an arch-vile at the foot of the cellar's stairs, which raises
  the demons killed there (not on the easiest skill).
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
  on it, at a piece of the south wall that opens with USE: the secret (a
  megasphere; it was the BFG).
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

**The level.** (Since "MAP31: the show" a hall starts empty and its first
monsters come after a count.) A foyer (shotgun, chaingun) and three halls joined by fixed
doorways: 768 x 704 (10 monsters and 9 in two waves), 1024 x 896 (17 and 15
in two waves, an arch-vile in the second; the super shotgun before it),
1280 x 1024 (25 and 27 in three waves, a cyberdemon the last; the plasma
rifle before it). One secret. Its look: see "Look: MAP31".

Tests: `MAP=TIME MODE=3 tools/smoke.sh` (the time box, `tools/map_time.py`:
14 checks, two trips, two earlier selves at once) and `MAP=MAP31 MODE=3
TIMEOUT=250 tools/smoke.sh` (21 checks: each hall begun, left, watched,
handed over, come back to, won; both cupboards), and `MAP=TIME MODE=4
TIMEOUT=60 tools/smoke.sh` (3 checks: a demon on the player's heels comes
out into the box and stays out of the fight). Not tested: a save and load
in the middle of a fight, dying in a box.

## Look: MAP31 (started 2026-11-17)

Board: https://claude.ai/artifact/MMbK5GrCDRL7CgunkFz8M1 (source `design/secret1-board.html`, images in
`build/board31/`: `<look>/view_NN.jpg`, `tex/` swatches, `sheet_<look>.jpg`
contact sheets). **Vadim chose 3, Fleapit, for the whole cinema
(2026-11-18)**, and it is the default; `AJAR_CINEMA=1` or `2` are the other
two. He also said yes to four of the options at the board's foot: see "MAP31:
seats, lights down, the leader" below, which changed all three looks. The
board shows the choice as open and none of that; this session could not open
its link (the account's artifact list does not have it). Not played by hand.

`AJAR_CINEMA` picks the cinema's look (`tools/gfx_cinema.py`, names
`AJY<part><look>`); unset is 3, and 0 is the plain level (whose map is byte
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

## MAP31: seats, lights down, the leader (2026-11-18)

Vadim chose Fleapit and, of the board's options, seats, lights down, a
picture on the screen and a darker surround for the time doors. Built for
every look (1 and 2 still build); the plain level (`AJAR_CINEMA=0`) is byte
for byte what it was, checked. **Not played by hand: no fight has been fought
over the seats or in this light.**

- **Seats** (`map_secret1.rows`): rows facing the screen, two banks either
  side of a middle aisle 128 wide, 96 from the side walls, the first row 192
  from the screen, one every 96 (5, 7 and 8 rows). A row is two low steps: 20
  of seat (12 high) and 12 of back (24 high), so nothing is more than a step
  and the player, every monster and every shot goes over them; they are not
  things and do not move, so the replay is not touched. The tall blocks stand
  among the rows. In look 3 some seats are gone (the same ones every build).
  One flat for a row from above (`SF`: the back is the north 12 of every 32,
  so a row starts at a multiple of 32), `SS` and `SB` for its sides.
- **Lights down**: the halls are 144 (looks 1 and 2: 148, 160; they were 176,
  180, 200); the 96 before the screen are 40 brighter and the next 96 are 20,
  as if the screen threw it. 120 was tried: walls across the view went black.
  Boxes (210), ways in, lobbies and the time doors' recesses are as they were,
  so the glass and the doors show from across a hall.
- **The screen** has a film leader's frame on it and is lit whatever the hall
  is (`lit=` on a line, new in `udmf.py`: the side's own light). The number
  counts down from hall to hall, 3, 2, 1 (textures `S1`..`S3`): fights left,
  this one included. The sweep has a quarter to go, as the time door's clock
  is at a quarter to. Provisional: the count could be read against HALL 1 to
  3; the hall's own number is a one-line change in `gfx_cinema.make`.
- **The time doors**: the recess round the ivory door is dark in every look
  (`TT`; `ajartime.hall_door(trim=)`), the boxes' doors too, and in the halls
  the wall over the door has a dark lintel (`TH`, `TG`).

Run in look 3: the tour (25 views, no engine warnings; `build/board31/3`,
`sheet_3.jpg`), `MAP=MAP31 MODE=3` (21 checks), `MAP=TIME MODE=3` (14). Not
run: the tour in looks 1 and 2 (their maps build), `MAP=TIME MODE=4`.
`tools/board31_shots.sh` now ends with look 3.

Left as they were: what the tall blocks are (in look 3 a bank of seats on a
riser, among rows of seats now), the posters, the signs. Not tried: seats
with backs high enough to hide behind (they would be walls to monsters).

## MAP31: the show, so that a replay is known at once (2026-11-18)

Vadim played MAP31: it did not read as going back in time at all. He asked
for something noticeable at the beginning of a fight, to be remembered and
then seen again from the box. Built; **he has not seen it yet.**

Every fight in a hall now begins the same way ("the show", `time.zs`):
- The hall is **empty and its house lights are up** (232) when the player
  comes in. After 50 tics the lights go down (to what the hall had), the
  screen counts **3, 2, 1** (tics 70, 105, 140; a click to each), and at 175
  the hall flashes and **the first monsters all come in at once** in
  teleport fog. Five seconds.
- From a box the same is the first thing seen: the hall lit and empty again,
  the earlier self walking in, lights down, the count, the monsters. The
  clicks are heard there too, quieter.
- After a fight is won its lights come up again.
- How: lights and the screen are not things, so they are not recorded; they
  are set from the fight's tic, the lived one or the shown one
  (`AjarTimeHandler.Show`). Map contract: sector tag and line id 3080 + 100 x
  fight (`ajartime.show_tag`). A hall without them (the TIME box) has no show
  and is as before. The monsters a hall used to start with are cues of wave
  1 that come at 0 left (`map_secret1.first`); the later waves are 2 to 4.
  They are thinned by difficulty as cues are, not as placed monsters were.
- The screen is blank but during the count (textures `Q0`..`Q3`, 96 high,
  and `R0`..`R3` for the great hall). The count from hall to hall (fights
  left) is gone.

Known: the screen is over the way in, so on coming in the player has their
back to the count and sees only the lights and the arrival (and hears the
clicks); from every box the screen is in view. If that is not enough: a
second count on the north wall, or the screen moved there.

Run in look 3: `MAP=MAP31 MODE=3 TIMEOUT=250` (39 checks, with `emptyAndLit`,
`count`, `theyCome` and the same three again from the box, per hall; its
pictures in `build/smoke31`), `MAP=TIME MODE=3` (14). **`MAP=TIME MODE=4`
fails (followed=0), and did before this change**: not looked into. Not run:
the tour, looks 0 to 2 (the plain level has the lights and the empty start
too, and no screen).

## MAP31: something to flee from, and its answer in the box (2026-11-18)

Vadim, after playing the show: better, but a fight needs something more
memorable, that sends him out of it and is seen again from the box. His
example, built as he gave it. **Not played by hand; the numbers are a guess.**

- **Hall 1.** With 4 of the first monsters left an arch-vile comes at the
  far end (and two demons); it raises what was killed, and the player has a
  shotgun and a chaingun. **Box 1 has the rocket launcher** and two boxes of
  rockets. With 2 left, two more arch-viles come (and two hell knights, a
  cacodemon): **box 2 has the BFG** and a cell pack. Box 3: rockets, cells,
  health. These lie in the open; hall 1 has no cupboards.
- **Hall 2.** A cyberdemon comes to the middle of the hall with the second
  wave (4 left). Its cupboards, which had the rocket launcher, now hold
  rockets and cells, and cells and a soulsphere.
- **Hall 3** is as it was (its cyberdemon is the last wave), but its secret
  is a megasphere now, the BFG being in hall 1.
- The arch-viles and the cyberdemon come on every difficulty
  (`ajartime.cue(always=True)`); the rest of a wave is thinned as before.

Run: `MAP=MAP31 MODE=3 TIMEOUT=250` (39 checks; each hall is won only when
every wave has come, so the new arrivals do come). No check looks at them
by name.

## MAP31: bigger halls, thick short fights (2026-11-18)

Vadim, after the arch-viles: better, still something missing. Bigger halls,
a bunch of monsters appearing in different places that can be set on each
other, more epic, and not long, so that watching it again is not a bore.
Built. **Not played by hand: sizes, numbers and thresholds are all guesses.**

- **Halls are half as big again**: 1152 x 960, 1536 x 1216, 1920 x 1472
  (they were 768 x 704, 1024 x 896, 1280 x 1024), four, four and six tall
  blocks. Their ways in are where they were (halls at x -192, 2752, 5696),
  so the foyer and the doorways did not move. Rows of seats fill them.
- **Monsters come in kinds, each kind in its own part of the hall** (imps
  along the far wall, chaingunners down the sides, knights opposite
  revenants, and so on), so they are in each other's fire.
- **The next wave comes while about half the last is alive** (thresholds
  10 and 6; 14 and 8; 16, 10 and 6; they were 2 to 5): thicker and shorter.
- Hall 1: 18, then the arch-vile with 3 hell knights and 3 revenants, then
  two arch-viles with 2 mancubi and 3 cacodemons (rocket launcher and BFG
  in boxes 1 and 2, as before). Hall 2: 28, then the cyberdemon with 3
  mancubi and 2 arachnotrons, then an arch-vile, 3 barons, a pain elemental,
  3 revenants. Hall 3: 31, then 12, then 9 with two arch-viles, then **two
  cyberdemons** and 4 imps.
- Nothing sets monsters on each other by script: it is left to where they
  stand and to the player. If they do not fight enough: give a wave's
  monsters a target of another kind when they come (one line in `Cues`).
- A replay still runs at the fight's speed. If it is still long to watch:
  run it faster after the count (the box's own track would have to be
  recorded per shown tic; not built).

Run: `MAP=MAP31 MODE=3 TIMEOUT=250` (39 checks; coordinates moved in
`SecretScript`). The tour's views in the halls were moved by hand
(`SecretOneViews`) and **not run**; the board's pictures are of the old
halls. Supplies were not raised for the bigger fights.

## MAP31: killed into a box, and a door that is felt (2026-11-18)

Vadim asked for both. Built; **not played by hand.**

- **Killed in a hall with a box still unused, the player is not dead** but
  in the next box, before the fight, health 50 (`RESCUE_HEALTH`), as if they
  had left at that moment by the time door nearest to where they fell; that
  is the door they come back in by. It uses up the box like any trip.
  Nothing follows them. With no box left, or in a box, death is death.
  How: `bBuddha` on the player while it can happen (health stops at 1),
  and `AjarTimeHandler.Rescue` at health 1. Damage that would have left
  exactly 1 health counts as a death too.
- **Going through a time door is felt**: a white flash (red after a death),
  the teleport sound, and for a second the clock runs back to 0:00, large,
  in the middle of the screen. A lighter flash on coming back into the hall.

Run: `MAP=MAP31 MODE=3 TIMEOUT=250` (40 checks; hall 2 is now left by being
killed in its middle: `killedIntoTheBox`), `MAP=TIME MODE=3` (14). The flash
and the clock were not looked at in a picture.

**The tall blocks are gone** (Vadim found them odd; he chose pillars and
stepped seating, not loudspeakers). In their places (`map_secret1.pillar`,
`platform`):
- **Pillars**, 64 square, to the ceiling, in the hall's own wall: the pair
  nearer the screen in each hall, and a third in the great hall.
- **Banks of raked seats**, 192 square, the pair further from the screen:
  three rows rising away from it, 24 a row, a walk behind each and a plain
  rim either side. Every step is 12, so everything walks up from the front;
  the back (72) and sides are sheer, which is the cover. Not things, so a
  replay is not touched.
- The great hall's arrow is on a bare patch in the top row of a third bank,
  straight north of the wall that opens, as before.
Seen in the tour (25 views, `build/tour31`, look 3; its moved cameras all
stand in the open). Not seen: looks 1 and 2. Not played: whether a bank is
cover enough, being 72 where a block was 80, and walkable.

**After a fight** (Vadim: the way into hall 2 offered too little): a
megasphere, a box of rockets and a cell pack in the way into hall 2 and
into hall 3 (hall 3's blue armour became the megasphere). Not played.

**Killed in a box** (Vadim: the game "kind of hangs" there; he asked for the
same as in the hall). With a box still unused the player is in the next one,
health 50, and watches from the start again; what they were watching is
dropped (`Rescue`: puppets away, the fight as it was left, the old box's door
shut), and they come back in by the door they first left by. What was in the
old box stays there. With no box left death is ordinary death, in hall or
box. `killedInABox` in MAP31's walk (the great hall). **The hang itself was
not found or reproduced**: if a death with no box left still hangs, that is
it, and it is open.

**Stuck at a door (Vadim, playing, "very often"): fixed.** A door that shuts
behind the player is a solid line, and whoever overlaps it cannot move at
all: in the box just after going out, and in the hall after the last trip.
`StepClear` now puts the player 26 clear of the line they came out of
(`Leave`, `Back`). Not played by hand. The headless walks never caught it:
they go through at speed 8, and two checks (`backIn` in MAP31, `backIn2` in
TIME) had the stuck position written into them; both now allow the player
to have walked on.

## MAP31: the second hall is an open fight (2026-11-18)

Vadim: in the second battle the box is open when the fight starts, so that
he can join his past self and help. Built for hall 2 only. **Not played by
hand, and never seen in a picture.** This is the first place in the game
where the past is changed; "No real rewind" still holds, differently:

- **A trip begins the fight again; it does not show it.** The hall is
  cleared (monsters, shots, corpses, what monsters dropped), the show runs
  and the same monsters come. The box's door is open at once, onto the door
  the player left by. Three boxes, by stepping out or by being killed, as
  in the other halls.
- **Every earlier go is there as an earlier self** (`AjarGhost`): it walks
  where the player walked, from the start of that go (the second one starts
  in its box), and fires what they fired, really. It cannot be hurt; what
  it hits turns on it. When that go's time is up it is gone: at the time
  door if the player left by one; if they were killed, **it runs to the
  nearest time door and goes in** (Vadim's rule: there is never more than
  one of the player left in a fight, even if what killed them is dead this
  time). It runs straight, through seats and pillars.
- The clock at the top shows how far the last go ran.
- What is kept of a go (`AjarTake`): place, angle, pitch, sprite each tic;
  missiles (anything flying whose shooter is the player: class, place,
  speed); bullets and shells by the ammunition that went (a bullet, 7
  pellets for a shell, 20 for two). **Fist and chainsaw are not kept, and
  the BFG's rays come from where the ghost stands.**
- Map contract: `ajartime.zone(open=True)` on the hall's zone (args[4]).
  Cues are now spent (`special1`), not destroyed, in every fight, so that
  one can begin again.
- Known: what the player took from the hall (the room key) stays taken;
  the kill count rises with each go; monsters do not see a ghost until it
  hurts them.

Run: `MAP=MAP31 MODE=3 TIMEOUT=250` (hall 2: `killedIntoTheBox`,
`begunAgain`, `besideMyself`, `itFiresAgain`, `theyComeAgain`,
`itWentToADoor`; the test hands the ghost a rocket and a missing bullet
rather than firing a weapon), `MAP=TIME MODE=3` (14).

## MAP31: boxes left over, and the end of the show (2026-11-18)

Vadim asked for both. Built; **not played by hand.**

- **Boxes not used in a fight that is won are kept** (`spare`). Killed in a
  later fight with none of its own boxes left (its own go first), the
  player is in the oldest spare box, health 50. That fight is over, so the
  box's door is open at once onto its hall's first time door; the way back
  is the way they came (steel door, lobby, arch). The fight they fell in is
  cleared and its lights are up; **it begins again when they walk into its
  hall** (`comeBack`, `Resume`): an open fight with their earlier selves,
  the others simply from the start, with no replay.
- **With no box of any kind left, being killed ends the level**: the player
  cannot die in a fight at all now (`bBuddha` throughout); the screen goes
  black, "The show is over", and the level is left two seconds later
  (`level.ExitLevel`; MAP31's next is MAP31, so it starts again). Vadim had
  found that the last death left the level hanging. **This path is not run
  by any test.**

- **A body is left where the player was killed in a hall** (`AjarCorpse`;
  Vadim: the past self just disappeared). It falls when the replay hands
  over (it is a thing of the hall, held and hidden like the rest until
  then), and later replays show it fall at that moment. Not in hall 2 when
  the fight begins again at once: there the earlier self runs for a door,
  as he asked before, and the hall is put back. Not for a death in a box.
  Checked only as "it is there" (`aBodyIsLeft`); not seen in a picture.

- **The end of the show, after Vadim played it: fixed.** The level began
  again with the player frozen, at 1 health and with all they carried
  (`CF_TOTALLYFROZEN` and the rest go with the player to the next level).
  Now the freeze is taken off, and the level is left by `level.ChangeLevel`
  with health reset, and inventory too when the next level is this one.
  `MAP=MAP31 MODE=5 TIMEOUT=60` (`smoke_MAP31_5.cfg`): `theShowIsOver`,
  `beganAgain`, `andCanWalk`.
- A level with no door to carry no longer opens with "USE a door to take it
  with you" (`AjarHandler.PlayerSpawned`): MAP31 says "Three halls, three
  fights. A door with a clock on it leads out of a fight: to before it began."

Run: `MAP=MAP31 MODE=3 TIMEOUT=250` (hall 3 now also: `killedIntoASpareBox`,
`begunOver`; a hall's part of the walk is 900 tics), `MAP=TIME MODE=3` (14).
Not tested: walking out of the spare box and back to the fight (the walk
teleports).

## MAP31: the reel (2026-11-18)

Vadim's idea: after all the fights, back in the first hall, a screen comes
down and on it are all his deaths, close up and slowed down. Built. **Seen
only in the headless walk's pictures (`build/smoke31`, the last three); not
played by hand.**

- **The last way out leads to a seat in hall 1** (a teleport, tid 3070; it
  was the level's exit). The player is held there, unseen, the lights go
  down, and **a big screen comes down before the way in** (512 by 224: a
  slice of the hall whose ceiling is lowered, sector tag 3070).
- **On it, every time the player was killed in a hall**: the last two
  seconds (`REEL_LEN` 70 tics) at a third of the speed, then the fall. A
  caption says which hall and which of how many; USE goes to the next.
  Then "THE END", black, and the level ends (its next is MAP31).
- **Never killed in a hall: the deaths of the three biggest monsters
  instead** (Vadim; 600 health and up, kept 45 tics after each died, so its
  fall is in the clip; the caption names it). Killed in a box only: the
  same. None of either: one line, and the end.
- How (`time.zs`, "the reel"): while a fight is lived, the hall's last 70
  tics are kept as stills (every thing's place and picture). A death, or a
  big monster's, keeps a copy. For the reel a clip is played with puppets
  in the hall where it happened, now empty, before a camera 120 from where
  the player fell (230 for a monster), put where it can see the spot; its
  view is the texture `AJREEL` (`cameratexture`, in `gfx.py`'s animdefs)
  on the screen's face.
- Known: no sound; 12 pictures a second (a still is shown three tics); a
  clip of hall 1 is played round the seated player, who is unseen so as not
  to be in it; clips are not kept in the fight a death with no box left
  ends, since the level ends there.

Run: `MAP=MAP31 MODE=3 TIMEOUT=250` (after the halls: `bigDeathsKept`,
`theReelBegins`, `theScreenIsDown`, `aDeathInHall2`, `theFall`, `theEnd`,
`levelExited`; 14 pictures). Not run: a reel of monsters' deaths, a reel
with nothing in it, USE to skip.

## MAP31: the reel's last scenes, and the count's sound (2026-11-19)

Vadim's two asks, done by the MAP12 session. **Not played by hand.**

- **After the reel's clips, one more for every hall: the monster killed
  last in it**, whatever its size, with its fall (kept 45 tics after it
  died, as the big ones are). Caption "HALL n - the last to fall: NAME".
  Where that death is already among the big monsters' it is not shown
  twice. Every death in a lived fight is a candidate; a later one in the
  same hall replaces it (`lastKills`, `dueLast` in `time.zs`). Checks in
  `MAP=MAP31 MODE=3 TIMEOUT=280`: `aLastKillForEveryHall`,
  `lastScenesOnScreen`.
- **The count before a fight ticks with the switch-off sound**
  (`switches/exitbutn`, what the menu makes closing) instead of the
  switch-on one. The plates that wind a fight keep the old sound.

## MAP31: not killed but taken out (2026-11-18)

Vadim changed his mind about the body: the player is not dead, they were
saved at the last moment and sent back to the past, so no death animation
and no corpse. **This replaces every "body" and "fall" above** (`AjarCorpse`
is gone). Instead (`AjarSnatch`): where they stood, their own shape gone to
light (additive, bright), rising and fading in a second, in a teleport's
flash with its sound. In halls 1 and 3 it happens when the replay hands
over, and later replays show it; in the reel a clip ends with it, slowed.
Hall 2 is as it was (the earlier self runs for a door). Not seen in a
picture; checks `goneToLight`, `goneToLightOnScreen`.

## Handoff (2026-11-18): MAP10 after Vadim played it

Four changes, all from his play of MAP10. Details are under "MAP10", "The two
ways out", and under "Ambushes: no two alike".

- **VIOLET's ambush**: a spectre at once, an arch-vile 3 s later at the foot
  of the cellar's stairs (it raises what was killed there). Not on skill 1.
  `AmbushClass` knows editor number 64 now.
- **PINK's room's frame takes any door** but PINK. No Stray door opens onto
  PINK's room (`StrayPool`; `solve.py` leaves the secret door's home out of a
  draw and refuses that door in the secret frame; no PUZZLE key needed, both
  read `home_chain["secret"]`).
- **Out of the line by the hole, the loop's doors are doors again**
  (`ChainTick`), so a plain loop can be rebuilt as the long one. MAP09 too.
- **MAP08's brass frame**, which still takes BLUE only, is inlaid with blue
  (`AJXA2`, `AJXF2`). What a brass frame is otherwise: the place where a loop
  counts, facing its twin, left alone by the repainter. Vadim asked whether
  the way out could do without brass frames; left as it is, not decided.

Run: the full build (every level re-proved with the changed solver: 0 stuck;
MAP10 9 door actions, 11 to the secret way out, nothing lost), `MAP=MAP10
MODE=3` (20 checks, `anyDoorInPinksRoom`, the arch-vile comes, out by the
secret way) and `MODE=1`, `MAP=MAP09 MODE=3` (19, `itsDoorsAreDoorsAgain`),
`MAP=MAP08 MODE=1` (41).

Not done:
- Nothing here is played by hand. The arch-vile's fight in a cellar 416 by
  448 with two low crates for cover may be too hard: ask.
- The blue inlay was seen only at the edge of a walkthrough's shot. Look at
  it in the game (MAP08's night room, the east frame).
- MAP10's other walkthrough (`MODE=2`, the tour) and MAP01 to MAP07's were
  not rerun; their maps did not change. MAP08's and MAP09's Stray draws are
  as before (they have no longer chain).
- No check plays the refusal of PINK in its own room, or taking the plain
  loop apart and building the long one after the hole (MAP10 has no such
  script; MAP09's only checks that the doors are free).

## MAP31: the great hall is an open fight too (2026-11-18)

Vadim: the third battle by the second's rule. `open=True` on hall 3's zone;
nothing else in the map changed. Only hall 1 is still watched from its box.
**Not played by hand.**

The walk (`MAP=MAP31 MODE=3 TIMEOUT=250`, 52 checks): being killed in a box
while watching (`killedInABox`) is now done in hall 1, the only hall where
one watches; hall 3 is left by its west door (the first time an open fight
is left by a door in a test): `begunAgain3`, `besideMyself3`,
`itLeftWhenIDid`. The spare box is therefore hall 1's third.

## MAP31: killed beside an earlier self, the player goes on as it (2026-11-18)

Vadim asked what should happen when a later go is killed sooner than an
earlier one (a long first go, then two deaths at the very start: three boxes
gone). He chose this of four. **Not played by hand.**

- Killed in an open fight's hall while an earlier self is still fighting,
  the player is not in a box: they go on as that self, from where it stands,
  facing as it faced, health 50 (`GoOnAs`; the self with the most time left).
  **No box is spent**; the price is that helper.
- The rest of what that self did is dropped for good: in a later go it is
  there only up to that moment, and is gone where the player took over.
- Their shape goes to light where they stood, and the death is in the reel,
  as any death in a hall.
- With no earlier self in the fight (none yet, or its time is up), and for a
  death in a box, it is as before: a box.
- Known: the earlier self could not be hurt and the player can, so they may
  take over in a bad place.

Run: `MAP=MAP31 MODE=3 TIMEOUT=250` (53 checks; hall 3: `onAsMyEarlierSelf`;
the reel now has three deaths), `MAP=TIME MODE=3` (14).

## MAP31: a monster shut in a box comes back to the hall (2026-11-18)

Vadim, playing hall 1: two revenants came into the box after him and killed
him there; he was in the next box, then won the rest of the fight, but those
two stood in the first box behind its glass, out of reach, and the fight
could not be won (its count is of every monster of the fight, in a box too).
He likes that monsters can come into a box; the fight must still end.

- `BackToTheHall`: while the fight is live and the player is in the hall
  (so every box is shut), a living monster that stands in a box of the fight
  is put in the hall, by the time door farthest from the player, in a
  teleport's fog, and is after the player. If there is no room there it
  comes when there is. Every fight, open or not. So it also covers a
  follower that was simply left behind in a box when the player went back.
- While the player is in a box with it, nothing changes: it fights there.

Run: `MAP=TIME MODE=4` (`notShutInTheBox`; its `followed` check still fails
as before: not looked into), `MAP=TIME MODE=3` (14), `MAP=MAP31 MODE=3
TIMEOUT=250` (53). **Not played by hand.**

## MAP31: waiting in the box of an open fight (2026-11-18)

Vadim: he tried to stay in the box for a while, and it did not work at all:
every monster was after him and came to his side of the hall.

- `Hunt`: in an open fight, while the player is in a box, each monster of
  the hall is after the nearest earlier self, not after the player (a
  monster is set on the player when it comes in; that is taken back). An
  earlier self cannot be hurt, so it holds them.
- When no earlier self is left, or the player is in the hall, a monster
  that is after no one is after the player. One that is on an earlier self
  stays on it until that self is gone or something else hurts it.

Run: `MAP=MAP31 MODE=3 TIMEOUT=250` (54; hall 2: `afterMyEarlierSelfNotMe`).
**Not played by hand.**

## MAP31: an open fight's last go is played, monsters and all (2026-11-18)

Vadim: the earlier self only fires where the monsters were, at nothing. He
asked for the monsters to be played too, and to mix the two: when he steps
in as the second of him, half the monsters still play the demo and half are
on him; as the third, two thirds and one third, at random. And what
arch-viles and pain elementals did is played as well. Built for both open
fights (halls 2 and 3). **Not played by hand; seen in two pictures of the
walk** (`build/smoke_MAP31_3`: from hall 2's box, and in hall 3 after
stepping in).

- **Each go is recorded whole** (`AjarDemo`, `AjarRole`): every monster in
  the hall, each tic: place, angle, picture, health; and every missile a
  monster shot. It is the next go's demo. A third go plays the second,
  which has the first self and the monsters as they then really moved.
- **In the box the last go plays exactly.** Its monsters are real monsters
  ON THE DEMO (they carry `AjarRail`): put each tic where they were, dying
  when they died, raised when they were raised; their missiles fly again,
  really (they can hit the player; bullets, bites and an arch-vile's blast
  do nothing). A lost soul comes again when it was spat, if its pain
  elemental is still on the demo. Flames, puffs, blood and fog of then are
  shown as pictures (`RecordFx`).
- **Stepping into the hall wakes a share of those alive just then**, picked
  at random: 1/2 in the second go, 1/3 in the third (`StepIn`). They are
  real from where they stand, with the health they had, and after the
  player. One that comes later has the same chance.
- **The player's shot wakes the one it hits**, with that damage. Nothing
  else can hurt a monster on the demo.
- **When the demo is over** (the tic the last go ended) all wake.
- A wave that came in the last go comes when it came then; a wave that did
  not comes by the usual rule, even while the demo plays.
- A monster on the demo is not solid: it walks through the player and the
  monsters that are awake. So it wakes when it stands free; after a second
  it steps aside or wakes where it is.
- This replaces "the fight begins again from nothing". `Hunt` (monsters
  after the earlier selves while the player is in the box) now only matters
  once the demo is over. Going on as an earlier self is as it was.
- Known: a monster that wakes begins its move again; a raise does not
  happen if the monster that was raised is awake this time; the flame of an
  arch-vile that is awake this time is still shown where it was; a monster
  awake may spend its fire on one on the demo, which it cannot hurt; the
  kill count rises with each go.

Run: `MAP=MAP31 MODE=3 TIMEOUT=250` (58; hall 2: `theyPlayAsTheyWent`,
`allAwakeAtItsEnd`; hall 3, stepped into at once by the test:
`halfOfThemWake`, `wokenByAShot`, `allAwakeAtItsEnd3`), `MAP=MAP31 MODE=5`,
`MAP=TIME MODE=3` (14). Not in any test: a death and a raise on the demo, a
lost soul, a third go.

## MAP31: armour in the boxes (2026-11-18)

Vadim: he left the boxes too weak. (First read as ammunition, built and
taken out again: the ammunition was right as it was, enough to win and not
easy; only a few more cells.) Every box has green armour now, on the floor
in its middle (`Hall.more`), and a cell pack beside it in all but hall 1's
first box. A box's things are taken once. Not played by hand; the walk
passes.

## MAP31: a pure demo, and what Vadim found playing (2026-11-18)

Vadim played the open fights. Three things.

- **Pure demo (his choice, instead of the share that woke).** By chance he
  had a go in which nothing noticed him, and liked it better than 1/2 and
  1/3. Now stepping into the hall wakes nothing. A monster stays on the demo
  until the player hurts it, **or walks into it** (it wakes once they are
  out of it, or after a second), or the demo is over. `StepIn` is gone.
  Why nothing woke in his go was not found; it no longer matters.
- **Shut in a box: fixed.** After coming back from a spare box he was
  suddenly in hall 3's third box, its door shut. Cause: killed, he went on
  as an earlier self (`GoOnAs`), and that self was at that tic still
  standing in its box, where a go begins. Now only an earlier self that is
  in the hall is taken; with none there, a death is a box as usual.
  **Not tested** (it needs a third go).
- **The green armour could not be taken.** Not explained. The game refuses
  it only at 100 armour or more. The walk now takes the armour of the box
  it is in during a replay (`armourInTheBox`), so the thing is real there.
  The HUD had no armour number: it has one now, over the health, green, or
  blue for blue armour and megaspheres (`AjarStatusBar`), so that he can
  see what he has when it is refused.

Run: `MAP=MAP31 MODE=3 TIMEOUT=250` (60; hall 3: `noneWakesAsIStepIn`,
`wokenByAShot`, `wokenByATouch`, `allAwakeAtItsEnd3`), `MAP=TIME MODE=3`
(14). **Not played by hand.**

## MAP31: no keys, and more monsters (2026-11-18)

Vadim, after playing the pure demo ("much better"): the room keys are of no
use, and the fights are easy now: twice the monsters in the second hall,
three times in the last.

- **The room keys and the boxes' cupboards are gone** from MAP31. What the
  cupboards held lies on the floor of the same boxes (`Hall.more`). The
  `AjarLocker` class and `ajartime.locker` are still there, unused here.
- **Hall 2 has twice its monsters, hall 3 three times** (`TIMES` in
  `map_secret1.py`; on the hardest difficulty 84 and 174, fewer on the
  easier ones as before). Every kind, the cyberdemons and arch-viles too
  (hall 2: 2 and 2; hall 3: 6 and 6). The spots in the script are as they
  were; `flush()` puts the others beside each, clear of walls, pillars,
  banks and each other. A wave comes when that many times as many are left.
- **Ammunition is as it was.** Not looked at; it was right for a third of
  these.
- A body that lies still is no longer written down tic by tic (`lag`): a
  demo of the great hall would have been tens of megabytes.

Run: `MAP=MAP31 MODE=3 TIMEOUT=250` (60), `MAP=MAP31 MODE=5`, `MAP=TIME
MODE=3` (14). **Not played by hand.**

## MAP31: what Vadim found on the third go (2026-11-18)

- **Bodies stopped in their fall.** A monster that was still falling dead
  when a go ended was left, at the end of that go's demo, on the picture it
  had reached (the first ones look like a standing monster): a stopped
  figure that nothing woke. Now it falls on from that picture (`FallOn`,
  `PictureState`; a gibbed body keeps its own).
- **Going on as an earlier self gives what it carried**: of each kind of
  ammunition, and of armour, its amount at that moment where that is more
  than the player's own (`Carry`; a go writes down every change, in
  `AjarTake`). Never less, so that what a box gave since is not lost.
- **Killed into a box, the player stands for a second** (`stand`,
  `CF_FROZEN`: they can look about). Keys still held from the fight walked
  them out of the door, which shut behind them. And **a spare box's door
  stays open** while they are in the box or its hall; it shuts when they
  have left that hall (`SpareTick`). Neither is run by a test.
- `MAP=MAP31 MODE=6 TIMEOUT=160 ./tools/smoke.sh`: hall 2 three times over,
  both later waves, a third go, on as an earlier self (8 checks).

Run: `MAP=MAP31 MODE=3 TIMEOUT=200` (62), `MAP=MAP31 MODE=6` (8). **Not
played by hand.**

## MAP31: a wave comes on the clock too (2026-11-19)

Vadim: in the third hall some monsters seemed to come only after he shot,
which spoils setting them on each other. They did: a later wave came only
when no more than its number of monsters were left, so only kills brought
it. Now a wave also comes when its time has: 25 seconds after the first
monsters for the second wave, 50 for the third, 75 for the fourth
(`WAVE_TICS` in `Cues`, `time.zs`), whichever is first. In every hall, and
in the TIME box. The 25 seconds are Claude's guess.

## MAP31: where it stands (handed on, 2026-11-18)

- Hall 1 is watched from its box (a replay, nothing changes). Halls 2 and 3
  are open fights: the last go is a pure demo; see the four sections above
  for the rules as they now are (the 1/2, 1/3 share and `Hunt`'s part
  before the demo's end are history).
- Open with Vadim: why green armour was refused in a box (the HUD shows
  armour now; he was to look at the number); whether ammunition is enough
  for the new numbers; whether the green armour in the boxes stays.
- Never run by a test: going on as an earlier self when one is still in
  its box; the second's stand in a box; a spare box's door.
  `MAP=TIME MODE=4` fails on `followed` and did before today.
- Everything is on `origin/main`.

## MAP32, the second secret level (2026-11-19, agreed in outline; built: see "Double Shift" below)

From MAP15's secret way out (the door only the glass shows). Vadim's brief:
MAP31 was time paradoxes; this one joins time and space. He chose four of
Claude's five ideas. Everything not marked as his is Claude's proposal, and
**every engine claim here is an expectation: `time.zs` was not read for
it.** No name yet.

- **The rule** (Claude's; Vadim took the ideas that rest on it and has not
  spoken on it by itself): MAP31's "the past cannot be changed" stays. New:
  **what an earlier self did to a door is done again for real** when the
  replay reaches that moment (hang, take down). Glass keeps the player
  from the earlier self's side as it does in the boxes; doors are what
  crosses it. Time parts the selves, space joins them.
- **1. Meet yourself halfway.** Two wings with no way between, a leaf of
  one Pair in each. First go: through wing A, hang the leaf, into the clock
  door. Out in wing B before the fight, the earlier self behind glass in A.
  Hang the twin; when the earlier self hangs its leaf the link opens. A
  leaf hung alone is a shut door, so nothing the earlier self saw is
  contradicted.
- **2. A fight handed across.** What is on the player's heels comes out
  into the box with them (MAP31 has this). The box has a frame: the player
  chooses where the earlier fight's monsters are delivered, a cell or the
  other group (MAP13's infighting).
- **3. Three of you, one chain.** MAP09's way out (two doors in two brass
  frames) with the frames too far apart for one carrier: each go carries
  one door, the third walks the line. The level's end.
- **The level's own secret: the glass shows later.** A mirror shows the
  room as it will be (MAP15's mirror-only things): a door hanging in a
  frame that is empty now. The player takes it out of the reflection and
  owes it: it must hang in that frame by the end. What is shut while it is
  owed is not settled.
- **Not here** (Vadim: "rather left as a secret or a puzzle for a normal
  level"): the relay with yourself. MAP08's shutter with the lever too far
  to run, the earlier self pulls it while the player stands at the shutter;
  or the earlier self sends the lift the player rides.
- **To test first**: done, all three steps, see "Doors in a fight that is
  stepped out of" below.
- **Open**: fights as thick as MAP31's or more puzzle than fight; the
  place and the name; whether it waits for MAP15's mirrors to be built.

## Doors in a fight that is stepped out of (2026-11-19, built and tested)

For MAP32. `src/zscript/timedoor.zs`, the test map `tools/map_timedoor.py`
(TDOOR: the time box with a frame in the hall, one in the west box and a
TEAL leaf in each; and a chain, a brass frame in the hall and one in the
box, RED and BLUE, the night room). `MAP=TDOOR MODE=3 TIMEOUT=120
tools/smoke.sh`: 20 checks; `MODE=4` (the chain): 8, and out by the line;
`MODE=5` (a fight handed across): 7. All pass. **Not played by hand.**

- **A door is not a puppet: what was done to it is done again.** Every
  change to a door while a fight is on is written down with the fight's
  tic, the one lived or the one being watched from a box. On stepping out
  the doors are put as they were at the fight's first tic, and the replay
  makes each change again for real (`AjarHandler.Hang`, `Unhang`): the
  earlier self takes the leaf, the leaf hangs, a Pair joins. What a self
  did in a box is done again in later trips the same way. Doors are left
  out of the puppets and of what stands still (`Counts`).
- **Held while watched** (Claude's choice, to be seen by Vadim): a hung
  door with an end in the fight's hall is seen through during the replay,
  the earlier self close to in front of its frame, but nothing passes it,
  no walker, shot or sight (`DoorHold`). It opens when the fight is where
  it was left. The other choice is a shut leaf until then.
- **A door does not go through a time door** (Claude's choice): it is left
  leaning at it. Carried through, the same door would lean in the hall and
  be in the player's hands at once.
- Tested: the hall's leaf hung alone, out, the leaf back where it leaned;
  the twin hung in the box first; the earlier self takes and hangs its
  leaf, the Pair is joined and held; open at the handover and walked
  through; a second trip with a leaf in hand, left at the door, and both
  earlier selves hang their leaves again.
- **The chain by two selves** (MODE=4): RED hung in the hall's brass frame,
  out; BLUE hung in the box's; the earlier self hangs RED again and the
  loop is closed in the replay. **A closed loop is held whole** while the
  fight is watched, the box's end too (Claude's choice), or the player
  would be on the line and out of the level before the fight is where it
  was left. At the handover: through BLUE onto the line, out by RED, the
  level ends. So two brass frames that one carrier cannot join (a door
  does not go through a time door) are step 3; the loop of three (MAP10's
  `way_longer`) would need the third self, and is not tried.
- **A fight handed across** (MODE=5): a demon on the player's heels comes
  out into the box; BLUE hung in the box's frame opens onto the night room;
  the player goes through, the demon after them (`AjarSense`, as with any
  hung door); BLUE taken down, the demon is shut away and no longer counts
  in the fight (`Left`: it is in none of the fight's zones). A door from a
  box to anywhere but the hall is not held. `MAP=TIME MODE=4`, the older
  test of following, fails all four checks as before.
- **Not done**: a paradox (the player takes down in a box a leaf that a
  self in the same box is about to hang: the replay just takes it out of
  their hands); a fight put back after a death (`Resume`, `GoOnAs`); open
  fights (halls 2 and 3 of MAP31 have other machinery); brass
  frames with a lift; the loop of three; a thief; a save in the middle.
- `MAP=TIME MODE=3` still passes (14). `MAP=MAP31 MODE=3` fails one to
  three checks a run, not the same ones (`noneWakesAsIStepIn`,
  `aLastKillForEveryHall`, `lastScenesOnScreen`), **with and without these
  changes**: the fights are not the same twice.
- Two sessions building at once write over `build/ajar.pk3`:
  `AJAR_OUT=build/mine.pk3 ./build.sh`, `PK3=build/mine.pk3 tools/smoke.sh`.

## MAP32 "Double Shift", built (2026-11-19)

`tools/map_secret2.py`, `src/zscript/map32.zs`; `MAP=MAP32 ./run.sh`;
`MAP=MAP32 MODE=3 TIMEOUT=120 tools/smoke.sh "$PWD/build/smoke32"`: 18
checks, all pass, and out by the line. **Not played by hand: no fight has
been fought, the test's monsters stand still, and the numbers of monsters
and supplies are a first guess.** Built in a worktree (`../ajar-map32`,
branch `map32`). Vadim chose the three steps and left the rest; the place,
the name, the layout and the numbers are Claude's, to be changed freely.

- **The place: a works, three shops.** A shop is a pit (the shop floor)
  under a gallery, which is the way in: a drop of 64 that is not climbed.
  Time doors in the pit's walls as in MAP31; behind glass, the offices. The
  first trip out of a fight leads to the big one, **the wing**; the next
  two to small ones with supplies, as MAP31's boxes. All fights are watched
  ones (hall 1 of MAP31), none open. In plain textures: no look yet.
- **What makes two selves needed.** A door does not go through a time door,
  and the gallery cannot be reached from the pit or the wing. So what is
  on the gallery can be hung there only before the drop, by the self that
  is then seen from the wing.
- **1, the fitting shop: meet yourself halfway.** On the gallery a TEAL
  leaf, YELLOW, and a frame that takes a TEAL leaf only (`only=3`); in the
  wing the twin and two frames. YELLOW opens onto shop 2, so it is wanted
  in the wing. Hang the leaf, drop, step out, hang the twin; when the fight
  is where it was left, go through to the gallery, fetch YELLOW, hang it
  in the wing. The fight is not won but left. 20 monsters and two waves
  (34 on "Resident" before thinning).
- **2, the press shop: a fight handed across.** This one is won (its steel
  door is the way on). Two arch-viles come with the second wave. The wing
  has a frame and GREEN, which opens onto the lock-up, a room with a pillar
  that nothing else leads to: what is on the player's heels at a time door
  (two at most, an arch-vile is small enough) comes into the wing and can
  be led through GREEN and shut away. 25 and two waves (46).
- **3, the despatch: one chain, two selves.** RED and a brass frame on the
  gallery, BLUE and the other brass frame in the wing, the night room
  (`way_through`). The loop is closed in the replay and held; at the
  handover, through BLUE onto the line and out. Left, not won. 30 and two
  waves, a cyberdemon in the last (48). **Not "three of you"**: the loop of
  three is not tried, and two selves are what the tests cover.
- **Nobody is stuck.** A fight won opens its steel doors: in shops 1 and 3
  a stair from the pit to the gallery and a passage from the gallery to
  the wing, so everything can then be carried on foot. A player who drops
  without hanging, or spends the wing's trip, has that left: the fight.
- **A fight left unwon is over when the next begins**
  (`AjarTimeHandler.Quit`, when the player stands in another fight's
  hall): MAP31 never needed it. Coming back to a fight that was left
  begins it again with what is still alive; not tested.
- **The generator refuses a monster in a wall, a pillar or another of its
  wave** (`Shop.room_for`): one that has no room never comes, and the
  fight is never won. The first build had five such.
- **Not here yet**: the level's own secret (the glass shows later: it
  needs MAP15's mirrors); a hint for the player who drops without hanging;
  a look; a `next` (it starts itself again until there is a MAP16).
  MAP15's secret way out leads here (`secretnext`).
- **Not tested**: any fight; a death in a fight with doors about (the
  rescue goes by `Leave`, so the doors should be put back the same way);
  the lock-up with real monsters after the player; the ways on foot after
  a fight is won in shops 1 and 3.

## MAP32: winding the fight that is watched (2026-11-19)

Vadim wanted MAP31's winding in MAP32 too, so that the wait in a box can be
cut short. `src/zscript/time.zs` (`Wind`, `WindWatch`, `WindWatched`,
`PuppetsAt`), `timedoor.zs` (`DoorWind`, `deTrip`), `tools/map_secret2.py`.
`MAP=MAP32 MODE=4 TIMEOUT=120 tools/smoke.sh "$PWD/build/smoke32w"`: 21
checks, all pass. **Not played by hand.**

- **Plates in every office**, two beside the glass on the box's own wall,
  back on the left of one who looks out and on on the right, as in MAP31:
  in the wing on its east wall 96 either side of the glass's middle, in
  the small offices by MAP31's formula. 18 in all. The generator refuses a
  plate with a thing within 40 of it, or a leaning door just in front of it.
  In shop 2 GREEN now leans 60 further from the wall (`wing(200, 270)`),
  or it stood between the back plate and the room (Claude's choice).
- **What a plate does**, from the box the player is in while the fight is
  watched: the fight goes half a minute back or on at once. Same price and
  refusals as MAP31: 10 health and 5 armour, not with 10 health or less. On
  goes no further than two seconds before the box's door opens (the door
  still opens only by the fight playing to that moment); back no further
  than the fight's start. "It ends here" / "It begins here" cost nothing.
- **What is seen** through the glass is the fight at that moment: every
  puppet as its last record up to then says (`PuppetsAt`; the same as
  playing it tic by tic, without the cost of a long fight in one tic). The
  hall's lights and screen are put as the show has them then. The real
  fight stands still as before; what came out after the player is where it
  is, out or still to come.
- **The doors**: on, every change up to then is done. Back, every door is
  put as at the fight's first tic and the changes up to then are done again.
- **What the player did in the box in this trip stays done** when the fight
  is wound back (Claude's choice): they are not wound, only the fight is.
  Every door change is written down with the trip it was made in; this
  trip's changes later than the moment wound to are moved to it, in their
  order. A door in the player's hands stays in their hands. The changes of
  the fight itself and of earlier trips are done again when their moment
  comes. So in shop 1 the twin hung in the wing still hangs after winding
  back, and the earlier self hangs its leaf again later, and the Pair joins.
- The player's own track in the box (what a later trip sees of them) stays
  as long as the fight shown: winding on adds tics in which nothing moved,
  winding back cuts it and writes down afresh what is in the box.
- **The test** (MODE=4): shop 1, its first go made long (the leaf is
  carried ten seconds before it is hung). Out, the twin hung in the wing;
  on: two seconds before the end, the leaf hangs, the Pair is joined and
  held, paid; on again: nothing; back: the start, the leaf leans where it
  did, the twin still hangs, paid; back again: nothing; refused at 10
  health; played on, the earlier self hangs the leaf again, the door opens
  and the Pair leads to the gallery.
- Still pass: `MAP=MAP32 MODE=3` (18, out by the line), `MAP=TDOOR` modes
  3, 4, 5 (20, 8, 7), `MAP=TIME MODE=3` (14), `MAP=MAP31 MODE=7`.
- **Not done**: winding while a door of the fight's own is in the player's
  hands past a moment an earlier self takes it (on: the replay takes it, as
  when played); the clock's "running back" for the first second after
  winding back to the start (the overlay shows it as at a step-out).

## MAP16 rebuilt after Vadim played it (2026-11-20)

`tools/map_institute6.py` written again; `src/zscript/map16.zs` (the
weighbridge and the tests), `enemies.zs` (the porter), `tools/solve.py`
(the porter and the lure in the solver), `tools/gfx.py` (glass, the CA wall
lever). **Not played by hand.**

**What Vadim found** in the first MAP16: too many keys and stores, and the
puzzle hid in them; the stair and its thief did not read. Agreed: keep the
Pair (the head's leaf fixed, the player's leaf loose), GREEN, RED, VIOLET
and the brass frame; drop keys 1 and 2, the strongroom, the cold store and
frame 105's stores.

**The level now**, MAP11's look, four floors, the well closed, each floor a
wing with its drop at the far end; the drops stay open:

- Top (384): the reading room (start, the leaf leans there) looks through
  glass into the sealed lobby: the head's TEAL frame, the weighbridge in
  front of it, and the heavy shutter to the test hall (brass frame,
  VIOLET only, the night room). The lobby's door to the reading room opens
  only from the lobby side (a bolt) and stays open.
- Labs (256): the hall cut east-west by a trench with bars (shots and sight
  pass, nobody crosses). GREEN in the south half; its frame in the south
  wall, its far side in the north wall. The drop to the canteen off the
  north half; a lab each side.
- Canteen (128): RED leans; its frame in the west wall, its far side on the
  gallery above. The gallery's lever opens the shutter to the base for
  good. Kitchen to the east. Secret: a panel in the gallery's west wall,
  the upper texture unpegged (the tell), opens on use; blue armour.
- Base (0): the boiler room and the foot (frame 104). The den is raised
  (40) behind bars with its own frame (105, TEAL only) and VIOLET. The staff
  stair into it: its top step is level with the den and 54 high, and the
  line at its foot blocks players; the porter (52) is the only thing that
  passes. The lower steps are open above so the porter sees down the
  stair (Claude's choice: with all four steps low it saw neither the
  foot nor the player). The hole (squeeze) to the cubby, whose doorway of
  the building's goes up to the lobby. The cubby is not secret.

**The porter** (a thief with args[2] = its frame): takes the TEAL leaf only,
hung or leaning, only while it sees the player, from any frame but its own;
always hangs it in the den's frame and never takes it from there; uses no
other door. With nothing to do it walks back to its post in a straight line
(Doom's chasing beside the hung leaf set it off the wrong way). Killed,
another comes out of the den 30 seconds later, every time; killed on its
stair or in the den with the leaf, the leaf is hung in the den's frame.
`CanReach` now also checks headroom.

**The nailer** comes when VIOLET is first taken, stays in the boiler room
(cannot climb into the den), nails what hangs at the foot. The porter
leaves a nailed leaf. The nails fall when the nailer dies.

**The weighbridge** (`AjarWeighbridge`, thing 20070): the first time the
player comes into the lobby a baron appears at the foot, on every skill;
20 seconds after it dies another comes, until the shutter is open. Anything
of a hell knight's mass or more on the plate opens the test hall's shutter
for good. The player's weight does not, and a message says it was built to
weigh something heavier. Only the first baron is in the tally.

**The way through** (the solver's, and the walkthrough's): a first trip
down empty-handed (GREEN, RED, the lever), up by the hole, the cubby and
the doorway to the lobby, open its door; the leaf down, hung at the foot,
up through it with the baron behind you onto the weighbridge; down again,
let the porter see you: it carries the leaf to the den, and the head now
opens into the den; up by the cubby, through the head into the den, VIOLET,
back through it to the lobby, the test hall, the brass frame.

Departures from the plan as briefed, and why:
- The first trip down cannot carry the leaf: one door at a time, and the
  labs have one frame, so GREEN must be hung first. Later trips are quick.
- "VIOLET to the lobby, then open the lobby door, take the leaf from the
  den" does not work: there is no frame in the lobby to set VIOLET down in,
  and a door is only put down in a frame. So the baron goes first (the
  leaf at the foot), then the porter carries the leaf to the den. With
  VIOLET parked at the foot instead, the nailer nails VIOLET there.
- The nailer is never needed: killing the porter gives 30 seconds.

**Solver**: 8 door actions, 3074 states, 0 stuck, nothing lost. What it
does not model: the porter's nails (its porter ignores the nailer; the
nailer is luck either way), the timing of a new porter (a dead porter is
back at once for it), the baron as a monster (it is a move: "through the
leaf at the foot, followed", needing the lobby once entered), the
weighbridge's other heavy monsters, and that the player alone on the plate
does nothing (there is no move for it).

**Monsters**: 148 at skill 3 (hp 17190), ammo x1.60 (about x1.51 with one
baron, which budget.py does not count); 78 at skill 1, x2.53. Knights only
in the base and the test hall. Ambushes: VIOLET (the nailer, revenants,
knights), TEAL (imps, sergeants), GREEN (spectres, imps), RED (spectres,
cacodemons).

**Checks**: mapcheck 306 sectors, 0 problems; thingcheck, itemcheck 0.
Smoke tests:
- `MAP=MAP16 tools/smoke.sh`: 41 checks, all pass, out by the brass frame.
- `MAP=MAP16 MODE=2 EXTRA=-nomonsters`: 17 views.
- `MAP=MAP16 MODE=3 TIMEOUT=260`: 13 checks, all pass: the porter carries
  the leaf from the foot to the den and stays in the base; leaves RED; a
  nailer nails the leaf at the foot while the player is away; the porter
  leaves the nailed leaf; the nails fall when the nailer dies; the player
  alone on the plate opens nothing; a baron comes to the foot, follows the
  player through the leaf onto the weighbridge, and the shutter opens; the
  porter killed, another comes out of the den.
- Still pass: `MAP=MAP15` modes 1 and 3 (24, 14, out by the line), `MAP=MAP32
  MODE=3` (10, out), `MAP=LAB` modes 1, 2, 3 (13, 9, 8). `MAP=MAP32 MODE=4`
  passes some runs and not others: its last check (`onTheGallery`, the
  player pushed through for 22 tics must stop short of y -192) lands
  anywhere from -35 to -206 from run to run with monsters about; on main
  too (-190 in one run). Not this change's, but worth making steady.

**Not done**: played by hand; how hard the base is with the baron and the
nailer at once; the den's look (dark, the bars) and whether the staff
stair reads as "only the porter".

## The plate lab: the sprung frame and the room of goes (built 2026-11-20)

A lab for the rebuilt MAP32 (the player working with their earlier selves
in one room): map `PLATE` (`tools/map_plate.py`), the engine piece in
`src/zscript/plate.zs`. No real level uses it yet; MAP31 and MAP32 are
untouched by it (their checks pass as before).

- **The sprung frame.** A plate on the floor (`AjarPlate`, editor number
  20044, `ajartime.plate(m, x, y, frame)`) names a frame by its id. A door
  hung in that frame is a door only while the plate is pressed: while the
  player or an earlier self (`AjarGhost`) stands within 28 of its middle,
  feet on the floor. Otherwise it is shut as a Pair's leaf hung alone is: its
  face on the frame's line and on its far side, both lines solid and
  blocking shots, hitscans and sight. Heard opening and shutting (the fast
  door's sounds, Claude's choice), and the plate clicks. Who stands in the
  doorway when it shuts is put 26 clear of the line, on the side they are on
  (`AjarHandler.StandClear`; the player only: ghosts walk through anything).
  Hooked into `Hang` (shut at once if the plate is not pressed) and `Unhang`
  (the lines are as any empty frame's); no plate, no change.
- **The room of goes.** An `AjarZone` of a hall with `args[4]` 2
  (`ajartime.zone(..., goes=True)`; documented in the header of `time.zs`).
  Built on the open fight's takes and ghosts (`AjarTake`, `RecordTake`,
  `PlayGhosts`), not on its demo: no monsters, never won by kills, no death
  rescue, no box limit. One box, number 1: every time door of the hall leads
  into it and it back by time door 1, open the whole time. Through a time
  door the player is in the box at the start of a new go, every time.
- **Doors done again.** Each go writes down what the player did to doors
  (took, hung, took down, left leaning) with the go's tic and how the door
  was found (`AjarGoLog`). At the start of every go every touched door is as
  at the first entry (a door in the player's hands then counts as leaning at
  time door 1). Each earlier self does its door actions again for real at
  their tic if the door is just then as it found it (leaning there, hanging
  in that frame, or in that self's own hands) and, to hang it, the frame is
  empty; if not, that action and its later ones on that door in this go are
  mimed. A take in the same tic as a hang (a swap) is done first. A door in
  a ghost's hands is hidden; when the ghost's go is over, what it holds is
  left leaning where it went.
- **Earlier goes that are over simply go** (Claude's choice): the ghost
  vanishes at its last tic, which is at the time door it went out by.
- **The room is over** when the player is outside its zones by a way that is
  not a time door: the time doors shut, ghosts gone (what they hold is left
  where they stood), and it is over for good (Claude's choice: it is marked
  won and does not begin again).
- **Begin anew**: a plate on the box's wall (`AjarAnew`, 20045,
  `ajartime.anew`; a ring that runs back to its start, pale blue) forgets
  every go; doors as at the first entry; the go that is on is the first.
- **The clock** at the top as the open fight's: this go's tic over the
  longest earlier go's length, while there is one.
- **The map**: the hall 512 square, time door in its west wall and the box
  (192 square) behind; sprung frame 101 in the north wall, RED leaning in
  the hall, its plate 312 from the mouth. RED's far side in the far room to
  the north, which is in the same zone as the hall. Sprung frame 102 in the
  far room's east wall, BLUE leaning there, its plate 352 from the mouth.
  BLUE's far side in the third room, outside the zone; its east end is the
  exit (a line to walk over).
- **Go 1 stands on the plate about six seconds** (o 60 to 272), not less:
  in go 2 the player walks through RED, hangs BLUE, stands on its plate and
  must come back through RED before the first self steps off.
- **Tests**: `MAP=PLATE MODE=3` (23 checks: alone, hung and shut, no walk
  and no shot through, opens with the plate, shuts again; go 1 out, in the
  box and open at once, doors as at the start; go 2 the earlier self hangs
  and holds RED, the player is put clear of the doorway when it lets go,
  through, BLUE hung and held, back through RED; go 3 two selves, through
  both, the room over and its time doors shut, out by the exit).
  `MAP=PLATE MODE=4` (6: the conflict rule mimed, six goes through the one
  box with five selves, begin anew forgets, one self in the go after).
- **Not done or not tested**: a Pair or a Stray door in a sprung frame; a
  monster or shot in a doorway when it shuts (only the player is put
  clear); doors carried into the room from outside after it began (they are
  reset as touched doors are); a hall with several time doors (all lead in,
  the box leads back by door 1); shooting in a room of goes (ghosts fire
  again what was fired, as in the open fight, untested). Not played by hand:
  `MAP=PLATE ./run.sh` in the worktree.

## The second goes lab: a won fight that stays, the press, two keys at once (built 2026-11-20)

Three more pieces for the rebuilt MAP32, on two lab maps: `PRESS`
(`tools/map_press.py`) and `TWOKEY` (`tools/map_twokey.py`); the engine in
`src/zscript/goes.zs` (its header has the contracts), hooks in `time.zs`,
`plate.zs` and `ajar.zs` (`Hang`, `SayHung`). No real level uses them yet:
MAP31, MAP32 and PLATE pass their checks as before.

- **A fight that becomes a room of goes.** An `AjarZone` of a hall with
  `args[4]` 3 (`ajartime.zone(..., mix=True)`; documented in the header of
  `time.zs`). Until it is won it is an open fight (boxes, ghosts whose shots
  are real, the last go's monsters on the demo, the rescue at death, winding
  if the map has plates), and besides: at the start of each go every touched
  door is as at the first entry, each go writes down what the player did to
  doors and presses (the room of goes' `AjarGoLog`), and the earlier selves
  do it again at their tics by the same rules (the conflict rule included);
  a ghost on a plate presses it. In the fight the door log replaces the
  stepping-out door record (`DoorWatch`): this kind of fight is never
  watched from a box. When it is won the steel door (sector tag 3090 + 100 *
  fight) opens as usual and the hall is a room of goes (`WonGoes` calls
  `BeginGoes`): its time doors lead into box 1, a go begins at the win, the
  hall as it is then (bodies, doors, what lies there) is the new first
  entry, the fight's ghosts and demo are gone. Begin anew forgets the goes
  since the win. Leaving its zones by a way that is not a time door ends it
  for good, as any room of goes.
- **Choices of mine there.** The press is not put up at the win itself (it
  finishes its stroke), only at the start of each later go. What earlier
  selves hold at the win is left leaning where they stand. Box 1 is not
  kept back from the spare boxes (it is spare only if the fight was won
  without stepping out, and the room of goes uses it anyway). After the win
  nobody is rescued (`bBuddha` off): the press kills the player for real
  there, as anything would in a room of goes. Killed in the fight while an
  earlier self is in the hall, the player goes on as it (the open fight's
  rule); what that self had still to do to doors and presses is dropped and
  what it held is left leaning where it stood (`MixGoOnAs`, not tested).
  Winding in such a fight (`MixWound`): the doors are as at the first entry
  with the earlier selves' door actions up to that moment done at once, and
  what the player did in this go is forgotten (not tested; PRESS has no
  winding plates). The messages say "as when the fight was won" in such a
  room (`goesWon`).
- **The press.** `AjarPress` (20046, `ajartime.press(m, x, y, tag)`): args[0]
  the sector tag of its area. `AjarPressSwitch` (20047,
  `ajartime.press_switch(m, x, y, angle, tag)`): a lever plate on a wall,
  args[0] the press's tag; USE sets it off if it is up ("The press is not up
  yet." otherwise). A warning (18 tics, the countdown beep), down in 16 tics,
  down 35, up in 70 (`WARN`, `DOWN`, `HOLD`, `RISE`), then ready again; the
  lever shows down while it works. Moved tic by tic with
  `Sector.MoveCeiling` (crush 0: things in the way are squeezed, not hurt,
  and do not stop it); bodies in the area are made `DontGib` first, so they
  are not ground to pulp. At the bottom and every tic while down, everything
  living in its sectors dies: awake monsters (damage with the player as the
  source, so the kill and the kill count are theirs), monsters on the demo
  (`Squashed`: the demo lets them go, as `Wake` does, and they are killed
  for real; the next go's demo has them die then), and the player (with
  the fight's `bBuddha`, they are then rescued by its rule). Ghosts are not
  hurt. Each go begins with every press up and ready (`PressesUp` in
  `Retake`, `Resume`, `NextGo`, `Anew`); a player's USE is written in the
  go log (`pTic`, `pTag`) and an earlier self's is done again at its tic if
  the press is up then (`GhostPresses`). Sounds (mine): the countdown beep
  to warn, the lift's start going down and up, the fast door's slam at the
  bottom, the lift's stop at the top. A dropped item under the press is
  destroyed by the engine (none in PRESS).
- **Two keys at once.** `AjarTogether` (20048, `ajartime.together(m, x, y,
  angle, frame)`): a small clock lamp on the wall beside a frame, args[0]
  the frame's id (a thing rather than a frame arg, so that there is
  something to see). A Pair whose leaves hang in two frames of which one or
  both have one is joined only if the leaves were hung within 70 tics of
  each other (`AjarDoor.hungAt`, set in `Hang`; `InTime`); else both are
  shut leaves. A leaf taken down and hung again is a new hanging; ghosts'
  hangings count (they hang through `Hang` too). While a leaf hangs alone in
  such a frame and its 70 tics are not up the lamps blink (every such lamp,
  so the far one shows it too) and that frame's lamp clicks every half
  second; joined in time the item pick-up chime and green lamps; too late
  the lift's stop, red lamps and "Too late: ..." (also when the time of a
  leaf hung alone runs out).
- **The maps.** PRESS: the hall 1024 by 768 entered from the way in to the
  south (outside the zones). Its north third (sector tag 3500, steel walls
  and ceiling) is the press; the switch is on the south wall at x 320. Ten
  monsters, all AjarCues of wave 1 (six demons, four imps, `always`), all
  outside the press. Time doors in the west and south walls; box 1 west and
  box 2 south, behind glass. Sprung frame 101 in the east wall, RED by it,
  its plate 324 from the mouth; RED's far side in a small room to the east
  (outside the zones), whose east end is the exit. The steel door is in the
  west wall, into a lobby that is in the hall's zone (harmless). TWOKEY: a
  room of goes shaped as an L (south arm 1152 by 320, north arm 320 by 768
  at its east end). Frame A (131) in the west wall, frame B (132) in the
  north wall, a lamp and a TEAL leaf by each; on foot about 1550 apart (the
  generator asserts over 1400: about 90 tics at a run; the brief's 900
  would be about 55). Time door south, the box behind it with the plate
  that forgets. The exit is a plain line in a nook off the north arm (the
  brief allowed it): the joined Pair is only the way across.
- **Tests.** `MAP=PRESS MODE=3` (13: begun, killedIntoTheBox,
  theyGoWhereTheyWent, pressCameDown, killsAreMine, killedOnTheDemo, won,
  clockDoorStays, steelOpens, afterTheWin, myEarlierSelfHoldsIt, through,
  levelExited). In the runs 4 to 6 of the 10 monsters were on the demo
  under the press and died. `killsAreMine` counts the press's own rise of
  the level's kill count and the player's: once a seventh kill came in the
  same second from elsewhere (most likely a death of the last go played on
  the demo: `Pose` calls `Die`, which counts it; MAP31 does the same, left
  alone). `MAP=PRESS MODE=4` (the switch is used at the first tic from 200
  on with nothing under it; 5: cameDownOnNothing, upAtTheStart,
  myEarlierSelfPressesIt, killedByThePress (under it while the first self
  is still in the hall: on as that self), upAtTheStartAgain). `MAP=TWOKEY
  MODE=3` (8: begun, itTicks, tooLateAlone, tookDown, forgotten,
  joinedWithMyself, throughThePair, tooLateTogether). The old ones pass as
  before (PLATE 3 and 4, TDOOR 3, 4 and 5, TIME 3, MAP32 3 and 4, MAP31 6
  and 7; MAP31 3 with only its known random `noneWakesAsIStepIn`).
- **Not done or not tested**: winding in such a fight, `MixGoOnAs` with
  doors in hand, a door carried in at the first entry, a monster that
  wakes on the demo under the press, the press over a frame or a door (a
  hung door's leaf is not hurt or moved), a press in a fight that is
  watched from a box (closed fights: it is not recorded for replay), several
  presses at once, a Pair whose leaves start hung in such frames, the exit
  behind the Pair. Not played by hand: `MAP=PRESS ./run.sh` and
  `MAP=TWOKEY ./run.sh` in the worktree.

## The third goes lab: the shutter, an earlier self's shots, killed in a room of goes, two rooms in a row, figures (built 2026-11-20)

Five more pieces for the rebuilt MAP32, on one lab map: `SHUT`
(`tools/map_shut.py`); the engine in `src/zscript/shut.zs` (its header has
the contracts), hooks in `time.zs`, `plate.zs`, `goes.zs` and `ajar.zs`,
helpers in `tools/ajartime.py`. No real level uses them yet: MAP31, MAP32
and the three earlier labs pass their checks as before.

- **The shutter.** `AjarShutter` (20049, `ajartime.shutter(m, a, b, out,
  floor, tag, high=96, keep=False)`): args[0] the sector tag of the
  shutter (a sector 16 deep in a wall opening, its ceiling at its floor
  while shut), args[1] how high it opens (0: 96); its angle points to the
  side it is worked from. A plate names it: an `AjarPlate` with args[1] the
  shutter's tag (`ajartime.shutter_plate`; args[0] stays a frame's id, so
  one plate could work both). Open only while such a plate is pressed (the
  player or an earlier self on it); shut, nothing passes it, no walker,
  shot or sight (a closed sector). Opens and shuts in 12 tics, the fast
  door's sounds (mine), moved tic by tic with `Sector.MoveCeiling` and no
  crushing (crush -1: something in its way stops it, and it waits). Shutting,
  it first puts the player clear of it on its worked side (the brief allowed
  either; mine: the player is put clear, anything else is waited for).
  `keep` makes its far line impassable (`blocking`: players and monsters)
  while shots and sight pass it: a pen behind a shutter is kept by that
  line, open or shut, and its monsters fight through it when it is open.
  Every go of a fight or a room of goes begins with every shutter shut at
  once and every shutter plate up (`ShuttersShut` in `Begin` of an open
  fight, `Retake`, `Resume`, `NextGo`, `Anew`, `BeginGoes` but not at the
  win, as the press). Not for a closed fight watched from a box (it is not
  recorded for replay).
- **An earlier self's shots, in a fight of goes** (`args[4]` 3, while it is
  a fight): `AjarRail.ModifyDamage` takes damage from an `AjarGhost` as from
  the player, so it hurts a monster on the demo and wakes it as the player's
  shot does (`Wake`: it is then after the player, and woken dead it is killed
  by the player). Kills: the engine already counts every monster death to
  the player in single play, so the player's kill count rises by each one;
  nothing more was needed. MAP31's open fights (`args[4]` 1) are untouched
  (`mixed` is false there).
- **Killed in a room of goes** (`args[4]` 2, and a fight of goes after its
  win): `GoesTick` keeps `bBuddha` on; at health 1 (`GoesKilled`) the
  player's shape goes to light where they fell (`AjarSnatch` and the
  teleport fog, as in the open fight), they are put in box 1 with 50 health
  and `NextGo` begins a new go (the ended go is kept: its earlier self
  vanishes where it fell), a red flash (mine: the open fight's colour for a
  death), "You were killed. Go n: ...", and they stand for a second
  (`STAND_TICS`). So the press after a win now puts the player in box 1.
- **Several rooms in one level.** Nothing new was needed in the engine:
  leaving a room of goes for good ends it (`EndGoes`: ghosts gone, logs and
  takes cleared, held doors left, its time doors shut, marked won), and
  walking into the next fight's zone begins it (`Begin`, `DoorBegin` takes
  stock of every door afresh, `MixBegin` a new log). The test checks that
  nothing of room A is left in room B. Two hall time doors in parts cut off
  from each other (room and pit) both lead into box 1, and the box back by
  door 1: tested. **A sprung frame made with `only`**: it did not work
  before. `only=1` frames are way-home frames (`args[1]` the door's far
  side), and hanging that door there ran `ComeHome`: the door was nailed
  and the level's way out marked built. Now a frame with a plate never
  comes home (`Hang`), and refusing another door it says "This frame takes
  the RED door and no other." The frame takes RED only, is shut, opens with
  its plate and is held by an earlier self.
- **Figures.** `AjarFigure` (20051, `ajartime.figure(m, x, y, what, kind=,
  angle=, scale=0.5, z=0)`): args[0] 1 the player standing (in the
  player's colours), 2 a body (args[1] a Doom editor number, by
  `AmbushClass`: the last picture of its Death state), 3 a plate pressed (a
  flat sprite), 4 a door of colour args[1] standing as hung (the door's own
  wall sprite and glow), 5 that door leaning (the same, tilted 10 degrees,
  mine: in the game a leaning door stands upright, so a model would not tell
  the two apart); args[2] the size in percent. No behaviour at all
  (`+NOINTERACTION`, no tick), not solid, not shootable, never counted, no
  weight on a plate (plates look only at the player and ghosts), and left
  out of `Counts`, `RecordFx` and `Snap`. `ajartime.case(m, a, b, out,
  floor, deep=96)` makes a glass case in a wall (the glass of
  `ajartime.glass` and a raised, lit case behind it) and returns its
  sector; `ajartime.sealed(m, sector)` says whether nothing can walk into
  it (every way out over a non-blocking line leads back into it); the map
  asserts it. Since 2026-11-20 (after Vadim played MAP32: a case did not
  read as the room later) more kinds: 7 the player mid-stride (`walking`,
  PLAY frame C), 8 the number args[1] of a go floating over a self's head
  (`go`, kind 1 to 3; `figure` puts it `GO_OVER` 34 up; an ivory digit
  outlined dark, sprite AJGN), 9 a door frame's face (`frame`, kind the
  colour: brass inlaid with it, 0 plain brass; sprite AJFM, a wall sprite at
  the door's scale, its opening 64 by 96 as the door's picture: stand it 2
  off the back wall and the `hung` door 2 in front of it), 10 the plaque
  (`plaque`, sprite AJPQ: ivory, a clock and the wind plate's two arrowheads
  pointing right, "later"). A plate figure is 0.75 by default and has a small
  warm light. `case` now frames the glass in the time door's ivory
  (AJTR10, AJTF10), makes the inside a piece of the room (`wall`, `ftex`,
  `ctex`, the room's own textures, by default AJWALL, AJFLOOR, AJCEIL; it was
  dark trim, AJTRIM, which is what made it a dark cell), lit 240, and puts
  the plaque over the glass, 2 off the wall, 24 over the head. The SHUT
  case has five figures with the plaque (`caseIsThere`).
- **The map.** Room A (fight 1, a room of goes): 640 square, the pit 256
  square in its north-east corner, 64 down; time door 1 in the west wall,
  time door 2 in the pit's east wall, the box west (with the plate that
  forgets). Sprung frame 101 in the north wall, `only` RED (brass inlaid
  red), RED leaning in the room, its plate 340 from the mouth. The glass
  case in the south wall: the player on a pressed plate, a dead imp and a
  dead hell knight, at half size. RED's far side is in the lobby of room B,
  west of the range. Room B (fight 2, a fight of goes): the range 384 by
  1100; the firing spot (1092, 80) at the south end, a pillar 64 square to
  its west for cover. At the north end the shutter (tag 3520, 256 wide) and
  the pen behind it, 288 by 100, level with the range, ceiling 128; four imps and two
  hell knights, AjarCues of wave 1. The booth east of the pen end (128 by
  200), entered from the range, glass onto it (`ajartime.glass`: it blocks
  sight too), the shutter's plate in it. Time doors in the west and east
  walls, boxes 1 and 2 south behind glass, the plate that forgets in box 1.
  The press (tag 3510, 128 square) in the middle of the range, its lever on
  the west wall. The steel door (3290) in the east wall, the exit room
  beyond it outside the fight's zones.
- **Tests.** `MAP=SHUT MODE=3` (20: caseIsThere, fromThePitToTheBox,
  outByDoorOne, onlyFrameHangsIt, opensWithItsPlate, heldByMyEarlierSelf,
  through, secondRoomBegins, shutWithoutThePlate, noShotThrough,
  opensWithThePlate, shutsAgain, killedIntoTheBox, shutAtTheStart,
  hurtThroughTheShutter, theyFireBack (a pen monster's missile came out
  past the shutter line while it was open), openWhileMyEarlierSelfStands,
  shutsWhenMyEarlierSelfLeaves, putClearOfIt (the player stands in the
  opening when the earlier self steps off), nothingWalksOut (every living
  monster still in the pen at the end of go 2)). The test fires rockets
  level (pitch 0, no autoaim), turned to face a monster in the pen
  (`ShootLevel`); it is given a rocket launcher and rockets. In go 2 three
  are fired, more would win the fight before the earlier self steps off; the
  ones they wake fire back at the player at the firing spot (3 to 4 missiles
  out in a run; godmode stays on, the check is the missile). `MAP=SHUT
  MODE=4` (7: rocketsStopped (go 1's sixteen rockets at the shut shutter
  hurt nothing), intoTheBox, myEarlierSelfHurtsThem, killsAreMine (checked
  at the first death: the earlier self's rockets killed all six in the runs
  before the test's own kills were due), won, steelOpens,
  pressPutsMeInTheBox). Each passed in three runs (MODE=3 20 of 20, MODE=4 7 of 7). The old
  ones as before: PRESS 3 (13) and 4 (5), TWOKEY 3 (8), PLATE 3 (23) and
  4 (6), TDOOR 3 (20), 4 (8 and the exit), TIME 3 (14), MAP32 3 (18 and
  out) and 4 (20), MAP31 7 (15), 6 (9) and 3 (all passed in the run).
  TDOOR 5 failed delivered, shutAway and outOfTheFight (once inTheBox too)
  in 2 of 9 runs on this branch, and passed 3 of 3 on the main package:
  the test's demon walks back out of the box into the hall. None of this
  lab's code runs in that closed fight, so it looks like chance (the
  demon's chase); left alone, worth watching.
- **The pen, first built 64 lower (as first asked), was changed** (Vadim,
  2026-11-20): sunk 64, its monsters could not see or shoot over the sill at
  anyone on the range (no missile came out in 400 tics open), and the
  player's level shots went over their heads. Now the pen is level and the
  shutter's far line keeps everything in.
- **Not done or not tested**: a monster or a body in the shutter's way (it
  waits: untested), several shutters, a shutter in a closed fight, a door
  figure in a case (the lab's case has none), `MixGoOnAs` and winding with
  shutters, a player killed in the box of a room of goes. Not played by
  hand: `MAP=SHUT ./run.sh` in the worktree.

## MAP32 rebuilt: five rooms where earlier selves work with you (built 2026-11-20)

Vadim played the first "Double Shift" and found that nothing in it needed
two of him and that its exit did not look like one. The new MAP32 is built
on the three goes labs (PLATE, PRESS and TWOKEY, SHUT). Same name, same place
(a works), plain textures, no look yet. `tools/map_secret2.py`, the tests in
`src/zscript/map32.zs`. **The old level is the lab map SHIFT**
(`tools/map_shift.py`, `src/zscript/shift.zs`, `MAP=SHIFT ./run.sh`); its two
tests pass as before (`MAP=SHIFT MODE=3`: 18 and out by the line; `MODE=4`:
20). `next` stays MAP16, MAP15's secret way out still leads here.

Five rooms in a row, each its own fight number with its own box 1 and plate
that forgets. A room is over for good when it is left by a way that is not a
time door, so every way on is one way: a sprung door that shuts behind, or a
drop of 96 whose fight zone starts 16 past the edge (a player on the ledge is
in no room, one below cannot climb back). Every frame of a puzzle takes its
own door and no other. Each room has a glass case where it is entered, with
figures of it solved. Each next room has a little health and ammunition at
its entrance. Nothing hurts in rooms 1, 2 and 5.

- **1, the plate** (room of goes; 640 by 512 at 0,0, the start in a nook to
  the south that is part of the room). Sprung frame 101 in the north wall,
  VIOLET only, VIOLET leaning, the plate 352 from the mouth; time door west,
  the box behind it. Case (north wall): the player on a pressed plate, VIOLET
  hanging. Hang it, stand on the plate, out by the time door; the next go
  walks through while the earlier self holds it. VIOLET's far side is in room 2.
- **2, two keys** (room of goes). A gallery 1280 by 320 (2000..3280, 0..320)
  and east of it a pit 512 by 896, 96 down. Frame A (131) in the gallery's
  west wall, frame B (132) in the pit's north wall, each with a clock lamp,
  both TEAL only, a leaf leaning by each; 1850 apart on foot (asserted over
  1400, and over two seconds at the fastest strafe-run, 1652). YELLOW leans
  in the pit; frame W (133) in the gallery's south wall takes YELLOW only. Time
  door 1 in the gallery's north wall (the box behind), time door 2 in the
  pit's east wall. The pit is left only by its time door or the joined Pair.
  Case: both leaves hung, both lamps green, YELLOW in W. Solution: go 1 hangs
  a in A at a moment and goes out by door 1; go 2 drops into the pit, hangs b
  in B within two seconds of it, takes YELLOW through B and out of A, hangs it
  in W and goes through. One body cannot: A then B is too late, and a door
  does not go through a time door, so YELLOW comes up only through the Pair.
- **3, the press** (fight of goes; the hall 1536 by 1280 at 5000,0, floor 0,
  ceiling 320; the north 512 is the press, three sectors, steel walls and a
  steel ceiling at 192, a trim floor). The lever on the south wall in the
  middle. Entered from YELLOW's far side, a ledge 96 over a lobby west of the
  hall. Four pillars in the south half. Time doors west, east and south,
  boxes behind glass west, east and south. Wave 1 (at the start): 6 barons,
  8 hell knights, 6 revenants, 4 mancubi, 10 imps, all in the south and
  middle; wave 2 (16 left): 2 arch-viles, 4 arachnotrons, 4 cacodemons; wave
  3 (8 left): 2 cyberdemons. Arch-viles and cyberdemons on every skill, the
  rest thinned as every AjarCue is. 27800 of health. Supplies: in the lobby a
  plasma rifle, a box of rockets, two stimpacks; box 1 armour, two medikits,
  a cell pack, rockets; box 2 armour, a medikit, a cell pack, rockets; box 3
  two medikits, a cell, rockets. Reckoned at 150 a rocket (a hit and some of
  its blast), 22 a cell, 70 a shell, 10 a bullet, that is 8720: 31 per cent
  of the health, asserted between 28 and 40 (what the player brings from
  MAP15 is not counted). The win opens the steel door (east wall): a corridor
  and a drop into room 4. Case (the lobby's north wall, a steel ceiling): the
  player at the lever, a baron, a revenant and a mancubus lying dead.
  Solution: a go as bait under the press, killed there or out by a time door;
  the next go at the lever while the monsters go where they went.
- **4, the range** (fight of goes; 512 by 1400 at 7200,0, floor -96, ceiling
  256 over it). Entered by a drop from the corridor into a lobby west of the
  range's south end. The shutter (384 wide, `keep`) in the north wall and the
  pen behind it, 768 by 320, level with the range: 2 arch-viles, 4 revenants,
  4 mancubi, 2 barons and a cyberdemon, AjarCues of wave 1 (arch-viles and
  the cyberdemon on every skill); the generator refuses one with no room. The
  booth east of the pen end (entered from the range, glass onto it), the
  shutter's plate in it. The firing spot (7456, 120) at the south end, a
  pillar either side for cover, clear of the line of fire. Time doors west
  and east; boxes 1 and 2 south, box 3 west, behind glass. Supplies in the
  corridor before the drop: a rocket launcher, a backpack, 10 boxes of
  rockets, 3 cell packs, 2 medikits: 14400 against the pen's 11000 (asserted
  over 1.2 times; the cyberdemon takes no blast, so it is less than it looks).
  Boxes: armour, medikit, rockets; armour, medikit, cell pack; two medikits,
  rockets. Case (the range's east wall, seen from the way in): the player on
  the plate, another player, a dead cyberdemon and mancubus. Solutions: hold
  the shutter in one go and shoot from the spot in the next, or shoot at the
  shut shutter in one go and hold it in the next.
- **5, the airlock** (room of goes, floor -192). Entered by a drop from the
  corridor into S (8048..8560, 160..672). F1 (141, GREEN only) in S's east
  wall, GREEN's far side in L's west wall (L 8800..9248); F2 (142, PINK only)
  in L's east wall, PINK's far side in E's south wall (E 9600..10112,
  160..608). GREEN leans in S and its plate is in S (414 from F1); PINK leans
  in L and its plate is in L (358 from F2); BLUE leans in S. In E the two
  brass frames face each other across it, west (RED only, RED hung from the
  start) and east (BLUE only); the night room (`way_through`) is north of E,
  96 up, a hole in its south wall drops back into E. Time doors in the south
  walls of S (door 1, the box south of it), L and E; E needs one, as it can
  be entered without BLUE. Case (S's east wall): BLUE and RED facing each
  other, a player on each plate. Solution, three goes: hang GREEN and stand
  on its plate, out by door 1; through F1, hang PINK and stand on its plate,
  out by L's door; take BLUE, through both, hang it opposite RED, walk the
  chain. With two bodies one plate is always left empty.
- **No dead end, asserted**: each room declares the regions a player can
  stand in, the ways on foot between them that need no earlier self, and its
  time doors (`ajartime.on_foot`); each region must reach a time door (or the
  box, which leads to one), and every sector of the room bigger than 64 by 64
  must lie in a region (`ajartime.covers`; the cases and the pen are
  exempt). Besides: every monster has room (`ajartime.Crowd`), the plates'
  distances, the walk from A to B, every case sealed, the supplies.
- **New in the engine, small**: `AjarFrame` args[4] 5, a plain frame that
  takes one door and is no way out (W; with args[4] 1 hanging that door ran
  `ComeHome`); a brass frame with `only` says which door it takes; a figure
  of a clock lamp lit green (`AjarFigure` args[0] 6, `figure(..., "lamp")`).
  The level's helpers in `tools/ajartime.py` (`Crowd`, `toughness`,
  `firepower`, `walk`, `on_foot`, `covers`). After MAP32's walk-through the
  test switches itself off, so MAP16 is not played as a test after it.
- **Choices of mine**: room 1's door is VIOLET, not RED (RED is in the chain,
  and a colour has one far side); F2's door is PINK (the six plain colours
  are all used: VIOLET, YELLOW, GREEN, PINK, BLUE, RED); the frames that take
  one door have brass inlaid with its colour, the chain's too; every size,
  coordinate and supply above; waves 2 and 3 at 16 and 8 left; room 4 has two
  time doors; the start nook is part of room 1; the night room is part of
  room 5 (out of it, a player who went through RED alone would end the room).
- **Tests.** `MAP=MAP32 MODE=3 TIMEOUT=300 tools/smoke.sh` (40 checks):
  begun1, allThere, shutAlone1, opensWithThePlate1, heldByMyEarlierSelf1,
  through1; noLeak2, itTicks2, tooLateAlone2, pitDoorToTheBox2, forgotten2
  (begin anew after the late try), joined2, yellowUp2, hungInW2, on2;
  begun3, noLeak3, killedIntoTheBox3, pressKills3, won3, steel3; begun4,
  noLeak4, shutWithoutThePlate4, opensWithThePlate4, killedIntoTheBox4,
  heldByMyEarlierSelf4, hurtThroughTheShutter4, theyFireBack4, won4, steel4;
  begun5, noLeak5, onlyItsPlate5, outByDoorOne5, through5a,
  twoEarlierSelves5, through5b, chainClosed5, levelExited. Godmode; room 3's
  bait stands under the press until six are under it, the press came down on
  5 to 8 monsters on the demo in the runs, the rest are killed by the script;
  in room 4 twelve rockets go through the held shutter, then the rest by the
  script. `pressKills3` allows the player's kill count to rise by one more
  than the press killed in those tics (a death the demo plays, as the PRESS
  lab found). `MAP=MAP32 MODE=4` (7: onlyItsOwnDoor (VIOLET carried into room
  2 is refused by W, A and B), inThePit, pitDoorToTheBox, outOfThePit,
  shutInTheLock, lockDoorToTheBox, outOfTheLock). `MAP=MAP32 MODE=2`: views
  for screenshots (BLUE is hung before the last two). On 2026-11-20 MODE=3
  passed 40 of 40 three times running, MODE=4 7 of 7 three times; the labs
  as before (SHIFT 3 and 4, SHUT, PRESS 4, PLATE, TWOKEY, TDOOR, TIME,
  MAP31 7).
- **Not tested**: any fight as fought (the test is in godmode, its kills are
  the script's), the other solution of room 4 (shooting the shut shutter
  first), a player in E with F2 shut, winding (no wind plates), the press
  killing the player after room 3 is won (it is then a room of goes: into box
  1), death in rooms 3 and 4 beyond the rescue the tests use, skills other
  than the default. The numbers of monsters and supplies are a first guess.
  **Not played by hand**: `MAP=MAP32 ./run.sh` in the worktree.
- **The cases, restaged (2026-11-20).** Vadim found room 1's case did not
  read as the room later: a dark box, one self staring out, a door standing
  free. Now every case is framed in ivory with the clock plaque over it
  ("later"), and inside is a piece of its room, as bright (room 3's: the
  press's steel walls and ceiling). Every self has its go's number over its
  head. Room 1: VIOLET hung in its frame (brass inlaid violet) against the
  back wall, self 2 walking into it with its back to the room, and to one
  side self 1 on the pressed plate, turned to the door: the first you holds
  the door, the second walks through. Room 3: the self at the lever is 2.
  Room 4: the self on the plate 1, the one at the firing spot 2. Room 5: the
  selves on the plates 1 and 2. Room 2 as it was. `MAP=MAP32 MODE=2` takes a
  close view of each case (about 150 from the glass, looking 10 up; room
  4's from south of the pillar before it) and room 1's from across the room
  (150, 60): 17 views. `begun1` now counts 37 figures (the five plaques and
  the new ones), not 23; SHUT's `caseIsThere` 5, not 4.

- Rooms 3 and 4 can be begun anew: see "Begin anew in a fight" below.
- Room 3 is rebuilt as a chamber after Vadim played it: see "MAP32 room 3: the press as a chamber" at the end.
- Room 3 is rebuilt again, as two shifts (the bait fights in the chamber, the next self fights through a guarded wing to the lever): see "MAP32 room 3: two shifts" at the end.
- Room 3 gets plates in the chamber that work the wing (a screen before the guards, a cage), guards that wake for whoever comes into the wing, and a timetable (amber lamps, a bar under the clock): see "MAP32 room 3: plates in the fight, and the timetable" at the end.
- Room 4 is rebuilt around two keys under fire (two key levers in two guarded wings, pulled within two seconds of each other by two selves, open the pen's shutter for half a minute; the booth and its plate are gone): see "MAP32 room 4: two keys under fire" at the end.
- Room 2's Pair stays joined three seconds only, and the pit is longer, YELLOW at its far end (three selves are needed now): see "MAP32 room 2: the Pair shuts again" at the end.

## Begin anew in a fight (built 2026-11-20)

Vadim played room 4 of MAP32, spent its three boxes without killing the pen
and was left alive in a fight that could not be won: the shutter's plate is
behind glass, the time doors were shut, and the only way on was to die and
play the level again from room 1. Room 3 had the same three-box rule. Now
spending a fight's boxes costs the room, never the level.

- **The rule.** A fight with a begin-anew plate in its hall can be put back,
  at any time while it is on and not won, as it was when the player first
  came in: every monster as at the start (the living and the bodies gone,
  every wave's cues ready, wave 1 comes again), every pick-up of the fight's
  zones (hall, lobby, boxes) where it lay (those taken come back, none is
  doubled, what monsters dropped is gone), the player's health, armour,
  weapons and ammunition as they were then, the player where they stood
  then, facing as then, standing still; every box unused, every take, log,
  earlier self and demo forgotten, the doors as at the first entry, the
  presses up, the shutters shut. The level's kill and item counts are as
  they were then (the kill total does not grow by it). A blue flash and the
  teleport's sound; "The fight begins anew: it is as when you first came
  in. All its boxes are unused." Nothing gained in the fight survives it.
- **Death after the last box** in such a fight does the same, with a red
  flash: "You were killed, and no box is left. The fight begins anew: it is
  as when you first came in." It comes before the spare boxes of earlier
  fights (on MAP32 a spare box of room 3 would put the player back into a
  room that is over). Going on as an earlier self still comes first. A
  fight with no such plate (MAP31, the labs) is as before: with no box left
  the show is over and the level begins again. The last box's message in
  such a fight says the plate begins it anew instead of "death is death".
- **Once the fight is won** the plate is the room of goes' begin-anew plate
  (`Anew`, plate.zs): every go since the win is forgotten. A fight is never
  un-won.
- **The thing.** `AjarFightAnew` (src/zscript/anew.zs, editor number 20052;
  `ajartime.fight_anew(m, k, x, y, angle, z=16)`), a new actor, not an
  argument of `AjarAnew` (the tests find the boxes' plates by class). Its
  fight is the zone it stands in. 56 by 56, its foot 16 over the floor, the
  boxes' begin-anew picture (AJAN) twice as big in a wide lit frame, bright,
  pulsing slowly between two frames (AJAF, `gfx_time.fight_anew`).
- **How it is built.** `Begin` keeps the first entry (`KeepFirst`, an
  `AjarFirstEntry`) for an open fight: the player's position, angle, pitch,
  health, armour (every field of BasicArmor), weapons, ammunition (amount
  and maximum: a backpack's) and powers, the weapon in hand, the player's
  and the level's kill and item counts, and every pick-up lying in the
  fight's zones (the thing, its class, place and angle). A fight begun anew
  keeps its first first entry. `FightAnew` then does what exists: it shuts
  every box door, `FirstDoors`, `ClearHall` (and `ClearBoxes`: bodies, shots
  and dropped things left in the boxes), `PressesUp`, `ShuttersShut`; puts
  the pick-ups back (`PickupsBack`: one that lies untaken stays, one taken
  is spawned again, anything else in the zones is removed) and the player
  (`PlayerBack`); sets the counts; drops what the reel kept of the fight;
  and calls `Begin` again, which forgets the takes, ghosts, demo, logs and
  trips and opens the hall's doors onto box 1. Rescue calls it where it
  would have ended the level (time.zs, one line).
- **MAP32.** Room 3's plate on the lobby's west wall (4746, 192), to the
  left of the way down from the ledge; room 4's on the lobby's north wall
  (6960, 318), to the left of the drop from the corridor. Both away from the
  monsters' line of fire. Room 4's box 1 keeps its plate that forgets.
  Room 3's first entry holds 19 pick-ups, not 17: the hall's zone (grown by
  72) takes in the corridor's first two things beyond the steel door, which
  cannot be reached before the win and so are never changed.
- **No dead end, asserted**: `ajartime.fight_anew_reached(m, {3: "room 3",
  4: "room 4"})` asserts that every fight of goes (`zone(mix=True)`) has such
  a plate and that from every region of its room declared to `on_foot` the
  plate's region is reached on foot, without an earlier self. (`on_foot`
  keeps each room's regions and ways in `ajartime.GRAPHS`.)
- **Tests.** `MAP=MAP32 MODE=5 TIMEOUT=200 tools/smoke.sh` (22 checks, 11
  a room): rooms 3 and 4, each entered at its lobby by the script (the room
  before is left and over): firstKept, killedIntoTheBox (after go 1 took
  the lobby's plasma rifle and rockets in room 3, or was given a rocket
  launcher in room 4, and killed two monsters), pickedUp (box 1's three
  things), plateThere, asAtTheFirstEntry (the plate used from the hall in
  go 2: one go, no trips, no earlier selves, no demo, the hall's door open
  onto box 1 and the boxes' shut, every pick-up where it lay and no more,
  the inventory, health, place and angle, the kill counts, no bodies),
  monstersAsAtFirst (wave 1 in again: as many monsters as at the first
  entry, and the level's total as then), everyBoxUsed (killed in each box,
  then out in the hall), killedAfterTheLastBox (as at the first entry, the
  level not ended), wonAfterAnew and steelAfterAnew (killed to the end by
  the script: the steel door opens), wonStaysWon (the plate then forgets
  the goes since the win). `MAP=MAP32 MODE=6`: views of the two plates as
  the player comes in and close (`smoke_MAP32_6.cfg`). `MAP=MAP31 MODE=5`
  (the show is over with no plate) passes as before.
- **Not restored or not tested**: a power's time left (one had then comes
  back fresh, one taken since is removed; there are none in rooms 3 and 4);
  keys, doors carried in from outside the fight, things not pick-ups;
  decals and blood on the walls; the player's pitch and the weapon in hand
  are set but not checked; a monster that had wandered
  out of the fight's zones is not put back (none can on MAP32: the ways out
  are shut); the plate used while in a box (it is in the hall); death after
  the last box while an earlier self still fights (the existing rule: go on
  as it). **Not played by hand.**

## Idea for maps 20 to 30: one map, two halves, two of you (Vadim, 2026-11-20; a note, nothing built or checked)

Like MAP32, but the whole map is the room of goes.

- The map has two halves. In the first go you play one half to its end.
- Then you begin again from the start, and play the other half while your
  earlier self plays the first beside you, in parallel.
- Mostly the two halves are apart: two parts of one map. In some places they
  cross, and there the two of you can be in the same fight.
- At the end something happens that is at the same moment for both, and the
  two of you must do something together, at once, to open the exit.

Not decided: how the halves are told apart and which is played first, what
the crossing fights are, what the thing done together is, what happens when
the second go spoils what the first one did. No checks asked for yet.

## Idea: one-sided portals (Vadim, 2026-11-20; a note, nothing built or checked)

Not for any particular map. Vadim: a portal that is one-sided. From one side
of an opening you simply see the normal neighbour room; from the other side
you see another place.

What follows is Claude's reading of it, to be agreed.

- **The rule it could be**: a doorway has two faces, and each face leads to
  its own place. An ordinary doorway is the case where the two agree.
- **What it gives in play.**
  - The turn-round: from A into B, look back, and the doorway shows C. Strong
    once; it needs one of the others to last.
  - Doorways with a direction: where you can get to depends on which side you
    come from (the only way into C is to walk into B and turn back). Route
    puzzles; a carried door hung in such a frame is a further twist.
  - One-way sight in a fight: from your side you see the monsters and can
    shoot them; they look at the same opening and see another room, so they
    do not see you. The map can turn it against the player as well.
  - Impossible shapes: a corridor longer going back than coming, a room bigger
    inside than its walls allow.
- **What would spoil it.** No visible rule: each face needs a sign of where it
  leads, as the clock marks a time door and brass a way home (a lintel colour
  per face, say). The automap, which would show A beside B while the doorway
  leads to C.
- **The engine**: an expectation, not tested. The game's portals are GZDoom
  line portals (`ajarmap.recess`, `Line_SetPortal`), and each belongs to one
  face of one line, so one-sided is their nature. Not known: a portal on a
  line between two real rooms (today every portal line has only a stub sector
  behind it), and what shots, sound and monsters' sight do across it. A small
  lab map would settle it.
- **Where first** (Claude's suggestion): a secret or one puzzle room in a
  normal level; the one-way sight in a fight once the rule is understood.

## MAP32 room 3: the press as a chamber (built 2026-11-20)

Vadim played room 3 and found three things. The monsters did not all come for
him: most kept fighting each other. When few were left he could lead them
under the press himself, run round and pull the lever alone: nothing made it
a job for an earlier self. When the arch-viles came there was nowhere to
hide. Now the press is a chamber with one way in, the bait waits in a cell
behind glass where nothing reaches it, the lever is in a booth that only an
earlier self can open, and the hall has cover.

- **No infighting in rooms 3 and 4.** The monsters of these two fights never
  turn on each other. An AjarCue with args[4] 1 makes its fight calm
  (`ajartime.cue(calm=True)`, `Crowd(calm=True)`): each monster of a calm
  fight gets NOINFIGHTING as it comes, live (`Cues`) or on the demo, and again
  when an arch-vile raises it (the engine gives a raised monster its default
  flags back; `AjarTimeHandler.Calm`, `WorldThingRevived`, time.zs). Other
  maps and fights are as before (their cues have args[4] 0).
- **The chamber.** The hall is 1536 by 768 (5000..6536, 0..768). North of it
  a solid wall 32 thick, and behind that the press: three sectors
  (5000..6536, 800..1280) with the press's tag, steel walls, a steel ceiling
  at 192. The one way in is the mouth in the middle of the wall, 192 wide
  (5672..5864, 768..800). The mouth is part of the press (a fourth sector with
  its tag): whatever stands in it with its middle there when the press comes
  down dies; one with its middle in the hall is clear of it and is only
  squeezed for the second the press is down, as the press does to anything
  half under it. Asserted: the mouth is wider than the widest monster of the
  fight (the arachnotron, 128) by 32, and every kind is lower than its
  ceiling (`ajartime.HEIGHT`).
- **The bait's cell.** Behind the chamber's north wall (16 thick, 1280..1296)
  a cell 256 by 96 (5672..5928, 1296..1392), plain walls, lit 230, ceiling
  128, not part of the press. Its front is a window of `ajartime.glass` from
  5736 to 5928 (no sill: nothing passes it, no walker, shot or sight), so the
  cell is seen from the mouth, lit, behind glass. The only way in is a
  squeeze (`ajarmap.squeeze`, 48 wide, 64 high, monsters blocked by its line,
  flying ones too) at 5672..5720 beside the glass. The squeeze's line id
  (500) only stops a player who carries a door (`AjarHandler.Squeeze`); no
  door is carried in room 3. The plate (5880, 1344) is behind the glass, out
  of line with the squeeze, with a warm point light on it. It holds the
  booth's shutter open (`shutter_plate`, tag 3535). Time door 3 is in the
  cell's east wall (5928, 1312..1376), by the plate; it was in the hall's
  south wall. Doors 1 and 2 stay in the west and east walls, three boxes as
  before. Asserted in the generator: a self on the plate is wholly in the
  cell, and no point of the hall, the mouth or the chamber (a grid of 32) has
  a clear line to the plate's middle, the walls and the glass as segments
  (the slabs left out, which only makes it harder). So the bait on the plate
  is seen by the player at the mouth and by the monsters, who come for it,
  but nothing reaches it or sees it from where it can shoot: they crowd
  against the glass under the press.
- **The lever's booth.** In the middle of the hall's south wall, 176 wide and
  96 deep (5704..5880, -112..-16), steel inside, lit 230. Its front is a
  shutter (5704..5832, 16 thick, not `keep`) and beside it a slit of glass
  48 wide (5832..5880), through which the lever on the back wall (5848, -110)
  is seen from the hall. The shutter is open only while someone stands on
  the cell's plate, so the player alone can never be the bait and at the
  lever: the walk from the plate through the squeeze and the mouth to the
  lever is far over 600 (asserted), the shutter shuts in 12 tics. An earlier
  self's time on the plate is played again, so in the next go the booth
  stands open as long as that self stood there. A player in the booth when
  it shuts is put out into the hall before the opening, as one in the
  shutter's way always was (`ajartime.shutter(behind=True)`, AjarShutter
  args[2] 1: the sector right behind it is a booth that `Clear` empties too).
- **Cover.** The four 64-square pillars are now four slabs 192 by 64, long
  side east-west, full height: (5160..5352, 160..224), (6184..6376,
  160..224), (5480..5672, 320..384), (5864..6056, 320..384). Each is 160 or
  more from every wall and from the others, and the place 40 south of its
  middle is out of sight of the mouth and of the hall's middle (asserted by
  a line test in the generator). Six monster spots moved off them (two imps
  40 south, two mancubi 60 north, two arachnotrons 20 south); nothing else
  moved.
- **The case** (lobby's north wall, steel as before): self 1 on a pressed
  plate with a revenant, a mancubus and a baron lying round it, and apart at
  the east end self 2 facing the side wall, where a new figure, "lever" (the
  press's switch set off, `AjarFigure` args[0] 11), hangs. `begun1` counts 41
  figures, not 37.
- **Unchanged**: the waves and their numbers, the supplies and the boxes'
  stock, the lobby, the begin-anew plate, the steel door and the corridor.
  The generator's checks hold for the new shape: `on_foot` has the chamber,
  the cell and the booth as regions (hall and chamber both ways, chamber and
  cell both ways, the booth to the hall only: in needs an earlier self),
  `covers`, `fight_anew_reached`, `Crowd` (the hall and the chamber as
  floors, the slabs as solid, no spot in the cell), the firepower, every case
  sealed.
- **Tests.** `MAP=MAP32 MODE=3 TIMEOUT=400` now plays the new solution in
  room 3. Go 1: `noInfighting3` (every living monster of the fight has the
  flag; two of two kinds each hurt by the other do not turn on each other,
  and one with the flag taken off for a moment does), `boothShutAlone3` (a
  trace from before the shutter hits it at its face, the lever out of reach,
  the press up); then the bait walks through the mouth and the squeeze to the
  plate and waits there, without godmode, until twelve are under the press
  (or 700 tics), and at least 150 tics after the first monster came within
  200 of the glass. `safeInTheCell3`: from that moment its health never fell,
  and no monster was ever in the cell. It leaves by the cell's time door
  (`outByTheCellDoor3`, in place of `killedIntoTheBox3`: the go did not end in
  death). Go 2: `boothOpenForMyEarlierSelf3`, into the booth, the lever when
  ten on the demo are under the press (`pressKills3`), and when the earlier
  self's time on the plate is over the shutter shuts and the player is put
  out into the hall and walks on (`notStuckInTheBooth3`). 45 checks.
  `MAP=MAP32 MODE=5`: room 3's go 2 stands on the cell's plate before it uses
  the begin-anew plate, and `boothShutAnew3` checks the shutter shut again
  and the plate up (23 checks). `MAP=MAP32 MODE=2`: 23 views; room 3's are the
  hall from the lobby, the mouth from the hall, the chamber from the mouth
  (the glass and the squeeze), the cell from outside the squeeze, inside the
  cell, the booth shut (the lever through the slit), the booth open (a bare
  AjarGhost stands on the plate for it).
- **Not tested**: the fight as fought (godmode but for the wait in the cell,
  the script's kills); arch-viles raising monsters (the flag is set again
  then, but no test raises one); a monster shut in the booth; hiding behind
  the slabs from arch-viles. The numbers are a first guess, to be tuned after
  Vadim plays. **Not played by hand.**

## MAP32 room 3: two shifts (built 2026-11-20)

Vadim played room 3 as a chamber and found it dull: go 1 stood on a plate in a
safe cell behind glass, go 2 stood in a booth and waited to pull the lever.
Now each self has a shift of real work. The bait is in danger in the chamber
and buys time by staying alive under the press; the next self has that time
to fight through a guarded wing to the lever, pulls it, and then is itself the
bait for the self after it.

- **The chamber is where the bait fights.** The cell, its glass, its squeeze,
  its plate and light, the booth, its shutter and slit are gone, with their
  asserts. The chamber (5000..6536, 800..1280) and its mouth are the press as
  before. In it two full-height slabs of no tag, (5320..5448, 1008..1072) and
  (6088..6216, 1008..1072): the press does not come down on them (asserted
  160 or more from every wall and from the mouth). Time doors 3 (east wall)
  and 4 (west wall) are in the chamber, at y 1008..1072. Doors 1 and 2 stay
  in the hall's west and east walls; the three boxes as before.
- **A time door that is out only** (time.zs, its header). args[4] 1 on a
  hall's time door line (`ajartime.hall_door(out_only=True)`). Leaving by it,
  or killed nearest to it, the player goes out by it as by any, and the take
  keeps it (an earlier self killed there still runs to it), but the next
  box opens onto the hall's time door 1. The three places that took the
  nearest door (`Retake`, `Leave` of a closed fight, and the spare-box path
  of the rescue) now go through `NearestDoor` and `ComeOutBy`; with no such
  door, `ComeOutBy` gives back the door left by, as before. Doors 3 and 4 are
  out only, so the next self never steps out into the crowd in the chamber.
- **The wing's shutter** (shut.zs, its header). `AjarShutter` args[3] a
  sector tag (`ajartime.shutter(under=)`): the shutter is open also while the
  player (alive) or an earlier self (`AjarGhost`) is in a sector with that tag,
  by where its middle is; with no plate naming it, only then. Room 3's shutter
  (tag 3535) takes the press's tag 3530, so it is open while someone is in the
  chamber or the mouth, and shut at the start of every go as every shutter. It
  is worked from the hall: a player in its way when it shuts is put out into
  the hall. Its face line stops monsters (walking and flying), not players,
  shots or sight (`nomonsters`). Beside it on the hall's wall a lamp,
  `AjarShutLamp` (20053, `ajartime.shut_lamp`), the clock lamp's pictures:
  red while the shutter is not open, green while it is. The first time it
  opens because the player stepped under the press: "A shutter in the hall is
  open while someone is under the press." (once a level, my choice). The walk
  from the nearest point under the press to the shutter is 873 (asserted over
  600; it shuts in 12 tics).
- **The wing, "the tool room"**, south of the hall, all of it the fight's hall
  (a zone of its own, besides the hall's). The shutter in the hall's south
  wall at x 5128..5256; behind it the landing at floor 0 (5112..5272,
  -176..-16); the stairs east, six steps of 16, 32 deep (5272..5464); the upper
  room at 96 (5464..5880, -176..-16); the wing's ceiling at 224 throughout. The
  window in the upper room's north wall onto the hall (5704..5832), open, its
  sill at the upper room's floor, 96 high: the wing's only way out when the
  shutter is shut, a drop of 96, no way back. Its lines stop monsters as the
  shutter's face does. From its middle the mouth is seen between the hall's
  two middle slabs (asserted: no slab cuts the line). The lever (5856, -18) on
  the upper room's north wall just east of the window. The pen (5464..5880,
  -432..-176), same floor, along the upper room's whole south side, open to it
  over a line of bars (AJGRIL, the grille texture): `blocking` (nobody walks
  across), shots and sight pass. A cell pack and a medikit on the landing.
- **What the pen sees, and a move of mine.** As laid out (stairs the whole
  width of the landing) the pen saw the landing at a grazing angle from its
  far east end, over the top step. So the stairs are 80 wide, along the north
  wall (y -96..-16); south of them is wall. The generator now has a sight test
  in 2.5D (`ajartime.seen`: the wing's floors and ceilings as boxes, a
  monster's eye 42 or 48 over the pen's floor, a player's feet, middle and
  head) and asserts: the pen does not see the landing at all, nor the first
  step; the second and third steps are seen from no more than a fifth of the
  pen (by the bars, at its east end); the top two from most of it; the pen
  sees the upper room, the lever and the window. So the top of the stairs is
  where the player fights from, the landing is safe.
- **The guards**, AjarCues of fight 3 (calm) standing in the pen: with wave 1
  two hell knights at the bars, with wave 2 two revenants and a mancubus at
  its back, with wave 3 an arch-vile (`always`) in the middle and two hell
  knights at the back. All eight spots clear of each other across waves
  (asserted: an earlier wave's may still be there). The waves' thresholds are
  as before (16 and 8 left, or on the clock), so the guards count among those
  left. No hall monster gets into the wing.
- **Supplies.** With the guards (3900 more health, 31700 in all) the lobby's
  and the boxes' ammunition alone was 27.5 per cent, under the asserted 28:
  the landing's cell pack makes it 10920, 34 per cent.
- **The case** in the lobby: self 1 standing among the three bodies, no plate
  under it; self 2 at the lever as before. `begun1` counts 40 figures, not 41.
- **Generator checks**: `on_foot` has the wing as a region with a one-way link
  to the hall (the window; the hall to the wing needs someone under the press,
  of use only as an earlier self, so it is left out), the chamber with doors 3
  and 4 as its time doors; `covers` exempts the pen; `Crowd` has the pen as a
  floor and the chamber's slabs as solid; `fight_anew_reached`, the firepower,
  every case sealed. The old "a monster on the lever" assert is dropped.
- **Unchanged**: the hall, its four slabs, the hall's waves, their numbers and
  thresholds, the lobby and its supplies, the boxes, the begin-anew plate, the
  steel door and the corridor, no infighting.
- **How it is meant to play.** Go 1: into the chamber, the horde after you
  through the mouth; stay alive among its slabs as long as you dare; out by
  door 3 or 4, or killed. Go 2: out of the box by door 1, across the hall past
  the horde (on the demo it goes where it went), through the open shutter, up
  the stairs, kill or pass the guards, pull the lever while the earlier self is
  still drawing them under the press; the shutter shuts when that self is gone
  (a pull after that still kills what is still under the press). Then out by
  the window and into the chamber as the next bait.
- **Tests.** `MAP=MAP32 MODE=3 TIMEOUT=750 tools/smoke.sh` (54 checks; the
  run is now about 5000 tics, `smoke_MAP32_3.cfg` waits 4970, it waited
  3970). Room 3's are begun3, noLeak3, noInfighting3; go 1: shutAlone3 (alone
  in the hall: a trace from before the shutter hits its face, the lamp red,
  the press up, nothing said yet), opensUnderThePress3 (standing in the mouth:
  open, green, the message said), shutsWhenIStepOut3; then the bait stands by
  door 3 in the chamber (godmode as everywhere in this test) until twelve are
  under the press and a second more, or 900 tics, and walks out by door 3.
  Go 2: outByDoorThree3 (the take's door is 3, the box opens onto door 1),
  outByDoorOne3 (walked out of box 1: in the hall by door 1, not in the
  chamber), openForMyEarlierSelf3 (open and green, an earlier self under the
  press, the player not), upTheStairs3, guardsInThePen3, pressKills3 (as
  before: the lever pulled when ten on the demo are under the press, or at the
  tic go 1 had twelve), shutBehindMe3 (the earlier self's time over: shut, red,
  the player in the upper room), outByTheWindow3 (down in the hall),
  noWayBack3 (walking at the window and at the shutter from the hall: neither
  lets them in), then the script kills the rest; guardsStayed3 (every monster
  first seen in the pen never left it, watched every tic), laterGuards3 (a
  revenant, mancubus or arch-vile first seen in the pen: a later wave's guards
  came into it), noneInTheWing3 (no other monster of the fight was ever in the
  wing), won3, steel3. Passed 54 of 54 three times running (and once more
  before the wait was lengthened, 50 of 50 up to the old quit). Twelve under
  the press came 619, 667, 699 and 313 tics after the bait came into the
  chamber (that last one a quick run); the lever was pulled each time with 10
  on the demo under it (the test's trigger), and the press killed 9 to 12.
  The guards counted: 10 first seen in the pen in each run (four of the later
  waves). `MAP=MAP32 MODE=5` (23): room 3's go 2 stands in the mouth before
  it uses the begin-anew plate, `shutterShutAnew3` checks the shutter was
  opening and is shut again; passed 23 of 23 three times. `MAP=MAP32 MODE=4`
  7 of 7 three times. `MAP=MAP32 MODE=2`: 24 views; room 3's are the case,
  the hall from the lobby, the mouth from the hall, the chamber from the mouth
  (its east slab, door 3), the shutter shut with its red lamp, the same open
  (a bare AjarGhost in the chamber) with the lamp green, the landing and the
  stairs, the upper room (the bars, the pen, the window, the lever), and
  through the window to the mouth between the hall's slabs.
- **The older suites** on this branch, once each: SHUT 3 (20) and 4 (7),
  PRESS 3 (13) and 4 (5), PLATE 3 (34) and 4 (6), TWOKEY 3 (8), SHIFT 3 (19)
  and 4 (20), TDOOR 3 (20) and 4 (10), TIME 3 (14), MAP31 7 (15), 6 (9), 5 (4)
  and 3. MAP31 3 run three times, four at once with other suites: once
  `won3` failed (the win came about a second after the check, the hall's
  show still playing), once the known `noneWakesAsIStepIn`, once all 57
  passed. The main package, run at the same time under the same load,
  failed two others (`aLastKillForEveryHall`, `lastScenesOnScreen`): MAP31
  3 is sensitive to timing under load; nothing of this build runs there
  (no out-only door, no shutter).
- **Not tested**: the fight as fought (godmode, the script's kills); a player
  killed nearest to an out-only door (the same code path as leaving by it);
  a closed fight with an out-only door (none exists); the bait leaving by door
  4; hall monsters' shots through the window or the open shutter at a player
  in the wing; the guards fighting through the bars (they are seen and shot,
  untested); a later wave kept waiting by a guard standing on its spot (the
  spots are apart, but guards walk about the pen; the wave comes when there is
  room, and the fight is not won till then); the message's wording on screen
  (it is seen in the MODE=2 views). The numbers are a first guess.
  **Not played by hand**: `MAP=MAP32 ./run.sh` in the worktree.
- **More arms (Vadim, after playing it, 2026-11-20).** He found the two
  shifts more interesting and asked for a BFG, rockets and more ammunition.
  In the lobby now also a BFG, a rocket launcher, a second box of rockets and
  a cell pack; in each box one more box of rockets, and box 3's small cell is
  a cell pack. Reckoned as before that is 19060 against 31700 of health, 60
  per cent (it was 34); the generator asserts 50 to 70. The BFG does more
  with a cell than the reckoning's 22, so in play it is more than that. The
  amounts are mine, a first guess. `firstKept3` still asks for 17 pick-ups
  or more.

## MAP16: the weighbridge made readable (built 2026-11-20)

`tools/map_institute6.py` (the dial, the case), `src/zscript/map16.zs` (the
weighbridge's rule, the dial, the announcement, the tests), `shut.zs` (two
figures), `tools/ajartime.py` (`case` without a plaque, in other trim),
`tools/gfx_institute.py` and `tools/gfx.py` (the dial's pictures),
`src/mapinfo.txt` (thing 20071), `tools/mapcheck.py` and
`tools/thingcheck.py` (figures and wall things), `tools/smoke_MAP16_2.cfg`
and `_3.cfg`. **Not played by hand.**

**What Vadim found**: playing MAP16 he could not find the weighbridge's
point. The level said only WEIGHBRIDGE over the head and "It was built to
weigh something heavier", and nothing tied the baron at the foot to the
plate. Agreed: a dial that reads the weight, the baron announced, and a
glass case that shows it solved.

**The dial** (`AjarWeighDial`, thing 20071, a bright wall sprite AJWG at
1.25 times its size) is on the lobby's east wall, north of the head's frame
(its middle at y -1912, 40 over the floor), seen from the plate, from the
lobby's door and through the glass from the reading room. A round face in
the look's steel (khaki in Post Box), a tick at each tenth, a red mark at
the weight the weighbridge needs and a red band past it, and a lamp over it
that is dark below the mark and green at it or past it. Twelve needle
places: none, the ten tenths, one past the mark. It reads the total on the
plate in tenths of 1000, and the needle steps once every 4 tics toward that,
so it is seen to swing (0 to the mark in about a second). The drawing is
mine.

**The rule changed** from "any one monster of Mass 1000 or more" to "the
total weight on the plate is 1000 or more": everything alive that stands on
it, the player (100) and monsters by their `Mass`. A baron alone still opens
it; the player alone still does not. `openedBy` is the heaviest thing on the
plate when it opened. Two choices of mine: something flying over the plate
(more than 4 over its floor: a cacodemon) weighs nothing, and lighter
monsters add up, so two demons and the player (900) do not open it but two
demons, an imp and the player would. Nothing that light comes up to the
lobby but by the head, behind the player.

**The words.** On the plate, alone: "The weighbridge does not stir under
you. / The dial beside it reads a tenth of what it was built to weigh." (with
more on it, "N tenths"). The plate's message waits while a baron's is on
screen. **The baron** is announced each time one comes to the foot: its
sight sound is heard wherever the player is (no attenuation), and "Far
below, something heavy has come in / at the foot of the building."; a later
one: "Another, as heavy, has come in / at the foot of the building." The
words are mine.

**The case** is in the reading room's north wall, x 576 to 736, just west of
the corner with the window onto the lobby: who stands at the window turns
left and sees it. Behind that wall there is nothing (the stair head is west
of it, the test hall east). Inside, the lobby's walls, floor and ceiling,
a pressed plate with a baron standing on it (half size), and the dial against
the back wall with its needle at the mark and its lamp green. No plaque, and
the glass framed in AJTRIM as the lobby's window: `ajartime.case` has
`plaque=False` and `trim=` for this; MAP32's and SHUT's maps come out of the
generator byte for byte the same. New figures: "standing" (a live monster
by Doom editor number, the first picture of its Spawn state) and "dial".
Asserted sealed and every figure inside.

**Checks**: mapcheck 308 sectors, 0 problems; thingcheck, itemcheck 0. To
get there mapcheck no longer counts wall things that are not solid (the
wind, begin-anew and press plates, the lamps, figures, the dial) as reaching
a wall, and thingcheck lets figures share a spot (a self on a plate figure);
MAP32 had 19 and 14 such reports, and now 1 and 2 that are not these. The
solver: 8 door actions, 3074 states, 0 stuck, as before (the rule is the
same move for it).

**Tests**:
- `MAP=MAP16 tools/smoke.sh`: 41 checks, all pass, out by the brass frame,
  twice. The walk-through's baron is put on the plate by hand as before; it
  opens it alone (weight 1000).
- `MAP=MAP16 MODE=3 TIMEOUT=260`: 17 checks (13 before), all pass, twice.
  New: `caseIsThere` (three figures, none solid, counted or hidden, a
  baron's picture and the dial at the mark among them); `dialReadsATenth`
  (the player alone, still on the plate: weight 100, needle 1, lamp dark,
  shutter shut) and `dialRestsAtATenth` ten tics later; `theBaronIsAnnounced`
  (one baron, one announcement); `dialAtTheMark` (70 tics after the baron
  opens it: weight 1000 or more, needle 10 or 11, lamp green, shutter open).
  For that last one the test holds the baron where it stood when it opened
  the shutter (it would walk off after the player). The baron's way up took
  longer in one run than the old ending allowed, so `smoke_MAP16_3.cfg`
  runs 500 tics more.
- `MAP=MAP16 MODE=2 EXTRA=-nomonsters`: 20 views (17 before): from the
  plate, the dial beside the head; through the glass from the reading room,
  the dial left of the head with the WEIGHBRIDGE sign, the needle at 0 and
  the red mark plain to see (the glass's mullions hide it from some spots, so
  the dial is north of the window's middle); the case: a baron on a lit
  plate, the dial with its needle on the red mark and its lamp green.
- `MAP=MAP32 MODE=3 TIMEOUT=750`: 54 checks, all pass, out. `MAP=SHUT
  MODE=3`: 20, all pass.
- **Not tested**: the sight sound heard everywhere (the smoke tests run with
  no sound: only that the announcement was made); the plate's message with
  more than the player on it; a flying monster over the plate; light monsters
  adding up to 1000; a later baron's message; whether the needle reads at a
  glance in play rather than in a still. **Not played by hand**:
  `cd .wt/ajar/m16-weigh-hints && MAP=MAP16 ./run.sh`.

## MAP32 room 3: plates in the fight, and the timetable (built 2026-11-20)

Vadim found that in the two shifts the selves had only one link between them:
someone under the press opens the wing's shutter. He agreed to two additions.
Plates in the chamber that work things in the wing, so that the bait works the
room while it fights and the next self moves in the windows the bait made. And
the timetable: the room shows what the earlier selves are about to do, lamps
that turn amber three seconds before, and marks under the clock at the top.
While it was being built a third thing was added: the guards in the pen were
puppets on the demo for the self in the wing (a monster on the demo wakes only
when hit, walked into or when the demo is over), so the screen would have
protected from nothing. Now they wake for whoever comes into the wing.

- **The screen** (shut.zs). `AjarShutter` args[4] 1 makes it the reverse of
  a shutter: SHUT while it is held (a plate that names it is pressed, or
  someone is in its args[3] area) and OPEN otherwise
  (`ajartime.shutter(screen=True)`, built open). Every go begins with it open:
  `ShuttersShut` puts every shutter at rest (a shutter shut, a screen open).
  Shutting, it puts the player clear on the side it is worked from, as a
  shutter does, and waits for anything else in its way. Two questions any
  shutter answers now: `Held()` (held now) and `Worked()` (wholly as held: a
  shutter fully open, a screen fully shut). `ajartime.shutter` returns its
  sector.
- **The timetable** (`src/zscript/table.zs`, an `AjarTable` on
  `AjarTimeHandler`). In a room of goes and a fight of goes, from the earlier
  selves' records: the HOLDS, for every shutter and screen of the room (in the
  fight's zones), the spans of this go's tics in which an earlier self holds
  it by the live rules (its recorded place within `AjarPlate.REACH` of a plate
  that names it and within `FEET` of the plate's height, or in a sector of its
  args[3] tag), and the same for every sprung frame's plate of the room; and
  the PULLS, every lever pull still in an earlier self's log (`pTic`, `pTag`).
  It is worked out again whenever its key changes: the fight, the kind of
  fight, the number of goes, each earlier go's length and each log's pulls.
  That covers the start of every go, begin anew, a fight begun anew, the win,
  going on as an earlier self (its record and log are cut) and winding. It is
  a forecast and is never corrected by what happens live. `HoldIn(tag)`: tics
  until an earlier self begins to hold that shutter (0 while one holds it, -1
  none will). `PullIn(tag)`: tics until an earlier self's next pull of that
  press (-1 none). `SOON` = 105 (three seconds).
- **The lamps.** A new frame of the clock lamp, amber (AJTW E,
  `gfx_time.py`). `AjarShutLamp`: green while its shutter is worked (open; a
  screen shut), else amber while an earlier self holds it or will begin to
  within SOON, else red. New `AjarPressLamp` (20054,
  `ajartime.press_lamp(m, x, y, angle, tag, z=72)`): red while the press is
  not up and ready, else amber while an earlier self's pull comes within
  SOON, else green. Both click softly once as they turn amber (the button
  sound at 0.35). Both are an `AjarLamp`, which keeps its height: a press
  coming down over a lamp pushes it down and it goes back. A plate does the
  same now (the two plates in the chamber are under the press).
- **The clock.** Under the "m:ss / m:ss" at the top (the open fight's clock
  in a fight of goes, `GoesClock` in a room of goes), a bar 240 wide in the
  640 by 400 frame, tic 0 to the clock's length: a dark strip, one row 3 high
  for each shutter, screen or sprung frame's plate an earlier self holds in
  this go (shutters by tag, then plates by frame), green where it is held, a
  gold tick the bar's full height at each pull, a white cursor at this go's
  tic. Nothing when there is no earlier self or the go is past that length.
  `TableBar` only reads the table.
- **Sentries** (time.zs, its header). `AjarSentry` (20055,
  `ajartime.sentries(m, x, y, fight, pen_tag, trip_tag)`): while a go's demo
  plays and the PLAYER (alive, in the hall, not in a box) stands in a sector
  with the trip tag, every living monster of that fight on the demo whose
  middle is in a sector with the pen tag wakes (`wakeDue`: `Wake` makes it
  real where it stands, with the health it had, after the player). One that
  comes into such a sector later does the same while the player is there; an
  earlier self never trips it. Nothing else about the demo changes: the
  hall's horde stays on the demo.
- **Room 3** (`tools/map_secret2.py`). New tags `SCREEN3` 3536, `CAGE3`
  3537, `PENTAG3` 3538 (the pen's sector), `WING3TAG` 3539 (the landing, the
  six steps, the upper room, the window's sector and the cage: every walkable
  sector of the wing that had no tag; the screen keeps its own, the wing's
  shutter is the threshold). One `sentries` thing for fight 3 with those two.
  - Two plates in the chamber: the screen's at the back opposite the mouth
    (5768, 1216), the cage's in the north-west corner (5096, 1184). Asserted
    wholly in the chamber, 64 or more clear of its slabs and of the time
    doors' mouths, and over 600 on foot from the wing's shutter.
  - The screen: a sector 16 deep along the whole of the bars on the upper
    room's side (5464..5880, -176..-160), worked from the upper room, opening
    the full height (128). The upper room is 16 shallower (-160..-16). The bars
    stay between the pen and the screen, so no guard can stand in its way.
    The pen's sight asserts hold with the screen open (its sector is one of
    the wing's spaces). Its lamps: in the upper room on the north wall west of
    the window (5672, -18), and a repeater on the landing's east wall south of
    the stairs (5270, -136), facing west.
  - The cage: an alcove 80 by 96 east of the upper room (5896..5976,
    -152..-56), floor 96, steel, lit 230. In the upper room's east wall its
    shutter (64 wide, -152..-88, `behind`: a player inside when it shuts is
    put out into the upper room) and a slit of glass (32 wide, -88..-56); the
    line between them blocks and shows no trim. A megasphere at (5940, -72),
    seen through the glass. Its lamp on the upper room's east wall (5878,
    -36). Asserted: entered only by its shutter, overlapping nothing. The
    wing's zone reaches east over it; `on_foot` has it as a region with a way
    out to the wing only. A fight begun anew puts the megasphere back
    (`Pickup` in anew.zs now counts a `Megasphere`: it is a CustomInventory,
    none of the classes there).
  - Press lamps: two in the chamber on its south wall either side of the
    mouth (5640 and 5896, 802), facing north; one in the hall on its north
    wall west of the mouth (5640, 766), facing south.
  - The messages, once a level each, the first time the player steps on the
    plate: "A screen comes down before the guards in the tool room / while
    someone stands on this plate." and "A cage in the tool room is open while
    someone stands on this plate." An `AjarPlate` with args[2] n says
    `PlateText(n)` (`ajartime.shutter_plate(say=)`); it counts the player's
    steps on it and its sayings.
  - The case in the lobby: a pressed plate under self 1 again. `begun1`
    counts 41 figures.
  - Unchanged: the hall, the waves, the guards and their spots, the supplies
    and their reckoning (a megasphere is not ammunition), the boxes, the time
    doors, the wing's shutter and lamp, the begin-anew plate, no infighting.
- **Choices of mine.** The table is worked out again by a key of the records,
  not by a call at each event (it catches every one of them, and one that is
  added later). The bar is drawn only in a room of goes or a fight of goes
  (not in MAP31's open fights, which have no shutters or presses); rows are 4
  apart with a gap of 1. The amber click is the button sound at 0.35. The
  message is said by the plate, not the shutter (the shutter's args are all
  in use). The lamps and the plates keep their height under the press. The
  screen's lamp in the upper room at x 5672 (the window is 5704..5832), the
  cage's lamp north of the glass at -36. The hall's press lamp west of the
  mouth. The wing's shutter sector has no trip tag (the landing trips them).
- **Tests.** `MAP=MAP32 MODE=7 TIMEOUT=400 tools/smoke.sh` (new,
  `smoke_MAP32_7.cfg`; room 3 entered at its lobby as MODE=5, godmode; 18
  checks). Go 1, the bait: atRest3 (screen open, cage shut, their lamps red,
  the press lamps green, no table); on the screen's plate from tic 160 to
  340: screenDownWithItsPlate3 (shut, its lamps green, no guard in the pen
  sees a point in the upper room and a level trace north from each guard
  stops at the screen), screenUpAgain3 (open, red, the guards see it again,
  the trace passes); on the cage's plate from 370 to 520:
  cageOpensWithItsPlate3, cageShutsAgain3. Out by door 3 at 700. Go 2:
  timetable3 (three rows, the wing's shutter, the screen, the cage, one span
  each, each beginning and ending within 2 tics of what go 1 did, no pull),
  amberBefore3 (each lamp red 125 tics before the earlier self steps on, amber
  40 before, green once worked), guardsOnTheDemo3 (before the wing's shutter),
  guardsWakeAsIStepIn3 (10 tics after stepping on the landing: each awake and
  after the player), screenHeldByMyEarlierSelf3 (in the upper room while the
  earlier self holds the screen: no awake guard sees the player; after it
  lets go some do), cageHeldByMyEarlierSelf3, megasphere3 (walked in, health
  200), putOutOfTheCage3 (the earlier self steps off: the player is in the
  upper room, the cage shut), the lever at tic 560; out by the window and the
  hall's time door 2. Go 3, in box 2: pullOnTheTimetable3 (one pull, at 560,
  the second self's), guardsOnTheDemoAgain3 (the second self in the wing, the
  guards on the demo), pressLampAmber3 (the press lamps green 125 tics before
  the pull, amber 30 before, red 25 after, the press set off by the earlier
  self); then the begin-anew plate: restAnew3 (screen open, cage shut, the
  megasphere back, the table empty); then both plates stepped on again:
  saidOnce3 (each stepped on twice or more, its message said once; checked
  here, at the end, rather than in go 1, so that "once" is tested without a
  second hold in go 1). The screenshots of go 3 show the clock with its bar:
  three green rows (the wing's shutter long, the screen, the cage later), a
  gold tick at 560 near the right end, the white cursor moving across.
  `MAP=MAP32 MODE=5`: room 3's go 1 also walks into the cage (from inside,
  behind the shut shutter) and takes the megasphere; `asAtTheFirstEntry3`
  now also asks the screen open, the cage shut, the megasphere back. `MODE=2`:
  30 views, six new after room 3's: the screen's plate, the cage's plate, the
  screen open and shut from the upper room (a bare `AjarGhost` on its plate),
  the cage through its glass, the landing with the repeater lamp. MODE=3,
  4, 6 unchanged in their scripts (the sentries wake the guards in MODE=3's
  go 2 too; `guardsInThePen3`, `guardsStayed3`, `laterGuards3`,
  `noneInTheWing3` pass as they were).
- **Results** (2026-11-20, full build): MODE=7 18 of 18 in each of four
  runs; MODE=3 54 of 54 in each of four runs (one on the quick build); MODE=5
  23 of 23; MODE=4 7 of 7; MODE=2 30 views and MODE=6 6 views, looked at. The
  labs once each: SHUT 3 (20) and 4 (7), PRESS 4 (5), PLATE 3 (34) and 4 (6),
  TWOKEY 3 (8), SHIFT 3 (19) and 4 (20), MAP31 6 (9) and 7 (15), MAP31 3 (57,
  no failed check) all pass. `MAP=PRESS MODE=3` (13) passed 3 of 6 runs on
  this branch, each failure a different check (killsAreMine with a sixth kill
  from elsewhere, as noted for it earlier; afterTheWin with a body moved;
  theyGoWhereTheyWent), and 4 of 4 runs of main's code. Nothing of this
  change runs differently on PRESS that I could find (no sentry, no screen;
  the table is only read). **Settled after the merge with main** (the MAP16
  weighbridge): run alone, one test at a time, PRESS 3 passed 5 of 5; the
  failures were from tests run side by side. On the merged build: MODE=7 18
  of 18 three times, MODE=3 54 of 54 twice, MODE=5 23, MODE=4 7, PRESS 4 5,
  SHUT 3 20, MAP16 3 all pass. Before that MODE=7 failed
  `screenDownWithItsPlate3` once: the test's trace from one guard hit the
  other guard, not the screen; the trace now goes through actors. And MODE=3
  failed `theyFireBack4` once (room 4, untouched here: no pen monster
  happened to fire out in its 230 tics).
- **Not tested.** The bar in a room of goes (`GoesClock`: no room of goes
  has an earlier self holding a shutter in a test; the code is the same
  `TableBar`). A sprung frame's plate as a row (none in room 3). The amber
  click (the tests run with no sound). A guard waking in the pen while the
  screen is shutting (the bars keep them off its sector; asserted only by
  geometry). Winding, or going on as an earlier self, while the table is up
  (it is rebuilt by its key; not exercised). The sentries in any other room.
- **Not played by hand**: `MAP=MAP32 ./run.sh` in the worktree.

## MAP32 room 4: two keys under fire (built 2026-11-20)

Room 4 was a range with a booth: a plate in it held the pen's shutter open, so
one self stood on the plate while the next fired. Now two selves must each turn
a key, far apart and under fire, at nearly the same moment. The booth, its
glass, its plate and its zone are gone.

- **Key levers** (`src/zscript/keys.zs`, `AjarKeyLever`, 20056,
  `ajartime.key_lever(m, x, y, angle, tag, number, seconds=30)`: args tag,
  seconds (0 is 30), number in the set). The name `AjarKey` was taken (the
  room keys). USE pulls it when it is up and its shutter is not keyed; it is
  then live for `JOIN` = `AjarHandler.TOGETHER_TICS` (70, two seconds). When
  every lever of the tag is live at once the shutter is KEYED: held open for
  the seconds (`AjarShutter.keyed` counts down; `Held()` is a pressed plate or
  keyed), the joined chime, the levers held down until it runs out, then up;
  a beep at three, two and one seconds left. A live lever that runs out alone
  comes up with the "too late" sound. The player's pulls are logged
  (`AjarGoLog.kTic/kTag/kNum`) and an earlier self replays each at its tic if
  that lever is up then (`GhostKeys`, after `GhostPresses`). Every go begins
  with every lever up and nothing keyed (`ShuttersShut` calls `KeysUp`).
  Three messages, each once a level: the first lone pull, the first too late,
  the first keyed with an earlier self.
- **Key lamps** (`AjarKeyLamp`, 20057, `ajartime.key_lamp`, args tag,
  number): green while keyed; while another lever of the set is live, amber
  and green by turns every 6 tics with a click each half second (pull now);
  amber within SOON of an earlier self's pull of another lever; else red.
- **The timetable** (table.zs): key pulls are gold ticks on the bar
  (`kTic`), `KeyPullIn(tag, n)`, and the shutter's row holds the spans in
  which the earlier selves' pulls key it (`KeyHolds`: their logged pulls in
  tic order, by the live rules, ignoring pulls while it is keyed).
- **Idle guards** (time.zs): an `AjarCue` with the ambush flag comes idle
  (deaf, no target, no fog or sound); on the demo it wakes idle where it is
  at the demo's end if it was not hit. Sentry args[3] 1 wakes the monsters
  idle (`ajartime.sentries(..., idle=True)`, `AjarRole.wakeIdle`). `Hunt`
  leaves an idle monster alone.
- **Room 4** (`tools/map_secret2.py`). Tags `SHUT4` 3540 (unchanged
  meaning), `WEST4TAG` 3541, `EAST4TAG` 3542. Two mirrored wings off the
  range (about MID4 7456): 288 by 660, a doorway that blocks monsters and
  sound, two baffles 224 long across the way, a window to the range (with
  asserts: the windows face each other, nothing cuts the line between them),
  at the far end the lever (1 west, 2 east) and its lamp, and stock by the
  lever (two cell packs, a rocket box, a medikit). Guards: wave 1 idle (two
  imps, two hell knights, a revenant, out of sight of the doorway), wave 2 a
  hell knight and a revenant, wave 3 a baron; sentries per wing, idle. The
  walk from lever to lever is 1845.5 (> 1750 asserted). Supplies 21800
  against 17440 (1.25). The time doors moved along their walls (door 1 at
  400..464, door 2 at 560..624) to make room. A new case on the range's far
  wall: two selves at two levers, a lamp, a cyberdemon and a mancubus.
- **Choices of mine.** A lever is live while `maptime - pulledAt <= 70`.
  Idle guards come without fog or sound, and one on the demo that was not hit
  wakes idle where it stands when the demo ends. The third message is said
  when the keying pull finds any earlier self in the fight. The wing is 660
  long (the brief's 580 left the lever-to-lever walk at about 1729) with
  baffles 224 long, which moved the time doors 1 and 2 along their walls.
  The doorway's ceiling is F4+128. Placements of the lamps, the stock and the
  guards are mine (mirrored for the east wing). No rockets were added at the
  entry: the stock by the levers already brings the supplies over 1.2.
- **Tests.** MODE=3 room 4 rewritten: begun4, noLeak4, guardsIdle4; go 1 the
  west lever alone (shutAlone4, both messages), rockets at the shut shutter
  (rocketsStopped4); go 2 the east wing on the demo, then awake and idle
  (guardsOnTheDemo4, guardsWake4), its lamp amber before the earlier self's
  pull and blinking (keyLampAmber4), keyed by two (keyedByTwo4), the earlier
  self's rockets in the pen (myEarlierSelfHurtsThem4), mine
  (hurtThroughTheShutter4), still open at 30 s less two tics (openStill4,
  added), shut again (shutsAfterHalfAMinute4), won4, steel4. theyFireBack4 is
  gone. MODE=5 room 4: go 1 pulls the west lever, takes what lies by it and
  fires; asAtTheFirstEntry4 also asks the levers up, the shutter shut, nothing
  keyed. New MODE=8 (`tools/smoke_MAP32_8.cfg`, `KeyScript`): four goes,
  tooLateTogether4 (go 2 pulls 100 tics after go 1), inTimeWithMyFirstSelf4
  (go 3, 30 after), shutterOnTheTimetable4 (go 4's table: one span of self 2
  from the keying pull, 30 s long, and the three pulls), amberBeforeItOpens4,
  openedByMyEarlierSelves4 (the player far from both levers), and a
  screenshot in go 4: the shutter open, both lamps green, the pen's crowd
  behind, the bar under the clock with its span and gold ticks. MODE=2's three
  views of room 4 are six now (entry, the west wing from its doorway, the
  lever, through the windows, the shutter, the case).
- **Results** (2026-11-20, full build, each suite alone): MODE=3 59 of 59
  checks (the count of `AJARTEST name=1` lines, with levelExited) in each of
  three runs, MODE=5 23 of 23 three times, MODE=8 5 of 5 three times. Once
  each (quick build): MODE=7 18, MODE=4 7, SHUT 3 20, SHUT 4 7, PRESS 3 13,
  PRESS 4 5, TWOKEY 3 8, PLATE 3 34, MAP31 6 9, MAP31 7 15; MODE=2 (33
  screenshots) and MODE=6 (6) run without errors.
- **Not tested.** The beeps in the last three seconds and the "too late" sound
  are only heard; the messages are checked by the bits said, not their text.
  The wave 2 and 3 guards of the wings (not idle) are not looked at by a test.
- **Not played by hand**: `MAP=MAP32 ./run.sh` in the worktree.

## MAP16: the weight has to stay, and the baron on the gallery (built 2026-11-20)

`tools/map_institute6.py` (the baron's spot, the gallery, the base's heavy
monsters, the case, the docstring, the PUZZLE), `src/zscript/map16.zs` (the
weighbridge's rule, its words, the three tests), `src/zscript/enemies.zs`
(`AjarSense.dogged`), `tools/solve.py` (a lure with a place of its own),
`tools/smoke_MAP16_1.cfg`, `_2.cfg`, `_3.cfg`. `shut.zs` and `ajartime.py`
not touched. **Not played by hand.**

**What Vadim found**: MAP16 was too weak as a puzzle. The baron appeared at
the foot beside the frame, and the plate was right in front of the head, so
"hang the leaf, step through" did the weighing; and the shutter opened for
good at a touch. Agreed: the two changes below. A third idea, a switch in
the labs shot through GREEN, was proposed and left out. Everything else
stays (the porter, the den, VIOLET, the nailer, GREEN, RED's far side on the
gallery, the lever, the secret, the dial).

**Change 1: the weight has to stay.** The weighbridge weighs everything that
stands or lies on the plate, by where its middle is: the player (100) and
live monsters by their `Mass` (more than 4 over the floor weighs nothing),
and dead monsters' bodies by theirs (`weight` the total, `deadWeight` the
dead part). The shutter follows the total: while it is 1000 or more the
shutter goes up, below it comes down again. The weighbridge moves it itself,
tic by tic (`Sector.MoveCeiling`, crush off, 2 a tic as Door_Open at speed
16 did: about 3.6 seconds up or down, with the door sound sequence). Coming
down it waits while anything stands or lies in the doorway (players,
monsters alive or dead, solid things), and goes on when it is clear. A body
of 1000 or more on the plate (a dead baron) settles it: the shutter goes up
and stays, and no more barons come.

**Change 2: the baron lives on the canteen's gallery.** The MapSpot (tid 16)
is at the gallery's east end, (840, -150), facing the canteen: clear of RED's
far side (x 496..560), the lever (704..768) and the panel (west end). The
weighbridge puts a baron there on its first look, on every skill, unannounced
(it is in the level's tally); 20 seconds after each dies another comes on
the same spot (tried again on later looks if the spot is taken), its sight
sound heard everywhere and announced, until settled. The gallery lost two
imps (four imps and the chaingunner are left). Its barons are **dogged**: a
flag on `AjarSense`, off for every other monster, that the weighbridge sets
on each baron. A dogged monster does not drop the door it is making for
because it sees the player straight while the player's floor is more than
24 from its own; once through (the jump) it is like any other monster. That
is what lets a baron on the gallery, which sees the player on the canteen
floor, follow the player down through RED.

The hell knights are gone from the base: the placed one at (-760,-620) and
the two of VIOLET's ambush (after 3) are cacodemons now (400, and they fly:
over the plate they weigh nothing). The test hall's two knights stay.
Nothing as heavy as a baron is anywhere but the gallery and the test hall.

**The way it gets weighed** (the puzzle): RED hung in the canteen's frame
101, up through it to the gallery carrying the leaf, down through RED again
with the baron behind; in the canteen RED swapped out of 101 for the leaf,
through the leaf to the lobby: the baron follows and comes out of the head
onto the plate. The shutter goes up while it is on the plate and comes down
when it walks off; killed on the plate, its body holds the shutter up for
good. The same from any floor's frame (RED hung in 102 or 104, swapped there
for the leaf; not tested).

**The words** (as agreed; through `AjarHandler.Say`):
- the player alone on the plate: as before ("does not stir under you ... a
  tenth of what it was built to weigh");
- the total reaches the mark: "The weighbridge takes the weight, and the test
  hall's / shutter rolls up." (the first time, then not more than every 10
  seconds);
- the total falls below: "The weight is off the weighbridge. / The shutter
  comes down again." (the same limit);
- settled, once: "Dead weight. The weighbridge holds it, / and the test
  hall's shutter stays up.";
- a baron of the weighbridge dies off the plate, the first two times: "It
  lies where nothing weighs it.";
- a later baron: "Another, as heavy, has come onto the gallery / over the
  canteen." (the first is not announced).

**The case** shows the baron lying dead on the plate: the existing "body"
figure (a monster's last death picture) instead of "standing"; no new figure
was needed. Still asserted sealed, every figure inside.

**The solver.** `lures` has a new form, `dict(home=region, to=region,
key=letter, name=word)`: the monster has a place in the state (an eighth
element), starts at `home`, may come with the player through any hung door
from the region it is in (both successors), goes by hung doors only (never a
drop, a squeeze or a doorway of the building's), is killed by a free move at
any time (another at `home`), and in `to` gives the key for good and leaves
the state. The old form still works (no map uses it now). MAP16:
`lures=[dict(home="gallery", to="lobby", key="W", name="baron")]`, and the
auto key "B" is gone. **10 door actions, 9529 states, 0 stuck, nothing
lost** (was 8, 3074). Every other level's numbers in the full build are
unchanged in kind (all solvable, 0 stuck). The solution as printed:

    walk to labS / pick up GREEN / hang GREEN in 102 / through GREEN to labN
    walk to canteen / pick up RED / hang RED in 101 / through RED to gallery
    through RED to canteen, the baron behind / through RED to gallery
    take key L / walk to canteen / kill the baron (another comes to gallery)
    walk to base (key L) / walk to cubby (squeeze) / walk to lobby / take key b
    walk to read (key b) / pick up the TEAL leaf / walk to labS
    through GREEN to labN / walk to canteen / through RED to gallery
    through RED to canteen, the baron behind
    swap RED for the TEAL leaf in 101
    through the TEAL leaf to lobby, the baron behind (key W)
    through the TEAL leaf to canteen / swap the TEAL leaf for RED in 101
    walk to base (key L) / hang the TEAL leaf in 104
    let the thief carry the TEAL leaf to 105 / walk to cubby (squeeze)
    walk to lobby / through the TEAL leaf to den / pick up VIOLET
    through the TEAL leaf to lobby / walk to test (key W) / walk to night
    hang VIOLET in 190

The first trip's "the baron behind ... kill the baron" costs nothing and
changes nothing: the search's order, not a needed step. The walkthrough
leaves it out.

**Monsters** (`budget.py`): 146 at skill 3 (hp 16770), ammunition x1.64
(about x1.55 with the gallery's baron, which budget.py does not count, and
less for each later baron); 76 at skill 1, x2.72.

**Checks**: mapcheck 308 sectors, 0 problems; thingcheck 0; itemcheck 0.
Full `./build.sh`: passes, every level solvable with 0 stuck.

**Tests**:
- `MAP=MAP16 tools/smoke.sh` (walkthrough, the solver's order): 43 checks,
  all pass, out by the brass frame; twice. New: the baron on the gallery at
  the start (then taken away); up through RED with the leaf and down again;
  RED swapped for the leaf, through it to the lobby; a baron put on the
  plate by hand and held there: the shutter goes up (`liveBaronRaisesTheShutter`,
  `shutterGoingUp`, `shutterUp`); moved off the plate: it comes down
  (`offThePlateItComesDown`, `shutterDownAgain`); back on and killed: settled,
  still up 140 tics later; back through the leaf, the leaf swapped for RED,
  the leaf to the foot and on as before.
- `MAP=MAP16 MODE=3 TIMEOUT=1000` (the company, by themselves): 41 checks,
  all pass; twice. The porter and nailer checks as before (phase 2 now hangs
  GREEN at the foot, not RED: RED's far side is on the gallery and the baron
  would come down through it). The baron: on the gallery at the start; with
  the player on the canteen floor in its sight and RED not hung it stays up
  (300 tics, awake, after the player); RED hung in 101, the player up through
  it with the leaf and down again: the real baron comes through RED into the
  canteen; RED swapped for the leaf, the player through it to the lobby: the
  baron follows through the leaf and comes out of the head onto the plate;
  held there 70 tics (as the last test did) the dial is at the mark, lamp
  green, the shutter going up; let go it walks off after the player and 170
  tics later the shutter is down; killed off the plate: "It lies ..." said,
  no baron for 600 tics, another on the gallery after the wait, announced;
  the whole walk again with the second, killed on the plate: dead weight
  1000, settled, the shutter up and still up 900 tics later, no more barons;
  and the porter, killed meanwhile, has another in the den. The test places
  the player (godmode) and the doors; the baron does its walking through RED
  and the leaf itself. To make room for the walk the player steps away from
  frame 101 after coming down (the baron comes out where the player stood
  and blocked the swap in the first try). `smoke_MAP16_3.cfg` runs 6150 tics.
- `MAP=MAP16 MODE=2 EXTRA=-nomonsters`: 21 views (20 before). New: the
  gallery from the canteen floor: the baron at the gallery's east end, RED's
  far side to the west of it. The case: the baron's body on the lit plate,
  the dial at the mark with its lamp green (the body is low in the picture,
  partly behind the weapon). The weighbridge's baron is there with
  -nomonsters (it is spawned, not placed).
- Regressions, once each, all pass: `MAP=LAB` modes 1, 2, 3 (13, 9, 8),
  `MAP=MAP15` modes 1 and 3 (31, 13), `MAP=SHUT MODE=3` (20),
  `MAP=MAP32 MODE=3 TIMEOUT=750` (54, out).

**Departures from the brief, and why**:
- "Takes the weight" is said whenever the total reaches the mark and it is
  not settled, not only when nothing dead is part of it: with a light body
  making up part of the total the shutter would otherwise go up unexplained.
- Anything lying in the doorway (a body too) keeps the shutter from coming
  down: closing on a body would grind it. A body left in the doorway keeps
  the shutter up.
- MODE 3's phase 2 uses GREEN for "the porter leaves other doors" (see above).

**Not tested**: the same weighing from the labs' frame 102 or the foot's 104;
the sight sound heard everywhere (no sound in the tests); the shutter waiting
for something in its doorway (nothing stood there in any test); lighter
monsters or bodies adding up to the mark; a later baron arriving while its
spot is taken; the up and down words' 10-second limit; how hard the gallery
fight is with a baron in it, and how often a player kills the first baron
before thinking of the weighbridge; whether "It lies where nothing weighs
it." is enough of a hint. A baron that dies on its way (in the canteen, on
the gallery) is the ordinary "off the plate" case, tested once.

**Not played by hand**:
`cd /data/src/doom/doomer/.wt/ajar/m16-gallery-baron && MAP=MAP16 ./run.sh`

## MAP16: the porter leaves a door swapped in under its hands (2026-11-20)

Vadim, playing: the porter set off for the leaf at the foot, RED was hung
there in its place before it arrived, and it carried RED to the den's frame.
Nobody could get into the den or to RED's far side again: the level could not
be finished. Why: the porter's rule (only the leaf) was checked when it chose
the job, not when it did it; on the way and at the hinges it only asked
whether some door still hung there. Now `JobStillThere()` asks the porter's
own question again (`PorterJob`: the leaf out of another frame, or into its
own empty one), so it gives the job up on the way or at the hinges, and
`A_ThiefAct` checks once more before it touches the frame. The plain thief is
as before. MODE 3 has a new phase 3 (the later ones are one higher): the leaf
at the foot, GREEN swapped in once the porter is at the hinges; it leaves
GREEN hanging, carries nothing, the den stays empty. Without the fix it took
GREEN and hung it in the den (both checks 0). `MAP=MAP16 MODE=3 TIMEOUT=260`
(about 3 minutes): 44 checks, all pass, twice. `MAP=MAP16` 52, `MAP=LAB
MODE=2` 9, `MAP=TEST MODE=5` 7: all pass.

## MAP32 room 2: the Pair shuts again (built 2026-11-20)

In room 2 the second self used to do everything at leisure: once joined, the
TEAL Pair stayed joined for good. Now a joined Pair can run out, room 2's after
three seconds, and the pit is long enough that the self who hangs the leaf in B
cannot then fetch YELLOW and bring it through.

- **A Pair joined for a time** (goes.zs, its header). `AjarTogether` args[1]
  n (`ajartime.together(..., seconds=n)`): the Pair stays joined n seconds
  after its second leaf is hung; 0 is for good, as before (TWOKEY and every
  other lamp have 0). If the two frames' lamps differ, the smaller that is not
  0 (`JoinSeconds`). `Hang` sets `AjarDoor.joinEnds` and `joinTics` on both
  leaves (`JoinFor`); `Unhang` clears them. While it is joined the lamps are
  green and each beeps (the key levers' countdown beep, `switches/exitbutn`)
  at every whole second left that is less than the whole time (at 2 and 1
  for three seconds). At the end (`Unjoin`, done by the first lamp that
  ticks then) both leaves stay hanging, un-joined: shut, both lines solid,
  red lamps, the "too late" sound at both frames; exactly the state of two
  leaves hung too late (`Late` is true). To join again both are taken down
  and hung together again by the old rule. It is not a door action, so
  nothing of it is written in the go log: the earlier selves' hangings bring
  it about again in every go by themselves.
- **Nobody is left stuck.** When it shuts, the player in either mouth is put a
  step clear on the side they are on (`StandClear`, as a sprung frame does
  when it shuts: 26 from the line). Without it the player could be left
  overlapping a line that has just become solid. An earlier self is put where
  its record says every tic (`SetOrigin`), so it is never stuck; one crossing
  in its record when it shuts simply walks on through the wall, as a ghost
  does wherever its go differs.
- **Messages**, once a level each (`AjarHandler.pairSaid`): the first join
  for a time, also when the earlier selves make it ("Both leaves of the TEAL
  pair hang: each frame opens onto the other, / but only for 3 seconds. Then
  both shut again."; `SayHung` does not say its own over it), and the first
  time one shuts again ("The TEAL pair has shut again. To join it, both
  leaves / must be taken down and hung together again.").
- **The timetable** (table.zs). `PairHolds`: from the earlier selves' logs,
  every hanging and taking down of a Pair leaf in tic order, played by the
  live rules (joined when the second leaf is hung within 70 tics of the
  first in frames of which one has a lamp; from that tic for the lamps'
  seconds, or until a leaf is taken down; a joining for good is not a row):
  one row on the bar per such Pair (`AjarTable.rPair`, its args[4]), green
  over the spans, and the spans with their frames (`jFa`, `jFb`, `jFrom`,
  `jTo`) for `PairJoinIn(frame)`: tics until the earlier selves have it
  joined (0 while they do, -1 never). The table's key now also counts the
  earlier logs' door entries. The lamp (`AjarTogether`) is amber (frame E,
  now loaded by it) while such a span begins within `SOON`, when it is
  neither joined nor blinking for a leaf hung alone, with the soft click of
  the other lamps as it turns amber.
- **Room 2** (`tools/map_secret2.py`): `PAIR2` 3 seconds on both lamps. The
  pit is 3280..3792 by -900..640 (`PIT2`; it was -256..640), nothing was in
  the way to the south; YELLOW leans at its far south end, (3600, -840).
  From before B's mouth (3696, 600) to YELLOW is 1443 (asserted 1400 or
  more), there and back at the fastest strafe-run (23.6 a tic) 122 tics
  (asserted 105 + 10 or more). Time door 2, the leaf by B, the drop are as
  they were. The zone, the `on_foot` pit region and the `covers` box follow
  the pit. The case (glass 2048..2304, 256 wide, was 224): self 1 by one
  hung TEAL leaf, self 2 by the other, both lamps green, self 3 by the
  second leaf with YELLOW leaning beside it (there is no figure of a self
  carrying a door), each with its number over its head. YELLOW in W is left
  out: a case wider than 256 has glass bigger than `covers()` lets go
  without a region, and three selves, two leaves and YELLOW fill 256.
  `begun1` counts 49 figures (was 43).
- **The solutions.** Three selves (tested): go 1 hangs a in A and leaves by
  door 1; go 2 drops into the pit, hangs b in B within two seconds (joined
  for three), runs for YELLOW, comes back to a shut Pair and leaves by the
  pit's door (YELLOW stays there); go 3 takes YELLOW before self 2 would
  (self 2's replayed pick-up finds it gone: the conflict rule drops that and
  the rest of what it does to YELLOW, nothing breaks), waits at B, walks
  through when the two earlier selves have joined it, and hangs YELLOW in W.
  **The two-self solution of the brief is impossible**: it needs go 2 to put
  YELLOW down by B and pick up leaf b, but a door cannot be put down (only
  hung; "You can only carry one door"), B takes a TEAL leaf only, and a door
  an earlier self holds is left leaning only where its go ends (at a time
  door, after its hanging of A). So room 2 now needs three selves, which is what
  Vadim asked for ("so we actually need 3 copies of the player"); the
  two-self way was an addition of the session's that rested on a wrong
  reading of the carrying rules. No way to put a door down was added.
- **Choices of mine.** The beep and the end are played by each lamp and
  each frame (heard at either end); the timed message is said by `Hang`
  (so also for the earlier selves' join) and suppressed in `SayHung` in
  that tic; amber only when the lamp is otherwise unlit or red; the span's
  row is per Pair, not per frame; the case's layout and the room's numbers
  above.
- **Tests.** `MAP=MAP32 MODE=3 TIMEOUT=850` (`smoke_MAP32_3.cfg` waits 6800,
  was 6300; the level is left at about tic 5450): room 2's part plays the
  three-self solution. Kept: noLeak2, itTicks2, tooLateAlone2,
  pitDoorToTheBox2, forgotten2, joined2 (now also asks the time it shuts),
  yellowUp2 (now in go 3), hungInW2, on2. New (8): stillJoined2 (2 tics
  before its time: joined, lines open, both lamps green), shutAgain2 (2
  after: both hang, `Late`, not joined, both lines solid, both lamps red,
  both messages said), putClear2 (self 2 stood 10 from B's line in its mouth
  as it shut: put 26 from it, in the pit), backTooLate2 (self 2 walks into B
  with YELLOW: still in the pit), pairOnTheTimetable2 (go 3's table: one
  Pair row, one span of self 2 from its hanging, 105 long, and YELLOW back
  at the far end), pairLampsAmber2 (both lamps unlit 140 tics before the
  earlier selves join it, amber 48 before, green when joined),
  joinedByMyEarlierSelves2, lostPickUp2 (self 2's pick-up of YELLOW broken,
  YELLOW in my hands, nothing held by self 2). 67 checks in all (was 59).
- **Results** (2026-11-20, full build, each suite alone): MODE=3 67 of 67 and
  out by the line in each of three runs; once each: MODE=4 7, MODE=5 23,
  MODE=7 18, MODE=8 5, TWOKEY 3 8, SHUT 3 20, PLATE 3 34, all as before;
  MODE=2 (33 screenshots) without errors, room 2's case and pit looked at.
- **Not tested**: a Pair joined for a time whose two lamps give different
  seconds; a leaf taken down by hand while it is joined for a time (the
  code path is `Unhang`'s, as before); a run by hand against the three
  seconds. **Not played by hand.**

## Fights of goes: an earlier self's shots wake nobody (built 2026-11-20)

**The bug.** In a mixed open fight (MAP32 rooms 3 and 4) `AjarRail.ModifyDamage`
counted an earlier self's (`AjarGhost`'s) hit on a monster on the demo as the
player's: it set `hit`, so the demo loop woke that monster, real and after the
PRESENT player. In room 3 the first self is the bait under the press and shoots
the horde around it; in the next go every one of those shots, replayed, woke its
monster, which left the press and hunted the next self ("after resurrection some
monsters attack me even though I never touched them"; "monsters don't all go
under the press"). And the hit was in the demo already (the recorded health fell
then), so counting it in `dmg` counted it twice. The tests' bait never shot.

**The rule** (time.zs `AjarRail`, `Replayed`, `Fell`, the demo loop; headers of
time.zs, goes.zs, shut.zs):
1. An earlier self's shot never wakes a monster on the demo. Only the present
   player does (hurting it, walking into it, tripping its sentries) and the
   demo's end. `rail.hit` now means hurt by the present player only.
2. An earlier self's hit that the demo already has does nothing (no `dmg`, no
   `hit`): the demo carries it, the monster's health and death come from the
   record.
3. One the demo does not have (room 4: rockets through a shutter that was shut
   in the last go) is counted in `dmg` (and in `ghostDmg`, for the tests) and
   the monster stays on the demo. When `hp - dmg` reaches 0 it dies then and
   there (`Fell`: off the demo, no target, killed by the player with
   `DMG_FORCED`, so the player's kill), without first turning on anyone. Woken
   later, it has the health left after what was counted (`Wake`, as before).
4. A monster awake (real) is hurt by an earlier self's shots as by anyone's.
5. MAP31's open fights (not mixed): an earlier self's shots do nothing to a
   monster on the demo, as before.
6. A guard at its post (idle cue) hurt only by an earlier self still wakes idle
   at the demo's end (`!rail.hit`), with what is left of its health. No second
   flag was needed: `hit` is the player's, `ghostDmg` the earlier selves'.

**The window** (`REPLAY_TICS` = 4). A role's record is written once a tic
(`RecordDemo`), index `ot - born`, and played at the same index. An earlier
self's hit "is in the demo" when the monster's recorded health falls between two
consecutive entries in the hall within 4 tics either side of the present index.
Fired again from where the earlier self was, the same shot lands on the posed
monster a tic after the index of its recorded fall (the record is written at
the start of the tic, after the last tic's thinkers), or within a tic or two.
The price: a hit the demo has not, landing within 4 tics of a recorded fall of
the same monster by some other cause, is taken as replayed and does nothing.

**The replay is not exact** (found by the tests, not changed). A monster on
the demo is posed where it was at the start of the tic, while in the recorded
go the shots met it where it had moved to in that tic, a few units on. So now
and then a shot that missed (or hit another monster) in the last go hits a
monster now that the record has not hurt then: in 3 of 8 MODE=9 runs with
plasma, one or two such hits of 10 to 30 among 22 to 39 replayed ones (where
logged, the nearest recorded fall of that monster was 7 and 44 tics away).
By rule 3 it is counted (the monster stays on the demo and wakes that much
weaker); it never wakes anything. Posing a tic ahead would close most of it
but moves every demo by a tic (MAP31's tests too); not done. A note: a monster
on the demo is recorded in the go being played with the demo's health
(`rail.hp`, not less `dmg`), so in a third go an earlier self's new hit (room
4) is new to that record too and is counted again; one that `Fell` is recorded
dead, and in the next go it dies when it died.

**Tests.**
- New MODE=9 (`tools/smoke_MAP32_9.cfg`, `GhostShotScript` in map32.zs; hooks
  `GsDamaged` from map32's `WorldThingDamaged`, `GsDied` from time.zs's
  `WorldThingDied`): entered at room 3's lobby as MODE=5 and 7. Go 1, the bait in
  the chamber by door 3, shoots rockets at the weakest monster in sight until
  one it hurt dies (at most 40; with plasma, 48 shots often killed nothing),
  then plasma twice each at two monsters of 300 health or more, and leaves by
  door 3 (`begun9`, `baitShoots3`: one it hurt dead, one
  alive, every shot written down). Go 2 stays in box 1 and touches nothing:
  `inTheBox9`; `myEarlierSelfsShotsWakeNone3` (no monster of the hall awake and
  none after the player while the demo played, replayed hits seen);
  `hurtOnceNotTwice3` (those it hurt and did not kill wake at the demo's end
  with the record's last health less what was counted on them, below their
  spawn health; one that fell of what was counted fell once; and every hit of
  the earlier self that was counted had no recorded fall of that monster within
  4 tics: logged with its distance); `diedWhenItDied3`
  (the one it killed died once, on the demo, within a tic of when it died).
  Under the old rule (checked once, the old line patched back in): all three
  fail (5 awake while the demo played, one after the player, woken with more
  or less than the record's health).
- MODE=3 room 4: new `hurtButOnTheDemo4` (go 2, K4P + 300, before the player
  fires: the earlier self's rockets have hit the pen, the hurt ones carry
  `ghostDmg`, every living pen monster is on the demo, none after the player).
  `myEarlierSelfHurtsThem4` asserted only hits and is unchanged, but its count
  of "my" hits no longer counts a `Fell` kill (the player is its source; it is
  told by `DMG_FORCED`, counted as `penFell`): the first run after the change
  failed on exactly that. New `killedOnTheDemo4` (K4P + 375): what the earlier
  self's rockets counted killed a pen monster on the demo (`penFell > 0`; 1, 2
  and 1 in the three final runs).
- **Results** (2026-11-20, full build, each suite alone under a shared lock):
  MAP32 MODE=3 61 of 61 (59 before, plus hurtButOnTheDemo4 and
  killedOnTheDemo4) in each of three runs; MODE=9 6 of 6 in each of three runs
  (11, 34 and 33 replayed hits; 0, 0 and 1 counted: 1 point of rocket splash,
  the nearest recorded fall 11 tics away); MODE=5 23, MODE=7 18, MODE=8 5, MODE=4 7,
  SHUT 3 20, SHUT 4 7, PRESS 3 13, PRESS 4 5, MAP31 6 9, MAP31 7 15, all pass.
  Flaky, not of this change (nothing of it runs there: no earlier self shoots
  in them): MODE=7 `guardsWakeAsIStepIn3` failed once (one of two guards still
  on the demo 10 tics after the landing), then passed 3 of 3; PRESS 3
  `killsAreMine` failed once (a sixth kill from elsewhere, as noted for it
  before), then passed 2 of 2.

**The megasphere in room 3's cage** ("once taken, never restored there, even
when I restart the level"). A scratch script (MODE=10, not kept) tried, on one
full build: at a fresh start of the level with the skill cvar 2 (what
`+skill 2` sets, "Resident", also the smoke runs' default) it is there; the
thing has skill1 to skill5 set in MAP32's TEXTMAP (udmf.py thins only
monsters). Every box used, taken in the last go, the player killed: the fight
begins anew by itself (`Rescue`, `FightAnew(mo, true)`) and it is back. Begun
anew by the plate twice in a row, taken before each: back each time. All pass.
The one path that loses it: once the fight is WON, the same plate is the room
of goes' (`UseFightAnew` -> plate.zs `Anew`), which forgets goes and puts the
doors back but no pick-ups; taken after the win (or before it), it does not
come back for the rest of the level (a scratch check `backAfterTheWinsPlate`
failed, as the code says). A fresh start of the level (`map MAP32`, the new
game, the show's end's `ChangeLevel`: there is no hub in mapinfo) has it. Not
tried: GZDoom, when the player dies in single play, loads the last save made
(autosave or one's own) if there is one, else restarts the map; a save made
after taking it brings it back taken. Nothing was changed for it: whether a won
fight's plate should give back the hall's pick-ups is a design question.

**Not tested.** That a monster killed by `Fell` never had the player as its
target first is not asserted (the code clears it). Rule 6 (a guard hurt only by
an earlier self wakes idle) has no check. A third go with two earlier selves shooting in room 3 is not run. A monster on
the demo hit by a new earlier-self hit may show its pain frame for a tic before
the next pose.
- **Not played by hand**: `MAP=MAP32 ./run.sh` in the worktree.

## The paradox: touching an earlier self ends the universe (built 2026-11-20)

Agreed with Vadim: in a room of goes the player must not touch a copy of
themselves. Touching one is a time paradox and the whole universe explodes:
the level is lost and begins again from its start. Until now the present
self walked through the copies as through scenery. The engine piece is
`src/zscript/paradox.zs` (new), hooked into `GoesTick` and `GoTake`
(plate.zs) and into `WorldTick` and `RenderOverlay` (time.zs); the headers
of plate.zs and time.zs (the zone contract and `AjarGhost`) say so.

- **Where** (`ParadoxHere`, the one place to change it): a room of goes
  proper, an `AjarZone` hall with `args[4]` 2, while it is on (`goes`, and
  not `goesWon`): MAP32's rooms 1, 2 and 5, the labs PLATE, TWOKEY and
  SHUT's room A. Not in an open fight (MAP31), not in a fight of goes
  (`args[4]` 3: MAP32's rooms 3 and 4, SHUT's room B, PRESS), and not after
  such a fight is won and has become a room of goes (`goesWon`).
- **Touching** is the bodies overlapping: |dx| and |dy| both less than the
  two radii (16 + 16) and the heights overlapping (`Touching`). Nothing comes
  before it: no warning, sound, glare or hint.
- **What counts**: a copy (`ghosts[i]`) while its record runs (`ot` less
  than its take's length; a copy whose time is up is gone, or runs to its
  door if that go was killed, and does not count) and while its middle is in
  the hall (`Where`: this room, box 0). Nothing counts while the player's
  middle is not in the hall (in the box).
- **The start of a go** (`parted`, per copy): set the first tic the player
  does not overlap copy i, wherever the two are (in the box too); cleared in
  `GoTake`, that is at the start of every go, by begin anew and at a room's
  first go. A copy can be touched only once it is set. So the selves who
  start together in the box are safe until they part, and a self who walks
  a copy's path with it and never parts from it is safe all along (Claude's
  reading: once parted, the next overlap anywhere in the hall counts).
- **The touch** (`EndUniverse`): the flag `paradox` and the count
  `paradoxes`; under `ajar_autotest` a line `AJARTEST info paradox t=<maptime>
  go=<this go> ot=<its tic> copy=<the copy's go> at=(x,y,z) me=(x,y,z)`. The
  touched copy is destroyed. The player's cheats (god mode and god mode 2,
  buddha and buddha 2, frozen) and `bBuddha`, `bInvulnerable` and
  `bNoDamage` are taken off and they are given `TELEFRAG_DAMAGE` forced
  (`DMG_FORCED | DMG_NO_ARMOR | DMG_THRUSTLESS`): dead through anything, and
  gibbed. From that tic `WorldTick` does nothing but `ParadoxTick` and the
  tests: no `GoesTick` (so no `GoesKilled` into the box), no `Rescue`, no
  `GoOnAs`, no beginning anew, no copies or doors played; the go's clock is
  not drawn. The engine begins the level again when the player presses USE,
  as after any death in Doom (no save or checkpoint of ours). The other
  copies stand still where they were (Claude's choice: time has stopped, and
  plates and doors do not change under the dead player).
- **What is seen and heard** (Claude's choices within the brief): at the
  touch a white flash over the whole screen (`A_SetBlend` alpha 1, fading
  over 50 tics), the BFG's blast, a rocket's and a barrel's at full volume
  heard everywhere (`ATTN_NONE`), the screen shaking (`A_QuakeEx` 6/6/4 for
  50 tics around the player) and four big explosions where the two met; then
  for 35 tics a ring of explosions spreads from the point of touch to the
  farthest corner of the room's zones (3 to 10 a tic, more as it widens),
  and explosions go off all over what it has reached (random places in the
  room's zones, up to 8 a tic) for 70 tics, fewer at the end; only where the
  room is (inside its zones, in a sector with room), with a rocket's sound
  every 4 tics, fading. The hit's red (`damagecount`) is cleared so that the
  flash is white, and the body does not slide on. The explosion is the rocket's (`MISL`
  B to D, bright, added, a little rising, sizes varied), as the Icon of Sin's
  death has them: `AjarParadoxBlast`, harmless, touches nothing. The
  message, as the others (`Say`, MidPrint) but each line in red (`\cg`) so
  that it reads on the white: "PARADOX / You touched your earlier self. /
  This universe is over.", said again at 90 and 180 tics so that it stays
  about eight seconds.
- **The test**: `MAP=PLATE MODE=5` (new: `ParadoxScript` in plate.zs,
  `tools/smoke_PLATE_5.cfg`, TIMEOUT 170). Go 1 is short; goes 2 and 3 are
  put on one spot in the box at their tic 1 and walk one path east into the
  hall: `startTogetherIsSafe` (tic 40 of go 3: overlapping the copy of go 2,
  both in the hall, no paradox). Begin anew; go 1 is short, go 2 stands at
  (-300, 256) in the box till 61; go 3 steps 48 clear of it and back into it:
  `inTheBoxIsSafe` (overlapping, both in the box, parted, no paradox); at 90
  it stands on the spot where go 2's record ended, at the time door:
  `afterItsTimeIsSafe`; then it stands at (300, 150) in the hall from 100 to
  200. Go 4 stands 34 east of that spot; at 120 it is given blue armour and
  invulnerability; `nearIsSafe` at 125 (34 apart, both in the hall, parted,
  no paradox); then it walks west at 4 a tic and touches the copy at tic 126:
  `touchIsParadox` (at the touch: flag set and counted once, the copy of go 3
  touched, health 0 or less with god mode on, the copy gone, the message
  said once, four takes; 70 tics later: still dead, still in the hall where
  it fell (not put in a box, not moved onto a copy), the room still on with
  four takes and its tic stopped, counted once). The level is not left (the
  cfg quits), so there is no `levelExited`. Screenshots before and 2, 14, 39 and
  99 tics after the touch.
- **The walk-throughs.** A dry build (every touch logged and nothing done,
  removed again) was run over every walk-through in scope, after the changes
  found by reading the scripts; it found one more (MAP32 room 5, go 3). What
  was changed, all in the present self's places and timing:
  - MAP32 MODE=3 room 2, go 3: waited at B's mouth (3696, 600), where the
    second self stands to hang b until join2 + 4: now 40 behind it, at
    (3696, 560), and walks through B from there (the brief's own example).
  - MAP32 MODE=3 room 5, go 3: went into F1's mouth at tic 5, where the first
    self stands hanging GREEN till 11 (found by the dry run, at go 3 tic 7):
    now at 12; and once through it stood where the second self's walk
    through F1 ends (25 to 39): now it steps aside to (9100, 520) at 28.
  - MAP32 MODE=3: `noParadox1`, `noParadox2`, `noParadox5` (the count is
    still 0 at the end of rooms 1, 2 and 5).
  - MAP32 MODE=4 room 5, go 2: waited at (8232, 240), right where the third
    self comes in by door 1: now at (8400, 240).
  - PLATE MODE=3, go 3: walked through RED at 66 on the second self's heels
    (same spot, same tic, after having parted from it): now through RED at 96
    and through BLUE at 120 (the second self holds BLUE from 90 to 150);
    `throughAgain` moved to 112.
  - PLATE MODE=4: every go walked out by the time door at tic 22, on the
    heels of the copies that did the same: now go n at 12 + 10n; and go 2,
    which took RED where the first self takes it at 10, steps away to
    (150, 380) at 6.
  - TWOKEY MODE=3, step 1, go 2: came out of A's mouth into the first self,
    which stands there till 330: now walks through the Pair at 334 instead of
    314 (it is joined for good); `throughThePair` and the walk out follow.
  - Not changed: MAP32 room 1, SHUT MODE=3 and MODE=4 (SHUT 4's room of goes
    is left at once; its room B is a fight of goes).
  The changes but the room 5 one were found by reading the recorded places;
  they were not each confirmed by a run without them.
- **For fights, later**: Vadim agreed that in MAP31's halls a copy standing
  on the rewind plate or in a box will not count (so that the next copy can
  use the plate), and that fights are to be decided after he has played the
  puzzle rooms. Only `ParadoxHere` (and what counts in `ParadoxWatch`) needs
  to change.
- **Results** (2026-11-20, full build, each suite alone under the shared
  lock; counts are the distinct `AJARTEST name=1` lines, `levelExited`
  included where the level is left): `MAP=PLATE MODE=5` 5 of 5 in each of
  three runs (no `levelExited`: the cfg quits). `MAP=MAP32 MODE=3
  TIMEOUT=850`: 70 of 70 and out (67 as before and the three `noParadox`),
  70 of 70, then 69 of 70 with `myEarlierSelfHurtsThem4=0` (room 4, a fight
  of goes where the rule is off; no paradox in the run); run twice more: 70 of 70 and out
  both times (so a flake, 1 in 5 runs; not touched by this change). Once
  each: MAP32 MODE=4 7, MODE=5 23, MODE=7 18, MODE=8 5; TWOKEY 3 8; SHUT 3
  20, SHUT 4 7; PLATE 3 23 (22 and out; the raw count of `=1` lines is 33,
  not 34, because the log repeats a part of itself at the end and the part
  is a line shorter), PLATE 4 6; PRESS 3 13, PRESS 4 5; MAP31 6 9, MAP31 7
  15. No paradox in any walk-through.
- **Not tested**: a touch in MAP32, TWOKEY or SHUT (only in PLATE); a touch
  where the copy is above or below the player (heights); a crouching
  player; the copy of a go that was killed (it runs to its door after its
  time and does not count); what USE does after it (the engine's own
  restart, as after any death: GZDoom may load its autosave of the level's
  start); the sounds (the tests run with `-nosound`); several copies touched
  in one tic (the first in go order counts).
- **Not played by hand.**

## MAP16: the way to the night room was shut by a platform (fixed 2026-11-21)

`tools/map_institute6.py` (the test hall's south-east platform and three of
its monsters, a phrase of the docstring), `src/zscript/map16.zs` (the
walkthrough's last stretch, one view), `tools/smoke_MAP16_1.cfg` and
`_2.cfg` (longer). **Not played by hand.**

**What Vadim found** (2026-11-21, playing): in the test hall with VIOLET and
no way on. The corridor to the night room, `rect(1232, -1840, 1440, -1792)`
on the top floor (384), opens off the hall's east wall at its south end, and
the hall's south-east platform (64 high) stood right in front of that mouth,
`(1104, -1840, 1232, -1776)`. The level has no jumping and a step is 24 at
most: nobody got onto the platform from the hall floor, nor back onto it from
the corridor. So VIOLET could not be carried to the brass frame, and whoever
came into the night room by VIOLET's far side could not get out to the hatch.
The PUZZLE graph had both walks (`test`-`night` and back), so the solver was
happy.

**Why no check caught it**: the walkthrough posed the player from the test
hall straight into the night room (`Pose(mo, 1600, -1648, ...)`), and
`itemcheck.py` seeds its walk from every line with an id, so the corridor
counted as reached from the night room's frame. Nothing walked that stretch.

**The change**: the platform moved 64 north, to `(1104, -1776, 1232, -1712)`;
the cell in front of the mouth is plain hall floor and the corridor opens at
floor level both ways (checked in the built map: the line (1232,-1840)-(1232,
-1792) has floor 384 on both sides). The north-east platform stays. The
revenant on it went with it, (1168, -1808) to (1168, -1744); the hell knight
that would have hung over its new edge, (1150, -1720), stands on the hall
floor at (1040, -1760), and the imp beside it moved 10 south to
(1040, -1810) to keep clear of it. Same monsters, same kinds, nothing heavy
left the hall. `fitted()` already had grid lines at -1776 and -1712, so no
new cuts.

**The walkthrough** now walks it: from the hall floor west of the mouth,
(1060, -1816) facing east, 30 tics into the corridor
(`intoTheCorridorOnFoot`), turned round, 30 tics west back onto the hall
floor (`backOutOfTheCorridor`: the way back was shut too), turned again, 36
tics east to the corridor's far end (`inTheCorridorAgain`, x 1376..1440),
turned north and 14 tics through the gap into the night room
(`intoTheNightRoomOnFoot`); only then the step at the frame as before. Each
turn is a `Pose` at the spot the player has reached (the last one snaps x to
1408, from about 1401). `smoke_MAP16_1.cfg` runs 1660 tics (was 1460).

**Checks**: mapcheck 308 sectors, 0 problems; thingcheck 0; itemcheck 0.
Full `./build.sh`: passes, every level solvable with 0 stuck; MAP16 **10
door actions, 9529 states, 0 stuck**, as before.

**Tests**:
- `MAP=MAP16 tools/smoke.sh` (walkthrough): 48 checks (44 before, plus
  `intoTheCorridorOnFoot`, `backOutOfTheCorridor`, `inTheCorridorAgain`,
  `intoTheNightRoomOnFoot`), all pass, out by the brass frame
  (`levelExited`); twice. (Counted as distinct names; the log repeats its
  first part, so the raw count of `=1` lines is 60.) The first try failed
  `inTheCorridorAgain`: 30 tics east from where the walk back had stopped
  ended at x 1364, short of the box; 36 tics end at 1401.
- `MAP=MAP16 MODE=3 TIMEOUT=1000`: all pass (45 check lines, 38 names: the
  second round repeats seven), to phase 15 at tic 6125; once.
- `MAP=MAP16 MODE=2 EXTRA=-nomonsters`: 22 views (21 before). New, view 20:
  from the hall floor at (980, -1790) facing 355, the moved platform on the
  left, the corridor running east from the hall's south-east corner at floor
  level, the walls over the mouth and behind the platform textured as the
  rest. `smoke_MAP16_2.cfg` takes one more screenshot.

**Open (not done)**: other levels' walkthroughs may also pose the player over
a stretch nobody walks, as this one did; a check of that kind (for each
`walk` edge in a PUZZLE graph, a path on foot in the geometry, not seeded
from frames) is not written.

## MAP32 room 3: the fight as fought, a demonstration (2026-11-21)

`DEMO=3 ./run.sh` puts a bot into room 3's lobby and lets it play the fight
as a player would, with a caption at the bottom saying what each self does
and why (`src/zscript/fightdemo.zs`, `ajar_autotest 20`; smoke test `MAP=MAP32
MODE=20 TIMEOUT=200 tools/smoke.sh`). It was also the first real test of the
fight. **It does not win.** What it shows is the plan working in parts: a
bait in the chamber, a later self at the lever pulling on them, that self
then the next bait, and the fight beginning anew after the fourth go.

- **Honest.** At its tic 2 it is put into the lobby with the pistol a fresh
  start gives (`Go`). After that: no god mode, no `SetOrigin`, no
  `GiveInventory`, no damage or missiles by script. It moves by thrust as
  the engine moves a running player (50·Speed·movefactor a tic, so at most
  about 16.7), turns at most 20° and pitches 8° a tic, picks weapons by
  `PendingWeapon`, fires by `FireWeapon` when the weapon is ready (and again
  on the refire frame, as holding the button does), takes things by walking
  over them and pulls the lever by `Used` from within use range, facing it.
  It reads the game's state (where the monsters are, the press, the demo).
  `honest=1` in the log is the check that no cheat flag or invulnerability
  was ever on.
- **The plan played** (plan 7; the others tried stay behind `+set fd_plan N`,
  see the comment at `FdPlanKnob`). Go 1, the bait: plasma rifle, BFG and
  cell pack from the lobby, then a run for the screen's plate in the
  chamber. From a box the role is chosen by what the self before did: if it
  was under the press for over two seconds, this one is the lever, else the
  bait. The lever: the box's supplies, wait for the shutter (open while the
  earlier self is under the press), up the stairs, shoot the guards through
  the bars, pull when 8 are on the demo under the press (if the press can be
  up again in time) or at the last moment of the earlier self's time; then,
  150 tics before that time is over, out by the window and down into the
  chamber as the next bait while the monsters still go where they went. A
  bait from a box walks past the monsters on the demo without touching them
  (they are not solid and do not see it) and waits on the plate; when they
  wake it fights, shooting only arch-viles and what is close, and leaves by
  door 3 or 4 at 40 health.
- **What was learned** (about 30 tuning runs of 200 s, each through two or
  three times the four goes; then the final runs below):
  - Go 1 is the hard one. It starts with a pistol, the lobby's guns take
    about 25 tics, and by 60 tics wave 1's imps, revenants and a mancubus
    stand at the lobby's mouth. Running for the chamber it got there a few
    times in some forty tries (at its tic 210 to 240, with 37 to 89
    health); otherwise it is killed in the hall or the lobby's mouth by its
    tic 70 to 260. Holding the
    lobby instead it lasts 100 to 380 tics and kills 10 to 15 of the 36.
  - A bait from a box is easy: past them on the demo every time (no run
    saw it touch one), on the plate by its tic 160 with the box's armour,
    then holding out 250 to 1000 tics.
  - Few come under the press: 6 to 10 at most while a bait holds the
    screen's plate (by door 3 about the same, on the cage's plate up to 8).
    Monsters after a target slide along the wall between hall and chamber
    towards its x (Doom's chase), so they bunch along the wall east or west
    of the mouth, and those that do come in are shot by the bait.
  - A pull on that kills 6 to 11 (the count of kills in the two seconds
    after it). A second pull in the same go gets 1 to 3. The lever's self
    reaches the lever by its tic 290 to 450 in nearly every try; after the
    earlier self's time it is killed in the wing within a few seconds, so it
    leaves before (the window).
  - The fewest left in a time through the four goes was about 14, usually
    20 to 30 (with wave 2's 13 come on the clock in the long goes); then the
    fourth go ends and the fight begins anew with all 36, so nothing carries
    over. A win needs every monster of all three waves in one time through.
  - **Dying pays better than leaving**: a self killed goes into the next box
    with `RESCUE_HEALTH` (50); a self that leaves by door 3 or 4 keeps what
    it has, which for a bait is 10 to 40. For Vadim to decide whether that
    is meant.
  - `i_timescale` (as `+set`, as `+i_timescale`, in the cfg), `-singletics`
    and a smaller screen gave no speed-up in the docker runs: every run is
    real time, about 20 s to start.
- **Final runs** (2026-11-21, full build, `MAP=MAP32 MODE=20 TIMEOUT=200
  tools/smoke.sh`, five times; each run is about 3500 tics, two times
  through and a bit). Every run `honest=1`, `goes4=1`, `won3=0`. The first
  time through the four goes: 58 s, 1 pull killing 10, at fewest 17 left;
  72 s, 1 pull 10, 12 left; 60 s, no pull, 22 left; 51 s, no pull, 19
  left; 75 s, 3 pulls killing 27, 15 left. So `pulled=1` in 3 of 5: when
  the bait from go 2 dies early the next self is a bait again, and no one
  is at the lever that time through.
- **The other suites** on the same build, once each: `MODE=3 TIMEOUT=850`
  74 of 74 and out (won3, won4, steel3, steel4 among them); `MODE=5
  TIMEOUT=200` 24 of 24; `MODE=9` 7 of 7; `MODE=7 TIMEOUT=400` 18 of 19 with
  `guardsWakeAsIStepIn3=0` (one guard of two still on the demo 10 tics
  after the step onto the landing), then 19 of 19 twice: a flake of that
  test, 1 in 3; mode 20's code does nothing outside mode 20.
- **The same seed gives the same fight**: two runs with `EXTRA="-rngseed
  7"` wrote the same log, go for go and tic for tic. The bot does not use
  the seed; without it every run differs.
- **What would make it win**, if anything: not found. The way the room
  is meant to be won needs the press to take most of the 54, which needs
  20 or more under it at once; a bait draws 6 to 10. Ideas not tried: the
  bait in the mouth itself (they come at it straight, but it is in the open
  to the whole hall), a bait that keeps moving east and west along the
  chamber's south wall, the megasphere behind the cage plate for go 1, the
  guards killed from the stairs' top before the shutter shuts.
- **Not tested**: rooms other than 3 under mode 20; `DEMO=3 ./run.sh` on
  Vadim's screen (only the docker smoke runs, software GL, 1024×640); the
  captions' size on other screens; what happens if Vadim touches the keys
  (the bot's moves are added to his); a win (none happened), so
  `FdReport`, the end caption and `steel3` in this mode were never reached.
