"""Builder rush bot with a minimal ammo lane.

This bot keeps the early game intentionally narrow:
  - The core spawns a capped rush wave toward the enemy.
  - The first two builders become titanium-line miners.
  - Everyone else lays roads toward the enemy core as quickly as possible.
  - Once the front reaches the enemy core, builders try to convert the lane into
    a gunner position that can fire directly into the core.

The rules do not allow a true zero-economy builder-only core kill: builder bots
cannot stand on the enemy core, and turrets need physical ammo stacks. The
minimal titanium tap exists only to make the rush able to finish the game.
"""

from cambc import Controller, Direction, EntityType, Environment, Position

ALL_DIRECTIONS = [d for d in Direction if d != Direction.CENTRE]
CARDINAL_DIRECTIONS = [
    Direction.NORTH,
    Direction.EAST,
    Direction.SOUTH,
    Direction.WEST,
]

MAX_BUILDERS = 18
MINER_SLOTS = 2
MINER_HEAD_START_ROUNDS = 12
EARLY_RUSH_BUILDERS = 18
LATE_WAVE_ROUND = 120
RESOURCE_RESERVE = 140


def in_bounds(ct: Controller, pos: Position) -> bool:
    return 0 <= pos.x < ct.get_map_width() and 0 <= pos.y < ct.get_map_height()


def manhattan(a: Position, b: Position) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def shift_pos(pos: Position, dx: int = 0, dy: int = 0) -> Position:
    return Position(pos.x + dx, pos.y + dy)


def nearby_core(ct: Controller, enemy: bool) -> Position | None:
    my_team = ct.get_team()
    for entity_id in ct.get_nearby_entities():
        if ct.get_entity_type(entity_id) != EntityType.CORE:
            continue
        other_is_enemy = ct.get_team(entity_id) != my_team
        if other_is_enemy == enemy:
            return ct.get_position(entity_id)
    return None


def guess_enemy_core(ct: Controller, own_core: Position, guess_slot: int = 0) -> Position:
    width = ct.get_map_width()
    height = ct.get_map_height()
    return Position(width - 1 - own_core.x, height - 1 - own_core.y)


def approach_direction(home_core: Position, enemy_core: Position) -> Direction:
    dx = enemy_core.x - home_core.x
    dy = enemy_core.y - home_core.y
    if abs(dx) >= abs(dy):
        return Direction.EAST if dx >= 0 else Direction.WEST
    return Direction.SOUTH if dy >= 0 else Direction.NORTH


def assault_tile(enemy_core: Position, approach: Direction) -> Position:
    if approach == Direction.EAST:
        return shift_pos(enemy_core, dx=-2)
    if approach == Direction.WEST:
        return shift_pos(enemy_core, dx=2)
    if approach == Direction.SOUTH:
        return shift_pos(enemy_core, dy=-2)
    return shift_pos(enemy_core, dy=2)


def lane_feed_tile(enemy_core: Position, approach: Direction) -> Position:
    return assault_tile(enemy_core, approach).add(approach.opposite())


def lane_shift(pos: Position, approach: Direction, offset: int) -> Position:
    if approach in (Direction.EAST, Direction.WEST):
        return shift_pos(pos, dy=offset)
    return shift_pos(pos, dx=offset)


def closest_spawn_tile(ct: Controller, target: Position) -> Position | None:
    core = ct.get_position()
    candidates = [
        Position(core.x + dx, core.y + dy)
        for dx in range(-1, 2)
        for dy in range(-1, 2)
    ]
    candidates.sort(key=lambda pos: (manhattan(pos, target), pos.y, pos.x))
    for pos in candidates:
        if ct.can_spawn(pos):
            return pos
    return None


def opening_spawn_tile(ct: Controller, spawned: int, approach: Direction) -> Position | None:
    core = ct.get_position()
    if approach == Direction.EAST:
        offsets = [(1, 1), (0, 1), (1, 0)]
    elif approach == Direction.WEST:
        offsets = [(-1, -1), (0, -1), (-1, 0)]
    elif approach == Direction.SOUTH:
        offsets = [(1, 1), (1, 0), (0, 1)]
    else:
        offsets = [(-1, -1), (-1, 0), (0, -1)]
    if spawned < len(offsets):
        dx, dy = offsets[spawned]
        pos = Position(core.x + dx, core.y + dy)
        if ct.can_spawn(pos):
            return pos
    return None


