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
