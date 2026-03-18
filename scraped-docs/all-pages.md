Title: Cambridge Battlecode

Source: https://docs.battlecode.cam/

---

## Quick start

## Install and scaffold

Install the CLI and run `cambc starter` to set up your project.

## Write your first bot

Learn the basics: spawning builder bots, placing conveyors, and harvesting resources.

## Game rules

Full game specification — map, resources, units, buildings, turrets, and win conditions.

## API reference

Every method available to your bot via the Controller object.

---

Title: Game Constants

Source: https://docs.battlecode.cam/api/constants

---

`GameConstants`:
## General

| Constant | Value | Description |
|---|---|---|
`MAX_TURNS` | 2000 | Maximum number of turns per game |
`STACK_SIZE` | 10 | Resources are moved in stacks of 10 |
`STARTING_TITANIUM` | 1000 | Each team’s initial titanium |
`STARTING_AXIONITE` | 0 | Each team’s initial axionite |

## Radii (squared)

| Constant | Value | Description |
|---|---|---|
`ACTION_RADIUS_SQ` | 2 | Default action radius for units |
`CORE_ACTION_RADIUS_SQ` | 8 | Core action radius (from centre) |
`CORE_SPAWNING_RADIUS_SQ` | 2 | Core spawning radius |
`CORE_VISION_RADIUS_SQ` | 36 | Core vision |
`BUILDER_BOT_VISION_RADIUS_SQ` | 20 | Builder bot vision |
`GUNNER_VISION_RADIUS_SQ` | 13 | Gunner vision |
`SENTINEL_VISION_RADIUS_SQ` | 32 | Sentinel vision |
`BREACH_VISION_RADIUS_SQ` | 10 | Breach vision |
`BREACH_ATTACK_RADIUS_SQ` | 5 | Breach attack cone |
`LAUNCHER_VISION_RADIUS_SQ` | 26 | Launcher vision + throw range |
`BRIDGE_TARGET_RADIUS_SQ` | 9 | Max bridge output distance² |

## Base costs (titanium, axionite)

| Constant | Value |
|---|---|
`BUILDER_BOT_BASE_COST` | (10, 0) |
`CONVEYOR_BASE_COST` | (3, 0) |
`SPLITTER_BASE_COST` | (6, 0) |
`BRIDGE_BASE_COST` | (10, 0) |
`ARMOURED_CONVEYOR_BASE_COST` | (10, 5) |
`HARVESTER_BASE_COST` | (80, 0) |
`ROAD_BASE_COST` | (1, 0) |
`BARRIER_BASE_COST` | (3, 0) |
`FOUNDRY_BASE_COST` | (120, 0) |
`GUNNER_BASE_COST` | (10, 0) |
`SENTINEL_BASE_COST` | (15, 0) |
`BREACH_BASE_COST` | (30, 10) |
`LAUNCHER_BASE_COST` | (20, 0) |

## Max HP

| Constant | Value |
|---|---|
`CORE_MAX_HP` | 500 |
`BUILDER_BOT_MAX_HP` | 30 |
`CONVEYOR_MAX_HP` | 20 |
`SPLITTER_MAX_HP` | 20 |
`BRIDGE_MAX_HP` | 20 |
`ARMOURED_CONVEYOR_MAX_HP` | 50 |
`HARVESTER_MAX_HP` | 30 |
`ROAD_MAX_HP` | 10 |
`BARRIER_MAX_HP` | 30 |
`FOUNDRY_MAX_HP` | 50 |
`MARKER_MAX_HP` | 1 |
`GUNNER_MAX_HP` | 40 |
`SENTINEL_MAX_HP` | 30 |
`BREACH_MAX_HP` | 60 |
`LAUNCHER_MAX_HP` | 30 |

## Combat

| Constant | Value | Description |
|---|---|---|
`BUILDER_BOT_SELF_DESTRUCT_DAMAGE` | 20 | Damage on self-destruct |
`HEAL_AMOUNT` | 10 | HP restored per heal action |
`GUNNER_DAMAGE` | 10 | Gunner base damage per shot |
`GUNNER_FIRE_COOLDOWN` | 1 | Turns between gunner shots |
`GUNNER_AMMO_COST` | 2 | Resources consumed per shot |
`SENTINEL_DAMAGE` | 20 | Sentinel damage per shot |
`SENTINEL_FIRE_COOLDOWN` | 4 | Turns between sentinel shots |
`SENTINEL_AMMO_COST` | 10 | Resources consumed per shot |
`BREACH_DAMAGE` | 40 | Breach direct hit damage |
`BREACH_SPLASH_DAMAGE` | 20 | Breach splash damage |
`BREACH_FIRE_COOLDOWN` | 1 | Turns between breach shots |
`BREACH_AMMO_COST` | 5 | Refined axionite per shot |
`LAUNCHER_FIRE_COOLDOWN` | 1 | Turns between launcher throws |

