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