def preferred_cardinal_dirs(start: Position, target: Position) -> list[Direction]:
    dx = target.x - start.x
    dy = target.y - start.y
    dirs: list[Direction] = []
    if abs(dx) >= abs(dy):
        if dx > 0:
            dirs.append(Direction.EAST)
        elif dx < 0:
            dirs.append(Direction.WEST)
        if dy > 0:
            dirs.append(Direction.SOUTH)
        elif dy < 0:
            dirs.append(Direction.NORTH)
    else:
        if dy > 0:
            dirs.append(Direction.SOUTH)
        elif dy < 0:
            dirs.append(Direction.NORTH)
        if dx > 0:
            dirs.append(Direction.EAST)
        elif dx < 0:
            dirs.append(Direction.WEST)
    for fallback in CARDINAL_DIRECTIONS:
        if fallback not in dirs:
            dirs.append(fallback)
    return dirs


def preferred_move_dirs(start: Position, target: Position) -> list[Direction]:
    primary = start.direction_to(target)
    ordered = [
        primary,
        primary.rotate_left(),
        primary.rotate_right(),
        primary.rotate_left().rotate_left(),
        primary.rotate_right().rotate_right(),
        primary.rotate_left().rotate_left().rotate_left(),
        primary.rotate_right().rotate_right().rotate_right(),
        primary.opposite(),
    ]
    result: list[Direction] = []
    for direction in ordered:
        if direction != Direction.CENTRE and direction not in result:
            result.append(direction)
    return result


def maybe_heal(ct: Controller) -> bool:
    if ct.get_action_cooldown() != 0:
        return False
    for entity_id in ct.get_nearby_entities():
        if ct.get_team(entity_id) != ct.get_team():
            continue
        pos = ct.get_position(entity_id)
        if ct.get_position().distance_squared(pos) > 2:
            continue
        if ct.get_hp(entity_id) >= ct.get_max_hp(entity_id):
            continue
        if ct.can_heal(pos):
            ct.heal(pos)
            return True
    return False


def try_build_frontline_gunner(
    ct: Controller,
    enemy_core: Position,
    approach: Direction,
    lane_offset: int,
) -> bool:
    front = lane_shift(assault_tile(enemy_core, approach), approach, lane_offset)
    if not in_bounds(ct, front):
        return False
    if ct.get_position().distance_squared(front) > 2:
        return False
    if ct.can_build_gunner(front, approach):
        ct.build_gunner(front, approach)
        return True
    return False


def try_advance_lane(ct: Controller, target: Position) -> bool:
    pos = ct.get_position()
    for direction in preferred_cardinal_dirs(pos, target):
        step = pos.add(direction)
        if not in_bounds(ct, step):
            continue
        if ct.get_tile_env(step) == Environment.WALL:
            continue
        if ct.can_move(direction):
            ct.move(direction)
            return True
        if ct.get_action_cooldown() == 0 and ct.can_build_conveyor(step, direction):
            ct.build_conveyor(step, direction)
            if ct.can_move(direction):
                ct.move(direction)
            return True
    return False


def try_advance_rush(ct: Controller, target: Position) -> bool:
    pos = ct.get_position()
    for direction in preferred_move_dirs(pos, target):
        step = pos.add(direction)
        if not in_bounds(ct, step):
            continue
        if ct.get_tile_env(step) == Environment.WALL:
            continue
        if ct.can_move(direction):
            ct.move(direction)
            return True
        titanium, _ = ct.get_global_resources()
        if (
            ct.get_action_cooldown() == 0
            and titanium > RESOURCE_RESERVE
            and ct.can_build_road(step)
        ):
            ct.build_road(step)
            if ct.can_move(direction):
                ct.move(direction)
            return True
    return False