---

Title: Controller

Source: https://docs.battlecode.cam/api/controller

---

`Controller` object is passed to your `Player.run()` method each round. It provides all queries and actions for interacting with the game.
## Info methods

## Unit info

Return the team of the entity with the given id, or this unit if omitted.

Return the position of the entity with the given id, or this unit if omitted.

Return the current HP of the entity with the given id, or this unit if omitted.

Return the max HP of the entity with the given id, or this unit if omitted.

Return the EntityType of the entity with the given id, or this unit if omitted.

Return the facing direction of a conveyor, splitter, armoured conveyor, or turret. Raises `GameError` if the entity has no direction. Return the vision radius squared of the given unit, or this unit if omitted.

## Turret info

Return the position of the closest non-empty tile in the gunner’s facing direction, or None if nothing is in range. Only valid on gunners.

## Building info

Return the output target position of a bridge. Raises `GameError` if not a bridge. Return the resource stored in a conveyor/splitter/armoured conveyor/bridge/foundry, or None if empty. Raises `GameError` if the entity has no storage.

### Tile queries

Return the environment type (empty, wall, ore) of the tile at pos.

Return the id of the building on the tile at pos, or None if empty.

Return the id of the builder bot on the tile at pos, or None if empty.

Return True if a builder bot belonging to this team could stand on the tile (conveyor, road, or allied core, and no other builder bot).

## Nearby queries

Return all in-bounds tile positions within dist_sq of this unit (defaults to vision radius). dist_sq must not exceed the vision radius.

Return ids of all entities on tiles within dist_sq (defaults to vision radius).

Return ids of all buildings within dist_sq (defaults to vision radius).

Return ids of all units within dist_sq (defaults to vision radius).

## Map and game state

Return (titanium, axionite) in this team’s global resource pool.

## Cost getters

Every buildable entity has a cost getter that returns the current scaled `(titanium, axionite)` cost:
## Movement

Move this builder bot one step in direction. Raises `GameError` if not legal. Return True if this builder bot can move in direction this round.

## Building

Every buildable entity has `can_build_*` and `build_*` methods. All require action cooldown == 0 and sufficient resources. The `can_build_*` variants return `bool`; `build_*` returns the new entity’s `int` id or raises `GameError` if not legal.

## Directional buildings

These take `(position: Position, direction: Direction)`

— the direction the building faces:

## Bridge

Takes `(position: Position, target: Position)`

— the bridge’s output target tile (within distance² 9):

## Non-directional buildings

Take only `(position: Position)`:
## Healing & destruction

Heal all friendly entities on the tile by 10 HP. Costs one action cooldown.

Destroy the allied building at building_pos. Does **not** cost action cooldown. Return True if this builder bot can destroy the allied building.

## Markers

Place a marker with the given u32 value. Does not cost action cooldown. Max one per round.

Return True if this unit can place a marker at position this round.

## Combat

Pick up the builder bot at bot_pos and throw it to target.

Return True if this launcher can pick up and throw the bot.

## Core

Spawn a builder bot on one of the 9 core tiles. Costs one action cooldown. Returns the new entity’s id.

Return True if the core can spawn a builder at position this round.

## Debug indicators

Draw a debug line between two positions with RGB colour. Saved to the replay.

---

Title: Types & Enums

Source: https://docs.battlecode.cam/api/types

---

`cambc` module: `Team`, `EntityType`, `ResourceType`, `Environment`, `Direction`, `Position`, `GameConstants`, `GameError`, and `Controller`.
## Team

## EntityType

## ResourceType

## Environment

## Direction

## Direction methods

Return the `(dx, dy)` step for this direction. North is `(0, -1)`, East is `(1, 0)`, etc.

## Position

A named tuple with `x` and `y` integer fields.

---

Title: CLI reference

Source: https://docs.battlecode.cam/getting-started/cli

---

`cambc`

