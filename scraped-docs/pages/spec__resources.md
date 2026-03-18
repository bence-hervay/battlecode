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