class Player:
    def __init__(self):
        self.spawned = 0
        self.birth_round: int | None = None
        self.home_core: Position | None = None
        self.enemy_core: Position | None = None
        self.approach: Direction | None = None
        self.target_slot = 0
        self.role = "rusher"
        self.role_slot = 0
        self.ore_target: Position | None = None
        self.ore_anchor: Position | None = None

    def ensure_builder_context(self, ct: Controller) -> bool:
        if self.home_core is None:
            self.home_core = nearby_core(ct, enemy=False)
        if self.home_core is None:
            return False
        if self.birth_round is None:
            self.birth_round = ct.get_current_round()
            if self.birth_round <= MINER_SLOTS:
                self.role = "miner"
                self.role_slot = self.birth_round - 1
            self.target_slot = 0
        if self.enemy_core is None:
            self.enemy_core = guess_enemy_core(ct, self.home_core, self.target_slot)
        seen_enemy = nearby_core(ct, enemy=True)
        if seen_enemy is not None:
            self.enemy_core = seen_enemy
        self.approach = approach_direction(self.home_core, self.enemy_core)
        return True

    def choose_titanium_target(self, ct: Controller) -> None:
        if self.ore_target is not None or self.home_core is None or self.enemy_core is None:
            return

        ores: list[tuple[int, int, int, Position]] = []
        feed = lane_feed_tile(self.enemy_core, self.approach)
        for pos in ct.get_nearby_tiles():
            if ct.get_tile_env(pos) != Environment.ORE_TITANIUM:
                continue
            ores.append(
                (
                    self.home_core.distance_squared(pos),
                    manhattan(pos, feed),
                    pos.y,
                    pos,
                )
            )
        ores.sort()
        if not ores:
            self.role = "rusher"
            return

        pick = min(self.role_slot, len(ores) - 1)
        self.ore_target = ores[pick][3]

        anchor_choices = []
        for direction in CARDINAL_DIRECTIONS:
            anchor = self.ore_target.add(direction)
            if not in_bounds(ct, anchor):
                continue
            anchor_choices.append(
                (
                    manhattan(anchor, self.home_core),
                    manhattan(anchor, feed),
                    anchor,
                )
            )
        if not anchor_choices:
            self.role = "rusher"
            self.ore_target = None
            return
        anchor_choices.sort()
        self.ore_anchor = anchor_choices[0][2]

    def run_core(self, ct: Controller) -> None:
        if self.enemy_core is None:
            self.enemy_core = guess_enemy_core(ct, ct.get_position(), 0)
        approach = approach_direction(ct.get_position(), self.enemy_core)
        target = lane_feed_tile(
            self.enemy_core,
            approach,
        )
        if self.spawned >= MAX_BUILDERS:
            return
        if self.spawned >= MINER_SLOTS and ct.get_current_round() <= MINER_HEAD_START_ROUNDS:
            return
        titanium, _ = ct.get_global_resources()
        if (
            self.spawned >= EARLY_RUSH_BUILDERS
            and ct.get_current_round() < LATE_WAVE_ROUND
        ):
            return
        if self.spawned >= EARLY_RUSH_BUILDERS and titanium < RESOURCE_RESERVE:
            return
        spawn_pos = opening_spawn_tile(ct, self.spawned, approach)
        if spawn_pos is None:
            spawn_pos = closest_spawn_tile(ct, target)
        if spawn_pos is not None:
            ct.spawn_builder(spawn_pos)
            self.spawned += 1

    def run_miner(self, ct: Controller) -> None:
        self.choose_titanium_target(ct)
        if self.ore_target is None or self.ore_anchor is None or self.enemy_core is None:
            self.run_rusher(ct)
            return

        if maybe_heal(ct):
            return

        if ct.get_position().distance_squared(self.ore_target) <= 2 and ct.can_build_harvester(self.ore_target):
            ct.build_harvester(self.ore_target)
            return

        if ct.get_position() != self.ore_anchor:
            if try_advance_rush(ct, self.ore_anchor):
                return

        feed = lane_feed_tile(self.enemy_core, self.approach)
        if try_build_frontline_gunner(ct, self.enemy_core, self.approach, 0):
            return
        try_advance_lane(ct, feed)

    def run_rusher(self, ct: Controller) -> None:
        if self.enemy_core is None or self.approach is None:
            return

        lane_offset = (ct.get_id() % 3) - 1

        if try_build_frontline_gunner(ct, self.enemy_core, self.approach, lane_offset):
            return

        if maybe_heal(ct):
            return

        feed = lane_shift(lane_feed_tile(self.enemy_core, self.approach), self.approach, lane_offset)
        if not in_bounds(ct, feed):
            feed = lane_feed_tile(self.enemy_core, self.approach)

        try_advance_rush(ct, feed)

    def run(self, ct: Controller) -> None:
        entity_type = ct.get_entity_type()
        if entity_type == EntityType.CORE:
            self.run_core(ct)
            return
        if entity_type != EntityType.BUILDER_BOT:
            return
        if not self.ensure_builder_context(ct):
            return
        if self.role == "miner":
            self.run_miner(ct)
        else:
            self.run_rusher(ct)