CLI is your main tool for local development, testing, and interacting with the platform. Install it with `pip install cambc`.
## Project setup

`cambc starter`

Scaffold a new Cambridge Battlecode project. Run this first after installing. `cambc.toml`

The config file created by `cambc starter`. All fields have defaults and all CLI options override config values. `cambc run` are resolved by first checking the raw path, then checking inside `bots_dir`. So `cambc run starter opponent` resolves to `bots/starter` and `bots/opponent`.
## Local development

`cambc run`

Run a local match between two bots. No time limits are enforced locally. **Arguments:**

| Argument | Description |
|---|---|
`bot_a ` | First bot — a directory containing ` main.py `, a `.py ` file, or a name in ` bots_dir` |
`bot_b ` | Second bot — same formats as ` bot_a` |
`map ` | Optional `.map26 ` map file. If omitted, uses the first map in ` maps_dir` |

**Options:**

| Option | Description |
|---|---|
`--replay PATH ` | Output replay file path (overrides ` cambc.toml` default) |
`--seed N ` | Map seed (overrides ` cambc.toml` default) |
`--watch` | Open the visualiser automatically after the match |

`cambc watch`

View a replay in the browser-based visualiser. **Local replay:** Serves the visualiser on `localhost` and opens your browser. Press `Ctrl+C` to stop the server. **Platform match:** Opens the platform visualiser in your browser for a specific match. `cambc map-editor`

Open the map editor to create custom `.map26` files.
## Platform commands

These commands interact with the online platform at game.battlecode.cam. Most require authentication via `cambc login`. `cambc login`

Authenticate with the platform. Opens a browser window for OAuth login and stores your session locally. `cambc logout`. `cambc logout`

Clear stored credentials. `cambc submit`

Upload a bot to compete on the ladder. `main.py`, a single `.py` file, or a `.zip`. Directories are auto-zipped before upload. See submission requirements for constraints. `cambc status`

Show your current team, rating, rank, and member list. `cambc unrated`

Challenge another team to an unrated match using both teams’ latest submissions.
| Option | Description |
|---|---|
`--match ID` | Use the opponent’s submission version from a specific past match instead of their latest |

`cambc test-run`

Upload two local bots and run a remote match with full time limit enforcement on AWS Graviton3 hardware. `cambc run`, this enforces the 2ms CPU time limit per round — use this to check your bot’s performance before submitting. `cambc matches`

View recent match history.
| Option | Description |
|---|---|
`--type {ladder|unrated}` | Filter by match type |
`--team NAME` | Filter by team name (substring match) |
`--limit N` | Number of matches to show (default 20, max 100) |
`--cursor CURSOR` | Pagination cursor from previous results |

---

Title: Your First Bot

Source: https://docs.battlecode.cam/getting-started/first-bot

---

## Get started with `cambc starter`

If you haven’t already, run `cambc starter` to scaffold your project. When prompted, choose to create the starter bot — it gives you a working bot to build on.
## Bot structure

Every bot is a Python file containing a `Player` class with a `run` method. The engine creates one `Player` instance per unit and calls `run(controller)` once per round. main.py

## Key concepts

One Player instance per unit

One Player instance per unit

The Controller object

The Controller object

Imports from cambc

Imports from cambc `from cambc import *` gives you all game types: `Team`, `EntityType`, `Direction`, `Position`, `ResourceType`, `Environment`, `GameConstants`, `GameError`, and `Controller`. Time limit

Time limit

Each unit gets **2ms of CPU time** per round, plus a 5% buffer that refills when you use less. Locally there are no time limits — use remote test runs to check performance on the actual hardware. No external packages

No external packages

Only Python standard library modules are available. External packages like `numpy` or `scipy` cannot be imported — bots run in a sandboxed environment with no `pip install`.

## Next steps

## Run a local match

Test your bot against itself or an example opponent.

## Game rules

Understand the full game mechanics before optimising.

## API reference

Every method available via the Controller object.

## Types and enums

All game types: Team, EntityType, Direction, Position, and more.

---

Title: Installation

Source: https://docs.battlecode.cam/getting-started/installation

---

## Requirements

**Python 3.12 or 3.13 ** (3.14 is not supported)**pip** (comes with Python)

## Install

The `cambc` package includes the full game engine compiled for your platform. Supported: macOS (Apple Silicon + Intel), Linux (x86_64 + ARM64), Windows (x86_64).

