Title: Controller

Source: https://docs.battlecode.cam/api/controller

---

Complete reference for all Controller methods available to your bot.

The `Controller` object is passed to your `Player.run()` method each round. It provides all queries and actions for interacting with the game.

```
class Player:
    def run(self, c: Controller):
        # c is the Controller for this unit
        pos = c.get_position()
```

##  Info methods

###  Unit info

get\_team(id: int | None = None)

Team

Return the team of the entity with the given id, or this unit if omitted.

get\_position(id: int | None = None)

Position

Return the position of the entity with the given id, or this unit if omitted.

get\_id()

int

Return this unit’s entity id.

get\_action\_cooldown()

int

Return this unit’s current action cooldown. Actions require cooldown == 0.

get\_move\_cooldown()

int

Return this unit’s current move cooldown. Movement requires cooldown == 0.

get\_hp(id: int | None = None)

int

Return the current HP of the entity with the given id, or this unit if omitted.

get\_max\_hp(id: int | None = None)

int

Return the max HP of the entity with the given id, or this unit if omitted.

get\_entity\_type(id: int | None = None)

EntityType

Return the EntityType of the entity with the given id, or this unit if omitted.

get\_direction(id: int | None = None)

Direction

Return the facing direction of a conveyor, splitter, armoured conveyor, or turret. Raises `GameError` if the entity has no direction.

get\_vision\_radius\_sq(id: int | None = None)

int

Return the vision radius squared of the given unit, or this unit if omitted.

###  Turret info

get\_ammo\_amount()

int

Return the amount of ammo this turret currently holds.

get\_ammo\_type()

ResourceType | None

Return the resource type loaded as ammo, or None if empty.

get\_gunner\_target()

Position | None

Return the position of the closest non-empty tile in the gunner’s facing direction, or None if nothing is in range. Only valid on gunners.

###  Building info

get\_bridge\_target(id: int)

Position

Return the output target position of a bridge. Raises `GameError` if not a bridge.

get\_stored\_resource(id: int | None = None)

ResourceType | None

Return the resource stored in a conveyor/splitter/armoured conveyor/bridge/foundry, or None if empty. Raises `GameError` if the entity has no storage.

###  Tile queries

get\_tile\_env(pos: Position)

Environment

Return the environment type (empty, wall, ore) of the tile at pos.

get\_tile\_building\_id(pos: Position)

int | None

Return the id of the building on the tile at pos, or None if empty.

get\_tile\_builder\_bot\_id(pos: Position)

int | None

Return the id of the builder bot on the tile at pos, or None if empty.

is\_tile\_empty(pos: Position)

bool

Return True if the tile has no building and is not a wall.

is\_tile\_passable(pos: Position)

bool

Return True if a builder bot belonging to this team could stand on the tile (conveyor, road, or allied core, and no other builder bot).

is\_in\_vision(pos: Position)

bool

Return True if pos is within this unit’s vision radius.

###  Nearby queries

get\_nearby\_tiles(dist\_sq: int | None = None)

list[Position]

Return all in-bounds tile positions within dist\_sq of this unit (defaults to vision radius). dist\_sq must not exceed the vision radius.

get\_nearby\_entities(dist\_sq: int | None = None)

list[int]

Return ids of all entities on tiles within dist\_sq (defaults to vision radius).

get\_nearby\_buildings(dist\_sq: int | None = None)

list[int]

Return ids of all buildings within dist\_sq (defaults to vision radius).

get\_nearby\_units(dist\_sq: int | None = None)

list[int]

Return ids of all units within dist\_sq (defaults to vision radius).

###  Map and game state

get\_map\_width()

int

Return the width of the map in tiles.

get\_map\_height()

int

Return the height of the map in tiles.

get\_current\_round()

int

Return the current round number (starts at 1).

get\_global\_resources()

tuple[int, int]

Return (titanium, axionite) in this team’s global resource pool.

get\_scale\_percent()

float

Return this team’s current cost scale as a percentage (100.0 = base cost).

get\_cpu\_time\_elapsed()

int

Return the CPU time elapsed this round in microseconds.

##  Cost getters

