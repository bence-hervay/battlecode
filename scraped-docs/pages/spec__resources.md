Title: Resources

Source: https://docs.battlecode.cam/spec/resources

---

Titanium, axionite, and the cost scaling formula.

##  Titanium

The primary resource used to construct most buildings. Each team starts with **1000 titanium**.
Titanium is harvested from titanium ore deposits and delivered to the core via conveyors.

##  Axionite

Axionite comes in two forms:

## Raw axionite

Mined from axionite ore deposits. When fed to a turret or core, it **decays into titanium**. Must be refined first for advanced uses.

## Refined axionite

Produced by [axionite foundries](/spec/harvester-and-foundry#axionite-foundry) from raw axionite + titanium. Used for powerful units and advanced infrastructure.

Whenever “axionite” is mentioned in the spec without qualification, it refers to **refined axionite**.

##  Resource distribution

Resources are stored and moved in **stacks of 10**. At the end of each round, buildings that output resources send them to adjacent buildings that accept them.

Resources can be outputted to buildings belonging to the **opposing team**.

See [conveyors](/spec/conveyors), [harvester & foundry](/spec/harvester-and-foundry), and [turrets](/spec/turrets) for details on input/output directions.

##  Cost scaling

Every building and unit you construct increases the cost of future builds. The cost of every building and unit is:
cost=⌊scale×base cost⌋\text{cost} = \lfloor \text{scale} \times \text{base cost} \rfloorcost=⌊scale×base cost⌋
Where scale starts at 1.0 and increases **additively** with each entity built — two builder bots at +10% each gives 1.2x, not 1.21x. You can query the current scale with `c.get_scale_percent()` which returns it as a percentage (100.0 at base).

When an entity is destroyed, its scaling contribution is removed — costs go back down.

Every entity you build makes the next one more expensive. Be efficient with what you build!

[Previous](/spec/overview)

⌘I