## Verify

## Set up your project

`cambc.toml` config, `bots/` and `maps/` directories, a `.gitignore`, and optionally a starter bot. See the CLI reference for details.
## What’s included

| Component | Description |
|---|---|
`cambc` CLI | Run local matches, open the visualiser, submit bots, trigger test runs |
`cambc ` Python module | Game types (` Team `, ` EntityType `, ` Direction `, ` Position`, etc.) for use in your bot code |
`titan_runner` | The compiled Rust game engine (embedded, runs locally with no time limits) |

## Next steps

## Write your first bot

Create a simple bot that spawns builders and starts harvesting.

## CLI reference

Full reference for all CLI commands.

---

Title: How Matches Work

Source: https://docs.battlecode.cam/getting-started/matches

---

## Match format

Every match consists of **5 games**. Each game is played on a different map with a different random seed. The team that wins more games wins the match.

## Win conditions per game

A game ends when:| Condition | Description |
|---|---|
Core destroyed | One team’s core reaches 0 HP |
Resources | After 2000 rounds, the tiebreaker sequence determines the winner |
Timeout | After 2000 rounds with equal tiebreakers — decided by coinflip |

## Ladder

The ladder ranks all teams by **Glicko-2** rating. New teams start unrated and are seeded to 1500 when they upload their first ready submission.

## Scheduling

Every **10 minutes**, the scheduler:

- Pairs each team with one similarly-rated opponent (greedy nearest-rating matching with small random jitter to avoid repetitive matchups)
- Avoids rematches from the last hour
- Submits matches to the runner infrastructure 
## Rating updates

Ratings are updated using **Glicko-2** after each scheduler cycle. Match outcomes use fractional scoring based on the game score (e.g., a 5-0 win counts more than a 3-2 win). Each team has three rating components: **Rating **— skill estimate (starts at 1500)** Uncertainty (RD) **— confidence in the rating (starts high, decreases with more matches)** Volatility**— expected rating fluctuation

---

Title: Running Matches

Source: https://docs.battlecode.cam/getting-started/running-matches

---

## Run a local match

**no time limits**— ideal for rapid iteration. The engine outputs a `replay.replay26` file. Bot paths can be a directory containing `main.py`, a `.py` file, or a bot name from your `bots_dir` (set in `cambc.toml`). The optional map argument is a `.map26` file — if omitted, the first map in your `maps_dir` is used.
## View a replay

## Run + watch in one command

## View a platform match

## Remote test runs

Remote commands require authentication — run `cambc login` first if you haven’t already. Test your bots on the **same hardware** that runs ladder matches, with full time limit enforcement: `test-run` must be a directory containing `main.py` or a `.zip` file (unlike `cambc run`, arbitrary `.py` files are not accepted).
## Debugging

**stdout** via `print("msg")` is captured and saved to the replay — view it per-unit in the visualiser **stderr** prints to your console in real time- Use `c.draw_indicator_line()` and `c.draw_indicator_dot()` to draw debug overlays on the map

## Next steps

## Submit your bot

Upload your bot to compete on the ladder.

## CLI reference

Full reference for all CLI commands.

---

Title: Submitting

Source: https://docs.battlecode.cam/getting-started/submitting

---

## Log in

Before submitting, authenticate the CLI with your platform account: `cambc logout`.
## Via CLI

## Via the platform

- Go to game.battlecode.cam
- Navigate to **Submissions** in the sidebar - Upload your bot zip 
## Bot requirements

Your submission must contain a `main.py` file with a `Player` class. The file can be at the root of the zip or inside a single top-level directory.
| Constraint | Limit |
|---|---|
| Zip size | 5 MB max |
| Decompressed size | 50 MB max |
| File count | 500 files max |
| Native extensions | Not allowed (`.so `, `.pyd `, `.dylib `, `.dll`) |
| Imports | Must be top-level (file I/O is blocked during `run()`) |

## What happens after upload

- Your zip is validated (structure, size, no native extensions)
- Status is set to **ready** - Your latest ready submission becomes your active bot on the ladder
- The scheduler pairs you against other teams every 10 minutes 
## Ladder

The ladder ranks all teams by Glicko-2 rating. Every 10 minutes, the scheduler creates one match per team, pairing you with a similarly-rated opponent. Each match consists of **5 games**— the team that wins more games wins the match. Ratings update after each scheduler cycle. See How matches work for details.

