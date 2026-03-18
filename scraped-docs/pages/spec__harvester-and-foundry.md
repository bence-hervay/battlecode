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
