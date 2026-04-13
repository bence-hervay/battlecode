"""Builder rush bot with a minimal sentinel siege.

This bot keeps the early game intentionally narrow:
  - The core spawns a capped rush wave toward the enemy.
  - The first two builders become titanium-line miners.
  - Everyone else lays roads toward the enemy core as quickly as possible.
  - Once the front reaches the enemy core, builders set up a diagonal sentinel
    backed by a bridge-fed ammo lane.

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
LANE_PATTERN = [0, -1, 1, -2, 2]
RECENT_HISTORY = 10


def in_bounds(ct: Controller, pos: Position) -> bool:
    return 0 <= pos.x < ct.get_map_width() and 0 <= pos.y < ct.get_map_height()


def manhattan(a: Position, b: Position) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def shift_pos(pos: Position, dx: int = 0, dy: int = 0) -> Position:
    return Position(pos.x + dx, pos.y + dy)


def same_pos(a: Position | None, b: Position | None) -> bool:
    return a is not None and b is not None and a.x == b.x and a.y == b.y


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


def step_sign(delta: int) -> int:
    if delta > 0:
        return 1
    if delta < 0:
        return -1
    return 0


def diagonal_direction(dx_sign: int, dy_sign: int) -> Direction:
    if dx_sign > 0 and dy_sign > 0:
        return Direction.SOUTHEAST
    if dx_sign > 0 and dy_sign < 0:
        return Direction.NORTHEAST
    if dx_sign < 0 and dy_sign > 0:
        return Direction.SOUTHWEST
    return Direction.NORTHWEST


def siege_vector(home_core: Position, enemy_core: Position) -> tuple[int, int]:
    return step_sign(home_core.x - enemy_core.x), step_sign(home_core.y - enemy_core.y)


def lane_vector(home_core: Position, enemy_core: Position) -> tuple[int, int]:
    sx, sy = siege_vector(home_core, enemy_core)
    return -sy, sx


def sentinel_candidates(home_core: Position, enemy_core: Position) -> list[Position]:
    sx, sy = siege_vector(home_core, enemy_core)
    return [
        Position(enemy_core.x + sx * dist, enemy_core.y + sy * dist)
        for dist in (4, 3, 2)
    ]


def bridge_candidates(home_core: Position, enemy_core: Position, sentinel: Position) -> list[Position]:
    sx, sy = siege_vector(home_core, enemy_core)
    return [
        Position(sentinel.x + sx, sentinel.y),
        Position(sentinel.x, sentinel.y + sy),
    ]


def staging_tile(home_core: Position, enemy_core: Position) -> Position:
    sentinel = sentinel_candidates(home_core, enemy_core)[0]
    sx, sy = siege_vector(home_core, enemy_core)
    return Position(sentinel.x + sx, sentinel.y + sy)


def reserved_front_tiles(ct: Controller, home_core: Position, enemy_core: Position) -> set[tuple[int, int]]:
    blocked: set[tuple[int, int]] = set()
    for sentinel in sentinel_candidates(home_core, enemy_core):
        if not in_bounds(ct, sentinel):
            continue
        blocked.add((sentinel.x, sentinel.y))
        for bridge in bridge_candidates(home_core, enemy_core, sentinel):
            if in_bounds(ct, bridge):
                blocked.add((bridge.x, bridge.y))
    return blocked


def clamp_pos(ct: Controller, pos: Position) -> Position:
    return Position(
        min(max(pos.x, 0), ct.get_map_width() - 1),
        min(max(pos.y, 0), ct.get_map_height() - 1),
    )


def wall_like(ct: Controller, pos: Position) -> bool:
    return not in_bounds(ct, pos) or ct.get_tile_env(pos) == Environment.WALL


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


def preferred_cardinal_dirs(
    start: Position,
    target: Position,
    wall_hand: int = 0,
) -> list[Direction]:
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
    fallback_order = CARDINAL_DIRECTIONS[:]
    if wall_hand < 0:
        fallback_order = [
            Direction.NORTH,
            Direction.WEST,
            Direction.SOUTH,
            Direction.EAST,
        ]
    elif wall_hand > 0:
        fallback_order = [
            Direction.SOUTH,
            Direction.EAST,
            Direction.NORTH,
            Direction.WEST,
        ]
    for fallback in fallback_order:
        if fallback not in dirs:
            dirs.append(fallback)
    return dirs


def preferred_move_dirs(
    start: Position,
    target: Position,
    wall_hand: int = 0,
) -> list[Direction]:
    primary = start.direction_to(target)
    if wall_hand == 0:
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
    else:
        first_turn = primary.rotate_left() if wall_hand < 0 else primary.rotate_right()
        second_turn = primary.rotate_right() if wall_hand < 0 else primary.rotate_left()
        ordered = [
            primary,
            first_turn,
            second_turn,
            first_turn.rotate_left() if wall_hand < 0 else first_turn.rotate_right(),
            second_turn.rotate_right() if wall_hand < 0 else second_turn.rotate_left(),
            primary.rotate_left().rotate_left().rotate_left(),
            primary.rotate_right().rotate_right().rotate_right(),
            primary.opposite(),
        ]
    result: list[Direction] = []
    for direction in ordered:
        if direction != Direction.CENTRE and direction not in result:
            result.append(direction)
    return result


def nearby_allied_builder_positions(ct: Controller) -> list[Position]:
    allies: list[Position] = []
    for entity_id in ct.get_nearby_units():
        if entity_id == ct.get_id():
            continue
        if ct.get_team(entity_id) != ct.get_team():
            continue
        if ct.get_entity_type(entity_id) != EntityType.BUILDER_BOT:
            continue
        allies.append(ct.get_position(entity_id))
    return allies


def recent_visit_penalty(step: Position, recent_positions: list[Position]) -> float:
    penalty = 0.0
    for age, past in enumerate(reversed(recent_positions), start=1):
        if same_pos(step, past):
            penalty += max(1.0, 5.0 - age * 0.4)
    return penalty


def crowd_penalty(
    pos: Position,
    step: Position,
    direction: Direction,
    allied_positions: list[Position],
) -> float:
    penalty = 0.0
    for other in allied_positions:
        dist = manhattan(step, other)
        if dist == 0:
            penalty += 100.0
        elif dist == 1:
            penalty += 6.0
        elif dist == 2:
            penalty += 2.0
        if pos.direction_to(other) == direction:
            penalty += 3.0
    return penalty


def wall_hug_bonus(
    ct: Controller,
    pos: Position,
    step: Position,
    direction: Direction,
    wall_hand: int,
) -> float:
    side = direction.rotate_left() if wall_hand < 0 else direction.rotate_right()
    side_tiles = [pos.add(side), step.add(side)]
    return float(sum(1 for tile in side_tiles if wall_like(ct, tile)))


def shifted_target(
    ct: Controller,
    base_target: Position,
    home_core: Position,
    enemy_core: Position,
    lane_offset: int,
    stuck_turns: int,
    wall_hand: int,
) -> Position:
    lateral_x, lateral_y = lane_vector(home_core, enemy_core)
    effective_offset = lane_offset
    if stuck_turns >= 2:
        effective_offset += wall_hand * min(4, stuck_turns - 1)
    if manhattan(base_target, enemy_core) <= 8:
        effective_offset = max(-2, min(2, effective_offset))
    return clamp_pos(
        ct,
        Position(
            base_target.x + lateral_x * effective_offset,
            base_target.y + lateral_y * effective_offset,
        ),
    )


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


def building_id_at(ct: Controller, pos: Position) -> int | None:
    if not in_bounds(ct, pos):
        return None
    if not ct.is_in_vision(pos):
        return None
    return ct.get_tile_building_id(pos)


def can_destroy_allied(ct: Controller, pos: Position) -> bool:
    building_id = building_id_at(ct, pos)
    if building_id is None:
        return False
    if ct.get_team(building_id) != ct.get_team():
        return False
    if ct.get_entity_type(building_id) == EntityType.CORE:
        return False
    return ct.can_destroy(pos)


def ensure_conveyor_tile(ct: Controller, pos: Position, direction: Direction) -> bool:
    if ct.get_action_cooldown() != 0:
        return False
    building_id = building_id_at(ct, pos)
    if building_id is not None:
        if ct.get_team(building_id) != ct.get_team():
            return False
        if ct.get_entity_type(building_id) == EntityType.CONVEYOR:
            try:
                if ct.get_direction(building_id) == direction:
                    return False
            except Exception:
                pass
        if ct.get_entity_type(building_id) == EntityType.CORE:
            return False
        if ct.can_destroy(pos):
            ct.destroy(pos)
        else:
            return False
    if ct.can_build_conveyor(pos, direction):
        ct.build_conveyor(pos, direction)
        return True
    return False


def ensure_bridge_tile(ct: Controller, pos: Position, target: Position) -> bool:
    if ct.get_action_cooldown() != 0:
        return False
    building_id = building_id_at(ct, pos)
    if building_id is not None:
        if ct.get_team(building_id) != ct.get_team():
            return False
        if ct.get_entity_type(building_id) == EntityType.BRIDGE:
            try:
                if ct.get_bridge_target(building_id) == target:
                    return False
            except Exception:
                pass
        if ct.get_entity_type(building_id) == EntityType.CORE:
            return False
        if ct.can_destroy(pos):
            ct.destroy(pos)
        else:
            return False
    if ct.can_build_bridge(pos, target):
        ct.build_bridge(pos, target)
        return True
    return False


def try_build_frontline_sentinel(
    ct: Controller,
    home_core: Position,
    enemy_core: Position,
) -> bool:
    sx, sy = siege_vector(home_core, enemy_core)
    fire_dir = diagonal_direction(-sx, -sy)
    for front in sentinel_candidates(home_core, enemy_core):
        if not in_bounds(ct, front):
            continue
        if ct.get_position().distance_squared(front) > 2:
            continue
        building_id = building_id_at(ct, front)
        if building_id is not None:
            if ct.get_team(building_id) != ct.get_team():
                continue
            if ct.get_entity_type(building_id) == EntityType.SENTINEL:
                return False
            if can_destroy_allied(ct, front):
                ct.destroy(front)
            else:
                continue
        if ct.can_build_sentinel(front, fire_dir):
            ct.build_sentinel(front, fire_dir)
            return True
    return False


def try_build_bridge_to_sentinel(
    ct: Controller,
    home_core: Position,
    enemy_core: Position,
) -> bool:
    for sentinel in sentinel_candidates(home_core, enemy_core):
        if not in_bounds(ct, sentinel):
            continue
        sentinel_building = building_id_at(ct, sentinel)
        if sentinel_building is not None:
            if ct.get_team(sentinel_building) != ct.get_team():
                continue
            if ct.get_entity_type(sentinel_building) != EntityType.SENTINEL:
                continue
        for bridge in bridge_candidates(home_core, enemy_core, sentinel):
            if not in_bounds(ct, bridge):
                continue
            if ct.get_position().distance_squared(bridge) > 2:
                continue
            if ensure_bridge_tile(ct, bridge, sentinel):
                return True
    return False


def try_advance_lane(
    ct: Controller,
    target: Position,
    blocked: set[tuple[int, int]] | None = None,
) -> bool:
    blocked = blocked or set()
    pos = ct.get_position()
    for direction in preferred_cardinal_dirs(pos, target):
        step = pos.add(direction)
        if not in_bounds(ct, step):
            continue
        if (step.x, step.y) in blocked:
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


def try_advance_rush(
    ct: Controller,
    target: Position,
    blocked: set[tuple[int, int]] | None = None,
) -> bool:
    blocked = blocked or set()
    pos = ct.get_position()
    for direction in preferred_move_dirs(pos, target):
        step = pos.add(direction)
        if not in_bounds(ct, step):
            continue
        if (step.x, step.y) in blocked:
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
        self.harvester_built = False

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
        feed = staging_tile(self.home_core, self.enemy_core)
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
        target = staging_tile(ct.get_position(), self.enemy_core)
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
            self.harvester_built = True
            return

        if not self.harvester_built and ct.get_position() != self.ore_anchor:
            if try_advance_rush(ct, self.ore_anchor):
                return

        blocked = reserved_front_tiles(ct, self.home_core, self.enemy_core)
        target = staging_tile(self.home_core, self.enemy_core)
        if self.harvester_built:
            if try_build_frontline_sentinel(ct, self.home_core, self.enemy_core):
                return
            if try_build_bridge_to_sentinel(ct, self.home_core, self.enemy_core):
                return
            lane_dir = ct.get_position().direction_to(target)
            if (
                lane_dir in CARDINAL_DIRECTIONS
                and (ct.get_position().x, ct.get_position().y) not in blocked
                and ensure_conveyor_tile(ct, ct.get_position(), lane_dir)
            ):
                if ct.can_move(lane_dir):
                    ct.move(lane_dir)
                return
        if self.harvester_built:
            try_advance_lane(ct, target, blocked)
        else:
            try_advance_rush(ct, self.ore_anchor)

    def run_rusher(self, ct: Controller) -> None:
        if self.enemy_core is None or self.approach is None:
            return

        blocked = reserved_front_tiles(ct, self.home_core, self.enemy_core)
        if (ct.get_position().x, ct.get_position().y) in blocked:
            if try_advance_rush(ct, staging_tile(self.home_core, self.enemy_core), set()):
                return

        if try_build_frontline_sentinel(ct, self.home_core, self.enemy_core):
            return
        if try_build_bridge_to_sentinel(ct, self.home_core, self.enemy_core):
            return

        if maybe_heal(ct):
            return

        feed = staging_tile(self.home_core, self.enemy_core)
        lane_offset = (ct.get_id() % 5) - 2
        if lane_offset != 0:
            sx, sy = siege_vector(self.home_core, self.enemy_core)
            feed = Position(feed.x - sy * lane_offset, feed.y + sx * lane_offset)
        try_advance_rush(ct, feed, blocked)

    def run(self, ct: Controller) -> None:
        entity_type = ct.get_entity_type()
        if entity_type == EntityType.CORE:
            self.run_core(ct)
            return
        if entity_type == EntityType.GUNNER:
            target = ct.get_gunner_target()
            if target is not None and ct.can_fire(target):
                ct.fire(target)
            return
        if entity_type == EntityType.SENTINEL:
            enemy_core = nearby_core(ct, enemy=True)
            if enemy_core is not None and ct.can_fire(enemy_core):
                ct.fire(enemy_core)
                return
            for entity_id in ct.get_nearby_entities():
                if ct.get_team(entity_id) == ct.get_team():
                    continue
                target = ct.get_position(entity_id)
                if ct.can_fire(target):
                    ct.fire(target)
                    return
            return
        if entity_type != EntityType.BUILDER_BOT:
            return
        if not self.ensure_builder_context(ct):
            return
        if self.role == "miner":
            self.run_miner(ct)
        else:
            self.run_rusher(ct)