---

Title: Builder Bot

Source: https://docs.battlecode.cam/spec/builder-bot

---

**only mobile unit**. They construct buildings, heal friendly entities, and can self-destruct for area damage.

## Properties

| Property | Value |
|---|---|
| HP | 30 |
| Base cost | 10 Ti |
| Scaling contribution | 10% |
| Vision radius² | 20 |
| Action radius² | 2 |

## Movement

Builder bots can move to an adjacent tile (including diagonals) if their move cooldown is 0. Moving increases the cooldown by 1.

## Actions

When action cooldown is 0, a builder bot can perform one of:

### Build

Build any building or turret on a tile within action radius that doesn’t already have a building. Only walkable buildings (conveyors and roads) can be built on a tile that contains a builder bot.

## Heal

Heal all friendly entities on a tile within action radius by **10 HP**.

## Destroy

Destroy any allied building within action radius. This can be done **any number of times per round** and does **not** cost action cooldown.

## Self-destruct

A builder bot can self-destruct at any time, dealing **20 damage** to the building on the tile it is standing on.

---

Title: Conveyors

Source: https://docs.battlecode.cam/spec/conveyors

---

**one stack** of any resource, and both accept input and produce output. Basic conveyors, splitters, and armoured conveyors point in one of the **cardinal directions**.

## Conveyor

Accepts resources from any of its three non-output directions. Sends its contents in the direction it is pointing if that tile can accept a resource.| Property | Value |
|---|---|
| HP | 20 |
| Base cost | 3 Ti |
| Scaling | 1% |

## Splitter

Alternates between outputting in three directions: the primary output and the two adjacent directions. **Only accepts input from the back.** Prioritises directions used least recently.

| Property | Value |
|---|---|
| HP | 20 |
| Base cost | 6 Ti |
| Scaling | 1% |

## Bridge

Outputs its contents to a **specific tile within Euclidean distance 3** (distance² ≤ 9), chosen when built. Bridges bypass directional restrictions — they can feed any building that accepts resources. Accepts input from all directions.

| Property | Value |
|---|---|
| HP | 20 |
| Base cost | 10 Ti |
| Scaling | 1% |

## Armoured Conveyor

Same function as a basic conveyor but with **much more HP**. Requires refined axionite to build.

| Property | Value |
|---|---|
| HP | 50 |
| Base cost | 10 Ti, 5 Ax |
| Scaling | 1% |

## Resource distribution

At the end of each round (after all units have acted), resources are distributed. Buildings that have resources to output attempt to send them to adjacent buildings that can accept them. Key rules:- Resources are always moved in **stacks of 10 ** ** Resources can be sent to enemy buildings**— be careful with conveyor placement near opponents- Harvesters and splitters prioritise outputting in directions **used least recently** - Foundries require one stack each of titanium and raw axionite before outputting one stack of refined axionite
- Turrets only accept resources when completely empty

---

Title: Core

Source: https://docs.battlecode.cam/spec/core

---

**If your core is destroyed, you lose the game.** Each team starts with one core.

## Properties

| Property | Value |
|---|---|
| HP | 500 |
| Footprint | 3×3 |
| Vision radius² | 36 |
| Action radius² | 8 (from centre) |

## Spawning

The core can **spawn one builder bot per round** on any of the 9 tiles it occupies. Spawning costs one action cooldown.

---

Title: Harvester & Foundry

Source: https://docs.battlecode.cam/spec/harvester-and-foundry

---

## Harvester

Must be placed on an **ore deposit**. Outputs one stack of the corresponding resource to an adjacent building every **4 rounds**. The first output happens immediately on the round the harvester is built. Prioritises outputting in directions used least recently.

| Property | Value |
|---|---|
| HP | 30 |
| Base cost | 80 Ti |
| Scaling | 10% |
| Output interval | 4 rounds |

## Axionite Foundry

Takes one stack each of **titanium and raw axionite**, then outputs one stack of **refined axionite**. Accepts input and produces output from any side.

| Property | Value |
|---|---|
| HP | 50 |
| Base cost | 120 Ti |
| Scaling | 100% |

## Refining process

- Feed titanium (via conveyor) → foundry stores it
- Feed raw axionite (via conveyor) → foundry combines them
- Foundry outputs one stack of refined axionite to an adjacent accepting building

---

Title: Road, Barrier & Marker

Source: https://docs.battlecode.cam/spec/other-buildings