Every buildable entity has a cost getter that returns the current scaled `(titanium, axionite)` cost:

```
c.get_conveyor_cost()           # -> (int, int)
c.get_splitter_cost()
c.get_bridge_cost()
c.get_armoured_conveyor_cost()
c.get_harvester_cost()
c.get_road_cost()
c.get_barrier_cost()
c.get_gunner_cost()
c.get_sentinel_cost()
c.get_breach_cost()
c.get_launcher_cost()
c.get_foundry_cost()
c.get_builder_bot_cost()
```

##  Movement

move(direction: Direction)

None

Move this builder bot one step in direction. Raises `GameError` if not legal.

can\_move(direction: Direction)

bool

Return True if this builder bot can move in direction this round.

##  Building

Every buildable entity has `can_build_*` and `build_*` methods. All require action cooldown == 0 and sufficient resources. The `can_build_*` variants return `bool`; `build_*` returns the new entity’s `int` id or raises `GameError` if not legal.

###  Directional buildings

These take `(position: Position, direction: Direction)` — the direction the building faces:

```
c.build_conveyor(pos, direction)          c.can_build_conveyor(pos, direction)
c.build_splitter(pos, direction)          c.can_build_splitter(pos, direction)
c.build_armoured_conveyor(pos, direction) c.can_build_armoured_conveyor(pos, direction)
c.build_gunner(pos, direction)            c.can_build_gunner(pos, direction)
c.build_sentinel(pos, direction)          c.can_build_sentinel(pos, direction)
c.build_breach(pos, direction)            c.can_build_breach(pos, direction)
```

###  Bridge

Takes `(position: Position, target: Position)` — the bridge’s output target tile (within distance² 9):

```
c.build_bridge(pos, target)               c.can_build_bridge(pos, target)
```

###  Non-directional buildings

Take only `(position: Position)`:

```
c.build_harvester(pos)                    c.can_build_harvester(pos)
c.build_road(pos)                         c.can_build_road(pos)
c.build_barrier(pos)                      c.can_build_barrier(pos)
c.build_foundry(pos)                      c.can_build_foundry(pos)
c.build_launcher(pos)                     c.can_build_launcher(pos)
```

##  Healing & destruction

heal(position: Position)

None

Heal all friendly entities on the tile by 10 HP. Costs one action cooldown.

can\_heal(position: Position)

bool

Return True if this builder bot can heal the tile this round.

destroy(building\_pos: Position)

None

Destroy the allied building at building\_pos. Does **not** cost action cooldown.

can\_destroy(building\_pos: Position)

bool

Return True if this builder bot can destroy the allied building.

self\_destruct()

None

Destroy this unit. Builder bots deal 20 damage to their tile.

resign()

None

Forfeit the game immediately. Destroys this team’s core, ending the game as a loss.

##  Markers

place\_marker(position: Position, value: int)

None

Place a marker with the given u32 value. Does not cost action cooldown. Max one per round.

can\_place\_marker(position: Position)

bool

Return True if this unit can place a marker at position this round.

get\_marker\_value(id: int)

int

Return the u32 value stored in the friendly marker.

##  Combat

fire(target: Position)

None

Fire this turret at target. Use `launch()` for launchers.

can\_fire(target: Position)

bool

Return True if this turret can fire at target this round.

launch(bot\_pos: Position, target: Position)

None

Pick up the builder bot at bot\_pos and throw it to target.

can\_launch(bot\_pos: Position, target: Position)

bool

Return True if this launcher can pick up and throw the bot.

##  Core

spawn\_builder(position: Position)

int

Spawn a builder bot on one of the 9 core tiles. Costs one action cooldown. Returns the new entity’s id.

can\_spawn(position: Position)

bool

Return True if the core can spawn a builder at position this round.

##  Debug indicators

draw\_indicator\_line(pos\_a: Position, pos\_b: Position, r: int, g: int, b: int)

None

Draw a debug line between two positions with RGB colour. Saved to the replay.

draw\_indicator\_dot(pos: Position, r: int, g: int, b: int)

None

Draw a debug dot at a position with RGB colour. Saved to the replay.

⌘I