---

## Road

Walkable tiles for builder bots to move on. The cheapest building.| Property | Value |
|---|---|
| HP | 10 |
| Base cost | 1 Ti |
| Scaling | 0.5% |

## Barrier

Cheap, takes up space, and has high HP. Useful for blocking enemy paths or protecting key buildings.| Property | Value |
|---|---|
| HP | 30 |
| Base cost | 3 Ti |
| Scaling | 1% |

## Marker

A tile containing a single **unsigned 32-bit integer** that can be read by any allied unit. Building a marker is completely free and does **not** cost action cooldown — you may place at most one marker per round. Any team may build over markers, destroying them.

| Property | Value |
|---|---|
| HP | 1 |
| Cost | Free |

Markers are the **only form of communication** between allied units. Global variables are not shared between `Player` instances — each unit has its own isolated Python environment.

### Communication patterns

Since each unit’s `Player` instance is isolated, markers are essential for coordination: **Scouting reports **: Write enemy positions to markers near your core** Build orders **: Use marker values as state machine flags** Territory claims**: Mark tiles to avoid duplicate work

---

Title: Game Overview

Source: https://docs.battlecode.cam/spec/overview

---

## Background

The year is 2076. A crystalline ore called **axionite**— a room-temperature superconductor — has been discovered on Titan, Saturn’s largest moon. At least six corporations have deployed autonomous extraction fleets to Titan’s surface. Titan is lethal to humans: −179°C, a nitrogen-methane atmosphere, and a 76-minute communication delay to Earth. All operations are carried out by robots. You write the software that controls your fleet: mining ore, refining axionite, and outcompeting the enemy.

## Objective

Collect resources and **destroy the enemy’s core**. To do this, you must find ore deposits, build harvesters, deliver resources back to the core using conveyors, and expand your territory.

## Win conditions

If both cores are still alive after **2000 rounds**, the winner is decided by tiebreakers in order:

## Map

The map is a rectangular grid between **20×20** and **50×50** inclusive. The top-left (northwest) corner is position `(0, 0)`. The map is guaranteed to be **symmetric** by either reflection or rotation. Each grid cell is one of: Walls prevent building anything on the tile they occupy. Ores are tiles on which harvesters may be built to mine resources.

## Units

Units are game entities which run an **independent instance** of the code that you submit. The core, builder bots, and turrets are units. **Harvesters are not units**— they operate automatically. Each round, units take their turns **in the order they were spawned**. After all units have taken their turn, resources are distributed. See the reference tables for a quick comparison of all entity stats.

## Vision and action radius

Units have a **vision radius** and an **action radius**.
- The **vision radius** is the area in which the unit can sense its environment.
- The **action radius** is the area in which the unit can perform actions, such as building, placing markers, or destroying buildings. **attack range** which is different from their action radius — see each turret’s page for details. 
## Cooldowns

All units have **action** and **move** cooldowns which are non-negative integers that decrease by 1 at the end of each round. Actions and movement can only be performed when the respective cooldown is 0.

The move cooldown is only used by the builder bot — it is the only mobile unit.

## Markers

All units may place one marker per round on a tile within action radius. This is separate from the action cooldown. You can overwrite an existing friendly marker, but not an enemy marker.

### Self-destruct

All units may self-destruct at any time. Builder bots deal **20 damage** to the tile they are standing on upon self-destruct.

## Buildings

Buildings are game entities which are **immovable**. All entities are buildings except builder bots. In particular, the core and turrets are considered **both a unit and a building**.

## Entity IDs

All entities (buildings and units) in the game have a **unique integer ID**. All Controller methods that deal with entities accept and return these IDs. Properties of an entity can be queried with getter functions — for example, `c.get_hp(id)`. The ID-based API was chosen for performance — constructing Python objects for every entity query would be too slow within the 2ms time limit.

## Computation limit

Each unit gets **2ms of CPU time** per round. If your code exceeds this, execution is interrupted and `run()` is called fresh on the next round — **your bot does not resume where it left off**. To absorb variance, each unit has an **extra time buffer** equal to 5% of the time limit. If a round takes longer than 2ms, the overage is deducted from the buffer. If a round takes less than 2ms, the savings are refunded to the buffer (capped at 5%). Once a unit exhausts both its 2ms budget and its buffer in a single round, it is interrupted immediately. Each bot process has a **1 GB memory limit**. Exceeding this will terminate the process. Only Python standard library modules are available. External packages (e.g. `numpy`, `scipy`) cannot be imported — bots run in a sandboxed environment with no `pip install`.
## Debugging

**stdout** via `print("msg")` is captured by the engine and saved to the replay. You can view each unit’s output in the visualiser. **stderr** prints to the console in real time — use this for debugging during local runs. `c.draw_indicator_line(pos_a, pos_b, r, g, b)` and `c.draw_indicator_dot(pos, r, g, b)` draw debug overlays on the map, saved to the replay.

---

Title: Reference Tables

Source: https://docs.battlecode.cam/spec/reference

---

Every entity you build increases the cost multiplier. Scale starts at 1.0x (100%). Increases are additive — two builder bots at +10% each gives 1.2x, not 1.21x.cost=⌊scale×base cost⌋

---

Title: Resources

Source: https://docs.battlecode.cam/spec/resources

---

## Titanium

The primary resource used to construct most buildings. Each team starts with **1000 titanium**. Titanium is harvested from titanium ore deposits and delivered to the core via conveyors.

## Axionite

Axionite comes in two forms:

## Raw axionite

Mined from axionite ore deposits. When fed to a turret or core, it **decays into titanium**. Must be refined first for advanced uses. Whenever “axionite” is mentioned in the spec without qualification, it refers to **refined axionite**.

## Resource distribution

Resources are stored and moved in **stacks of 10**. At the end of each round, buildings that output resources send them to adjacent buildings that accept them. See conveyors, harvester & foundry, and turrets for details on input/output directions.

## Cost scaling

Every building and unit you construct increases the cost of future builds. The cost of every building and unit is: Where scale starts at 1.0 and increases **additively** with each entity built — two builder bots at +10% each gives 1.2x, not 1.21x. You can query the current scale with `c.get_scale_percent()` which returns it as a percentage (100.0 at base). When an entity is destroyed, its scaling contribution is removed — costs go back down.

---

Title: Turrets

Source: https://docs.battlecode.cam/spec/turrets

---

**except the launcher** faces in one of **8 directions**. Ammo must be fed to turrets via conveyors, from any direction except the direction the turret is facing. Diagonal turrets can be fed from all four sides. Ammo-based turrets can hold up to one stack of one resource type and only accept incoming resources when completely empty.

If a tile containing both a building and a unit is hit, **both** take full damage.

## Gunner

Has a vision radius of √13. Can only target the **closest non-empty tile** in the direction it is facing. Using refined axionite as ammo deals double damage.

| Property | Value |
|---|---|
| HP | 40 |
| Base cost | 10 Ti |
| Scaling | 10% |
| Damage | 10 (20 with refined axionite) |
| Reload | 1 round |
| Ammo per shot | 2 |
| Vision r² | 13 |
| Attack r² | 13 (same as vision) |

- Cardinal
- Diagonal 
## Sentinel

High range, low damage support turret. Can hit all tiles within **1 king move** (Chebyshev distance) of the straight line in its facing direction, within vision range. Using refined axionite instead of titanium as ammo adds **+3 to the action and move cooldown** of any unit directly hit — acting as a stun.

| Property | Value |
|---|---|
| HP | 30 |
| Base cost | 15 Ti |
| Scaling | 10% |
| Damage | 20 |
| Reload | 4 rounds |
| Ammo per shot | 10 |
| Vision r² | 32 |
| Attack r² | 32 (same as vision) |

- Cardinal
- Diagonal 
## Breach

Very high damage with **splash**. Attacks in a **180° cone** in the facing direction.

| Property | Value |
|---|---|
| HP | 60 |
| Base cost | 30 Ti, 10 Ax |
| Scaling | 10% |
| Damage | 40 direct + 20 splash (8 surrounding tiles) |
| Reload | 1 round |
| Ammo per shot | 5 (refined axionite only) |
| Vision r² | 10 |
| Attack r² | 5 |

- Cardinal
- Diagonal 
## Launcher

Picks up and **throws adjacent builder bots** to a target tile within range. The target tile must be bot-passable. Unlike other turrets, launchers have **no facing direction** and do not use ammo.

| Property | Value |
|---|---|
| HP | 30 |
| Base cost | 20 Ti |
| Scaling | 10% |
| Reload | 1 round |
| Vision r² | 26 |
| Attack r² | 26 (same as vision) |
